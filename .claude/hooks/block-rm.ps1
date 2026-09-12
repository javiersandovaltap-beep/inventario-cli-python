# Hook PreToolUse: bloquea comandos destructivos en Bash y PowerShell.
# Casos bloqueados: rm -rf, Remove-Item -Recurse, git push --force/-f,
# DROP TABLE, TRUNCATE, del /s (cmd.exe), Format-Volume, diskpart clean.
# Diseñado para Windows nativo (sin WSL2), corre en PowerShell.

$callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
$command = $callInput.tool_input.command

# Si no hay command (no es invocación Bash), salir silenciosamente
if (-not $command) {
    exit 0
}

# Patrones destructivos (case-insensitive)
$patrones = @(
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

foreach ($patron in $patrones) {
    if ($command -match $patron) {
        @{
            hookSpecificOutput = @{
                hookEventName = "PreToolUse"
                permissionDecision = "deny"
                permissionDecisionReason = "Comando destructivo bloqueado por hook: patron coincidente = $patron"
            }
        } | ConvertTo-Json
        exit 0
    }
}

# Ningún patrón coincidió: permitir
exit 0
