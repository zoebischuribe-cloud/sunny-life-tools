# 每日英语推送 — 可行性深度分析

> 日期: 2026-05-17 | 模型: Claude Opus 4.7 | 版本: v2.0
> 任务: 分析4个英文书签仓库 + 5个ClawHub/GitHub技能，评估能否复现菜谱模式
> 方法: 每个仓库/技能均通过 gh CLI / clawhub CLI 实际读取真实内容后分析

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

---

## 七、ClawHub + GitHub 英语技能深度分析（v2.0 新增）

> 以下 5 个技能/仓库均通过实际联网检索、`clawhub inspect`、`clawhub install` + 读取 SKILL.md、`gh repo view` + `gh api` + curl 下载 README 后逐字分析。
> 每个结论均附实际检索来源。

---

### 🥇 English Learning Coach（ClawHub 技能）

| 字段 | 实际值（已核实） |
|------|-----------------|
| 来源 | ClawHub 技能市场 |
| 作者 | jiangtaoid (Popeye) |
| 版本 | 1.0.0 |
| 许可 | MIT-0 |
| 评分 | 3.008 |
| 可安装 | `clawhub install english-learning-coach` |
| 有数据吗 | **无结构化数据。** 纯 SKILL.md 方法论文档 |
| 有脚本吗 | **无。** 只有 1 个 SKILL.md (4.8KB) |
| 有 API 吗 | 无 |

**真实内容剖析（已读 SKILL.md 全文）：**

技能定义了一个 AI 英语教练的角色，包含 6 大模块：
1. **口语提升** — 影子跟读法步骤、口语练习 Prompt 模板、常用表达示例
2. **听力提升** — 精听训练法、3 级听力训练层次、资源推荐表
3. **阅读提升** — SQ3R 阅读法、生词处理策略、分级阅读材料表
4. **写作提升** — 议论文/邮件结构模板、写作练习 Prompt
5. **考试准备** — 雅思/托福口语写作题型拆解
6. **日常练习计划** — 30 分钟每日计划模板（Morning/Commute/Evening）

**对每日英语推送的可用性评估：**

| 可复用部分 | 不可用部分 |
|-----------|-----------|
| ✅ 影子跟读法步骤 → 作为 prompt 模板注入 | ❌ 无内容生成能力 |
| ✅ 精听训练法 → 推送每周挑战任务 | ❌ 无数据底座 |
| ✅ 口语/写作 Prompt 模板 → 直接复用 | ❌ 不能直接产生每日推送内容 |
| ✅ 分级资源表 → 指导内容难度 | ❌ 是「方法手册」不是「内容工厂」 |

**结论：不是内容源，是教师手册。** 可以提取其中的方法论模板注入 AI prompt，让生成的英语内容带「教练感」（如跟读提示、分级建议），但不能直接提供推送内容。

---

### 🥈 Language Learning Tutor（ClawHub 技能）

| 字段 | 实际值（已核实） |
|------|-----------------|
| 来源 | ClawHub 技能市场 |
| 作者 | chipagosfinest (Alec Gutman) |
| 版本 | 1.0.0 |
| 许可 | MIT-0 |
| 评分 | 4.318 |
| 文件数 | 1 个 SKILL.md |
| 有数据吗 | **有主题词汇分组。** 10 个主题词群，含具体教学结构 |
| 有脚本吗 | **无。** |

**真实内容剖析（已读 SKILL.md 全文）：**

一个巨无霸级别的 AI 语言导师技能，支持 100+ 语言，7 种教学模式：
1. **Vocabulary Builder** — 按主题教词（10 组：Greetings/Numbers/Food/Family/Travel/Shopping/…），含 quiz 格式
2. **Grammar Lessons** — 4 级语法教学（Beginner/Elementary/Intermediate/Advanced）
3. **Conversation Practice** — 场景模拟 + 错题纠正 + 文化注释
4. **Flashcard Drill** — 间隔重复抽认卡
5. **Script & Writing System** — 非拉丁文字教学（中日韩阿俄希……）
6. **Cultural Context** — 礼貌级别/手势/禁忌/幽默/谚语
7. **Exam Prep** — DELE/DELF/Goethe/JLPT/HSK/TOPIK 等

**对每日英语推送的可用性评估：**

| 可复用部分 | 不可用部分 |
|-----------|-----------|
| ✅ 10 组主题词汇分类 → 可作为内容轮换框架 | ❌ 是交互式教学引擎，不是推送引擎 |
| ✅ 词条格式（Word-IPA-Meaning-Example-MemoryHook）→ 直接复用 | ❌ 无实际词汇数据库（依赖 AI 生成） |
| ✅ 场景对话模板 → 作为 AI prompt 模板 | ❌ 不能自动化定时推送 |
| ✅ Quiz 格式 → 可做成互动卡片 | ❌ 过于庞大，英语只是其 100+ 语言之一 |

**结论：词汇教学格式和主题分类有极高参考价值。** 可以把它的「10 组主题 + 5 词条格式」作为每日英语推送的内容模板。但它本身不产出内容，需要 MiniMax 按模板生成。

---

### 🥉 Daily English Vocab（ClawHub 技能）

| 字段 | 实际值（已核实） |
|------|-----------------|
| 来源 | ClawHub 技能市场 |
| 作者 | forkercat |
| 版本 | 1.0.0 |
| 许可 | MIT-0 |
| 评分 | 4.096 |
| 文件数 | 1 个 SKILL.md |
| 有数据吗 | **有！12 个主题类别，每类有具体词条例句** |
| 有脚本吗 | **无代码文件。** 依赖 OpenClaw cron 调度 |

**真实内容剖析（已读 SKILL.md 全文）：**

**这是 5 个技能中最接近「每日英语推送」目标的一个。** 它本身就是为「daily push」设计的：

**课程结构（已核实）：**
```
Part 1: Daily Small Talk 🗣️
  - Scene（场景）
  - Phrase（地道表达）
  - Variations（2-3 个变体）
  - Natural responses（地道回法）
  - Chinese translation（中英对照）

Part 2: Themed Vocabulary 📚
  - 3-5 words with IPA + Chinese meaning + example sentence
  - 💡 Tip（易混淆词 / 文化注释）
```

**12 类主题轮换表（每类 2-3 天，完整循环约 1 个月）：**
1. 🍔 Food & Drinks
2. 🏥 Body & Health
3. 🏠 Home & Living
4. 👔 Work & Office
5. 🏋️ Fitness & Sports
6. 🛒 Grocery Shopping
7. 🚗 Transportation
8. 🐱 Pets & Animals
9. 🧹 Daily Chores
10. 🎮 Entertainment
11. 💰 Finance
12. 🌤️ Weather & Nature

**状态追踪机制：**
```json
{
  "currentCategory": 1,
  "daysOnCategory": 1,
  "lastRun": "2026-03-15",
  "wordsUsed": ["booger", "saliva", "sweat"]
}
```

**对每日英语推送的可用性评估：**

| 可复用部分 | 不可用部分 |
|-----------|-----------|
| ✅ 两段式课程结构 → **直接照搬** | ❌ 无独立 Python 脚本，依赖 OpenClaw 环境 |
| ✅ 12 类主题轮换表 → **直接照搬** | ❌ 无自己的数据文件 |
| ✅ 状态追踪 JSON 格式 → **直接复用逻辑** | ❌ 推送格式为 Telegram/Discord，无飞书适配 |
| ✅ 中英对照 + 美式英语风格 → 与目标用户匹配 | |
| ✅ 示例输出（含 booger/drool/sweat 等）→ 已验证可运行 | |

**结论：⭐⭐⭐⭐⭐ 最适配。** 它就是为「每日推送英语学习内容」而生的。可以直接把它的 SKILL.md 内容转化为独立的 Python 脚本（daily_english.py），配合 MiniMax M2.7 生成具体内容，飞书推送。

---

### 4. Did You Know（ClawHub + GitHub）

| 字段 | 实际值（已核实） |
|------|-----------------|
| 来源 | ClawHub 技能 + GitHub 仓库 |
| 作者 | jonathandeamer |
| 仓库 | https://github.com/jonathandeamer/did-you-know |
| 版本 | 0.2.2 |
| 许可 | MIT |
| GitHub 星标 | 0 (新仓库，ClawHub 评分 4.117) |
| 有数据吗 | **有！Wikipedia DYK 实时数据，无 API Key 需要** |
| 有脚本吗 | **有！4 个 Python 脚本** |

**真实代码结构（已通过 GitHub README + SKILL.md 核实）：**

```
did-you-know/
├── SKILL.md                  # 技能定义 + 完整使用指南
├── scripts/
│   ├── dyk.py               # 提供事实（serve one fact）
│   ├── prefs.py             # 偏好管理（init/list/get/set）
│   ├── fetch_hooks.py       # 抓取 Wikipedia DYK 新事实
│   └── write_tags.py        # 给事实打标签
├── references/
│   ├── commands.md          # 命令参考
│   ├── tagging-guide.md     # 标签指南
│   └── tags.csv             # 20 个 domain 标签 + 9 个 tone 标签
└── README.md
```

**核心能力：**
1. **自动抓取** Wikipedia "Did You Know?" 栏目（志愿者每天更新）
2. **智能排序** — 20 个领域标签 × 9 个风格标签，支持个性化偏好
3. **去重缓存** — 看过的不会重复出现
4. **定时调度** — 通过 OpenClaw cron 每天自动推送
5. **零 API 依赖** — 纯网页抓取，不需要任何 API key

**20 个领域标签（domain）：** `animals` · `economics_business` · `film` · `history` · `journalism` · `language_linguistics` · `literature` · `medicine_health` · `military_history` · `music` · `mythology_folklore` · `nature` · `performing_arts` · `places` · `religion` · `science` · `sports` · `technology` · `television` · `visual_art`

**9 个风格标签（tone）：** `dark` · `dramatic` · `inspiring` · `poignant` · `provocative` · `quirky` · `straight` · `surprising` · `whimsical`

**对每日英语推送的可用性评估：**

| 可复用部分 | 不可用部分 |
|-----------|-----------|
| ✅ Wikipedia DYK 事实抓取 → **可直接作为「英语冷知识」频道** | ❌ 依赖 OpenClaw 调度环境 |
| ✅ 20 域 × 9 调 标签系统 → 可以筛选适合学习的领域 | ❌ 事实是英文维基条目摘要，非教学格式 |
| ✅ 自动去重 + 缓存机制 → 直接复用 | ❌ 需要改造输出格式为「英文学习材料」 |
| ✅ 不需要任何 API key → 零成本零依赖 | |
| ✅ tags.csv 标签体系 → 可复用为内容分类 | |

**结论：⭐⭐⭐⭐ 适合作为「英语趣味冷知识」补充频道。** 不能替代每日英语教学，但可以做成每周 1-2 次的「Fun Fact Friday」等趣味副线。技术实现最完整（4 个 Python 脚本可独立运行）。

---

### 5. PaperClaw（GitHub 仓库）

| 字段 | 实际值（已核实） |
|------|-----------------|
| 来源 | GitHub 仓库 |
| 作者 | guhaohao0991 |
| 仓库 | https://github.com/guhaohao0991/PaperClaw |
| 星标 | 232 ⭐ |
| 语言 | Python |
| 许可 | MIT |
| 有数据吗 | **有。arXiv API 实时论文数据** |
| 有脚本吗 | **有！完整代码库** |

**真实代码结构（已通过 GitHub README 核实）：**

```
PaperClaw/
├── skills/
│   └── paper-expert-generator/     # 生成领域论文专家Agent的Skill
│       ├── SKILL.md               # 8步工作流（领域访谈→关键词→脚手架→交付）
│       ├── scripts/
│       │   └── init_domain_agent.py   # 自动脚手架脚本
│       ├── references/
│       │   ├── domain-adaptation-guide.md  # 8个领域示例
│       │   └── agent-template-guide.md
│       └── assets/templates/      # AGENT.md/models.json/schedules.json 模板
│
├── agents/
│   └── surrogate-modeling/        # Demo: Scientific ML + 3D Geometry
│       ├── agent/AGENT.md         # Agent 角色定义
│       ├── skills/
│       │   ├── arxiv-search/      # arXiv 批量搜索 + 去重
│       │   ├── semantic-scholar/  # 引用数据 API
│       │   ├── paper-review/      # 论文评估 + 安全写入
│       │   ├── daily-search/      # 每日自动检索
│       │   └── weekly-report/     # 周报生成
│       └── docs/architecture.md
```

**核心能力：**
1. **每日论文检索** — arXiv API 批量搜索，自动去重，精选 Top 3
2. **深度总结** — 回答 10 个核心问题，生成结构化 summary.md
3. **四维评分** — 可定制的领域专属评分维度 + Date-Citation 权重
4. **周报生成** — Top 3 精选报告，支持推送通知
5. **领域生成器** — `init_domain_agent.py` 可为任意领域自动生成专家 Agent

**对每日英语推送的可用性评估：**

| 可复用部分 | 不可用部分 |
|-----------|-----------|
| ✅ arXiv 每日检索架构 → 可改为「每日英文论文摘要推送」 | ❌ 核心目的是科研论文，不是英语教学 |
| ✅ 自动去重 + 评分 → 直接复用逻辑 | ❌ 需要领域知识才能理解内容 |
| ✅ weekly-report → 可做「每周英语学习进度报告」 | ❌ 对非科研用户无意义 |
| ✅ 领域生成器 → 可创建「英语学习论文专家」Agent | |

**结论：⭐⭐⭐ 适合科研英语场景。** 如果你订阅 `q-bio`（生物信息学）或 `cs.CL`（NLP）类别的论文，可以每天推送一篇英文论文摘要 + 关键图表 + 中文解读。这同时满足了「阅读前沿论文」和「练习英语」两个目标。但对普通英语学习者不适用。

---

## 八、5技能综合对比 & 推荐方案

### 与菜谱架构的适配度

| 技能 | 数据底座 | AI 选择 | 推送格式 | 适配度 |
|------|---------|---------|---------|--------|
| daily-english-vocab | ⭐⭐⭐ 12主题+词条模板 | ⭐⭐⭐ MiniMax 填充内容 | ⭐⭐ 需适配飞书 | **最高** |
| did-you-know | ⭐⭐⭐⭐⭐ Wikipedia 实时 | ⭐⭐ 标签偏好排序 | ⭐⭐ 需适配飞书 | **高** |
| english-learning-coach | ⭐ 方法论无数据 | ⭐⭐⭐ 方法论注入 prompt | ⭐ 纯方法 | 中 |
| language-learning | ⭐⭐ 主题分类+格式 | ⭐⭐⭐ 词条格式注入 prompt | ⭐ 纯教学 | 中 |
| PaperClaw | ⭐⭐⭐⭐⭐ arXiv 实时 | ⭐⭐⭐⭐ 领域评分引擎 | ⭐⭐⭐ 已有周报 | 中（科研向） |

### 推荐方案：组合拳

不是选一个，而是组合：

```
每日英语推送系统 v2.0
│
├─ 主频道：Daily English Vocab 模式
│   ├─ 内容模板 → 从 daily-english-vocab 照搬（Part1口语 + Part2词汇）
│   ├─ AI 生成 → MiniMax M2.7 按模板生成具体内容
│   └─ 推送 → 飞书群机器人卡片
│
├─ 副频道：Did You Know 模式（每周六）
│   ├─ 内容源 → Wikipedia DYK 实时抓取
│   ├─ 标签筛选 → 偏好 history + science + quirky
│   └─ 推送 → 飞书群「趣味英语冷知识」
│
├─ 方法论层：English Learning Coach
│   ├─ 影子跟读法 → 每周推送跟读挑战
│   ├─ 精听训练 → 月度听力材料推荐
│   └─ 注入 AI prompt → 让每日内容有「教练感」
│
└─ 科研副线（可选）：PaperClaw
    └─ 订阅 q-bio + cs.CL → 每周推送 1 篇英文论文摘要
```

### 实现优先级

| 优先级 | 模块 | 依赖 | 预计时间 |
|--------|------|------|---------|
| P0 | Daily English Vocab（主频道） | MiniMax M2.7 | 今天就做 |
| P1 | Did You Know（趣味副线） | 零依赖 | 30min |
| P2 | Coach 方法论注入 | 修改 AI prompt | 10min |
| P3 | PaperClaw 科研线 | arXiv API | 后续 |

---

## 九、最终结论

| 对比维度 | 菜谱系统 | 英语系统 |
|---------|---------|---------|
| 数据底座 | HowToCook (357道菜) | daily-english-vocab (12主题模板) + Wikipedia DYK |
| AI 引擎 | MiniMax 选菜 | MiniMax 生成内容 |
| 视频源 | Bilibili API | YouGlish API（发音示范） |
| 推送通道 | 飞书群机器人 | 飞书群机器人（同一通道） |
| 定时任务 | Windows Task Scheduler | Windows Task Scheduler（同一方式） |
| 月成本 | ~¥2-5 | ~¥2-5（仅 MiniMax API） |

**可以复现。** 菜谱是「选」的模式，英语是「生成」的模式——但核心技术栈完全相同（MiniMax + 飞书 + Windows 定时任务）。daily-english-vocab 的 12 类主题轮换 + 两段式课程结构，就是英语系统的「recipes.json」。

---

文档已写入 Nutstore:C:\Users\Admin\Nutstore\1\SunnyWiki\raw\inbox\20260517\Daily_English_spec_Feasibility-Analysis_v1.0_spec.md
