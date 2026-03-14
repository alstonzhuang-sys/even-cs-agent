#!/usr/bin/env python3
"""
Even CS Agent - OpenClaw Entry Point

This is the main entry point called by OpenClaw when a message is received.
Handles customer support queries for Even Realities products (G1/G2 AR glasses).

Usage:
    Called automatically by OpenClaw when a message is received.
    Can also be tested manually:
    
    echo '{"channel":"discord","sender_id":"123","message":"What is the battery life?"}' | python3 main.py

Architecture:
    1. Ingress: Normalize input from different channels
    2. Router: Classify intent (Regex-first, LLM fallback)
    3. Worker: Execute appropriate handler (Knowledge/Skill/Escalation)
    4. Renderer: Filter output based on surface (external/internal)
    5. Output: Return formatted response
"""

import sys
import json
import os
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import components
try:
    from ingress import normalize_payload, validate_payload
    from router import route
    from output_switch import load_config, get_surface
except ImportError as e:
    print(json.dumps({"error": f"Failed to import modules: {e}"}), file=sys.stderr)
    sys.exit(1)


def check_config():
    """
    Validate configuration before starting.
    
    Checks:
    1. GEMINI_API_KEY is set
    2. config/channels.json exists
    3. Rosen's Feishu ID is not a placeholder
    
    Raises:
        SystemExit: If configuration is invalid
    """
    # Check 1: API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(json.dumps({
            "error": "GEMINI_API_KEY not set",
            "help": "Set with: export GEMINI_API_KEY='your_key_here'"
        }), file=sys.stderr)
        sys.exit(1)
    
    # Check 2: Config file
    try:
        config = load_config()
    except Exception as e:
        print(json.dumps({
            "error": f"Failed to load configuration: {e}",
            "help": "Create config/channels.json from config/channels.json.example"
        }), file=sys.stderr)
        sys.exit(1)
    
    # Check 3: Placeholder check
    rosen_id = config.get("rosen_contact", {}).get("feishu_id", "")
    if rosen_id == "ou_xxx":
        print(json.dumps({
            "error": "Rosen's Feishu ID is still a placeholder (ou_xxx)",
            "help": "Edit config/channels.json and replace with actual Feishu ID"
        }), file=sys.stderr)
        sys.exit(1)


def process_knowledge_query(message: str, intent: str, surface: str) -> str:
    """
    Process knowledge query using full context injection.
    
    Args:
        message: User message
        intent: Detected intent
        surface: external or internal
        
    Returns:
        Response text
    """
    try:
        from knowledge_worker import build_context, generate_response
        
        # Build context from knowledge base
        context = build_context(intent, surface)
        
        # Generate response
        response = generate_response(message, intent, surface, context)
        
        return response
    except Exception as e:
        return f"I encountered an error processing your query. Please try again. (Error: {str(e)[:50]})"


def handle_escalation(message: str, intent: str, surface: str) -> str:
    """
    Handle escalation (unknown queries or jailbreak attempts).
    
    Args:
        message: User message
        intent: Detected intent
        surface: external or internal
        
    Returns:
        Response text
    """
    if intent == "jailbreak":
        return "I cannot fulfill that request. How can I help you with Even Realities products?"
    
    # Unknown query - store for escalation
    try:
        from escalation_worker import store_case
        
        case_id = store_case(
            message=message,
            intent=intent,
            surface=surface,
            case_type="gap",
            severity="medium"
        )
        
        if surface == "internal":
            return f"I don't have that information right now. Let me check with the team. (Case: {case_id})"
        else:
            return "I don't have that information right now. Let me check with the team."
    except Exception as e:
        return "I don't have that information right now. Let me check with the team."


def render_response(raw_response: str, surface: str, intent: str, confidence: float) -> str:
    """
    Render response with appropriate filtering.
    
    Args:
        raw_response: Raw response from worker
        surface: external or internal
        intent: Detected intent
        confidence: Confidence score
        
    Returns:
        Filtered response
    """
    try:
        from renderer import filter_sensitive_info, add_debug_info
        
        # Filter sensitive info for external surface
        if surface == "external":
            response = filter_sensitive_info(raw_response)
        else:
            response = raw_response
        
        # Add debug info for internal surface
        if surface == "internal":
            response = add_debug_info(
                response,
                intent=intent,
                confidence=confidence,
                surface=surface
            )
        
        return response
    except Exception as e:
        # Fallback: return raw response
        return raw_response


def main():
    """
    Main entry point for OpenClaw.
    
    Expected input (JSON from stdin):
    {
        "channel": "discord" | "feishu",
        "sender_id": "user_id",
        "message_id": "msg_id",
        "message": "user message text"
    }
    
    Output (JSON to stdout):
    {
        "response": "response text",
        "intent": "detected_intent",
        "confidence": 0.0-1.0,
        "surface": "external" | "internal"
    }
    """
    # Validate configuration
    check_config()
    
    # Read input from stdin
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print(json.dumps({"error": "No input provided"}), file=sys.stderr)
            sys.exit(1)
        
        context = json.loads(input_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)
        sys.exit(1)
    
    # Extract fields
    channel = context.get("channel", "unknown")
    sender_id = context.get("sender_id", "unknown")
    message_id = context.get("message_id", "unknown")
    message = context.get("message", "")
    
    if not message.strip():
        print(json.dumps({"error": "Empty message"}), file=sys.stderr)
        sys.exit(1)
    
    # Step 1: Normalize input
    payload = normalize_payload(
        channel=channel,
        sender_id=sender_id,
        message_id=message_id,
        message=message
    )
    
    # Validate payload
    is_valid, error = validate_payload(payload)
    if not is_valid:
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(1)
    
    surface = payload["surface"]
    
    # Step 2: Route to worker
    routing = route(message, use_llm=True)
    intent = routing["intent"]
    worker = routing["worker"]
    confidence = routing["confidence"]
    
    # Step 3: Execute worker
    if worker == "knowledge_worker":
        raw_response = process_knowledge_query(message, intent, surface)
    elif worker == "escalation_worker":
        raw_response = handle_escalation(message, intent, surface)
    elif worker == "skill_worker":
        # Skill worker not implemented yet (Phase 2)
        raw_response = "This feature is coming soon. For now, please contact support directly."
    else:
        raw_response = "I don't have that information right now. Let me check with the team."
    
    # Step 4: Render response
    final_response = render_response(
        raw_response,
        surface=surface,
        intent=intent,
        confidence=confidence
    )
    
    # Step 5: Output
    output = {
        "response": final_response,
        "intent": intent,
        "confidence": confidence,
        "surface": surface,
        "worker": worker
    }
    
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
