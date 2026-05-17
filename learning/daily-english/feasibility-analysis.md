# 每日英语推送 — 可行性深度分析

> 日期: 2026-05-17 | 模型: Claude Opus 4.7 | 任务: 分析4个英文书签仓库，评估能否复现菜谱模式

---

## 一、四个仓库逐一解剖

### 1. yujiangshui/A-Programmers-Guide-to-English（16.4k ⭐）

专为程序员编写的英语学习指南。

| 维度 | 评估 |
|------|------|
| 是什么 | Markdown 文档，中文写作的英语学习方法论 |
| 有数据吗 | 无。纯文本教程，无结构化学习内容 |
| 有 API 吗 | 无 |
| 有价值吗 | 有。语音学原理讲得透彻，可作为 AI prompt 的理论底座 |
| 能直接推送吗 | **不能。没有每日内容单元，是一本「书」** |

**对你每日英语的价值：** 方法论教材。可以提取其中的学习理念注入 AI prompt，让 AI 生成内容时遵循「程序员学英语」的思维框架，而不是用培训班套路。

---

### 2. yvoronoy/awesome-english（3.5k ⭐）

精选英语学习资源合集（Awesome List 格式）。

| 维度 | 评估 |
|------|------|
| 是什么 | 一个超大的资源索引：播客、YouTube、新闻、App、AI工具…… |
| 有数据吗 | 全是外链。BBC Learning English、NPR、YouTube频道URL…… |
| 有 API 吗 | 无 |
| 有价值吗 | **极高。这是「内容来源地图」，告诉 AI 去哪里找素材** |
| 能直接推送吗 | **不能。链接不是内容，无法直接提取后推送** |

**对你每日英语的价值：** 路线图。它告诉你：初级用 BBC 6 Minute English，中级用 NPR，高级用 Lex Fridman。这些可以编码成规则，让 AI 根据难度等级自动选择内容源。

---

### 3. AgenticHealthAI/Awesome-AI-Agents-for-Healthcare

❌ 与英语无关。医疗 AI Agent 合集。跳过。

---

### 4. KoljaB/RealtimeSTT（9.8k ⭐）

Python 实时语音转文字库。

| 维度 | 评估 |
|------|------|
| 是什么 | 本地语音识别引擎，支持 faster-whisper/whisper.cpp |
| 有数据吗 | 无。这是工具，不是内容 |
| 有 API 吗 | 无。本地安装，需 GPU 加速 |
| 有价值吗 | **有。可实现「用户跟读 → AI 评分」的闭环** |
| 能用吗 | **可以，但太重。本地装 GPU 依赖，不适合轻量推送场景** |

**对你每日英语的价值：** 进阶功能。如果未来要做「发音跟读评分」，它是核心技术。但 MVP 阶段不需要——飞书群推文本卡片就够。

---

## 二、核心发现：菜谱模式 vs 英语模式

### 菜谱模式为什么能成功

```
HowToCook（357道菜的数据金矿）→ extract_recipes.py → recipes.json
                                                          ↓
                                            MiniMax AI 从357道中选1道
                                                          ↓
                                            Bilibili API 搜视频 → BV号
                                                          ↓
                                            飞书推送 → 家人收到卡片
```

**关键前提**：有结构化数据源（357道菜名+分类+难度），AI 只要「选」，不用「造」。

### 英语模式缺什么

```
awesome-english（外链索引，无内容）
A-Programmers-Guide（方法论，无数据单元）
                              ↓
                    没有「英语内容数据库」
                              ↓
            MiniMax AI 无法「选」——因为没有库可以选
                              ↓
            需要 AI 自己去「造」内容，而不是「选」内容
```

**菜谱是选菜问题，英语是造内容问题。** 前者有数据底座，后者没有。

---

## 三、三条可行路径

### 路径A：AI纯生成模式（最快落地，今天就能跑）

MiniMax 直接生成每日英语内容，不依赖外部数据源。

```
MiniMax AI 生成：
  ├─ 每日一句（经典/实用/地道）
  ├─ 语法解析
  ├─ 例句 × 2
  ├─ 记忆技巧
  └─ 今日词汇

B站/YouTube 搜索：英文发音视频（可选）

飞书推送：富文本卡片
```

| 优势 | 劣势 |
|------|------|
| 零外部依赖，今天就能跑 | AI 生成质量取决于 prompt |
| 完全可控，想推什么推什么 | 没有「权威感」——是AI生成的，不是BBC原版 |
| 可以个性化（根据用户水平调整） | 长期可能重复或套路化 |

**适用场景**：MVP 快速验证。先用 AI 生成跑起来，看家人反馈。

### 路径B：外部API内容源模式（更权威，有真实素材）

使用免费/低成本的外部 API 获取真实英语内容。

| 内容源 | API | 费用 | 说明 |
|--------|-----|------|------|
| BBC 6 Minute English | RSS + 网页抓取 | 免费 | 6分钟音频+文稿，最适合初学者 |
| NPR News | NPR API | 免费 | 美国公共广播，有文稿 |
| YouGlish | Web API | 免费 | YouTube 中的英语发音片段 |
| 柯林斯词典 | Collins API | 免费额度 | 每日一词 + 例句 |
| Merriam-Webster | Word of the Day API | 免费 | 每日一词 + 词源 + 例句 |

**推荐组合**：柯林斯「每日一词」+ NPR「一句话新闻」+ AI 生成记忆技巧。

### 路径C：混合模式（推荐）

```
数据层：
  ├─ 柯林斯/韦氏 Word of the Day → 每日一词
  ├─ BBC 6 Minute RSS → 每周听力素材（可自动摘要）
  └─ awesome-english 索引 → 难度分级规则

AI 层：
  ├─ MiniMax M2.7 生成：语法拆解 + 记忆技巧 + 情景造句
  └─ MiniMax M2.7 翻译：英文 → 中文解释

推送层：
  ├─ 飞书群机器人 → 每日英语卡片
  └─ 可选：B站搜「英语发音」视频 → 跟读示范
```

---

## 四、推荐方案：路径A 先行 MVP

**今天就实现，今晚就能推送。**

### 内容结构（MiniMax 一次生成全部）

```json
{
  "sentence": "The best way to predict the future is to create it.",
  "source": "Peter Drucker",
  "translation": "预测未来的最好方式就是去创造它。",
  "grammar": "不定式 to predict / to create 作定语和表语",
  "vocabulary": [
    {"word": "predict", "phonetic": "/prɪˈdɪkt/", "meaning": "预测，预言"},
    {"word": "create", "phonetic": "/kriˈeɪt/", "meaning": "创造，创建"}
  ],
  "memory_tip": "pre(提前) + dict(说) → 提前说出 = 预测",
  "daily_word": {
    "word": "inevitable",
    "phonetic": "/ɪnˈevɪtəbəl/",
    "meaning": "不可避免的",
    "example": "Change is inevitable."
  }
}
```

### 难度分级（从 awesome-english 提炼）

| 等级 | 句子类型 | 词汇量 | 对应人群 |
|------|---------|--------|---------|
| 初级 | 日常口语短句 | 500-1500 | 小学生/零基础 |
| 中级 | 名人名言/新闻摘要 | 1500-4000 | 初高中生 |
| 高级 | 经济学人/学术长句 | 4000+ | 大学生/职场 |

默认推中级，通过环境变量可切换。

### 推送卡片效果

```
┌──────────────────────────────────┐
│ 📖 每日英语 | 2026-05-17         │  ← 红色标题
├──────────────────────────────────┤
│                                  │
│ "The best way to predict the     │
│  future is to create it."        │
│  — Peter Drucker                 │
│                                  │
│ 预测未来的最好方式就是去创造它。  │
│                                  │
│ 🔍 语法：不定式作定语和表语      │
│                                  │
│ 📝 今日词汇：                    │
│  • predict /prɪˈdɪkt/ 预测       │
│  • create /kriˈeɪt/ 创造         │
│                                  │
│ 💡 记忆技巧：                    │
│  pre(提前) + dict(说) = 预测     │
│                                  │
│ 🎯 每日一词：inevitable          │
│  不可避免的                      │
│  Change is inevitable.           │
│                                  │
│        [ 📺 听发音示范 ]         │  ← 按钮，跳转 YouGlish
└──────────────────────────────────┘
```

---

## 五、实现计划

| Phase | 内容 | 时间 |
|-------|------|------|
| 1 | `daily_english.py` — MiniMax 生成每日一句 + 飞书推送 | 30 min |
| 2 | 难度分级（初级/中级/高级） | 10 min |
| 3 | 添加到 sunny-life-tools `learning/daily-english/` | 5 min |
| 4 | 测试 → 推送 → 验证飞书卡片 | 10 min |
| 5 | SOP 文档 | 20 min |

---

## 六、结论

| 仓库 | 对每日英语的价值 |
|------|-----------------|
| A-Programmers-Guide | 方法论注入 AI prompt，让内容符合程序员思维 |
| awesome-english | 难度分级规则 + 内容源地图 |
| RealtimeSTT | 进阶功能储备（跟读评分），MVP 不用 |

**可以复现菜谱模式，但数据底座从「本地菜谱库」变成了「MiniMax AI 生成」。**
核心链路一致：AI 智能生成内容 → 飞书群推送 → 定时任务自动化。

---

文档已写入 Nutstore:C:\Users\Admin\Nutstore\1\SunnyWiki\raw\inbox\20260517\Daily_English_spec_Feasibility-Analysis_v1.0_spec.md
