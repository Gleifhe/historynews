# rollback.ps1 — Emergency revert to last good commit and redeploy
# Usage: .\scripts\rollback.ps1
#        .\scripts\rollback.ps1 -Commits 2   # go back 2 commits

param(
    [int]$Commits = 1
)

if ($Commits -le 0) {
    Write-Host "Error: -Commits must be a positive integer." -ForegroundColor Red
    exit 1
}

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "`n=============================" -ForegroundColor Red
Write-Host "  EMERGENCY ROLLBACK" -ForegroundColor Red
Write-Host "=============================" -ForegroundColor Red

# Show what we're reverting
Write-Host "`nCurrent HEAD:" -ForegroundColor Yellow
git log --oneline -1

Write-Host "`nRolling back $Commits commit(s):" -ForegroundColor Yellow
git log --oneline -$($Commits + 1) | Select-Object -Skip 1

Write-Host "`nTarget:" -ForegroundColor Green
git log --oneline -1 --skip $Commits

# Confirm
$confirm = Read-Host "`nAre you sure? This will revert and force-push. (yes/no)"
if ($confirm -ne 'yes') {
    Write-Host "Cancelled." -ForegroundColor DarkGray
    exit 0
}

# Revert
Write-Host "`nReverting..." -ForegroundColor Yellow
git revert --no-commit HEAD~$($Commits - 1)..HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Host "Revert failed (merge conflict?). Resolve manually." -ForegroundColor Red
    git revert --abort 2>$null
    exit 1
}
git commit -m "Rollback: revert last $Commits commit(s)"

# Push
Write-Host "Pushing..." -ForegroundColor Yellow
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. Check authentication and network." -ForegroundColor Red
    exit 1
}

# Watch deploy
Write-Host "Watching deploy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
gh run list -L 1 -R gleifhe/historynews

Write-Host "`n=============================" -ForegroundColor Green
Write-Host "  ROLLBACK COMPLETE" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "  Site: https://red-stone-0ed2b5d10.7.azurestaticapps.net/"
