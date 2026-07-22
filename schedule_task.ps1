param(
    [string]$WorkflowPath,
    [string]$TaskName,
    [string]$TriggerType,
    [string]$Time = "09:00",
    [string]$DaysOfWeek = "Monday",
    [string]$FolderPath = ""
)

$taskFolder = "\Automator"
$pythonExe = (Get-Command python).Source
$mainPy = Join-Path (Split-Path $PSScriptRoot -Parent) "main.py"
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$mainPy`" --run `"$WorkflowPath`""

if (-not (Get-ScheduledTask -TaskPath $taskFolder -ErrorAction SilentlyContinue)) {
    New-Item -Path "TaskPath" -Name $taskFolder -Type "Container" -Force | Out-Null
}

$trigger = $null
switch ($TriggerType) {
    "daily" {
        $trigger = New-ScheduledTaskTrigger -Daily -At $Time
    }
    "weekly" {
        $days = $DaysOfWeek -split ","
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At $Time
    }
    "folder" {
        $trigger = New-ScheduledTaskTrigger -AtStartup
    }
    "startup" {
        $trigger = New-ScheduledTaskTrigger -AtStartup
    }
}

if (-not $trigger) {
    Write-Error "Invalid trigger type: $TriggerType"
    exit 1
}

try {
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -TaskPath $taskFolder -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
    Write-Output "Scheduled task '$TaskName' created successfully"
    exit 0
} catch {
    Write-Error "Failed to create task: $_"
    exit 1
}
