# Hook PostToolUse: corre pytest tras cada edición de archivo .py
# Diseñado para Windows nativo (PowerShell).
# Si pytest no está disponible o no hay tests, sale silenciosamente (no bloquea).

$callInput = [Console]::In.ReadToEnd() | ConvertFrom-Json
$filePath = $callInput.tool_input.file_path

# Solo correr si el archivo editado es .py
if (-not $filePath -or $filePath -notmatch '\.py$') {
    exit 0
}

# Si no hay directorio tests/, salir sin error (Fase 0-3 no tienen tests)
if (-not (Test-Path "tests")) {
    exit 0
}

# Correr pytest silenciosamente; si falla, devolver deny
$output = & pytest --tb=line -q 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "=== PostToolUse: pytest falló tras editar $filePath ==="
    Write-Host $output
    @{
        hookSpecificOutput = @{
            hookEventName = "PostToolUse"
            permissionDecision = "deny"
            permissionDecisionReason = "pytest falló tras edición. Corrige tests antes de continuar."
        }
    } | ConvertTo-Json
    exit 0
}

exit 0
