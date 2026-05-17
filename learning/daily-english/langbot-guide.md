# LangBot 多平台部署指南

> 将 daily_english 部署到微信/Telegram/Discord/QQ/飞书/钉钉等 10+ 平台

## LangBot 是什么

[LangBot](https://github.com/langbot-app/LangBot)（16k ⭐）是一个开源的生产级 IM 机器人平台。一条命令部署 AI 机器人到几乎所有聊天平台。

## 当前方案 vs LangBot

| | 当前（飞书 webhook） | LangBot |
|---|---------------------|---------|
| 支持的平台 | 仅飞书群机器人 | 10+ 平台（微信/企微/QQ/飞书/钉钉/Telegram/Discord/Slack/LINE） |
| Web 管理面板 | 无 | ✅ 浏览器配置 |
| 多 Bot 管理 | 无 | ✅ 一个面板管所有 Bot |
| 插件生态 | 无 | ✅ 数百个插件 |
| 部署 | 手写 Python + Task Scheduler | `uvx langbot` 一行启动 |
| 适用场景 | 个人/家庭小规模 | 多人/多群/企业级 |

## 集成方式

### 方式一：LangBot 作为推送层（推荐）

我们的 daily_english.py 继续生成内容 → 通过 LangBot Webhook 推送到任意平台。

```
daily_english.py (内容引擎) → HTTP POST → LangBot (推送层) → 微信/Telegram/飞书/...
```

### 方式二：daily_english 作为 LangBot 插件

将 daily_english 封装为 LangBot Plugin，直接在 LangBot 生态中运行。

### 方式三：共存

飞书 webhook 保持日常推送，LangBot 处理交互式请求（如用户输入 `/review` 触发 SM-2 复习）。

## 快速部署

### 1. 安装 LangBot

```bash
# 一行启动（需 uv）
uvx langbot

# 或 Docker
git clone https://github.com/langbot-app/LangBot
cd LangBot/docker && docker compose up -d
```

### 2. 配置 LLM

访问 `http://localhost:5300` → 设置 → LLM 配置 → 添加 MiniMax/DeepSeek/OpenAI

### 3. 配置平台

设置 → 平台 → 选择要接入的平台（微信/Telegram/飞书…）

### 4. 添加定时任务

在 LangBot 中配置 cron 定时触发 daily_english：

```yaml
# LangBot pipeline 配置示例
pipelines:
  - name: daily-english-morning
    cron: "0 8 * * *"
    action: run_script
    script: python /path/to/daily_english.py
    channel: feishu
    to: "群聊ID"
```

## 平台接入速查

| 平台 | 接入方式 | 难度 |
|------|---------|------|
| 飞书 | 飞书开放平台 → 创建应用 → 机器人 | ⭐⭐ |
| 企业微信 | 企业微信后台 → 应用管理 → 自建应用 | ⭐⭐ |
| 微信公众号 | 公众号后台 → 开发设置 | ⭐⭐⭐ |
| Telegram | @BotFather 创建 Bot → 获取 Token | ⭐ |
| Discord | Discord Developer Portal → 创建 Bot | ⭐ |
| QQ | QQ 开放平台 / 官方 API | ⭐⭐⭐ |
| Slack | Slack API → 创建 App | ⭐⭐ |
| LINE | LINE Developers → 创建 Channel | ⭐⭐ |

## 当前推荐

**单用户/家庭场景：飞书 webhook 够用，不需要升级。**

**以下情况考虑 LangBot：**
- 需要微信推送（飞书家人不用）
- 多人多群需要分别管理
- 需要 Web 面板可视化管理
- 需要交互式命令（`/review` `/speak` `/quiz`）

---

## 参考文献

- [LangBot GitHub](https://github.com/langbot-app/LangBot)
- [LangBot 文档](https://link.langbot.app/en/docs/guide)
- [LangBot 云服务](https://space.langbot.app/cloud)
- [sunny-life-tools](https://github.com/zoebischuribe-cloud/sunny-life-tools)
