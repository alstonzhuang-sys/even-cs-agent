#!/bin/bash
# Test Knowledge Worker - Hot-reload & Tiered Injection

echo "=== Testing Knowledge Worker ==="
echo ""

echo "Test 1: Discover all knowledge files"
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'scripts')
from knowledge_worker import discover_knowledge_files, determine_tier

files = discover_knowledge_files()
print(f"Found {len(files)} knowledge files:")
for file_path, metadata, content in files:
    tier = determine_tier(metadata, file_path.name)
    print(f"  - {file_path.name} (Tier {tier})")
PYEOF
echo ""

echo "Test 2: Build context (check tier injection)"
python3 scripts/knowledge_worker.py "What's the battery life?" "specs_query" "external" --debug 2>&1 | grep -E "(kb_.*\.md|Tier)" | head -20
echo ""

echo "Test 3: Hot-reload test - Create new Tier 4 file"
cat > knowledge/kb_test_tier4.md << 'EOF'
---
visibility: internal
keyTags: Test
owner: Test
tier: 4
---

# Test Tier 4 File

This is a test file for Tier 4 (dynamic injection).
EOF

echo "Created kb_test_tier4.md"
echo ""

echo "Test 4: Verify new file is discovered"
python3 << 'PYEOF'
import sys
sys.path.insert(0, 'scripts')
from knowledge_worker import discover_knowledge_files, determine_tier

files = discover_knowledge_files()
print(f"Found {len(files)} knowledge files (should be +1):")
for file_path, metadata, content in files:
    tier = determine_tier(metadata, file_path.name)
    if 'test' in file_path.name.lower():
        print(f"  ✅ {file_path.name} (Tier {tier}) - NEW FILE DETECTED")
PYEOF
echo ""

echo "Test 5: Cleanup"
rm -f knowledge/kb_test_tier4.md
echo "Removed test file"
echo ""

echo "=== All Tests Complete ==="
