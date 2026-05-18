# jif.ps1 — PowerShell 一行命令查期刊 JIF
# 数据源: ManuSights (manusights.com)
# 用法: .\jif.ps1 <期刊名>
# 示例: .\jif.ps1 nature
#       .\jif.ps1 "nature communications"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Journal
)

$slug = $Journal.ToLower() -replace ' ', '-'
$url = "https://manusights.com/blog/${slug}-impact-factor"

try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec 15 -UseBasicParsing
    $title = [regex]::Match($response.Content, '<title>([^<]*)</title>').Groups[1].Value

    if ($title -match "Journal Guides") {
        Write-Host "❌ 期刊未收录: $Journal" -ForegroundColor Red
        Write-Host "💡 尝试搜索: site:manusights.com $Journal impact factor"
        exit 1
    }

    Write-Host $title -ForegroundColor Green
}
catch {
    Write-Host "❌ 查询失败: $_" -ForegroundColor Red
    exit 1
}
