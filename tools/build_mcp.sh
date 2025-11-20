#!/usr/bin/env bash
# build_mcp.sh - Build a specific MCP server database
# Usage: ./build_mcp.sh --mcp-name <name> [--skip-process] [--skip-embed] [--use-python]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MCP_NAME=""
SKIP_PROCESS=false
SKIP_EMBED=false
USE_PYTHON=false

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") --mcp-name <name> [OPTIONS]

Build a specific MCP server by running the full preprocessing and indexing pipeline.

Required Arguments:
  --mcp-name <name>       MCP server name (e.g., 'mojo', 'duckdb')

Optional Arguments:
  --skip-process          Skip preprocessing step (use existing processed docs)
  --skip-embed            Skip embedding generation (use existing embeddings)
  --use-python            Use direct python instead of pixi (for non-pixi environments)
  -h, --help             Show this help message

Pipeline Steps:
  1. Process:     Parse and chunk documentation
  2. Embed:       Generate embeddings using MAX server
  3. Consolidate: Combine chunks and embeddings into Parquet
  4. Load:        Load Parquet into DuckLake catalog
  5. Index:       Create indexed DuckDB with HNSW + FTS

Examples:
  # Full build using pixi
  ./build_mcp.sh --mcp-name mojo

  # Build without pixi (direct python)
  ./build_mcp.sh --mcp-name mojo --use-python

  # Skip preprocessing (reuse existing chunks)
  ./build_mcp.sh --mcp-name mojo --skip-process

  # Skip both preprocessing and embedding
  ./build_mcp.sh --mcp-name mojo --skip-process --skip-embed

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --mcp-name)
            MCP_NAME="$2"
            shift 2
            ;;
        --skip-process)
            SKIP_PROCESS=true
            shift
            ;;
        --skip-embed)
            SKIP_EMBED=true
            shift
            ;;
        --use-python)
            USE_PYTHON=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown argument '$1'${NC}" >&2
            show_help
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$MCP_NAME" ]]; then
    echo -e "${RED}Error: --mcp-name is required${NC}" >&2
    show_help
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if MCP server exists
SERVER_DIR="$PROJECT_ROOT/servers/${MCP_NAME}-manual-mcp"
if [[ ! -d "$SERVER_DIR" ]] && [[ ! -d "$PROJECT_ROOT/servers/${MCP_NAME}-docs-mcp" ]]; then
    # Try to find any matching server directory
    FOUND_SERVER=$(find "$PROJECT_ROOT/servers" -maxdepth 1 -type d -name "${MCP_NAME}-*-mcp" | head -n 1)
    if [[ -n "$FOUND_SERVER" ]]; then
        SERVER_DIR="$FOUND_SERVER"
    else
        echo -e "${RED}Error: No MCP server found for '$MCP_NAME'${NC}" >&2
        echo "Available servers:"
        ls -1 "$PROJECT_ROOT/servers" | grep -E "^${MCP_NAME}-.*-mcp$" || echo "  (none)"
        exit 1
    fi
fi

echo -e "${GREEN}==> Building MCP server: $MCP_NAME${NC}"
echo "    Server directory: $SERVER_DIR"
echo "    Using: $(if $USE_PYTHON; then echo 'Python'; else echo 'Pixi'; fi)"
echo ""

# Function to run a command
run_cmd() {
    local step_name="$1"
    local task_name="$2"
    
    echo -e "${YELLOW}==> Step: $step_name${NC}"
    
    if $USE_PYTHON; then
        # Map task names to python commands
        case "$task_name" in
            *-process)
                python -m shared.preprocessing.src.pipeline --mcp-name "$MCP_NAME"
                ;;
            *-embed|*-generate-embeddings)
                python shared/embedding/generate_embeddings.py --mcp-name "$MCP_NAME"
                ;;
            *-consolidate)
                python shared/embedding/consolidate_data.py --mcp-name "$MCP_NAME"
                ;;
            *-load)
                python shared/embedding/load_to_ducklake.py --mcp-name "$MCP_NAME"
                ;;
            *-index)
                python shared/embedding/create_indexes.py --mcp-name "$MCP_NAME"
                ;;
            *)
                echo -e "${RED}Error: Unknown task '$task_name'${NC}" >&2
                return 1
                ;;
        esac
    else
        # Use pixi
        pixi run "$task_name"
    fi
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✓ $step_name completed${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $step_name failed${NC}" >&2
        return 1
    fi
}

# Track start time
START_TIME=$(date +%s)

# Run pipeline steps
if ! $SKIP_PROCESS; then
    run_cmd "1. Process documentation" "${MCP_NAME}-process" || exit 1
else
    echo -e "${BLUE}==> Skipping: Process documentation${NC}"
    echo ""
fi

if ! $SKIP_EMBED; then
    run_cmd "2. Generate embeddings" "${MCP_NAME}-generate-embeddings" || exit 1
else
    echo -e "${BLUE}==> Skipping: Generate embeddings${NC}"
    echo ""
fi

run_cmd "3. Consolidate data" "${MCP_NAME}-consolidate" || exit 1
run_cmd "4. Load to DuckLake" "${MCP_NAME}-load" || exit 1
run_cmd "5. Create indexes" "${MCP_NAME}-index" || exit 1

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo -e "${GREEN}==> Build completed successfully!${NC}"
echo "    Duration: ${MINUTES}m ${SECONDS}s"
echo ""
echo -e "${BLUE}Server artifacts:${NC}"
echo "    Database: $SERVER_DIR/runtime/${MCP_NAME}_*.db"
echo "    Catalog:  $SERVER_DIR/runtime/${MCP_NAME}_*_catalog.ducklake"
echo ""
echo -e "${BLUE}Test the server:${NC}"
if $USE_PYTHON; then
    echo "    python $SERVER_DIR/runtime/*_mcp_server.py"
else
    echo "    pixi run mcp-dev"
fi
