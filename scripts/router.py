#!/usr/bin/env python3
"""
Router - Intent Detection & Worker Assignment

Purpose: 
1. Match user messages to intents using hard-coded Regex patterns (deterministic)
2. Use LLM (Gemini 2 Flash) as fallback for ambiguous cases
3. Assign to appropriate worker: skill_worker / knowledge_worker / escalation_worker

Usage:
    python router.py "Where is my order #12345?"
    # Output: {"intent": "order_status", "worker": "skill_worker", "confidence": 1.0, "method": "regex"}
    
    python router.py "What's the battery life?" --use-llm
    # Output: {"intent": "specs_query", "worker": "knowledge_worker", "confidence": 0.85, "method": "llm"}
"""

import re
import sys
import json
import os
import argparse

# Define patterns (order matters - check high-risk first)
PATTERNS = {
    # ===== SECURITY (Highest Priority) =====
    "jailbreak": [
        r"ignore.*instruction",
        r"you are now",
        r"disregard.*programming",
        r"system prompt",
        r"tell me.*instructions",
        r"what are your.*rules",
        r"reveal.*prompt",
        r"act as.*different",
        r"pretend.*you.*are"
    ],
    
    # ===== HIGH-RISK OPERATIONS (Skill Worker) =====
    "order_status": [
        # English patterns
        r"order\s*#?\d{4,}",
        r"where is my.*order",
        r"track.*shipment",
        r"shipping.*status",
        r"delivery.*status",
        r"when will.*arrive",
        r"order.*tracking",
        # Chinese patterns
        r"订单.*在哪",
        r"快递.*到哪",
        r"什么时候.*到",
        r"物流.*信息",
        r"订单.*状态",
        r"发货.*了吗"
    ],
    
    "return_request": [
        r"return.*product",
        r"return.*glasses",
        r"return.*g[12]",
        r"refund.*order",
        r"send.*back",
        r"cancel.*order",
        r"exchange.*product",
        r"want.*refund",
        r"want.*return",
        # Chinese patterns
        r"退货",
        r"退款",
        r"退钱",
        r"取消.*订单",
        r"不想要"
    ],
    
    # ===== KNOWLEDGE QUERIES (Knowledge Worker) =====
    "specs_query": [
        # English patterns
        r"battery.*life",
        r"how much.*cost",
        r"what.*price",
        r"support.*language",
        r"compatible.*with",
        r"weight",
        r"display",
        r"resolution",
        r"field.*view",
        r"bluetooth",
        r"charging.*time",
        r"waterproof",
        r"ip\d+",
        r"warranty",
        r"g1.*g2.*difference",
        r"compare.*g1.*g2",
        # Chinese patterns
        r"电池.*续航",
        r"多少.*钱",
        r"什么.*价格",
        r"价格.*多少",
        r"支持.*语言",
        r"兼容.*吗",
        r"重量",
        r"显示.*效果",
        r"分辨率",
        r"视场角",
        r"蓝牙",
        r"充电.*时间",
        r"防水",
        r"保修"
    ],
    
    "policy_query": [
        # English patterns
        r"return.*policy",
        r"refund.*policy",
        r"warranty.*period",
        r"shipping.*cost",
        r"ship.*to",
        r"customs.*fee",
        r"delivery.*time",
        r"how long.*ship",
        # Chinese patterns
        r"退货.*政策",
        r"退款.*政策",
        r"保修.*期",
        r"运费",
        r"邮费",
        r"发货.*时间",
        r"多久.*到",
        r"配送.*时间"
    ],
    
    "competitor_comparison": [
        r"compare.*meta",
        r"compare.*ray-ban",
        r"better than.*meta",
        r"vs.*meta",
        r"meta.*ray-ban",
        r"xreal",
        r"nreal",
        r"vuzix"
    ],
    
    "troubleshooting": [
        # English patterns
        r"not.*work",
        r"broken",
        r"error",
        r"problem.*with",
        r"can't.*connect",
        r"won't.*charge",
        r"display.*issue",
        r"bluetooth.*problem",
        # Chinese patterns
        r"不能.*充电",
        r"无法.*连接",
        r"蓝牙.*断开",
        r"显示.*不清楚",
        r"镜片.*模糊",
        r"坏了",
        r"故障",
        r"问题"
    ],
    
    "prescription_query": [
        # English patterns
        r"prescription",
        r"rx\b",
        r"diopter",
        r"myopi",
        r"astigmatis",
        r"progressive.*lens",
        r"single.*vision",
        r"optical.*insert",
        r"lens.*replacement",
        r"eye.*glass.*prescription",
        # Chinese patterns
        r"处方",
        r"近视",
        r"散光",
        r"度数",
        r"配镜",
        r"镜片.*更换",
        r"光学",
        r"验光"
    ]
}

# Worker assignment rules
WORKER_ASSIGNMENT = {
    # Security → Escalation (hard-coded response)
    "jailbreak": "escalation_worker",
    
    # High-risk operations → Knowledge Worker (Phase 2: will switch to Skill Worker)
    "order_status": "knowledge_worker",
    "return_request": "knowledge_worker",
    
    # Knowledge queries → Knowledge Worker (RAG + LLM)
    "specs_query": "knowledge_worker",
    "policy_query": "knowledge_worker",
    "competitor_comparison": "knowledge_worker",
    "troubleshooting": "knowledge_worker",
    "prescription_query": "knowledge_worker",
    
    # Unknown → Escalation Worker (gap detection)
    "unknown": "escalation_worker"
}


def route_regex(message: str) -> dict:
    """
    Route using Regex patterns (deterministic, fast).
    
    Args:
        message: User message
        
    Returns:
        {
            "intent": str,
            "worker": str,
            "confidence": float,
            "method": str,
            "matched_pattern": str (optional)
        }
    """
    message_lower = message.lower()
    
    # Try to match patterns
    for intent, pattern_list in PATTERNS.items():
        for pattern in pattern_list:
            if re.search(pattern, message_lower):
                worker = WORKER_ASSIGNMENT.get(intent, "knowledge_worker")
                return {
                    "intent": intent,
                    "worker": worker,
                    "confidence": 1.0,
                    "method": "regex",
                    "matched_pattern": pattern
                }
    
    # No match → Return None (will trigger LLM fallback)
    return None


def route_llm(message: str) -> dict:
    """
    Route using LLM (Gemini 2 Flash) for classification.
    
    This is NOT a fallback - it's the normal classification method
    for queries that don't match Regex patterns.
    
    Args:
        message: User message
        
    Returns:
        {
            "intent": str,
            "worker": str,
            "confidence": float,
            "method": str,
            "error": str (optional)
        }
    """
    # Check if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # No API key → Cannot classify, route to escalation_worker
        return {
            "intent": "unknown",
            "worker": "escalation_worker",
            "confidence": 0.0,
            "method": "error",
            "error": "GEMINI_API_KEY not set"
        }
    
    try:
        import google.generativeai as genai
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prompt for intent classification
        prompt = f"""You are an intent classifier for Even Realities customer support.

User message: "{message}"

Classify the intent into ONE of these categories:
- order_status: User asking about order tracking, delivery status
- return_request: User wants to return/refund/cancel order
- specs_query: User asking about product specifications (battery, price, features)
- policy_query: User asking about policies (return, warranty, shipping)
- competitor_comparison: User comparing with competitors (Meta Ray-Ban, Xreal, etc.)
- troubleshooting: User reporting issues or problems
- jailbreak: User trying to manipulate the system
- prescription_query: User asking about prescription lenses, Rx, diopter, myopia
- unknown: Cannot determine intent

Respond with ONLY the intent name (one word, lowercase).
"""
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 20
            }
        )
        
        intent = response.text.strip().lower()
        
        # Validate intent
        valid_intents = list(PATTERNS.keys()) + ["unknown"]
        if intent not in valid_intents:
            intent = "unknown"
        
        # Assign worker
        worker = WORKER_ASSIGNMENT.get(intent, "knowledge_worker")
        
        return {
            "intent": intent,
            "worker": worker,
            "confidence": 0.8,  # LLM confidence is lower than regex
            "method": "llm"
        }
        
    except ImportError:
        # Library not installed → Cannot classify, route to escalation_worker
        return {
            "intent": "unknown",
            "worker": "escalation_worker",
            "confidence": 0.0,
            "method": "error",
            "error": "google-generativeai not installed"
        }
    except Exception as e:
        # API error → Cannot classify, route to escalation_worker
        return {
            "intent": "unknown",
            "worker": "escalation_worker",
            "confidence": 0.0,
            "method": "error",
            "error": str(e)
        }


def route(message: str, use_llm: bool = True) -> dict:
    """
    Main routing function - Classify and assign to worker.
    
    Strategy:
    1. Try Regex first (fast, deterministic, ~80-90% coverage)
    2. If no Regex match, use LLM to classify (Gemini 2 Flash)
    3. Assign to appropriate worker based on intent
    
    This is NOT a fallback/degradation - LLM is a normal classification method
    for queries that don't match hard-coded patterns.
    
    Args:
        message: User message
        use_llm: Whether to use LLM for classification (default: True)
        
    Returns:
        {
            "intent": str,
            "worker": str,
            "confidence": float,
            "method": str
        }
    """
    # Step 1: Try Regex (fast path)
    result = route_regex(message)
    if result:
        return result
    
    # Step 2: Use LLM to classify (normal path for non-regex queries)
    if use_llm:
        return route_llm(message)
    
    # Step 3: If LLM disabled, classify as unknown → knowledge_worker
    # (This is the actual fallback - when LLM is intentionally disabled)
    return {
        "intent": "unknown",
        "worker": "knowledge_worker",
        "confidence": 0.3,
        "method": "default"
    }


def main():
    """CLI interface for testing"""
    parser = argparse.ArgumentParser(description="Router - Intent Detection")
    parser.add_argument("message", nargs="+", help="User message")
    parser.add_argument("--use-llm", action="store_true", help="Enable LLM fallback")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM fallback")
    
    args = parser.parse_args()
    
    message = " ".join(args.message)
    use_llm = not args.no_llm  # Default: True (unless --no-llm)
    
    result = route(message, use_llm=use_llm)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

