#!/usr/bin/env python3
"""
Escalation Worker - Learning Loop System

Purpose:
1. Detect gaps (unanswerable questions, security threats)
2. Store escalation cases temporarily
3. Generate daily reports for Rosen
4. Support reverse injection (Rosen's answer → KB)

Learning Loop:
    User Query → Gap Detected → Store Case → Daily Report → Rosen Answers → Inject to KB
    
Usage:
    # Detect and store escalation
    python3 escalation_worker.py store "User asked: X" "jailbreak" "external"
    
    # Generate daily report
    python3 escalation_worker.py report --date 2026-03-13
    
    # Inject Rosen's answer to KB
    python3 escalation_worker.py inject <case_id> "Answer: Y" --tier 2
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

# Escalation storage directory
ESCALATION_DIR = Path(__file__).parent.parent / "escalations"
ESCALATION_DIR.mkdir(exist_ok=True)

# Knowledge base directory
KB_DIR = Path(__file__).parent.parent / "knowledge"

# Configuration directory
CONFIG_DIR = Path(__file__).parent.parent / "config"


def get_rosen_feishu_id() -> str:
    """Load Rosen's Feishu ID from config/channels.json."""
    config_file = CONFIG_DIR / "channels.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("rosen_contact", {}).get("feishu_id", "ou_xxx")
        except Exception:
            pass
    return "ou_xxx"


def generate_case_id() -> str:
    """
    Generate unique case ID.
    
    Format: ESC-YYYYMMDD-HHMMSS-microseconds
    Example: ESC-20260313-231700-123456
    """
    now = datetime.now(timezone.utc)
    return now.strftime("ESC-%Y%m%d-%H%M%S-") + str(now.microsecond)


def store_case(message: str, intent: str, surface: str, metadata: Dict = None, case_type: str = None, severity: str = None) -> str:
    """
    Store escalation case to temporary storage.
    
    Args:
        message: User message
        intent: Intent from Router
        surface: external or internal
        metadata: Additional metadata (sender_id, channel, etc.)
        
    Returns:
        str: Case ID
    """
    case_id = generate_case_id()
    
    # Build case data
    case = {
        "case_id": case_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "intent": intent,
        "surface": surface,
        "status": "pending",  # pending / resolved / injected
        "metadata": metadata or {}
    }
    
    # Determine escalation type (explicit params override auto-detection)
    if case_type:
        case["type"] = case_type
    elif intent == "jailbreak":
        case["type"] = "security"
    elif intent == "unknown":
        case["type"] = "gap"
    else:
        case["type"] = "other"
    
    if severity:
        case["severity"] = severity
    elif intent == "jailbreak":
        case["severity"] = "high"
    elif intent == "unknown":
        case["severity"] = "medium"
    else:
        case["severity"] = "low"
    
    # Save to file
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    case_file = ESCALATION_DIR / f"{today}.jsonl"
    
    with open(case_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(case, ensure_ascii=False) + '\n')
    
    return case_id


def load_cases(date: str = None) -> List[Dict]:
    """
    Load escalation cases from storage.
    
    Args:
        date: Date string (YYYY-MM-DD). If None, load today's cases.
        
    Returns:
        List of case dicts
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    case_file = ESCALATION_DIR / f"{date}.jsonl"
    
    if not case_file.exists():
        return []
    
    cases = []
    with open(case_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    
    return cases


def generate_report(date: str = None) -> str:
    """
    Generate daily escalation report for Rosen.
    
    Args:
        date: Date string (YYYY-MM-DD). If None, use today.
        
    Returns:
        str: Markdown report
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    cases = load_cases(date)
    
    if not cases:
        return f"# Escalation Report - {date}\n\nNo escalations today. 🎉"
    
    # Group by type
    by_type = {"security": [], "gap": [], "other": []}
    for case in cases:
        case_type = case.get("type", "other")
        by_type[case_type].append(case)
    
    # Build report
    report = f"# Escalation Report - {date}\n\n"
    report += f"**Total Cases:** {len(cases)}\n\n"
    
    # Security threats
    if by_type["security"]:
        report += "## 🚨 Security Threats\n\n"
        for case in by_type["security"]:
            report += f"### {case['case_id']}\n"
            report += f"- **Message:** {case['message']}\n"
            report += f"- **Intent:** {case['intent']}\n"
            report += f"- **Surface:** {case['surface']}\n"
            report += f"- **Time:** {case['timestamp']}\n"
            report += f"- **Status:** {case['status']}\n\n"
    
    # Knowledge gaps
    if by_type["gap"]:
        report += "## 📚 Knowledge Gaps\n\n"
        for case in by_type["gap"]:
            report += f"### {case['case_id']}\n"
            report += f"- **Message:** {case['message']}\n"
            report += f"- **Intent:** {case['intent']}\n"
            report += f"- **Surface:** {case['surface']}\n"
            report += f"- **Time:** {case['timestamp']}\n"
            report += f"- **Status:** {case['status']}\n\n"
            report += "**Suggested Action:**\n"
            report += "1. Provide answer below\n"
            report += "2. Specify target KB file (e.g., kb_policies.md)\n"
            report += "3. System will auto-inject to KB\n\n"
    
    # Other escalations
    if by_type["other"]:
        report += "## 📋 Other Escalations\n\n"
        for case in by_type["other"]:
            report += f"### {case['case_id']}\n"
            report += f"- **Message:** {case['message']}\n"
            report += f"- **Intent:** {case['intent']}\n"
            report += f"- **Surface:** {case['surface']}\n"
            report += f"- **Time:** {case['timestamp']}\n"
            report += f"- **Status:** {case['status']}\n\n"
    
    return report


def inject_to_kb(case_id: str, answer: str, kb_file: str, tier: int = 2) -> bool:
    """
    Inject Rosen's answer to knowledge base.
    
    Args:
        case_id: Case ID
        answer: Rosen's answer
        kb_file: Target KB file (e.g., kb_policies.md)
        tier: Tier level (default: 2)
        
    Returns:
        bool: Success or not
    """
    # Find the case
    cases = []
    for date_file in ESCALATION_DIR.glob("*.jsonl"):
        cases.extend(load_cases(date_file.stem))
    
    case = None
    for c in cases:
        if c["case_id"] == case_id:
            case = c
            break
    
    if not case:
        print(f"Error: Case {case_id} not found")
        return False
    
    # Build Q&A entry
    qa_entry = f"\n\n## {case['message']}\n\n{answer}\n\n*Source: Escalation {case_id} on {case['timestamp'][:10]}*\n"
    
    # Append to KB file
    kb_path = KB_DIR / kb_file
    
    if not kb_path.exists():
        print(f"Error: KB file {kb_file} not found")
        return False
    
    with open(kb_path, 'a', encoding='utf-8') as f:
        f.write(qa_entry)
    
    # Update case status
    date = case['timestamp'][:10]
    case_file = ESCALATION_DIR / f"{date}.jsonl"
    
    # Read all cases
    with open(case_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Update the case
    updated_lines = []
    for line in lines:
        if line.strip():
            c = json.loads(line)
            if c["case_id"] == case_id:
                c["status"] = "injected"
                c["injected_to"] = kb_file
                c["injected_at"] = datetime.now(timezone.utc).isoformat()
            updated_lines.append(json.dumps(c, ensure_ascii=False) + '\n')
    
    # Write back
    with open(case_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"✅ Injected to {kb_file}")
    print(f"✅ Case {case_id} marked as resolved")
    
    return True


def send_report_to_rosen(report: str, date: str):
    """
    Send daily report to Rosen via Feishu.
    
    Args:
        report: Markdown report
        date: Date string
    """
    # TODO: Implement Feishu message sending
    # For now, just print to console
    print("=" * 80)
    print(f"DAILY REPORT TO ROSEN ({date})")
    print("=" * 80)
    print(report)
    print("=" * 80)
    rosen_id = get_rosen_feishu_id()
    print(f"\nTo send to Rosen: Use feishu_im_user_message tool")
    print(f"Target: {rosen_id}")


def main():
    parser = argparse.ArgumentParser(description="Escalation Worker")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Store command
    store_parser = subparsers.add_parser("store", help="Store escalation case")
    store_parser.add_argument("message", help="User message")
    store_parser.add_argument("intent", help="Intent from Router")
    store_parser.add_argument("surface", choices=["external", "internal"], help="Surface type")
    store_parser.add_argument("--metadata", help="Additional metadata (JSON)")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate daily report")
    report_parser.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    report_parser.add_argument("--send", action="store_true", help="Send to Rosen")
    
    # Inject command
    inject_parser = subparsers.add_parser("inject", help="Inject answer to KB")
    inject_parser.add_argument("case_id", help="Case ID")
    inject_parser.add_argument("answer", help="Rosen's answer")
    inject_parser.add_argument("--kb-file", required=True, help="Target KB file")
    inject_parser.add_argument("--tier", type=int, default=2, help="Tier level")
    
    args = parser.parse_args()
    
    if args.command == "store":
        metadata = json.loads(args.metadata) if args.metadata else {}
        case_id = store_case(args.message, args.intent, args.surface, metadata)
        print(f"✅ Stored case: {case_id}")
    
    elif args.command == "report":
        report = generate_report(args.date)
        if args.send:
            send_report_to_rosen(report, args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        else:
            print(report)
    
    elif args.command == "inject":
        success = inject_to_kb(args.case_id, args.answer, args.kb_file, args.tier)
        if not success:
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

