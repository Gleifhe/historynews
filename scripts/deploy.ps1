# deploy.ps1 — One-command validation, build, and deploy pipeline
# Usage: .\scripts\deploy.ps1
#        .\scripts\deploy.ps1 -SkipValidation
#        .\scripts\deploy.ps1 -DryRun

param(
    [switch]$SkipValidation,
    [switch]$DryRun,
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  HISTORY NEWS DEPLOY" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan

# Step 1: Validate
if (-not $SkipValidation) {
    Write-Host "`n[1/5] Validating articles..." -ForegroundColor Yellow
    python scripts/validate-all.py --errors-only
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n❌ Validation failed. Fix errors before deploying." -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Validation passed" -ForegroundColor Green
} else {
    Write-Host "`n[1/5] Skipping validation" -ForegroundColor DarkGray
}

# Step 2: Audit images
Write-Host "`n[2/5] Auditing images..." -ForegroundColor Yellow
python scripts/audit-images.py
Write-Host "✅ Image audit complete" -ForegroundColor Green

# Step 3: Hugo build
Write-Host "`n[3/5] Building site..." -ForegroundColor Yellow
hugo --minify
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Hugo build failed." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build successful" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n[DRY RUN] Skipping commit and push." -ForegroundColor DarkGray
    exit 0
}

# Step 4: Git commit
Write-Host "`n[4/5] Committing changes..." -ForegroundColor Yellow
git add -A
if (-not $Message) {
    $articleCount = (Get-ChildItem content/articles/*.md | Where-Object { $_.Name -ne '_index.md' }).Count
    $imageCount = (Get-ChildItem static/images/articles/*.jpg -ErrorAction SilentlyContinue).Count
    $Message = "Update site: $articleCount articles, $imageCount images"
}
git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Host "  No changes to commit" -ForegroundColor DarkGray
}

# Step 5: Push and watch
Write-Host "`n[5/5] Pushing to GitHub..." -ForegroundColor Yellow
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPush failed. Check authentication and network." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Pushed. Watching deploy..." -ForegroundColor Green

# Watch the deployment
Start-Sleep -Seconds 5
gh run list -L 1 -R gleifhe/historynews

Write-Host "`n=============================" -ForegroundColor Cyan
Write-Host "  DEPLOY COMPLETE" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "  Site: https://red-stone-0ed2b5d10.7.azurestaticapps.net/" -ForegroundColor White
