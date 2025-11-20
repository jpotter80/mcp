#!/usr/bin/env bash
# sync_documentation.sh - Sync documentation from upstream repositories
# Usage: ./sync_documentation.sh --repo <url> --target <path> [--path <subdir>] [--branch <branch>]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
REPO_URL=""
TARGET_DIR=""
SUBPATH=""
BRANCH="main"

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") --repo <url> --target <path> [OPTIONS]

Sync documentation from an upstream git repository.

Required Arguments:
  --repo <url>          Git repository URL to sync from
  --target <path>       Target directory (relative to project root or absolute)

Optional Arguments:
  --path <subdir>       Subdirectory within repo to sync (e.g., 'docs' or 'manual')
  --branch <branch>     Branch to sync from (default: main)
  -h, --help           Show this help message

Examples:
  # Sync entire repo
  ./sync_documentation.sh --repo https://github.com/modularml/mojo --target source-documentation/mojo/manual

  # Sync specific subdirectory
  ./sync_documentation.sh --repo https://github.com/example/docs --target source-documentation/example/docs --path docs/guide

  # Sync from specific branch
  ./sync_documentation.sh --repo https://github.com/example/docs --target source-documentation/example/docs --branch develop

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO_URL="$2"
            shift 2
            ;;
        --target)
            TARGET_DIR="$2"
            shift 2
            ;;
        --path)
            SUBPATH="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
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
if [[ -z "$REPO_URL" ]]; then
    echo -e "${RED}Error: --repo is required${NC}" >&2
    show_help
    exit 1
fi

if [[ -z "$TARGET_DIR" ]]; then
    echo -e "${RED}Error: --target is required${NC}" >&2
    show_help
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve target directory (make absolute if relative)
if [[ "$TARGET_DIR" = /* ]]; then
    ABSOLUTE_TARGET="$TARGET_DIR"
else
    ABSOLUTE_TARGET="$PROJECT_ROOT/$TARGET_DIR"
fi

# Create temp directory for cloning
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

echo -e "${GREEN}==> Syncing documentation${NC}"
echo "    Repository: $REPO_URL"
echo "    Branch: $BRANCH"
echo "    Target: $ABSOLUTE_TARGET"
if [[ -n "$SUBPATH" ]]; then
    echo "    Subpath: $SUBPATH"
fi
echo ""

# Clone or update repository
if [[ -d "$ABSOLUTE_TARGET/.git" ]]; then
    echo -e "${YELLOW}==> Updating existing repository${NC}"
    cd "$ABSOLUTE_TARGET"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
else
    echo -e "${YELLOW}==> Cloning repository${NC}"
    
    if [[ -n "$SUBPATH" ]]; then
        # Use sparse checkout for subdirectory
        mkdir -p "$ABSOLUTE_TARGET"
        cd "$ABSOLUTE_TARGET"
        git init
        git remote add origin "$REPO_URL"
        git config core.sparseCheckout true
        echo "$SUBPATH/*" >> .git/info/sparse-checkout
        git fetch --depth=1 origin "$BRANCH"
        git checkout "$BRANCH"
    else
        # Clone entire repository
        git clone --depth=1 --branch "$BRANCH" "$REPO_URL" "$ABSOLUTE_TARGET"
    fi
fi

echo ""
echo -e "${GREEN}==> Sync completed successfully!${NC}"
echo "    Documentation available at: $ABSOLUTE_TARGET"

# Show summary
if [[ -n "$SUBPATH" ]]; then
    DOC_PATH="$ABSOLUTE_TARGET/$SUBPATH"
    if [[ -d "$DOC_PATH" ]]; then
        FILE_COUNT=$(find "$DOC_PATH" -type f | wc -l)
        echo "    Files in $SUBPATH: $FILE_COUNT"
    fi
else
    FILE_COUNT=$(find "$ABSOLUTE_TARGET" -type f -not -path '*/\.git/*' | wc -l)
    echo "    Total files: $FILE_COUNT"
fi
