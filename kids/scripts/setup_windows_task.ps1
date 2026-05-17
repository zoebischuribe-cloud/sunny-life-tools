#Requires -RunAsAdministrator
<#
.SYNOPSIS
    一键创建 Windows 计划任务，实现每日本地自动推送。

.DESCRIPTION
    创建两个计划任务：
    - OpenClawKids_MorningPush : 每天 06:30 推送科普
    - OpenClawKids_EveningPush : 每天 21:00 推送小古文（含图片）

.PARAMETER WebhookUrl
    机器人 Webhook 地址（必填）。

.PARAMETER WebhookType
    机器人类型：wechat(默认) / feishu / dingtalk。

.PARAMETER PythonPath
    Python 可执行文件路径。默认自动查找 python/python3。

.EXAMPLE
    .\scripts\setup_windows_task.ps1 -WebhookUrl "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"

.EXAMPLE
    .\scripts\setup_windows_task.ps1 -WebhookUrl "xxx" -WebhookType "feishu" -PythonPath "C:\Python311\python.exe"
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$WebhookUrl,

    [Parameter(Mandatory=$false)]
    [ValidateSet("wechat","feishu","dingtalk")]
    [string]$WebhookType = "wechat",

    [Parameter(Mandatory=$false)]
    [string]$PythonPath = ""
)

$ErrorActionPreference = "Stop"

# ---------- 自动查找 Python ----------
if (-not $PythonPath) {
    $candidates = @("python", "python3", "py")
    foreach ($c in $candidates) {
        $found = (Get-Command $c -ErrorAction SilentlyContinue).Source
        if ($found) {
            $PythonPath = $found
            break
        }
    }
}

if (-not $PythonPath -or -not (Test-Path $PythonPath)) {
    Write-Host "错误: 找不到 Python。请安装 Python 3.9+ 并加入 PATH，或用 -PythonPath 指定。" -ForegroundColor Red
    exit 1
}

Write-Host "使用 Python: $PythonPath" -ForegroundColor Cyan

# ---------- 路径 ----------
$RepoRoot = Split-Path -Parent $PSScriptRoot
$ScriptPath = Join-Path $RepoRoot "scripts\local_push.py"

if (-not (Test-Path $ScriptPath)) {
    Write-Host "错误: 找不到 $ScriptPath" -ForegroundColor Red
    exit 1
}

# ---------- 删除旧任务（如果存在）----------
$taskNames = @("OpenClawKids_MorningPush", "OpenClawKids_EveningPush")
foreach ($name in $taskNames) {
    $existing = Get-ScheduledTask -TaskName $name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "删除旧任务: $name" -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $name -Confirm:$false
    }
}

# ---------- 创建任务 ----------
$ArgMorning = "`"" + $ScriptPath + "`" morning --webhook `"" + $WebhookUrl + "`" --type `"" + $WebhookType + "`""
$ArgEvening = "`"" + $ScriptPath + "`" evening --webhook `"" + $WebhookUrl + "`" --type `"" + $WebhookType + "`""

$ActionMorning = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument $ArgMorning `
    -WorkingDirectory $RepoRoot

$ActionEvening = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument $ArgEvening `
    -WorkingDirectory $RepoRoot

# 触发器：每天 06:30 和 21:00
$TriggerMorning = New-ScheduledTaskTrigger -Daily -At "06:30"
$TriggerEvening = New-ScheduledTaskTrigger -Daily -At "21:00"

# 设置：唤醒运行、网络可用时启动、失败后 5 分钟重试
$Settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# 使用当前用户凭据（支持锁屏时运行）
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Limited

# 注册任务
Register-ScheduledTask `
    -TaskName "OpenClawKids_MorningPush" `
    -Action $ActionMorning `
    -Trigger $TriggerMorning `
    -Settings $Settings `
    -Principal $Principal `
    -Description "OpenClaw Kids 每日科普推送 (6:30)" `
    -Force | Out-Null

Register-ScheduledTask `
    -TaskName "OpenClawKids_EveningPush" `
    -Action $ActionEvening `
    -Trigger $TriggerEvening `
    -Settings $Settings `
    -Principal $Principal `
    -Description "OpenClaw Kids 每日小古文推送 (21:00，含图片)" `
    -Force | Out-Null

# ---------- 结果 ----------
Write-Host ""
Write-Host "计划任务创建成功!" -ForegroundColor Green
Write-Host ""
Write-Host "任务列表:" -ForegroundColor Cyan
Get-ScheduledTask -TaskName "OpenClawKids_*" | Select-Object TaskName, State, NextRunTime | Format-Table -AutoSize

Write-Host ""
Write-Host "手动测试命令:" -ForegroundColor Cyan
Write-Host "  早上科普 : $PythonPath `"$ScriptPath`" morning" -ForegroundColor White
Write-Host "  晚上古文 : $PythonPath `"$ScriptPath`" evening" -ForegroundColor White
Write-Host ""
Write-Host "如需修改 Webhook，重新运行本脚本即可。" -ForegroundColor Gray
