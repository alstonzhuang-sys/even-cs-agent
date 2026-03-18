#!/usr/bin/env python3
"""
Structured Logger for Even CS Agent

Outputs JSON log lines to stderr (stdout reserved for pipeline output).
"""

import sys
import json
from datetime import datetime, timezone


def log(level: str, component: str, message: str, **extra):
    """
    Write structured log line to stderr.
    
    Args:
        level: DEBUG / INFO / WARN / ERROR
        component: ingress / router / knowledge_worker / escalation_worker / renderer / rate_limiter
        message: Human-readable message
        **extra: Additional fields
    """
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "component": component,
        "msg": message,
    }
    entry.update(extra)
    print(json.dumps(entry, ensure_ascii=False), file=sys.stderr)


def debug(component: str, message: str, **extra):
    log("DEBUG", component, message, **extra)

def info(component: str, message: str, **extra):
    log("INFO", component, message, **extra)

def warn(component: str, message: str, **extra):
    log("WARN", component, message, **extra)

def error(component: str, message: str, **extra):
    log("ERROR", component, message, **extra)
