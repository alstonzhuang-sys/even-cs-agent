#!/bin/bash
# Test Ingress Normalizer

echo "=== Testing Ingress Normalizer ==="
echo ""

echo "Test 1: Feishu (Internal) Message"
python3 scripts/ingress.py \
  --channel feishu \
  --sender-id ou_ceae7c2ca21c67c92ae07f04d6347a81 \
  --message "查询G2电池续航" \
  --message-id om_123456
echo ""

echo "Test 2: Discord (External) Message"
python3 scripts/ingress.py \
  --channel discord \
  --sender-id 795976834868445234 \
  --message "What's the battery life of G2?" \
  --message-id 1482025385645310012
echo ""

echo "Test 3: Missing Required Field (should fail)"
python3 scripts/ingress.py \
  --channel discord \
  --sender-id 123 2>&1
echo ""

echo "Test 4: Long Message (should fail)"
python3 scripts/ingress.py \
  --channel discord \
  --sender-id 123 \
  --message "$(python3 -c 'print("x" * 10001)')" 2>&1
echo ""

echo "=== All Tests Complete ==="
