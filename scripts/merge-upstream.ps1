# Merge ColinGPT9/clips-studio into this fork. Run from the repo root.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (git remote get-url upstream 2>$null)) {
  Write-Host "Adding upstream remote..."
  git remote add upstream https://github.com/ColinGPT9/clips-studio.git
}

Write-Host "Fetching upstream..."
git fetch upstream

$branch = (git rev-parse --abbrev-ref HEAD)
Write-Host "Merging upstream/main into $branch..."
git merge upstream/main

Write-Host "Done. Resolve any conflicts, then run: cd ui; npm run dev"