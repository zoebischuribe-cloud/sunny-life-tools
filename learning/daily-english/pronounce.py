#!/usr/bin/env python3
"""
Pronunciation evaluator — compare user speech with target text.

Usage:
  python pronounce.py --target "Hello world" --spoken "Hallo world"
  python pronounce.py --target "The quick brown fox" --audio recording.wav
  python pronounce.py --shadow       # Generate a shadowing task

Dependencies (optional, for audio file mode):
  pip install SpeechRecognition whisper
"""
import json, re, sys
import requests
from config import AI_BASE_URL, AI_API_KEY, AI_MODEL, PROXIES

def evaluate_pronunciation(target, spoken):
    """
    Compare spoken text with target text using MiniMax AI.
    Returns detailed pronunciation report.
    """
    system_prompt = (
        "你是一位英语发音教练。用户会提供「目标句子」和「实际说出」两段文字。\n"
        "请逐词对比，生成发音评估报告。\n\n"
        "返回纯JSON：\n"
        '{"accuracy": 85, "fluency": 80, "completeness": 90,'
        '"errors": [{"word":"读错的词","expected":"正确发音要点(IPA/中文提示)","actual":"可能的错误",'
        '"tip":"改正建议"}],'
        '"summary":"总体评价(50字,鼓励为主)",'
        '"practice":"针对性练习建议(30字)"}'
    )

    user_prompt = (
        f"目标句子：{target}\n"
        f"实际说出：{spoken}\n"
        "请评估发音并给出纠错建议。"
    )

    try:
        resp = requests.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"},
            json={"model": AI_MODEL, "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ], "temperature": 0.3, "max_tokens": 600},
            proxies=PROXIES, timeout=45,
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        content = re.sub(r'```(?:json)?\s*\n?|\n?```', '', content).strip()
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
        print(f"  Evaluation failed: {e}")
    return None

def transcribe_audio(filepath):
    """Transcribe audio file to text using Whisper."""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(filepath) as source:
            audio = r.record(source)
        return r.recognize_whisper(audio)
    except ImportError:
        print("  Install: pip install SpeechRecognition whisper")
        return None
    except Exception as e:
        print(f"  Transcription failed: {e}")
        return None

def format_report(target, spoken, result):
    """Build a Feishu card for pronunciation report."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    errors_text = ""
    if result and "errors" in result:
        errors_text = "\n".join(
            f"**{e.get('word','?')}** → 应读: {e.get('expected','')}\n"
            f"　💡 {e.get('tip','')}"
            for e in result.get("errors", [])
        )

    acc = result.get("accuracy", "?") if result else "?"
    flu = result.get("fluency", "?") if result else "?"
    comp = result.get("completeness", "?") if result else "?"

    content = (
        f"**🎙️ 发音评估报告**\n\n"
        f"📝 **目标句**\n{target}\n\n"
        f"🗣️ **你说的是**\n{spoken}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📊 评分**\n"
        f"• 准确度: {acc}/100\n"
        f"• 流利度: {flu}/100\n"
        f"• 完整度: {comp}/100\n\n"
        f"**🔧 纠错**\n{errors_text}\n\n"
        f"**💬 总评**\n{result.get('summary','加油！多练几次就好！') if result else '请继续练习！'}\n\n"
        f"**🎯 练习建议**\n{result.get('practice','每天跟读10遍，录音对比原声') if result else ''}"
    )

    return {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": f"🎙️ 发音评估 | {today}"}, "template": "red"},
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
        }
    }

def format_shadow_task(target_text, tips):
    """Build a shadowing task card for Feishu."""
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    tips_text = "\n".join(f"• {t}" for t in (tips or ["朗读10遍，录下自己的声音"]))
    content = (
        f"**🗣️ 影子跟读任务**\n\n"
        f"**请大声跟读以下句子 10 遍：**\n\n"
        f"## {target_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"**📋 跟读要点**\n{tips_text}\n\n"
        f"**🎯 完成标准**\n"
        f"1️⃣ 不看文字能流利说出\n"
        f"2️⃣ 语调自然，不像机器人\n"
        f"3️⃣ 录下来对比原声，找出差距\n\n"
        f"完成后，输入你说的内容 → /pronounce --target \"{target_text}\" --spoken \"<你说的>\""
    )
    return {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text", "content": f"🗣️ 跟读任务 | {today}"}, "template": "blue"},
            "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": content}}],
        }
    }

if __name__ == "__main__":
    target = ""
    spoken = ""
    audio = ""
    shadow = "--shadow" in sys.argv

    for i, a in enumerate(sys.argv):
        if a == "--target" and i+1 < len(sys.argv):
            target = sys.argv[i+1]
        if a == "--spoken" and i+1 < len(sys.argv):
            spoken = sys.argv[i+1]
        if a == "--audio" and i+1 < len(sys.argv):
            audio = sys.argv[i+1]

    if shadow:
        print("Shadowing task mode — use from daily_english.py for full integration.")
        sys.exit(0)

    if not target:
        print("Usage: python pronounce.py --target 'sentence' --spoken 'what you said'")
        print("       python pronounce.py --target 'sentence' --audio recording.wav")
        sys.exit(1)

    if audio:
        print(f"Transcribing {audio}...")
        spoken = transcribe_audio(audio)
        if not spoken:
            sys.exit(1)
        print(f"  Transcribed: {spoken}")

    if not spoken:
        print("No spoken text. Use --spoken or --audio.")
        sys.exit(1)

    print(f"Target: {target}")
    print(f"Spoken: {spoken}")
    print("Evaluating...")

    if AI_API_KEY:
        result = evaluate_pronunciation(target, spoken)
    else:
        print("No AI API key. Cannot evaluate.")
        result = None

    if result:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print("Evaluation failed.")
