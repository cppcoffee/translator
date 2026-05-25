# Translator

A Chinese-English translation tool using OpenAI-compatible APIs.

## Features

- Chinese → English translation
- English → Chinese translation

## Requirements

No external dependencies required. Uses Python standard library only.

Python 3.6+ is required.

## Installation

```bash
git clone <repo-url>
cd translator
```

## Configuration

Edit `.env` file with your API settings. Supports OpenAI-compatible APIs:

**OpenAI:**
```env
API_KEY=sk-xxx
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4o
```

**DeepSeek:**
```env
API_KEY=sk-xxx
BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat
```

**Other compatible providers** (Anthropic, local LLMs, etc.) work similarly.

## Usage

Run the script:

```bash
python translator.py
```

Follow the prompts to select translation direction and input your text.

## Example

```
Select translation direction:
1. Chinese -> English
2. English -> Chinese

Enter option (1/2, default: 1): 1

Enter Chinese text (Ctrl+C or empty to exit):

> 你好，世界
Hello, world

> 今天天气怎么样
How's the weather today

>
Exit.
```

## License

MIT
