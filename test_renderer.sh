#!/bin/bash
# Test Renderer - External vs Internal Output

echo "=== Testing Renderer ==="
echo ""

echo "Test 1: External - Basic response (no filtering needed)"
python3 scripts/renderer.py \
  "The G2 has a battery life of 3-4 hours with typical use." \
  "external" \
  "specs_query" \
  "1.0"
echo ""

echo "Test 2: External - Response with internal keywords (should be filtered)"
python3 scripts/renderer.py \
  "The G2 costs \$599. Internal note: our cost is \$300. Contact @Caris for details." \
  "external" \
  "specs_query" \
  "1.0"
echo ""

echo "Test 3: External - Response with sensitive info (should be blocked)"
python3 scripts/renderer.py \
  "Our internal cost is \$300 and profit margin is 50%." \
  "external" \
  "specs_query" \
  "1.0"
echo ""

echo "Test 4: Internal - Basic response (with debug info)"
python3 scripts/renderer.py \
  "The G2 has a battery life of 3-4 hours with typical use." \
  "internal" \
  "specs_query" \
  "1.0" \
  "battery.*life"
echo ""

echo "Test 5: Internal - Response with internal keywords (no filtering)"
python3 scripts/renderer.py \
  "The G2 costs \$599. Internal note: Check with @Caris for bulk pricing." \
  "internal" \
  "policy_query" \
  "0.8" \
  "price.*bulk"
echo ""

echo "Test 6: External - Policy response"
python3 scripts/renderer.py \
  "We offer a 30-day return policy. See kb_policies.md for details." \
  "external" \
  "policy_query" \
  "1.0"
echo ""

echo "Test 7: Internal - Escalation case"
python3 scripts/renderer.py \
  "Unable to answer. Escalate to @Rosen." \
  "internal" \
  "unknown" \
  "0.3" \
  "N/A"
echo ""

echo "=== All Tests Complete ==="
