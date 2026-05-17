#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日小古文资源索引器
扫描音频目录和图片目录，建立编号映射索引

用法:
    python indexer.py \
        --audio "D:/Download/百度网盘下载/每日小古文音频" \
        --images "D:/Download/百度网盘下载/图片" \
        --output index.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_audio_filename(filename: str) -> dict | None:
    """解析音频文件名，提取编号、出处、原文。

    支持的格式:
        001《论语》：不怨天，不尤人.mp3
        005.《墨子》：兼相爱，交相利.mp3   (编号后带.)
        032.《世说新语》：...mp3
        365《冬夜读书示子聿》：纸上得来终觉浅，绝知此事要躬行.mp3
        358《诗经》一日不见，如三月兮.mp3   (无冒号)
        360.1 小古文彩蛋.mp3   (跳过)
        凯叔给家长的一封信.mp3  (跳过)
    """
    # 去掉扩展名
    name = Path(filename).stem

    # 排除彩蛋和特殊文件
    if "彩蛋" in name or "凯叔" in name or "家长" in name:
        return None

    # 策略1: 标准格式 001《论语》：不怨天，不尤人
    # 也支持 005.《墨子》：兼相爱，交相利（编号后带.）
    pattern = re.compile(
        r'^(\d+)\.?\s*[《《](.+?)[》》]\s*[：:]\s*(.+)$'
    )
    m = pattern.match(name)
    if m:
        return {
            "id": m.group(1),
            "number": int(m.group(1)),
            "source": m.group(2).strip(),
            "text": m.group(3).strip(),
            "audio_file": filename,
        }

    # 策略2: 无冒号格式，如 358《诗经》一日不见，如三月兮
    pattern2 = re.compile(
        r'^(\d+)\.?\s*[《《](.+?)[》》]\s*(.+)$'
    )
    m2 = pattern2.match(name)
    if m2:
        return {
            "id": m2.group(1),
            "number": int(m2.group(1)),
            "source": m2.group(2).strip(),
            "text": m2.group(3).strip(),
            "audio_file": filename,
        }

    # 策略3: 没有书名号但有数字前缀
    pattern3 = re.compile(r'^(\d+)\.?\s*(.+)$')
    m3 = pattern3.match(name)
    if m3:
        num = int(m3.group(1))
        rest = m3.group(2).strip()
        if "彩蛋" in rest or "凯叔" in rest:
            return None
        # 尝试从中解析出处和原文
        if '：' in rest or ':' in rest:
            parts = re.split(r'[：:]', rest, maxsplit=1)
            return {
                "id": m3.group(1),
                "number": num,
                "source": parts[0].strip().strip('《》'),
                "text": parts[1].strip() if len(parts) > 1 else parts[0].strip(),
                "audio_file": filename,
            }
        return {
            "id": m3.group(1),
            "number": num,
            "source": "",
            "text": rest,
            "audio_file": filename,
        }

    return None


def find_image_folder(images_dir: Path, number: int) -> Path | None:
    """根据编号在图片目录中查找对应的图卡文件夹。"""
    num_str = f"{number:03d}"

    # 策略1: 直接在当前目录下搜索 001xxx、241xxx 等
    for item in images_dir.iterdir():
        if not item.is_dir():
            continue
        # 匹配 001... 或 241... 开头的文件夹名
        if item.name.startswith(num_str):
            return item
        # 匹配 251-300集 这种需要递归
        if item.name in ("251-300集",):
            sub = find_image_folder(item, number)
            if sub:
                return sub

    # 策略2: 递归搜索子目录（如 小古文（1~240）/小古文图卡（1~150）/001...）
    for item in images_dir.rglob("*"):
        if not item.is_dir():
            continue
        if item.name.startswith(num_str):
            return item

    return None


def find_images_in_folder(folder: Path) -> dict:
    """在图卡文件夹中查找大卡、小卡、长文稿。"""
    result = {}
    if not folder.exists():
        return result

    for f in folder.iterdir():
        if not f.is_file():
            continue
        name_lower = f.name.lower()
        if f.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.webp'):
            continue

        if '大卡' in f.name or '大卡' in name_lower:
            result['big_card'] = str(f)
        elif '小卡' in f.name or '小卡' in name_lower:
            result['small_card'] = str(f)
        elif '长文稿' in f.name or '长文稿' in name_lower:
            result['long_text'] = str(f)

    return result


def build_index(audio_dir: Path, images_dir: Path) -> list[dict]:
    """建立完整索引。"""
    entries = []

    # 1. 扫描音频
    audio_files = sorted([f for f in audio_dir.iterdir() if f.suffix.lower() == '.mp3'])

    for af in audio_files:
        parsed = parse_audio_filename(af.name)
        if not parsed:
            print(f"  [跳过] 无法解析: {af.name}")
            continue

        number = parsed['number']
        entry = {
            "id": parsed['id'],
            "number": number,
            "source": parsed['source'],
            "text": parsed['text'],
            "audio_path": str(af),
        }

        # 2. 查找对应图片
        img_folder = find_image_folder(images_dir, number)
        if img_folder:
            images = find_images_in_folder(img_folder)
            if images:
                entry['images'] = images
                entry['images_folder'] = str(img_folder)
            else:
                print(f"  [警告] 找到文件夹但无图片: {img_folder}")
        else:
            print(f"  [缺失] 无图片: {number} {parsed['text']}")

        entries.append(entry)

    # 按编号排序
    entries.sort(key=lambda x: x['number'])
    return entries


def main():
    parser = argparse.ArgumentParser(description="每日小古文资源索引器")
    parser.add_argument("--audio", required=True, help="音频目录路径")
    parser.add_argument("--images", required=True, help="图片目录路径")
    parser.add_argument("--output", default="index.json", help="输出索引文件路径")
    args = parser.parse_args()

    audio_dir = Path(args.audio).expanduser().resolve()
    images_dir = Path(args.images).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not audio_dir.exists():
        print(f"错误: 音频目录不存在: {audio_dir}")
        sys.exit(1)
    if not images_dir.exists():
        print(f"错误: 图片目录不存在: {images_dir}")
        sys.exit(1)

    print(f"扫描音频目录: {audio_dir}")
    print(f"扫描图片目录: {images_dir}")

    index = build_index(audio_dir, images_dir)

    # 统计
    with_audio = len(index)
    with_images = sum(1 for e in index if 'images' in e)
    print(f"\n索引完成: 共 {with_audio} 首")
    print(f"  有音频+图片: {with_images}")
    print(f"  仅有音频: {with_audio - with_images}")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n索引已保存到: {output_path}")


if __name__ == "__main__":
    main()
