# ARCDIS Agent Mitigation Logic & Attack Preemption

This document explains the core behavioral mechanics of the ARCDIS Agent, specifically focusing on how it mitigates rapid process creation storms (like MITRE T1059) and why the reported numbers might seem lower than expected by an attacker.

## The "Race Condition" of Preemption

When testing the ARCDIS Agent using a gradual process-creation script (e.g., `dump.py`), you might notice a discrepancy between the number of processes you *intended* to spawn and the number of processes the agent *reports* mitigating.

For example:
- **Attacker Intent:** Run `dump.py` 10 times in the background. Each script is programmed to spawn 5 sub-children. Total intended processes: **60**.
- **Agent Report:** The agent detects the attack, terminates the trees, and reports exactly **10** processes spawned (or 5-6 processes per tree).

### Why does this happen?

The ARCDIS Agent operates on a preemptive strike model. It is designed to be **faster than the attack itself**.

1. **The Threshold:** The agent is configured with a strict threshold (e.g., `MAX_CHILDREN_PER_WINDOW=4`).
2. **The Monitor Interval:** The agent polls the system state every 2 seconds (`MONITOR_INTERVAL=2`).
3. **The Preemption:** When you launch `dump.py` 10 times, the scripts immediately start running. However, because `dump.py` has an artificial `sleep()` delay between spawning its sub-children, the attack happens gradually.
4. **The Termination:** The instant a process tree crosses the threshold of 4 children, the agent detects it. It does not wait for the attack to finish. It immediately suspends the entire tree and forcefully terminates it.

Because the agent kills the parent script *instantly* upon detection, the script never gets the chance to spawn its remaining sub-children. The attack is stopped in its tracks. 

### Accurate Reporting

When the agent triggers, it performs a deep, recursive scan of the parent process to calculate the **true tree size** at that exact millisecond. 

If the agent reports that a tree had `5` children at the time of death, it is not missing the other processes—the other processes simply never existed because the agent successfully prevented them from being born.

## Strict Monitored Interpreters

To ensure 100% stability of the host Operating System and Desktop Environment, the agent uses a strict **Allow-List** of monitored parent processes.

The agent will only trigger detection if the malicious parent process is one of the following command or scripting interpreters:
- `bash`
- `sh`, `dash`, `zsh`
- `python`, `python2`, `python3`
- `perl`, `ruby`

This guarantees that the agent will never accidentally terminate critical system daemons (`systemd`), display managers (`gnome-shell`, `Xorg`), or heavy benign applications (`node`, `chrome`) that naturally spawn dozens of child processes.
