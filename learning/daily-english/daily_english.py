#!/usr/bin/env python3
"""
Daily English v2.0 — AI-powered English lesson push to Feishu.

Content sources:
  - 12-category rotation (from Daily English Vocab skill)
  - Wikipedia API (random/featured articles, free, no key)
  - Free Dictionary API (random word with IPA + definitions)

SM-2 Review:
  - Auto-tracks all vocabulary from lessons
  - python daily_english.py --review    # Run spaced repetition review

Usage:
  python daily_english.py              # Full run (AI + push)
  python daily_english.py --dry        # Dry run (no push)
  python daily_english.py --mock       # Rule-based fallback (no AI API)
  python daily_english.py --source wiki  # Force Wikipedia mode
  python daily_english.py --review     # SM-2 review session
"""
import json, re, random, sys
import requests
from datetime import datetime
from pathlib import Path
from sm2 import load_review_state, save_review_state, add_words_batch, add_word, get_due_words, sm2_update, get_stats

from config import (
    STATE_FILE, AI_BASE_URL, AI_API_KEY, AI_MODEL, AI_PROVIDER,
    FEISHU_WEBHOOK, LEVEL, PROXIES,
)

# ── Content Sources ──

def fetch_wikipedia_random():
    """Fetch a random English Wikipedia article summary. Free, no API key."""
    try:
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/random/summary",
            headers={"User-Agent": "DailyEnglishBot/1.0"},
            proxies=PROXIES, timeout=15, allow_redirects=True,
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "title": data.get("title", ""),
                "extract": data.get("extract", "")[:1500],
                "description": data.get("description", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": data.get("thumbnail", {}).get("source", ""),
            }
    except Exception as e:
        print(f"  Wikipedia fetch error: {e}")
    return None

def fetch_wikipedia_featured(date_str=None):
    """Fetch Wikipedia's featured article of the day."""
    if not date_str:
        date_str = datetime.now().strftime("%Y/%m/%d")
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/feed/featured/{date_str}",
            headers={"User-Agent": "DailyEnglishBot/1.0"},
            proxies=PROXIES, timeout=15, allow_redirects=True,
        )
        if r.status_code == 200:
            data = r.json()
            tfa = data.get("tfa", {})
            return {
                "title": tfa.get("titles", {}).get("normalized", ""),
                "extract": tfa.get("extract", "")[:1500],
                "description": tfa.get("description", ""),
                "url": tfa.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": tfa.get("thumbnail", {}).get("source", ""),
            }
    except Exception as e:
        print(f"  Wikipedia featured error: {e}")
    return None

def fetch_random_word():
    """Fetch a random English word from Free Dictionary API."""
    try:
        r = requests.get(
            "https://api.dictionaryapi.dev/api/v2/entries/en/random",
            proxies=PROXIES, timeout=10,
        )
        if r.status_code == 200 and isinstance(r.json(), list):
            entry = r.json()[0]
            word = entry.get("word", "")
            phonetic = entry.get("phonetic", "")
            meanings = entry.get("meanings", [])
            defs = []
            for m in meanings[:2]:
                pos = m.get("partOfSpeech", "")
                for d in m.get("definitions", [])[:2]:
                    defs.append(f"({pos}) {d.get('definition', '')}")
                    if d.get("example"):
                        defs.append(f"  e.g. {d['example']}")
            # Get audio URL
            audio = ""
            for p in entry.get("phonetics", []):
                if p.get("audio"):
                    audio = p["audio"]
                    break
            return {
                "word": word,
                "phonetic": phonetic,
                "definitions": defs[:4],
                "audio": audio,
            }
    except Exception as e:
        print(f"  Dictionary fetch error: {e}")
    return None

# ── 12-Category Rotation ──

CATEGORIES = [
    {"id": 1,  "name": "Food & Drinks",       "cn": "饮食",    "topics": "食材、调味料、烹饪方式、餐厅用语"},
    {"id": 2,  "name": "Body & Health",       "cn": "健康",    "topics": "身体部位、症状、看病、健身"},
    {"id": 3,  "name": "Home & Living",       "cn": "居家",    "topics": "家具、家电、清洁、维修"},
    {"id": 4,  "name": "Work & Office",       "cn": "职场",    "topics": "会议、邮件、同事交流、面试"},
    {"id": 5,  "name": "Fitness & Sports",    "cn": "运动",    "topics": "健身器材、运动项目、肌肉群、健身房"},
    {"id": 6,  "name": "Grocery Shopping",    "cn": "购物",    "topics": "蔬菜水果、肉类、日用品、结账"},
    {"id": 7,  "name": "Transportation",      "cn": "出行",    "topics": "驾驶、加油站、修车、路标"},
    {"id": 8,  "name": "Pets & Animals",      "cn": "宠物",    "topics": "品种、行为、宠物医院、宠物用品"},
    {"id": 9,  "name": "Daily Chores",        "cn": "家务",    "topics": "洗衣、做饭、打扫、垃圾分类"},
    {"id": 10, "name": "Entertainment",       "cn": "娱乐",    "topics": "游戏、电影、音乐、社交活动"},
    {"id": 11, "name": "Finance",             "cn": "理财",    "topics": "股票、银行、税务、保险"},
    {"id": 12, "name": "Weather & Nature",    "cn": "天气",    "topics": "天气现象、自然灾害、地形、植物"},
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
    state["daysOnCategory"] = state.get("daysOnCategory", 0) + 1
    if state["daysOnCategory"] >= 2:
        state["currentCategory"] = (state.get("currentCategory", 0) + 1) % len(CATEGORIES)
        state["daysOnCategory"] = 0
        state["wordsUsed"] = []
    state["lastRun"] = datetime.now().strftime("%Y-%m-%d")
    return state

# ── AI Generation ──

def _call_ai(system_prompt, user_prompt):
    """Generic AI call with MiniMax think-tag handling."""
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
            proxies=PROXIES, timeout=45,
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        content = re.sub(r'```(?:json)?\s*\n?|\n?```', '', content).strip()
        # Try parse JSON
        jm = re.search(r'\{.*\}', content, re.DOTALL)
        if jm:
            raw = jm.group(0)
            try: return json.loads(raw)
            except json.JSONDecodeError:
                raw = re.sub(r',\s*}', '}', raw)
                raw = re.sub(r',\s*]', ']', raw)
                try: return json.loads(raw)
                except json.JSONDecodeError: pass
    except Exception as e:
        print(f"  AI call failed: {e}")
    return None

def generate_vocab_lesson(category_idx, state):
    """Generate 12-theme vocab + small talk lesson (original mode)."""
    cat = CATEGORIES[category_idx]
    used = state.get("wordsUsed", [])
    level_hint = LEVEL_HINTS.get(LEVEL, LEVEL_HINTS["intermediate"])

    system_prompt = (
        "你是一位热情的美国英语老师。每天给中国学生推送一节微型英语课。\n"
        f"{level_hint}\n"
        "风格：友好有趣、带emoji、手机阅读友好（短行清晰分段）。中文解释用简体中文。优先美式拼写。\n\n"
        "返回纯JSON：\n"
        '{"scene":"场景(中文10字内)","phrase":"地道口语(英文)","phrase_meaning":"中文意思",'
        '"variations":["变体1","变体2"],"responses":["回法1(中英)","回法2(中英)"],'
        '"vocab":[{"word":"词","ipa":"/IPA/","meaning":"中文","example":"英文例句",'
        '"example_cn":"翻译","tip":"记忆技巧"}]}'
    )

    user_prompt = (
        f"今天是{datetime.now().strftime('%Y年%m月%d日')}。\n"
        f"主题：{cat['name']}（{cat['cn']}）\n子话题：{cat['topics']}\n"
        f"最近用过(避免)：{', '.join(used) if used else '无'}\n请生成今日英语课。"
    )
    return _call_ai(system_prompt, user_prompt)

def generate_wiki_lesson(wiki_data):
    """Generate a mini English lesson from a Wikipedia article."""
    if not wiki_data:
        return None

    level_hint = LEVEL_HINTS.get(LEVEL, LEVEL_HINTS["intermediate"])

    system_prompt = (
        "你是一位热情的英语阅读老师。你会拿到一篇Wikipedia英文文章摘要，"
        "把它变成一节微型英语阅读课。\n"
        f"{level_hint}\n"
        "返回纯JSON：\n"
        '{"article_title":"原标题","summary_cn":"中文摘要(80字内)",'
        '"key_vocab":[{"word":"词","ipa":"/IPA/","meaning":"中文","sentence":"原文中的句子"}],'
        '"grammar_point":"文章中最值得学的一个语法点(30字内，中英对照)",'
        '"reading_tip":"这篇英语文章的阅读技巧(30字内)"}'
    )

    user_prompt = (
        f"标题：{wiki_data.get('title','')}\n"
        f"英文摘要：{wiki_data.get('extract','')[:1200]}\n"
        f"描述：{wiki_data.get('description','')}\n"
        "请生成英语阅读微课。"
    )
    return _call_ai(system_prompt, user_prompt)

def generate_ted_lesson(wiki_data):
    """Generate a deep TED-style lesson: background + shadowing + grammar + retell."""
    if not wiki_data:
        return None
    level_hint = LEVEL_HINTS.get(LEVEL, LEVEL_HINTS["intermediate"])
    system_prompt = (
        "你是一位TED演讲教练。拿到一篇英文文章后，把它变成一堂完整的英语深度学习课。\n"
        f"{level_hint}\n"
        "返回纯JSON：\n"
        '{"title":"文章标题","background":"背景知识(50字，中英双语)",'
        '"shadowing_text":"选一段100-150词的英文原文(完整段落，适合跟读)",'
        '"shadowing_cn":"跟读段落的中文翻译",'
        '"shadowing_tips":["发音重点1","发音重点2","发音重点3"],'
        '"grammar_deep":"深入讲解一个语法点(连读/弱读/时态/从句，选最有价值的)",'
        '"grammar_example":"语法点的例句(标注音变/连读)",'
        '"retell_prompt":"请用户用自己的话复述这段话(中英提示)",'
        '"culture_note":"文化背景知识(30字)",'
        '"challenge":"今日挑战任务(20字)"}'
    )
    user_prompt = (
        f"标题：{wiki_data.get('title','')}\n"
        f"英文全文：{wiki_data.get('extract','')[:2000]}\n"
        f"描述：{wiki_data.get('description','')}\n"
        "请生成TED风格深度学习课（含跟读段落+语法深度讲解+复述任务）。"
    )
    return _call_ai(system_prompt, user_prompt)

def format_ted_card(lesson, wiki_data):
    """Build TED-style deep learning card for Feishu."""
    today = datetime.now().strftime("%Y-%m-%d")
    shadowing = lesson.get("shadowing_text","")
    tips = "\n".join(f"• {t}" for t in lesson.get("shadowing_tips",[]))
    content = (
        f"**🎤 TED 深度学习**\n\n"
        f"**{wiki_data.get('title','')}**\n"
        f"_{wiki_data.get('description','')}_\n\n"
        f"📖 **背景知识**\n{lesson.get('background','')}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**🗣️ 跟读训练（Repeat 10x）**\n\n"
        f"{shadowing}\n\n"
        f"中文翻译：{lesson.get('shadowing_cn','')}\n\n"
        f"**发音重点：**\n{tips}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**🔍 语法深度讲解**\n{lesson.get('grammar_deep','')}\n"
        f"例句：_{lesson.get('grammar_example','')}_\n\n"
        f"**📝 复述任务**\n{lesson.get('retell_prompt','')}\n\n"
        f"**💡 文化背景**\n{lesson.get('culture_note','')}\n\n"
        f"**🎯 今日挑战**\n{lesson.get('challenge','')}"
    )
    header = f"🎤 TED 英语课 | {today}"
    url = wiki_data.get("url","")
    return _build_card(header, "red", content, url, "📖 阅读全文" if url else "")

def generate_word_lesson(word_data):
    """Generate a word-of-the-day mini lesson."""
    if not word_data:
        return None

    level_hint = LEVEL_HINTS.get(LEVEL, LEVEL_HINTS["intermediate"])

    system_prompt = (
        "你是一位英语词汇老师。根据给定的单词信息，生成一个生动的「每日一词」微型课。\n"
        f"{level_hint}\n"
        "返回纯JSON：\n"
        '{"word":"词","ipa":"/IPA/","meaning_cn":"中文意思",'
        '"memory_hook":"记忆技巧/词根拆解(20字)",'
        '"daily_use":"这个词在日常中的使用场景(20字，中英)",'
        '"collocations":["搭配1(中英)","搭配2(中英)"]}'
    )

    defs_text = "\n".join(word_data.get("definitions", []))
    user_prompt = (
        f"单词：{word_data.get('word','')}\n音标：{word_data.get('phonetic','')}\n"
        f"释义：\n{defs_text}\n请生成每日一词微课。"
    )
    return _call_ai(system_prompt, user_prompt)

# ── Fallback Generators ──

FALLBACK_PHRASES = {
    "beginner": {"scene": "在学校和同学打招呼", "phrase": "How are you doing?",
        "phrase_meaning": "你怎么样？", "variations": ["How's it going?", "What's up?"],
        "responses": ["Pretty good, thanks! (挺好的，谢谢！)", "Not much, you? (没啥，你呢？)"]},
    "intermediate": {"scene": "周一早上在茶水间碰到同事", "phrase": "How was your weekend? Do anything fun?",
        "phrase_meaning": "周末过得怎么样？", "variations": ["Good weekend?", "What'd you get up to?"],
        "responses": ["Not bad! Just took it easy. (还行，就休息了)", "Yeah! Went hiking. (去了爬山！)"]},
    "advanced": {"scene": "和外国同事讨论项目进展", "phrase": "Where do we stand on the Q2 deliverables?",
        "phrase_meaning": "Q2交付物的进展如何？", "variations": ["What's the status on Q2?", "How are we tracking?"],
        "responses": ["We're on track. (按计划进行中)", "Running a bit behind. (稍微落后)"]},
}

FALLBACK_VOCAB = {
    1: [{"word":"recipe","ipa":"/ˈresəpi/","meaning":"食谱","example":"Can you share the recipe?","example_cn":"能分享一下食谱吗？","tip":"注意发音 re-ci-pe"}],
    2: [{"word":"symptom","ipa":"/ˈsɪmptəm/","meaning":"症状","example":"What are your symptoms?","example_cn":"你有什么症状？","tip":"p不发音，类似 psychology"}],
    3: [{"word":"appliance","ipa":"/əˈplaɪəns/","meaning":"家用电器","example":"The appliance broke.","example_cn":"电器坏了。","tip":"apply+ance=应用到生活"}],
    4: [{"word":"deadline","ipa":"/ˈdedlaɪn/","meaning":"截止日期","example":"The deadline is Friday.","example_cn":"截止日期是周五。","tip":"dead+line=死线"}],
    5: [{"word":"workout","ipa":"/ˈwɜːrkaʊt/","meaning":"锻炼","example":"Great workout today!","example_cn":"今天锻炼得真好！","tip":"动词work out，名词workout"}],
    6: [{"word":"produce","ipa":"/ˈproʊduːs/","meaning":"农产品","example":"Produce section is over there.","example_cn":"农产品区在那边。","tip":"名词读PROduce，动词读proDUCE"}],
    7: [{"word":"commute","ipa":"/kəˈmjuːt/","meaning":"通勤","example":"My commute takes an hour.","example_cn":"通勤要一小时。","tip":"com+together+mute=move"}],
    8: [{"word":"breed","ipa":"/briːd/","meaning":"品种","example":"What breed is your dog?","example_cn":"你的狗是什么品种？","tip":"名词=品种，动词=繁殖"}],
    9: [{"word":"laundry","ipa":"/ˈlɔːndri/","meaning":"洗衣","example":"I need to do laundry.","example_cn":"我得洗衣服了。","tip":"do laundry=洗衣服"}],
    10:[{"word":"binge-watch","ipa":"/bɪndʒ wɒtʃ/","meaning":"刷剧","example":"I binge-watched it all.","example_cn":"我一口气全刷完了。","tip":"binge=狂做"}],
    11:[{"word":"budget","ipa":"/ˈbʌdʒɪt/","meaning":"预算","example":"Stick to the budget.","example_cn":"按预算来。","tip":"名词=预算，动词=精打细算"}],
    12:[{"word":"drizzle","ipa":"/ˈdrɪzəl/","meaning":"毛毛雨","example":"Just a drizzle.","example_cn":"只是毛毛雨。","tip":"drizzle小雨 pour大雨"}],
}

def fallback_vocab_lesson(category_idx, state):
    cat = CATEGORIES[category_idx]
    phrase = FALLBACK_PHRASES.get(LEVEL, FALLBACK_PHRASES["intermediate"])
    base = FALLBACK_VOCAB.get(category_idx, FALLBACK_VOCAB[1])
    extras = {
        "beginner": [{"word":"hello","ipa":"/həˈloʊ/","meaning":"你好","example":"Hello!","example_cn":"你好！","tip":"最基础问候"}],
        "intermediate": [{"word":"basically","ipa":"/ˈbeɪsɪkli/","meaning":"基本上","example":"Basically, yes.","example_cn":"基本上是的。","tip":"口语高频总结词"}],
        "advanced": [{"word":"nuance","ipa":"/ˈnuːɑːns/","meaning":"细微差别","example":"There's a nuance.","example_cn":"有微妙的差别。","tip":"法语借词"}],
    }
    vocab = base + extras.get(LEVEL, extras["intermediate"])
    used = set(state.get("wordsUsed", []))
    vocab = [v for v in vocab if v["word"] not in used][:3]
    return {"scene": phrase["scene"], "phrase": phrase["phrase"],
            "phrase_meaning": phrase["phrase_meaning"], "variations": phrase["variations"],
            "responses": phrase["responses"], "vocab": vocab}

# ── Feishu Formatting ──

def format_vocab_card(lesson, category_idx):
    cat = CATEGORIES[category_idx]
    today = datetime.now().strftime("%Y-%m-%d")
    vl = "\n".join(
        f"**{i+1}. {v.get('word','')}** {v.get('ipa','')}\n"
        f"　{v.get('meaning','')}\n"
        f"　🗨️ {v.get('example','')}（{v.get('example_cn','')}）\n"
        f"　💡 {v.get('tip','')}"
        for i, v in enumerate(lesson.get("vocab", []))
    )
    content = (
        f"**🗣️ 今日口语**\n\n"
        f"场景：{lesson.get('scene','')}\n"
        f"💬 \"{lesson.get('phrase','')}\"\n"
        f"（{lesson.get('phrase_meaning','')}）\n\n"
        f"**变体：**\n" + "".join(f"• {v}\n" for v in lesson.get("variations",[])) + "\n"
        f"**回法：**\n" + "".join(f"• {r}\n" for r in lesson.get("responses",[])) + "\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📚 今日词汇** | {cat['name']}\n\n{vl}"
    )
    header = f"📖 每日英语 | {today}"
    url = None
    if lesson.get("phrase"):
        url = f"https://youglish.com/pronounce/{lesson['phrase'].replace(' ','+')}/english/us"
    return _build_card(header, "blue", content, url, "🔊 听发音 (YouGlish)")

def format_wiki_card(lesson, wiki_data):
    today = datetime.now().strftime("%Y-%m-%d")
    vl = "\n".join(
        f"**{i+1}. {v.get('word','')}** {v.get('ipa','')}\n"
        f"　{v.get('meaning','')}\n"
        f"　📖 {v.get('sentence','')}"
        for i, v in enumerate(lesson.get("key_vocab", []))
    )
    content = (
        f"**📰 今日阅读** | Wikipedia\n\n"
        f"**{wiki_data.get('title','')}**\n"
        f"_{wiki_data.get('description','')}_\n\n"
        f"📝 **中文摘要**\n{lesson.get('summary_cn','')}\n\n"
        f"🔍 **语法点睛**\n{lesson.get('grammar_point','')}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📚 重点词汇**\n\n{vl}\n\n"
        f"💡 **阅读技巧**\n{lesson.get('reading_tip','')}"
    )
    header = f"📰 英语阅读 | {today}"
    url = wiki_data.get("url", "")
    return _build_card(header, "green", content, url, "📖 阅读全文 (Wikipedia)" if url else "")

def format_word_card(lesson):
    today = datetime.now().strftime("%Y-%m-%d")
    coll = "\n".join(f"• {c}" for c in lesson.get("collocations", []))
    content = (
        f"**🔤 每日一词**\n\n"
        f"## {lesson.get('word','')}\n"
        f"*{lesson.get('ipa','')}*\n\n"
        f"**{lesson.get('meaning_cn','')}**\n\n"
        f"🧠 **记忆技巧**\n{lesson.get('memory_hook','')}\n\n"
        f"💬 **使用场景**\n{lesson.get('daily_use','')}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📎 常用搭配**\n{coll}"
    )
    header = f"🔤 每日一词 | {today}"
    return _build_card(header, "yellow", content, None, "")

def _build_card(header_title, header_color, content, link_url, btn_text):
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": header_title}, "template": header_color},
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
        }
    }
    if link_url and btn_text:
        card["card"]["elements"].append({"tag": "hr"})
        card["card"]["elements"].append({
            "tag": "action",
            "actions": [{"tag": "button", "text": {"tag": "plain_text", "content": btn_text}, "type": "primary", "url": link_url}]
        })
    return card

# ── Push ──

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

# ── SM-2 Review ──

def _generate_review_quiz(review_words):
    """Generate a review quiz using AI based on SM-2 due words."""
    words_text = "\n".join(
        f"- {w['word']} ({w.get('ipa','')}): {w.get('meaning','')}"
        + (f" e.g. {w.get('example','')}" if w.get('example') else "")
        for w in review_words
    )
    system_prompt = (
        "你是英语复习教练。根据待复习词汇生成一套快速自测题。\n"
        "返回纯JSON：\n"
        '{"title":"今日复习","words":['
        '{"word":"词","hint":"提示(不直接给答案)","answer":"中文意思","example":"例句"},...],'
        '"tip":"复习建议(20字)"}'
    )
    user_prompt = f"待复习词汇：\n{words_text}\n请生成复习自测题。"
    return _call_ai(system_prompt, user_prompt)

def format_review_card(lesson, review_words):
    """Build SM-2 review card for Feishu."""
    today = datetime.now().strftime("%Y-%m-%d")
    words_section = ""
    if lesson and "words" in lesson:
        words_section = "\n".join(
            f"**{i+1}. {w.get('word','')}**\n"
            f"　💬 {w.get('hint','')}\n"
            f"　<font color='grey'>答案：{w.get('answer','')}</font>\n"
            f"　📖 {w.get('example','')}"
            for i, w in enumerate(lesson.get("words", []))
        )
    else:
        words_section = "\n".join(
            f"**{i+1}. {w.get('word','')}** {w.get('ipa','')}\n"
            f"　{w.get('meaning','')}"
            for i, w in enumerate(review_words)
        )

    content = (
        f"**🔄 间隔复习** | SM-2 算法\n\n"
        f"{words_section}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📊 自评标准：**\n"
        f"• 5分 = 秒懂，脱口而出\n"
        f"• 4分 = 想了一下，答对了\n"
        f"• 3分 = 有点卡，但最终对了\n"
        f"• 2分 = 答错了，看到答案就想起\n"
        f"• 1分 = 答错了，看到答案也没印象\n"
        f"• 0分 = 完全不记得\n\n"
        f"💡 {lesson.get('tip','') if lesson else '诚实自评，效果翻倍！'}"
    )
    return _build_card(f"🔄 英语复习 | {today}", "purple", content, None, "")

# ── Main ──

def main():
    dry = "--dry" in sys.argv
    mock = "--mock" in sys.argv
    source = "review" if "--review" in sys.argv else (
        "ted" if "--source" in sys.argv and "ted" in sys.argv else (
        "wiki" if "--source" in sys.argv and "wiki" in sys.argv else (
        "word" if "--source" in sys.argv and "word" in sys.argv else "auto")))

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 每日英语 v2.0 启动")
    print(f"  提供商: {AI_PROVIDER} | 模型: {AI_MODEL} | 难度: {LEVEL} | 源: {source}")

    state = load_state()

    # ── Mode A: TED Deep Lesson ──
    if source == "ted":
        print("\n--- TED 深度学习模式 ---")
        wiki = fetch_wikipedia_random()
        if not wiki:
            wiki = fetch_wikipedia_featured()
        if wiki:
            print(f"  文章: {wiki['title'][:60]}")
            lesson = None
            if AI_API_KEY and not mock:
                print(f"  调用 {AI_PROVIDER} 生成TED深度学习课...")
                lesson = generate_ted_lesson(wiki)
            if not lesson:
                extract = wiki.get("extract","")[:300]
                lesson = {
                    "title": wiki.get("title","Untitled"),
                    "background": f"This is about {wiki.get('title','')}. {wiki.get('description','')}",
                    "shadowing_text": extract[:200] if extract else "No text available for shadowing.",
                    "shadowing_cn": "请自行翻译跟读段落",
                    "shadowing_tips": ["注意重音和语调", "连读时辅音+元音要自然", "模仿原声的节奏感"],
                    "grammar_deep": "注意段落中的时态一致性（tense consistency），同一段落内时态通常保持一致",
                    "grammar_example": extract[:80] if extract else "",
                    "retell_prompt": "请用自己的话复述这段文字的主要观点（中英文均可尝试）",
                    "culture_note": "这篇内容反映了英语世界的知识传统",
                    "challenge": "大声朗读跟读段落10遍，录下来自己听",
                }
            card = format_ted_card(lesson, wiki)
            # Track key vocab
            rstate = load_review_state()
            words = re.findall(r'[A-Z][a-z]{5,20}', wiki.get("extract","")[:300])
            for w in set(words[:5]):
                rstate = add_word(rstate, w.lower(), "来自TED深度课", "", "")
            save_review_state(rstate)
        else:
            print("  Wikipedia 不可用，回退口语模式")
            source = "auto"

    # ── Mode B: Wikipedia Reading ──
    if source == "wiki":
        print("\n--- Wikipedia 阅读模式 ---")
        wiki = fetch_wikipedia_random()
        if not wiki:
            wiki = fetch_wikipedia_featured()
        if wiki:
            print(f"  文章: {wiki['title'][:60]}")
            lesson = None
            if AI_API_KEY and not mock:
                print(f"  调用 {AI_PROVIDER} 生成阅读课...")
                lesson = generate_wiki_lesson(wiki)
            if not lesson:
                title = wiki.get("title","Untitled")
                desc = wiki.get("description","")
                extract = wiki.get("extract","")[:200]
                lesson = {
                    "article_title": title,
                    "summary_cn": f"这是一篇关于{title}的英文Wikipedia文章。{desc}",
                    "key_vocab": [{"word": w.split("(")[0].strip()[:20], "ipa": "", "meaning": "请查阅词典", "sentence": extract[:80]}
                        for w in re.findall(r'[A-Z][a-z]{4,15}', extract)[:3]],
                    "grammar_point": "观察文章中的时态和语态使用",
                    "reading_tip": "先读首段了解大意，再逐段精读",
                }
            card = format_wiki_card(lesson, wiki)
            print(f"  词汇数: {len(lesson.get('key_vocab',[]))}")
        else:
            print("  Wikipedia 不可用，回退口语模式")
            source = "auto"

    # ── Mode B: Word of the Day ──
    if source == "word":
        print("\n--- 每日一词模式 ---")
        word = fetch_random_word()
        if word:
            print(f"  单词: {word['word']}")
            lesson = None
            if AI_API_KEY and not mock:
                print(f"  调用 {AI_PROVIDER} 生成词汇课...")
                lesson = generate_word_lesson(word)
            if not lesson:
                defs = word.get("definitions", ["No definition available"])
                lesson = {
                    "word": word.get("word","unknown"),
                    "ipa": word.get("phonetic",""),
                    "meaning_cn": defs[0] if defs else "请查阅词典",
                    "memory_hook": "尝试用这个词造一个句子加深记忆",
                    "daily_use": f"在日常对话中使用 '{word.get('word','')}' 代替常见词",
                    "collocations": [f"{word.get('word','')} + 常见搭配"],
                }
            card = format_word_card(lesson)
        else:
            print("  Dictionary API 不可用，回退口语模式")
            source = "auto"

    # ── Mode C: Vocab + Small Talk (default/fallback) ──
    if source == "auto":
        print("\n--- 主题口语模式 ---")
        state = advance_category(state)
        cat = CATEGORIES[state["currentCategory"]]
        print(f"  今日主题: {cat['name']}（{cat['cn']}）[{cat['id']}/12]")

        lesson = None
        if AI_API_KEY and not mock:
            print(f"  调用 {AI_PROVIDER} 生成...")
            lesson = generate_vocab_lesson(state["currentCategory"], state)

        if not lesson:
            print("  使用规则引擎生成...")
            lesson = fallback_vocab_lesson(state["currentCategory"], state)

        if not lesson:
            print("  生成失败")
            return 1

        print(f"  口语: {lesson.get('phrase','')[:50]}")
        print(f"  词汇数: {len(lesson.get('vocab',[]))}")

        # Track used words
        for v in lesson.get("vocab", []):
            if v.get("word") and v["word"] not in state["wordsUsed"]:
                state["wordsUsed"].append(v["word"])
        save_state(state)

        # Auto-register vocab for SM-2 review
        rstate = load_review_state()
        rstate = add_words_batch(rstate, lesson.get("vocab", []))
        rstate["last_review"] = rstate.get("last_review", datetime.now().strftime("%Y-%m-%d"))
        save_review_state(rstate)

        card = format_vocab_card(lesson, state["currentCategory"])

    # ── Mode D: SM-2 Review ──
    if source == "review":
        print("\n--- SM-2 间隔复习模式 ---")
        rstate = load_review_state()
        due = get_due_words(rstate)
        stats = get_stats(rstate)
        print(f"  词汇库: {stats['total']} 词 | 待复习: {stats['due']} 词 | 已掌握: {stats['mastered']} 词")

        if not due:
            print("  今天没有需要复习的词汇！")
            card = _build_card(f"✅ 复习完成 | {datetime.now().strftime('%Y-%m-%d')}", "green",
                f"词汇库共 **{stats['total']}** 词，今天没有需要复习的。\n\n已掌握 **{stats['mastered']}** 词（间隔≥30天）\n平均易度: **{stats['avg_ease_factor']}**",
                None, "")
        else:
            # Take up to 5 due words
            review_words = due[:5]
            print(f"  复习词: {', '.join(w['word'] for w in review_words)}")

            # Generate review content with AI
            lesson = None
            if AI_API_KEY and not mock:
                print(f"  调用 {AI_PROVIDER} 生成复习题...")
                lesson = _generate_review_quiz(review_words)
            if not lesson:
                lesson = {"words": review_words, "tip": "自测：看到英文能否立刻说出中文意思？想不起来就标记 0-2 分。"}

            card = format_review_card(lesson, review_words)

        # Update last_review date
        rstate["last_review"] = datetime.now().strftime("%Y-%m-%d")
        save_review_state(rstate)

    # Auto-register words from wiki/word modes into SM-2
    if source in ("wiki", "word"):
        rstate = load_review_state()
        if source == "wiki" and lesson:
            rstate = add_words_batch(rstate, lesson.get("key_vocab", []))
        elif source == "word" and lesson:
            rstate = add_word(rstate, lesson.get("word",""), lesson.get("meaning_cn",""),
                            lesson.get("ipa",""), lesson.get("collocations",[""])[0] if lesson.get("collocations") else "")
        save_review_state(rstate)

    # Push
    print("\n--- 推送 ---")
    ok = push_to_feishu(card, dry=dry)
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'完成' if ok or dry else '推送失败'}")
    return 0 if (ok or dry) else 1

if __name__ == "__main__":
    sys.exit(main())
