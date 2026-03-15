# Even CS Agent v3.0 - Changelog

## [3.0.0] - 2026-03-15

### 🎉 Major Release - Production Ready

#### ✅ Fixed Issues
1. **Function signature mismatch** (Critical)
   - Fixed `build_context()` call in `main.py` - now includes `confidence` parameter
   - Fixed renderer import - now uses `render_response()` function

2. **Gemini API model update**
   - Changed from `gemini-2.0-flash-exp` (404) to `gemini-2.0-flash` (working)
   - Model is now stable and production-ready

3. **Missing plugin configuration**
   - Added `openclaw.plugin.json` with complete metadata
   - OpenClaw can now recognize and load this as a plugin

4. **Indentation error in main.py**
   - Removed duplicate code block at end of file
   - File now parses correctly

#### 🚀 New Features
1. **Automated installation script** (`install.sh`)
   - Interactive setup wizard
   - Automatic dependency installation
   - Configuration file creation
   - API key setup
   - Health check verification

2. **Comprehensive test suite** (`test.sh`)
   - 8 test categories (Ingress, Router, Knowledge Worker, Renderer, etc.)
   - End-to-end integration tests
   - Colored output with pass/fail summary

3. **Plugin metadata** (`openclaw.plugin.json`)
   - Complete plugin definition
   - Dependency specifications
   - Setup instructions
   - Capability declarations

#### 📚 Documentation Updates
- Updated README.md with installation instructions
- Added troubleshooting section
- Clarified configuration requirements
- Added examples for all major use cases

#### 🔧 Technical Improvements
1. **Error handling**
   - Better fallback messages
   - Graceful degradation when components fail
   - Detailed error logging

2. **Code quality**
   - Fixed all syntax errors
   - Improved function signatures
   - Better type hints

3. **Configuration validation**
   - Pre-flight checks before execution
   - Clear error messages for missing config
   - Placeholder detection

#### 🧪 Testing
- All 8 test categories passing
- End-to-end tests verified
- Manual testing completed

#### 📦 Dependencies
- `google-generativeai>=0.3.0` (with deprecation warning - future migration needed)
- Python 3.8+ required

---

## [2.2.0] - 2026-03-14

### Initial GitHub Release
- Basic pipeline implementation
- Knowledge base structure
- Router with Regex + LLM
- 2-tier context injection
- Escalation handling

---

## Migration Notes

### From v2.2 to v3.0
1. Run `./install.sh` for automated setup
2. Or manually:
   - Update `config/channels.json` with actual Feishu ID
   - Set `GEMINI_API_KEY` environment variable
   - Run `python3 scripts/health_check.py` to verify

### Known Issues
- `google-generativeai` package is deprecated (warning shown)
  - Future versions will migrate to `google-genai`
  - Current version still works, but will need migration

### Breaking Changes
- None (v3.0 is backward compatible with v2.2 configuration)

---

## Roadmap

### v3.1 (Planned)
- [ ] Migrate to `google-genai` package
- [ ] Add more Chinese Regex patterns
- [ ] Implement caching for common queries
- [ ] Add metrics/analytics

### v4.0 (Future)
- [ ] Skill Worker implementation (API calls)
- [ ] Shopify integration
- [ ] Order tracking
- [ ] Advanced escalation routing

---

**Full Changelog**: https://github.com/alstonzhuang-sys/even-cs-agent/compare/v2.2...v3.0
