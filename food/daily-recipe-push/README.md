# 🍳 每次菜谱 — AI 驱动的每日菜谱推送系统

每天 10:00，飞书群自动收到一道智能推荐的家常菜 + B站高清做菜视频。

## 特性

- **🧠 AI 智能选菜**: 9 种大模型可选（MiniMax / DeepSeek / OpenAI / Groq / 硅基流动 / Moonshot / 智谱 / 通义千问 / Ollama），春秋秋冬不同策略，工作日家常菜/周末大菜
- **📺 B站视频**: 自动搜索高播放量做菜教程，质量筛选保证能学会
- **📱 飞书推送**: 富文本卡片消息，带视频直达按钮，永久免费
- **🔄 品类均衡**: 热菜、凉菜、甜品、汤羹均衡轮换，21天不重复
- **🛡️ 容错降级**: AI 不可用时自动切换规则引擎，同样智能
- **📊 357道菜谱**: 来自 [Anduin2017/HowToCook](https://github.com/Anduin2017/HowToCook) (10万⭐), 结构规整

## 架构

```
每日定时触发 (Windows Task Scheduler / cron)
    │
    ├─ 1. MiniMax AI 选菜 (ai_selector.py)
    │       季节感知 + 星期策略 + 品类平衡 + 21天去重
    │
    ├─ 2. B站视频搜索 (bilibili_search.py)
    │       搜索 → 质量评分 → 最佳视频
    │
    ├─ 3. 飞书推送 (wechat_push.py)
    │       飞书/企业微信/WxPusher/PushPlus/Server酱
    │
    └─ 4. Landing Page (可选)
            嵌入 B站播放器 + 菜谱详情
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置推送通道

**推荐飞书**（3分钟，永久免费）:

1. 飞书建群 → 群设置 → 添加机器人 → 自定义机器人
2. 复制 Webhook URL
3. 设置环境变量:

```powershell
[Environment]::SetEnvironmentVariable("FEISHU_WEBHOOK", "你的webhook地址", "User")
```

也支持企业微信、WxPusher、PushPlus、Server酱（编辑 `config.py` 切换）。

### 3. 配置 AI（可选，9 种大模型任意选）

支持的 AI 提供商（OpenAI 兼容协议，切换只需改环境变量）：

| 提供商 | `RECIPE_AI_PROVIDER` | 获取 Key |
|--------|---------------------|----------|
| MiniMax（默认） | `minimax` | [platform.minimaxi.com](https://platform.minimaxi.com/user-center/payment/token-plan) |
| DeepSeek | `deepseek` | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| OpenAI | `openai` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Groq | `groq` | [console.groq.com](https://console.groq.com/keys) |
| 硅基流动 | `siliconflow` | [siliconflow.cn](https://siliconflow.cn/models) |
| Moonshot | `moonshot` | [platform.moonshot.cn](https://platform.moonshot.cn/console/api-keys) |
| 智谱 GLM | `zhipu` | [open.bigmodel.cn](https://open.bigmodel.cn/usercenter/apikeys) |
| 通义千问 | `qwen` | [dashscope.aliyun.com](https://dashscope.console.aliyun.com/apiKey) |
| Ollama（本地） | `ollama` | `ollama pull qwen2.5:7b` |

```powershell
# 方式一：使用默认 MiniMax
[Environment]::SetEnvironmentVariable("RECIPE_AI_KEY", "sk-你的Key", "User")

# 方式二：切换到 DeepSeek
[Environment]::SetEnvironmentVariable("RECIPE_AI_PROVIDER", "deepseek", "User")
[Environment]::SetEnvironmentVariable("RECIPE_AI_KEY", "sk-你的DeepSeekKey", "User")

# 方式三：本地 Ollama（零成本，完全离线）
[Environment]::SetEnvironmentVariable("RECIPE_AI_PROVIDER", "ollama", "User")
```

不配置也能用，自动降级为规则引擎（同样有季节和星期智能）。

### 4. 测试运行

```bash
# Dry run（不推送，验证全流程）
python daily_runner.py --dry

# 指定菜名测试
python daily_runner.py --dish "宫保鸡丁"

# 规则引擎模式（无需 AI API）
python daily_runner.py --mock --dry
```

### 5. 设置每日自动推送

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File "install_schedule.ps1"
```

**Linux/Mac:**
```bash
crontab -e
# 0 10 * * * cd /path/to/project && python daily_runner.py
```

## 文件说明

| 文件 | 作用 |
|------|------|
| [`daily_runner.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/daily_runner.py) | 主入口，一条命令跑全流程 |
| [`ai_selector.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/ai_selector.py) | MiniMax AI 选菜 + 规则引擎降级 |
| [`bilibili_search.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/bilibili_search.py) | B站视频搜索 + 质量筛选 |
| [`wechat_push.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/wechat_push.py) | 推送（飞书/企业微信/WxPusher/PushPlus/Server酱） |
| [`config.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/config.py) | 集中配置 |
| [`extract_recipes.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/extract_recipes.py) | 菜谱提取（一次性） |
| [`install_schedule.ps1`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/install_schedule.ps1) | Windows 定时任务 |
| [`landing_server.py`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/landing_server.py) | Landing Page API |
| [`landing/`](https://github.com/zoebischuribe-cloud/sunny-life-tools/tree/master/food/daily-recipe-push/landing) | H5 落地页 |
| [`recipes.json`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/recipes.json) | 357 道菜谱 |
| [`docs/SOP.md`](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/docs/SOP.md) | **完整从0到1搭建文档** |

## 成本

| 项目 | 月成本 |
|------|--------|
| MiniMax AI | ~¥2-5 |
| 飞书推送 | ¥0 |
| B站搜索 | ¥0 |
| **总计** | **~¥2-5/月** |

## 完整SOP

详见 [完整 SOP 文档](https://github.com/zoebischuribe-cloud/sunny-life-tools/blob/master/food/daily-recipe-push/docs/SOP.md) — 从环境准备到定时任务，10个Phase完整教程，可复现。
