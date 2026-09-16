#!/usr/bin/env bash
# scripts/docker-cleanup.sh -- Docker hygiene script (monthly).
# inventario-cli-python project.
#
# Prunes stopped containers, dangling images, and unused networks by default.
# Volumes and build cache are opt-in (--volumes, --builder) to avoid destroying
# persistent data or build state by accident.
#
# Idempotent: safe to run multiple times (no-op if nothing to clean).
# Signal handling: SIGINT/SIGTERM trapped, exits 130/143 (each prune is atomic).
#
# Usage: scripts/docker-cleanup.sh [--dry-run] [--verbose] [--volumes] [--builder] [--help]
#
# Exit codes:
#   0   success (nothing to clean is also success)
#   1   docker daemon not running or docker command failed
#   2   docker not in PATH
#   130 interrupted via SIGINT
#   143 interrupted via SIGTERM
#
# ASCII policy: code file, ASCII-only (project convention).
# Language: user-facing messages in English (matches scripts/ascii_cleanup.py).

set -euo pipefail

# ---- Defaults
DRY_RUN=false
VERBOSE=false
PRUNE_VOLUMES=false
PRUNE_BUILDER=false

# ---- Usage
usage() {
    cat <<'USAGE'
Usage: scripts/docker-cleanup.sh [--dry-run] [--verbose] [--volumes] [--builder] [--help]

Docker hygiene script (monthly). Prunes stopped containers, dangling images,
unused networks, and (opt-in) volumes and build cache.

Options:
  --dry-run    Print what would be cleaned without doing it.
  --verbose    Print per-step docker output (default: quiet).
  --volumes    ALSO prune unused volumes. DESTRUCTIVE: removes named volumes
               with persistent data not referenced by any container.
               Default: volumes SKIPPED.
  --builder    ALSO prune build cache (docker builder prune -af).
  --help, -h   Show this help and exit.

Exit codes:
  0    success (nothing to clean is also success)
  1    docker daemon not running or docker command failed
  2    docker not in PATH
  130  SIGINT
  143  SIGTERM
USAGE
}

# ---- Argument parsing
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=true;          shift ;;
        --verbose)  VERBOSE=true;           shift ;;
        --volumes)  PRUNE_VOLUMES=true;     shift ;;
        --builder)  PRUNE_BUILDER=true;     shift ;;
        --help|-h)  usage; exit 0 ;;
        *)          echo "ERROR: unknown option: $1" >&2; usage >&2; exit 1 ;;
    esac
done

# ---- Signal handling (each docker prune is atomic; no partial state to clean)
abort() {
    echo "" >&2
    echo "Aborted by signal. Each docker prune is atomic; no partial state." >&2
    exit 130
}
trap 'abort' SIGINT
trap 'abort' SIGTERM

# ---- Step 0: docker dependency
if ! command -v docker >/dev/null 2>&1; then
    echo "ERROR: docker not found in PATH." >&2
    echo "Install Docker Desktop (Windows/macOS) or Docker Engine (Linux)." >&2
    exit 2
fi

# ---- Step 1: docker daemon alive
if ! docker info >/dev/null 2>&1; then
    echo "ERROR: docker daemon not responding." >&2
    echo "Start Docker Desktop or run: systemctl start docker" >&2
    exit 1
fi

# ---- Helper: dry-run-aware prune runner
run_prune() {
    local label="$1"; shift
    local subcmd="$1"; shift
    local flags=("$@")

    if $DRY_RUN; then
        echo "  [dry-run] would run: docker ${flags[*]}"
        case "${subcmd}" in
            container)
                docker container ls -a --filter status=exited --filter status=created \
                    --format '  {{.ID}} {{.Image}} {{.Status}}' 2>/dev/null || true
                ;;
            image)
                docker images --filter dangling=true \
                    --format '  {{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}' 2>/dev/null || true
                ;;
            network)
                docker network ls --filter type=unused 2>/dev/null || true
                ;;
            volume)
                docker volume ls --filter dangling=true 2>/dev/null || true
                ;;
            builder)
                docker builder du 2>/dev/null || echo "  (no size preview available)"
                ;;
        esac
        echo "  [dry-run] ${label}: no action taken"
        return 0
    fi

    if $VERBOSE; then
        echo "  >>> docker ${flags[*]}"
        docker "${flags[@]}" || true
    else
        if docker "${flags[@]}" >/dev/null 2>&1; then
            echo "  [OK] ${label}"
        else
            echo "  [WARN] ${label}: docker command failed (continuing)"
        fi
    fi
}

# ---- Header
echo "=== Docker cleanup ==="
SERVER_VER=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo unknown)
echo "Daemon: ${SERVER_VER}"
MODE_LINE="Mode: "
if $DRY_RUN; then MODE_LINE+="DRY-RUN"; else MODE_LINE+="APPLY"; fi
if $PRUNE_VOLUMES; then MODE_LINE+=" + VOLUMES"; else MODE_LINE+=" (volumes skipped)"; fi
if $PRUNE_BUILDER; then MODE_LINE+=" + BUILDER"; else MODE_LINE+=" (builder skipped)"; fi
echo "${MODE_LINE}"
echo ""

# ---- Prunes (idempotent: no-op if nothing to clean)
echo "1/5 Stopped containers..."
run_prune "container prune" container container prune -f

echo "2/5 Dangling images..."
run_prune "image prune"    image     image prune -f

echo "3/5 Unused networks..."
run_prune "network prune"  network   network prune -f

if $PRUNE_VOLUMES; then
    echo "4/5 Unused volumes (DESTRUCTIVE)..."
    run_prune "volume prune"  volume  volume prune -f
else
    echo "4/5 Unused volumes -- SKIPPED (use --volumes to enable)"
fi

if $PRUNE_BUILDER; then
    echo "5/5 Build cache..."
    run_prune "builder prune" builder builder prune -af
else
    echo "5/5 Build cache -- SKIPPED (use --builder to enable)"
fi

echo ""
echo "=== Cleanup complete ==="
exit 0
