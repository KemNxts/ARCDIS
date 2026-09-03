import os
import time
import shutil
import psutil
from typing import List
from utils import logger
import subprocess
from utils import logger

class Preventer:
    @staticmethod
    def remove_cron_line(malicious_line: str) -> bool:
        """
        Removes a specific malicious line from all users' crontabs.
        """
        import subprocess
        import pwd
        
        success = False
        try:
            users = [p.pw_name for p in pwd.getpwall() if p.pw_uid >= 1000 or p.pw_name == 'root']
            for user in users:
                result = subprocess.run(['crontab', '-u', user, '-l'], capture_output=True, text=True)
                if result.returncode != 0:
                    continue
                    
                current_cron = result.stdout.splitlines()
                if malicious_line not in current_cron:
                    continue
                    
                new_cron = [line for line in current_cron if line != malicious_line]
                new_cron_text = "\n".join(new_cron) + "\n"
                
                process = subprocess.Popen(['crontab', '-u', user, '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate(input=new_cron_text)
                
                if process.returncode == 0:
                    logger.info(f"Successfully removed malicious line from {user}'s crontab.")
                    success = True
                else:
                    logger.error(f"Failed to write new crontab for {user}: {stderr}")
        except Exception as e:
            logger.error(f"Error modifying crontab: {e}")
        
        return success

    @staticmethod
    def quarantine_and_terminate(pid: int, files_to_quarantine: list = None) -> bool:
        """
        Suspends the process to halt encryption, quarantines the specific files it was touching,
        and then completely terminates the process tree.
        """
        try:
            parent = psutil.Process(pid)
            # 1. Instantly Suspend to halt encryption
            parent.suspend()
            for child in parent.children(recursive=True):
                try:
                    child.suspend()
                except:
                    pass
            
            logger.info(f"Suspended ransomware process tree (PID {pid}) to halt encryption.")
            
            # 2. Quarantine files
            if files_to_quarantine:
                quarantine_dir = "/tmp/arcdis_quarantine"
                os.makedirs(quarantine_dir, exist_ok=True)
                for f in files_to_quarantine:
                    try:
                        if os.path.exists(f):
                            filename = os.path.basename(f)
                            # Append timestamp to avoid collisions
                            quarantine_path = os.path.join(quarantine_dir, f"{filename}_{int(time.time())}.quarantined")
                            shutil.move(f, quarantine_path)
                            logger.info(f"Quarantined suspicious file: {f} -> {quarantine_path}")
                    except Exception as e:
                        logger.warning(f"Could not quarantine {f}: {e}")
            
            # 3. Terminate Tree
            return Preventer.terminate_process_tree(pid)
            
        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} already dead, cannot quarantine/terminate.")
            return False
        except Exception as e:
            logger.error(f"Failed to quarantine/terminate PID {pid}: {e}")
            return False

    @staticmethod
    def terminate_single_process(pid: int) -> bool:
        """
        Forcefully terminates a single process without touching its children.
        """
        try:
            p = psutil.Process(pid)
            p.suspend()
            p.terminate()
            p.wait(timeout=3)
            logger.info(f"Terminated single process PID {pid}.")
            return not psutil.pid_exists(pid)
        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} already dead, cannot terminate.")
            return False
        except psutil.AccessDenied:
            logger.warning(f"Access denied terminating PID {pid}")
            return False
        except psutil.TimeoutExpired:
            p.kill()
            return not psutil.pid_exists(pid)
        except Exception as e:
            logger.error(f"Failed to terminate PID {pid}: {e}")
            return False

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

        logger.info(f"Terminated process tree for parent PID {parent_pid} ({len(processes_to_kill)} processes killed).")
        
        # Explicit process death verification
        try:
            if psutil.pid_exists(parent_pid):
                return False
        except Exception:
            pass
            
        return True

    @staticmethod
    def execute_policy(policy: dict, target_pid: int, files_to_quarantine: list = None) -> bool:
        """
        Securely executes a structured JSON policy action.
        Validates the action string against an allow-list of safe capabilities.
        """
        action = policy.get("action", "MONITOR_ONLY")
        
        if action == "MONITOR_ONLY":
            logger.info(f"Policy indicates MONITOR_ONLY. No local mitigation taken for PID {target_pid}.")
            return True
            
        elif action == "TERMINATE_PROCESS_TREE":
            logger.warning(f"Executing policy TERMINATE_PROCESS_TREE on PID {target_pid}")
            success = Preventer.terminate_process_tree(target_pid)
            if success:
                logger.info(f"Mitigation successful: PID {target_pid} tree eradicated.")
            else:
                logger.error(f"Mitigation failed or incomplete for PID {target_pid}.")
            return success
            
        elif action == "TERMINATE_SINGLE_PROCESS":
            logger.warning(f"Executing policy TERMINATE_SINGLE_PROCESS on PID {target_pid}")
            success = Preventer.terminate_single_process(target_pid)
            if success:
                logger.info(f"Mitigation successful: PID {target_pid} eradicated.")
            else:
                logger.error(f"Mitigation failed for PID {target_pid}.")
            return success
            
        elif action == "QUARANTINE_AND_TERMINATE":
            logger.warning(f"Executing policy QUARANTINE_AND_TERMINATE on PID {target_pid}")
            success = Preventer.quarantine_and_terminate(target_pid, files_to_quarantine)
            if success:
                logger.info(f"Mitigation successful: PID {target_pid} quarantined and eradicated.")
            else:
                logger.error(f"Mitigation failed for PID {target_pid}.")
            return success
            
        else:
            logger.error(f"Unsupported policy action '{action}'. Rejecting execution for safety.")
            return False
