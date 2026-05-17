#!/usr/bin/env python3
"""
SM-2 Spaced Repetition Algorithm — ported from SuperMemo/fluent reference.

Tracks vocabulary review intervals to optimise long-term retention.
Each word gets: quality score → ease factor → next review date.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from config import BASE_DIR

REVIEW_FILE = BASE_DIR / "review_state.json"

def load_review_state():
    if REVIEW_FILE.exists():
        return json.loads(REVIEW_FILE.read_text(encoding="utf-8"))
    return {"words": {}, "last_review": ""}

def save_review_state(state):
    REVIEW_FILE.parent.mkdir(parents=True, exist_ok=True)
    REVIEW_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

def sm2_update(word_entry, quality):
    """
    Apply SM-2 algorithm to a single word entry.
    quality: 0-5 (0=complete blackout, 5=perfect recall)
    Returns updated entry dict.
    """
    ef = word_entry.get("ease_factor", 2.5)
    rep = word_entry.get("repetitions", 0)
    interval = word_entry.get("interval", 1)

    if quality >= 3:
        if rep == 0:
            interval = 1
        elif rep == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        rep += 1
    else:
        rep = 0
        interval = 1

    # Update ease factor (SuperMemo formula)
    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ef < 1.3:
        ef = 1.3

    word_entry["ease_factor"] = round(ef, 2)
    word_entry["repetitions"] = rep
    word_entry["interval"] = interval
    word_entry["next_review"] = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
    word_entry["last_quality"] = quality
    word_entry["review_count"] = word_entry.get("review_count", 0) + 1
    return word_entry

def add_word(state, word, meaning="", ipa="", example=""):
    """Add a new word to the review system (from any lesson)."""
    if word not in state["words"]:
        state["words"][word] = {
            "word": word,
            "meaning": meaning,
            "ipa": ipa,
            "example": example,
            "ease_factor": 2.5,
            "repetitions": 0,
            "interval": 1,
            "next_review": datetime.now().strftime("%Y-%m-%d"),
            "last_quality": 0,
            "review_count": 0,
            "added": datetime.now().strftime("%Y-%m-%d"),
        }
    return state

def add_words_batch(state, vocab_list):
    """Add multiple words at once (from lesson vocab)."""
    for v in vocab_list:
        w = v.get("word", "")
        if w:
            state = add_word(state, w, v.get("meaning", ""), v.get("ipa", ""), v.get("example", ""))
    return state

def get_due_words(state):
    """Return words due for review today (or overdue)."""
    today = datetime.now().strftime("%Y-%m-%d")
    due = []
    for w, entry in state["words"].items():
        if entry.get("next_review", "2000-01-01") <= today:
            due.append(entry)
    # Sort: overdue first, then by ease_factor (harder words first)
    due.sort(key=lambda e: (e.get("next_review", ""), e.get("ease_factor", 99)))
    return due

def get_stats(state):
    """Return review statistics."""
    words = state["words"]
    total = len(words)
    due = len(get_due_words(state))
    avg_ef = round(sum(w.get("ease_factor", 2.5) for w in words.values()) / max(total, 1), 2)
    mastered = sum(1 for w in words.values() if w.get("interval", 0) >= 30)
    return {
        "total": total,
        "due": due,
        "avg_ease_factor": avg_ef,
        "mastered": mastered,
        "last_review": state.get("last_review", "never"),
    }
