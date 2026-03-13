# SKILL.md 实现指南

## 问题：OpenClaw 如何执行 SKILL.md？

**关键理解：** SKILL.md 不是直接可执行的代码，而是给 OpenClaw Agent（LLM）的**指令文档**。

OpenClaw 的执行流程：
1. 用户发送消息
2. OpenClaw 读取 `SKILL.md`
3. OpenClaw（LLM）根据 SKILL.md 的指令，调用工具（`read`, `exec`, `write` 等）
4. OpenClaw 返回结果

---

## 当前架构的问题

### 问题 1: SKILL.md 中的伪代码无法直接执行

**SKILL.md 中的代码：**
```python
if matched_intent == "specs_query":
    kb_core = read("knowledge/kb_core.md")
    context = f"{kb_core}\n\nUser: {user_message}"
    response = llm_generate(context, temperature=0)
```

**问题：**
- `llm_generate()` 不是 OpenClaw 工具
- LLM 需要"理解"这段伪代码，然后自己调用正确的工具
- 依赖 LLM 的理解能力（违反"降低 LLM 依赖"原则）

---

## 解决方案：两种实现方式

### 方式 1: 纯 SKILL.md（依赖 LLM 理解）

**优点：**
- 简单，无需额外脚本
- 灵活，LLM 可以自适应

**缺点：**
- 依赖 LLM 理解能力（需要高质量 LLM）
- 不确定性（相同输入可能产生不同输出）
- 难以调试

**适用场景：**
- 使用高质量 LLM（Opus 4.6, Gemini 3 Pro）
- 可以接受一定的不确定性

---

### 方式 2: SKILL.md + Python 脚本（推荐）

**优点：**
- 确定性（相同输入，相同输出）
- 低 LLM 依赖（LLM 只需调用脚本）
- 易于调试和测试

**缺点：**
- 需要编写额外的 Python 脚本
- 稍微复杂一些

**适用场景：**
- 使用低端 LLM（Gemini 2 Flash）
- 需要 100% 可复现行为
- **推荐用于生产环境**

---

## 方式 2 的实现方案

### 架构

```
User Message
    ↓
OpenClaw (LLM)
    ↓
Read SKILL.md (简化版指令)
    ↓
Call Python Scripts (确定性逻辑)
    ↓
├─ scripts/router.py (Intent Detection)
├─ scripts/knowledge_worker.py (Knowledge Query)
├─ scripts/renderer.py (Policy Filter)
└─ scripts/helpers.py (Utility Functions)
    ↓
Return Response
```

### 简化版 SKILL.md

**核心思想：** SKILL.md 只包含高层指令，具体逻辑由 Python 脚本实现。

```markdown
# DivaD CS Agent Skill

## When to Use This Skill

Use when user asks about Even Realities products (G1/G2).

## Execution Steps

### Step 1: Detect Surface

```bash
# Detect if this is external (Discord) or internal (Feishu)
channel=$(echo "$CONTEXT" | jq -r '.channel')

if [ "$channel" = "discord" ]; then
    surface="external"
elif [ "$channel" = "feishu" ]; then
    surface="internal"
else
    surface="external"
fi
```

### Step 2: Route Intent

```bash
# Call router.py to detect intent
result=$(python3 scripts/router.py "$USER_MESSAGE")
intent=$(echo "$result" | jq -r '.intent')
confidence=$(echo "$result" | jq -r '.confidence')
```

### Step 3: Execute Worker

```bash
if [ "$intent" = "jailbreak" ]; then
    # Hard-coded response
    response="I cannot fulfill that request. How can I help you with Even Realities products?"
    
elif [ "$intent" = "specs_query" ] || [ "$intent" = "policy_query" ] || [ "$intent" = "knowledge_query" ]; then
    # Call knowledge_worker.py
    response=$(python3 scripts/knowledge_worker.py "$USER_MESSAGE" "$intent" "$surface")
    
elif [ "$intent" = "order_status" ]; then
    # TODO: Call Shopify API
    response="To check your order status, I'll need your order number."
    
else
    # Default to knowledge query
    response=$(python3 scripts/knowledge_worker.py "$USER_MESSAGE" "knowledge_query" "$surface")
fi
```

### Step 4: Render Response

```bash
# Call renderer.py to filter output
final_response=$(python3 scripts/renderer.py "$response" "$surface" "$intent")
```

### Step 5: Return

```bash
echo "$final_response"
```
```

---

## 需要实现的 Python 脚本

### 1. router.py ✅ (已完成)

**输入：** User message

**输出：** JSON
```json
{
  "intent": "specs_query",
  "confidence": 1.0,
  "method": "regex",
  "matched_pattern": "battery.*life"
}
```

**测试：**
```bash
python3 scripts/router.py "What's the battery life of G2?"
```

---

### 2. knowledge_worker.py (待实现)

**输入：**
- User message
- Intent (specs_query, policy_query, knowledge_query)
- Surface (external, internal)

**输出：** Response text

**实现逻辑：**
1. 读取对应的知识库文件
2. 构建 Context（Full Context Injection）
3. 调用 LLM（Gemini 2 Flash, Temperature=0）
4. 返回 Response

**示例：**
```bash
python3 scripts/knowledge_worker.py "What's the battery life of G2?" "specs_query" "external"
# Output: "The G2 has a 220mAh battery that provides 3-4 hours of typical use."
```

---

### 3. renderer.py (待实现)

**输入：**
- Response text
- Surface (external, internal)
- Intent

**输出：** Filtered response

**实现逻辑：**
1. 如果 surface == "external"：
   - 调用 `helpers.filter_internal_keywords()`
   - 调用 `helpers.contains_sensitive_info()`
   - 如果包含敏感信息，返回安全回复
2. 如果 surface == "internal"：
   - 调用 `helpers.format_debug_info()`
   - 添加 Debug 信息

**示例：**
```bash
python3 scripts/renderer.py "The G2 has a 220mAh battery..." "external" "specs_query"
# Output: "The G2 has a 220mAh battery..."

python3 scripts/renderer.py "The G2 has a 220mAh battery..." "internal" "specs_query"
# Output: "The G2 has a 220mAh battery...\n\n[Debug Info]\n- Intent: specs_query\n..."
```

---

### 4. helpers.py ✅ (已完成)

**功能：**
- `extract_section()` - 提取 Markdown 章节
- `contains_sensitive_info()` - 检测敏感信息
- `get_owner()` - 获取负责人
- `filter_internal_keywords()` - 过滤内部关键词
- `format_debug_info()` - 格式化 Debug 信息

**测试：**
```bash
python3 scripts/helpers.py extract_section knowledge/kb_core.md "G2 Specifications"
python3 scripts/helpers.py contains_sensitive "cost $50"
python3 scripts/helpers.py get_owner specs_query
python3 scripts/helpers.py filter_keywords "This is from kb_core.md"
```

---

## 下一步实现计划

### 立即实现（今天）

1. **knowledge_worker.py**
   - 读取知识库文件
   - 构建 Context
   - 调用 LLM（使用 OpenClaw 的 LLM API）
   - 返回 Response

2. **renderer.py**
   - 实现 External/Internal 过滤逻辑
   - 调用 helpers.py 的函数
   - 返回最终 Response

3. **简化版 SKILL.md**
   - 重写为高层指令
   - 明确调用 Python 脚本
   - 减少对 LLM 理解能力的依赖

### 短期实现（本周）

1. **测试完整流程**
   - 在 OpenClaw 中测试 SKILL.md
   - 验证所有脚本正常工作
   - 测试 External/Internal 输出差异

2. **创建测试用例**
   - 至少 50 个基础测试用例
   - 测试 Regex 覆盖率
   - 测试 LLM 准确性

---

## 关键问题解答

### Q1: OpenClaw 如何调用 Python 脚本？

**A:** 使用 `exec` 工具：

```markdown
Call the `exec` tool with:
- command: "python3 scripts/router.py 'What is the battery life?'"
- workdir: "~/.openclaw/workspace/skills/even-cs-agent"
```

### Q2: 如何在 Python 脚本中调用 LLM？

**A:** 有两种方式：

**方式 1: 使用 OpenClaw 的 LLM API（推荐）**
```python
# 在 SKILL.md 中调用
response = llm_generate(context, temperature=0, max_tokens=300)
```

**方式 2: 直接调用 Gemini API**
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(context)
```

### Q3: 如何传递 Context 给 Python 脚本？

**A:** 通过命令行参数或环境变量：

```bash
# 方式 1: 命令行参数
python3 scripts/knowledge_worker.py "$USER_MESSAGE" "$INTENT" "$SURFACE"

# 方式 2: 环境变量
export USER_MESSAGE="What's the battery life?"
export INTENT="specs_query"
export SURFACE="external"
python3 scripts/knowledge_worker.py
```

---

## 总结

**当前状态：**
- ✅ router.py 已完成并测试通过
- ✅ helpers.py 已完成并测试通过
- 🔲 knowledge_worker.py 待实现
- 🔲 renderer.py 待实现
- 🔲 简化版 SKILL.md 待重写

**下一步：**
1. 实现 knowledge_worker.py
2. 实现 renderer.py
3. 重写 SKILL.md（简化版）
4. 测试完整流程

**核心原则：**
- **Hard-code everything that can be hard-coded**
- **LLM only for ambiguous cases**
- **Python scripts for deterministic logic**
- **SKILL.md for high-level orchestration**
