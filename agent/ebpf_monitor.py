import time
import threading
from collections import defaultdict
import uuid
import ctypes
import os

try:
    from bcc import BPF
except ImportError:
    BPF = None

from config import config
from utils import logger
from preventer import Preventer
from reporter import Reporter
from models import AttackEvent
from ml import LocalAnomalyDetector

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <uapi/linux/limits.h>
#include <linux/sched.h>
#include <linux/fs.h>

struct data_t {
    u32 pid;
    char comm[TASK_COMM_LEN];
};

BPF_PERF_OUTPUT(events);

// 1. openat
TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
    int flags = args->flags;
    // O_WRONLY = 1, O_RDWR = 2, O_CREAT = 64 (0100 octal)
    if ((flags & 3) != 0 || (flags & 0100)) {
        struct data_t data = {};
        data.pid = bpf_get_current_pid_tgid() >> 32;
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        events.perf_submit(args, &data, sizeof(data));
    }
    return 0;
}

// 2. open
TRACEPOINT_PROBE(syscalls, sys_enter_open) {
    int flags = args->flags;
    if ((flags & 3) != 0 || (flags & 0100)) {
        struct data_t data = {};
        data.pid = bpf_get_current_pid_tgid() >> 32;
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        events.perf_submit(args, &data, sizeof(data));
    }
    return 0;
}

// 3. creat
TRACEPOINT_PROBE(syscalls, sys_enter_creat) {
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}

struct open_how_local {
    u64 flags;
    u64 mode;
    u64 resolve;
};

// 4. openat2
TRACEPOINT_PROBE(syscalls, sys_enter_openat2) {
    struct open_how_local how = {};
    bpf_probe_read_user(&how, sizeof(how), args->how);
    if ((how.flags & 3) != 0 || (how.flags & 0100)) {
        struct data_t data = {};
        data.pid = bpf_get_current_pid_tgid() >> 32;
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        events.perf_submit(args, &data, sizeof(data));
    }
    return 0;
}
"""

class DataEvent(ctypes.Structure):
    _fields_ = [
        ("pid", ctypes.c_uint32),
        ("comm", ctypes.c_char * 16)
    ]

class EBPFMonitor:
    def __init__(self, reporter: Reporter):
        self.reporter = reporter
        self.running = False
        self.bpf = None
        self.pid_history = defaultdict(list)
        self.thread = None
        self.ml = LocalAnomalyDetector()

    def start(self):
        if BPF is None:
            logger.error("BCC (BPF Compiler Collection) is not installed. eBPF Monitor cannot start.")
            return

        self.running = True
        logger.info(f"Initializing eBPF Monitor for T1486 (Threshold: {config.EBPF_FILE_CREATION_THRESHOLD} files / {config.EBPF_WINDOW_SECONDS}s)")
        
        try:
            self.bpf = BPF(text=bpf_text)
            self.bpf["events"].open_perf_buffer(self._print_event)
            
            self.thread = threading.Thread(target=self._poll_loop, daemon=True)
            self.thread.start()
            logger.info("eBPF Monitor started successfully.")
        except Exception as e:
            logger.error(f"Failed to start eBPF monitor: {e}")
            self.running = False

    def _poll_loop(self):
        while self.running:
            try:
                # Poll for events
                self.bpf.perf_buffer_poll(timeout=500)
                # Periodically clean up old timestamps
                self._cleanup_history()
            except Exception as e:
                logger.error(f"Error polling eBPF buffer: {e}")
                time.sleep(1)

    def _print_event(self, cpu, data, size):
        event = ctypes.cast(data, ctypes.POINTER(DataEvent)).contents
        pid = event.pid
        comm = event.comm.decode('utf-8', 'replace')
        
        current_time = time.time()
        self.pid_history[pid].append(current_time)
        
        # Check threshold
        window_start = current_time - config.EBPF_WINDOW_SECONDS
        self.pid_history[pid] = [t for t in self.pid_history[pid] if t >= window_start]
        
        file_count = len(self.pid_history[pid])
        
        anomaly_score = self.ml.evaluate_ebpf(file_count)
        
        if anomaly_score > 0.8:
            # Whitelist check before taking action to avoid killing browsers/system apps
            try:
                import psutil
                proc = psutil.Process(pid)
                proc_name = proc.name().lower()
                
                safe_apps = {
                    'chrome', 'chromium', 'firefox', 'brave', 'code', 'vscode',
                    'apt', 'apt-get', 'dpkg', 'snapd', 'dockerd', 'containerd',
                    'node', 'npm', 'java', 'systemd', 'rsyslogd', 'journald',
                    'git', 'tar', 'unzip', 'gzip'
                }
                
                if any(app in proc_name for app in safe_apps):
                    # Safe app doing burst IO (e.g., Chrome cache, npm install)
                    self.pid_history[pid] = []
                    return
            except Exception:
                pass
                
            self._handle_detection(pid, comm, file_count, anomaly_score)
            # Reset to avoid spamming
            self.pid_history[pid] = []

    def _cleanup_history(self):
        current_time = time.time()
        window_start = current_time - config.EBPF_WINDOW_SECONDS
        for pid in list(self.pid_history.keys()):
            self.pid_history[pid] = [t for t in self.pid_history[pid] if t >= window_start]
            if not self.pid_history[pid]:
                del self.pid_history[pid]

    def _handle_detection(self, pid: int, comm: str, count: int, anomaly_score: float):
        logger.warning(f"eBPF DETECTED T1486 (Ransomware/Storage Fill): PID {pid} ({comm}) created {count} files in {config.EBPF_WINDOW_SECONDS}s. Score: {anomaly_score}")
        
        print("\n" + "="*70)
        print("\033[91m\033[1m[!!!] T1486 RANSOMWARE BEHAVIOR DETECTED BY ML (eBPF) [!!!]\033[0m")
        print(f"\033[93mTarget:\033[0m PID {pid} ({comm})")
        print(f"\033[93mEvidence:\033[0m Rapid file creation ({count} files in {config.EBPF_WINDOW_SECONDS}s, ML Score: {anomaly_score})")
        print(f"\033[91m-> Action:\033[0m Terminating Process Tree")
        print("="*70 + "\n")

        # Mitigate locally
        mitigated = Preventer.terminate_process_tree(pid)
        action_taken = "TERMINATE_PROCESS_TREE" if mitigated else "mitigation_failed"
        
        features = {
            "files_created_in_window": count,
            "parent_pid": pid,
            "parent_name": comm,
            "window_seconds": config.EBPF_WINDOW_SECONDS,
            "behavior_type": "ransomware_ebpf"
        }
        
        # Report
        event = AttackEvent(
            attack_id=str(uuid.uuid4()),
            agent_id=config.AGENT_ID,
            technique="T1486",
            title="eBPF Detection: Ransomware",
            description=f"Detected rapid file creation by {comm} (PID: {pid}). {count} files in {config.EBPF_WINDOW_SECONDS}s. ML Score: {anomaly_score}",
            features=features,
            action_taken=action_taken,
            severity="critical",
            local_anomaly_score=anomaly_score
        )
        self.reporter.send_attack_event(event)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.bpf:
            self.bpf.cleanup()
        logger.info("eBPF Monitor stopped.")
