# ☀️ Sunny Life Tools

> 用 AI 和自动化，把日常生活过得更好。

一个汇集亲子教育、美食烹饪、语言学习、科研效率等日常场景的自动化工具箱。每个工具都可独立运行，配置后通过飞书/企业微信/定时任务全自动运转。

---

## 📦 工具箱总览

| 分类 | 工具 | 说明 | 状态 |
|------|------|------|------|
| 🧒 亲子 | [每日小古文](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/kids/daily-guguwen) | 每天推送一首古文经典，含原文、出处、音频 | ✅ 运行中 |
| 🧒 亲子 | [每日科学](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/kids/daily-science-kids) | 按科目轮换的儿童科学知识推送 | ✅ 运行中 |
| 🍳 美食 | [每日菜谱](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/food/daily-recipe-push) | AI 智能选菜 + B站视频 + 飞书推送 | ✅ 运行中 |
| 📚 学习 | [每日英语](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/learning/daily-english) | 12主题轮换 + 地道口语 + 词汇 + 发音示范 | ✅ 运行中 |
| 🔬 科研 | [科研工具](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/research) | GWAS/MR/生信分析工具集 | 🚧 待建 |
| 🏠 生活 | [生活工具](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/life) | 日常效率小工具 | 🚧 待建 |

---

## 🚀 快速开始

每个工具独立运作，进入对应目录查看 README 即可。

### 通用依赖

```bash
pip install requests
```

### 推送通道配置

所有工具统一通过飞书/企业微信 webhook 推送：

- **飞书群机器人**（推荐，永久免费）：建群 → 添加机器人 → 复制 webhook URL
- **企业微信群机器人**：建群 → 群机器人 → 复制 webhook URL

配置后设为环境变量即可自动推送。

---

## 🧒 亲子教育

### 每日小古文 (`kids/daily-guguwen/`)

每天推送一条国学经典，内容来自凯叔《每日小古文》：
- 原文朗读音频
- 字词注释
- 白话文翻译
- 配套图片卡片

```bash
cd kids/scripts
python local_push.py evening --webhook "你的webhook地址"
```

### 每日科学 (`kids/daily-science-kids/`)

按星期轮换科目（物理/化学/生物/地理/天文/英语/惊喜），为小学生生成适龄科普短文。

```bash
cd kids/scripts
python local_push.py morning --webhook "你的webhook地址"
```

---

## 🍳 美食

### 每日菜谱 (`food/daily-recipe-push/`)

AI 驱动的每日菜谱推送系统：
- **🧠 MiniMax M2.7 AI** 智能选菜（季节感知 + 工作日家常/周末大菜）
- **📺 B站视频** 自动搜索高质量做菜教程
- **📱 飞书推送** 富文本卡片消息
- **📊 357道菜谱** 来自 HowToCook (10万⭐)
- **🛡️ 容错降级** AI 不可用时自动切换规则引擎

```bash
cd food/daily-recipe-push
python daily_runner.py --dry    # 试运行
python daily_runner.py          # 正式推送
```

详见 [完整 SOP 文档](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/docs/SOP.md)。

---

## 📚 学习

### 每日英语 ([`learning/daily-english/`](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/learning/daily-english))

✅ 已实现。每日推送一节微型英语课：地道口语 + 主题词汇 + 记忆技巧 + YouGlish 发音。

- **🗣️ 两段式课程**：Part 1 实用口语（场景+变体+回法）+ Part 2 主题词汇（IPA+例句+记忆技巧）
- **🔄 12 类主题轮换**：饮食/健康/居家/职场/运动/购物/出行/宠物/家务/娱乐/理财/天气
- **📊 三级难度**：初级（小学生）/ 中级（初高中）/ 高级（大学职场）
- **🔊 发音示范**：每条口语带 YouGlish 按钮，一键听真人发音

```bash
cd learning/daily-english
python daily_english.py --dry
```

参考：[深度可行性分析](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/learning/daily-english/feasibility-analysis.md)（含 9 个仓库/技能的实检分析）

---

## 🔬 科研

🚧 规划中。计划收录：
- GWAS 数据检索与 MR 分析流程
- 文献管理自动化
- 生信分析常用脚本

---

## 🏠 生活

🚧 规划中。计划收录：
- 家庭记账自动化
- 健康提醒
- 日常小工具

---

## 🛠 定时任务

所有工具都支持 Windows Task Scheduler 或 Linux cron 定时执行：

**Windows:**
```powershell
# 安装定时任务（示例：小古文每晚21:00）
powershell -ExecutionPolicy Bypass -File "kids/scripts/setup_windows_task.ps1" -WebhookUrl "你的webhook" -WebhookType "feishu"
```

**Linux/Mac:**
```bash
# 每天上午10:00 菜谱推送
0 10 * * * cd /path/to/food/daily-recipe-push && python daily_runner.py
```

---

## 📁 仓库结构

```
sunny-life-tools/
├── README.md                   ← 总目录
├── kids/                       ← 亲子教育
│   ├── daily-guguwen/          ←   每日小古文
│   ├── daily-science-kids/     ←   每日科学知识
│   └── scripts/                ←   推送脚本 & 定时任务
├── food/                       ← 美食
│   └── daily-recipe-push/      ←   每日AI菜谱 (含完整SOP)
├── learning/                   ← 学习
│   └── daily-english/          ←   每日英语 (待建)
├── research/                   ← 科研
└── life/                       ← 生活
```

---

## 💰 运行成本

| 工具 | AI 引擎 | 月成本 |
|------|---------|--------|
| 每日菜谱 | 9 种大模型可选 (MiniMax/DeepSeek/OpenAI/Groq/...) | ¥0-30 |
| 每日科学 | 本地规则 | ¥0 |
| 小古文 | 本地索引 | ¥0 |
| 推送通道 | 飞书群机器人 | ¥0 |
| **总计** | | **¥0-30/月** |

---

## 🤝 贡献

这是个人生活项目的公开集合。如果你有类似需求，欢迎 Fork 修改。
