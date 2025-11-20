#!/usr/bin/env bash
# scaffold_new_mcp.sh - Create a new MCP server structure from templates
# Usage: ./scaffold_new_mcp.sh --name <tool> --doc-type <type> [--format <format>] [--url-base <url>]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TOOL_NAME=""
DOC_TYPE=""
FORMAT="mdx"
FORMAT_EXT="mdx"
URL_BASE=""

# Help message
show_help() {
    cat << EOF
Usage: $(basename "$0") --name <tool> --doc-type <type> [OPTIONS]

Create a new MCP server structure from templates.

Required Arguments:
  --name <tool>           Tool name (e.g., 'duckdb', 'mojo')
  --doc-type <type>       Documentation type (e.g., 'manual', 'docs', 'guide')

Optional Arguments:
  --format <format>       Documentation format: mdx, markdown, rst (default: mdx)
  --url-base <url>        Base URL for documentation links
  -h, --help             Show this help message

Examples:
  # Create DuckDB docs server
  ./scaffold_new_mcp.sh --name duckdb --doc-type docs --format markdown --url-base https://duckdb.org/docs

  # Create Mojo manual server (MDX format)
  ./scaffold_new_mcp.sh --name mojo --doc-type manual --url-base https://docs.modular.com/mojo/manual

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            TOOL_NAME="$2"
            shift 2
            ;;
        --doc-type)
            DOC_TYPE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --url-base)
            URL_BASE="$2"
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
if [[ -z "$TOOL_NAME" ]]; then
    echo -e "${RED}Error: --name is required${NC}" >&2
    show_help
    exit 1
fi

if [[ -z "$DOC_TYPE" ]]; then
    echo -e "${RED}Error: --doc-type is required${NC}" >&2
    show_help
    exit 1
fi

# Set format extension
case "$FORMAT" in
    mdx)
        FORMAT_EXT="mdx"
        ;;
    markdown|md)
        FORMAT="markdown"
        FORMAT_EXT="md"
        ;;
    rst|restructuredtext)
        FORMAT="rst"
        FORMAT_EXT="rst"
        ;;
    *)
        echo -e "${RED}Error: Unsupported format '$FORMAT'. Use: mdx, markdown, or rst${NC}" >&2
        exit 1
        ;;
esac

# Generate names
MCP_NAME="${TOOL_NAME}-${DOC_TYPE}-mcp"
MCP_NAME_UPPER=$(echo "${TOOL_NAME}_${DOC_TYPE}_mcp" | tr '[:lower:]' '[:upper:]' | tr '-' '_')
DOC_TYPE_TITLE="$(echo "${TOOL_NAME} ${DOC_TYPE}" | sed 's/\b\(.\)/\u\1/g')"

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$PROJECT_ROOT/shared/templates"
SERVER_DIR="$PROJECT_ROOT/servers/$MCP_NAME"

# Check if server already exists
if [[ -d "$SERVER_DIR" ]]; then
    echo -e "${RED}Error: Server directory already exists: $SERVER_DIR${NC}" >&2
    exit 1
fi

# Check if templates exist
if [[ ! -d "$TEMPLATE_DIR" ]]; then
    echo -e "${RED}Error: Template directory not found: $TEMPLATE_DIR${NC}" >&2
    exit 1
fi

echo -e "${GREEN}==> Creating new MCP server: $MCP_NAME${NC}"
echo "    Tool: $TOOL_NAME"
echo "    Doc Type: $DOC_TYPE"
echo "    Format: $FORMAT ($FORMAT_EXT)"
echo "    Location: $SERVER_DIR"
echo ""

# Create directory structure
echo -e "${YELLOW}==> Creating directory structure${NC}"
mkdir -p "$SERVER_DIR/runtime"
mkdir -p "$SERVER_DIR/config"

# Function to replace placeholders in a file
replace_placeholders() {
    local file="$1"
    sed -i.bak \
        -e "s|{{TOOL_NAME}}|${TOOL_NAME}|g" \
        -e "s|{{DOC_TYPE}}|${DOC_TYPE}|g" \
        -e "s|{{MCP_NAME}}|${MCP_NAME}|g" \
        -e "s|{{MCP_NAME_UPPER}}|${MCP_NAME_UPPER}|g" \
        -e "s|{{DOC_TYPE_TITLE}}|${DOC_TYPE_TITLE}|g" \
        -e "s|{{FORMAT}}|${FORMAT}|g" \
        -e "s|{{FORMAT_EXT}}|${FORMAT_EXT}|g" \
        -e "s|{{URL_BASE}}|${URL_BASE}|g" \
        "$file"
    rm "${file}.bak"
}

# Copy and process templates
echo -e "${YELLOW}==> Copying templates${NC}"

# Copy search.py
if [[ -f "$TEMPLATE_DIR/search_template.py" ]]; then
    cp "$TEMPLATE_DIR/search_template.py" "$SERVER_DIR/runtime/search.py"
    replace_placeholders "$SERVER_DIR/runtime/search.py"
    echo "    ✓ Created runtime/search.py"
else
    echo -e "${RED}    ✗ Template not found: search_template.py${NC}" >&2
fi

# Copy server file
if [[ -f "$TEMPLATE_DIR/mcp_server_template.py" ]]; then
    SERVER_FILE="${TOOL_NAME}_${DOC_TYPE}_mcp_server.py"
    cp "$TEMPLATE_DIR/mcp_server_template.py" "$SERVER_DIR/runtime/$SERVER_FILE"
    replace_placeholders "$SERVER_DIR/runtime/$SERVER_FILE"
    echo "    ✓ Created runtime/$SERVER_FILE"
else
    echo -e "${RED}    ✗ Template not found: mcp_server_template.py${NC}" >&2
fi

# Copy processing config
if [[ -f "$TEMPLATE_DIR/processing_config_template.yaml" ]]; then
    cp "$TEMPLATE_DIR/processing_config_template.yaml" "$SERVER_DIR/config/processing_config.yaml"
    replace_placeholders "$SERVER_DIR/config/processing_config.yaml"
    echo "    ✓ Created config/processing_config.yaml"
else
    echo -e "${RED}    ✗ Template not found: processing_config_template.yaml${NC}" >&2
fi

# Copy server config
if [[ -f "$TEMPLATE_DIR/server_config_template.yaml" ]]; then
    cp "$TEMPLATE_DIR/server_config_template.yaml" "$SERVER_DIR/config/server_config.yaml"
    replace_placeholders "$SERVER_DIR/config/server_config.yaml"
    echo "    ✓ Created config/server_config.yaml"
else
    echo -e "${RED}    ✗ Template not found: server_config_template.yaml${NC}" >&2
fi

# Copy requirements.txt
if [[ -f "$TEMPLATE_DIR/requirements_template.txt" ]]; then
    cp "$TEMPLATE_DIR/requirements_template.txt" "$SERVER_DIR/requirements.txt"
    echo "    ✓ Created requirements.txt"
else
    echo -e "${RED}    ✗ Template not found: requirements_template.txt${NC}" >&2
fi

# Copy README.md
if [[ -f "$TEMPLATE_DIR/README_template.md" ]]; then
    cp "$TEMPLATE_DIR/README_template.md" "$SERVER_DIR/README.md"
    replace_placeholders "$SERVER_DIR/README.md"
    echo "    ✓ Created README.md"
else
    echo -e "${RED}    ✗ Template not found: README_template.md${NC}" >&2
fi

echo ""
echo -e "${GREEN}==> Server structure created successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Add documentation source to: source-documentation/$TOOL_NAME/$DOC_TYPE/"
echo "  2. Review and adjust: $SERVER_DIR/config/processing_config.yaml"
echo "  3. Review and adjust: $SERVER_DIR/config/server_config.yaml"
echo "  4. Build the server database:"
echo "     pixi run ${TOOL_NAME}-process"
echo "     pixi run ${TOOL_NAME}-embed"
echo "     pixi run ${TOOL_NAME}-consolidate"
echo "     pixi run ${TOOL_NAME}-load"
echo "     pixi run ${TOOL_NAME}-index"
echo "  5. Test the server:"
echo "     mcp dev $SERVER_DIR/runtime/${TOOL_NAME}_${DOC_TYPE}_mcp_server.py"
echo ""
echo "For more details, see: $SERVER_DIR/README.md"
