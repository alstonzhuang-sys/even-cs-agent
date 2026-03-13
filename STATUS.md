# Even CS Agent - V2 架构总结

## 核心变化

### 从 Pipeline 到 Skill

**V1 架构（废弃）：**
- 独立的 Python 服务
- 复杂的状态管理
- 难以打包为 Skill

**V2 架构（当前）：**
- 单一 SKILL.md 文件驱动
- 无状态设计
- 100% 可复现
- 安装即用

---

## 关键设计决策

### 1. Hard-code First, LLM Last

**Router（Intent Detection）：**
- 90% Regex 匹配（确定性）
- 10% LLM 兜底（仅用于模糊查询）

**优势：**
- 快速（Regex 比 LLM 快 10-100 倍）
- 确定性（相同输入，相同输出）
- 低成本（减少 LLM 调用）

### 2. Full Context Injection

**不使用 VectorDB：**
- 避免切片（Chunking）导致的"断章取义"
- 避免召回不全
- 减少依赖（无需 Embedding）

**使用完整注入：**
- 将 `kb_core.md` + `kb_policies.md` 完整注入 Context
- Gemini 2 Flash 支持 1M tokens，足够容纳所有核心知识
- 完整逻辑链，减少幻觉

### 3. One Brain, Two Voices

**统一逻辑：**
- 一个 SKILL.md 处理所有渠道
- 根据 `surface` (external/internal) 动态渲染输出

**External (Discord)：**
- 仅输出合规信息
- 过滤内部关键词
- 专业、简洁

**Internal (Feishu)：**
- 输出完整信息
- 包含 Debug 信息（Intent, Confidence, Sources, Owner）
- 透明、详细

---

## 项目结构

```
even-cs-agent/
├── SKILL.md                  # 主 Skill 文件（Router + Workers + Renderer）
├── ARCHITECTURE_V2.md        # V2 架构设计文档
├── DEPLOYMENT.md             # 部署指南
├── knowledge/                # 知识库
│   ├── kb_core.md           # Tier 1: 核心事实（G1/G2 规格、价格）
│   ├── kb_policies.md       # Tier 2: 规则（退货、退款、保修、物流）
│   └── kb_golden.md         # Tier 3: 金标准话术（20 个示例）
├── prompts/                  # 提示词
│   ├── SOUL.md              # 运行时人格（Prime Directive, 语气指南）
│   └── AGENT.md             # 工具逻辑（触发器、升级逻辑）
└── scripts/                  # 脚本
    └── router.py            # Router 逻辑（Regex 匹配）
```

---

## 已完成的工作

### ✅ 核心文档
- [x] `SKILL.md` - 主 Skill 文件（完整的执行流程）
- [x] `ARCHITECTURE_V2.md` - V2 架构设计
- [x] `DEPLOYMENT.md` - 部署指南

### ✅ 知识库
- [x] `kb_core.md` - G1/G2 规格、价格、SKU、常见问题
- [x] `kb_policies.md` - 退货、退款、保修、物流政策
- [x] `kb_golden.md` - 20 个金标准示例对话

### ✅ 提示词
- [x] `SOUL.md` - DivaD 的人格定义（Prime Directive, 语气指南）
- [x] `AGENT.md` - 工具逻辑（5 个刚性触发器）

### ✅ 脚本
- [x] `router.py` - Router 逻辑（Regex 匹配）
- [x] 测试通过（order_status, specs_query, jailbreak）

---

## 待完成的工作

### 🔲 Phase 1: 核心功能（优先级：高）

1. **完善 SKILL.md**
   - [ ] 实现 `extract_section()` 函数
   - [ ] 实现 `contains_sensitive_info()` 函数
   - [ ] 实现 `get_owner()` 函数
   - [ ] 测试完整的执行流程

2. **补充知识库**
   - [ ] 从 help.evenrealities.com 提取更多内容
   - [ ] 补充 G1/G2 详细规格
   - [ ] 补充常见问题解答
   - [ ] 创建 `kb_evenHubPilot.md`（Tier 4 长尾知识）

3. **测试**
   - [ ] 创建 100 个 Basics 测试用例
   - [ ] 创建 59 个 Logic 测试用例
   - [ ] 创建 72 个 Adversarial 测试用例
   - [ ] 配置 PromptFoo
   - [ ] 运行第一次完整测试

### 🔲 Phase 2: 高级功能（优先级：中）

1. **Skill Worker（API 调用）**
   - [ ] 实现 `scripts/check_order.py`（Shopify API）
   - [ ] 实现 `scripts/check_return_eligibility.py`
   - [ ] 实现 `scripts/check_logistics.py`

2. **Gap Detection**
   - [ ] 实现 Gap Log 机制
   - [ ] 创建 Feishu Gap Log Channel
   - [ ] 自动升级到对应 Owner

3. **Renderer 优化**
   - [ ] 实现更智能的敏感信息过滤
   - [ ] 实现 Metadata 读取（从 kb_*.md）
   - [ ] 实现 Debug 信息格式化

### 🔲 Phase 3: 优化与监控（优先级：低）

1. **性能优化**
   - [ ] 缓存常见问题的答案
   - [ ] 减少 Context 长度（仅注入相关部分）
   - [ ] 并行处理（异步 API 调用）

2. **监控与日志**
   - [ ] 记录 Intent 分布
   - [ ] 监控 Hallucination Rate
   - [ ] 监控 Deflection Rate

3. **持续改进**
   - [ ] Teacher-Student Loop（Gemini 3 Pro 优化 Prompt）
   - [ ] A/B 测试（不同 Prompt 版本）
   - [ ] 用户反馈收集

---

## 技术栈

- **Runtime:** OpenClaw (Local)
- **LLM:** Gemini 2 Flash (Reasoning)
- **Language:** Python 3.11+
- **Testing:** PromptFoo / pytest
- **Deployment:** OpenClaw Skill

---

## North Star Metrics

- **Deflection Rate:** > 70% (tickets resolved without human reply)
- **Hallucination Rate:** < 5% (measured via random sampling)
- **Regex Coverage:** > 90% (intents matched by Regex)
- **Response Time:** < 3 seconds (average)

---

## 下一步行动

### 立即执行（本周）

1. **完善 SKILL.md**
   - 实现所有 Helper Functions
   - 测试完整的执行流程
   - 确保可以在 OpenClaw 中运行

2. **补充知识库**
   - 从 help.evenrealities.com 提取内容
   - 补充 G1/G2 详细规格
   - 补充常见问题解答

3. **创建测试用例**
   - 至少创建 50 个基础测试用例
   - 测试 Regex 覆盖率
   - 测试 LLM 准确性

### 短期目标（本月）

1. **Phase 1 完成**
   - 核心功能全部实现
   - 测试通过率 > 90%
   - 可以处理基础的客服查询

2. **灰度上线**
   - 部署到测试环境
   - 邀请内部用户测试
   - 收集反馈

### 中期目标（下月）

1. **Phase 2 完成**
   - API 调用功能实现
   - Gap Detection 机制上线
   - Renderer 优化完成

2. **正式上线**
   - 部署到生产环境（Discord + Feishu）
   - 监控 Deflection Rate 和 Hallucination Rate
   - 持续优化

---

## 关键优势

### 1. 插件化
- ✅ 任何人安装后都能 100% follow
- ✅ 不需要修改 OpenClaw 核心代码
- ✅ 易于分发和更新

### 2. 低 LLM 依赖
- ✅ Router: 90% Regex（确定性）
- ✅ Knowledge Worker: Full Context Injection（减少幻觉）
- ✅ Renderer: 100% Hard-coded（零 LLM）

### 3. 可测试
- ✅ 每个组件可独立测试
- ✅ 使用 PromptFoo 自动化测试
- ✅ 易于调试和优化

### 4. 可扩展
- ✅ 新增 Intent → 添加 Regex Pattern
- ✅ 新增知识 → 更新 kb_*.md
- ✅ 新增渠道 → 更新 channels.json

---

## 风险与挑战

### 1. 知识库维护
**风险：** 知识库过时，导致错误回复

**缓解措施：**
- 每月审查知识库
- 自动检测 Gap（知识缺口）
- 及时补充新知识

### 2. Regex 覆盖率
**风险：** Regex 无法覆盖所有场景

**缓解措施：**
- 持续优化 Pattern
- 分析失败的匹配
- 使用 LLM 兜底

### 3. LLM 幻觉
**风险：** LLM 生成错误信息

**缓解措施：**
- Temperature=0（减少随机性）
- Full Context Injection（完整逻辑链）
- 明确指令："Answer ONLY with information from the knowledge base"

### 4. 性能瓶颈
**风险：** Context 过长，响应慢

**缓解措施：**
- 仅注入相关部分（使用 `extract_section()`）
- 缓存常见问题
- 使用更快的模型（Gemini 2 Flash）

---

## 总结

**V2 架构的核心理念：**
- **Hard-code everything that can be hard-coded**
- **LLM only for ambiguous cases**
- **100% reproducible behavior**
- **Install and use, no configuration needed**

**当前状态：**
- 框架搭建完成 ✅
- 核心文档完成 ✅
- Router 实现并测试通过 ✅
- 知识库基础版本完成 ✅

**下一步：**
- 完善 SKILL.md（实现 Helper Functions）
- 补充知识库（从实际文档提取）
- 创建测试用例（PromptFoo）

---

**项目状态:** 框架完成，进入实现阶段  
**预计完成时间:** Phase 1（本周），Phase 2（本月）  
**负责人:** David (技术), Rosen (知识库), Caris (产品)
