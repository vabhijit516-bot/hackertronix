# PowerShell script to push your profile README directly to your special GitHub repository
param (
    [string]$Username = "vabhijit516-bot"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Pushing Profile README to https://github.com/$Username/$Username" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$RemoteUrl = "https://github.com/$Username/$Username.git"

# Verify repository exists on GitHub
Write-Host "Checking if repository '$Username' exists on GitHub..." -ForegroundColor Yellow
$check = git ls-remote $RemoteUrl 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Repository '$Username' not found on GitHub!" -ForegroundColor Red
    Write-Host "Please create it first:" -ForegroundColor Yellow
    Write-Host "  1. Open https://github.com/new"
    Write-Host "  2. Set repository name to: $Username"
    Write-Host "  3. Set visibility to: Public"
    Write-Host "  4. Click 'Create repository'"
    Write-Host "Then run this script again!" -ForegroundColor Green
    exit 1
}

# Create a clean temporary directory in scratch for the profile repo
$TempDir = Join-Path $env:TEMP "gh-profile-push"
if (Test-Path $TempDir) { Remove-Item -Recurse -Force $TempDir }
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Copy PROFILE_README.md, banner.svg, and footer.svg
Copy-Item ".\PROFILE_README.md" (Join-Path $TempDir "README.md")
if (Test-Path ".\banner.svg") {
    Copy-Item ".\banner.svg" (Join-Path $TempDir "banner.svg")
}
if (Test-Path ".\footer.svg") {
    Copy-Item ".\footer.svg" (Join-Path $TempDir "footer.svg")
}

# Initialize and push
Push-Location $TempDir
try {
    git init
    git branch -M main
    git add .
    git commit -m "feat: upgrade GitHub profile with custom vector banner"
    git remote add origin $RemoteUrl
    git push -u origin main --force
    Write-Host "`nSUCCESS! Your GitHub Profile is now transformed at https://github.com/$Username" -ForegroundColor Green
}
finally {
    Pop-Location
    Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
}
