#!/usr/bin/env python3
"""
Initialize VS Code user settings for Unsloth configuration.
This script sets default values for unsloth.apiKey and unsloth.contextLength.
"""

import sys
from config import initialize_vscode_settings, get_vscode_user_settings_path


def main():
    """Initialize VS Code user settings."""
    base_url = input("Enter Unsloth base URL (or press Enter for default http://localhost:8888): ").strip() or None
    api_key = input("Enter your Unsloth API key (or press Enter to skip): ").strip() or None
    context_length_input = input("Enter context length (or press Enter for default 32768): ").strip()

    context_length = None
    if context_length_input:
        try:
            context_length = int(context_length_input)
        except ValueError:
            print("Invalid context length, skipping.")

    result = initialize_vscode_settings(
        base_url=base_url,
        api_key=api_key,
        context_length=context_length,
    )

    print(f"\nSettings saved to: {get_vscode_user_settings_path()}")
    for key, status in result.items():
        print(f"  {key}: {status}")


if __name__ == "__main__":
    main()
