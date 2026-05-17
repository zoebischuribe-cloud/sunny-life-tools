#!/usr/bin/env python3
"""
Centralized configuration. Edit this file or set environment variables.

Supported AI backends (all OpenAI-compatible):
  MiniMax     → https://platform.minimaxi.com
  DeepSeek    → https://platform.deepseek.com
  OpenAI      → https://platform.openai.com
  Groq        → https://console.groq.com
  SiliconFlow → https://siliconflow.cn
  Moonshot    → https://platform.moonshot.cn
  Zhipu       → https://open.bigmodel.cn
  Qwen        → https://dashscope.aliyun.com
  Local LLM   → http://localhost:11434/v1 (Ollama) / http://localhost:1234/v1 (LM Studio)
"""
import os
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
RECIPES_JSON = BASE_DIR / "recipes.json"
HISTORY_FILE = BASE_DIR / "history.json"
STATE_FILE = BASE_DIR / "state.json"

# ============================================================
# AI Backend — 选一个，设环境变量即可
# ============================================================
# 格式: 提供商名 → { base_url, 默认模型, 获取API Key的链接 }
AI_PROVIDERS = {
    "minimax": {
        "base_url": "https://api.minimaxi.com/v1",
        "default_model": "MiniMax-M2.7",
        "key_url": "https://platform.minimaxi.com/user-center/payment/token-plan",
        "note": "性价比高，中文理解好，思考链输出",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
        "key_url": "https://platform.deepseek.com/api_keys",
        "note": "国产性价比之王，代码能力强",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "key_url": "https://platform.openai.com/api-keys",
        "note": "综合能力最强，英文内容质量高",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.1-8b-instant",
        "key_url": "https://console.groq.com/keys",
        "note": "极速推理，免费额度慷慨",
    },
    "siliconflow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "default_model": "Qwen/Qwen2.5-7B-Instruct",
        "key_url": "https://siliconflow.cn/models",
        "note": "国产多模型平台，免费额度",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "moonshot-v1-8k",
        "key_url": "https://platform.moonshot.cn/console/api-keys",
        "note": "长文本能力强，128K上下文",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-4-flash",
        "key_url": "https://open.bigmodel.cn/usercenter/apikeys",
        "note": "清华智谱，国产老牌",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyun.com/compatible-mode/v1",
        "default_model": "qwen-turbo",
        "key_url": "https://dashscope.console.aliyun.com/apiKey",
        "note": "阿里通义千问，生态完善",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "default_model": "qwen2.5:7b",
        "key_url": None,
        "note": "本地运行，零成本，完全离线",
    },
}

# --- 环境变量读取（优先级：环境变量 > 默认值） ---
AI_PROVIDER = os.environ.get("RECIPE_AI_PROVIDER", "minimax")
AI_BASE_URL = os.environ.get(
    "RECIPE_AI_URL",
    AI_PROVIDERS.get(AI_PROVIDER, AI_PROVIDERS["minimax"])["base_url"]
)
AI_API_KEY = os.environ.get("RECIPE_AI_KEY", "")
AI_MODEL = os.environ.get(
    "RECIPE_AI_MODEL",
    AI_PROVIDERS.get(AI_PROVIDER, AI_PROVIDERS["minimax"])["default_model"]
)

# --- 飞书 / WeChat Push ---
PUSH_BACKEND = os.environ.get("RECIPE_PUSH_BACKEND", "feishu")

# 飞书群机器人 webhook
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")

# WeCom酱 — 注册企业微信 → 创建应用 → 获取三参数
WECOM_CORPID = os.environ.get("WECOM_CORPID", "")
WECOM_AGENTID = os.environ.get("WECOM_AGENTID", "")
WECOM_SECRET = os.environ.get("WECOM_SECRET", "")

# WxPusher (备选) — https://wxpusher.zjiecode.com/
WXPUSHER_TOKEN = os.environ.get("WXPUSHER_TOKEN", "")
WXPUSHER_TOPIC_ID = os.environ.get("WXPUSHER_TOPIC_ID", "")

# PushPlus (收费, 保留兼容)
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")

# Server酱
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")

# --- Proxy ---
HTTP_PROXY = os.environ.get("http_proxy") or "http://127.0.0.1:7890"
PROXIES = {"http": HTTP_PROXY, "https": HTTP_PROXY}

# --- Schedule ---
PUSH_HOUR = int(os.environ.get("RECIPE_PUSH_HOUR", "10"))
