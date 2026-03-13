# 架构设计详细说明

## 整体架构

DivaD v2.1 采用流水线架构，摒弃复杂的"多智能体协作"模型：

```
Ingress Normalizer -> Router -> Worker(s) -> Renderer OR Escalator
```

## 数据流

### 1. Ingress Normalizer (入口标准化)

**职责：** 将来自不同渠道的消息统一转化为标准 JSON Payload

**输入：**
- Discord 消息
- Feishu 消息

**输出：**
```json
{
  "surface": "external" | "internal",
  "user_id": "...",
  "message": "...",
  "intent_hints": ["shipping", "urgent"],
  "session_id": "...",
  "timestamp": "..."
}
```

**关键逻辑：**
- **Context Management:** 执行 Session Reset。每一条新的 Ticket/咨询都被视为一个全新的 Session，防止历史对话污染 Context Window
- **Surface Detection:** 根据消息来源自动标记 `surface` 字段
  - Discord → `external`
  - Feishu → `internal`
- **Intent Pre-tagging:** 使用轻量级规则提取意图提示（如检测到 "urgent", "ASAP" 等关键词）

**实现要点：**
- 暂时先做单轮对话
- 为多轮对话打好基础（保留 `user_id` 和 `session_id` 字段）

---

### 2. Router (决策中枢)

**职责：** 决定调用哪个 Worker

**策略：** Code-First Strategy

**决策流程：**

```
1. Regex 匹配高危关键词
   ├─ "Refund" → Skill Worker (Phase 2)
   ├─ "Order #" → Skill Worker (Phase 2)
   ├─ "Return" → Skill Worker (Phase 2)
   └─ "DFU" → Skill Worker (Phase 2)

2. 如果 Regex 无匹配
   └─ 调用轻量级 LLM 分类
      ├─ "Knowledge Query" → Knowledge Worker
      ├─ "Unknown/Risk" → Escalation Worker
      └─ "Ambiguous" → Escalation Worker
```

**输出：**
```json
{
  "worker_type": "skill" | "knowledge" | "escalation",
  "confidence": 0.95,
  "matched_rule": "regex:order_number" | "llm:knowledge_query"
}
```

**实现要点：**
- 优先使用 Regex（快速、确定性）
- LLM 仅作为兜底分类器
- 记录每次路由决策（用于后续优化）

---

### 3. Workers (执行单元)

#### 3.1 Skill Worker (Phase 2 - 暂不实现)

**职责：** 执行确定性代码（查询 Shopify API，执行 Testflight 邀请...）

**触发条件：**
- Regex 匹配到高危关键词
- Router 明确指定

**执行流程：**
1. Extract 参数（如 Order ID）
2. Call 外部 API（Shopify, Logistics 3rd Party）
3. Return 结构化数据
4. LLM 仅负责将 JSON 润色为自然语言回复

**示例：**
```python
# Input: "Where is my order #12345?"
# Step 1: Extract Order ID via Regex
order_id = extract_order_id(message)  # "12345"

# Step 2: Call Shopify API
order_data = shopify_api.get_order(order_id)
# {status: "In Transit", loc: "HK", eta: "3 days"}

# Step 3: Return to Renderer
return {
    "type": "skill_result",
    "data": order_data,
    "template": "order_status"
}
```

#### 3.2 Knowledge Worker

**职责：** 负责信息检索

**检索策略：**

| 知识库层级 | 检索方式 |
|-----------|---------|
| Tier 1: Core | Always Injected (常驻注入) |
| Tier 2: Policies | Always Injected (常驻注入) |
| Tier 3: Golden | Few-Shot Injection |
| Tier 4: Niche | Dynamic（按需检索 metadata） |

**执行流程：**
1. 读取 `kb_core.md` 和 `kb_policies.md`（完整注入到 Context）
2. 根据 Intent Hints 动态加载 Tier 3/4 知识
3. 调用 Gemini 2.0 Flash 生成回复
4. 返回回复 + 引用来源

**输出：**
```json
{
  "type": "knowledge_result",
  "answer": "...",
  "sources": [
    {"file": "kb_core.md", "section": "G2 Specs"},
    {"file": "kb_policies.md", "section": "Return Policy"}
  ],
  "confidence": 0.92
}
```

#### 3.3 Escalation Worker

**职责：** 当意图不明或触发风控时，生成 Escalation Payload

**触发条件：**
- Router 无法分类
- 检测到 Jailbreak 尝试
- 用户情绪激动（检测到 "angry", "frustrated" 等关键词）
- 知识库无法回答（Gap Detection）

**执行流程：**
1. 分析无法处理的原因
2. 生成 Escalation Payload
3. 记录到 Gap Log Channel（Feishu）
4. 返回安抚话术

**输出：**
```json
{
  "type": "escalation",
  "reason": "knowledge_gap" | "jailbreak_attempt" | "emotional",
  "user_message": "...",
  "suggested_owner": "@Caris",
  "log_channel": "gap_log_channel_id"
}
```

---

### 4. Renderer (策略过滤器)

**职责：** "Separate internal truth from external safe truth"

**核心逻辑：**

```python
def render(worker_output, surface):
    # 读取知识片段的 Metadata
    metadata = worker_output.get("metadata", {})
    visibility = metadata.get("visibility", "internal")
    
    if surface == "external":
        # 仅输出合规信息
        if visibility == "internal":
            return "I don't have that information right now. Let me check with the team."
        else:
            return worker_output["answer"]
    
    elif surface == "internal":
        # 输出完整信息 + Debug 链路 + 负责人建议
        return {
            "answer": worker_output["answer"],
            "debug": {
                "sources": worker_output["sources"],
                "confidence": worker_output["confidence"],
                "suggested_owner": metadata.get("owner", "@Caris")
            }
        }
```

**Filter Logic:**
1. 读取知识片段的 Metadata (`visibility`, `approved_for_external`)
2. 如果 `surface == external` → 仅输出合规信息
3. 如果 `surface == internal` → 输出完整信息 + Debug 链路 + 负责人建议

**输出格式：**

**External (Discord):**
```
The G2 supports 15+ languages including English, Chinese, Spanish, etc.
```

**Internal (Feishu):**
```
The G2 supports 15+ languages including English, Chinese, Spanish, etc.

[Debug Info]
- Source: kb_core.md (G2 Specs)
- Confidence: 0.95
- Owner: @Caris
```

---

## 关键设计决策

### 1. 为什么采用流水线架构？

- **简单可维护：** 每个组件职责单一，易于调试
- **可扩展：** 新增 Worker 不影响其他组件
- **可测试：** 每个组件可独立测试

### 2. 为什么 Code-First？

- **确定性：** 高风险操作不依赖 LLM 的"自信度"
- **可控：** 规则清晰，易于审计
- **快速：** Regex 匹配比 LLM 推理快 10-100 倍

### 3. 为什么 Full Context Injection？

- **完整逻辑链：** 避免 RAG 切片导致的"断章取义"
- **零幻觉容忍：** 核心事实和规则必须完整注入
- **利用长窗口：** Gemini 2.0 Flash 支持 1M tokens，足够容纳所有核心知识

### 4. 为什么 One Brain, Two Voices？

- **统一逻辑：** 避免维护两套系统
- **动态渲染：** 根据 `surface` 字段动态调整输出
- **合规安全：** External 输出经过严格过滤

---

## 技术栈

- **Runtime:** OpenClaw (Local)
- **LLM:** Gemini 2.0 Flash (Reasoning)
- **VectorDB:** (Optional, for Tier 4 Niche Knowledge)
- **Language:** Python 3.11+
- **Testing:** PromptFoo / DSPy

---

## 下一步

1. 实现 Ingress Normalizer
2. 实现 Router (Regex + LLM Fallback)
3. 实现 Knowledge Worker
4. 实现 Renderer
5. 编写测试套件
