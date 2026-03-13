#!/bin/bash
# Test script for Even CS Agent

echo "=== Even CS Agent Test Suite ==="
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set. LLM fallback will not work."
    echo "   Set it with: export GEMINI_API_KEY='your-api-key'"
    echo ""
fi

# Test 1: Router
echo "Test 1: Router (Intent Detection)"
echo "Input: 'What's the battery life of G2?'"
python3 scripts/router.py "What's the battery life of G2?"
echo ""

# Test 2: Knowledge Worker (Exact Match)
echo "Test 2: Knowledge Worker (Exact Match)"
echo "Input: 'What's the price of G2?'"
python3 scripts/knowledge_worker.py "What's the price of G2?" "specs_query" "external"
echo ""

# Test 3: Knowledge Worker (LLM Fallback)
echo "Test 3: Knowledge Worker (LLM Fallback)"
echo "Input: 'Does G2 support Klingon language?'"
python3 scripts/knowledge_worker.py "Does G2 support Klingon language?" "specs_query" "external"
echo ""

# Test 4: Renderer (External)
echo "Test 4: Renderer (External)"
echo "Input: 'The G2 costs \$599'"
python3 scripts/renderer.py "The G2 costs \$599" "external" "specs_query" "1.0"
echo ""

# Test 5: Renderer (Internal)
echo "Test 5: Renderer (Internal)"
echo "Input: 'The G2 costs \$599'"
python3 scripts/renderer.py "The G2 costs \$599" "internal" "specs_query" "1.0" "price.*g2"
echo ""

# Test 6: Helpers
echo "Test 6: Helpers (Extract Section)"
python3 scripts/helpers.py extract_section knowledge/kb_core.md "G2 Specifications" | head -10
echo ""

echo "=== Test Suite Complete ==="
