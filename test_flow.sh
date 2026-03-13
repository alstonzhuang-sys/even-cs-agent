#!/bin/bash
# Test End-to-End Flow: Ingress → Router

echo "=== Testing Ingress → Router Flow ==="
echo ""

echo "Step 1: Ingress normalizes Discord message"
INGRESS_OUTPUT=$(python3 scripts/ingress.py \
  --channel discord \
  --sender-id 795976834868445234 \
  --message "What's the battery life of G2?" \
  --message-id msg_001)

echo "$INGRESS_OUTPUT"
echo ""

echo "Step 2: Extract message from Ingress output"
MESSAGE=$(echo "$INGRESS_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['message'])")
echo "Extracted message: $MESSAGE"
echo ""

echo "Step 3: Router processes message"
python3 scripts/router.py "$MESSAGE" --no-llm
echo ""

echo "=== Testing with Feishu (Internal) ==="
echo ""

echo "Step 1: Ingress normalizes Feishu message"
INGRESS_OUTPUT=$(python3 scripts/ingress.py \
  --channel feishu \
  --sender-id ou_ceae7c2ca21c67c92ae07f04d6347a81 \
  --message "我想退货" \
  --message-id om_002)

echo "$INGRESS_OUTPUT"
echo ""

echo "Step 2: Extract message"
MESSAGE=$(echo "$INGRESS_OUTPUT" | python3 -c "import sys, json; print(json.load(sys.stdin)['message'])")
echo "Extracted message: $MESSAGE"
echo ""

echo "Step 3: Router processes message"
python3 scripts/router.py "$MESSAGE" --no-llm
echo ""

echo "=== Flow Test Complete ==="
