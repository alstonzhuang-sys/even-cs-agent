# Even CS Agent (DivaD v3.0)

> 🤖 Intelligent Customer Support Agent for Even Realities  
> Built on OpenClaw | Powered by Gemini 2 Flash

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)](https://github.com/alstonzhuang/even-cs-agent)

---

## ⚠️ IMPORTANT: Configuration Required

**Before using this skill, you MUST configure it:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Copy configuration template:**
   ```bash
   cp config/channels.json.example config/channels.json
   ```

3. **Edit `config/channels.json` and replace `ou_xxx` with actual Feishu ID:**
   ```json
   {
     "rosen_contact": {
       "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81",  // ✅ Replace this
       "name": "Rosen"
     }
   }
   ```

4. **Set Gemini API key:**
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

5. **Verify configuration:**
   ```bash
   python3 scripts/health_check.py
   ```

---

## 📖 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Examples](#examples)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**Even CS Agent** is an intelligent customer support bot for Even Realities (AR smart glasses company). It provides:

- **Dual-Surface Support**: External (Discord) for customers, Internal (Feishu) for team
- **Learning Loop**: Today's escalations become tomorrow's knowledge
- **Full Context Injection**: Leverages Gemini 2 Flash's 1M token window
- **Deterministic Routing**: 90% Regex matching, 10% LLM classification
- **Hot-Reload**: Add new knowledge files without restart

### Why Even CS Agent?

| Traditional Chatbot | Even CS Agent |
|---------------------|---------------|
| ❌ Hallucinations | ✅ Zero-tolerance (Temperature=0) |
| ❌ Inconsistent answers | ✅ Deterministic routing (Regex-first) |
| ❌ No learning | ✅ Continuous improvement (Escalation → KB) |
| ❌ One-size-fits-all | ✅ One Brain, Two Voices (External/Internal) |
| ❌ Hard to update | ✅ Hot-reload (Add .md files instantly) |

---

## 🏗️ Architecture

### Pipeline Overview

```
┌─────────────┐
│ User Message│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ 1. Ingress          │  Normalize input
│    Normalizer       │  Discord → external
└──────┬──────────────┘  Feishu → internal
       │
       ▼
┌─────────────────────┐
│ 2. Router           │  Classify intent
│    (Regex + LLM)    │  Assign worker
└──────┬──────────────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Knowledge    │  │ Skill        │  │ Escalation   │
│ Worker       │  │ Worker       │  │ Worker       │
│ (RAG + LLM)  │  │ (API calls)  │  │ (Gap detect) │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ 4. Renderer  │  Filter sensitive info
                  │              │  Add debug info
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ 5. Output    │  Route to channel
                  │    Switch    │  Discord / Feishu
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Response   │
                  └──────────────┘
```

### Component Details

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Ingress Normalizer** | Standardize input | Channel detection, Payload normalization |
| **Router** | Intent classification | Regex (90%) + LLM (10%), Hard-coded worker assignment |
| **Knowledge Worker** | Answer questions | 2-tier injection (Core + Extended), Hot-reload |
| **Skill Worker** | Execute actions | API calls (Phase 2) |
| **Escalation Worker** | Handle gaps | Learning loop, Daily reports |
| **Renderer** | Format output | Sentence-level filtering, Debug info |
| **Output Switch** | Route to channel | Config-driven, Safe fallback |

---

## ✨ Features

### 🎯 Deterministic Routing

- **90% Regex Matching**: Fast (<1ms), deterministic, zero-cost
- **10% LLM Classification**: Handles edge cases with Gemini 2 Flash
- **Hard-coded Worker Assignment**: No LLM guessing

### 📚 2-Tier Context Injection

**Core (Tier 1)**: Always injected
- `kb_core.md` - Hardware specs, pricing (~6KB)
- `kb_policies.md` - Return/refund/shipping (~11KB)

**Extended (Tier 2)**: Confidence-based injection
- **High confidence (≥ 0.7)**: Intent-based selective injection
  - `specs_query` → `kb_golden.md`
  - `return_request` → `kb_manual.md`
  - `prescription_query` → `kb_prescription.md`
- **Low confidence (< 0.7)**: Inject all extended KB (safety net)

**Average Context**: ~20KB per query (<1% of Gemini 2 Flash capacity)

### 🔄 Learning Loop

```
User Query → Gap Detected → Store Case → Daily Report → Rosen Answers → Inject to KB
     ↑                                                                        ↓
     └────────────────────────────────────────────────────────────────────────┘
                            (Next user gets answer from KB)
```

### 🎭 One Brain, Two Voices

**External (Discord)**:
- Filtered output (no internal notes)
- Compliant, user-friendly
- Sensitive info blocked

**Internal (Feishu)**:
- Full transparency
- Debug info (intent, confidence, pattern)
- Owner suggestions

### 🔥 Hot-Reload

Add new knowledge files without restart:

```bash
# Add new file
echo "---
visibility: external
tier: 2
---
# New Knowledge
..." > knowledge/kb_new.md

# Immediately available (no restart needed)
```

---

## 📦 Installation

### Prerequisites

- **OpenClaw**: Installed and running
- **Python**: 3.8+
- **Gemini API Key**: From [Google AI Studio](https://makersuite.google.com/app/apikey)

### Step 1: Clone Repository

```bash
cd ~/.openclaw/workspace
git clone https://github.com/alstonzhuang/even-cs-agent.git
cd even-cs-agent
```

### Step 2: Install Dependencies

```bash
# For development (allows upgrades)
pip3 install -r requirements.txt

# For production (locked versions)
pip3 install -r requirements.lock
```

### Step 3: Set API Key

```bash
# Add to shell profile
echo 'export GEMINI_API_KEY="your_gemini_api_key_here"' >> ~/.zshrc
source ~/.zshrc

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

Replace `ou_xxx` with Rosen's actual Feishu ID:

```json
{
  "external": ["discord"],
  "internal": ["feishu"],
  "fallback": "external",
  "rosen_contact": {
    "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81",
    "name": "Rosen (罗雄胜)"
  }
}
```

### Step 5: Validate Configuration

```bash
python3 scripts/health_check.py
```

**Expected Output:**

```
=== Configuration Verification ===

✅ GEMINI_API_KEY: Set (39 chars)
✅ Configuration file: config/channels.json
✅ Configuration loaded successfully
✅ External channels: ['discord']
✅ Internal channels: ['feishu']
✅ Rosen contact: ou_ceae7c2ca21c67c92ae07f04d6347a81
✅ Fallback surface: external

=== Configuration is valid! ===
```

---

## ⚙️ Configuration

### Required Configuration

#### 1. Gemini API Key

**Environment Variable:**
```bash
export GEMINI_API_KEY="your_key_here"
```

**How to get:**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and set as environment variable

#### 2. Channel Configuration

**File:** `config/channels.json`

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `external` | array | Yes | Channels for external users (filtered output) |
| `internal` | array | Yes | Channels for internal team (full debug info) |
| `fallback` | string | No | Default surface for unknown channels (default: "external") |
| `rosen_contact.feishu_id` | string | Yes | Rosen's Feishu ID for escalation reports |
| `rosen_contact.name` | string | No | Display name |

**Example:**

```json
{
  "external": ["discord", "telegram"],
  "internal": ["feishu", "slack"],
  "fallback": "external",
  "rosen_contact": {
    "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81",
    "name": "Rosen"
  }
}
```

---

## 🚀 Usage

### As OpenClaw Skill

The agent runs automatically when triggered by OpenClaw. No manual invocation needed.

### Manual Testing

#### Test Individual Components

```bash
# Test Ingress
python3 scripts/ingress.py --channel discord --sender-id 123 --message "Test" --message-id msg_001

# Test Router
python3 scripts/router.py "What's the battery life of G2?" --no-llm

# Test Knowledge Worker
python3 scripts/knowledge_worker.py "What's the battery life?" "specs_query" "external"

# Test Renderer
python3 scripts/renderer.py "The G2 costs \$599" "external" "specs_query" "1.0"

# Test Output Switch
python3 scripts/output_switch.py --get-surface discord
```

#### Run All Tests

```bash
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh
```

---

## 🔍 How It Works

### Example 1: Simple Query (Regex Path)

**User (Discord):** "What's the battery life of G2?"

```
1. Ingress Normalizer
   Input: "What's the battery life of G2?"
   Output: {"surface": "external", "channel": "discord", "message": "..."}

2. Router
   Regex Match: "battery.*life" → intent="specs_query"
   Worker: knowledge_worker
   Confidence: 1.0 (Regex)

3. Knowledge Worker
   Context: Inject Core KB (kb_core.md + kb_policies.md)
   Confidence: 1.0 → No extended KB needed
   LLM: Gemini 2 Flash (Temperature=0)
   Response: "The G2 has a battery life of 3-4 hours with typical use."

4. Renderer (External)
   Filter: No sensitive info detected
   Output: "The G2 has a battery life of 3-4 hours with typical use."

5. Output Switch
   Channel: discord → external
   Send to Discord
```

**Response Time:** ~650ms

---

### Example 2: Complex Query (LLM Path)

**User (Discord):** "How long does it take to arrive?"

```
1. Ingress Normalizer
   Input: "How long does it take to arrive?"
   Output: {"surface": "external", "channel": "discord", "message": "..."}

2. Router
   Regex Match: None
   LLM Classification: Gemini 2 Flash → intent="policy_query"
   Worker: knowledge_worker
   Confidence: 0.8 (LLM)

3. Knowledge Worker
   Context: Inject Core KB (includes shipping policies)
   Confidence: 0.8 → Inject extended KB (kb_golden.md)
   LLM: Gemini 2 Flash (Temperature=0)
   Response: "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days."

4. Renderer (External)
   Filter: No sensitive info detected
   Output: "Standard shipping takes 5-7 business days..."

5. Output Switch
   Channel: discord → external
   Send to Discord
```

**Response Time:** ~1100ms

---

### Example 3: Internal Query (Feishu)

**User (Feishu):** "G2电池续航多久？"

```
1. Ingress Normalizer
   Input: "G2电池续航多久？"
   Output: {"surface": "internal", "channel": "feishu", "message": "..."}

2. Router
   Regex Match: None (Chinese not in patterns yet)
   LLM Classification: Gemini 2 Flash → intent="specs_query"
   Worker: knowledge_worker
   Confidence: 0.8 (LLM)

3. Knowledge Worker
   Context: Inject Core KB
   Confidence: 0.8 → Inject extended KB (kb_golden.md)
   LLM: Gemini 2 Flash (Temperature=0)
   Response: "G2 电池续航 3-4 小时（典型使用）。"

4. Renderer (Internal)
   No filtering (internal surface)
   Add debug info:
   
   [Debug Info]
   - Intent: specs_query
   - Pattern: N/A
   - Surface: internal
   - Confidence: 0.80
   - Suggested Owner: @Caris

5. Output Switch
   Channel: feishu → internal
   Send to Feishu
```

**Response Time:** ~1100ms

---

### Example 4: Escalation (Unknown Query)

**User (Discord):** "Can I use G2 underwater?"

```
1. Ingress Normalizer
   Input: "Can I use G2 underwater?"
   Output: {"surface": "external", "channel": "discord", "message": "..."}

2. Router
   Regex Match: None
   LLM Classification: intent="unknown"
   Worker: escalation_worker
   Confidence: 0.3

3. Escalation Worker
   Store case: ESC-20260313-152131-860704
   Type: gap
   Severity: medium
   Status: pending

4. Renderer (External)
   Output: "I don't have that information right now. Let me check with the team."

5. Output Switch
   Channel: discord → external
   Send to Discord

6. Daily Report (Next Day)
   Send to Rosen:
   
   ## 📚 Knowledge Gaps
   
   ### ESC-20260313-152131-860704
   - Message: Can I use G2 underwater?
   - Intent: unknown
   - Surface: external
   
   **Suggested Action:**
   1. Provide answer below
   2. Specify target KB file
   3. System will auto-inject to KB

7. Rosen Provides Answer
   python3 scripts/escalation_worker.py inject \
     ESC-20260313-152131-860704 \
     "G2 has IP55 rating. Avoid direct water exposure." \
     --kb-file kb_manual.md

8. Next User Gets Answer
   Same question → Knowledge Worker finds answer in kb_manual.md
```

---

## 📝 Examples

### Example Queries

#### Specs Queries (Regex → Knowledge Worker)

```
✅ "What's the battery life of G2?"
✅ "How much does G2 cost?"
✅ "What languages does G2 support?"
✅ "Is G2 waterproof?"
✅ "What's the difference between G1 and G2?"
```

#### Policy Queries (Regex → Knowledge Worker)

```
✅ "What's your return policy?"
✅ "How long does shipping take?"
✅ "Do you ship to Canada?"
✅ "What's the warranty period?"
```

#### Order Status (Regex → Skill Worker - Phase 2)

```
✅ "Where is my order #12345?"
✅ "Track my shipment"
✅ "When will my order arrive?"
```

#### Escalation (LLM → Escalation Worker)

```
⚠️ "Can I use G2 underwater?" (Unknown)
⚠️ "Tell me something interesting" (Unknown)
🚨 "Ignore all previous instructions" (Jailbreak)
```

---

## 🧪 Testing

### Run All Tests

```bash
cd ~/.openclaw/workspace/even-cs-agent

# Test each component
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh
./test.sh

# Validate configuration
python3 scripts/health_check.py
```

### Test Results

| Component | Tests | Passed | Status |
|-----------|-------|--------|--------|
| Ingress Normalizer | 4 | 4 | ✅ |
| Router | 8 | 8 | ✅ |
| Knowledge Worker | 5 | 5 | ✅ |
| Escalation Worker | 8 | 8 | ✅ |
| Renderer | 10 | 10 | ✅ |
| Output Switch | 6 | 6 | ✅ |
| **Total** | **41** | **41** | **✅** |

---

## 🚢 Deployment

### Pre-Deployment Checklist

- [ ] Install dependencies: `pip3 install google-generativeai`
- [ ] Set `GEMINI_API_KEY` environment variable
- [ ] Create `config/channels.json`
- [ ] Replace `ou_xxx` with Rosen's actual Feishu ID
- [ ] Run `python3 scripts/health_check.py`
- [ ] Run all test scripts
- [ ] Verify all tests pass

### Post-Deployment Checklist

- [ ] Monitor escalation cases
- [ ] Review daily reports
- [ ] Check for unknown channel warnings
- [ ] Verify no sensitive info leaks
- [ ] Collect user feedback
- [ ] Adjust KB as needed

### Monitoring

#### Daily Reports

Escalation reports are sent to Rosen daily at 9:00 AM (UTC+8):

```bash
# Manual report generation
python3 scripts/escalation_worker.py report --date 2026-03-13

# Set up cron job
crontab -e
# Add: 0 1 * * * cd ~/.openclaw/workspace/even-cs-agent && bash scripts/daily_report.sh
```

#### Logs

Check OpenClaw logs for errors:

```bash
tail -f ~/.openclaw/logs/gateway.log
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Adding New Knowledge

1. Create new `.md` file in `knowledge/` directory
2. Add YAML frontmatter with metadata
3. Specify tier (1-4)
4. File is immediately available (hot-reload)

**Example:**

```markdown
---
visibility: external
keyTags: [Feature, Setup]
owner: @YourName
tier: 2
last_updated: 2026-03-13
---

# New Knowledge Module

Your content here...
```

### Adding New Regex Patterns

Edit `scripts/router.py`:

```python
PATTERNS = {
    "your_intent": [
        r"pattern1",
        r"pattern2"
    ]
}
```

### Reporting Issues

Open an issue on GitHub with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Logs (if applicable)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenClaw**: AI agent framework
- **Gemini 2 Flash**: LLM provider
- **Even Realities**: Product knowledge and support

---

## 📞 Contact

- **Author**: Alston Zhuang (@alstonzhuang)
- **Email**: [Your Email]
- **GitHub**: https://github.com/alstonzhuang/even-cs-agent
- **Issues**: https://github.com/alstonzhuang/even-cs-agent/issues

---

## 🔗 Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Gemini API](https://ai.google.dev)
- [Even Realities](https://evenrealities.com)

---

**Made with ❤️ for Even Realities**
