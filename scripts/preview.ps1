#Requires -Version 5.1
Set-Location (Split-Path $PSScriptRoot -Parent)
Write-Host "The Associated Guess - preview at http://localhost:8081/ (Ctrl+C to stop)"
python -m http.server 8081
