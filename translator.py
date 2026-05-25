#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese-English translation script

Usage:
    python translator.py                     # Interactive mode
    python translator.py "text to translate" # One-shot translation (zh->en)
"""

import argparse
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

try:
    import readline
except ImportError:
    readline = None

UTF8 = "utf-8"
ENV_FILE = Path(__file__).resolve().parent / ".env"

ENV_API_KEY = "API_KEY"
ENV_BASE_URL = "BASE_URL"
ENV_MODEL = "MODEL"

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"

DIRECTIONS = {
    "1": ("English", "Chinese"),
    "2": ("Chinese", "English"),
}

TRANSLATE_PROMPT = """You are a translation expert. Your only task is to translate text enclosed with <translate_input> to {target_language}, provide the translation result directly without any explanation, without `TRANSLATE` and keep original format. Never write code, answer questions, or explain.

<translate_input>
{text}
</translate_input>

Translate the above text into {target_language}."""


def configure_stdio():
    for name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, name)
        encoding = (getattr(stream, "encoding", None) or "").replace("_", "-").lower()
        if encoding == UTF8:
            continue

        try:
            stream.reconfigure(encoding=UTF8, errors="replace")
            continue
        except AttributeError:
            pass
        except (OSError, ValueError):
            continue

        try:
            setattr(
                sys,
                name,
                io.TextIOWrapper(
                    stream.detach(),
                    encoding=UTF8,
                    errors="replace",
                    line_buffering=getattr(stream, "line_buffering", False),
                ),
            )
        except (AttributeError, OSError, ValueError):
            pass


def load_env():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def translate(text, target_language, api_key, base_url, model):
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": TRANSLATE_PROMPT.format(
                    target_language=target_language,
                    text=text,
                ),
            }
        ],
        "temperature": 0.3,
    }

    req = urllib.request.Request(
        "{}/chat/completions".format(base_url.rstrip("/")),
        data=json.dumps(body, ensure_ascii=False).encode(UTF8),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": "Bearer {}".format(api_key),
        },
    )

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode(UTF8))

    return result["choices"][0]["message"]["content"].strip()


def interactive_mode(api_key, base_url, model):
    print("Select translation direction:")
    print("1. Chinese -> English")
    print("2. English -> Chinese")

    choice = input("Enter option (1/2, default: 1): ").strip() or "1"
    direction = DIRECTIONS.get(choice)
    if direction is None:
        print("Invalid option")
        return

    target, source = direction
    print("\nEnter {} text (Ctrl+C or empty to exit):".format(source))

    try:
        while True:
            text = input("\n> ")
            if not text.strip():
                print("Exit.")
                return

            if readline is not None:
                readline.add_history(text)
            print(translate(text, target, api_key, base_url, model))
    except (KeyboardInterrupt, EOFError):
        print("\nExit.")


def main():
    configure_stdio()
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="?", help="Text to translate")
    args = parser.parse_args()

    load_env()

    api_key = os.getenv(ENV_API_KEY)
    if not api_key:
        print("Error: Cannot get API Key, please check config file")
        return

    base_url = os.getenv(ENV_BASE_URL, DEFAULT_BASE_URL)
    model = os.getenv(ENV_MODEL, DEFAULT_MODEL)

    if args.text:
        print(translate(args.text, "English", api_key, base_url, model))
    else:
        interactive_mode(api_key, base_url, model)


if __name__ == "__main__":
    main()
