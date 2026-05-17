#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地定时推送入口（Windows 计划任务专用）。
支持企业微信 / 飞书 / 钉钉 Webhook。

用法:
    set WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
    python scripts/local_push.py morning   # 6:30 科普
    python scripts/local_push.py evening   # 21:00 小古文 + 本地图片

环境变量:
    WEBHOOK_URL   必填  机器人 Webhook 地址
    WEBHOOK_TYPE  可选  wechat(默认) / feishu / dingtalk
"""

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests

# ============================================================
# 路径配置
# ============================================================

REPO_ROOT = Path(__file__).parent.parent.resolve()
SCIENCE_SCRIPT = REPO_ROOT / "daily-science-kids" / "scripts" / "generate.py"
GUGUWEN_SCRIPT = REPO_ROOT / "daily-guguwen" / "scripts" / "generate.py"
GUGUWEN_INDEX = REPO_ROOT / "daily-guguwen" / "index.json"


# ============================================================
# Webhook 推送
# ============================================================

def push_text(webhook_url: str, webhook_type: str, title: str, content: str):
    """推送 Markdown 文字消息。"""
    full = f"## {title}\n\n{content}"
    if webhook_type == "wechat":
        # 企业微信限制 4096 字节
        if len(full.encode("utf-8")) > 4000:
            full = full[:3500] + "\n\n...(内容过长，已截断)"
        payload = {"msgtype": "markdown", "markdown": {"content": full}}
    elif webhook_type == "feishu":
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": "blue",
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": content}}
                ],
            },
        }
    else:  # dingtalk
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": full},
        }

    resp = requests.post(webhook_url, json=payload, timeout=30)
    result = resp.json()
    _check_result(webhook_type, result)
    return result


def push_image_wechat(webhook_url: str, image_path: Path):
    """企业微信：直接发送 base64 图片（本地文件无需上传第三方）。"""
    data = _read_image_bytes(image_path)
    b64 = base64.b64encode(data).decode("ascii")
    md5 = hashlib.md5(data).hexdigest()
    payload = {"msgtype": "image", "image": {"base64": b64, "md5": md5}}
    resp = requests.post(webhook_url, json=payload, timeout=60)
    result = resp.json()
    _check_result("wechat", result)
    return result


def _read_image_bytes(image_path: Path, max_bytes: int = 2_000_000) -> bytes:
    """读取图片，超过限制时自动压缩。"""
    raw = image_path.read_bytes()
    if len(raw) <= max_bytes:
        return raw

    # 尝试用 Pillow 压缩
    try:
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(raw))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 先尝试降低质量
        for quality in range(85, 20, -15):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            if buf.tell() <= max_bytes:
                return buf.getvalue()

        # 再降低分辨率
        while True:
            w, h = img.size
            if w <= 400 and h <= 400:
                break
            img = img.resize((max(w // 2, 400), max(h // 2, 400)), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=60)
            if buf.tell() <= max_bytes:
                return buf.getvalue()
    except Exception as e:
        print(f"[警告] 图片压缩失败 ({e})，将尝试直接发送原图。若超过 2MB 企业微信会拒收。")

    return raw


def _check_result(webhook_type: str, result: dict):
    """检查返回结果是否成功。"""
    errcode = result.get("errcode")
    code = result.get("code")
    errmsg = result.get("errmsg", "")

    if errcode is not None and errcode != 0:
        raise RuntimeError(f"企业微信推送失败: {errmsg} (errcode={errcode})")
    if code is not None and code != 0:
        raise RuntimeError(f"飞书推送失败: {result}")
    if webhook_type == "dingtalk" and result.get("errcode") != 0:
        raise RuntimeError(f"钉钉推送失败: {result}")


# ============================================================
# 内容生成
# ============================================================

def generate_science(output_path: Path) -> str:
    """生成每日科普内容，返回 Markdown 文本。"""
    subprocess.run(
        [sys.executable, str(SCIENCE_SCRIPT), "--grade", "elementary", "-o", str(output_path)],
        check=True,
        cwd=str(REPO_ROOT),
    )
    return output_path.read_text(encoding="utf-8")


def generate_guguwen(output_path: Path) -> dict:
    """生成每日小古文内容。返回 {"text": 文案, "images": [路径列表]}。"""
    # 先运行 generate.py 记录历史
    subprocess.run(
        [sys.executable, str(GUGUWEN_SCRIPT), "--index", str(GUGUWEN_INDEX),
         "--day", "today", "--base-date", "2026-05-15", "-o", str(output_path)],
        check=True,
        cwd=str(REPO_ROOT),
    )

    # 从索引获取今日条目，提取本地图片路径
    with open(GUGUWEN_INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)

    now = datetime.now()
    day_of_year = now.timetuple().tm_yday
    entry = index[(day_of_year - 1) % len(index)]

    num = entry["number"]
    source = entry["source"]
    text = entry["text"]

    lines = [
        f"📜 每日小古文 · 第{num}集",
        "",
        f"**出处**：{source}",
        f"**原文**：{text}",
        "",
        "---",
        "📝 今日任务",
        "1. 大声朗读原文3遍",
        "2. 理解意思后能用自己的话讲给家人听",
        "3. 想一想：生活中什么时候可以用到这句话？",
    ]

    images = []
    imgs = entry.get("images", {})
    for key in ("big_card", "long_text"):
        p = imgs.get(key, "")
        if p and Path(p).exists():
            images.append(Path(p))

    return {"text": "\n".join(lines), "images": images}


# ============================================================
# 主流程
# ============================================================

def run_morning(webhook_url: str, webhook_type: str):
    """早上科普推送。"""
    print(f"[{datetime.now():%H:%M:%S}] 开始生成科普推送...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        tmp_path = Path(f.name)

    try:
        content = generate_science(tmp_path)
        day_of_year = datetime.now().timetuple().tm_yday
        title = f"📚 每日科普 · 第{day_of_year}天"
        print(f"[{datetime.now():%H:%M:%S}] 正在发送文字消息...")
        push_text(webhook_url, webhook_type, title, content)
        print(f"[{datetime.now():%H:%M:%S}] 科普推送完成")
    finally:
        tmp_path.unlink(missing_ok=True)


def run_evening(webhook_url: str, webhook_type: str):
    """晚上小古文推送（含图片）。"""
    print(f"[{datetime.now():%H:%M:%S}] 开始生成小古文推送...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        tmp_path = Path(f.name)

    try:
        data = generate_guguwen(tmp_path)
        day_of_year = datetime.now().timetuple().tm_yday
        title = f"📜 每日小古文 · 第{day_of_year}天"

        print(f"[{datetime.now():%H:%M:%S}] 正在发送文字消息...")
        push_text(webhook_url, webhook_type, title, data["text"])

        if data["images"]:
            if webhook_type == "wechat":
                for img_path in data["images"]:
                    print(f"[{datetime.now():%H:%M:%S}] 正在发送图片: {img_path.name} ...")
                    push_image_wechat(webhook_url, img_path)
            else:
                print(f"[{datetime.now():%H:%M:%S}] [提示] {webhook_type} 暂不支持直接发送本地图片，"
                      f"已跳过 {len(data['images'])} 张图片。如需发图请改用企业微信，"
                      f"或手动查看本地文件夹。")
        else:
            print(f"[{datetime.now():%H:%M:%S}] [提示] 未找到本地图片")

        print(f"[{datetime.now():%H:%M:%S}] 小古文推送完成")
    finally:
        tmp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="本地定时教育推送")
    parser.add_argument("mode", choices=["morning", "evening"], help="morning=科普, evening=小古文")
    parser.add_argument("--webhook", help="Webhook URL（也可通过环境变量 WEBHOOK_URL 设置）")
    parser.add_argument("--type", dest="webhook_type", choices=["wechat", "feishu", "dingtalk"],
                        help="机器人类型（也可通过环境变量 WEBHOOK_TYPE 设置）")
    args = parser.parse_args()

    webhook_url = args.webhook or os.environ.get("WEBHOOK_URL", "").strip()
    webhook_type = args.webhook_type or os.environ.get("WEBHOOK_TYPE", "wechat").strip().lower()

    if not webhook_url:
        print("错误: 未设置 WEBHOOK_URL。请通过 --webhook 参数或 WEBHOOK_URL 环境变量指定。", file=sys.stderr)
        sys.exit(1)

    try:
        if args.mode == "morning":
            run_morning(webhook_url, webhook_type)
        else:
            run_evening(webhook_url, webhook_type)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
