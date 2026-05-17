#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用 Webhook 推送脚本
支持：企业微信(wechat)、飞书(feishu)、钉钉(dingtalk)

用法:
    python scripts/push.py \
        --webhook "$WEBHOOK_URL" \
        --type wechat \
        --title "每日小古文 · 第42集" \
        --content-file today.md
"""

import argparse
import json
import sys

import requests


def push_wechat(webhook_url: str, title: str, content: str):
    """企业微信机器人 - Markdown 消息。"""
    # 企业微信限制：markdown 内容最长 4096 字节
    full = f"## {title}\n\n{content}"
    if len(full.encode("utf-8")) > 4000:
        full = full[:3500] + "\n\n...(内容过长，已截断)"

    payload = {
        "msgtype": "markdown",
        "markdown": {"content": full},
    }
    resp = requests.post(webhook_url, json=payload, timeout=30)
    return resp.json()


def push_feishu(webhook_url: str, title: str, content: str):
    """飞书机器人 - 交互式卡片消息。"""
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
    resp = requests.post(webhook_url, json=payload, timeout=30)
    return resp.json()


def push_dingtalk(webhook_url: str, title: str, content: str):
    """钉钉机器人 - Markdown 消息。"""
    payload = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": f"## {title}\n\n{content}"},
    }
    resp = requests.post(webhook_url, json=payload, timeout=30)
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="推送 Markdown 到 IM 机器人")
    parser.add_argument("--webhook", required=True, help="Webhook URL")
    parser.add_argument("--type", choices=["wechat", "feishu", "dingtalk"], default="wechat",
                        help="机器人类型 (默认: wechat)")
    parser.add_argument("--title", required=True, help="消息标题")
    parser.add_argument("--content-file", required=True, help="Markdown 内容文件路径")
    args = parser.parse_args()

    with open(args.content_file, "r", encoding="utf-8") as f:
        content = f.read()

    if args.type == "wechat":
        result = push_wechat(args.webhook, args.title, content)
    elif args.type == "feishu":
        result = push_feishu(args.webhook, args.title, content)
    else:
        result = push_dingtalk(args.webhook, args.title, content)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 检查是否成功
    errcode = result.get("errcode")
    code = result.get("code")
    errmsg = result.get("errmsg", "")

    if errcode is not None and errcode != 0:
        print(f"推送失败: {errmsg}", file=sys.stderr)
        sys.exit(1)
    if code is not None and code != 0:
        print(f"推送失败: {result}", file=sys.stderr)
        sys.exit(1)

    print("推送成功")


if __name__ == "__main__":
    main()
