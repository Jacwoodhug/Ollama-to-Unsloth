"""
Configuration module: Reads settings from .env and VS Code user settings.
Priority: .env > VS Code user settings > defaults
"""

import json
import os
from pathlib import Path


def get_vscode_user_settings_path() -> Path:
    """Get the path to VS Code user settings.json on Windows."""
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable not set")
    return Path(appdata) / "Code" / "User" / "settings.json"


def read_vscode_user_settings() -> dict:
    """Read VS Code user settings from settings.json."""
    settings_path = get_vscode_user_settings_path()
    if not settings_path.exists():
        return {}
    
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            return settings
    except (json.JSONDecodeError, IOError):
        return {}


# Mapping from environment variable names to VS Code user settings keys
_ENV_TO_VSCODE_KEY: dict[str, str] = {
    "UNSLOTH_BASE_URL": "unsloth.baseUrl",
    "UNSLOTH_API_KEY": "unsloth.apiKey",
    "MODEL_CONTEXT_LENGTH": "unsloth.contextLength",
}


def get_config_value(key: str, default: str = "") -> str:
    """
    Get configuration value with priority: .env > VS Code user settings > default.
    
    Args:
        key: Configuration key (environment variable name)
        default: Default value if not found in .env or VS Code settings
    
    Returns:
        Configuration value or default
    """
    # Priority 1: .env file
    env_value = os.getenv(key)
    if env_value is not None:
        return env_value
    
    # Priority 2: VS Code user settings (using mapped key name)
    vscode_key = _ENV_TO_VSCODE_KEY.get(key)
    if vscode_key is not None:
        vscode_settings = read_vscode_user_settings()
        if vscode_key in vscode_settings:
            return str(vscode_settings[vscode_key])
    
    # Priority 3: Default
    return default


def get_int_config_value(key: str, default: int) -> int:
    """
    Get integer configuration value with priority: .env > VS Code user settings > default.
    
    Args:
        key: Configuration key (environment variable name)
        default: Default value if not found in .env or VS Code settings
    
    Returns:
        Configuration value or default as int
    """
    value = get_config_value(key, str(default))
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# Default values for each VS Code settings key
_VSCODE_DEFAULTS: dict[str, object] = {
    "unsloth.baseUrl": "http://localhost:8888",
    "unsloth.apiKey": "",
    "unsloth.contextLength": 32768,
}


def initialize_vscode_settings(
    base_url: str | None = None,
    api_key: str | None = None,
    context_length: int | None = None,
) -> dict[str, str]:
    """
    Initialize VS Code user settings, only adding keys that are not already set.
    Creates the settings file if it doesn't exist.

    Returns a dict mapping each key to 'added' or 'skipped'.
    """
    settings_path = get_vscode_user_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    existing_settings = read_vscode_user_settings()

    updates: dict[str, object] = {}
    if base_url is not None:
        updates["unsloth.baseUrl"] = base_url
    if api_key is not None:
        updates["unsloth.apiKey"] = api_key
    if context_length is not None:
        updates["unsloth.contextLength"] = context_length

    result: dict[str, str] = {}
    for vscode_key, value in updates.items():
        if vscode_key in existing_settings:
            result[vscode_key] = "skipped"
        else:
            existing_settings[vscode_key] = value
            result[vscode_key] = "added"

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(existing_settings, f, indent=2)

    return result
