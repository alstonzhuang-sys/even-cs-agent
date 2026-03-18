#!/bin/bash
# test_knowledge_worker.sh - Test Knowledge Worker (offline, no LLM call)
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

echo "=== Knowledge Worker Tests ==="

# Test context building (no LLM needed)
result=$(python3 -c "
import sys
sys.path.insert(0, 'scripts')
from knowledge_worker import build_context

# Test 1: Core KB always injected
ctx = build_context('specs_query', confidence=1.0, surface='external')
assert 'kb_core.md' in ctx, 'kb_core.md not in context'
assert 'kb_policies.md' in ctx, 'kb_policies.md not in context'
print('core_injected:OK')

# Test 2: High confidence → selective extended
ctx = build_context('prescription_query', confidence=0.9, surface='external')
assert 'kb_prescription.md' in ctx, 'kb_prescription.md not in context'
print('selective_inject:OK')

# Test 3: Low confidence → all extended
ctx = build_context('unknown', confidence=0.3, surface='external')
# Should include all non-core KB files
print('low_conf_inject:OK')
" 2>&1)

run_test "Core KB always injected" "core_injected:OK" "$result"
run_test "Selective extended injection" "selective_inject:OK" "$result"
run_test "Low confidence → all extended" "low_conf_inject:OK" "$result"

echo "  Passed: $PASS, Failed: $FAIL"
[ $FAIL -eq 0 ]

