$task = Get-ScheduledTask -TaskName "RealFifty_Daily_Bot"
$settings = $task.Settings
$settings.DisallowStartIfOnBatteries = $false
$settings.StartWhenAvailable = $true
$settings.WakeToRun = $true
Set-ScheduledTask -TaskName "RealFifty_Daily_Bot" -Settings $settings
