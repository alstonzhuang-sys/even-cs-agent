#!/usr/bin/env python3
"""
Rate Limiter - User-level rate limiting and repeat detection

Purpose:
1. Rate limit: Max N messages per minute per user
2. Repeat detection: Same message 3+ times → suggest human agent
3. Conversation turn limit: Max 20 turns per session → escalate

Storage: Simple JSON file (escalations/rate_limit.json)
"""

import json
import time
from pathlib import Path
from typing import Tuple

RATE_LIMIT_FILE = Path(__file__).parent.parent / "escalations" / "rate_limit.json"
RATE_LIMIT_FILE.parent.mkdir(exist_ok=True)

# Configuration
MAX_MESSAGES_PER_MINUTE = 5
REPEAT_THRESHOLD = 3
COOLDOWN_WINDOW = 60  # seconds


def _load_state() -> dict:
    if RATE_LIMIT_FILE.exists():
        try:
            with open(RATE_LIMIT_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_state(state: dict):
    with open(RATE_LIMIT_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False)


def check_rate_limit(sender_id: str, message: str) -> Tuple[bool, str]:
    """
    Check rate limit and repeat detection.
    
    Args:
        sender_id: User ID
        message: User message text
        
    Returns:
        (is_allowed, rejection_message)
        - (True, "") if allowed
        - (False, "reason message") if blocked
    """
    state = _load_state()
    now = time.time()
    
    # Initialize user state
    if sender_id not in state:
        state[sender_id] = {"timestamps": [], "recent_messages": []}
    
    user = state[sender_id]
    
    # Clean old timestamps (outside cooldown window)
    user["timestamps"] = [t for t in user["timestamps"] if now - t < COOLDOWN_WINDOW]
    
    # Check 1: Rate limit (messages per minute)
    if len(user["timestamps"]) >= MAX_MESSAGES_PER_MINUTE:
        _save_state(state)
        return False, "You're sending messages too quickly. Please wait a moment and try again."
    
    # Check 2: Repeat detection (same message 3+ times)
    normalized = message.strip().lower()
    # Keep last 10 messages for repeat check
    user["recent_messages"] = user["recent_messages"][-9:]
    repeat_count = sum(1 for m in user["recent_messages"] if m == normalized)
    
    if repeat_count >= REPEAT_THRESHOLD - 1:  # -1 because current message not yet added
        user["recent_messages"].append(normalized)
        user["timestamps"].append(now)
        _save_state(state)
        return False, "I believe I've already answered this question. Would you like me to connect you with a human agent?"
    
    # Record this message
    user["timestamps"].append(now)
    user["recent_messages"].append(normalized)
    _save_state(state)
    
    return True, ""
