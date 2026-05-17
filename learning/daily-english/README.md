# 📖 每日英语 — AI 驱动的英语学习推送

每天 8:00，飞书群收到一节微型英语课：一句地道口语 + 3-5 个实用词汇。

## 特性

- **🗣️ 主题口语模式**：两段式课程（实用口语 + 主题词汇），12 类轮换
- **📰 Wikipedia 阅读模式**：随机英文文章 → AI 阅读课（语法+词汇+技巧）
- **🔤 每日一词模式**：随机单词 → AI 词汇课（记忆技巧+场景+搭配）
- **🧠 9 种大模型可选**：MiniMax / DeepSeek / OpenAI / Groq / 硅基流动 / Moonshot / 智谱 / 通义千问 / Ollama
- **📊 三级难度**：初级（小学生）/ 中级（初高中）/ 高级（大学职场）
- **🛡️ 容错降级**：所有模式均有无 AI 回退方案

## 架构

```
每日定时触发 (Windows Task Scheduler)
    │
    ├─ 1. 内容源
    │      Wikipedia API (免费) / Free Dictionary (免费) / 12主题库
    │
    ├─ 2. AI 生成内容 (daily_english.py v2.0)
    │      MiniMax M2.7 生成阅读课 / 词汇课 / 口语课
    │
    └─ 3. 飞书推送
           三种卡片样式：阅读(绿) / 词汇(黄) / 口语(蓝)
```

## 快速开始

### 1. 依赖

```bash
pip install requests
```

### 2. 配置

```powershell
# 飞书 webhook（必填）
[Environment]::SetEnvironmentVariable("FEISHU_WEBHOOK", "你的webhook地址", "User")

# AI API Key（可选，不配也能跑）
[Environment]::SetEnvironmentVariable("RECIPE_AI_KEY", "sk-你的Key", "User")

# 难度等级（可选，默认 intermediate）
[Environment]::SetEnvironmentVariable("ENGLISH_LEVEL", "intermediate", "User")

# 切换 AI 提供商（可选，默认 minimax）
[Environment]::SetEnvironmentVariable("ENGLISH_AI_PROVIDER", "deepseek", "User")
```

支持的 AI 提供商详见 [food/daily-recipe-push 文档](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/README.md)。

### 3. 测试

```bash
cd learning/daily-english

# 主题口语模式（默认，12类轮换）
python daily_english.py --dry

# Wikipedia 阅读模式（随机英文文章）
python daily_english.py --source wiki --dry

# 每日一词模式
python daily_english.py --source word --dry

# 规则引擎模式（无需 AI，所有模式通用）
python daily_english.py --mock --dry
```

### 4. 定时任务

```powershell
# 每天 8:00 自动推送
$Action = New-ScheduledTaskAction -Execute (Get-Command python).Source -Argument "`"$PWD\daily_english.py`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "08:00"
Register-ScheduledTask -TaskName "每日英语推送" -Action $Action -Trigger $Trigger
```

## 难度分级

| 等级 | 环境变量 | 词汇量 | 适用人群 |
|------|---------|--------|---------|
| 初级 | `ENGLISH_LEVEL=beginner` | 500-1500 | 小学生 / 零基础 |
| 中级 | `ENGLISH_LEVEL=intermediate` | 1500-4000 | 初高中生 |
| 高级 | `ENGLISH_LEVEL=advanced` | 4000+ | 大学生 / 职场 |

## 12 主题轮换表

| # | 主题 | 子话题 |
|---|------|--------|
| 🍔 | 饮食 | 食材、调料、烹饪、餐厅用语 |
| 🏥 | 健康 | 身体部位、症状、看病、健身 |
| 🏠 | 居家 | 家具、家电、清洁、维修 |
| 👔 | 职场 | 会议、邮件、同事交流、面试 |
| 🏋️ | 运动 | 健身器材、运动项目、健身房用语 |
| 🛒 | 购物 | 蔬菜水果、肉类、日用品、结账 |
| 🚗 | 出行 | 驾驶、加油站、修车、路标 |
| 🐱 | 宠物 | 品种、行为、宠物医院 |
| 🧹 | 家务 | 洗衣、做饭、打扫、垃圾分类 |
| 🎮 | 娱乐 | 游戏、电影、音乐、社交 |
| 💰 | 理财 | 股票、银行、税务、保险 |
| 🌤️ | 天气 | 天气现象、自然灾害、地形植物 |

## 文件说明

| 文件 | 作用 |
|------|------|
| [`daily_english.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/learning/daily-english/daily_english.py) | 主入口 |
| [`config.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/learning/daily-english/config.py) | 9 种大模型 + 飞书配置 |
| `english_state.json` | 轮换状态（自动维护） |

## 成本

| 项目 | 月成本 |
|------|--------|
| AI 生成 | ¥0-5（可选免费额度） |
| YouGlish | ¥0 |
| 飞书推送 | ¥0 |
| **总计** | **¥0-5/月** |
