#!/bin/bash
cd /var/www/visa-application/osprey-core/backend
source venv/bin/activate
python -m pytest tests/test_e2e.py -v --tb=short 2>&1 | tee tests/last_run.log
echo ""
echo "=== RESULTADO ==="
grep -E "PASSED|FAILED|ERROR" tests/last_run.log
echo "Relatório completo: tests/last_run.log"
