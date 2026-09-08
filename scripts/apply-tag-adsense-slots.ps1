# Apply TAG AdSense slot IDs to config.js, commit, and push.
param(
    [Parameter(Mandatory = $true)]
    [string]$Header,
    [Parameter(Mandatory = $true)]
    [string]$InContent,
    [Parameter(Mandatory = $true)]
    [string]$Footer,
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$configPath = Join-Path $root "assets\js\config.js"

foreach ($slot in @($Header, $InContent, $Footer)) {
    if ($slot -notmatch '^\d{10}$') {
        throw "Invalid slot ID '$slot' — expected 10 digits (data-ad-slot value)."
    }
}

$text = Get-Content -Raw -Path $configPath
$text = $text -replace '(header:\s*")[^"]*(")', "`${1}$Header`${2}"
$text = $text -replace '(footer:\s*")[^"]*(")', "`${1}$Footer`${2}"
$text = $text -replace '(inContent:\s*")[^"]*(")', "`${1}$InContent`${2}"
Set-Content -Path $configPath -Value $text -NoNewline

Write-Host "Updated $configPath"
Write-Host "  header:    $Header"
Write-Host "  inContent: $InContent"
Write-Host "  footer:    $Footer"

Set-Location $root
git add assets/js/config.js
git -c user.name="Brandon Sparks" -c user.email="laughingdragonsproductions@gmail.com" commit -m "TAG: AdSense display slot IDs (header, inContent, footer)"
if (-not $NoPush) {
    git push origin main
    Write-Host "Pushed to origin/main"
}
