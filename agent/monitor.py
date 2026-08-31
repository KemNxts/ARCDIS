import time
import psutil
from collections import defaultdict
from config import config
from utils import logger
from preventer import Preventer
from reporter import Reporter
from models import AttackEvent, ProcessInfo
from ml import LocalAnomalyDetector
from risk import RiskEvaluator
from policy import PolicyEngine

class Monitor:
    def __init__(self, reporter: Reporter):
        self.reporter = reporter
        self.running = False
        # Map of parent_pid -> list of (child_create_time, memory_mb, child_pid)
        self.parent_history = defaultdict(list)
        # Map of pid -> list of recent cpu_percent values
        self.cpu_history = defaultdict(list)
        # Map of pid -> (timestamp, write_bytes, write_count)
        self.io_history = {}
        
        import os
        self.protected_dirs = [
            os.path.expanduser('~'),
            os.path.expanduser('~/Documents'),
            os.path.expanduser('~/Desktop'),
            '/tmp/test_dir',
            '/tmp/test'
        ]
        self.dir_state = {}
        
        self.ml = LocalAnomalyDetector()
        self.policy_engine = PolicyEngine()
        
    def _check_directory_deltas(self):
        """Lightweight tracking of file creations in protected directories"""
        import os
        new_files = []
        for d in self.protected_dirs:
            if not os.path.exists(d):
                continue
            try:
                # 1. Check top-level items
                current_items = {f for f in os.listdir(d) if not f.startswith('.')}
                
                if d not in self.dir_state:
                    self.dir_state[d] = {'items': set(), 'subdirs': {}}
                
                # Check top-level creations
                diff = current_items - self.dir_state[d]['items']
                for f in diff:
                    new_files.append(os.path.join(d, f))
                
                self.dir_state[d]['items'] = current_items
                
                # 2. Check 2nd-level subdirectories using lazy st_mtime
                for item in current_items:
                    item_path = os.path.join(d, item)
                    if os.path.isdir(item_path):
                        mtime = os.stat(item_path).st_mtime
                        if item_path not in self.dir_state[d]['subdirs']:
                            self.dir_state[d]['subdirs'][item_path] = {'mtime': mtime, 'files': set(os.listdir(item_path))}
                            continue
                            
                        # If directory was modified, do a lazy listdir to find new files!
                        if mtime != self.dir_state[d]['subdirs'][item_path]['mtime']:
                            current_sub_files = {f for f in os.listdir(item_path) if not f.startswith('.')}
                            sub_diff = current_sub_files - self.dir_state[d]['subdirs'][item_path]['files']
                            for sf in sub_diff:
                                new_files.append(os.path.join(item_path, sf))
                            
                            self.dir_state[d]['subdirs'][item_path]['mtime'] = mtime
                            self.dir_state[d]['subdirs'][item_path]['files'] = current_sub_files
            except Exception:
                pass
        return new_files
        
    def _scan_processes(self):
        """Scans the active process list to build parent-child relations and detect abuse."""
        current_time = time.time()
        
        # 1. Global Directory Delta (Decoupled File Creation Monitor)
        newly_created_files = self._check_directory_deltas()
        
        # Get all current processes with required attributes
        try:
            procs = list(psutil.process_iter(['pid', 'ppid', 'create_time', 'name', 'cmdline', 'memory_info', 'cpu_percent', 'num_threads', 'io_counters']))
        except Exception as e:
            logger.error(f"Error iterating processes: {e}")
            return

        # Rebuild fresh mapping for current tick
        current_children = defaultdict(list)
        process_lookup = {}
        evaluated_processes = []
        
        for p in procs:
            try:
                info = p.info
                process_lookup[info['pid']] = info
                
                # Add to tree for process_storm detection
                if info['ppid']:
                    current_children[info['ppid']].append({
                        'pid': info['pid'],
                        'create_time': info['create_time'],
                        'memory_mb': info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0,
                        'name': info['name']
                    })
                
                # Skip core OS, desktop environments, and browsers for Universal ML Monitor
                # Killing these processes will instantly crash the user's laptop session.
                SAFE_PROCESSES = {
                    'systemd', 'gnome-shell', 'Xorg', 'Xwayland', 'dbus-daemon', 'pulseaudio', 
                    'pipewire', 'pipewire-pulse', 'kworker', 'chrome', 'brave', 'firefox', 
                    'code', 'docker', 'containerd', 'dockerd', 'NetworkManager', 'wpa_supplicant',
                    'wireplumber', 'polkitd', 'rtkit-daemon', 'gdm', 'gdm-session-worker',
                    'gnome-terminal-server', 'gnome-session-binary', 'gnome-keyring-daemon',
                    'systemd-journald', 'systemd-logind', 'systemd-udevd', 'systemd-resolved',
                    'irqbalance', 'accounts-daemon', 'cron', 'rsyslogd', 'systemd-oomd', 'auditd',
                    'bash', 'zsh', 'sh', 'dash', 'sshd', 'tmux', 'screen'
                }
                
                if info['name'] in SAFE_PROCESSES or info['name'].startswith('kworker') or info['name'] == 'agent.py':
                    continue
                    
                # Safe Project Apps (Backend/Frontend)
                cmdline = " ".join(info.get('cmdline', []) or [])
                if 'uvicorn' in cmdline or 'vite' in cmdline or 'node' in info['name'] or 'npm' in info['name']:
                    continue
                
                # Single Process Evaluation (Universal Monitor)
                mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                cpu = info.get('cpu_percent') or 0.0
                threads = info.get('num_threads') or 1
                pid = info['pid']
                
                self.cpu_history[pid].append(cpu)
                # Keep last 5 ticks
                if len(self.cpu_history[pid]) > 5:
                    self.cpu_history[pid].pop(0)
                    
                # Check for sustained high CPU (e.g. > 70% for 3+ ticks)
                sustained_high_cpu = len(self.cpu_history[pid]) >= 3 and all(c > 70.0 for c in self.cpu_history[pid][-3:])
                
                # --- File System IO Evaluation (Ransomware T1486) ---
                io = info.get('io_counters')
                write_mb_rate = 0.0
                write_count_rate = 0.0
                protected_open_files = 0
                suspicious_files = []
                
                if io:
                    current_write_bytes = io.write_bytes
                    current_write_count = io.write_chars if hasattr(io, 'write_chars') else io.write_count
                    
                    if pid in self.io_history:
                        last_time, last_bytes, last_count = self.io_history[pid]
                        time_delta = current_time - last_time
                        if time_delta > 0:
                            write_mb_rate = ((current_write_bytes - last_bytes) / (1024 * 1024)) / time_delta
                            write_count_rate = (current_write_count - last_count) / time_delta
                    
                    self.io_history[pid] = (current_time, current_write_bytes, current_write_count)
                    
                    # If writing heavily, check open files (Threshold lowered to 5 writes/sec to catch mock scripts)
                    if write_mb_rate > 1.0 or write_count_rate > 5:
                        try:
                            p = psutil.Process(pid)
                            open_files = p.open_files()
                            for f in open_files:
                                # Check if modifying files in explicitly protected user space
                                # We ignore hidden folders (e.g. .cache, .vscode-server, .gemini) to prevent false positives
                                # on normal IDE/Agent logging activity.
                                protected_dirs = ['/Documents', '/Desktop', '/Downloads', '/Pictures', '/Music', '/Videos']
                                is_protected_home = any(f.path.startswith(os.path.expanduser(f"~{d}")) for d in protected_dirs)
                                
                                if f.path.startswith('/tmp/test') or is_protected_home:
                                    protected_open_files += 1
                                    suspicious_files.append(f.path)
                        except Exception:
                            pass
                            
                evaluated_processes.append({
                    'pid': pid,
                    'mem_mb': mem_mb,
                    'cpu': cpu,
                    'threads': threads,
                    'write_mb_rate': write_mb_rate,
                    'write_count_rate': write_count_rate,
                    'protected_open_files': protected_open_files,
                    'suspicious_files': suspicious_files,
                    'sustained_high_cpu': sustained_high_cpu
                })

            except Exception:
                continue

        # 2. Correlate global file creation delta with highest IO writer
        if newly_created_files and evaluated_processes:
            highest_writer = max(evaluated_processes, key=lambda x: x['write_count_rate'])
            if highest_writer['write_count_rate'] > 2:
                highest_writer['protected_open_files'] += len(newly_created_files)
                highest_writer['suspicious_files'].extend(newly_created_files)

        # 3. Evaluate Machine Learning Models for Single Processes
        for p_data in evaluated_processes:
            fs_anomaly = self.ml.evaluate_fs(p_data['write_mb_rate'], p_data['write_count_rate'], p_data['protected_open_files'])
            proc_anomaly = self.ml.evaluate_process(p_data['cpu'], p_data['mem_mb'], p_data['threads'])
            
            if fs_anomaly >= 0.85:
                self._handle_detection(
                    pid=p_data['pid'],
                    spawn_count=0,
                    total_memory=p_data['mem_mb'],
                    process_lookup=process_lookup,
                    anomaly_score=fs_anomaly,
                    behavior_type="ransomware",
                    files_to_quarantine=p_data['suspicious_files']
                )
            elif p_data['sustained_high_cpu']:
                self._handle_detection(
                    pid=p_data['pid'],
                    spawn_count=0,
                    total_memory=p_data['mem_mb'],
                    process_lookup=process_lookup,
                    anomaly_score=max(proc_anomaly, 0.90),
                    behavior_type="resource_hijacker"
                )
            elif proc_anomaly >= 0.5:
                self._handle_detection(
                    pid=p_data['pid'],
                    spawn_count=0,
                    total_memory=p_data['mem_mb'],
                    process_lookup=process_lookup,
                    anomaly_score=proc_anomaly,
                    behavior_type="anomalous_process"
                )

        # Evaluate against thresholds
        for ppid, children in current_children.items():
            if ppid in (0, 1, 2):
                continue
                
            parent_info = process_lookup.get(ppid, {})
            parent_name = parent_info.get('name', 'Unknown')
            
            # MITRE T1059 focuses on Command and Scripting Interpreters.
            # To ensure 100% safety of the host OS and desktop environment, we ONLY 
            # monitor specific interpreters for process/memory abuse storms.
            MONITORED_INTERPRETERS = {
                'bash', 'sh', 'dash', 'zsh', 
                'python', 'python2', 'python3', 
                'perl', 'ruby'
            }
            
            if parent_name not in MONITORED_INTERPRETERS:
                continue

            # Total active children and memory
            total_children_count = len(children)
            total_memory = sum(c['memory_mb'] for c in children)
            avg_memory = total_memory / total_children_count if total_children_count else 0.0

            # Get local ML anomaly score
            anomaly_score = self.ml.evaluate_tree(total_children_count, total_memory, avg_memory)

            # Trigger if anomaly score indicates suspicious or high confidence anomaly
            if anomaly_score >= 0.5:
                # We need accurate CPU % to distinguish between a pure fork bomb and a CPU miner (T1496).
                # The psutil process_iter doesn't always have accurate instant CPU on the first tick, 
                # so we actively measure the parent's CPU for a fraction of a second.
                try:
                    parent_proc = psutil.Process(ppid)
                    child_procs = [psutil.Process(c['pid']) for c in children[:5]]
                    
                    # Initialize CPU counters (first call returns 0)
                    parent_proc.cpu_percent(interval=None)
                    for cp in child_procs:
                        cp.cpu_percent(interval=None)
                        
                    time.sleep(0.2) # Active measurement window
                    
                    # Second call returns actual CPU % over the window
                    active_cpu = parent_proc.cpu_percent(interval=None)
                    children_cpu = sum(cp.cpu_percent(interval=None) for cp in child_procs)
                    total_tree_cpu = active_cpu + children_cpu
                except Exception:
                    total_tree_cpu = 0.0

                # If the tree is burning CPU, it's a cryptominer (Resource Hijacker), not just a process storm
                behavior_type = "resource_hijacker" if total_tree_cpu > 60.0 else "process_storm"
                
                # Delegate to Risk & Policy Engine
                self._handle_detection(
                    pid=ppid,
                    spawn_count=total_children_count,
                    total_memory=total_memory,
                    process_lookup=process_lookup,
                    anomaly_score=anomaly_score,
                    behavior_type=behavior_type
                )
                
    def _handle_detection(self, pid: int, spawn_count: int, total_memory: float, process_lookup: dict, anomaly_score: float, behavior_type: str, files_to_quarantine: list = None):
        parent_info = process_lookup.get(pid, {})
        parent_name = parent_info.get('name', 'Unknown')
        parent_cmd = " ".join(parent_info.get('cmdline', [])) if parent_info.get('cmdline') else ""
        
        # Calculate the TRUE recursive tree size and memory for the report
        true_spawn_count = spawn_count
        true_total_memory = total_memory
        try:
            if behavior_type in ("process_storm", "resource_hijacker", "ransomware"):
                parent = psutil.Process(pid)
                all_children = parent.children(recursive=True)
                true_spawn_count = len(all_children)
                true_total_memory = sum(c.memory_info().rss / (1024 * 1024) for c in all_children)
        except Exception:
            pass
        
        # Evaluate Risk Tier
        risk_tier = RiskEvaluator.evaluate(anomaly_score)
        
        # We only proceed to policy evaluation for Suspicious or High risk
        if risk_tier == "LOW":
            return
            
        # Select Generic Policy
        policy = self.policy_engine.select_policy(risk_tier, behavior_type=behavior_type)
        
        # High visibility terminal warning for the user
        print("\n" + "="*70)
        print("\033[91m\033[1m[!!!] MALICIOUS BEHAVIOR DETECTED [!!!]\033[0m")
        print(f"\033[93mTarget:\033[0m PID {pid} ({parent_name})")
        print(f"\033[93mEvidence:\033[0m ML Score: {anomaly_score:.2f} | Risk Tier: {risk_tier} | Behavior: {behavior_type}")
        print(f"\033[93mDetails:\033[0m Process tree/Target reached {true_spawn_count} children. Total Mem: {true_total_memory:.2f} MB")
        if files_to_quarantine:
            print(f"\033[93mQuarantine:\033[0m {len(files_to_quarantine)} protected files actively targeted.")
        print(f"\033[91m-> Selected Policy:\033[0m {policy.get('id')} (Action: {policy.get('action')})")
        print("="*70 + "\n")
        
        logger.warning(f"ATTACK DETECTED - ML Score: {anomaly_score:.2f} - Tier: {risk_tier} - Target: PID {pid}")
        
        # 1. Execute the selected policy locally
        mitigated = Preventer.execute_policy(policy, pid, files_to_quarantine)
        action_taken = policy.get('action') if mitigated else "mitigation_failed"
        
        # 2. Extract features
        avg_memory = true_total_memory / true_spawn_count if true_spawn_count else 0
        features = {
            "spawn_count_in_window": true_spawn_count,
            "total_child_memory_mb": round(true_total_memory, 2),
            "avg_child_memory_mb": round(avg_memory, 2),
            "parent_pid": pid,
            "parent_name": parent_name,
            "parent_cmdline": parent_cmd,
            "window_seconds": config.SPAWN_WINDOW_SECONDS,
            "behavior_type": behavior_type
        }

        # Map MITRE technique
        technique = "T1059"
        if behavior_type == "resource_hijacker":
            technique = "T1496"
        elif behavior_type == "ransomware":
            technique = "T1486"
        elif behavior_type == "anomalous_process":
            technique = "T1046"

        import uuid
        # 3. Report
        event = AttackEvent(
            attack_id=str(uuid.uuid4()),
            agent_id=config.AGENT_ID,
            technique=technique,
            title=f"Autonomous ML Detection: {behavior_type}",
            description=f"Detected abnormal {behavior_type} by {parent_name} (PID: {pid}). Local Anomaly: {anomaly_score}",
            features=features,
            action_taken=action_taken,
            severity="high" if anomaly_score > 0.85 else "medium",
            local_anomaly_score=anomaly_score
        )
        
        self.reporter.send_attack_event(event)
        
        # Add a sleep to prevent spamming if termination failed
        time.sleep(1)

    def start(self):
        self.running = True
        logger.info(f"Monitor started. Window: {config.SPAWN_WINDOW_SECONDS}s, Max Spawns: {config.MAX_CHILDREN_PER_WINDOW}, Max Mem: {config.MAX_CHILD_MEMORY_MB}MB")
        try:
            while self.running:
                self._scan_processes()
                time.sleep(config.MONITOR_INTERVAL)
        except Exception as e:
            logger.error(f"Monitor crashed: {e}")

    def stop(self):
        self.running = False
