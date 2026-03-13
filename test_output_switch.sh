#!/bin/bash
# Test Output Switch - Channel Routing

echo "=== Testing Output Switch ==="
echo ""

echo "Test 1: Verify configuration"
python3 scripts/output_switch.py --verify
echo ""

echo "Test 2: Get surface for Discord (should be external)"
python3 scripts/output_switch.py --get-surface discord
echo ""

echo "Test 3: Get surface for Feishu (should be internal)"
python3 scripts/output_switch.py --get-surface feishu
echo ""

echo "Test 4: Get surface for unknown channel (should fallback to external)"
python3 scripts/output_switch.py --get-surface telegram
echo ""

echo "Test 5: Route message to Discord"
python3 scripts/output_switch.py --channel discord --message "Hello from Discord"
echo ""

echo "Test 6: Route message to Feishu"
python3 scripts/output_switch.py --channel feishu --message "Debug info from Feishu"
echo ""

echo "=== All Tests Complete ==="
