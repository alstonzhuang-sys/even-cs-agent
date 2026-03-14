# Even CS Agent - OpenClaw 配置需求说明

**问题**: 安装这个项目的 OpenClaw 是否需要修改核心配置文件？

**答案**: ❌ **不需要修改 OpenClaw 的核心配置文件**

---

## ✅ 无需修改的文件

安装 Even CS Agent 时，**不需要**修改以下 OpenClaw 核心文件：

- ❌ `~/.openclaw/workspace/SOUL.md` (OpenClaw 主 Agent 的身份)
- ❌ `~/.openclaw/workspace/AGENTS.md` (OpenClaw 系统配置)
- ❌ `~/.openclaw/workspace/USER.md` (用户信息)
- ❌ `~/.openclaw/workspace/TOOLS.md` (工具配置)
- ❌ `~/.openclaw/openclaw.json` (OpenClaw 主配置)

---

## 🎯 项目自包含设计

Even CS Agent 采用**完全自包含**的设计：

### 1. 独立的身份文件

项目内部有自己的身份定义：

```
even-cs-agent/
├── prompts/
│   ├── SOUL.md      # DivaD 的身份和个性
│   └── AGENT.md     # DivaD 的工具逻辑
```

这些文件**只在项目内部使用**，不会影响 OpenClaw 主 Agent。

### 2. 独立的知识库

```
even-cs-agent/
├── knowledge/
│   ├── kb_core.md        # 产品规格
│   ├── kb_policies.md    # 政策
│   ├── kb_golden.md      # 示例
│   ├── kb_manual.md      # 手册
│   └── kb_prescription.md # 处方
```

### 3. 独立的配置

```
even-cs-agent/
├── config/
│   └── channels.json     # 渠道配置
```

---

## 📦 安装步骤 (无需修改 OpenClaw 配置)

### Step 1: Clone 项目

```bash
cd ~/.openclaw/workspace
git clone https://github.com/alstonzhuang-sys/even-cs-agent.git
cd even-cs-agent
```

### Step 2: 安装依赖

```bash
pip3 install -r requirements.lock
```

### Step 3: 配置项目 (仅配置项目本身)

```bash
# 1. 复制配置模板
cp config/channels.json.example config/channels.json

# 2. 编辑配置
nano config/channels.json
# 替换 ou_xxx 为实际的 Feishu ID

# 3. 设置 API Key
export GEMINI_API_KEY="your_key_here"
```

### Step 4: 验证

```bash
python3 scripts/health_check.py
```

---

## 🔧 OpenClaw 如何调用这个项目？

### 方式 1: 通过 SKILL.md (推荐)

OpenClaw 会自动扫描 `~/.openclaw/workspace/` 下的所有 `SKILL.md` 文件。

当用户消息匹配 SKILL.md 中的触发条件时，OpenClaw 会：

1. 读取 `even-cs-agent/SKILL.md`
2. 按照 SKILL.md 中的指令执行
3. 调用 `main.py` 处理消息

**触发条件** (在 SKILL.md 中定义):
- 用户提到 "Even Realities"
- 用户提到 "G1" 或 "G2"
- 用户询问产品规格、价格、退货等

### 方式 2: 直接调用 main.py

```bash
echo '{"channel":"discord","sender_id":"123","message":"What is the battery life?"}' | python3 main.py
```

---

## 🎭 身份隔离机制

### OpenClaw 主 Agent (AtonBot)
- **身份**: 你的个人助理
- **配置**: `~/.openclaw/workspace/SOUL.md`
- **职责**: 处理所有通用任务

### Even CS Agent (DivaD)
- **身份**: Even Realities 客服专员
- **配置**: `even-cs-agent/prompts/SOUL.md`
- **职责**: 仅处理 Even Realities 相关问题

**关键**: 两个 Agent 完全独立，互不干扰。

---

## 🔄 工作流程示例

### 场景 1: 用户问 Even Realities 问题

```
用户: "What's the battery life of G2?"
  ↓
OpenClaw 主 Agent (AtonBot) 检测到关键词 "G2"
  ↓
AtonBot 读取 even-cs-agent/SKILL.md
  ↓
AtonBot 调用 even-cs-agent/main.py
  ↓
DivaD (Even CS Agent) 处理请求
  ↓
返回答案: "The G2 has a 220mAh battery..."
```

### 场景 2: 用户问其他问题

```
用户: "What's the weather today?"
  ↓
OpenClaw 主 Agent (AtonBot) 检测到不匹配 Even CS Agent
  ↓
AtonBot 直接处理 (使用 weather skill)
  ↓
返回答案: "Today's weather is..."
```

---

## ⚙️ 唯一需要的环境变量

```bash
# 仅需要设置 Gemini API Key
export GEMINI_API_KEY="your_gemini_api_key_here"

# 添加到 shell profile (永久生效)
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🚫 常见误区

### ❌ 误区 1: 需要修改 OpenClaw 的 SOUL.md

**错误**: 将 DivaD 的身份写入 `~/.openclaw/workspace/SOUL.md`

**正确**: DivaD 的身份已经在 `even-cs-agent/prompts/SOUL.md` 中定义，无需修改 OpenClaw 主配置。

### ❌ 误区 2: 需要在 AGENTS.md 中注册

**错误**: 在 `~/.openclaw/workspace/AGENTS.md` 中添加 Even CS Agent 配置

**正确**: OpenClaw 会自动扫描所有 SKILL.md 文件，无需手动注册。

### ❌ 误区 3: 需要修改 openclaw.json

**错误**: 在 `~/.openclaw/openclaw.json` 中添加 Even CS Agent 配置

**正确**: 项目使用独立的 `config/channels.json`，不需要修改 OpenClaw 主配置。

---

## 📊 配置文件对比

| 文件 | 位置 | 用途 | 是否需要修改 |
|------|------|------|--------------|
| **OpenClaw 核心配置** |
| `SOUL.md` | `~/.openclaw/workspace/` | OpenClaw 主 Agent 身份 | ❌ 不需要 |
| `AGENTS.md` | `~/.openclaw/workspace/` | OpenClaw 系统配置 | ❌ 不需要 |
| `openclaw.json` | `~/.openclaw/` | OpenClaw 主配置 | ❌ 不需要 |
| **Even CS Agent 配置** |
| `SOUL.md` | `even-cs-agent/prompts/` | DivaD 身份 | ✅ 已包含 |
| `AGENT.md` | `even-cs-agent/prompts/` | DivaD 工具逻辑 | ✅ 已包含 |
| `channels.json` | `even-cs-agent/config/` | 渠道配置 | ✅ 需要配置 |

---

## ✅ 总结

### 需要做的事情

1. ✅ Clone 项目到 `~/.openclaw/workspace/`
2. ✅ 安装 Python 依赖 (`pip3 install -r requirements.lock`)
3. ✅ 配置项目本身 (`config/channels.json`)
4. ✅ 设置环境变量 (`GEMINI_API_KEY`)

### 不需要做的事情

1. ❌ 修改 OpenClaw 的 SOUL.md
2. ❌ 修改 OpenClaw 的 AGENTS.md
3. ❌ 修改 OpenClaw 的 openclaw.json
4. ❌ 修改 OpenClaw 的任何核心配置

---

## 🎯 设计原则

Even CS Agent 遵循 **"零侵入"** 原则：

- **自包含**: 所有配置和逻辑都在项目内部
- **即插即用**: Clone 后配置即可使用
- **无污染**: 不修改 OpenClaw 核心文件
- **易卸载**: 删除项目文件夹即可完全移除

这样设计的好处：

1. **安全**: 不会破坏 OpenClaw 主 Agent
2. **灵活**: 可以同时运行多个专业 Agent
3. **可维护**: 项目更新不影响 OpenClaw
4. **可移植**: 可以轻松分享给其他 OpenClaw 用户

---

**结论**: Even CS Agent 是一个**完全独立**的项目，安装时**无需修改 OpenClaw 的任何核心配置文件**。
