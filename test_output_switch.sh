#!/bin/bash
# test_output_switch.sh - Test Output Switch / Channel Config
set -e
cd "$(dirname "$0")"

PASS=0
FAIL=0

run_test() {
    local name="$1" expected="$2" actual="$3"
    if echo "$actual" | grep -q "$expected"; then
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $name (expected '$expected', got: $actual)"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== Output Switch Tests ==="

# Need config file for these tests
CONFIG_FILE="config/channels.json"
if [ ! -f "$CONFIG_FILE" ]; then
    cp config/channels.json.example "$CONFIG_FILE"
    CLEANUP=1
fi

# Test 1: Discord → external
result=$(python3 scripts/output_switch.py --get-surface discord)
run_test "Discord → external" "external" "$result"

# Test 2: Feishu → internal
result=$(python3 scripts/output_switch.py --get-surface feishu)
run_test "Feishu → internal" "internal" "$result"

# Cleanup
if [ "${CLEANUP:-0}" = "1" ]; then
    rm -f "$CONFIG_FILE"
fi

echo "  Passed: $PASS, Failed: $FAIL"
[ $FAIL -eq 0 ]
