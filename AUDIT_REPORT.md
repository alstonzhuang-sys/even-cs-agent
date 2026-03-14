# Even CS Agent - 架构审核报告

**审核日期**: 2026-03-14  
**审核人**: AtonBot  
**项目版本**: v2.2  
**审核标准**: OpenClaw Skill 最佳实践 + Harness Engineering

---

## 📊 总体评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **可复现性** | ⭐⭐⭐⭐☆ (4/5) | 配置清晰，但需要手动设置 |
| **流程顺畅** | ⭐⭐⭐⭐⭐ (5/5) | 无卡点，逻辑清晰 |
| **Harness Engineering** | ⭐⭐⭐⭐⭐ (5/5) | 90% 硬编码，10% LLM |
| **可扩展性** | ⭐⭐⭐⭐☆ (4/5) | 结构清晰，但缺少插件机制 |

**总分**: 18/20 (90%)

---

## ✅ 优点

### 1. 架构设计优秀

**Pipeline 清晰**:
```
Ingress → Router → Worker → Renderer → Output
```

- ✅ 单一职责原则（每个组件只做一件事）
- ✅ 可测试性强（每个组件都有独立测试脚本）
- ✅ 易于调试（每个环节都有日志）

**代码示例**:
```python
# main.py - 清晰的流程编排
payload = normalize_payload(...)  # Step 1
routing = route(message)          # Step 2
response = execute_worker(...)    # Step 3
final = render_response(...)      # Step 4
```

### 2. Harness Engineering 做得很好

**90% 硬编码，10% LLM**:

```python
# router.py - Regex 优先
PATTERNS = {
    "jailbreak": [r"ignore.*instruction", ...],
    "order_status": [r"order\s*#?\d{4,}", ...],
    "specs_query": [r"battery.*life", ...]
}

# 只有 Regex 失败才用 LLM
result = route_regex(message)
if not result:
    result = route_llm(message)  # Gemini 2 Flash
```

**优点**:
- ✅ 高风险操作（订单、退款）100% 确定性
- ✅ 速度快（Regex < 1ms，LLM ~500ms）
- ✅ 成本低（90% 请求不需要 LLM）

### 3. 学习循环系统完善

**Escalation Worker**:
```python
# 今天的 gap → 明天的 knowledge
store_case(message, intent, surface)  # 存储
generate_daily_report()               # 日报
inject_answer(case_id, answer)        # 注入
```

**优点**:
- ✅ 自动检测知识缺口
- ✅ 每日汇总发送给 Rosen
- ✅ 回复后自动注入到 KB
- ✅ Hot-reload（无需重启）

### 4. 双表面设计合理

**One Brain, Two Voices**:
```python
if surface == "external":
    response = filter_sensitive_info(response)
elif surface == "internal":
    response = add_debug_info(response, intent, confidence)
```

**优点**:
- ✅ 单一逻辑核心（避免重复代码）
- ✅ External 过滤敏感信息（合规）
- ✅ Internal 显示调试信息（透明）

### 5. 测试覆盖完整

**每个组件都有测试脚本**:
```bash
test_ingress.sh          # 入口标准化
test_router.sh           # 意图分类
test_knowledge_worker.sh # 知识查询
test_renderer.sh         # 输出过滤
test_escalation_worker.sh # 升级处理
test_main.sh             # 端到端
```

---

## ⚠️ 问题与改进建议

### 🔴 严重问题

#### 1. SKILL.md 不符合 OpenClaw 规范

**问题**: 当前 SKILL.md 是一个 **教程文档**，而不是 **执行指令**。

**当前内容**:
```markdown
## Execution Flow

### Step 1: Detect Surface
First, determine if this is an external (Discord) or internal (Feishu) message:

```python
channel = context.get("channel", "unknown")
if channel == "discord":
    surface = "external"
```
```

**OpenClaw 期望的内容**:
```markdown
## Execution Instructions

When a message is received:

1. **Read inbound metadata** from OpenClaw context
2. **Execute main.py** with JSON payload:
   ```bash
   echo '{"channel":"discord","sender_id":"123","message":"text"}' | python3 main.py
   ```
3. **Parse output** and return response to user
4. **Handle errors** gracefully (fallback to escalation)

## Error Handling

If main.py fails:
- Log error to escalation_cases/
- Return: "I'm having trouble right now. Let me get back to you."
- Notify Rosen via Feishu
```

**影响**: 
- ❌ OpenClaw 无法自动执行（需要人工解读）
- ❌ 新安装无法 100% follow（不知道如何调用）

**修复建议**:
```markdown
# SKILL.md 应该包含:
1. 明确的执行命令（exec tool 调用）
2. 输入/输出格式（JSON schema）
3. 错误处理流程（fallback 策略）
4. 依赖检查（API key, config files）
```

---

#### 2. 配置文件需要手动编辑

**问题**: `config/channels.json` 中的 `ou_xxx` 是占位符，需要手动替换。

**当前流程**:
```bash
# 用户需要手动做这些:
1. cp config/channels.json.example config/channels.json
2. vim config/channels.json  # 手动替换 ou_xxx
3. export GEMINI_API_KEY="..."
4. python3 validate_config.py
```

**影响**:
- ❌ 无法做到 "下载即用"
- ❌ 容易出错（忘记替换占位符）

**修复建议**:

**方案 A: 交互式配置脚本**
```bash
#!/bin/bash
# setup.sh - 交互式配置

echo "=== Even CS Agent Setup ==="
echo

# 1. 检测 OpenClaw 配置
if [ -f ~/.openclaw/openclaw.json ]; then
    echo "✅ OpenClaw detected"
    FEISHU_ID=$(jq -r '.channels.feishu.userId' ~/.openclaw/openclaw.json)
    echo "Found Feishu ID: $FEISHU_ID"
else
    echo "❌ OpenClaw not found"
    read -p "Enter Rosen's Feishu ID (ou_xxx): " FEISHU_ID
fi

# 2. 生成配置文件
cat > config/channels.json <<EOF
{
  "external": ["discord"],
  "internal": ["feishu"],
  "fallback": "external",
  "rosen_contact": {
    "feishu_id": "$FEISHU_ID",
    "name": "Rosen"
  }
}
EOF

echo "✅ Configuration saved to config/channels.json"

# 3. 检查 API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set"
    read -p "Enter Gemini API key: " API_KEY
    echo "export GEMINI_API_KEY='$API_KEY'" >> ~/.zshrc
    export GEMINI_API_KEY="$API_KEY"
fi

echo "✅ Setup complete!"
```

**方案 B: 从 OpenClaw 配置读取**
```python
# scripts/auto_config.py
import json
import os
from pathlib import Path

def load_openclaw_config():
    """从 OpenClaw 配置中读取 Feishu ID"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    if not config_path.exists():
        return None
    
    with open(config_path) as f:
        config = json.load(f)
    
    return config.get("channels", {}).get("feishu", {}).get("userId")

def generate_config():
    """自动生成配置文件"""
    feishu_id = load_openclaw_config()
    
    if not feishu_id:
        print("❌ Cannot auto-detect Feishu ID")
        feishu_id = input("Enter Rosen's Feishu ID: ")
    
    config = {
        "external": ["discord"],
        "internal": ["feishu"],
        "fallback": "external",
        "rosen_contact": {
            "feishu_id": feishu_id,
            "name": "Rosen"
        }
    }
    
    with open("config/channels.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved (Feishu ID: {feishu_id})")

if __name__ == "__main__":
    generate_config()
```

---

### 🟡 中等问题

#### 3. 缺少依赖管理

**问题**: 没有 `requirements.txt` 或 `pyproject.toml`。

**影响**:
- ❌ 用户不知道需要安装哪些库
- ❌ 版本不一致可能导致错误

**修复建议**:
```txt
# requirements.txt
google-generativeai>=0.3.0
```

```bash
# 在 SKILL.md 中添加:
## Prerequisites

Install dependencies:
```bash
pip install -r requirements.txt
```
```

---

#### 4. 错误处理不够健壮

**问题**: `main.py` 中的错误处理过于简单。

**当前代码**:
```python
try:
    response = generate_response(...)
except Exception as e:
    return f"Error: {str(e)[:50]}"  # ❌ 暴露内部错误
```

**问题**:
- ❌ 错误信息可能泄露敏感信息
- ❌ 没有区分 external/internal 错误消息

**修复建议**:
```python
try:
    response = generate_response(...)
except Exception as e:
    # Log error
    logger.error(f"Worker failed: {e}", exc_info=True)
    
    # Store escalation case
    case_id = store_case(
        message=message,
        intent=intent,
        surface=surface,
        case_type="error",
        error=str(e)
    )
    
    # Return safe message
    if surface == "external":
        return "I'm having trouble right now. Let me get back to you."
    else:
        return f"Error: {str(e)} (Case: {case_id})"
```

---

#### 5. 知识库更新机制不够自动化

**问题**: Escalation Worker 需要 Rosen 手动回复才能注入答案。

**当前流程**:
```
1. User asks unknown question
2. Bot stores case → escalation_cases/2026-03-14.jsonl
3. Bot generates daily report → sends to Rosen
4. Rosen reads report → manually replies
5. Bot injects answer → knowledge/kb_manual.md
```

**问题**:
- ❌ 依赖人工（Rosen 可能忙/忘记）
- ❌ 延迟高（可能几天后才回复）

**改进建议**:

**方案 A: 自动搜索现有文档**
```python
def auto_resolve_gap(message: str, intent: str) -> str:
    """尝试从现有文档中找答案"""
    
    # 1. 搜索 Feishu 文档库
    docs = search_feishu_docs(message)
    
    # 2. 如果找到相关文档，提取答案
    if docs:
        answer = extract_answer(docs[0], message)
        return answer
    
    # 3. 如果没找到，才 escalate
    return None
```

**方案 B: 定时提醒 + 自动催促**
```python
def check_pending_cases():
    """检查超过 24 小时未回复的 cases"""
    
    cases = load_pending_cases()
    
    for case in cases:
        if case["age_hours"] > 24:
            # 发送提醒给 Rosen
            send_feishu_message(
                rosen_id,
                f"⚠️ Case {case['id']} 已超过 24 小时未回复"
            )
```

---

### 🟢 小问题

#### 6. 文档过多，信息冗余

**问题**: 项目根目录有 **20+ 个 .md 文件**，信息重复。

**当前文件**:
```
ARCHITECTURE_V2.md
COMPLETION_SUMMARY.md
IMPLEMENTATION_COMPLETE.md
IMPLEMENTATION_GUIDE.md
IMPLEMENTATION_STATUS.md
PROJECT_SUMMARY.md
STATUS.md
...
```

**问题**:
- ❌ 用户不知道该看哪个
- ❌ 维护成本高（更新需要改多个文件）

**修复建议**:

**保留核心文档**:
```
README.md              # 项目介绍 + 快速开始
SKILL.md               # OpenClaw 执行指令
ARCHITECTURE.md        # 架构设计
CHANGELOG.md           # 版本历史
```

**归档其他文档**:
```bash
mkdir -p docs/archive
mv COMPLETION_SUMMARY.md docs/archive/
mv IMPLEMENTATION_STATUS.md docs/archive/
mv PROJECT_SUMMARY.md docs/archive/
```

---

#### 7. 测试脚本缺少自动化

**问题**: 测试脚本需要手动运行，没有 CI/CD。

**当前流程**:
```bash
# 用户需要手动运行每个测试
./test_ingress.sh
./test_router.sh
./test_knowledge_worker.sh
...
```

**修复建议**:

**创建统一测试脚本**:
```bash
#!/bin/bash
# test_all.sh - 运行所有测试

echo "=== Running All Tests ==="

FAILED=0

# Run each test
for test in test_*.sh; do
    echo "Running $test..."
    if ! ./$test > /dev/null 2>&1; then
        echo "❌ $test failed"
        FAILED=$((FAILED + 1))
    else
        echo "✅ $test passed"
    fi
done

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ $FAILED tests failed"
    exit 1
fi
```

**添加 GitHub Actions**:
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: ./test_all.sh
```

---

## 🎯 优先级改进清单

### 🔴 高优先级（必须修复）

1. **重写 SKILL.md** - 改为执行指令格式
   - 预计时间: 2 小时
   - 影响: 100% follow rate

2. **添加自动配置脚本** - `setup.sh` 或 `auto_config.py`
   - 预计时间: 1 小时
   - 影响: 用户体验

3. **添加 requirements.txt** - 明确依赖
   - 预计时间: 10 分钟
   - 影响: 可复现性

### 🟡 中优先级（建议修复）

4. **改进错误处理** - 区分 external/internal 错误消息
   - 预计时间: 1 小时
   - 影响: 安全性

5. **优化知识库更新** - 自动搜索 + 定时提醒
   - 预计时间: 3 小时
   - 影响: 学习效率

### 🟢 低优先级（可选）

6. **清理文档** - 归档冗余文件
   - 预计时间: 30 分钟
   - 影响: 可维护性

7. **添加 CI/CD** - GitHub Actions
   - 预计时间: 1 小时
   - 影响: 代码质量

---

## 📝 具体修复方案

### 修复 1: 重写 SKILL.md

**新的 SKILL.md 结构**:

```markdown
# Even CS Agent Skill

**Version**: v2.2  
**Purpose**: Intelligent customer support for Even Realities

---

## When to Use

Use this skill when:
- User asks about Even Realities products (G1/G2/R1)
- User asks about orders, shipping, returns
- Message is from Discord (external) or Feishu (internal)

---

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

Run setup script:
```bash
python3 scripts/auto_config.py
```

Or manually edit `config/channels.json`:
```json
{
  "rosen_contact": {
    "feishu_id": "ou_ceae7c2ca21c67c92ae07f04d6347a81"
  }
}
```

### 3. Set API Key

```bash
export GEMINI_API_KEY="your_key_here"
```

### 4. Verify

```bash
python3 scripts/health_check.py
```

---

## Execution Instructions

### Step 1: Read Inbound Context

Extract metadata from OpenClaw:

```python
channel = context.get("channel", "unknown")
sender_id = context.get("sender_id", "unknown")
message_id = context.get("message_id", "unknown")
message = context.get("message", "")
```

### Step 2: Execute main.py

Call main.py with JSON payload:

```bash
echo '{
  "channel": "discord",
  "sender_id": "123",
  "message_id": "456",
  "message": "What is the battery life?"
}' | python3 main.py
```

### Step 3: Parse Output

main.py returns JSON:

```json
{
  "response": "The G2 has a 220mAh battery...",
  "intent": "specs_query",
  "confidence": 1.0,
  "surface": "external",
  "worker": "knowledge_worker"
}
```

### Step 4: Return Response

Send `response` field to user via OpenClaw message tool.

---

## Error Handling

### If main.py Fails

1. **Log error** to `escalation_cases/errors.jsonl`
2. **Return fallback message**:
   - External: "I'm having trouble right now. Let me get back to you."
   - Internal: "Error: {error_message} (logged)"
3. **Notify Rosen** via Feishu (if internal)

### If Configuration Missing

1. **Check** `config/channels.json` exists
2. **Check** `GEMINI_API_KEY` is set
3. **Return**: "Configuration error. Please run setup.sh"

---

## Testing

Run all tests:

```bash
./test_all.sh
```

Or test individual components:

```bash
./test_router.sh
./test_knowledge_worker.sh
./test_main.sh
```

---

## Maintenance

### Update Knowledge Base

1. Edit files in `knowledge/`:
   - `kb_core.md` - Product specs
   - `kb_policies.md` - Policies
   - `kb_golden.md` - Q&A examples

2. Changes take effect immediately (hot-reload)

### Add New Intent

1. Edit `scripts/router.py`:
   ```python
   PATTERNS = {
       "new_intent": [r"pattern1", r"pattern2"]
   }
   ```

2. Add worker logic in `main.py`

3. Add test case in `test_router.sh`

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not set"

**Solution**:
```bash
export GEMINI_API_KEY="your_key_here"
# Or add to ~/.zshrc for persistence
```

### Issue: "Configuration error"

**Solution**:
```bash
python3 scripts/auto_config.py
# Or manually edit config/channels.json
```

### Issue: LLM hallucinating

**Solution**:
- Check knowledge base is complete
- Temperature is already 0 (deterministic)
- Add more examples to `kb_golden.md`

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

**Pipeline**:
```
Ingress → Router → Worker → Renderer → Output
```

**Workers**:
- `knowledge_worker` - Answer from KB
- `skill_worker` - API calls (Phase 2)
- `escalation_worker` - Unknown queries

---

## License

MIT License - See [LICENSE](LICENSE)
```

---

### 修复 2: 添加自动配置脚本

**创建 `scripts/auto_config.py`**:

```python
#!/usr/bin/env python3
"""
Auto Configuration Script

Automatically generates config/channels.json by:
1. Reading Feishu ID from OpenClaw config
2. Prompting user if not found
3. Validating configuration
"""

import json
import os
from pathlib import Path


def load_openclaw_config():
    """Load OpenClaw configuration"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    
    if not config_path.exists():
        return None
    
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Failed to load OpenClaw config: {e}")
        return None


def get_feishu_id():
    """Get Feishu ID from OpenClaw or user input"""
    # Try to read from OpenClaw config
    openclaw_config = load_openclaw_config()
    
    if openclaw_config:
        feishu_id = openclaw_config.get("channels", {}).get("feishu", {}).get("userId")
        if feishu_id:
            print(f"✅ Found Feishu ID in OpenClaw config: {feishu_id}")
            return feishu_id
    
    # Prompt user
    print("❌ Feishu ID not found in OpenClaw config")
    feishu_id = input("Enter Rosen's Feishu ID (ou_xxx): ").strip()
    
    if not feishu_id.startswith("ou_"):
        print("⚠️  Warning: Feishu ID should start with 'ou_'")
    
    return feishu_id


def generate_config(feishu_id: str):
    """Generate config/channels.json"""
    config = {
        "external": ["discord"],
        "internal": ["feishu"],
        "fallback": "external",
        "rosen_contact": {
            "feishu_id": feishu_id,
            "name": "Rosen"
        }
    }
    
    # Create config directory if not exists
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Write config
    config_path = config_dir / "channels.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_path}")


def check_api_key():
    """Check if GEMINI_API_KEY is set"""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set")
        print("Set with: export GEMINI_API_KEY='your_key_here'")
        return False
    
    print("✅ GEMINI_API_KEY is set")
    return True


def main():
    print("=== Even CS Agent - Auto Configuration ===")
    print()
    
    # Step 1: Get Feishu ID
    feishu_id = get_feishu_id()
    
    # Step 2: Generate config
    generate_config(feishu_id)
    
    # Step 3: Check API key
    check_api_key()
    
    print()
    print("=== Configuration Complete ===")
    print()
    print("Next steps:")
    print("1. Run health check: python3 scripts/health_check.py")
    print("2. Run tests: ./test_all.sh")
    print("3. Start using: echo '{...}' | python3 main.py")


if __name__ == "__main__":
    main()
```

---

### 修复 3: 添加 requirements.txt

```txt
# requirements.txt
google-generativeai>=0.3.0
```

---

## 🎓 总结

### 当前状态

**优点**:
- ✅ 架构设计优秀（Pipeline 清晰）
- ✅ Harness Engineering 做得好（90% 硬编码）
- ✅ 学习循环完善（Escalation → KB）
- ✅ 测试覆盖完整（每个组件都有测试）

**问题**:
- ❌ SKILL.md 不符合 OpenClaw 规范（教程 vs 执行指令）
- ❌ 配置需要手动编辑（无法 100% follow）
- ❌ 缺少依赖管理（requirements.txt）

### 改进后的状态

**修复后**:
- ✅ SKILL.md 改为执行指令格式
- ✅ 自动配置脚本（setup.sh / auto_config.py）
- ✅ 添加 requirements.txt
- ✅ 改进错误处理
- ✅ 优化知识库更新

**预期效果**:
- ✅ 100% follow rate（新安装可直接使用）
- ✅ 流程顺畅（无卡点）
- ✅ 符合 Harness Engineering（90% 硬编码）
- ✅ 易于扩展（清晰的结构）

---

## 📋 行动计划

### Phase 1: 核心修复（必须完成）

1. **重写 SKILL.md** (2 小时)
   - 改为执行指令格式
   - 添加明确的 exec 命令
   - 添加错误处理流程

2. **添加自动配置** (1 小时)
   - 创建 `scripts/auto_config.py`
   - 从 OpenClaw 读取 Feishu ID
   - 自动生成 `config/channels.json`

3. **添加依赖管理** (10 分钟)
   - 创建 `requirements.txt`
   - 在 README 中添加安装说明

### Phase 2: 改进优化（建议完成）

4. **改进错误处理** (1 小时)
   - 区分 external/internal 错误消息
   - 添加错误日志
   - 自动 escalate 错误

5. **优化知识库更新** (3 小时)
   - 自动搜索 Feishu 文档
   - 定时提醒未回复的 cases
   - 批量注入答案

### Phase 3: 长期维护（可选）

6. **清理文档** (30 分钟)
   - 归档冗余文件
   - 保留核心文档

7. **添加 CI/CD** (1 小时)
   - GitHub Actions
   - 自动测试

---

**总结**: 项目整体质量很高（90%），只需要修复 SKILL.md 和配置流程，就可以达到 100% follow rate。

