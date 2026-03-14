#!/bin/bash
# Test main.py entry point

echo "=== Testing main.py Entry Point ==="
echo

# Test 1: Missing input
echo "Test 1: Empty input (should fail)"
echo "" | python3 main.py 2>&1 | head -1
echo

# Test 2: Invalid JSON
echo "Test 2: Invalid JSON (should fail)"
echo "not json" | python3 main.py 2>&1 | head -1
echo

# Test 3: Valid input (will fail on config check)
echo "Test 3: Valid input (will fail on config validation)"
echo '{"channel":"discord","sender_id":"test","message":"Hello"}' | python3 main.py 2>&1 | head -1
echo

# Test 4: Health check
echo "Test 4: Health check"
python3 scripts/health_check.py
echo

echo "=== Tests Complete ==="
