#!/bin/bash
# =============================================================================
# Osprey Single File Security Scanner
# Analisa um arquivo específico para vulnerabilidades
# Uso: ./security/scan-file.sh <caminho_do_arquivo>
# =============================================================================

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: ./security/scan-file.sh <file_path>"
    echo "Example: ./security/scan-file.sh backend/server.py"
    exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
    echo "Error: File not found: $FILE"
    exit 1
fi

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Security scan: $FILE${NC}"
echo "---"

EXT="${FILE##*.}"
ISSUES=0

case "$EXT" in
    py)
        echo -e "\n${YELLOW}[Bandit] Python security analysis:${NC}"
        bandit "$FILE" -f txt 2>/dev/null || true

        echo -e "\n${YELLOW}[Patterns] Osprey-specific checks:${NC}"

        echo -e "\n  ${YELLOW}NoSQL injection:${NC}"
        grep -n 'find_one\|find(\|update_one\|delete_one\|aggregate' "$FILE" 2>/dev/null | head -20 || echo "  None"

        echo -e "\n  ${YELLOW}Auth checks:${NC}"
        grep -n 'get_current_user\|verify_token\|Depends.*auth\|Authorization' "$FILE" 2>/dev/null | head -20 || echo "  None"

        echo -e "\n  ${YELLOW}Unsafe operations:${NC}"
        grep -n 'eval(\|exec(\|pickle\|subprocess\|os\.system\|yaml\.load(' "$FILE" 2>/dev/null || echo "  None"

        echo -e "\n  ${YELLOW}Secrets/credentials:${NC}"
        grep -n 'secret\|password\|api_key\|token.*=' "$FILE" 2>/dev/null | grep -v 'os.environ\|os.getenv\|\.get(\|import\|#\|def \|"""' || echo "  None"
        ;;

    ts|tsx|js|jsx)
        echo -e "\n${YELLOW}[Patterns] Frontend security checks:${NC}"

        echo -e "\n  ${YELLOW}XSS (dangerouslySetInnerHTML):${NC}"
        grep -n 'dangerouslySetInnerHTML\|innerHTML\|v-html' "$FILE" 2>/dev/null || echo "  None"

        echo -e "\n  ${YELLOW}Exposed secrets:${NC}"
        grep -n 'sk_\|api_key\|secret\|password\|PRIVATE' "$FILE" 2>/dev/null | grep -v 'process.env\|import.meta.env\|VITE_\|NEXT_PUBLIC_' || echo "  None"

        echo -e "\n  ${YELLOW}Unsafe URL handling:${NC}"
        grep -n 'window\.location.*=\|document\.location.*=\|eval(' "$FILE" 2>/dev/null || echo "  None"

        echo -e "\n  ${YELLOW}Insecure localStorage usage:${NC}"
        grep -n 'localStorage.*token\|localStorage.*secret\|localStorage.*password' "$FILE" 2>/dev/null || echo "  None"
        ;;

    *)
        echo "Unsupported file type: .$EXT"
        echo "Supported: .py .ts .tsx .js .jsx"
        exit 1
        ;;
esac

echo -e "\n${BLUE}---${NC}"
echo -e "${GREEN}Scan complete for: $FILE${NC}"
