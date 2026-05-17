#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日小古文推送生成器

用法:
    python generate.py --index index.json --day today --output today.md
    python generate.py --index index.json --number 42 --output today.md
    python generate.py --index index.json --random --output today.md
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path


def load_index(index_path: Path) -> list[dict]:
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def select_by_day(index: list[dict], year: int | None = None, month: int | None = None, day: int | None = None, base_date: datetime | None = None) -> dict:
    """按天数循环选择。base_date 指定后，从该日期起每天顺序播放。"""
    now = datetime.now()
    y = year or now.year
    m = month or now.month
    d = day or now.day
    target = datetime(y, m, d)

    if base_date:
        delta = (target - base_date).days
        idx = delta % len(index)
    else:
        # 兼容旧逻辑：按一年中的第几天
        day_of_year = target.timetuple().tm_yday
        idx = (day_of_year - 1) % len(index)
    return index[idx]


def select_by_number(index: list[dict], number: int) -> dict | None:
    """按编号选择。"""
    for entry in index:
        if entry['number'] == number:
            return entry
    return None


def select_random(index: list[dict], history_path: Path | None = None) -> dict:
    """随机选择，优先选近期未播放过的。"""
    recently_played = set()
    if history_path and history_path.exists():
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
            # 取最近30条
            for h in history[-30:]:
                recently_played.add(h.get('number'))
        except Exception:
            pass

    candidates = [e for e in index if e['number'] not in recently_played]
    if not candidates:
        candidates = index

    return random.choice(candidates)


def generate_push(entry: dict, grade: str = "elementary") -> str:
    """生成推送文案。"""
    num = entry['number']
    source = entry['source']
    text = entry['text']
    audio = entry.get('audio_path', '')
    images = entry.get('images', {})
    big_card = images.get('big_card', '')
    small_card = images.get('small_card', '')
    long_text = images.get('long_text', '')

    lines = [
        f"📜 每日小古文 · 第{num}集",
        "",
        f"**出处**：{source}",
        f"**原文**：{text}",
        "",
    ]

    # 图片
    if big_card:
        lines.append(f"![大卡]({big_card})")
        lines.append("")

    if long_text:
        lines.append(f"![长文稿]({long_text})")
        lines.append("")

    # 音频提示
    if audio:
        lines.append(f"🎧 [点击收听讲解音频](file://{audio})")
        lines.append("")

    # 思考/背诵提示
    lines.extend([
        "---",
        "📝 今日任务",
        "1. 大声朗读原文3遍",
        "2. 理解意思后能用自己的话讲给家人听",
        "3. 想一想：生活中什么时候可以用到这句话？",
        "",
        "---",
        "📋 家长备注",
        f"- 本集编号：{num}",
        f"- 图片文件夹：{entry.get('images_folder', '无')}",
        f"- 音频文件：{audio}",
    ])

    return "\n".join(lines)


def record_history(entry: dict, history_path: Path):
    """记录播放历史。"""
    history = []
    if history_path.exists():
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            pass

    history.append({
        "number": entry['number'],
        "text": entry['text'],
        "time": datetime.now().isoformat(),
    })

    # 只保留最近90条
    history = history[-90:]

    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="每日小古文推送生成器")
    parser.add_argument("--index", default="index.json", help="索引文件路径")
    parser.add_argument("--output", "-o", help="输出Markdown文件路径")
    parser.add_argument("--day", choices=["today", "yesterday", "tomorrow"], default="today",
                        help="选择哪一天 (today/yesterday/tomorrow)")
    parser.add_argument("--number", type=int, help="指定编号")
    parser.add_argument("--random", action="store_true", help="随机选择")
    parser.add_argument("--history", default=".history.json", help="历史记录文件")
    parser.add_argument("--grade", default="elementary", choices=["elementary", "junior_high"],
                        help="目标年级")
    parser.add_argument("--base-date", help="基准日期 YYYY-MM-DD，从该日期起第1天开始顺序播放")
    args = parser.parse_args()

    index_path = Path(args.index).expanduser().resolve()
    if not index_path.exists():
        print(f"错误: 索引文件不存在: {index_path}")
        print("请先运行 indexer.py 建立索引:")
        print("  python indexer.py --audio <音频目录> --images <图片目录>")
        sys.exit(1)

    index = load_index(index_path)
    if not index:
        print("错误: 索引为空")
        sys.exit(1)

    # 选择条目
    if args.number:
        entry = select_by_number(index, args.number)
        if not entry:
            print(f"错误: 找不到编号 {args.number}")
            sys.exit(1)
    elif args.random:
        history_path = Path(args.history).expanduser().resolve()
        entry = select_random(index, history_path)
    else:
        offset = {"today": 0, "yesterday": -1, "tomorrow": 1}[args.day]
        now = datetime.now()
        target = datetime.fromordinal(now.toordinal() + offset)
        base_date = None
        if args.base_date:
            try:
                base_date = datetime.strptime(args.base_date, "%Y-%m-%d")
            except ValueError:
                print(f"错误: --base-date 格式应为 YYYY-MM-DD，例如 2026-05-15")
                sys.exit(1)
        entry = select_by_day(index, target.year, target.month, target.day, base_date)

    # 生成
    output = generate_push(entry, args.grade)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output, encoding='utf-8')
        print(f"推送已保存到: {out_path}")
    else:
        print(output)

    # 记录历史
    history_path = Path(args.history).expanduser().resolve()
    record_history(entry, history_path)


if __name__ == "__main__":
    main()
