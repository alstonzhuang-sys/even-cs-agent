# Architecture V2 - Skill-Based Design

## 核心约束

1. **插件化部署** - 必须做成 OpenClaw Skill，任何人安装后都能 100% follow
2. **降低 LLM 依赖** - 尽可能用 hard coding，适配低端模型（Gemini 2 Flash）

---

## 重新设计：从 Pipeline 到 Skill

### 原架构的问题

原设计是一个完整的 Pipeline（Ingress → Router → Workers → Renderer），需要：
- 独立的 Python 服务
- 复杂的状态管理
- 难以打包为 Skill

### 新架构：Skill-First Design

**核心理念：** 将每个功能模块做成独立的 OpenClaw Skill，通过 SKILL.md 驱动执行。

```
User Message
    ↓
OpenClaw (Main Agent)
    ↓
SKILL.md (Router Logic)
    ↓
├─ Hard-coded Rules (Regex Match)
│  ├─ Order Status → Call Shopify API
│  ├─ Return Request → Check Eligibility
│  └─ Specs Query → Read kb_core.md
│
└─ LLM Fallback (Only for ambiguous cases)
   └─ Knowledge Worker → Full Context Injection
```

---

## Skill 结构

### 目录结构

```
even-cs-agent/
├── SKILL.md                  # 主 Skill 文件（Router + Orchestrator）
├── knowledge/                # 知识库目录
│   ├── kb_core.md           # Tier 1: 核心事实
│   ├── kb_policies.md       # Tier 2: 规则
│   ├── kb_golden.md         # Tier 3: 金标准话术
│   └── kb_evenHubPilot.md   # Tier 4: 长尾知识
├── prompts/                  # 提示词目录
│   ├── SOUL.md              # 运行时人格
│   └── AGENT.md             # 工具逻辑
├── scripts/                  # 脚本目录
│   ├── router.py            # Router 逻辑（Regex + Intent Detection）
│   ├── knowledge_worker.py  # Knowledge Worker（Full Context Injection）
│   ├── renderer.py          # Renderer（Policy Filter）
│   └── utils.py             # 工具函数
├── tests/                    # 测试目录
│   ├── test_router.py       # Router 测试
│   ├── test_knowledge.py    # Knowledge Worker 测试
│   └── test_cases.yaml      # 测试用例（PromptFoo 格式）
└── config/                   # 配置目录
    └── channels.json        # 渠道配置（Discord/Feishu）
```

---

## SKILL.md 设计

### 核心逻辑

SKILL.md 是整个系统的"大脑"，负责：
1. **接收用户消息**
2. **执行 Router 逻辑**（优先 Regex，兜底 LLM）
3. **调用对应的 Worker**
4. **执行 Renderer**（根据 surface 过滤输出）

### SKILL.md 伪代码

```markdown
# DivaD CS Agent Skill

## When to Use This Skill

Use this skill when:
- User asks about Even Realities products (G1/G2)
- User asks about orders, shipping, returns, refunds
- User asks for product specs, pricing, compatibility
- User needs troubleshooting help

## Execution Flow

### Step 1: Detect Surface (External vs Internal)

```python
# Read from OpenClaw context
channel = context.get("channel")  # "discord" or "feishu"

if channel == "discord":
    surface = "external"
elif channel == "feishu":
    surface = "internal"
```

### Step 2: Router (Hard-coded Rules First)

```python
import re

# High-priority Regex patterns
patterns = {
    "order_status": r"(order|shipment|tracking|where is my).*(#?\d{4,})",
    "return_request": r"(return|refund|send back).*(order|product|G1|G2)",
    "specs_query": r"(battery|weight|display|resolution|language|price|cost)",
    "jailbreak": r"(ignore.*instruction|you are now|disregard|system prompt)"
}

# Match patterns
for intent, pattern in patterns.items():
    if re.search(pattern, user_message, re.IGNORECASE):
        matched_intent = intent
        break
else:
    # No match → LLM Fallback
    matched_intent = llm_classify(user_message)
```

### Step 3: Execute Worker

```python
if matched_intent == "order_status":
    # Extract Order ID
    order_id = re.search(r"#?(\d{4,})", user_message).group(1)
    
    # Call Shopify API (via exec tool)
    result = exec(f"python scripts/check_order.py {order_id}")
    
    # Format response
    response = format_order_status(result)

elif matched_intent == "return_request":
    # Check eligibility
    result = exec(f"python scripts/check_return_eligibility.py")
    
    # Format response
    response = format_return_response(result)

elif matched_intent == "specs_query":
    # Read kb_core.md
    kb_core = read("knowledge/kb_core.md")
    
    # Full Context Injection
    context = f"{kb_core}\n\nUser: {user_message}"
    
    # Call LLM (Gemini 2 Flash)
    response = llm_generate(context, temperature=0)

elif matched_intent == "jailbreak":
    # Hard-coded refusal
    response = "I cannot fulfill that request. How can I help you with Even Realities products?"
```

### Step 4: Renderer (Policy Filter)

```python
if surface == "external":
    # Filter sensitive info
    response = filter_internal_info(response)
    
elif surface == "internal":
    # Add debug info
    response += f"\n\n[Debug Info]\n- Intent: {matched_intent}\n- Confidence: {confidence}\n- Source: {source}"
```

### Step 5: Return Response

```python
return response
```
```

---

## Hard-coded Components

### 1. Router (scripts/router.py)

**职责：** 使用 Regex 匹配高危关键词，返回 Intent

**输入：** User message

**输出：** Intent + Confidence

**实现：**

```python
import re

PATTERNS = {
    "order_status": [
        r"order\s*#?\d{4,}",
        r"where is my.*order",
        r"track.*shipment",
        r"shipping.*status"
    ],
    "return_request": [
        r"return.*product",
        r"refund.*order",
        r"send.*back",
        r"cancel.*order"
    ],
    "specs_query": [
        r"battery.*life",
        r"how much.*cost",
        r"what.*price",
        r"support.*language",
        r"compatible.*with"
    ],
    "jailbreak": [
        r"ignore.*instruction",
        r"you are now",
        r"disregard.*programming",
        r"system prompt"
    ]
}

def route(message):
    message_lower = message.lower()
    
    for intent, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                return {
                    "intent": intent,
                    "confidence": 1.0,
                    "method": "regex"
                }
    
    # No match → LLM Fallback
    return {
        "intent": "unknown",
        "confidence": 0.0,
        "method": "none"
    }
```

---

### 2. Knowledge Worker (scripts/knowledge_worker.py)

**职责：** Full Context Injection + LLM 生成

**输入：** User message + Surface

**输出：** Response + Sources

**实现：**

```python
def knowledge_worker(message, surface):
    # Read knowledge base
    kb_core = read_file("knowledge/kb_core.md")
    kb_policies = read_file("knowledge/kb_policies.md")
    kb_golden = read_file("knowledge/kb_golden.md")
    
    # Build context
    context = f"""
{kb_core}

{kb_policies}

{kb_golden}

User: {message}
"""
    
    # Call LLM (Gemini 2 Flash)
    response = llm_generate(
        context,
        temperature=0,
        max_tokens=300
    )
    
    # Extract sources (simple keyword matching)
    sources = extract_sources(response, [kb_core, kb_policies, kb_golden])
    
    return {
        "response": response,
        "sources": sources,
        "confidence": 0.8  # Placeholder
    }
```

---

### 3. Renderer (scripts/renderer.py)

**职责：** 根据 Surface 过滤输出

**输入：** Response + Surface

**输出：** Filtered Response

**实现：**

```python
def render(response, surface, metadata):
    if surface == "external":
        # Filter internal info
        response = filter_internal_keywords(response)
        
        # Check visibility
        if metadata.get("visibility") == "internal":
            return "I don't have that information right now. Let me check with the team."
        
        return response
    
    elif surface == "internal":
        # Add debug info
        debug_info = f"""
[Debug Info]
- Intent: {metadata.get('intent')}
- Confidence: {metadata.get('confidence')}
- Sources: {metadata.get('sources')}
- Owner: {metadata.get('owner', '@Caris')}
"""
        return response + "\n\n" + debug_info

def filter_internal_keywords(text):
    # Remove internal keywords
    internal_keywords = [
        "internal", "debug", "confidence", "owner",
        "@Caris", "@Rosen", "@David"
    ]
    
    for keyword in internal_keywords:
        text = text.replace(keyword, "")
    
    return text
```

---

## LLM 依赖最小化策略

### 1. Router: 90% Regex, 10% LLM

**Regex 覆盖的场景：**
- Order status query (订单查询)
- Return request (退货请求)
- Specs query (规格查询)
- Jailbreak attempt (越狱尝试)

**LLM 仅用于：**
- 模糊查询（"How long does it last?"）
- 复杂问题（"Can I use G2 with my prescription glasses?"）

### 2. Knowledge Worker: Full Context Injection

**优势：**
- 不依赖 VectorDB（减少依赖）
- 不需要 Embedding（减少成本）
- 完整逻辑链（减少幻觉）

**劣势：**
- Context 长度限制（Gemini 2 Flash 支持 1M tokens，足够）

### 3. Renderer: 100% Hard-coded

**完全不依赖 LLM：**
- 使用 Metadata 过滤
- 使用关键词匹配
- 使用模板生成

---

## 部署流程

### 1. 安装 Skill

```bash
# Clone skill to OpenClaw workspace
cd ~/.openclaw/workspace/skills
git clone https://github.com/your-org/even-cs-agent.git

# Or use clawhub
clawhub install even-cs-agent
```

### 2. 配置 Channels

编辑 `config/channels.json`：

```json
{
  "discord": {
    "enabled": true,
    "surface": "external"
  },
  "feishu": {
    "enabled": true,
    "surface": "internal"
  }
}
```

### 3. 测试

```bash
# Run tests
cd ~/.openclaw/workspace/skills/even-cs-agent
python -m pytest tests/
```

### 4. 启用 Skill

OpenClaw 会自动扫描 `skills/` 目录，读取 `SKILL.md`。

---

## 关键优势

### 1. 插件化
- 任何人安装后都能 100% follow
- 不需要修改 OpenClaw 核心代码
- 易于分发和更新

### 2. 低 LLM 依赖
- Router: 90% Regex（确定性）
- Knowledge Worker: Full Context Injection（减少幻觉）
- Renderer: 100% Hard-coded（零 LLM）

### 3. 可测试
- 每个组件可独立测试
- 使用 PromptFoo 自动化测试
- 易于调试和优化

### 4. 可扩展
- 新增 Intent → 添加 Regex Pattern
- 新增知识 → 更新 kb_*.md
- 新增渠道 → 更新 channels.json

---

## 下一步

1. **重写 SKILL.md** - 将 Router + Workers + Renderer 整合为单一 Skill
2. **实现 scripts/** - 创建 router.py, knowledge_worker.py, renderer.py
3. **简化知识库** - 确保 kb_*.md 可以完整注入 Context
4. **创建测试用例** - 使用 PromptFoo 测试 Regex 覆盖率
5. **打包为 Skill** - 确保可以通过 clawhub 安装

---

**核心原则：**
- **Hard-code everything that can be hard-coded**
- **LLM only for ambiguous cases**
- **100% reproducible behavior**
