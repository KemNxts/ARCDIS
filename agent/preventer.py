import psutil
from typing import List
from utils import logger

class Preventer:
    @staticmethod
    def terminate_process_tree(parent_pid: int) -> bool:
        """
        Forcefully terminates a parent process and all its children.
        """
        try:
            parent = psutil.Process(parent_pid)
        except psutil.NoSuchProcess:
            logger.warning(f"Process {parent_pid} already dead, cannot terminate.")
            return False

        children = parent.children(recursive=True)
        processes_to_kill = [parent] + children

        # Suspend processes first to prevent them from spawning more children while we kill them
        for p in processes_to_kill:
            try:
                p.suspend()
            except psutil.Error:
                pass

        # Terminate all
        for p in processes_to_kill:
            try:
                p.terminate()
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                logger.warning(f"Access denied terminating PID {p.pid}")
        
        # Wait for termination and force kill if necessary
        gone, alive = psutil.wait_procs(processes_to_kill, timeout=3)
        for p in alive:
            try:
                p.kill()
            except psutil.Error:
                pass

        logger.warning(f"Terminated process tree for parent PID {parent_pid} ({len(processes_to_kill)} processes killed).")
        return True
