#!/bin/bash
# =============================================================================
# Osprey Semgrep Scanner
# Usa regras customizadas + regras da comunidade
# Uso: ./security/scan-semgrep.sh [--custom-only | --full]
# =============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES_FILE="$PROJECT_ROOT/security/semgrep-osprey-rules.yaml"
REPORT_DIR="$PROJECT_ROOT/security/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$REPORT_DIR"

MODE="${1:---custom-only}"

echo -e "${BLUE}Osprey Semgrep Scanner (Mode: $MODE)${NC}"
echo "---"

# 1. Custom Osprey rules
echo -e "\n${YELLOW}[1] Running Osprey-specific rules...${NC}"
CUSTOM_REPORT="$REPORT_DIR/semgrep_custom_${TIMESTAMP}.json"

semgrep scan \
    --config "$RULES_FILE" \
    --json \
    --output "$CUSTOM_REPORT" \
    "$PROJECT_ROOT/backend/" \
    2>/dev/null || true

CUSTOM_COUNT=$(python3 -c "import json; d=json.load(open('$CUSTOM_REPORT')); print(len(d.get('results',[])))" 2>/dev/null || echo "0")
echo -e "  Custom rules: ${CUSTOM_COUNT} findings"

if [ "$MODE" = "--full" ]; then
    # 2. Community rules (slower, requires internet)
    echo -e "\n${YELLOW}[2] Running community security rules...${NC}"
    COMMUNITY_REPORT="$REPORT_DIR/semgrep_community_${TIMESTAMP}.json"

    semgrep scan \
        --config "p/python" \
        --config "p/jwt" \
        --config "p/owasp-top-ten" \
        --json \
        --output "$COMMUNITY_REPORT" \
        "$PROJECT_ROOT/backend/" \
        2>/dev/null || true

    COMMUNITY_COUNT=$(python3 -c "import json; d=json.load(open('$COMMUNITY_REPORT')); print(len(d.get('results',[])))" 2>/dev/null || echo "0")
    echo -e "  Community rules: ${COMMUNITY_COUNT} findings"
fi

# Summary
echo -e "\n${BLUE}Reports saved to: $REPORT_DIR/${NC}"

if [ "$CUSTOM_COUNT" -gt 0 ]; then
    echo -e "\n${YELLOW}Top findings:${NC}"
    python3 -c "
import json
data = json.load(open('$CUSTOM_REPORT'))
for r in data.get('results', [])[:10]:
    sev = r.get('extra',{}).get('severity','?')
    msg = r.get('extra',{}).get('message','').strip()[:80]
    path = r.get('path','')
    line = r.get('start',{}).get('line','?')
    print(f'  [{sev}] {path}:{line} - {msg}')
" 2>/dev/null || true
fi
