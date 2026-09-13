# PreToolUse hook: blocks destructive Bash and PowerShell commands.
# Blocked cases: rm -rf, Remove-Item -Recurse, git push --force/-f,
# DROP TABLE, TRUNCATE, del /s (cmd.exe), Format-Volume, diskpart clean.
# Designed for native Windows (no WSL2), runs in PowerShell.

$callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
$command = $callInput.tool_input.command

# If no command present (not a Bash invocation), exit silently
if (-not $command) {
    exit 0
}

# Destructive patterns (case-insensitive)
$patterns = @(
    'rm\s+-rf',
    'Remove-Item.*-Recurse',
    'git\s+push\s+--force',
    'git\s+push\s+-f\b',
    'DROP\s+TABLE',
    'TRUNCATE',
    '\bDEL\s+/[sS]\b',
    'Format-Volume',
    'diskpart.*clean'
)

foreach ($pattern in $patterns) {
    if ($command -match $pattern) {
        @{
            hookSpecificOutput = @{
                hookEventName = "PreToolUse"
                permissionDecision = "deny"
                permissionDecisionReason = "Destructive command blocked by hook: matching pattern = $pattern"
            }
        } | ConvertTo-Json
        exit 0
    }
}

# No pattern matched: allow
exit 0
