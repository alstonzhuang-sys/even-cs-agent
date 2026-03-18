#!/bin/bash
# test_ingress.sh - Test Ingress Normalizer
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

echo "=== Ingress Tests ==="

# Test 1: Discord → external
result=$(python3 scripts/ingress.py --channel discord --sender-id user123 --message "hello")
run_test "Discord → external" '"surface": "external"' "$result"

# Test 2: Feishu → internal
result=$(python3 scripts/ingress.py --channel feishu --sender-id ou_xxx --message "你好")
run_test "Feishu → internal" '"surface": "internal"' "$result"

# Test 3: Unknown channel → fallback external
result=$(python3 scripts/ingress.py --channel slack --sender-id user123 --message "hello")
run_test "Unknown channel → external" '"surface": "external"' "$result"

# Test 4: Message preserved
result=$(python3 scripts/ingress.py --channel discord --sender-id user123 --message "battery life")
run_test "Message preserved" '"message": "battery life"' "$result"

echo "  Passed: $PASS, Failed: $FAIL"
[ $FAIL -eq 0 ]
