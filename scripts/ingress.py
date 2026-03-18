#!/usr/bin/env python3
"""
Ingress Normalizer - Entry Point for All Messages

Purpose: Normalize incoming messages from different channels (Discord/Feishu)
         into a standard format for downstream processing.

Key Responsibilities:
1. Detect channel (Discord = external, Feishu = internal)
2. Extract sender_id, message_id, timestamp
3. Normalize message payload
4. Session reset (each ticket = new session)

Usage:
    python3 ingress.py --channel discord --sender-id 123 --message "Hello"
    python3 ingress.py --channel feishu --sender-id ou_xxx --message "查询订单"

Output: JSON payload
{
    "surface": "external" | "internal",
    "channel": "discord" | "feishu",
    "sender_id": "...",
    "message_id": "...",
    "timestamp": "...",
    "message": "...",
    "session_reset": true
}
"""

import sys
import json
import argparse
from datetime import datetime

# Hard-coded channel mapping (deterministic, no LLM needed)
CHANNEL_SURFACE_MAP = {
    "discord": "external",
    "feishu": "internal",
    "telegram": "external",  # Future support
    "whatsapp": "external",  # Future support
}

def normalize_payload(channel, sender_id, message_id, message, timestamp=None):
    """
    Normalize incoming message into standard format.
    
    Args:
        channel: Channel name (discord/feishu)
        sender_id: User ID from the channel
        message_id: Message ID
        message: User message text
        timestamp: Optional timestamp (ISO 8601)
    
    Returns:
        dict: Normalized payload
    """
    # Determine surface (external vs internal)
    surface = CHANNEL_SURFACE_MAP.get(channel.lower(), "external")
    
    # Generate timestamp if not provided
    if not timestamp:
        from datetime import timezone
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Build normalized payload
    payload = {
        "surface": surface,
        "channel": channel.lower(),
        "sender_id": sender_id,
        "message_id": message_id or "unknown",
        "timestamp": timestamp,
        "message": message.strip(),
        "session_reset": True  # Each message = new session (stateless)
    }
    
    return payload

def validate_payload(payload):
    """
    Validate normalized payload.
    
    Args:
        payload: Normalized payload dict
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ["surface", "channel", "sender_id", "message"]
    
    for field in required_fields:
        if field not in payload or not payload[field]:
            return False, f"Missing required field: {field}"
    
    # Validate surface
    if payload["surface"] not in ["external", "internal"]:
        return False, f"Invalid surface: {payload['surface']}"
    
    # Validate message length
    if len(payload["message"]) > 10000:
        return False, "Message too long (max 10000 chars)"
    
    return True, None

def main():
    parser = argparse.ArgumentParser(description="Ingress Normalizer")
    parser.add_argument("--channel", required=True, help="Channel name (discord/feishu)")
    parser.add_argument("--sender-id", required=True, help="Sender ID")
    parser.add_argument("--message-id", help="Message ID (optional)")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--timestamp", help="Timestamp (ISO 8601, optional)")
    
    args = parser.parse_args()
    
    # Normalize payload
    payload = normalize_payload(
        channel=args.channel,
        sender_id=args.sender_id,
        message_id=args.message_id,
        message=args.message,
        timestamp=args.timestamp
    )
    
    # Validate payload
    is_valid, error = validate_payload(payload)
    if not is_valid:
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(1)
    
    # Output normalized payload
    print(json.dumps(payload, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

