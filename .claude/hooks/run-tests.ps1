# PostToolUse hook: runs pytest after each .py file edit.
# Designed for native Windows (PowerShell).
# If pytest is not available or no tests/ directory exists, exits silently (does not block).

$callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
$filePath = $callInput.tool_input.file_path

# Only run if the edited file is .py
if (-not $filePath -or $filePath -notmatch '\.py$') {
    exit 0
}

# If no tests/ directory exists, exit without error (Fase 0-3 have no tests yet)
if (-not (Test-Path "tests")) {
    exit 0
}

# Run pytest silently; if it fails, return deny
$output = & pytest --tb=line -q 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "=== PostToolUse: pytest failed after editing $filePath ==="
    Write-Host $output
    @{
        hookSpecificOutput = @{
            hookEventName = "PostToolUse"
            permissionDecision = "deny"
            permissionDecisionReason = "pytest failed after edit. Fix tests before continuing."
        }
    } | ConvertTo-Json
    exit 0
}

exit 0
