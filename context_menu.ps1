param(
    [string]$Action = "install"
)

$pythonExe = (Get-Command python).Source
$mainPy = Join-Path (Split-Path $PSScriptRoot -Parent) "main.py"
$automatorExe = "python.exe `"$mainPy`" --run-with-files `"%1`""

if ($Action -eq "install") {
    $regPath = "Registry::HKEY_CLASSES_ROOT\*\shell\RunWithAutomator"
    New-Item -Path $regPath -Force | Out-Null
    Set-ItemProperty -Path $regPath -Name "(Default)" -Value "Run with Automator"
    Set-ItemProperty -Path $regPath -Name "Icon" -Value "$pythonExe,0"

    $cmdPath = "$regPath\command"
    New-Item -Path $cmdPath -Force | Out-Null
    Set-ItemProperty -Path $cmdPath -Name "(Default)" -Value "$pythonExe `"$mainPy`" --run-with-files `"%1`""

    $folderRegPath = "Registry::HKEY_CLASSES_ROOT\Directory\shell\RunWithAutomator"
    New-Item -Path $folderRegPath -Force | Out-Null
    Set-ItemProperty -Path $folderRegPath -Name "(Default)" -Value "Run with Automator"
    Set-ItemProperty -Path $folderRegPath -Name "Icon" -Value "$pythonExe,0"

    $folderCmdPath = "$folderRegPath\command"
    New-Item -Path $folderCmdPath -Force | Out-Null
    Set-ItemProperty -Path $folderCmdPath -Name "(Default)" -Value "$pythonExe `"$mainPy`" --run-with-files `"%1`""

    Write-Output "Context menu installed. Right-click any file/folder and select 'Run with Automator'."
} elseif ($Action -eq "remove") {
    Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\*\shell\RunWithAutomator" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "Registry::HKEY_CLASSES_ROOT\Directory\shell\RunWithAutomator" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Output "Context menu removed."
}
