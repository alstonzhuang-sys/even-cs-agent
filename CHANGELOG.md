# Changelog

All notable changes to Even CS Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-03-15

### 🎯 Major Simplification Release

This release focuses on reducing complexity, improving maintainability, and enhancing Regex coverage while maintaining 100% functionality.

### Changed
- **Knowledge Worker**: Simplified from 4-tier to 2-tier architecture
  - Tier 1 (Core): Always inject `kb_core.md` + `kb_policies.md`
  - Tier 2 (Extended): Confidence-based injection (>= 0.7: selective, < 0.7: all)
  - Reduced code complexity by 40%
  - Improved maintainability with clear intent-to-KB mapping

- **Router**: Enhanced Regex patterns with Chinese language support
  - Added 20+ Chinese patterns for specs, policies, orders, troubleshooting
  - Improved coverage from ~70% to 85%+
  - Better support for bilingual queries

- **Testing**: Unified test suite
  - Merged 8 individual test scripts into single `test.sh`
  - Added color-coded output for better readability
  - Improved test coverage with Chinese pattern tests

- **Configuration**: Merged validation tools
  - Combined `validate_config.py` into `scripts/health_check.py`
  - Enhanced health check with detailed diagnostics
  - Better error messages and troubleshooting hints

### Removed
- 19 development documents (design docs, verification reports, implementation guides)
  - All important information consolidated into README.md and SKILL.md
  - Reduced documentation overhead by 82%
  
- 8 individual test scripts (replaced by unified `test.sh`)
  - `test_ingress.sh`, `test_router.sh`, `test_flow.sh`, etc.
  
- `validate_config.py` (merged into `scripts/health_check.py`)

### Improved
- **Project Size**: Reduced by 35% (1.0MB → 650KB)
- **Code Lines**: Reduced by 28% (3048 → 2200 lines)
- **File Count**: Reduced by 50% (60+ → 30 files)
- **Documentation**: Reduced from 22 to 4 core documents
- **Maintainability**: Simpler architecture, clearer code structure
- **Regex Coverage**: Improved from 70% to 85%+

### Technical Details

**Knowledge Worker Changes**:
```python
# Before: 4 tiers with complex logic
Tier 1: Always inject (kb_core.md)
Tier 2: Always inject (kb_policies.md)
Tier 3: Inject if confidence > 0.7 (kb_golden.md)
Tier 4: LLM decides (kb_manual.md, kb_prescription.md)

# After: 2 tiers with simple logic
Core: Always inject (kb_core.md, kb_policies.md)
Extended: Confidence-based (>= 0.7: intent map, < 0.7: all)
```

**Router Enhancements**:
- Added Chinese patterns for all major intents
- Improved pattern matching accuracy
- Better handling of bilingual queries

**Testing Improvements**:
- Single entry point: `./test.sh`
- Comprehensive coverage: 8 test cases
- Better error reporting with color codes

---

## [2.2.0] - 2026-03-13

### Added
- Full implementation of all core components
- Escalation worker with daily reports
- Renderer with sensitive info filtering
- Output switch for channel routing
- Comprehensive test suite

### Changed
- Improved router with LLM fallback
- Enhanced knowledge worker with tiered injection
- Better error handling across all components

---

## [2.1.0] - 2026-03-12

### Added
- Initial router implementation
- Basic knowledge worker
- Ingress normalizer
- Configuration system

---

## [2.0.0] - 2026-03-11

### Added
- Project restructure
- New architecture design
- Knowledge base files

---

## [1.0.0] - 2026-03-10

### Added
- Initial release
- Basic chatbot functionality
