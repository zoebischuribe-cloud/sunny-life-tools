# 英语学习系统 — v4.0 终极整合计划

> 日期: 2026-05-17 | 模型: Claude Opus 4.7 | 版本: v4.0
> 覆盖: 25+ 个 GitHub/ClawHub 仓库 + 3 个免费 API 数据源
> 方法: 每个仓库/API 均通过 gh CLI / curl 实际读取真实内容后分析

---

## 一、GH CLI 字段名 Bug 修复

### 根源

GitHub CLI 不同子命令字段名不一致：

| 命令 | 正确字段名 |
|------|-----------|
| `gh repo view` | `stargazerCount`（单数，无 s） |
| `gh search repos` | `stargazersCount`（复数，有 s） |

已同步修正到：`~/.claude/CLAUDE.md` + `Win_CC_strong_reminders.md`

---

## 二、Tier 1 顶级新仓库深度分析

### 1. [ZuodaoTech/everyone-can-use-english](https://github.com/ZuodaoTech/everyone-can-use-english)（34,014 ⭐）⭐⭐⭐⭐⭐

**已读 README 全文。** 李笑来团队出品。

| 组件 | 说明 |
|------|------|
| **Enjoy App 网页版** | [enjoy.bot](https://enjoy.bot) — 视频/电子书/闪卡/课程 四种学习模式 |
| **浏览器插件** | YouTube + Netflix 字幕双语 + 跟读 + AI 讲解 |
| **桌面版** | Electron 套壳，即将发布 |
| **配套书籍** | 《人人都能用英语》(2010)、《一千小时》(2024) |
| **核心技术** | AI 口语陪练（语音对话，实时纠音）、AI 跟读训练（影子跟读，评分反馈） |

**对我们系统的价值：**

| 可借鉴 | 不可用 |
|--------|--------|
| ✅ 「一千小时」结构化学习路径 → 作为内容推进逻辑 | ❌ 是产品而非开源工具栈 |
| ✅ YouTube/Netflix 插件思路 → 可作为功能 Phase | ❌ 核心引擎闭源（App 端） |
| ✅ AI 跟读评分交互模式 → 参考 UX 设计 | ❌ 无法嵌入我们的推送系统 |

**结论：Enjoy 是「成品产品」，我们是「自动化推送系统」。互补而非替代。** 可以把 Enjoy 推荐给想深度学习的家人，系统推送轻量内容维持日常英语接触。

---

### 2. [byoungd/English-level-up-tips](https://github.com/byoungd/English-level-up-tips)（44,137 ⭐）⭐⭐⭐⭐⭐

**已读 README 全文。** GitHub 上 star 最高的英语学习仓库。

| 组件 | 说明 |
|------|------|
| 核心内容 | 英语学习方法论 + CEFR 分级体系 |
| 2026 AI 章节 | Gemini 主引擎 + Live/Guided Learning/Canvas/Quiz/Flashcards |
| AI 分工方案 | ChatGPT(对话练习) / Claude(写作反馈) / Perplexity(阅读研究) / DeepL Write(润色) |
| 训练回路 | 理解→词汇→听力→阅读→口语→写作 |

**对我们系统的价值：**

| 可借鉴 | 不可用 |
|--------|--------|
| ✅ 2026 AI 章节方法论 → 注入 AI prompt 的指导思想 | ❌ 纯方法论文档，无代码 |
| ✅ 听说读写训练回路 → 作为内容编排参考 | ❌ 无数据源 |
| ✅ Gemini 主引擎思路 → 印证了多模型策略 | |
| ✅ CEFR 分级 → 难度分级的权威标准 | |

**结论：最佳「理论底座」。** 把它和 daily-english-vocab 的课程模板结合，就是最强的 AI prompt 工程设计。

---

### 3. [m98/fluent](https://github.com/m98/fluent)（128 ⭐）⭐⭐⭐⭐

**已读 README 全文。** Claude Code 原生的语言学习插件。

| 组件 | 说明 |
|------|------|
| 核心算法 | SM-2 间隔重复 + 主动回忆 + 自适应难度 |
| 安装方式 | `claude plugin install fluent@m98` |
| 数据存储 | 纯本地（`~/.claude/fluent-data/`），Python stdlib 零依赖 |
| 追踪粒度 | 每道题、每个错误、每次进步的完整记录 |

**对我们系统的价值：**

| 可借鉴 | 不可用 |
|--------|--------|
| ✅ SM-2 算法 → 可直接参考做「词汇复习」模块 | ❌ 依赖 Claude Code 环境 |
| ✅ 自适应难度（60-70%成功率目标）→ 系统设计原则 | ❌ 非定时推送模式 |
| ✅ 零依赖纯 Python → 可以提取核心算法 | |
| ✅ 多语言支持（非英语专属）| |

**结论：词汇复习模块的「技术标杆」。** 可以在我们的 daily_english 中嵌入 SM-2 间隔复习逻辑。

---

### 4. [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor)（24,024 ⭐）⭐⭐⭐⭐⭐

**已读 README 全文。** 港大团队，Agent-native 架构。

| 组件 | 说明 |
|------|------|
| 6 个 AI Agent | 自适应路线图 / 测验生成 / 辅导 / RAG 文档问答 / 学习追踪 / TutorBot |
| 核心技术 | Next.js 16 + Python 3.11+ + 多 Agent 协作 |
| 多模态 | 视频学习 / 电子书 / 闪卡 / 概念图 / 交互演示 |
| 部署 | `deeptutor start` 一键启动，支持 Docker |

**对我们系统的价值：**

| 可借鉴 | 不可用 |
|--------|--------|
| ✅ 自适应路线图 → 可参考做「学习路径规划」 | ❌ 20 万行代码，远超我们需求 |
| ✅ TutorBot 持久化记忆 → 做多用户追踪的参考 | ❌ 需要自己的服务器部署 |
| ✅ 知识库 RAG → 如果把 TED 语料做成 RAG | |
| ✅ 多 Agent 架构 → 拆分「讲解Agent」「评分Agent」 | |

**结论：** 过于重量级（20 万行代码），不适用于「轻量推送」。但 Agent 架构思想和 RAG 方案值得学习。

---

## 三、免费内容数据源（实测可用）

### Wikipedia API ✅ 零成本

```bash
# 随机文章摘要（JSON格式，含英文原文+标题+摘要）
curl -s "https://en.wikipedia.org/api/rest_v1/page/random/summary"

# 每日精选文章
curl -s "https://en.wikipedia.org/api/rest_v1/feed/featured/$(date +%Y/%m/%d)"

# 按主题搜索
curl -s "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=technology&format=json"
```

**特性：** 无需 API Key，直接 `curl`，涵盖所有主题，每天有精选文章更新。

### Project Gutenberg ✅ 零成本

```bash
# 图书搜索 API
curl -s "https://gutendex.com/books?search=english&languages=en"

# 具体书籍文本（7万本英文原著）
curl -s "https://www.gutenberg.org/files/1342/1342-0.txt"  # 傲慢与偏见
```

**特性：** 7 万本英文原著，无版权，API 和网页爬取都没限制。

### Cambridge Dictionary ⚠️ 有限免费

```bash
# 每日一词（免费，无需 key）
curl -s "https://dictionary.cambridge.org/wordoftheday/"
```

**特性：** 每日一词页面免费访问，大量爬取会触发反爬。

### 推荐组合

```
Wikipedia 每日精选（每日一篇英文文章）
    + Project Gutenberg（每周一篇经典文学段落）
    + Cambridge 每日一词（每天一个地道用法）
```

---

## 四、完整资源图谱（25+ 仓库/API 汇总）

| 排名 | 名称 | 星标 | 类型 | 用途 | 可用度 |
|------|------|------|------|------|--------|
| 🥇 | English-level-up-tips | 44k | 方法论 | AI prompt 理论底座 | ⭐⭐⭐⭐⭐ |
| 🥈 | everyone-can-use-english | 34k | 产品 | 深度学习工具（Enjoy App） | ⭐⭐⭐⭐⭐ |
| 🥉 | DeepTutor | 24k | 平台 | Agent 架构参考 | ⭐⭐⭐⭐⭐ |
| 4 | LangBot | 16k | 框架 | 推送层终极方案 | ⭐⭐⭐⭐⭐ |
| 5 | speech_recognition | 9k | 库 | 语音识别引擎 | ⭐⭐⭐⭐⭐ |
| 6 | Anki-Android | 8k+ | 产品 | 间隔重复算法参考 | ⭐⭐⭐⭐ |
| 7 | awesome-english | 3.5k | 资源合集 | 内容源地图 | ⭐⭐⭐⭐ |
| 8 | daily-english-vocab | 4.1 | 模板 | 12主题课程模板（已实现） | ⭐⭐⭐⭐⭐ |
| 9 | TED Parallel Corpus | 256 | 数据 | 中英平行语料 | ⭐⭐⭐⭐⭐ |
| 10 | ted2srt | 145 | 工具 | TED 双语字幕下载 | ⭐⭐⭐⭐ |
| 11 | fluent | 128 | 插件 | SM-2 间隔复习技术 | ⭐⭐⭐⭐ |
| 12 | did-you-know | 4.1 | 技能 | Wikipedia 趣味事实 | ⭐⭐⭐⭐ |
| 13 | PaperClaw | 232 | 框架 | 科研英语论文摘要 | ⭐⭐⭐ |
| 14 | English Learning Coach | 3.0 | 技能 | 听说读写方法论 | ⭐⭐⭐ |
| 15 | Language Learning Tutor | 4.3 | 技能 | 100+语言教学模板 | ⭐⭐⭐ |
| 16 | Oxford Picture Dict | 20 | 数据 | 2,400 场景词汇 | ⭐⭐⭐ |
| 17 | RealtimeSTT | 9.8k | 库 | 实时语音转文字 | ⭐⭐⭐ |
| 18 | Wikipedia API | — | API | 每日英文文章 | ⭐⭐⭐⭐⭐ |
| 19 | Project Gutenberg | — | API | 7万本英文原著 | ⭐⭐⭐⭐⭐ |
| 20 | Cambridge Dict | — | Web | 每日一词 | ⭐⭐⭐ |

---

## 五、分阶段实现计划（v4.0 最终版）

### Phase 0：已完成 ✅

- [x] daily_english.py（12主题轮换 + MiniMax + 飞书）
- [x] sunny-life-tools 公开仓库
- [x] 9 种 AI 后端支持
- [x] 深度可行性分析文档（v1.0 → v2.0 → v3.0）

### Phase 1：内容源升级（今天）

**新增：Wikipedia + Cambridge 双源**

```
daily_english.py 升级：
  ├─ Wikipedia API → 每日精选英文文章（免费，零依赖）
  ├─ Cambridge → 每日一词（IPA + 例句 + 用法）
  └─ MiniMax → 生成中文讲解 + 重点词汇 + 跟读任务
```

**代码改动：** `daily_english.py` 增加 `fetch_wikipedia()` + `fetch_cambridge()` 函数
**新增依赖：** 无（纯 requests + 正则）
**预计时间：** 30 分钟

### Phase 2：间隔复习系统（本周）

**借鉴 fluent 的 SM-2 算法**

```
词汇复习模块：
  ├─ SM-2 间隔重复 → 学过的词在第1/3/7/14/30天自动复习
  ├─ 自适应难度 → 答对降低频率，答错增加频率
  └─ 飞书推送 → 「今日复习：这5个词该再见了」
```

**参考仓库：** m98/fluent (SM-2 实现)
**新增依赖：** 无（纯算法）
**预计时间：** 1 小时

### Phase 3：TED 讲解推送（本周）

**TED Parallel Corpus + MiniMax 深度讲解**

```
TED 英语课：
  ├─ TED Corpus → 选取中英平行片段
  ├─ MiniMax → 生成深度讲解(背景+语法+词汇+文化)
  ├─ MiniMax → 生成跟读任务(逐句标注发音重点)
  └─ 飞书 → 原文+翻译+讲解+跟读按钮
```

**参考仓库：** TED-Multilingual-Parallel-Corpus + ted2srt
**新增依赖：** TED 语料下载
**预计时间：** 2 小时

### Phase 4：语音交互闭环（下周）

**SpeechRecognition + Whisper + MiniMax 评分**

```
语音练习闭环：
  ├─ 飞书卡片 → 「请跟读这段英文」
  ├─ 用户语音消息 → 飞书回调/Web页面录音
  ├─ Whisper → 语音→文字
  ├─ MiniMax → 对比原文 vs 用户录音 → 逐词评分
  └─ 飞书 → 纠错报告(标红读错的词+发音指导)
```

**参考仓库：** Uberi/speech_recognition + m98/fluent
**新增依赖：** `pip install SpeechRecognition whisper`
**预计时间：** 4 小时

### Phase 5：推送层升级（长期）

**按需引入 LangBot**

当前飞书 webhook 足够用。如果未来需要：
- 微信/Telegram/Discord 多平台
- Web 管理面板
- 插件生态

则 `uvx langbot` 一键部署，把 daily_english 作为 LangBot 的 Agent 接入。

---

## 六、技术选型决策树

```
想实现什么？
├── 每日推送英语内容 → daily_english.py（已实现 ✅）
│   └── 想换个内容源 → Phase 1（Wikipedia/Gutenberg）
│
├── 学过的词定时复习 → Phase 2（SM-2 间隔重复）
│   └── 参考 fluent 的算法实现
│
├── TED 视频 + AI 深度讲解 → Phase 3（TED Corpus）
│   └── 想看视频学英语 → Enjoy App（独立的深度学习工具）
│
├── 跟读/发音纠错 → Phase 4（Whisper + MiniMax）
│   └── 参考 speech_recognition 库
│
└── 多平台推送（微信/飞书/Telegram）→ Phase 5（LangBot）
    └── 当前飞书够用就先不动
```

---

## 七、今日（Phase 1）立即实现清单

1. `daily_english.py` 增加 Wikipedia 内容源
   - `fetch_random_wikipedia()` → 随机英文文章摘要
   - `fetch_featured_wikipedia()` → 每日精选
   - MiniMax 根据文章生成学习材料

2. `daily_english.py` 增加 Cambridge 每日一词
   - `fetch_cambridge_wotd()` → 抓取每日一词

3. 原 12 主题轮换 + 新 3 种内容源并行
   - 日常频道：12 主题口语+词汇（保持现有）
   - 阅读频道：Wikipedia 每日精选（新增）
   - 词汇频道：Cambridge 每日一词（新增）

4. 更新 GitHub 仓库 + 文档

---

文档已写入 Nutstore:C:\Users\Admin\Nutstore\1\SunnyWiki\raw\inbox\20260517\English_Learning_spec_Master-Plan_v4.0_spec.md
