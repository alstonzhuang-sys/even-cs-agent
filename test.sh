#!/bin/bash
# Even CS Agent - Unified Test Suite

set -e  # Exit on error

echo "=== Even CS Agent Test Suite ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Test 1: Ingress Normalizer
echo "1. Testing Ingress Normalizer..."
if python3 scripts/ingress.py --channel discord --sender-id 123 --message "Test" --message-id msg_001 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ingress test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Ingress test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: Router (Regex)
echo "2. Testing Router (Regex)..."
RESULT=$(python3 scripts/router.py "What's the battery life?" --no-llm 2>/dev/null)
if echo "$RESULT" | grep -q "specs_query"; then
    echo -e "${GREEN}✅ Router (Regex) test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Router (Regex) test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: Router (Chinese)
echo "3. Testing Router (Chinese patterns)..."
RESULT=$(python3 scripts/router.py "电池续航多久？" --no-llm 2>/dev/null)
if echo "$RESULT" | grep -q "specs_query"; then
    echo -e "${GREEN}✅ Router (Chinese) test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Router (Chinese) test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: Knowledge Worker (requires GEMINI_API_KEY)
echo "4. Testing Knowledge Worker..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}⚠️  Skipped (GEMINI_API_KEY not set)${NC}"
else
    if python3 scripts/knowledge_worker.py "What's the battery life?" "specs_query" "external" --confidence 0.9 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Knowledge Worker test passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ Knowledge Worker test failed${NC}"
        ((FAILED++))
    fi
fi
echo ""

# Test 5: Escalation Worker
echo "5. Testing Escalation Worker..."
if python3 scripts/escalation_worker.py store "Test message" "unknown" "external" "gap" "medium" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Escalation Worker test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Escalation Worker test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Renderer
echo "6. Testing Renderer..."
if python3 scripts/renderer.py "Test response" "external" "specs_query" "1.0" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Renderer test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Renderer test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 7: Output Switch
echo "7. Testing Output Switch..."
if python3 scripts/output_switch.py --get-surface discord > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Output Switch test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Output Switch test failed${NC}"
    ((FAILED++))
fi
echo ""

# Test 8: Health Check
echo "8. Testing Health Check..."
if python3 scripts/health_check.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health Check test passed${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Health Check test failed${NC}"
    ((FAILED++))
fi
echo ""

# Summary
echo "=== Test Summary ==="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
