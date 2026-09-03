import sys
import signal
from reporter import Reporter
from monitor import Monitor
from ebpf_monitor import EBPFMonitor
from utils import logger
from config import config

class ARCDISAgent:
    def __init__(self):
        self.reporter = Reporter()
        self.monitor = Monitor(self.reporter)
        self.ebpf_monitor = EBPFMonitor(self.reporter)

    def start(self):
        logger.info("Initializing ARCDIS Agent...")
        
        # 1. Validate Config
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Configuration Error: {e}")
            sys.exit(1)

        # 2. Register with backend
        if not self.reporter.register():
            logger.error("Failed to register with ARCDIS backend. Exiting.")
            sys.exit(1)

        # 3. Start Heartbeat
        self.reporter.start_heartbeat()

        # 4. Start eBPF Monitor (Non-blocking)
        self.ebpf_monitor.start()

        # 5. Start Monitoring (Blocking)
        try:
            self.monitor.start()
        except Exception as e:
            logger.error(f"Monitor crashed: {e}")
        finally:
            self.stop()

    def stop(self):
        logger.info("Stopping ARCDIS Agent...")
        self.ebpf_monitor.stop()
        self.monitor.stop()
        self.reporter.stop_heartbeat()
        logger.info("Agent stopped cleanly.")

agent_instance = None

def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}. Initiating graceful shutdown...")
    if agent_instance:
        agent_instance.stop()
    sys.exit(0)

if __name__ == "__main__":
    import ctypes, sys
    try:
        libc = ctypes.CDLL('libc.so.6')
        # PR_SET_NAME = 15
        libc.prctl(15, b'Arcdis\0', 0, 0, 0)
    except Exception:
        pass
    
    try:
        import setproctitle
        setproctitle.setproctitle("Arcdis")
    except ImportError:
        pass
        
    if len(sys.argv) > 0:
        sys.argv[0] = "Arcdis"

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    agent_instance = ARCDISAgent()
    agent_instance.start()
