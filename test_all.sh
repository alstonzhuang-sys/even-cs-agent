#!/bin/bash
# test_all.sh - Run all tests

echo "=== Running All Tests ==="
echo

FAILED=0
PASSED=0

# Test scripts to run
TESTS=(
    "test_ingress.sh"
    "test_router.sh"
    "test_knowledge_worker.sh"
    "test_renderer.sh"
    "test_escalation_worker.sh"
    "test_output_switch.sh"
    "test_main.sh"
)

# Run each test
for test in "${TESTS[@]}"; do
    if [ -f "$test" ]; then
        echo "Running $test..."
        if bash "$test" > /dev/null 2>&1; then
            echo "✅ $test passed"
            PASSED=$((PASSED + 1))
        else
            echo "❌ $test failed"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "⚠️  $test not found (skipped)"
    fi
done

echo
echo "=== Test Summary ==="
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo

if [ $FAILED -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed. Check logs for details."
    exit 1
fi
