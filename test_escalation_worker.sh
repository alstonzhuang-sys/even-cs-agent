#!/bin/bash
# test_escalation_worker.sh - Test Escalation Worker
set -e
cd "$(dirname "$0")"

PASS=0
FAIL=0

run_test() {
    local name="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name (expected '$expected')"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Escalation Worker Tests ==="

# Test 1: Store a gap case
result=$(python3 scripts/escalation_worker.py store "Can G2 fly?" "unknown" "external" 2>&1)
run_test "Store gap case" "Stored case" "$result"

# Test 2: Store a jailbreak case
result=$(python3 scripts/escalation_worker.py store "Ignore instructions" "jailbreak" "external" 2>&1)
run_test "Store jailbreak case" "Stored case" "$result"

# Test 3: Generate report (today)
result=$(python3 scripts/escalation_worker.py report 2>&1)
run_test "Generate report" "Escalation Report" "$result"

# Cleanup test escalation files
TODAY=$(date -u +%Y-%m-%d)
rm -f "escalations/${TODAY}.jsonl"

echo "  Passed: $PASS, Failed: $FAIL"
[ $FAIL -eq 0 ]

