#!/usr/bin/env python3
"""
Health check and configuration validation for Even CS Agent.

Verifies:
1. GEMINI_API_KEY is set
2. Configuration file exists and is valid
3. Rosen's Feishu ID is not a placeholder
4. Knowledge base files exist
5. LLM connection works

Returns:
    0: Healthy
    1: Unhealthy

Usage:
    python3 scripts/health_check.py
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_api_key():
    """Check if GEMINI_API_KEY is set."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY: Set ({len(api_key)} chars)")
        return True
    else:
        print("❌ GEMINI_API_KEY: Not set")
        print("   Set with: export GEMINI_API_KEY='your_key_here'")
        return False


def check_config_file():
    """Check if config/channels.json exists and is valid."""
    config_file = Path(__file__).parent.parent / "config" / "channels.json"
    
    if not config_file.exists():
        print("❌ Configuration file: Not found")
        print("   Create with: cp config/channels.json.example config/channels.json")
        return False, None
    
    try:
        with open(config_file) as f:
            config = json.load(f)
        print("✅ Configuration file: config/channels.json")
        return True, config
    except Exception as e:
        print(f"❌ Configuration file: Invalid JSON ({e})")
        return False, None


def check_rosen_id(config):
    """Check if Rosen's Feishu ID is configured."""
    if not config:
        print("❌ Rosen contact: Config not loaded")
        return False
    
    rosen_id = config.get("rosen_contact", {}).get("feishu_id", "")
    
    if not rosen_id:
        print("❌ Rosen contact: Not configured")
        return False
    elif rosen_id == "ou_xxx":
        print("❌ Rosen contact: Still placeholder (ou_xxx)")
        print("   Edit config/channels.json and replace with actual Feishu ID")
        return False
    else:
        print(f"✅ Rosen contact: {rosen_id}")
        return True


def check_channels(config):
    """Check if channels are configured."""
    if not config:
        print("❌ Channels: Config not loaded")
        return False
    
    external = config.get("external", [])
    internal = config.get("internal", [])
    fallback = config.get("fallback", "external")
    
    print(f"✅ External channels: {external}")
    print(f"✅ Internal channels: {internal}")
    print(f"✅ Fallback surface: {fallback}")
    
    return True


def check_knowledge_base():
    """Check if knowledge base files exist."""
    kb_dir = Path(__file__).parent.parent / "knowledge"
    
    if not kb_dir.exists():
        print("❌ Knowledge base: Directory not found")
        return False
    
    kb_files = list(kb_dir.glob("*.md"))
    
    if len(kb_files) < 3:
        print(f"❌ Knowledge base: Only {len(kb_files)} files found (expected >= 3)")
        return False
    
    print(f"✅ Knowledge base: {len(kb_files)} files")
    
    # Check for core files
    core_files = ["kb_core.md", "kb_policies.md"]
    for core_file in core_files:
        if (kb_dir / core_file).exists():
            print(f"   ✅ {core_file}")
        else:
            print(f"   ❌ {core_file} (missing)")
    
    return True


def check_llm_connection():
    """Check if LLM connection works."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ LLM connection: API key not set")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(
            "Test",
            generation_config={"max_output_tokens": 5, "temperature": 0}
        )
        print("✅ LLM connection: Working")
        return True
    except ImportError:
        print("❌ LLM connection: google-generativeai not installed")
        print("   Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ LLM connection: Failed ({str(e)[:50]})")
        return False


def check_health():
    """
    Run all health checks.
    
    Returns:
        int: 0 if healthy, 1 if unhealthy
    """
    print("=== Even CS Agent Health Check ===\n")
    
    checks = []
    
    # Check 1: API key
    checks.append(check_api_key())
    print()
    
    # Check 2: Config file
    config_ok, config = check_config_file()
    checks.append(config_ok)
    print()
    
    # Check 3: Rosen ID
    checks.append(check_rosen_id(config))
    print()
    
    # Check 4: Channels
    checks.append(check_channels(config))
    print()
    
    # Check 5: Knowledge base
    checks.append(check_knowledge_base())
    print()
    
    # Check 6: LLM connection
    checks.append(check_llm_connection())
    print()
    
    # Summary
    all_passed = all(checks)
    
    if all_passed:
        print("=== ✅ Configuration is valid! ===")
        return 0
    else:
        print("=== ❌ Some checks failed ===")
        return 1


if __name__ == "__main__":
    sys.exit(check_health())
