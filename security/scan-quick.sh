#!/bin/bash
# =============================================================================
# Osprey Quick Security Check
# Scan rapido para usar durante desenvolvimento (< 30 segundos)
# Uso: ./security/scan-quick.sh [arquivo_ou_diretorio]
# =============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET="${1:-$PROJECT_ROOT/backend}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Quick Security Scan: $TARGET${NC}"
echo "---"

ISSUES=0

# 1. Bandit (high severity only, fast)
echo -e "\n${YELLOW}[Bandit] High-severity issues:${NC}"
BANDIT_OUT=$(bandit -r "$TARGET" \
    --severity-level high \
    -f txt \
    -x ".venv,__pycache__,node_modules" \
    2>/dev/null || true)

BANDIT_COUNT=$(echo "$BANDIT_OUT" | grep -c ">> Issue:" 2>/dev/null || echo "0")
if [ "$BANDIT_COUNT" -gt 0 ]; then
    echo "$BANDIT_OUT" | grep -A2 ">> Issue:" 2>/dev/null || true
    ISSUES=$((ISSUES + BANDIT_COUNT))
else
    echo -e "${GREEN}  Clean${NC}"
fi

# 2. Hardcoded secrets (fast grep)
echo -e "\n${YELLOW}[Secrets] Checking for hardcoded credentials:${NC}"
SECRET_HITS=$(grep -rn \
    'sk_live_\|sk_test_\|pk_live_\|AKIA\|password.*=.*"[^"]\{8,\}"' \
    "$TARGET" \
    --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    --exclude-dir=".venv" --exclude-dir="node_modules" --exclude-dir="__pycache__" \
    2>/dev/null | grep -v "os.environ\|os.getenv\|process.env\|import.meta.env\|\.get(\|hashed\|bcrypt\|hash" || true)

if [ -n "$SECRET_HITS" ]; then
    echo -e "${RED}$SECRET_HITS${NC}"
    ISSUES=$((ISSUES + $(echo "$SECRET_HITS" | wc -l)))
else
    echo -e "${GREEN}  Clean${NC}"
fi

# 3. NoSQL injection patterns
echo -e "\n${YELLOW}[NoSQL] Checking for injection patterns:${NC}"
NOSQL_HITS=$(grep -rn \
    '\$where\|\$regex.*request\|find_one.*json()' \
    "$TARGET" \
    --include="*.py" \
    --exclude-dir=".venv" --exclude-dir="__pycache__" \
    2>/dev/null || true)

if [ -n "$NOSQL_HITS" ]; then
    echo -e "${RED}$NOSQL_HITS${NC}"
    ISSUES=$((ISSUES + $(echo "$NOSQL_HITS" | wc -l)))
else
    echo -e "${GREEN}  Clean${NC}"
fi

# 4. Unsafe functions
echo -e "\n${YELLOW}[Code] Checking for unsafe functions:${NC}"
UNSAFE_HITS=$(grep -rn \
    '\beval(\|\bexec(\|pickle\.loads\|yaml\.load(' \
    "$TARGET" \
    --include="*.py" \
    --exclude-dir=".venv" --exclude-dir="__pycache__" \
    2>/dev/null || true)

if [ -n "$UNSAFE_HITS" ]; then
    echo -e "${RED}$UNSAFE_HITS${NC}"
    ISSUES=$((ISSUES + $(echo "$UNSAFE_HITS" | wc -l)))
else
    echo -e "${GREEN}  Clean${NC}"
fi

# Summary
echo -e "\n---"
if [ "$ISSUES" -gt 0 ]; then
    echo -e "${RED}Found $ISSUES potential issues. Run ./security/scan-all.sh for full report.${NC}"
    exit 1
else
    echo -e "${GREEN}Quick scan passed - no high-severity issues detected.${NC}"
    exit 0
fi
