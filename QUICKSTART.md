# Quick Start Guide

Get Even CS Agent running in 5 minutes!

---

## 🚀 Quick Install

```bash
# 1. Clone repository
cd ~/.openclaw/workspace
git clone https://github.com/alstonzhuang/even-cs-agent.git
cd even-cs-agent

# 2. Install dependencies
pip3 install google-generativeai

# 3. Set API key
export GEMINI_API_KEY="your_gemini_api_key_here"

# 4. Configure channels
nano config/channels.json
# Replace ou_xxx with Rosen's actual Feishu ID

# 5. Validate
python3 validate_config.py

# 6. Test
./test_ingress.sh
./test_router.sh
```

---

## ✅ Verification Checklist

- [ ] `GEMINI_API_KEY` is set
- [ ] `config/channels.json` exists
- [ ] Rosen's Feishu ID is configured (not `ou_xxx`)
- [ ] All tests pass
- [ ] Configuration validation passes

---

## 📝 Minimal Configuration

**config/channels.json:**

```json
{
  "external": ["discord"],
  "internal": ["feishu"],
  "rosen_contact": {
    "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81",
    "name": "Rosen"
  }
}
```

---

## 🧪 Quick Test

```bash
# Test a simple query
python3 scripts/router.py "What's the battery life of G2?" --no-llm

# Expected output:
# {
#   "intent": "specs_query",
#   "worker": "knowledge_worker",
#   "confidence": 1.0,
#   "method": "regex"
# }
```

---

## 🆘 Troubleshooting

### Issue: "GEMINI_API_KEY not set"

```bash
export GEMINI_API_KEY="your_key_here"
# Or add to ~/.zshrc permanently
```

### Issue: "Configuration file not found"

```bash
mkdir -p config
cp config/channels.json.example config/channels.json
nano config/channels.json
```

### Issue: "google-generativeai not installed"

```bash
pip3 install google-generativeai
```

---

## 📚 Next Steps

1. Read [README.md](README.md) for full documentation
2. Read [CONFIG.md](CONFIG.md) for configuration details
3. Explore [knowledge/](knowledge/) directory
4. Check [docs/](docs/) for architecture details

---

## 🎯 Common Use Cases

### Add New Knowledge

```bash
# Create new KB file
cat > knowledge/kb_new.md << 'EOF'
---
visibility: external
tier: 2
---
# New Knowledge
Your content here...
EOF

# Immediately available (no restart needed)
```

### Test External vs Internal

```bash
# External (Discord) - Filtered output
python3 scripts/renderer.py "The G2 costs \$599" "external" "specs_query" "1.0"

# Internal (Feishu) - Full debug info
python3 scripts/renderer.py "The G2 costs \$599" "internal" "specs_query" "1.0"
```

### Generate Escalation Report

```bash
python3 scripts/escalation_worker.py report --date 2026-03-13
```

---

**Need help?** Open an issue on [GitHub](https://github.com/alstonzhuang/even-cs-agent/issues)
