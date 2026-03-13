# Even CS Agent (DivaD v2.1) - 项目框架总结

## 项目概览

已完成 Even CS Agent (DivaD v2.1) 的完整项目框架搭建。这是一个基于 OpenClaw 的智能客服机器人，旨在将 DivaD 从简单的 FAQ 问答机器人升级为 Tier-1 智能支持专员。

## 核心设计理念

### 1. From Probability to Determinism
- 高风险操作（订单、退款、DFU）依赖代码触发的硬规则，而非 LLM 的"自信度"
- 使用 Regex 优先匹配，LLM 仅作为兜底分类器

### 2. From Blurry RAG to Long Context
- 利用 Gemini 2.0 Flash 的长窗口能力（1M tokens）
- 将核心知识库（Core + Policies）完整注入 Context
- 避免 RAG 切片导致的"断章取义"

### 3. One Brain, Two Voices
- 一个核心逻辑中枢
- 根据入口（Discord/Feishu）动态渲染 External（合规）或 Internal（透明）的回复

## 架构设计

```
Ingress Normalizer -> Router -> Worker(s) -> Renderer OR Escalator
```

### 组件说明

1. **Ingress Normalizer (入口标准化)**
   - 统一转化为标准 JSON Payload
   - 执行 Session Reset（每条新 Ticket 视为全新 Session）

2. **Router (决策中枢)**
   - Code-First Strategy: 优先使用 Regex 匹配高危关键词
   - LLM 仅作为兜底分类器

3. **Workers (执行单元)**
   - **Skill Worker (Phase 2):** 执行确定性代码（暂不实现）
   - **Knowledge Worker:** 负责信息检索
   - **Escalation Worker:** 意图不明或触发风控时，生成 Escalation Payload

4. **Renderer (策略过滤器)**
   - 根据 `surface` (external/internal) 输出不同内容
   - External: 仅输出合规信息
   - Internal: 输出完整信息 + Debug 链路 + 负责人建议

## 知识库架构

### Three-Tier KB Structure

| 层级 | 文件 | 内容类型 | 检索策略 |
|------|------|---------|---------|
| **Tier 1: Core** | `kb_core.md` | 硬件参数、SKU、价格 | Always Injected |
| **Tier 2: Policies** | `kb_policies.md` | 售后条款、物流规则 | Always Injected |
| **Tier 3: Golden** | `kb_golden.md` | 金标准回复范例、语气指南 | Few-Shot Injection |
| **Tier 4: Niche** | `kb_evenHubPilot.md` | 小众排障知识 | Dynamic（按需检索） |

### Metadata 格式

所有 `.md` 文件必须包含 Metadata Header：

```yaml
---
visibility: internal | external
keyTags: ["tag1", "tag2"]
owner: "@username"
last_updated: "YYYY-MM-DD"
---
```

## 测试策略

### The "Gauntlet" Approach

Before any deployment, DivaD must pass the **"Gauntlet"** (Automated Eval using `promptfoo`).

- **Suite 1: The Basics (n=100)** - Specs, Pricing, Shipping
- **Suite 2: Logic & Policy (n=59)** - Return/Refund logic
- **Suite 3: Adversarial (n=72)** - Jailbreaks, Competitor comparisons

### 测试工具

- **PromptFoo:** 自动化测试框架
- **Teacher-Student Loop:** Gemini 3 Pro 优化 Prompt，Gemini 2.0 Flash 执行

## 安全与风控

### 防注入 (Anti-Prompt Injection)

- **沙箱机制:** 将用户输入包裹在 XML 标签中
- **Prime Directive:** 核心指令不可变
- **拒答脚本:** 统一回复 Jailbreak 尝试

### 防噪策略 (Spam & Rate Limiting)

- **冷却 (Cooldown):** 用户级限流（5条/分钟）
- **复读检测:** 相同消息 3 次触发终止回复
- **成本控制:** 限制单次回复 Max Token (300 tokens)

## 项目结构

```
even-cs-agent/
├── README.md                 # 项目总览
├── docs/                     # 文档目录
│   ├── architecture.md       # 架构设计详细说明
│   ├── knowledge-strategy.md # 知识库策略
│   └── testing-guide.md      # 测试指南
├── knowledge/                # 知识库目录
│   ├── kb_core.md           # Tier 1: 核心事实
│   ├── kb_policies.md       # Tier 2: 规则
│   ├── kb_golden.md         # Tier 3: 金标准话术
│   └── kb_evenHubPilot.md   # Tier 4: 长尾知识（待创建）
├── prompts/                  # 提示词目录
│   ├── SOUL.md              # 运行时人格
│   ├── AGENT.md             # 工具逻辑
│   └── system-prompt.md     # 系统提示词（待创建）
├── src/                      # 源代码目录
│   ├── ingress/             # 入口标准化（待实现）
│   ├── router/              # 路由逻辑（待实现）
│   ├── workers/             # Worker 实现（待实现）
│   └── renderer/            # 渲染器（待实现）
├── tests/                    # 测试目录
│   ├── suite1_basics/       # 基础测试套件（待创建）
│   ├── suite2_logic/        # 逻辑测试套件（待创建）
│   └── suite3_adversarial/  # 对抗测试套件（待创建）
└── config/                   # 配置目录
    ├── openclaw.json        # OpenClaw 配置（待创建）
    └── channels.json        # 渠道配置（待创建）
```

## 已完成的工作

### 文档
- ✅ `README.md` - 项目总览
- ✅ `docs/architecture.md` - 架构设计详细说明
- ✅ `docs/knowledge-strategy.md` - 知识库策略
- ✅ `docs/testing-guide.md` - 测试指南

### 提示词
- ✅ `prompts/SOUL.md` - 运行时人格定义
- ✅ `prompts/AGENT.md` - 工具逻辑定义

### 知识库
- ✅ `knowledge/kb_core.md` - 核心事实（G1/G2 规格、价格、SKU）
- ✅ `knowledge/kb_policies.md` - 规则（退货、退款、保修、物流）
- ✅ `knowledge/kb_golden.md` - 金标准话术（20 个示例）

## 下一步工作

### 第二阶段：工程与配置（继续）

1. **任务 6: 实现 Ingress Normalizer 逻辑**
   - 创建 `src/ingress/normalizer.py`
   - 实现 Discord 和 Feishu 消息标准化
   - 实现 Session Reset 逻辑

2. **创建系统提示词**
   - 创建 `prompts/system-prompt.md`
   - 整合 SOUL.md + AGENT.md + kb_core.md + kb_policies.md

3. **实现 Router**
   - 创建 `src/router/router.py`
   - 实现 Regex 匹配逻辑
   - 实现 LLM 兜底分类器

4. **实现 Knowledge Worker**
   - 创建 `src/workers/knowledge_worker.py`
   - 实现 Full Context Injection
   - 实现 Gap Detection

5. **实现 Renderer**
   - 创建 `src/renderer/renderer.py`
   - 实现 Policy Filter
   - 实现 External/Internal 输出格式化

### 第三阶段：测试与调优

1. **任务 7: 创建测试用例**
   - 创建 100 个 Basics 测试用例
   - 创建 59 个 Logic 测试用例
   - 创建 72 个 Adversarial 测试用例

2. **任务 8: 配置 PromptFoo**
   - 创建 `promptfooconfig.yaml`
   - 运行第一次完整测试

3. **任务 9: 迭代优化**
   - 分析失败案例
   - 修正 Prompt 或知识库
   - 重新测试

4. **任务 10: 灰度上线**
   - 部署到测试环境
   - 监控 Hallucination Rate
   - 收集用户反馈

## 关键设计决策

1. **为什么采用流水线架构？**
   - 简单可维护：每个组件职责单一
   - 可扩展：新增 Worker 不影响其他组件
   - 可测试：每个组件可独立测试

2. **为什么 Code-First？**
   - 确定性：高风险操作不依赖 LLM 的"自信度"
   - 可控：规则清晰，易于审计
   - 快速：Regex 匹配比 LLM 推理快 10-100 倍

3. **为什么 Full Context Injection？**
   - 完整逻辑链：避免 RAG 切片导致的"断章取义"
   - 零幻觉容忍：核心事实和规则必须完整注入
   - 利用长窗口：Gemini 2.0 Flash 支持 1M tokens

4. **为什么 One Brain, Two Voices？**
   - 统一逻辑：避免维护两套系统
   - 动态渲染：根据 `surface` 字段动态调整输出
   - 合规安全：External 输出经过严格过滤

## North Star Metrics

- **Deflection Rate:** %/# of tickets resolved without human reply (Target: > 70%)
- **Hallucination Rate:** Measured via random sampling of 50 interactions/week (Target: < 5%)

## 技术栈

- **Runtime:** OpenClaw (Local)
- **LLM:** Gemini 2.0 Flash (Reasoning)
- **VectorDB:** (Optional, for Tier 4 Niche Knowledge)
- **Language:** Python 3.11+
- **Testing:** PromptFoo / DSPy

---

**项目状态:** 框架搭建完成，进入实现阶段  
**下一步:** 实现 Ingress Normalizer 和 Router  
**预计完成时间:** 根据开发进度调整
