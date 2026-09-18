# Emulate Brandon ADSENSE-MANUAL.md pre-review verification for TAG.
# Console steps (Auto ads off, EU CMP, Sites review) still require AdSense login.
param(
    [switch]$Live,
    [string]$Domain = "theassociatedguess.com"
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent
$fail = 0

function Test-FileContains {
    param([string]$Path, [string]$Pattern, [string]$Label)
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "FAIL $Label - missing $Path" -ForegroundColor Red
        $script:fail++
        return
    }
    $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
    if ($text -notmatch $Pattern) {
        Write-Host "FAIL $Label" -ForegroundColor Red
        $script:fail++
    } else {
        Write-Host "OK   $Label" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== TAG Brandon checklist (automated) ===" -ForegroundColor Cyan

$config = Join-Path $repo "assets\js\config.js"
Test-FileContains $config "2936560577" "Header slot ID"
Test-FileContains $config "7102817128" "In-content slot ID"
Test-FileContains $config "4852277474" "Footer slot ID"
Test-FileContains $config "ca-pub-7048606415692002" "Publisher ID"

foreach ($page in @("privacy.html", "terms.html", "search.html")) {
    $p = Join-Path $repo $page
    $text = Get-Content -LiteralPath $p -Raw -Encoding UTF8
    if ($text -match "adsbygoogle") {
        Write-Host "FAIL $page contains adsbygoogle" -ForegroundColor Red
        $fail++
    } else {
        Write-Host "OK   $page ad-free" -ForegroundColor Green
    }
}

foreach ($page in @("about.html", "contact.html", "editorial-standards.html", "corrections.html", "newsroom.html", "feed.xml", "ads.txt")) {
    if (Test-Path (Join-Path $repo $page)) {
        Write-Host "OK   $page exists" -ForegroundColor Green
    } else {
        Write-Host "FAIL $page missing" -ForegroundColor Red
        $fail++
    }
}

$articlesJson = Join-Path $repo "data\articles.json"
$data = Get-Content -LiteralPath $articlesJson -Raw -Encoding UTF8 | ConvertFrom-Json
$total = $data.articles.Count
$indexable = @($data.articles | Where-Object { $_.indexable }).Count
$pct = [math]::Round(100 * $indexable / $total)
$ratioMsg = "INFO Indexable: $indexable / $total ($pct pct)"
$ratioColor = if ($pct -ge 75) { "Green" } else { "Yellow" }
Write-Host $ratioMsg -ForegroundColor $ratioColor
if ($pct -lt 75) { $fail++ }

Write-Host ""
Write-Host "--- adsense_readiness.py ---" -ForegroundColor Cyan
& py -3 G:\LocalAIagent\desktop-agent\integrations\adsense_readiness.py --site tag
if ($LASTEXITCODE -ne 0) { $fail++ }

if ($Live) {
    Write-Host ""
    Write-Host "--- Live checks ($Domain) ---" -ForegroundColor Cyan
    try {
        $ads = Invoke-WebRequest -Uri "https://$Domain/ads.txt" -UseBasicParsing -TimeoutSec 20
        if ($ads.Content -match "pub-7048606415692002") {
            Write-Host "OK   live ads.txt" -ForegroundColor Green
        } else {
            Write-Host "FAIL live ads.txt" -ForegroundColor Red
            $fail++
        }
    } catch {
        Write-Host "FAIL live ads.txt - $($_.Exception.Message)" -ForegroundColor Red
        $fail++
    }
    try {
        $homePage = Invoke-WebRequest -Uri "https://$Domain/" -UseBasicParsing -TimeoutSec 20
        if ($homePage.Content -notmatch "site-disclaimer") {
            Write-Host "OK   homepage disclaimer moved off header" -ForegroundColor Green
        } else {
            Write-Host "WARN homepage still has header disclaimer (push pending?)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "WARN live homepage - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "--- Brandon console (manual login) ---" -ForegroundColor Yellow
Write-Host "  [ ] AdSense -> Auto ads -> OFF for $Domain"
Write-Host "  [ ] AdSense -> Privacy and messaging -> EU regulations -> Publish"
Write-Host "  [ ] AdSense -> Sites -> Add/verify $Domain -> Request review"
Write-Host "  [ ] Search Console -> Verify + submit sitemap.xml"

if ($fail -gt 0) {
    Write-Host ""
    Write-Host "Automated checks FAILED: $fail issue(s)" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "Automated checks PASSED - code-side ready for console + review." -ForegroundColor Green
exit 0
