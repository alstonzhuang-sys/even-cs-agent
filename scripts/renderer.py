#!/usr/bin/env python3
"""
Renderer - Filter and format responses based on surface

Purpose:
    1. External (Discord): Filter sensitive info, remove internal keywords
    2. Internal (Feishu): Add debug info, show full context

Usage:
    python renderer.py <response> <surface> <intent> [confidence]
    
Example:
    python renderer.py "The G2 costs $599" "external" "specs_query" "1.0"
    python renderer.py "The G2 costs $599" "internal" "specs_query" "1.0"
"""

import sys
import os

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from helpers import (
    filter_internal_keywords,
    contains_sensitive_info,
    format_debug_info,
    get_owner
)


def render_external(response: str) -> str:
    """
    Render response for external surface (Discord).
    
    Args:
        response: Raw response text
        
    Returns:
        Filtered response
    """
    # Filter internal keywords
    filtered = filter_internal_keywords(response)
    
    # Check for sensitive info in filtered text
    if contains_sensitive_info(filtered):
        return "I don't have that information right now. Let me check with the team."
    
    # If filtering removed everything, return fallback
    if not filtered or len(filtered.strip()) < 10:
        return "I don't have that information right now. Let me check with the team."
    
    return filtered.strip()


def render_internal(response: str, intent: str, confidence: float, pattern: str = None) -> str:
    """
    Render response for internal surface (Feishu).
    
    Args:
        response: Raw response text
        intent: Detected intent
        confidence: Confidence score
        pattern: Matched pattern (optional)
        
    Returns:
        Response with debug info
    """
    # Add debug info
    debug_info = format_debug_info(
        intent=intent,
        pattern=pattern or "N/A",
        surface="internal",
        confidence=confidence
    )
    
    return response.strip() + debug_info


def render_response(response: str, surface: str, intent: str, confidence: float, pattern: str = None) -> str:
    """
    Render response based on surface.
    
    Args:
        response: Raw response text
        surface: external or internal
        intent: Detected intent
        confidence: Confidence score
        pattern: Matched pattern (optional)
        
    Returns:
        Rendered response
    """
    if surface == "external":
        return render_external(response)
    elif surface == "internal":
        return render_internal(response, intent, confidence, pattern)
    else:
        # Default to external (safer)
        return render_external(response)


def main():
    """CLI interface"""
    if len(sys.argv) < 4:
        print("Usage: python renderer.py <response> <surface> <intent> [confidence] [pattern]")
        print("\nExample:")
        print('  python renderer.py "The G2 costs $599" "external" "specs_query" "1.0"')
        print('  python renderer.py "The G2 costs $599" "internal" "specs_query" "1.0" "price.*g2"')
        sys.exit(1)
    
    response = sys.argv[1]
    surface = sys.argv[2]
    intent = sys.argv[3]
    confidence = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    pattern = sys.argv[5] if len(sys.argv) > 5 else None
    
    if surface == "external":
        result = render_external(response)
    elif surface == "internal":
        result = render_internal(response, intent, confidence, pattern)
    else:
        # Default to external (safer)
        result = render_external(response)
    
    print(result)


if __name__ == "__main__":
    main()
