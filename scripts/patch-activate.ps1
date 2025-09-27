$ErrorActionPreference = 'Stop'

Write-Host "Patching virtualenv activate.ps1 if needed..." -ForegroundColor Cyan

function Get-VenvPath {
  try {
    $p = (& poetry env info -p).Trim()
    if ($p) { return $p }
  } catch { }
  $fallback = Join-Path (Get-Location) '.venv'
  return $fallback
}

$venvPath = Get-VenvPath
$activate = Join-Path $venvPath 'Scripts/activate.ps1'

if (-not (Test-Path -LiteralPath $activate)) {
  Write-Host "activate.ps1 not found at: $activate" -ForegroundColor Yellow
  Write-Host "Nothing to patch. If you haven't installed yet, run 'poetry install' first." -ForegroundColor Yellow
  exit 0
}

$content = Get-Content -LiteralPath $activate -Raw
if ($content -match '\$PSScriptRoot') {
  Write-Host "activate.ps1 already uses \$PSScriptRoot. No patch needed." -ForegroundColor Green
  exit 0
}

# Perform a safe, line-wise patch: replace the line that sets $script:THIS_PATH and the following BASE_DIR line
$lines = Get-Content -LiteralPath $activate
[System.Collections.Generic.List[string]]$out = New-Object System.Collections.Generic.List[string]
$patched = $false
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match '\$myinvocation\.mycommand\.path') {
    # Replace with a robust BASE_DIR using $PSScriptRoot and skip the next BASE_DIR line if present
    $out.Add('$script:BASE_DIR = Split-Path $PSScriptRoot -Parent')
    if ($i + 1 -lt $lines.Count -and $lines[$i + 1] -match '^\$script:BASE_DIR') { $i++ }
    $patched = $true
  } else {
    $out.Add($lines[$i])
  }
}

if (-not $patched) {
  # As a fallback, if we didn't see the myinvocation line, try replacing an existing BASE_DIR assignment
  $replaced = $false
  for ($j = 0; $j -lt $out.Count; $j++) {
    if ($out[$j] -match '^\$script:BASE_DIR') {
      $out[$j] = '$script:BASE_DIR = Split-Path $PSScriptRoot -Parent'
      $replaced = $true
      break
    }
  }
  $patched = $replaced
}

if ($patched) {
  Set-Content -LiteralPath $activate -Value $out -NoNewline
  Write-Host "Patched: $activate" -ForegroundColor Green
} else {
  Write-Host "No suitable spot to patch found; leaving file unchanged." -ForegroundColor Yellow
}
