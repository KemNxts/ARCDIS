import time
import psutil
from collections import defaultdict
from config import config
from utils import logger
from preventer import Preventer
from reporter import Reporter
from models import AttackEvent, ProcessInfo

class Monitor:
    def __init__(self, reporter: Reporter):
        self.reporter = reporter
        self.running = False
        # Map of parent_pid -> list of (child_create_time, memory_mb, child_pid)
        self.parent_history = defaultdict(list)
        
    def _evaluate_process_tree(self):
        """Scans the active process list to build parent-child relations and detect abuse."""
        current_time = time.time()
        
        # Get all current processes with required attributes
        try:
            procs = list(psutil.process_iter(['pid', 'ppid', 'create_time', 'name', 'cmdline', 'memory_info']))
        except Exception as e:
            logger.error(f"Error iterating processes: {e}")
            return

        # Rebuild fresh mapping for current tick
        current_children = defaultdict(list)
        process_lookup = {}

        for p in procs:
            try:
                info = p.info
                process_lookup[info['pid']] = info
                if info['ppid']:
                    mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                    current_children[info['ppid']].append({
                        'pid': info['pid'],
                        'create_time': info['create_time'],
                        'memory_mb': mem_mb,
                        'name': info['name']
                    })
            except Exception:
                continue

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

            # Recent spawn rate (within the sliding window)
            recent_children = [c for c in children if (current_time - c['create_time']) <= config.SPAWN_WINDOW_SECONDS]
            recent_spawn_count = len(recent_children)

            # Trigger if there are too many total active children, too many recent spawns, or too much memory
            if total_children_count >= config.MAX_CHILDREN_PER_WINDOW or recent_spawn_count >= config.MAX_CHILDREN_PER_WINDOW or total_memory >= config.MAX_CHILD_MEMORY_MB:
                # Trigger Prevention!
                self._handle_detection(ppid, total_children_count, total_memory, process_lookup, children)
                
    def _handle_detection(self, ppid: int, spawn_count: int, total_memory: float, process_lookup: dict, recent_children: list):
        parent_info = process_lookup.get(ppid, {})
        parent_name = parent_info.get('name', 'Unknown')
        parent_cmd = " ".join(parent_info.get('cmdline', [])) if parent_info.get('cmdline') else ""
        
        # Calculate the TRUE recursive tree size and memory for the report
        true_spawn_count = spawn_count
        true_total_memory = total_memory
        try:
            parent = psutil.Process(ppid)
            all_children = parent.children(recursive=True)
            true_spawn_count = len(all_children)
            true_total_memory = sum(c.memory_info().rss / (1024 * 1024) for c in all_children)
        except Exception:
            pass
        
        # High visibility terminal warning
        print("\n" + "="*60)
        print("\033[91m\033[1m[!!!] MALICIOUS BEHAVIOR DETECTED [!!!]\033[0m")
        print(f"\033[93mTarget:\033[0m Parent PID {ppid} ({parent_name})")
        print(f"\033[93mReason:\033[0m Process tree reached {true_spawn_count} total children. Total Mem: {true_total_memory:.2f} MB")
        print("\033[91m-> Initiating Process Tree Termination...\033[0m")
        print("="*60 + "\n")
        
        logger.warning(f"ATTACK DETECTED [T1059] - Parent PID {ppid} ({parent_name}) spawned {true_spawn_count} children.")
        
        # 1. Prevent the attack
        mitigated = Preventer.terminate_process_tree(ppid)
        action_taken = "process_tree_terminated" if mitigated else "termination_failed"
        
        # 2. Extract features
        avg_memory = true_total_memory / true_spawn_count if true_spawn_count else 0
        features = {
            "spawn_count_in_window": true_spawn_count,
            "total_child_memory_mb": round(true_total_memory, 2),
            "avg_child_memory_mb": round(avg_memory, 2),
            "parent_pid": ppid,
            "parent_name": parent_name,
            "parent_cmdline": parent_cmd,
            "window_seconds": config.SPAWN_WINDOW_SECONDS
        }

        import uuid
        # 3. Report
        event = AttackEvent(
            attack_id=str(uuid.uuid4()),
            agent_id=config.AGENT_ID,
            technique="T1059",
            title="Rapid Process Creation / Memory Abuse Storm",
            description=f"Detected abnormal process spawning or memory consumption by parent process {parent_name} (PID: {ppid}).",
            features=features,
            action_taken=action_taken,
            severity="high"
        )
        
        self.reporter.send_attack_event(event)
        
        # Add a sleep to prevent spamming if termination failed
        time.sleep(1)

    def start(self):
        self.running = True
        logger.info(f"Monitor started. Window: {config.SPAWN_WINDOW_SECONDS}s, Max Spawns: {config.MAX_CHILDREN_PER_WINDOW}, Max Mem: {config.MAX_CHILD_MEMORY_MB}MB")
        while self.running:
            self._evaluate_process_tree()
            time.sleep(config.MONITOR_INTERVAL)

    def stop(self):
        self.running = False
