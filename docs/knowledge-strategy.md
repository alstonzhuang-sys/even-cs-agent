# 知识库策略

## 核心理念

**From Blurry RAG to Long Context**

传统 RAG 方法的问题：
- **断章取义：** 切片（Chunking）可能破坏完整逻辑链
- **召回不全：** 可能只召回了规则的前半句
- **幻觉风险：** LLM 可能"脑补"缺失的信息

**解决方案：Full Context Injection**

利用 Gemini 2.0 Flash 的长窗口能力（1M tokens），将核心知识库完整注入 Context，而非依赖碎片化的 VectorDB 检索。

---

## Three-Tier KB Structure

### Tier 1: Core (核心事实)

**文件：** `kb_core.md`

**内容类型：**
- 硬件参数（屏幕尺寸、重量、电池续航...）
- SKU 列表
- 价格信息
- 技术规格

**检索策略：** Always Injected (常驻注入)

**特点：**
- 关键词/精确匹配
- Temperature=0
- 零幻觉容忍

**示例：**

```markdown
---
visibility: external
keyTags: ["specs", "hardware", "G2"]
owner: "@Caris"
last_updated: "2026-03-13"
---

# G2 Specifications

## Display
- Type: Micro-OLED
- Resolution: 640x400 per eye
- Field of View: 16°

## Battery
- Capacity: 220mAh
- Runtime: 3-4 hours typical use
- Charging: USB-C, 1 hour to full

## Weight
- Glasses: 38g
- With clip: 42g

## Supported Languages
English, Chinese (Simplified/Traditional), Spanish, French, German, Italian, Portuguese, Japanese, Korean, Dutch, Polish, Russian, Turkish, Arabic, Hebrew
```

---

### Tier 2: Policies (规则)

**文件：** `kb_policies.md`

**内容类型：**
- 售后条款（退货、换货、保修）
- 物流规则（配送范围、时效、费用）
- Negative Constraints（禁止承诺的内容）

**检索策略：** Always Injected (常驻注入)

**特点：**
- 语义检索辅助
- 必须引用来源
- 完整逻辑链（例如："退货仅限14天内" **AND** "人为损坏除外"）

**示例：**

```markdown
---
visibility: external
keyTags: ["return", "refund", "warranty"]
owner: "@Rosen"
last_updated: "2026-03-13"
---

# Return & Refund Policy

## Return Window
- **14 days** from delivery date
- Product must be in original condition
- Original packaging required

## Exclusions
- Human damage (scratches, cracks, water damage)
- Missing accessories
- Software issues caused by user modification

## Refund Process
1. Contact support with order number
2. Receive return label
3. Ship product back
4. Refund processed within 5-7 business days after receipt

## Important Notes
- **We do NOT accept returns after 14 days**
- **We do NOT refund shipping costs**
- **We do NOT accept returns for opened software/digital products**
```

---

### Tier 3: Golden (金标准话术)

**文件：** `kb_golden.md`

**内容类型：**
- "金标准"回复范例
- 语气指南
- 安抚话术
- Few-Shot 示例

**检索策略：** Few-Shot Injection

**特点：**
- 用于规范输出风格 (Style)，而非事实源
- 提供语气参考
- 展示如何处理棘手情况

**示例：**

```markdown
---
visibility: internal
keyTags: ["tone", "style", "examples"]
owner: "@Rosen"
last_updated: "2026-03-13"
---

# Golden Q&A Pairs

## Example 1: Specs Query

**User:** "What's the battery life of G2?"

**DivaD:** "The G2 has a 220mAh battery that provides 3-4 hours of typical use. It charges fully in about 1 hour via USB-C."

---

## Example 2: Return Request (Within Window)

**User:** "I want to return my G2. I received it 5 days ago."

**DivaD:** "I can help you with that. Since you're within the 14-day return window, you're eligible for a return. Please confirm:
1. Is the product in original condition with all accessories?
2. Do you have the original packaging?

Once confirmed, I'll send you a return label."

---

## Example 3: Return Request (Outside Window)

**User:** "I want to return my G2. I received it 20 days ago."

**DivaD:** "I understand you'd like to return your G2. Unfortunately, our return policy allows returns only within 14 days of delivery. Since you received it 20 days ago, we're unable to process a return.

However, if you're experiencing any issues with the product, I'd be happy to help troubleshoot or explore warranty options. What specific concerns do you have?"

---

## Example 4: Angry User

**User:** "This is ridiculous! Your product is garbage!"

**DivaD:** "I'm sorry to hear you're frustrated. I want to help resolve this. Can you tell me what specific issue you're experiencing with your G2? I'll do my best to find a solution."

---

## Tone Guidelines

- **Be concise:** Get to the point quickly
- **Be empathetic:** Acknowledge user's feelings
- **Be professional:** No slang, no emojis (external)
- **Be helpful:** Offer solutions, not excuses
- **Be honest:** Don't promise what we can't deliver
```

---

### Tier 4: Niche (长尾知识)

**文件：** `kb_evenHubPilot.md`, `kb_troubleshooting.md`, etc.

**内容类型：**
- 小众排障知识
- 特定场景的详细指南
- 高级功能说明

**检索策略：** Dynamic（按需检索 metadata）

**特点：**
- 类似 Skill 的调用机制
- 仅在需要时加载
- 避免污染 Context

**示例：**

```markdown
---
visibility: internal
keyTags: ["evenHub", "pilot", "advanced"]
owner: "@David"
last_updated: "2026-03-13"
---

# EvenHub Pilot Program

## What is EvenHub?

EvenHub is our experimental app ecosystem for G2. It's currently in closed beta.

## How to Join

1. Must be a G2 owner
2. Must have iOS 16+ or Android 12+
3. Apply via: https://evenrealities.com/evenhub-pilot

## Known Issues

- Battery drain when using 3rd party apps
- Occasional sync issues with Android 12
- Limited app selection (10 apps as of Mar 2026)

## Troubleshooting

### Issue: "App not syncing"
1. Force close EvenHub app
2. Restart G2 glasses
3. Re-pair via Bluetooth
4. If issue persists, contact @David
```

---

## Metadata 格式

所有 `.md` 文件必须包含 Metadata Header：

```yaml
---
visibility: internal | external
keyTags: ["tag1", "tag2", "tag3"]
owner: "@username"
last_updated: "YYYY-MM-DD"
approved_for_external: true | false  # Optional, defaults to false
---
```

**字段说明：**

- `visibility`: 控制 Renderer 的输出策略
  - `internal`: 仅内部可见（Feishu）
  - `external`: 外部可见（Discord）

- `keyTags`: 用于动态检索（Tier 4）

- `owner`: 负责人，用于 Escalation

- `last_updated`: 最后更新时间，用于知识库维护

- `approved_for_external`: 是否经过审核可对外发布

---

## Knowledge Injection 策略

### Context 构建流程

```python
def build_context(user_message, surface):
    context = []
    
    # 1. Always Inject: Core + Policies
    context.append(read_file("kb_core.md"))
    context.append(read_file("kb_policies.md"))
    
    # 2. Few-Shot Injection: Golden
    context.append(read_file("kb_golden.md"))
    
    # 3. Dynamic Injection: Niche (if needed)
    intent_hints = extract_intent_hints(user_message)
    if "evenHub" in intent_hints:
        context.append(read_file("kb_evenHubPilot.md"))
    
    # 4. User Message
    context.append(f"<user_input>{user_message}</user_input>")
    
    return "\n\n".join(context)
```

### 为什么不切片（Chunking）？

**传统 RAG 的问题：**

假设有这样一条规则：
> "退货仅限14天内，且产品必须处于原始状态，人为损坏除外。"

如果切片为：
- Chunk 1: "退货仅限14天内"
- Chunk 2: "产品必须处于原始状态"
- Chunk 3: "人为损坏除外"

当用户问："我的 G2 屏幕碎了，能退货吗？"

RAG 可能只召回 Chunk 1 和 Chunk 2，导致 LLM 回答："可以，只要在14天内且产品处于原始状态。"

**但正确答案应该是："不可以，人为损坏不在退货范围内。"**

**Full Context Injection 的优势：**

LLM 能看到完整的逻辑链，避免"断章取义"。

---

## Gap Detection (知识缺口检测)

当 Knowledge Worker 无法回答时，触发 Gap Detection：

```python
def detect_gap(user_message, context):
    # 1. 尝试在 Context 中查找答案
    answer = llm.generate(context + user_message)
    
    # 2. 检查 LLM 的自信度
    if answer.confidence < 0.7:
        # 3. 记录到 Gap Log
        log_gap(user_message, answer, context)
        
        # 4. 返回安抚话术
        return "I don't have that information right now. Let me check with the team."
```

**Gap Log 格式：**

```json
{
  "timestamp": "2026-03-13T20:31:00Z",
  "user_message": "Does the G2 support the Klingon language?",
  "context_used": ["kb_core.md", "kb_policies.md"],
  "llm_response": "...",
  "confidence": 0.45,
  "suggested_owner": "@Caris"
}
```

---

## 知识库维护

### 更新流程

1. **识别缺口：** 从 Gap Log 中识别高频问题
2. **补充知识：** 由 Owner 补充到对应的 `.md` 文件
3. **审核：** 确保 Metadata 正确（尤其是 `visibility`）
4. **测试：** 运行 Test Suite 验证
5. **部署：** 更新到生产环境

### 质量控制

- **每周审查：** 检查 Gap Log，识别知识缺口
- **每月更新：** 更新过时信息（如价格、规格）
- **季度审计：** 全面审查知识库，删除冗余内容

---

## 下一步

1. 创建 `kb_core.md`（从 help.evenrealities.com 提取）
2. 创建 `kb_policies.md`（从内部文档提取）
3. 创建 `kb_golden.md`（从历史客服记录提取）
4. 设计 Gap Detection 机制
5. 实现 Knowledge Worker
