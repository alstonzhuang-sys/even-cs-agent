# Even CS Agent Skill

**Version**: v3.1.1
**Purpose**: Customer support for Even Realities (G1/G2/R1)

---

## When to Use

- User asks about Even Realities products (G1/G2/R1)
- User asks about orders, shipping, returns, refunds
- User asks for product specs, pricing, compatibility
- User needs troubleshooting help

## Prerequisites

1. `pip3 install -r requirements.txt`
2. `cp config/channels.json.example config/channels.json` and edit with real Feishu ID
3. `export GEMINI_API_KEY="your_key"`
4. Verify: `python3 scripts/health_check.py`

## How to Execute

**Step 1**: Build JSON payload from inbound context:

```json
{
  "channel": "discord",
  "sender_id": "user123",
  "message_id": "msg_001",
  "message": "What is the battery life?"
}
```

- `channel`: Use the inbound channel name (discord/feishu/telegram/slack)
- `sender_id`: From inbound metadata
- `message_id`: From inbound metadata
- `message`: The user's message text

**Step 2**: Execute main.py via stdin:

```bash
cd ~/.openclaw/workspace/even-cs-agent && echo '<payload_json>' | python3 main.py
```

**Step 3**: Parse JSON output:

```json
{
  "response": "The G2 has a 220mAh battery...",
  "intent": "specs_query",
  "confidence": 1.0,
  "surface": "external",
  "worker": "knowledge_worker"
}
```

**Step 4**: Send `response` field to the user.

## Error Handling

- If main.py exits non-zero or returns no output:
  - External surface → reply: "I'm having trouble right now. Let me get back to you."
  - Internal surface → reply with the error details
- If timeout (>30s) → reply: "I'm taking too long to respond. Let me get back to you."

## Prompt Files

- `prompts/SOUL.md` — DivaD's identity, personality, tone, and safety boundaries
- `prompts/AGENT.md` — Tool logic, rigid triggers, escalation rules

These files are automatically loaded by the pipeline (`knowledge_worker.py`) and injected into every Gemini request. No manual setup needed.

If running DivaD as a standalone OpenClaw agent (not via the main.py pipeline), copy these files into your OpenClaw workspace:

```bash
cp prompts/SOUL.md ~/.openclaw/workspace/SOUL.md
cp prompts/AGENT.md ~/.openclaw/workspace/AGENT.md
```

## Knowledge Base

Files in `knowledge/` are hot-reloaded on every request:

| File | Content | Injection |
|------|---------|-----------|
| `kb_core.md` | Product specs, pricing | Always |
| `kb_policies.md` | Return/shipping/warranty | Always |
| `kb_golden.md` | Golden Q&A examples | Intent-based |
| `kb_manual.md` | Troubleshooting guide | Intent-based |
| `kb_prescription.md` | Prescription lens info | Intent-based |

Add new `.md` files to `knowledge/` — they're available immediately.

## Architecture

```
User Message → Ingress (normalize) → Router (regex 90% / LLM 10%)
  → Knowledge Worker (KB + Gemini) | Escalation Worker (gap/jailbreak)
  → Renderer (external=safe / internal=debug) → JSON Output
```

## Testing

```bash
./test_all.sh
```

