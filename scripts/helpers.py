#!/usr/bin/env python3
"""
Helper Functions for DivaD CS Agent

Purpose: Provide utility functions for SKILL.md execution
"""

import re
import json


def extract_section(text: str, section_name: str) -> str:
    """
    Extract a specific section from a Markdown file.
    
    Args:
        text: Full Markdown content
        section_name: Section header name (without ##)
        
    Returns:
        Extracted section content (including header)
        
    Example:
        text = "## Specs\nG2 has...\n## Pricing\n$599"
        extract_section(text, "Specs")
        # Returns: "## Specs\nG2 has..."
    """
    # Find section header (## Section Name)
    # Match until next ## (same level) or end of file
    # Include all ### subsections
    pattern = f"## {re.escape(section_name)}.*?(?=\n## [^#]|\\Z)"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(0).strip()
    else:
        return ""


def contains_sensitive_info(text: str) -> bool:
    """
    Check if response contains sensitive information.
    
    Args:
        text: Response text to check
        
    Returns:
        True if sensitive info detected, False otherwise
        
    Sensitive patterns:
        - Internal cost (e.g., "our cost is $50", "cost us $50")
        - Profit margin
        - Internal process
        - User mentions (e.g., "@Caris")
    """
    sensitive_patterns = [
        r"(our|internal|actual)\s+cost.*\$\d+",  # Internal cost (not product price)
        r"cost\s+(us|them)\s+\$\d+",             # "cost us $50"
        r"profit.*margin",                        # Profit margin
        r"internal.*process",                     # Internal process
        r"@\w+",                                  # Mentions (@Caris, @Rosen)
        r"kb_\w+\.md",                           # Knowledge base file names
        r"SOUL\.md",                             # Internal file names
        r"AGENT\.md"
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def get_owner(intent: str) -> str:
    """
    Get suggested owner for escalation based on intent.
    
    Args:
        intent: Detected intent (e.g., "specs_query", "return_request")
        
    Returns:
        Owner mention (e.g., "@Caris")
    """
    owner_map = {
        "specs_query": "@Caris",
        "policy_query": "@Rosen",
        "order_status": "@Rosen",
        "return_request": "@Rosen",
        "jailbreak": "@David",
        "knowledge_query": "@Caris"
    }
    
    return owner_map.get(intent, "@Caris")


def filter_internal_keywords(text: str) -> str:
    """
    Remove internal keywords and sensitive content from response (for external surface).
    
    Strategy:
    1. Remove sentences containing internal keywords
    2. Remove mentions (@Username)
    3. Remove file references (kb_*.md, SOUL.md, etc.)
    
    Args:
        text: Response text
        
    Returns:
        Filtered text with internal content removed
    """
    # Split into sentences
    sentences = re.split(r'([.!?]\s+)', text)
    
    # Internal patterns to remove
    internal_patterns = [
        r"@\w+",                    # Mentions
        r"kb_\w+\.md",             # KB file names
        r"SOUL\.md",               # Internal files
        r"AGENT\.md",
        r"internal\s+(note|cost|process)",  # Internal notes
        r"our\s+cost",             # Internal cost
        r"profit\s+margin",        # Profit margin
        r"debug",                  # Debug info
        r"confidence",             # Confidence scores
        r"owner"                   # Owner mentions
    ]
    
    # Filter sentences
    filtered_sentences = []
    for i in range(0, len(sentences), 2):  # Process sentence + delimiter pairs
        sentence = sentences[i]
        delimiter = sentences[i+1] if i+1 < len(sentences) else ""
        
        # Check if sentence contains internal patterns
        contains_internal = False
        for pattern in internal_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                contains_internal = True
                break
        
        # Keep sentence if it doesn't contain internal patterns
        if not contains_internal:
            filtered_sentences.append(sentence + delimiter)
    
    return ''.join(filtered_sentences).strip()


def format_debug_info(intent: str, pattern: str, surface: str, confidence: float = 1.0) -> str:
    """
    Format debug information for internal surface.
    
    Args:
        intent: Detected intent
        pattern: Matched regex pattern
        surface: Surface type (external/internal)
        confidence: Confidence score (0-1)
        
    Returns:
        Formatted debug info string
    """
    owner = get_owner(intent)
    
    debug_info = f"""

[Debug Info]
- Intent: {intent}
- Pattern: {pattern}
- Surface: {surface}
- Confidence: {confidence:.2f}
- Suggested Owner: {owner}
"""
    
    return debug_info


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python helpers.py extract_section <file> <section_name>")
        print("  python helpers.py contains_sensitive <text>")
        print("  python helpers.py get_owner <intent>")
        print("  python helpers.py filter_keywords <text>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "extract_section":
        if len(sys.argv) < 4:
            print("Usage: python helpers.py extract_section <file> <section_name>")
            sys.exit(1)
        
        file_path = sys.argv[2]
        section_name = sys.argv[3]
        
        with open(file_path, 'r') as f:
            text = f.read()
        
        result = extract_section(text, section_name)
        print(result)
    
    elif command == "contains_sensitive":
        text = " ".join(sys.argv[2:])
        result = contains_sensitive_info(text)
        print(json.dumps({"contains_sensitive": result}))
    
    elif command == "get_owner":
        intent = sys.argv[2]
        result = get_owner(intent)
        print(result)
    
    elif command == "filter_keywords":
        text = " ".join(sys.argv[2:])
        result = filter_internal_keywords(text)
        print(result)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

