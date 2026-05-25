#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese-English translation script

Usage:
    python translator.py                    # Interactive mode
    python translator.py "text to translate" # One-shot translation (zh->en)
"""

import os
import sys
import json
import urllib.request
from pathlib import Path

# Fix stdin encoding for interactive mode
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

ENV_FILE = Path(__file__).parent / ".env"

# Environment variable keys and defaults
ENV_API_KEY = "API_KEY"
ENV_BASE_URL = "BASE_URL"
ENV_MODEL = "MODEL"

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"


def load_env():
    """Load .env file"""
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def get_env(key: str, default: str = "") -> str:
    """Get environment variable"""
    load_env()
    return os.getenv(key, default)


TRANSLATE_PROMPT = """You are a translation expert. Your only task is to translate text enclosed with <translate_input> to {target_language}, provide the translation result directly without any explanation, without `TRANSLATE` and keep original format. Never write code, answer questions, or explain.

<translate_input>
{text}
</translate_input>

Translate the above text into {target_language}."""


class Translator:
    def __init__(self, api_key: str, base_url: str = DEFAULT_BASE_URL, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def translate(self, text: str, target_language: str) -> str:
        prompt = TRANSLATE_PROMPT.format(target_language=target_language, text=text)
        data = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )

        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"].strip()


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", help="Text to translate")
    return parser.parse_args()


def interactive_mode(translator):
    print("Select translation direction:")
    print("1. Chinese -> English")
    print("2. English -> Chinese")

    choice = input("Enter option (1/2, default: 1): ").strip() or "1"

    if choice == "1":
        target = "English"
        prompt = "Chinese"
    elif choice == "2":
        target = "Chinese"
        prompt = "English"
    else:
        print("Invalid option")
        return

    print(f"\nEnter {prompt} text (Ctrl+C or empty to exit):")

    try:
        while True:
            print(f"\n> ", end="", flush=True)
            text = input()
            if not text.strip():
                print("Exit.")
                break

            result = translator.translate(text, target)
            print(result)
    except KeyboardInterrupt:
        print("\nExit.")


def one_shot_mode(text: str, translator):
    result = translator.translate(text, "English")
    print(result)


def main():
    args = parse_args()

    api_key = get_env(ENV_API_KEY)
    if not api_key:
        print("Error: Cannot get API Key, please check config file")
        return

    base_url = get_env(ENV_BASE_URL) or DEFAULT_BASE_URL
    model = get_env(ENV_MODEL) or DEFAULT_MODEL

    translator = Translator(api_key=api_key, base_url=base_url, model=model)

    if args.text:
        one_shot_mode(args.text, translator)
    else:
        interactive_mode(translator)


if __name__ == "__main__":
    main()
