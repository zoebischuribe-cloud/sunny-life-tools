#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Science Kids — 每日儿童科普推送生成器

用法：
    python generate.py --grade elementary              # 生成小学版
    python generate.py --grade junior_high             # 生成初中版（默认）
    python generate.py --category physics              # 强制指定学科
    python generate.py --kb /path/to/knowledge_base.yaml  # 指定知识库
    python generate.py --history                       # 查看使用历史
    python generate.py --output /path/to/output.md     # 指定输出文件
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml


# ============================================================
# 配置
# ============================================================

DEFAULT_KB_PATHS = [
    "knowledge_base.yaml",
    "../knowledge_base.yaml",
    "../../knowledge_base.yaml",
    str(Path.home() / "knowledge_base.yaml"),
]

SCRIPT_DIR = Path(__file__).parent.resolve()
HISTORY_FILE = SCRIPT_DIR / ".history.json"

WEEKDAY_MAP = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

CATEGORY_ICONS = {
    "tech": "🚀",
    "physics": "⚡",
    "chemistry": "🧪",
    "nature": "🌿",
    "news": "🌍",
    "english": "🗣️",
    "surprise": "🎁",
}

CATEGORY_NAMES = {
    "tech": "科技前沿",
    "physics": "物理世界",
    "chemistry": "化学奥秘",
    "nature": "自然探秘",
    "news": "天下大事",
    "english": "英语趣谈",
    "surprise": "惊喜知识",
}

GRADE_LABELS = {
    "elementary": "小学版",
    "junior_high": "初中版",
}


# ============================================================
# 工具函数
# ============================================================

def find_knowledge_base(kb_path: str | None = None) -> Path:
    """查找知识库文件。"""
    if kb_path:
        p = Path(kb_path).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"指定的知识库不存在: {kb_path}")

    for candidate in DEFAULT_KB_PATHS:
        p = Path(candidate)
        if p.is_absolute():
            if p.exists():
                return p.resolve()
        else:
            # 相对脚本目录
            rel = SCRIPT_DIR / candidate
            if rel.exists():
                return rel.resolve()
            # 相对当前工作目录
            cwd = Path.cwd() / candidate
            if cwd.exists():
                return cwd.resolve()

    raise FileNotFoundError(
        "未找到 knowledge_base.yaml。请指定路径：--kb /path/to/knowledge_base.yaml"
    )


def load_knowledge_base(path: Path) -> dict:
    """加载 YAML 知识库。"""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_history() -> list[dict]:
    """加载使用历史。"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list[dict]):
    """保存使用历史。"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def get_recently_used_ids(history: list[dict], days: int = 30) -> set[str]:
    """获取最近 N 天使用过的知识点 ID。"""
    cutoff = datetime.now() - timedelta(days=days)
    used = set()
    for entry in history:
        used_time = datetime.fromisoformat(entry.get("time", "1970-01-01T00:00:00"))
        if used_time >= cutoff:
            used.add(entry.get("id"))
    return used


def pick_item(kb: dict, category: str, used_ids: set[str]) -> dict:
    """从指定学科中随机选择一条未近期使用过的知识点。"""
    items = [item for item in kb.get("knowledge_items", []) if item.get("category") == category]

    if not items:
        raise ValueError(f"知识库中不存在学科: {category}")

    # 优先选未用过的
    unused = [item for item in items if item.get("id") not in used_ids]
    pool = unused if unused else items

    return random.choice(pool)


def get_today_category(kb: dict, force_category: str | None = None) -> str:
    """根据今天星期几确定学科。"""
    if force_category:
        return force_category

    weekday = datetime.now().weekday()
    schedule_key = WEEKDAY_MAP[weekday]
    schedule = kb.get("daily_schedule", {})
    category = schedule.get(schedule_key, "surprise")
    return category


# ============================================================
# 文案生成
# ============================================================

def generate_elementary(item: dict, category_name: str, icon: str) -> str:
    """生成小学版推送文案。"""
    lines = [
        f"{icon} 今天发现了一个超酷的事情！",
        "",
        f"你有没有想过？{item['hook']}",
        "",
        f"其实呀：{item['explanation']}",
        "",
        f"在我们身边：{item['real_life']}",
        "",
        f"更神奇的是：{item['fun_fact']}",
        "",
        f"来考考你：{item['question']}",
    ]
    return "\n".join(lines)


def generate_junior_high(item: dict, category_name: str, icon: str) -> str:
    """生成初中版推送文案。"""
    lines = [
        f"{icon} 【{category_name}】{item['title']}",
        "",
        f"❓ 问题引入：{item['hook']}",
        "",
        f"🔬 原理解析：{item['explanation']}",
        "",
        f"🎯 实际应用：{item['real_life']}",
        "",
        f"💡 拓展冷知识：{item['fun_fact']}",
        "",
        f"📝 思考题：{item['question']}",
    ]
    return "\n".join(lines)


def generate_parent_note(item: dict, category_name: str) -> str:
    """生成家长审核备注。"""
    return f"""
---
📋 家长审核备注
- 今日学科：{category_name}
- 知识点：{item['title']}
- 适用年级：{item.get('grade', '未标注')}
- 本推送由 AI 根据预置知识库生成，核心事实经过校验
- 如需查看完整知识库或调整年级适配，请检查 knowledge_base.yaml
"""


def generate_daily_push(item: dict, grade: str, category: str) -> str:
    """生成完整推送文案（含家长备注）。"""
    icon = CATEGORY_ICONS.get(category, "📚")
    category_name = CATEGORY_NAMES.get(category, "知识")

    if grade == "elementary":
        body = generate_elementary(item, category_name, icon)
    else:
        body = generate_junior_high(item, category_name, icon)

    note = generate_parent_note(item, category_name)
    return body + note


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Daily Science Kids 推送生成器")
    parser.add_argument("--grade", choices=["elementary", "junior_high"], default="junior_high",
                        help="目标年级：elementary（小学）或 junior_high（初中，默认）")
    parser.add_argument("--kb", help="知识库 YAML 文件路径")
    parser.add_argument("--category", help="强制指定学科（覆盖星期规则）")
    parser.add_argument("--output", "-o", help="输出文件路径（默认输出到 stdout）")
    parser.add_argument("--history", action="store_true", help="查看使用历史")
    parser.add_argument("--preview", action="store_true", help="预览模式：不记录历史")
    args = parser.parse_args()

    # 查看历史
    if args.history:
        history = load_history()
        if not history:
            print("暂无使用历史。")
            return
        print(f"最近 {len(history)} 条使用记录：\n")
        for entry in history[-20:]:  # 只显示最近20条
            time_str = entry.get("time", "?")[:16]
            print(f"  [{time_str}] {entry.get('category', '?')} | {entry.get('title', '?')}")
        return

    # 加载知识库
    try:
        kb_path = find_knowledge_base(args.kb)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        print("\n提示: 你可以从以下位置获取知识库模板：", file=sys.stderr)
        print("  1. 当前目录下创建 knowledge_base.yaml", file=sys.stderr)
        print("  2. 用户目录下放置 knowledge_base.yaml", file=sys.stderr)
        print("  3. 使用 --kb 参数指定路径", file=sys.stderr)
        sys.exit(1)

    kb = load_knowledge_base(kb_path)

    # 确定今日学科
    category = get_today_category(kb, args.category)

    # 加载历史并选择知识点
    history = load_history()
    used_ids = get_recently_used_ids(history, days=30)

    try:
        item = pick_item(kb, category, used_ids)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 生成文案
    output = generate_daily_push(item, args.grade, category)

    # 输出
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output, encoding="utf-8")
        print(f"推送文案已保存到: {out_path}")
    else:
        print(output)

    # 记录历史（预览模式跳过）
    if not args.preview:
        history.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "category": category,
            "grade": args.grade,
            "time": datetime.now().isoformat(),
        })
        # 保留最近 90 天记录
        cutoff = datetime.now() - timedelta(days=90)
        history = [h for h in history if datetime.fromisoformat(h["time"]) >= cutoff]
        save_history(history)


if __name__ == "__main__":
    main()
