# GitHub Setup Instructions

Follow these steps to push Even CS Agent to GitHub.

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `even-cs-agent`
   - **Description**: `Intelligent Customer Support Agent for Even Realities | Built on OpenClaw | Powered by Gemini 2 Flash`
   - **Visibility**: Public (or Private if you prefer)
   - **⚠️ Important**: Do NOT initialize with README, .gitignore, or license (we already have them)

3. Click "Create repository"

---

## Step 2: Add Remote and Push

```bash
cd ~/.openclaw/workspace/even-cs-agent

# Add remote
git remote add origin https://github.com/alstonzhuang/even-cs-agent.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Step 3: Configure Repository Settings

### Add Topics (Tags)

Go to repository settings and add these topics:
- `openclaw`
- `ai-agent`
- `customer-support`
- `chatbot`
- `gemini`
- `python`
- `even-realities`
- `ar-glasses`

### Add Description

```
🤖 Intelligent Customer Support Agent for Even Realities | Built on OpenClaw | Powered by Gemini 2 Flash
```

### Add Website (Optional)

```
https://evenrealities.com
```

---

## Step 4: Create Release (Optional)

1. Go to "Releases" → "Create a new release"
2. Tag version: `v2.1.0`
3. Release title: `Even CS Agent v2.1 - Production Ready`
4. Description:

```markdown
## 🎉 Even CS Agent v2.1 - Production Ready

First production-ready release of Even CS Agent, an intelligent customer support bot for Even Realities.

### ✨ Features

- **Dual-Surface Support**: External (Discord) + Internal (Feishu)
- **Deterministic Routing**: 90% Regex + 10% LLM
- **Full Context Injection**: Tiered knowledge base (Tier 1-4)
- **Learning Loop**: Escalations → Knowledge Base
- **Hot-Reload**: Add KB files without restart
- **One Brain, Two Voices**: Dynamic rendering based on surface

### 📊 Stats

- **Components**: 6/6 implemented
- **Tests**: 41/41 passed (100%)
- **Knowledge Base**: 5 files (~35KB)
- **Average Latency**: ~695ms

### 📦 Installation

```bash
git clone https://github.com/alstonzhuang/even-cs-agent.git
cd even-cs-agent
pip3 install -r requirements.txt
export GEMINI_API_KEY="your_key_here"
python3 validate_config.py
```

See [README.md](README.md) for full documentation.

### 🙏 Acknowledgments

Built with OpenClaw and Gemini 2 Flash.
```

5. Click "Publish release"

---

## Step 5: Add README Badges (Optional)

Add these badges to the top of README.md:

```markdown
[![GitHub release](https://img.shields.io/github/v/release/alstonzhuang/even-cs-agent)](https://github.com/alstonzhuang/even-cs-agent/releases)
[![GitHub stars](https://img.shields.io/github/stars/alstonzhuang/even-cs-agent)](https://github.com/alstonzhuang/even-cs-agent/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/alstonzhuang/even-cs-agent)](https://github.com/alstonzhuang/even-cs-agent/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## Step 6: Verify

1. Visit https://github.com/alstonzhuang/even-cs-agent
2. Check that all files are present
3. Verify README renders correctly
4. Test clone on a different machine

---

## 🎉 Done!

Your project is now on GitHub and ready to share!

**Share URL**: https://github.com/alstonzhuang/even-cs-agent
