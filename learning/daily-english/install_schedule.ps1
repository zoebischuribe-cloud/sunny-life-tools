# Daily English — 安装三条定时任务
# Usage: powershell -ExecutionPolicy Bypass -File install_schedule.ps1

$python = (Get-Command python).Source
$script = "C:\Users\Admin\sunny-life-tools\learning\daily-english\daily_english.py"
$proxy = 'set http_proxy=http://127.0.0.1:7890&& set https_proxy=http://127.0.0.1:7890&&'
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Limited

# 1. 早上 6:47 — TED 深度学习
Register-ScheduledTask -TaskName "DailyEnglish_MorningTED" `
  -Action (New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $proxy `"$python`" `"$script`" --source ted") `
  -Trigger (New-ScheduledTaskTrigger -Daily -At "06:47") `
  -Principal $principal `
  -Description "6:47 AM — TED英语深度学习（跟读+语法+复述+视频）" -Force

# 2. 中午 12:07 — NPR/NYT 实时新闻
Register-ScheduledTask -TaskName "DailyEnglish_NoonNews" `
  -Action (New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $proxy `"$python`" `"$script`"") `
  -Trigger (New-ScheduledTaskTrigger -Daily -At "12:07") `
  -Principal $principal `
  -Description "12:07 PM — NPR/NYT真实英文新闻阅读" -Force

# 3. 晚上 18:37 — SM-2 间隔复习
Register-ScheduledTask -TaskName "DailyEnglish_EveningReview" `
  -Action (New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $proxy `"$python`" `"$script`" --review") `
  -Trigger (New-ScheduledTaskTrigger -Daily -At "18:37") `
  -Principal $principal `
  -Description "6:37 PM — SM-2间隔复习（自动追踪已学词汇）" -Force

Write-Host "Daily English 三条定时任务已安装:"
Write-Host "  06:47  DailyEnglish_MorningTED     TED深度学习"
Write-Host "  12:07  DailyEnglish_NoonNews       NPR/NYT新闻"
Write-Host "  18:37  DailyEnglish_EveningReview  SM-2复习"
