#!/bin/bash
# test_renderer.sh - Test Renderer filtering
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

run_test_absent() {
    local name="$1" absent="$2" actual="$3"
    if echo "$actual" | grep -q "$absent"; then
        echo "  FAIL: $name (should NOT contain '$absent')"
        FAIL=$((FAIL + 1))
    else
        PASS=$((PASS + 1))
    fi
}

echo "=== Renderer Tests ==="

# Test 1: External - clean response passes through
result=$(python3 scripts/renderer.py "The G2 has a 220mAh battery." "external" "specs_query" "1.0")
run_test "External clean pass" "220mAh" "$result"

# Test 2: External - filters internal keywords
result=$(python3 scripts/renderer.py "The G2 costs 599. Ask @Caris for details. See kb_core.md." "external" "specs_query" "1.0")
run_test_absent "External filters @mention" "@Caris" "$result"
run_test_absent "External filters kb ref" "kb_core" "$result"

# Test 3: Internal - includes debug info
result=$(python3 scripts/renderer.py "The G2 has a 220mAh battery." "internal" "specs_query" "0.95")
run_test "Internal has debug" "Debug Info" "$result"
run_test "Internal has intent" "specs_query" "$result"
run_test "Internal has confidence" "0.95" "$result"

echo "  Passed: $PASS, Failed: $FAIL"
[ $FAIL -eq 0 ]
