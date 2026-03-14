#!/usr/bin/env python3
"""
Health check script for Even CS Agent.

Verifies:
1. GEMINI_API_KEY is set
2. Configuration file exists and is valid
3. Knowledge base files exist
4. LLM connection works

Returns:
    0: Healthy
    1: Unhealthy

Usage:
    python3 scripts/health_check.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_health():
    """
    Check if the agent is healthy.
    
    Returns:
        int: 0 if healthy, 1 if unhealthy
    """
    checks = []
    
    # Check 1: API key
    api_key = os.environ.get("GEMINI_API_KEY")
    checks.append(("GEMINI_API_KEY", bool(api_key)))
    
    # Check 2: Config file
    config_file = Path(__file__).parent.parent / "config" / "channels.json"
    checks.append(("Config file", config_file.exists()))
    
    # Check 3: Config is not placeholder
    if config_file.exists():
        try:
            import json
            with open(config_file) as f:
                config = json.load(f)
            rosen_id = config.get("rosen_contact", {}).get("feishu_id", "")
            checks.append(("Rosen ID configured", rosen_id != "ou_xxx"))
        except Exception:
            checks.append(("Rosen ID configured", False))
    else:
        checks.append(("Rosen ID configured", False))
    
    # Check 4: Knowledge base
    kb_dir = Path(__file__).parent.parent / "knowledge"
    kb_files = list(kb_dir.glob("*.md")) if kb_dir.exists() else []
    checks.append(("Knowledge base", len(kb_files) >= 3))
    
    # Check 5: Test LLM connection
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(
                "Test",
                generation_config={"max_output_tokens": 5, "temperature": 0}
            )
            checks.append(("LLM connection", True))
        except Exception as e:
            checks.append(("LLM connection", False))
    else:
        checks.append(("LLM connection", False))
    
    # Print results
    print("=== Even CS Agent Health Check ===\n")
    
    all_passed = True
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("=== All checks passed! ===")
        return 0
    else:
        print("=== Some checks failed ===")
        return 1


if __name__ == "__main__":
    sys.exit(check_health())
