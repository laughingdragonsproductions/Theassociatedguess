#Requires -Version 5.1
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Message
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

git add .
git status

if (-not (git diff --cached --quiet)) {
    git commit -m $Message
    git push -u origin main
    Write-Host "Pushed to main. Connect Cloudflare Pages to this repo for deploy."
} else {
    Write-Host "Nothing to commit."
}

$tagFbPipeline = "G:\LocalAIagent\desktop-agent\integrations\tag_facebook_pipeline.py"
if (Test-Path $tagFbPipeline) {
    Write-Host "Syncing TAG Facebook posts pool and queueing missing articles..."
    & py -3 $tagFbPipeline --full --max-age-days 60
}
