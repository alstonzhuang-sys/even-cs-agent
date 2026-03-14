# Changelog

All notable changes to Even CS Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-03-14

### Added
- **OpenClaw Integration**: Added `main.py` as the official entry point for OpenClaw
- **Configuration Validation**: Added startup checks to prevent deployment with placeholder values
- **Logging System**: Added centralized logging with `utils/logger.py`
- **Health Check**: Added `scripts/health_check.py` for monitoring
- **Dependency Locking**: Added `requirements.lock` for production deployments
- **Configuration Template**: Added `config/channels.json.example` to prevent accidental commits

### Changed
- **Version**: Bumped from v2.1 to v2.2
- **README**: Added prominent configuration warning at the top
- **Installation**: Updated to use `requirements.lock` for production
- **.gitignore**: Added `config/channels.json` and `logs/` to prevent sensitive data commits

### Fixed
- **Configuration Management**: Actual config file (`channels.json`) is now excluded from Git
- **Error Handling**: Improved error messages with actionable help text
- **Validation**: Added checks for placeholder values before startup

### Security
- **Sensitive Data Protection**: Configuration file with real IDs is no longer tracked in Git
- **Startup Validation**: System refuses to start with placeholder configuration

## [2.1.0] - 2026-03-13

### Added
- Initial release with core pipeline architecture
- Regex-first routing with LLM fallback
- Knowledge base with tiered injection strategy
- Dual-surface support (external/internal)
- Escalation worker with learning loop
- Comprehensive documentation

### Features
- Deterministic routing (90% Regex, 10% LLM)
- Full context injection (Tier 1-4)
- Hot-reload knowledge base
- Jailbreak detection
- Sensitive info filtering

---

## Migration Guide

### From v2.1 to v2.2

1. **Copy configuration template:**
   ```bash
   cp config/channels.json.example config/channels.json
   ```

2. **Update your configuration:**
   - Edit `config/channels.json`
   - Replace `ou_xxx` with actual Feishu ID

3. **Verify configuration:**
   ```bash
   python3 validate_config.py
   # Or
   python3 scripts/health_check.py
   ```

4. **Update dependencies (optional):**
   ```bash
   pip3 install -r requirements.lock
   ```

5. **Test the new entry point:**
   ```bash
   echo '{"channel":"discord","sender_id":"test","message":"What is the battery life?"}' | python3 main.py
   ```

---

## Versioning

- **Major version** (X.0.0): Breaking changes, major architecture changes
- **Minor version** (2.X.0): New features, backward compatible
- **Patch version** (2.2.X): Bug fixes, documentation updates
