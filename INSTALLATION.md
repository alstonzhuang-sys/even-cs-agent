# Even CS Agent - Installation & Usage Guide

**For New OpenClaw Users**

This guide walks you through installing and using Even CS Agent from scratch.

---

## 📋 Prerequisites

Before you start, make sure you have:

1. **OpenClaw installed and running**
   ```bash
   # Check if OpenClaw is installed
   openclaw --version
   
   # If not installed, visit: https://openclaw.ai
   ```

2. **Python 3.8+**
   ```bash
   python3 --version
   ```

3. **Gemini API Key**
   - Get one from: https://makersuite.google.com/app/apikey
   - Free tier available

---

## 🚀 Installation Steps

### Step 1: Clone the Repository

```bash
# Navigate to OpenClaw workspace
cd ~/.openclaw/workspace

# Clone the repository
git clone https://github.com/alstonzhuang-sys/even-cs-agent.git

# Enter the directory
cd even-cs-agent
```

### Step 2: Install Dependencies

```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Verify installation
pip3 list | grep google-generativeai
```

**Expected output:**
```
google-generativeai    0.3.2
```

### Step 3: Set API Key

```bash
# Add to your shell profile (choose one)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.zshrc   # For zsh
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc  # For bash

# Reload shell
source ~/.zshrc  # or source ~/.bashrc

# Verify
echo $GEMINI_API_KEY
```

### Step 4: Configure Channels

```bash
# Copy configuration template
cp config/channels.json.example config/channels.json

# Edit configuration
nano config/channels.json
```

**Replace `ou_xxx` with actual Feishu ID:**

```json
{
  "external": ["discord"],
  "internal": ["feishu"],
  "fallback": "external",
  "rosen_contact": {
    "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81",  // ⚠️ CHANGE THIS
    "name": "Rosen"
  }
}
```

**How to get Feishu ID:**
1. Open Feishu
2. Click on user profile
3. Copy the ID (format: `ou_xxxxx`)

### Step 5: Verify Installation

```bash
# Run health check
python3 scripts/health_check.py
```

**Expected output:**
```
=== Even CS Agent Health Check ===

✅ GEMINI_API_KEY: Set (39 chars)
✅ Configuration file: config/channels.json
✅ Rosen contact: ou_ceae7c2ca21c67c92ae07f04d6347a81
✅ External channels: ['discord']
✅ Internal channels: ['feishu']
✅ Fallback surface: external
✅ Knowledge base: 5 files
   ✅ kb_core.md
   ✅ kb_policies.md
✅ LLM connection: Working

=== ✅ Configuration is valid! ===
```

### Step 6: Run Tests

```bash
# Run all tests
./test.sh
```

**Expected output:**
```
=== Even CS Agent Test Suite ===

1. Testing Ingress Normalizer...
✅ Ingress test passed

2. Testing Router (Regex)...
✅ Router (Regex) test passed

3. Testing Router (Chinese patterns)...
✅ Router (Chinese) test passed

...

=== Test Summary ===
Passed: 8
Failed: 0

✅ All tests passed!
```

---

## 🎯 How OpenClaw Will Use This Skill

### Automatic Invocation

Once installed, OpenClaw will **automatically** invoke this skill when:

1. **User sends a message** to Discord/Feishu
2. **Message matches Even Realities topics** (products, orders, support)
3. **OpenClaw routes to this skill** based on SKILL.md

### Execution Flow

```
User Message (Discord/Feishu)
    ↓
OpenClaw receives message
    ↓
OpenClaw reads SKILL.md
    ↓
Checks: "Is this about Even Realities?"
    ↓
YES → Execute main.py
    ↓
main.py runs the pipeline:
    1. Ingress: Normalize input
    2. Router: Classify intent (Regex → LLM)
    3. Worker: Execute (Knowledge/Skill/Escalation)
    4. Renderer: Filter output
    5. Output: Send response
    ↓
Response sent back to user
```

### What OpenClaw Follows

OpenClaw will **100% follow** these instructions from `SKILL.md`:

#### 1. **When to Use This Skill**

```markdown
Use this skill when:
- User asks about Even Realities products (G1/G2)
- User asks about orders, shipping, returns, refunds
- User asks for product specs, pricing, compatibility
- User needs troubleshooting help
```

**How it works:**
- OpenClaw scans the message
- If keywords match (G1, G2, battery, order, return, etc.)
- → Invokes this skill

#### 2. **Execution Steps**

OpenClaw follows the exact steps in SKILL.md:

**Step 1: Detect Surface**
```python
if channel == "discord":
    surface = "external"  # Customer-facing
elif channel == "feishu":
    surface = "internal"  # Team-facing
```

**Step 2: Router (Hard-coded Regex First)**
```python
# Try Regex patterns first (deterministic, fast)
patterns = {
    "specs_query": [r"battery.*life", r"电池.*续航", ...],
    "return_request": [r"return.*product", r"退货", ...],
    ...
}

# If no Regex match → Use LLM (Gemini 2 Flash)
if not matched:
    intent = llm_classify(message)
```

**Step 3: Execute Worker**
```python
if intent == "specs_query":
    # Knowledge Worker
    context = inject_kb(intent, confidence)
    response = llm_generate(message, context)

elif intent == "order_status":
    # Skill Worker (API call)
    response = check_order_api(order_id)

elif intent == "unknown":
    # Escalation Worker
    response = "I don't have that information. Let me check with the team."
```

**Step 4: Render Response**
```python
if surface == "external":
    # Filter sensitive info
    response = remove_internal_notes(response)
else:
    # Add debug info
    response += f"\n[Debug: intent={intent}, confidence={confidence}]"
```

#### 3. **Hard Coding Guarantees**

OpenClaw will follow these **deterministic rules** (no LLM guessing):

| Scenario | Action | Confidence |
|----------|--------|------------|
| Message matches Regex | Use Regex intent | 1.0 (100%) |
| No Regex match | Use LLM to classify | 0.8 (80%) |
| Confidence ≥ 0.7 | Inject selective KB | Deterministic |
| Confidence < 0.7 | Inject all KB | Deterministic |
| Jailbreak detected | Hard-coded rejection | 1.0 (100%) |

**Example:**

```
User: "What's the battery life?"
    ↓
Regex: "battery.*life" → intent="specs_query" (confidence=1.0)
    ↓
Worker: knowledge_worker
    ↓
KB Injection: Core (always) + kb_golden.md (confidence ≥ 0.7)
    ↓
LLM: Gemini 2 Flash (Temperature=0)
    ↓
Response: "The G2 has a battery life of 3-4 hours."
```

---

## 🧪 Testing the Installation

### Test 1: Simple Query (Regex Path)

```bash
# Simulate a Discord message
echo '{"channel":"discord","sender_id":"123","message":"What is the battery life?","message_id":"msg_001"}' | python3 main.py
```

**Expected output:**
```json
{
  "response": "The G2 has a battery life of 3-4 hours with typical use.",
  "intent": "specs_query",
  "confidence": 1.0,
  "surface": "external",
  "worker": "knowledge_worker"
}
```

### Test 2: Chinese Query (Regex Path)

```bash
echo '{"channel":"feishu","sender_id":"ou_123","message":"电池续航多久？","message_id":"msg_002"}' | python3 main.py
```

**Expected output:**
```json
{
  "response": "G2 电池续航 3-4 小时（典型使用）。\n\n[Debug Info]\n- Intent: specs_query\n- Confidence: 1.0\n- Surface: internal",
  "intent": "specs_query",
  "confidence": 1.0,
  "surface": "internal",
  "worker": "knowledge_worker"
}
```

### Test 3: Unknown Query (LLM Path)

```bash
echo '{"channel":"discord","sender_id":"123","message":"Tell me something interesting","message_id":"msg_003"}' | python3 main.py
```

**Expected output:**
```json
{
  "response": "I don't have that information right now. Let me check with the team.",
  "intent": "unknown",
  "confidence": 0.8,
  "surface": "external",
  "worker": "escalation_worker"
}
```

---

## 🔧 Customization

### Adding New Knowledge

1. Create a new `.md` file in `knowledge/` directory:

```bash
nano knowledge/kb_new_feature.md
```

2. Add content:

```markdown
---
visibility: external
tier: 2
---

# New Feature Knowledge

Your content here...
```

3. **No restart needed** - Hot-reload automatically discovers new files

### Adding New Regex Patterns

Edit `scripts/router.py`:

```python
PATTERNS = {
    "your_new_intent": [
        r"pattern1",
        r"pattern2",
        r"中文模式"
    ]
}

WORKER_ASSIGNMENT = {
    "your_new_intent": "knowledge_worker"
}
```

### Updating Configuration

Edit `config/channels.json`:

```json
{
  "external": ["discord", "telegram"],  // Add new channels
  "internal": ["feishu", "slack"],
  "fallback": "external"
}
```

---

## 🐛 Troubleshooting

### Issue 1: "GEMINI_API_KEY not set"

**Solution:**
```bash
export GEMINI_API_KEY="your_key_here"
echo $GEMINI_API_KEY  # Verify
```

### Issue 2: "Rosen ID is still placeholder (ou_xxx)"

**Solution:**
```bash
nano config/channels.json
# Replace ou_xxx with actual Feishu ID
python3 scripts/health_check.py  # Verify
```

### Issue 3: "google-generativeai not installed"

**Solution:**
```bash
pip3 install google-generativeai
pip3 list | grep google-generativeai  # Verify
```

### Issue 4: Tests failing

**Solution:**
```bash
# Check health first
python3 scripts/health_check.py

# Run individual tests
python3 scripts/router.py "test message" --no-llm
python3 scripts/knowledge_worker.py "test" "specs_query" "external" --confidence 0.9
```

---

## 📚 Next Steps

1. **Monitor Escalations**
   ```bash
   # Check escalation logs
   cat escalations/$(date +%Y-%m-%d).jsonl
   ```

2. **Review Daily Reports**
   - Escalation reports sent to Rosen daily at 9:00 AM (UTC+8)
   - Contains knowledge gaps and suggested improvements

3. **Update Knowledge Base**
   - Add new KB files as needed
   - Update existing files based on escalations
   - No restart required (hot-reload)

4. **Customize for Your Use Case**
   - Modify `prompts/SOUL.md` for personality
   - Update `knowledge/` files for your products
   - Add new Regex patterns for your domain

---

## 🔗 Resources

- **GitHub**: https://github.com/alstonzhuang-sys/even-cs-agent
- **OpenClaw Docs**: https://docs.openclaw.ai
- **Gemini API**: https://ai.google.dev
- **Issues**: https://github.com/alstonzhuang-sys/even-cs-agent/issues

---

## ✅ Installation Checklist

- [ ] OpenClaw installed
- [ ] Repository cloned
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] API key set (`export GEMINI_API_KEY="..."`)
- [ ] Configuration created (`cp config/channels.json.example config/channels.json`)
- [ ] Rosen ID updated (replace `ou_xxx`)
- [ ] Health check passed (`python3 scripts/health_check.py`)
- [ ] Tests passed (`./test.sh`)
- [ ] Test queries work (manual testing)

**Once all checked, you're ready to go! 🚀**
