# Changelog

## [3.1.1] - 2026-03-18

### Cleanup & Polish
- Unified all version numbers to v3.1.1
- Removed obsolete files (AUDIT_REPORT.md, INSTALLATION.md, init_github.sh, docs/, utils/)
- Replaced old test.sh with 7 modular test scripts
- Rewrote README with clear examples and architecture details
- Cleaned up .gitignore

### Bug Fixes
- Fixed `store_case()` signature mismatch — `main.py` passed `case_type`/`severity` but function didn't accept them
- Fixed unterminated f-string in `knowledge_worker.py` (sandbox prompt)
- Unified Gemini model to `gemini-2.0-flash` across all files (router, knowledge_worker, health_check were inconsistent)

### New Features
- Rate limiting: 5 msg/min per user + repeat detection (same message 3x → suggest human agent)
- Prompt injection sandbox: user input wrapped in `<user_input>` tags
- Prescription intent: regex patterns (EN + CN) for prescription/Rx/lens queries
- Structured JSON logger (`scripts/logger.py`) — logs to stderr, doesn't pollute stdout
- Non-interactive install: `FEISHU_ID=x GEMINI_API_KEY=y ./install.sh`
- Daily report script reads Rosen ID from config + includes cron setup instructions

### Improvements
- SKILL.md slimmed from ~300 to ~80 lines (low-end model friendly)
- `openclaw.plugin.json` now includes `skills` field for auto-discovery
- Rosen Feishu ID unified to read from `config/channels.json` (removed hardcoded `ou_xxx`)
- `order_status` / `return_request` now route to `knowledge_worker` instead of returning "coming soon"
- `max_output_tokens` aligned to 300 (per spec, was 500)
- Added `.env.example`

## [3.0.0] - 2026-03-15

### Major Release
- Fixed `build_context()` signature mismatch
- Fixed renderer import
- Updated Gemini model to `gemini-2.0-flash` (stable)
- Added `openclaw.plugin.json`
- Added `install.sh` automated setup
- Added comprehensive test suite
- Production-ready pipeline: Ingress → Router → Worker → Renderer

## [2.2.0] - 2026-03-14

### Initial Release
- Basic pipeline implementation
- Knowledge base structure (Core/Policies/Golden/Manual/Prescription)
- Router with Regex + LLM fallback
- 2-tier context injection
- Escalation handling with learning loop

