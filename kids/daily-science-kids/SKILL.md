---
name: daily-science-kids
description: 每日儿童跨学科科普知识推送 Skill。从结构化知识库中按学科轮替抽取知识点，根据孩子年级（小学/初中）自动生成揭秘式科普文案，支持定时推送和家长审核。
keywords:
  - education
  - kids
  - science
  - daily-push
  - STEM
  - 科普
  - 儿童教育
  - 每日推送
license: MIT
---

# Daily Science Kids — 每日儿童科普推送

每天为孩子生成一篇跨学科趣味科普推送，涵盖科技、物理、化学、自然、地理时政、英语六大领域。

## 触发方式

自然语言触发：
- `/科普时间`
- `/今日知识`
- `/daily-science`
- `今天给孩子讲什么`
- `生成今日科普`

## 核心工作流

### Step 1: 读取知识库

读取 `knowledge_base.yaml`（默认路径：与脚本同级目录或用户根目录下的 `knowledge_base.yaml`）。

如果找不到文件，提示用户：
> 未找到 knowledge_base.yaml，请先准备知识库文件。可以从以下路径获取模板：
> https://github.com/（用户自行托管）

### Step 2: 确定今日学科

根据星期几自动选择学科：

| 星期 | 学科 | 图标 |
|------|------|------|
| 周一 | 科技前沿 | 🚀 |
| 周二 | 物理世界 | ⚡ |
| 周三 | 自然探秘 | 🌿 |
| 周四 | 化学奥秘 | 🧪 |
| 周五 | 天下大事 | 🌍 |
| 周六 | 英语趣谈 | 🗣️ |
| 周日 | 惊喜知识 | 🎁 |

### Step 3: 选择知识点

在同学科中，排除最近 30 天内已使用过的知识点，随机选择一条。首次使用无历史限制。

### Step 4: 生成推送文案

根据 `grade_level` 生成不同风格：

**小学版（elementary）**：
- 语气：像大哥哥/大姐姐一样耐心，多用比喻
- 每段不超过 3 句话
- 多使用"你有没有想过""其实呀""在我们身边"等亲切引导词

**初中版（junior_high）**：
- 语气：知识型但不枯燥，有逻辑链条
- 适当使用学科术语（如"折射率""电化学腐蚀""电磁感应"）
- 包含"原理解析""实际应用"等结构化板块

### Step 5: 输出格式

生成 Markdown 格式文案，可直接复制到微信/飞书/企业微信发送。

---

## 脚本调用

### 生成今日推送

```bash
# 小学版
python scripts/generate.py --grade elementary

# 初中版（默认）
python scripts/generate.py --grade junior_high

# 指定知识库路径
python scripts/generate.py --grade elementary --kb /path/to/knowledge_base.yaml
```

### 查看使用历史

```bash
python scripts/generate.py --history
```

### 强制指定学科（覆盖星期规则）

```bash
python scripts/generate.py --grade elementary --category physics
```

---

## 输出示例

### 小学版

```markdown
🚀 今天发现了一个超酷的事情！

你有没有想过？你每天都在扫的二维码，黑白格子其实只代表两个数字——0和1。但它为什么能装下那么多信息？

其实呀：二维码的本质是二进制编码。黑色格子代表1，白色格子代表0。三个角落的大方块是"定位点"，让手机知道从哪开始读。中间密密麻麻的小格子存储信息，最多能装下7089个数字！

在我们身边：健康码、支付码、WiFi密码共享……二维码已经成为数字世界的"通用语言"。

更神奇的是：二维码是日本工程师原昌宏在1994年发明的，初衷是为了追踪丰田汽车的零部件。他从来没想过，30年后全世界的人每天都会扫它几十次。

来考考你：为什么二维码三个角都有大方块，但右下角没有？
```

### 初中版

```markdown
🚀 【科技前沿】二维码的秘密

❓ 问题引入：你每天都在扫的二维码，黑白格子其实只代表两个数字——0和1。但它为什么能装下那么多信息？

🔬 原理解析：二维码的本质是二进制编码。黑色格子代表1，白色格子代表0。三个角落的大方块是"定位点"（Position Detection Pattern），让扫码设备快速定位和解码。中间数据区使用 Reed-Solomon 纠错算法，即使污损30%，依然能被正确识别。Version 25 的二维码（117×117格子）可编码约3000个汉字。

🎯 实际应用：健康码、移动支付、物流追踪、门票验证。二维码已成为物联网时代的"低成本信息入口"。

💡 拓展冷知识：二维码的组合数约为 2^13000，远超宇宙原子总数（约 10^80）。理论上，二维码永远不会被"用完"。

📝 思考题：为什么二维码三个角都有大方块定位点，但右下角没有？这种不对称设计有什么作用？
```

---

## 家长审核机制

每次生成后，文案应**先发给家长确认**，再转发给孩子。

脚本会在输出末尾附加 `parent-note` 提示：

```
---
📋 家长审核备注
- 本推送由 AI 根据预置知识库生成，核心事实经过校验
- 思考题答案：...
- 如需跳过审核直接发送给孩子，设置环境变量：SKIP_PARENT_REVIEW=1
```

---

## 定时推送配置（GitHub Actions）

创建 `.github/workflows/daily-science.yml`：

```yaml
name: Daily Science Kids
on:
  schedule:
    - cron: '0 23 * * *'  # UTC 23:00 = 北京时间早7点
  workflow_dispatch:

jobs:
  push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install pyyaml
      - run: python daily-science-kids/scripts/generate.py --grade elementary
      - run: |
          # 推送到企业微信/飞书机器人
          curl -X POST "$WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d '{"msgtype": "markdown", "markdown": {"content": "'"$(cat output.md | sed 's/"/\\"/g')"'"}}'
        env:
          WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
```

---

## 依赖

- Python 3.8+
- PyYAML (`pip install pyyaml`)

无其他外部依赖，纯本地运行。

---

## 文件结构

```
daily-science-kids/
├── SKILL.md              # 本文件
├── SOUL.md               # 语气与人格定义
├── README.md             # 使用说明
└── scripts/
    └── generate.py       # 核心生成脚本
```

---

## 扩展建议

1. **接入 Wikipedia MCP**：安装 `Rudra-ravi/wikipedia-mcp`，让 Agent 为知识点自动补充维基百科细节
2. **接入 OpenEdu MCP**：安装 `Cicatriiz/openedu-mcp`，扩展学科覆盖和年级适配
3. **家长面板**：定期汇总 `history.json` 生成月度学习报告
4. **语音版**：用 TTS（如 Edge-TTS、火山引擎）将文案转为音频，适合睡前听
