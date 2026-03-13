#!/usr/bin/env python3
"""
Knowledge Worker - Full Context Injection with Tiered Strategy

Purpose:
1. Inject knowledge base files into LLM context based on tier strategy
2. Support hot-reload (auto-discover new .md files)
3. Use Gemini 2 Flash for generation

Tier Strategy:
- Tier 1 (Core): Always injected - Hardware specs, SKU, pricing
- Tier 2 (Policies): Always injected - Return/refund/shipping policies
- Tier 3 (Golden): Few-shot injection - Golden Q&A examples (style guide)
- Tier 4 (Niche): Dynamic injection - Long-tail troubleshooting (on-demand)

Usage:
    python3 knowledge_worker.py "What's the battery life?" "specs_query" "external"
    python3 knowledge_worker.py "退货政策是什么？" "policy_query" "internal"
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

# Knowledge base directory
KB_DIR = Path(__file__).parent.parent / "knowledge"

# Tier definitions (based on metadata)
TIER_STRATEGY = {
    1: "always",      # Core facts - always inject
    2: "always",      # Policies - always inject
    3: "few_shot",    # Golden examples - inject 3-5 examples
    4: "dynamic"      # Niche knowledge - inject on-demand
}


def parse_metadata(content: str) -> Dict:
    """
    Parse YAML frontmatter from markdown file.
    
    Args:
        content: File content
        
    Returns:
        dict: Metadata (visibility, keyTags, owner, tier, etc.)
    """
    # Extract YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    
    yaml_text = match.group(1)
    metadata = {}
    
    # Parse simple YAML (key: value)
    for line in yaml_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle lists (e.g., keyTags: [tag1, tag2])
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
            
            metadata[key] = value
    
    return metadata


def extract_content(content: str) -> str:
    """
    Extract content (remove YAML frontmatter).
    
    Args:
        content: File content
        
    Returns:
        str: Content without frontmatter
    """
    # Remove YAML frontmatter
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    return content.strip()


def discover_knowledge_files() -> List[Tuple[Path, Dict, str]]:
    """
    Auto-discover all .md files in knowledge/ directory.
    
    Returns:
        List of (file_path, metadata, content) tuples
    """
    files = []
    
    if not KB_DIR.exists():
        return files
    
    for md_file in KB_DIR.glob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            metadata = parse_metadata(raw_content)
            content = extract_content(raw_content)
            
            files.append((md_file, metadata, content))
        except Exception as e:
            print(f"Warning: Failed to read {md_file}: {e}", file=sys.stderr)
    
    return files


def determine_tier(metadata: Dict, filename: str) -> int:
    """
    Determine tier from metadata or filename.
    
    Priority:
    1. Explicit 'tier' field in metadata
    2. Infer from filename (kb_core.md → Tier 1)
    3. Default to Tier 4 (dynamic)
    
    Args:
        metadata: File metadata
        filename: File name
        
    Returns:
        int: Tier number (1-4)
    """
    # Explicit tier in metadata
    if 'tier' in metadata:
        try:
            return int(metadata['tier'])
        except:
            pass
    
    # Infer from filename
    filename_lower = filename.lower()
    if 'core' in filename_lower:
        return 1
    elif 'polic' in filename_lower:
        return 2
    elif 'golden' in filename_lower:
        return 3
    else:
        return 4


def build_context(intent: str, surface: str) -> str:
    """
    Build LLM context by injecting knowledge files based on tier strategy.
    
    Args:
        intent: User intent (from Router)
        surface: external or internal
        
    Returns:
        str: Full context for LLM
    """
    # Discover all knowledge files
    files = discover_knowledge_files()
    
    # Sort by tier
    files_by_tier = {1: [], 2: [], 3: [], 4: []}
    for file_path, metadata, content in files:
        tier = determine_tier(metadata, file_path.name)
        files_by_tier[tier].append((file_path, metadata, content))
    
    # Build context
    context_parts = []
    
    # Tier 1: Core (Always inject)
    for file_path, metadata, content in files_by_tier[1]:
        context_parts.append(f"# {file_path.name}\n\n{content}")
    
    # Tier 2: Policies (Always inject)
    for file_path, metadata, content in files_by_tier[2]:
        context_parts.append(f"# {file_path.name}\n\n{content}")
    
    # Tier 3: Golden (Few-shot - inject 5 examples)
    for file_path, metadata, content in files_by_tier[3]:
        # Extract first 5 Q&A pairs (simplified)
        lines = content.split('\n')
        sample_lines = lines[:200]  # Rough approximation
        context_parts.append(f"# {file_path.name} (Sample)\n\n" + '\n'.join(sample_lines))
    
    # Tier 4: Niche (Dynamic - inject if intent matches)
    # TODO: Implement semantic matching for Tier 4
    # For now, skip Tier 4 (will implement in Phase 2)
    
    return "\n\n---\n\n".join(context_parts)


def generate_response(message: str, intent: str, surface: str, context: str) -> str:
    """
    Generate response using Gemini 2 Flash with full context.
    
    Args:
        message: User message
        intent: Intent from Router
        surface: external or internal
        context: Knowledge base context
        
    Returns:
        str: Generated response
    """
    # Check if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "[ERROR] GEMINI_API_KEY not set. Cannot generate response."
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build prompt
        system_instruction = f"""You are DivaD, a customer support agent for Even Realities.

Surface: {surface}
- If external (Discord): Only provide approved, compliant information. Be professional.
- If internal (Feishu): Provide full details including debug info.

Intent: {intent}

Knowledge Base:
{context}

Instructions:
1. Answer ONLY based on the knowledge base above
2. If information is not in the knowledge base, say "I don't have that information"
3. Be concise and helpful
4. For external surface, avoid internal notes marked [INTERNAL ONLY]
5. Use Temperature=0 for factual accuracy
"""
        
        prompt = f"{system_instruction}\n\nUser: {message}\n\nAssistant:"
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 500
            }
        )
        
        return response.text.strip()
        
    except ImportError:
        return "[ERROR] google-generativeai not installed. Run: pip install google-generativeai"
    except Exception as e:
        return f"[ERROR] {str(e)}"


def main():
    parser = argparse.ArgumentParser(description="Knowledge Worker")
    parser.add_argument("message", help="User message")
    parser.add_argument("intent", help="Intent from Router")
    parser.add_argument("surface", choices=["external", "internal"], help="Surface type")
    parser.add_argument("--debug", action="store_true", help="Show context")
    
    args = parser.parse_args()
    
    # Build context
    context = build_context(args.intent, args.surface)
    
    if args.debug:
        print("=== Context ===")
        print(context[:1000] + "..." if len(context) > 1000 else context)
        print("\n=== Response ===")
    
    # Generate response
    response = generate_response(args.message, args.intent, args.surface, context)
    
    print(response)


if __name__ == "__main__":
    main()
