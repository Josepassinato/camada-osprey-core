#!/bin/bash
# =============================================================================
# Osprey Security Scanner - Arsenal Completo
# Executa todos os scans de seguranca disponíveis
# Uso: ./security/scan-all.sh [--quick | --full]
# =============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
REPORT_DIR="$PROJECT_ROOT/security/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

mkdir -p "$REPORT_DIR"

MODE="${1:---quick}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Osprey Security Scanner              ${NC}"
echo -e "${BLUE}  Mode: $MODE                          ${NC}"
echo -e "${BLUE}  Time: $(date)                        ${NC}"
echo -e "${BLUE}========================================${NC}"

TOTAL_ISSUES=0
CRITICAL_ISSUES=0

# ---------------------------------------------------------------------------
# 1. BANDIT - Python Security Linter
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[1/6] Running Bandit (Python Security Linter)...${NC}"
BANDIT_REPORT="$REPORT_DIR/bandit_${TIMESTAMP}.json"

if bandit -r "$BACKEND_DIR" \
    -f json \
    -o "$BANDIT_REPORT" \
    --severity-level medium \
    -x "$BACKEND_DIR/.venv,$BACKEND_DIR/__pycache__" \
    2>/dev/null; then
    echo -e "${GREEN}  No issues found${NC}"
else
    BANDIT_COUNT=$(python3 -c "import json; d=json.load(open('$BANDIT_REPORT')); print(len(d.get('results',[])))" 2>/dev/null || echo "?")
    BANDIT_HIGH=$(python3 -c "import json; d=json.load(open('$BANDIT_REPORT')); print(len([r for r in d.get('results',[]) if r['issue_severity']=='HIGH']))" 2>/dev/null || echo "0")
    echo -e "${RED}  Found $BANDIT_COUNT issues ($BANDIT_HIGH HIGH severity)${NC}"
    echo -e "  Report: $BANDIT_REPORT"
    TOTAL_ISSUES=$((TOTAL_ISSUES + ${BANDIT_COUNT:-0}))
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + ${BANDIT_HIGH:-0}))
fi

# ---------------------------------------------------------------------------
# 2. BANDIT - Specific checks for Osprey patterns
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[2/6] Running Bandit Osprey-Specific Checks...${NC}"
BANDIT_OSPREY="$REPORT_DIR/bandit_osprey_${TIMESTAMP}.txt"

bandit -r "$BACKEND_DIR" \
    --tests B608,B301,B303,B324,B501,B502,B503,B506,B601,B602,B603,B604,B605,B607,B609,B610,B611,B701,B702 \
    -f txt \
    -o "$BANDIT_OSPREY" \
    2>/dev/null || true

# B608 = SQL/NoSQL injection
# B301 = pickle deserialization
# B303 = insecure hash (MD5/SHA1)
# B324 = insecure hash usage
# B501-503 = insecure SSL/TLS
# B506 = unsafe YAML load
# B601-611 = shell injection / subprocess
# B701-702 = Jinja2 template injection

if [ -s "$BANDIT_OSPREY" ]; then
    OSPREY_COUNT=$(grep -c ">> Issue:" "$BANDIT_OSPREY" 2>/dev/null || echo "0")
    echo -e "${RED}  Found $OSPREY_COUNT Osprey-specific issues${NC}"
    echo -e "  Report: $BANDIT_OSPREY"
else
    echo -e "${GREEN}  No Osprey-specific issues found${NC}"
fi

# ---------------------------------------------------------------------------
# 3. PIP-AUDIT - Python Dependency Vulnerabilities
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[3/6] Running pip-audit (Dependency Vulnerabilities)...${NC}"
PIPAUDIT_REPORT="$REPORT_DIR/pip_audit_${TIMESTAMP}.json"

if pip-audit -r "$BACKEND_DIR/requirements.txt" \
    --format json \
    --output "$PIPAUDIT_REPORT" \
    2>/dev/null; then
    echo -e "${GREEN}  No vulnerable dependencies found${NC}"
else
    VULN_COUNT=$(python3 -c "import json; d=json.load(open('$PIPAUDIT_REPORT')); print(len(d.get('dependencies',[d for d in d if d.get('vulns')])))" 2>/dev/null || echo "?")
    echo -e "${RED}  Found vulnerable dependencies${NC}"
    echo -e "  Report: $PIPAUDIT_REPORT"
fi

# ---------------------------------------------------------------------------
# 4. NPM AUDIT - Frontend Dependency Vulnerabilities
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[4/6] Running npm audit (Frontend Dependencies)...${NC}"
NPM_REPORT="$REPORT_DIR/npm_audit_${TIMESTAMP}.json"

if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package-lock.json" ]; then
    cd "$FRONTEND_DIR"
    npm audit --json > "$NPM_REPORT" 2>/dev/null || true
    cd "$PROJECT_ROOT"

    NPM_VULNS=$(python3 -c "import json; d=json.load(open('$NPM_REPORT')); print(d.get('metadata',{}).get('vulnerabilities',{}).get('total',0))" 2>/dev/null || echo "?")
    NPM_CRITICAL=$(python3 -c "import json; d=json.load(open('$NPM_REPORT')); v=d.get('metadata',{}).get('vulnerabilities',{}); print(v.get('critical',0) + v.get('high',0))" 2>/dev/null || echo "0")

    if [ "$NPM_VULNS" = "0" ]; then
        echo -e "${GREEN}  No vulnerable npm packages${NC}"
    else
        echo -e "${RED}  Found $NPM_VULNS npm vulnerabilities ($NPM_CRITICAL critical/high)${NC}"
        echo -e "  Report: $NPM_REPORT"
    fi
else
    echo -e "${YELLOW}  Skipped (no package-lock.json)${NC}"
fi

# ---------------------------------------------------------------------------
# 5. CUSTOM - Osprey Hardcoded Secrets Scan
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[5/6] Scanning for Hardcoded Secrets...${NC}"
SECRETS_REPORT="$REPORT_DIR/secrets_${TIMESTAMP}.txt"

{
    echo "=== Hardcoded Secrets Scan ==="
    echo "Date: $(date)"
    echo ""

    echo "--- JWT Secret Defaults ---"
    grep -rn "jwt_secret\|JWT_SECRET\|secret_key.*=.*[\"']" \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null | grep -v "os.environ\|os.getenv\|\.get(" || echo "  None found"

    echo ""
    echo "--- API Keys in Source Code ---"
    grep -rn "sk_live_\|sk_test_\|pk_live_\|pk_test_\|AIza\|AKIA\|api_key.*=.*[\"'][a-zA-Z0-9]" \
        "$BACKEND_DIR" "$FRONTEND_DIR/src" \
        --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
        --exclude-dir=".venv" \
        --exclude-dir="node_modules" \
        --exclude-dir="__pycache__" \
        2>/dev/null | grep -v "os.environ\|os.getenv\|process.env\|import.meta.env\|\.get(" || echo "  None found"

    echo ""
    echo "--- Passwords in Source ---"
    grep -rn "password.*=.*[\"']\|passwd.*=.*[\"']" \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null | grep -v "os.environ\|os.getenv\|\.get(\|request\.\|form\.\|data\.\|body\.\|json\.\|hashed\|bcrypt\|hash" || echo "  None found"

    echo ""
    echo "--- MongoDB Connection Strings ---"
    grep -rn "mongodb://\|mongodb+srv://" \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null | grep -v "os.environ\|os.getenv\|localhost\|127.0.0.1\|\.get(" || echo "  None found"

} > "$SECRETS_REPORT" 2>&1

SECRETS_COUNT=$(grep -c "^[^= -].*:[0-9]*:" "$SECRETS_REPORT" 2>/dev/null || echo "0")
if [ "$SECRETS_COUNT" -gt 0 ]; then
    echo -e "${RED}  Found $SECRETS_COUNT potential hardcoded secrets${NC}"
    echo -e "  Report: $SECRETS_REPORT"
    CRITICAL_ISSUES=$((CRITICAL_ISSUES + SECRETS_COUNT))
else
    echo -e "${GREEN}  No hardcoded secrets found${NC}"
fi

# ---------------------------------------------------------------------------
# 6. CUSTOM - Osprey-Specific Vulnerability Patterns
# ---------------------------------------------------------------------------
echo -e "\n${YELLOW}[6/6] Scanning Osprey-Specific Vulnerability Patterns...${NC}"
OSPREY_REPORT="$REPORT_DIR/osprey_vulns_${TIMESTAMP}.txt"

{
    echo "=== Osprey Vulnerability Pattern Scan ==="
    echo "Date: $(date)"
    echo ""

    echo "--- CORS Wildcard ---"
    grep -rn 'allow_origins.*\[.*"\*".*\]\|CORSMiddleware.*origins.*\*\|Access-Control-Allow-Origin.*\*' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Unsafe MongoDB Queries (potential NoSQL injection) ---"
    grep -rn 'find_one.*{.*request\.\|find.*{.*request\.\|update_one.*{.*request\.\|delete_one.*{.*request\.\|\$where\|\$regex.*request\.\|\.aggregate.*request\.' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Missing Auth Decorators on Sensitive Endpoints ---"
    grep -rn '@app\.\(get\|post\|put\|delete\|patch\).*"/api/\(admin\|payment\|case\|documents\|auto-application\)' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Unsafe eval/exec Usage ---"
    grep -rn '\beval(\|\bexec(\|\bcompile(' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Unsafe Deserialization ---"
    grep -rn 'pickle\.loads\|yaml\.load(\|yaml\.unsafe_load' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Open Redirects ---"
    grep -rn 'redirect.*request\.\|RedirectResponse.*request\.' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- File Path Traversal ---"
    grep -rn 'open(.*request\.\|os\.path\.join.*request\.\|send_file.*request\.' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Debug Mode in Production ---"
    grep -rn 'debug=True\|DEBUG.*=.*True' \
        "$BACKEND_DIR" \
        --include="*.py" \
        --exclude-dir=".venv" \
        --exclude-dir="__pycache__" \
        2>/dev/null || echo "  None found"

    echo ""
    echo "--- Rate Limiting Check ---"
    if ! grep -rq "slowapi\|RateLimiter\|rate_limit\|throttle" "$BACKEND_DIR" --include="*.py" 2>/dev/null; then
        echo "  WARNING: No rate limiting detected on API endpoints"
    else
        echo "  Rate limiting found"
    fi

    echo ""
    echo "--- HTTPS Enforcement Check ---"
    if ! grep -rq "HTTPSRedirectMiddleware\|force_https\|ssl_redirect" "$BACKEND_DIR" --include="*.py" 2>/dev/null; then
        echo "  WARNING: No HTTPS enforcement middleware detected"
    else
        echo "  HTTPS enforcement found"
    fi

} > "$OSPREY_REPORT" 2>&1

echo -e "  Report: $OSPREY_REPORT"

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}  SCAN SUMMARY                         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "  Reports saved to: $REPORT_DIR/"
echo -e "  Total issues found: ${TOTAL_ISSUES}"
echo -e "  Critical/High issues: ${CRITICAL_ISSUES}"

if [ "$CRITICAL_ISSUES" -gt 0 ]; then
    echo -e "\n${RED}  ⚠ CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION${NC}"
    exit 1
else
    echo -e "\n${GREEN}  Scan completed successfully${NC}"
    exit 0
fi
