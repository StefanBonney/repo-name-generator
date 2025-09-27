# scripts/patch-activate.ps1
param([string]$File = ".\.venv\Scripts\Activate.ps1")

# Read whole file
$raw = Get-Content -Raw -LiteralPath $File

# 1) Drop the two problematic lines if present
$raw = [regex]::Replace($raw, '^\s*\$script:THIS_PATH\s*=.*\r?\n', '', 'Multiline')
$raw = [regex]::Replace(
    $raw,
    '^\s*\$script:BASE_DIR\s*=\s*Split-Path\s*\(Resolve-Path[^\n]*\)\s*-Parent\s*\r?\n',
    '',
    'Multiline'
)

# 2) Ensure the correct BASE_DIR line is present before the first function
if ($raw -notmatch '\$PSScriptRoot') {
    $insert = '$script:BASE_DIR = Split-Path $PSScriptRoot -Parent' + "`r`n`r`n"
    $raw = [regex]::Replace($raw, '^(?=function )', $insert, 'Multiline')
}

# Write back
Set-Content -LiteralPath $File -Value $raw
Write-Host "Patched $File"
