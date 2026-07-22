import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SCHEDULER_SCRIPT = SCRIPT_DIR / "schedule_task.ps1"


def get_workflow_run_command(workflow_path: str) -> str:
    python_exe = sys.executable
    main_py = str(SCRIPT_DIR / "main.py")
    return f'"{python_exe}" "{main_py}" --run "{workflow_path}"'


def schedule_workflow(
    workflow_path: str,
    task_name: str,
    trigger_type: str,
    trigger_params: dict
) -> tuple[bool, str]:
    cmd = [
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", str(SCHEDULER_SCRIPT),
        "-WorkflowPath", workflow_path,
        "-TaskName", task_name,
        "-TriggerType", trigger_type,
    ]
    if trigger_type == "daily":
        cmd.extend(["-Time", trigger_params.get("time", "09:00")])
    elif trigger_type == "weekly":
        cmd.extend([
            "-Time", trigger_params.get("time", "09:00"),
            "-DaysOfWeek", trigger_params.get("days", "Monday"),
        ])
    elif trigger_type == "folder":
        cmd.extend(["-FolderPath", trigger_params.get("folder_path", "")])
    elif trigger_type == "startup":
        pass
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout
        return False, result.stderr
    except Exception as e:
        return False, str(e)


def remove_scheduled_task(task_name: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["powershell", "-Command", f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false"],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        return False, str(e)


def list_scheduled_tasks() -> list[dict]:
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-ScheduledTask | Where-Object TaskPath -like '*\\Automator*' | "
             "ForEach-Object { $_.TaskName }"],
            capture_output=True, text=True, timeout=10
        )
        tasks = []
        for line in result.stdout.strip().splitlines():
            line = line.strip()
            if line:
                tasks.append({"name": line, "path": f"\\Automator\\{line}"})
        return tasks
    except Exception:
        return []
