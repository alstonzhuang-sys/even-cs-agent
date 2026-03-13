# Even CS Agent Configuration

## Required Configuration

### 1. Gemini API Key

**Environment Variable:**
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

**How to get:**
1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and set as environment variable

**Verification:**
```bash
echo $GEMINI_API_KEY
# Should output your API key
```

---

### 2. Channel Configuration

**File:** `config/channels.json`

**Format:**
```json
{
  "external": ["discord"],
  "internal": ["feishu"],
  "rosen_contact": {
    "feishu_id": "ou_xxx",
    "name": "Rosen (罗雄胜)"
  }
}
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `external` | array | Channels for external users (filtered output) | `["discord", "telegram"]` |
| `internal` | array | Channels for internal team (full debug info) | `["feishu"]` |
| `rosen_contact.feishu_id` | string | Rosen's Feishu ID for escalation reports | `"ou_ceae7c2ca21c67c92ae07f04d6347a81"` |
| `rosen_contact.name` | string | Display name | `"Rosen (罗雄胜)"` |

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ~/.openclaw/workspace/even-cs-agent
pip3 install google-generativeai
```

### Step 2: Set Gemini API Key

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Create Channel Configuration

```bash
mkdir -p config
cat > config/channels.json << 'EOF'
{
  "external": ["discord"],
  "internal": ["feishu"],
  "rosen_contact": {
    "feishu_id": "ou_xxx",
    "name": "Rosen"
  }
}
EOF
```

**⚠️ Important:** Replace `ou_xxx` with Rosen's actual Feishu ID.

### Step 4: Verify Configuration

```bash
# Test Gemini API key
python3 scripts/knowledge_worker.py "Test query" "specs_query" "external" --debug

# Test channel configuration
python3 scripts/output_switch.py --verify
```

---

## Configuration Examples

### Example 1: Discord + Feishu (Default)

```json
{
  "external": ["discord"],
  "internal": ["feishu"]
}
```

**Behavior:**
- Discord messages → External surface → Filtered output
- Feishu messages → Internal surface → Full debug info

### Example 2: Multiple External Channels

```json
{
  "external": ["discord", "telegram", "whatsapp"],
  "internal": ["feishu"]
}
```

**Behavior:**
- Discord/Telegram/WhatsApp → External surface
- Feishu → Internal surface

### Example 3: Multiple Internal Channels

```json
{
  "external": ["discord"],
  "internal": ["feishu", "slack"]
}
```

**Behavior:**
- Discord → External surface
- Feishu/Slack → Internal surface

---

## Troubleshooting

### Issue 1: "GEMINI_API_KEY not set"

**Solution:**
```bash
export GEMINI_API_KEY="your_key_here"
# Or add to ~/.zshrc permanently
```

### Issue 2: "Channel configuration not found"

**Solution:**
```bash
# Create config directory
mkdir -p ~/.openclaw/workspace/even-cs-agent/config

# Create channels.json
cat > ~/.openclaw/workspace/even-cs-agent/config/channels.json << 'EOF'
{
  "external": ["discord"],
  "internal": ["feishu"]
}
EOF
```

### Issue 3: "Unknown channel: xxx"

**Solution:**
Add the channel to `channels.json`:
```json
{
  "external": ["discord", "xxx"],
  "internal": ["feishu"]
}
```

---

## Security Notes

### 1. API Key Protection

**Do NOT:**
- ❌ Commit API key to Git
- ❌ Share API key in public channels
- ❌ Hard-code API key in scripts

**Do:**
- ✅ Use environment variables
- ✅ Add `.env` to `.gitignore`
- ✅ Rotate keys regularly

### 2. Channel Configuration

**Do NOT:**
- ❌ Expose internal channels to external users
- ❌ Mix external/internal channels

**Do:**
- ✅ Clearly separate external/internal
- ✅ Review configuration regularly
- ✅ Test with both surfaces

---

## Advanced Configuration

### Custom Fallback Behavior

**File:** `config/channels.json`

```json
{
  "external": ["discord"],
  "internal": ["feishu"],
  "fallback": "external",
  "rosen_contact": {
    "feishu_id": "ou_xxx",
    "name": "Rosen"
  }
}
```

**Field:** `fallback`
- `"external"` (default): Unknown channels treated as external (safer)
- `"internal"`: Unknown channels treated as internal (riskier)

---

## Validation

### Automatic Validation

The system will validate configuration on startup:

```python
# Check 1: Gemini API key exists
if not os.environ.get("GEMINI_API_KEY"):
    raise ConfigError("GEMINI_API_KEY not set")

# Check 2: Channel configuration exists
if not os.path.exists("config/channels.json"):
    raise ConfigError("config/channels.json not found")

# Check 3: Required fields present
config = load_config()
if "external" not in config or "internal" not in config:
    raise ConfigError("Missing required fields in channels.json")
```

### Manual Validation

```bash
# Run validation script
python3 scripts/validate_config.py

# Expected output:
# ✅ GEMINI_API_KEY: Set
# ✅ config/channels.json: Found
# ✅ External channels: ['discord']
# ✅ Internal channels: ['feishu']
# ✅ Rosen contact: ou_xxx
# 
# Configuration is valid!
```

---

## Next Steps

After configuration:

1. ✅ Set `GEMINI_API_KEY`
2. ✅ Create `config/channels.json`
3. ✅ Replace `ou_xxx` with Rosen's actual ID
4. ✅ Run validation script
5. ✅ Test with sample queries
6. ✅ Deploy to production

---

**Last Updated:** 2026-03-13  
**Maintainer:** @Alston
