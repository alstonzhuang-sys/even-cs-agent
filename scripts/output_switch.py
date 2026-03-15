#!/usr/bin/env python3
"""
Output Switch - Channel Routing & Configuration

Purpose:
1. Load channel configuration (external/internal)
2. Route output to correct channel
3. Validate configuration on startup

Usage:
    # Verify configuration
    python3 output_switch.py --verify
    
    # Route output
    python3 output_switch.py --channel discord --message "Hello"
    python3 output_switch.py --channel feishu --message "Debug info"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List

# Configuration file path
CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "channels.json"


class ConfigError(Exception):
    """Configuration error"""
    pass


def load_config() -> Dict:
    """
    Load channel configuration from config/channels.json.
    
    Returns:
        dict: Configuration
        
    Raises:
        ConfigError: If configuration is invalid
    """
    if not CONFIG_FILE.exists():
        raise ConfigError(f"Configuration file not found: {CONFIG_FILE}")
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {CONFIG_FILE}: {e}")
    
    # Validate required fields
    if "external" not in config:
        raise ConfigError("Missing 'external' field in configuration")
    if "internal" not in config:
        raise ConfigError("Missing 'internal' field in configuration")
    
    # Validate types
    if not isinstance(config["external"], list):
        raise ConfigError("'external' must be a list")
    if not isinstance(config["internal"], list):
        raise ConfigError("'internal' must be a list")
    
    return config


def get_surface(channel: str, config: Dict = None) -> str:
    """
    Determine surface type (external/internal) for a channel.
    
    Args:
        channel: Channel name (e.g., "discord", "feishu")
        config: Configuration dict (optional, will load if not provided)
        
    Returns:
        str: "external" or "internal"
    """
    if config is None:
        config = load_config()
    
    # Check external channels
    if channel in config["external"]:
        return "external"
    
    # Check internal channels
    if channel in config["internal"]:
        return "internal"
    
    # Fallback (default: external for safety)
    fallback = config.get("fallback", "external")
    print(f"Warning: Unknown channel '{channel}', using fallback: {fallback}", file=sys.stderr)
    return fallback


def get_rosen_contact(config: Dict = None) -> Dict:
    """
    Get Rosen's contact information.
    
    Args:
        config: Configuration dict (optional)
        
    Returns:
        dict: {"feishu_id": "...", "name": "..."}
    """
    if config is None:
        config = load_config()
    
    return config.get("rosen_contact", {
        "feishu_id": "ou_xxx",
        "name": "Rosen"
    })


def verify_config() -> bool:
    """
    Verify configuration is valid.
    
    Returns:
        bool: True if valid, False otherwise
    """
    print("=== Configuration Verification ===\n")
    
    # Check 1: Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print(f"✅ GEMINI_API_KEY: Set ({len(api_key)} chars)")
    else:
        print("❌ GEMINI_API_KEY: Not set")
        print("   Set with: export GEMINI_API_KEY='your_key_here'")
        return False
    
    # Check 2: Configuration file exists
    if CONFIG_FILE.exists():
        print(f"✅ Configuration file: {CONFIG_FILE}")
    else:
        print(f"❌ Configuration file not found: {CONFIG_FILE}")
        print(f"   Create with: mkdir -p {CONFIG_DIR} && touch {CONFIG_FILE}")
        return False
    
    # Check 3: Load and validate configuration
    try:
        config = load_config()
        print(f"✅ Configuration loaded successfully")
    except ConfigError as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Check 4: External channels
    external = config["external"]
    print(f"✅ External channels: {external}")
    
    # Check 5: Internal channels
    internal = config["internal"]
    print(f"✅ Internal channels: {internal}")
    
    # Check 6: Rosen contact
    rosen = config.get("rosen_contact", {})
    if rosen.get("feishu_id") == "ou_xxx":
        print(f"⚠️  Rosen contact: {rosen.get('feishu_id')} (PLACEHOLDER - Replace with actual ID)")
    else:
        print(f"✅ Rosen contact: {rosen.get('feishu_id')} ({rosen.get('name')})")
    
    # Check 7: Fallback
    fallback = config.get("fallback", "external")
    print(f"✅ Fallback surface: {fallback}")
    
    print("\n=== Configuration is valid! ===")
    return True


def route_output(channel: str, message: str, config: Dict = None):
    """
    Route output to the correct channel.
    
    Args:
        channel: Channel name
        message: Message to send
        config: Configuration dict (optional)
    """
    if config is None:
        config = load_config()
    
    surface = get_surface(channel, config)
    
    print(f"Channel: {channel}")
    print(f"Surface: {surface}")
    print(f"Message: {message}")
    
    # TODO: Implement actual channel sending
    # For now, just print
    print(f"\n[Would send to {channel} ({surface})]")


def main():
    parser = argparse.ArgumentParser(description="Output Switch - Channel Routing")
    parser.add_argument("--verify", action="store_true", help="Verify configuration")
    parser.add_argument("--channel", help="Channel name (e.g., discord, feishu)")
    parser.add_argument("--message", help="Message to send")
    parser.add_argument("--get-surface", help="Get surface for a channel")
    
    args = parser.parse_args()
    
    if args.verify:
        success = verify_config()
        sys.exit(0 if success else 1)
    
    elif args.get_surface:
        try:
            surface = get_surface(args.get_surface)
            print(surface)
        except ConfigError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.channel and args.message:
        try:
            route_output(args.channel, args.message)
        except ConfigError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
