#!/usr/bin/env python3
"""
Daily English config — same multi-provider architecture as daily-recipe-push.
Set environment variables or edit defaults below.
"""
import os
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = BASE_DIR / "english_state.json"

# --- AI Backend (OpenAI-compatible, 9 providers) ---
AI_PROVIDERS = {
    "minimax":    {"base_url": "https://api.minimaxi.com/v1",        "model": "MiniMax-M2.7",   "key_url": "https://platform.minimaxi.com/user-center/payment/token-plan"},
    "deepseek":   {"base_url": "https://api.deepseek.com/v1",        "model": "deepseek-chat",   "key_url": "https://platform.deepseek.com/api_keys"},
    "openai":     {"base_url": "https://api.openai.com/v1",          "model": "gpt-4o-mini",     "key_url": "https://platform.openai.com/api-keys"},
    "groq":       {"base_url": "https://api.groq.com/openai/v1",     "model": "llama-3.1-8b-instant", "key_url": "https://console.groq.com/keys"},
    "siliconflow":{"base_url": "https://api.siliconflow.cn/v1",      "model": "Qwen/Qwen2.5-7B-Instruct", "key_url": "https://siliconflow.cn/models"},
    "moonshot":   {"base_url": "https://api.moonshot.cn/v1",         "model": "moonshot-v1-8k",  "key_url": "https://platform.moonshot.cn/console/api-keys"},
    "zhipu":      {"base_url": "https://open.bigmodel.cn/api/paas/v4","model": "glm-4-flash",    "key_url": "https://open.bigmodel.cn/usercenter/apikeys"},
    "qwen":       {"base_url": "https://dashscope.aliyun.com/compatible-mode/v1","model": "qwen-turbo","key_url": "https://dashscope.console.aliyun.com/apiKey"},
    "ollama":     {"base_url": "http://localhost:11434/v1",          "model": "qwen2.5:7b",     "key_url": None},
}

AI_PROVIDER = os.environ.get("ENGLISH_AI_PROVIDER", "minimax")
AI_BASE_URL = os.environ.get("ENGLISH_AI_URL", AI_PROVIDERS.get(AI_PROVIDER, AI_PROVIDERS["minimax"])["base_url"])
AI_API_KEY = os.environ.get("ENGLISH_AI_KEY", os.environ.get("RECIPE_AI_KEY", ""))
AI_MODEL = os.environ.get("ENGLISH_AI_MODEL", AI_PROVIDERS.get(AI_PROVIDER, AI_PROVIDERS["minimax"])["model"])

# --- 飞书 Push ---
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", os.environ.get("ENGLISH_FEISHU_WEBHOOK", ""))

# --- Difficulty Level ---
LEVEL = os.environ.get("ENGLISH_LEVEL", "intermediate")  # beginner | intermediate | advanced

# --- Proxy ---
HTTP_PROXY = os.environ.get("http_proxy") or "http://127.0.0.1:7890"
PROXIES = {"http": HTTP_PROXY, "https": HTTP_PROXY}

# --- Schedule ---
PUSH_HOUR = int(os.environ.get("ENGLISH_PUSH_HOUR", "8"))
