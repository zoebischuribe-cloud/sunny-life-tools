#!/usr/bin/env python3
"""
Daily English MVP — AI-powered English lesson push to Feishu.

Based on Daily English Vocab skill (forkercat) + MiniMax generation.
12-category rotation, two-part lesson: Small Talk + Themed Vocabulary.

Usage:
  python daily_english.py           # Full run (AI + push)
  python daily_english.py --dry     # Dry run (no push)
  python daily_english.py --mock    # Rule-based fallback (no AI API)
"""
import json, re, random, sys
import requests
from datetime import datetime
from pathlib import Path

from config import (
    STATE_FILE, AI_BASE_URL, AI_API_KEY, AI_MODEL, AI_PROVIDER,
    FEISHU_WEBHOOK, LEVEL, PROXIES,
)

# ── 12-Category Rotation (from Daily English Vocab) ──

CATEGORIES = [
    {"id": 1,  "emoji": "🍔", "name": "Food & Drinks",       "cn": "饮食",    "topics": "食材、调味料、烹饪方式、餐厅用语"},
    {"id": 2,  "emoji": "🏥", "name": "Body & Health",       "cn": "健康",    "topics": "身体部位、症状、看病、健身"},
    {"id": 3,  "emoji": "🏠", "name": "Home & Living",       "cn": "居家",    "topics": "家具、家电、清洁、维修"},
    {"id": 4,  "emoji": "👔", "name": "Work & Office",       "cn": "职场",    "topics": "会议、邮件、同事交流、面试"},
    {"id": 5,  "emoji": "🏋️", "name": "Fitness & Sports",    "cn": "运动",   "topics": "健身器材、运动项目、肌肉群、健身房"},
    {"id": 6,  "emoji": "🛒", "name": "Grocery Shopping",    "cn": "购物",    "topics": "蔬菜水果、肉类、日用品、结账"},
    {"id": 7,  "emoji": "🚗", "name": "Transportation",      "cn": "出行",    "topics": "驾驶、加油站、修车、路标"},
    {"id": 8,  "emoji": "🐱", "name": "Pets & Animals",      "cn": "宠物",    "topics": "品种、行为、宠物医院、宠物用品"},
    {"id": 9,  "emoji": "🧹", "name": "Daily Chores",        "cn": "家务",    "topics": "洗衣、做饭、打扫、垃圾分类"},
    {"id": 10, "emoji": "🎮", "name": "Entertainment",       "cn": "娱乐",    "topics": "游戏、电影、音乐、社交活动"},
    {"id": 11, "emoji": "💰", "name": "Finance",             "cn": "理财",    "topics": "股票、银行、税务、保险"},
    {"id": 12, "emoji": "🌤️", "name": "Weather & Nature",    "cn": "天气",   "topics": "天气现象、自然灾害、地形、植物"},
]

LEVEL_HINTS = {
    "beginner":     "目标用户是小学生或英语零基础。用最简单的词汇（500-1500词），短句，中文解释要详细。",
    "intermediate": "目标用户是初高中生。使用日常口语+常见词汇（1500-4000词），加入一些地道表达。",
    "advanced":     "目标用户是大学生或职场人。使用学术/商务词汇（4000+词），加入习语、俚语、文化背景。",
}

# ── State Management ──

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"currentCategory": 0, "daysOnCategory": 0, "lastRun": "", "wordsUsed": []}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def advance_category(state):
    """Rotate to next category every 2 days."""
    state["daysOnCategory"] = state.get("daysOnCategory", 0) + 1
    if state["daysOnCategory"] >= 2:
        state["currentCategory"] = (state.get("currentCategory", 0) + 1) % len(CATEGORIES)
        state["daysOnCategory"] = 0
        state["wordsUsed"] = []
    state["lastRun"] = datetime.now().strftime("%Y-%m-%d")
    return state

# ── AI Generation ──

def generate_with_ai(category, state):
    """Use LLM to generate today's English lesson."""
    cat = CATEGORIES[category]
    used = state.get("wordsUsed", [])
    level_hint = LEVEL_HINTS.get(LEVEL, LEVEL_HINTS["intermediate"])

    system_prompt = (
        "你是一位热情的美国英语老师。每天给中国学生推送一节微型英语课。\n"
        f"{level_hint}\n"
        "风格要求：友好、有趣、带emoji、手机阅读友好（短行、清晰分段）。\n"
        "中文解释用简体中文。优先美式拼写和发音。\n\n"
        "返回纯JSON（不要markdown代码块）：\n"
        "{\n"
        '  "scene": "今天的口语使用场景(中文10字内)",\n'
        '  "phrase": "今日地道口语(英文)",\n'
        '  "phrase_meaning": "口语中文意思",\n'
        '  "variations": ["变体1", "变体2"],\n'
        '  "responses": ["地道回法1(中英对照)", "地道回法2(中英对照)"],\n'
        '  "vocab": [\n'
        '    {"word": "单词", "ipa": "/IPA/", "meaning": "中文意思",\n'
        '     "example": "英文例句", "example_cn": "例句翻译", "tip": "记忆技巧或易混提示"},\n'
        '    ...(3-5个词)\n'
        '  ]\n'
        "}"
    )

    user_prompt = (
        f"今天是{datetime.now().strftime('%Y年%m月%d日')}。\n"
        f"今日主题类别：{cat['emoji']} {cat['name']}（{cat['cn']}）\n"
        f"子话题范围：{cat['topics']}\n"
        f"最近用过的词汇(避免重复)：{', '.join(used) if used else '无'}\n"
        "请生成今日英语课程内容。"
    )

    try:
        resp = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.9,
                "max_tokens": 800,
            },
            proxies=PROXIES,
            timeout=45,
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        # Strip think tags (MiniMax) and code fences
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'```(?:json)?\s*\n?', '', content)
        content = re.sub(r'\n?```', '', content)
        # Try to find the outermost JSON object
        jm = re.search(r'\{.*\}', content, re.DOTALL)
        if jm:
            try:
                return json.loads(jm.group(0))
            except json.JSONDecodeError:
                # Fix common JSON issues
                raw = jm.group(0)
                raw = re.sub(r',\s*}', '}', raw)  # trailing comma before }
                raw = re.sub(r',\s*]', ']', raw)  # trailing comma before ]
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
    except Exception as e:
        print(f"  AI generation failed: {e}")
    return None

# ── Rule-Based Fallback ──

FALLBACK_PHRASES = {
    "beginner": {
        "scene": "在学校和同学打招呼", "phrase": "How are you doing?", "phrase_meaning": "你怎么样？",
        "variations": ["How's it going?", "What's up?"],
        "responses": ["Pretty good, thanks! (挺好的，谢谢！)", "Not much, you? (没啥，你呢？)"],
    },
    "intermediate": {
        "scene": "周一早上在茶水间碰到同事", "phrase": "How was your weekend? Do anything fun?",
        "phrase_meaning": "周末过得怎么样？有什么好玩的事吗？",
        "variations": ["Good weekend?", "What'd you get up to this weekend?"],
        "responses": ["Not bad! Just took it easy. (还行，就休息了)", "Yeah! Went hiking. (去了爬山！)"],
    },
    "advanced": {
        "scene": "和外国同事讨论项目进展", "phrase": "Where do we stand on the Q2 deliverables?",
        "phrase_meaning": "我们Q2交付物的进展如何？",
        "variations": ["What's the status on Q2?", "How are we tracking for Q2?"],
        "responses": ["We're on track to hit the deadline. (按计划能赶上截止日期)", "Running a bit behind, but we'll catch up. (有点落后但能赶上)"],
    },
}

FALLBACK_VOCAB = {
    1: [{"word": "recipe", "ipa": "/ˈresəpi/", "meaning": "食谱", "example": "Can you share the recipe?", "example_cn": "能分享一下食谱吗？", "tip": "注意发音：re-ci-pe，不是 re-cipe"}],
    2: [{"word": "symptom", "ipa": "/ˈsɪmptəm/", "meaning": "症状", "example": "What are your symptoms?", "example_cn": "你有什么症状？", "tip": "p不发音，类似 psychology"}],
    3: [{"word": "appliance", "ipa": "/əˈplaɪəns/", "meaning": "家用电器", "example": "The kitchen appliance broke.", "example_cn": "厨房电器坏了。", "tip": "apply(应用)+ance→应用到生活=电器"}],
    4: [{"word": "deadline", "ipa": "/ˈdedlaɪn/", "meaning": "截止日期", "example": "The deadline is Friday.", "example_cn": "截止日期是周五。", "tip": "dead(死)+line(线)→死线=截止日"}],
    5: [{"word": "workout", "ipa": "/ˈwɜːrkaʊt/", "meaning": "锻炼", "example": "I had a great workout.", "example_cn": "我锻炼得很好。", "tip": "work out作动词，workout作名词"}],
    6: [{"word": "produce", "ipa": "/ˈproʊduːs/", "meaning": "农产品", "example": "The produce section is over there.", "example_cn": "农产品区在那边。", "tip": "作名词读PROduce，作动词读proDUCE"}],
    7: [{"word": "commute", "ipa": "/kəˈmjuːt/", "meaning": "通勤", "example": "My commute takes an hour.", "example_cn": "我通勤要一小时。", "tip": "com(一起)+mute(变化)→来回移动"}],
    8: [{"word": "breed", "ipa": "/briːd/", "meaning": "品种", "example": "What breed is your dog?", "example_cn": "你的狗是什么品种？", "tip": "breed作名词=品种，作动词=繁殖"}],
    9: [{"word": "laundry", "ipa": "/ˈlɔːndri/", "meaning": "洗衣", "example": "I need to do laundry.", "example_cn": "我得洗衣服了。", "tip": "do laundry=洗衣服，laundromat=自助洗衣店"}],
    10:[{"word": "binge-watch", "ipa": "/bɪndʒ wɒtʃ/", "meaning": "刷剧", "example": "I binge-watched the whole season.", "example_cn": "我一口气刷了一整季。", "tip": "binge=狂吃/狂做，binge-watch=追剧"}],
    11:[{"word": "budget", "ipa": "/ˈbʌdʒɪt/", "meaning": "预算", "example": "We need to stick to the budget.", "example_cn": "我们得按预算来。", "tip": "作名词=预算，作动词=精打细算"}],
    12:[{"word": "drizzle", "ipa": "/ˈdrɪzəl/", "meaning": "毛毛雨", "example": "It's just a drizzle, no need for an umbrella.", "example_cn": "只是毛毛雨，不用打伞。", "tip": "drizzle=小雨，pour=倾盆大雨，shower=阵雨"}],
}

def generate_fallback(category, state):
    """Rule-based fallback when AI unavailable."""
    cat = CATEGORIES[category]
    phrase = FALLBACK_PHRASES.get(LEVEL, FALLBACK_PHRASES["intermediate"])

    # Pick 3 vocab words from the category's fallback + extras
    base_word = FALLBACK_VOCAB.get(category, FALLBACK_VOCAB[1])
    # Add generic words by level
    extras = {
        "beginner": [{"word": "hello", "ipa": "/həˈloʊ/", "meaning": "你好", "example": "Hello, how are you?", "example_cn": "你好，你好吗？", "tip": "最基础的问候语"}],
        "intermediate": [{"word": "basically", "ipa": "/ˈbeɪsɪkli/", "meaning": "基本上", "example": "Basically, it's that simple.", "example_cn": "基本上就这么简单。", "tip": "口语高频词，用来总结"}],
        "advanced": [{"word": "nuance", "ipa": "/ˈnuːɑːns/", "meaning": "细微差别", "example": "There's a subtle nuance in meaning.", "example_cn": "意思上有微妙的差别。", "tip": "源自法语，表示细微差异"}],
    }
    vocab = base_word + extras.get(LEVEL, extras["intermediate"])
    # Avoid repeats
    used = set(state.get("wordsUsed", []))
    vocab = [v for v in vocab if v["word"] not in used][:3]

    return {
        "scene": phrase["scene"],
        "phrase": phrase["phrase"],
        "phrase_meaning": phrase["phrase_meaning"],
        "variations": phrase["variations"],
        "responses": phrase["responses"],
        "vocab": vocab,
    }

# ── Format Message for Feishu ──

def format_message(lesson, category, state):
    """Build Feishu card JSON from lesson data."""
    cat = CATEGORIES[category]
    today = datetime.now().strftime("%Y-%m-%d")

    vocab_lines = []
    for i, v in enumerate(lesson.get("vocab", []), 1):
        vocab_lines.append(
            f"**{i}. {v['word']}** {v.get('ipa', '')}\n"
            f"　{v.get('meaning', '')}\n"
            f"　🗨️ {v.get('example', '')}\n"
            f"　（{v.get('example_cn', '')}）\n"
            f"　💡 {v.get('tip', '')}"
        )

    content = (
        f"**🗣️ 今日口语**\n\n"
        f"场景：{lesson.get('scene', '')}\n"
        f"💬 \"{lesson.get('phrase', '')}\"\n"
        f"（{lesson.get('phrase_meaning', '')}）\n\n"
        f"**变体：**\n"
        + "".join(f"• {v}\n" for v in lesson.get("variations", [])) + "\n"
        f"**地道回法：**\n"
        + "".join(f"• {r}\n" for r in lesson.get("responses", [])) + "\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📚 今日词汇** | {cat['emoji']} {cat['name']}\n\n"
        + "\n".join(vocab_lines)
    )

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"📖 每日英语 | {today}"},
                "template": "blue"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": content}},
            ]
        }
    }

    # Add YouGlish pronunciation link for the main phrase
    if lesson.get("phrase"):
        phrase_encoded = lesson["phrase"].replace(" ", "+")
        card["card"]["elements"].append({"tag": "hr"})
        card["card"]["elements"].append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": "🔊 听发音示范 (YouGlish)"},
                "type": "primary",
                "url": f"https://youglish.com/pronounce/{phrase_encoded}/english/us"
            }]
        })

    return card

# ── Push to Feishu ──

def push_to_feishu(card, dry=False):
    if not FEISHU_WEBHOOK:
        print("  飞书 webhook 未配置, 跳过推送")
        return False
    if dry:
        print("  [DRY RUN] 跳过推送")
        return True
    try:
        r = requests.post(FEISHU_WEBHOOK, json=card, proxies=PROXIES, timeout=15)
        data = r.json()
        code = data.get("code", -1)
        print(f"  飞书: code={code} {data.get('msg', '')}")
        return code == 0
    except Exception as e:
        print(f"  飞书 error: {e}")
        return False

# ── Main ──

def main():
    dry = "--dry" in sys.argv
    mock = "--mock" in sys.argv

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 每日英语启动")
    print(f"  提供商: {AI_PROVIDER} | 模型: {AI_MODEL} | 难度: {LEVEL}")

    # 1. Load and rotate state
    state = load_state()
    state = advance_category(state)
    cat = CATEGORIES[state["currentCategory"]]
    print(f"\n--- 今日主题: {cat['name']}（{cat['cn']}）[{cat['id']}/12] ---")
    print(f"  子话题: {cat['topics']}")

    # 2. Generate lesson
    print("\n--- 生成课程 ---")
    lesson = None
    if AI_API_KEY and not mock:
        print(f"  调用 {AI_PROVIDER} 生成...")
        lesson = generate_with_ai(state["currentCategory"], state)

    if not lesson:
        print("  使用规则引擎生成...")
        lesson = generate_fallback(state["currentCategory"], state)

    if not lesson:
        print("  生成失败")
        sys.exit(1)

    print(f"  口语: {lesson.get('phrase', '')[:50]}")
    print(f"  词汇数: {len(lesson.get('vocab', []))}")

    # Track used words
    for v in lesson.get("vocab", []):
        if v["word"] not in state["wordsUsed"]:
            state["wordsUsed"].append(v["word"])
    save_state(state)

    # 3. Format and push
    print("\n--- 推送 ---")
    card = format_message(lesson, state["currentCategory"], state)
    ok = push_to_feishu(card, dry=dry)

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'完成' if ok or dry else '推送失败'}")
    return 0 if (ok or dry) else 1


if __name__ == "__main__":
    sys.exit(main())
