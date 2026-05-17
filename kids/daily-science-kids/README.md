# Daily Science Kids — 每日儿童科普推送

为中小学生设计的每日跨学科科普推送系统，基于 OpenClaw/Claude Code Skill 架构。

## 特色

- **6大学科轮替**：科技→物理→自然→化学→时政→英语，周日惊喜
- **年龄自适应**：小学版用比喻讲故事，初中版讲原理和逻辑
- **揭秘式结构**："你知道吗？→答案→生活例子→冷知识→思考题"
- **家长审核机制**：每次生成附带家长备注，可先审核再转发
- **零成本运行**：GitHub Actions 定时触发，无需服务器

## 快速开始

### 1. 安装依赖

```bash
pip install pyyaml
```

### 2. 准备知识库

将 `knowledge_base.yaml` 放到以下任一位置：
- 当前工作目录
- 用户主目录（`~/knowledge_base.yaml`）
- 或通过 `--kb` 参数指定

### 3. 生成今日推送

```bash
# 小学版
python daily-science-kids/scripts/generate.py --grade elementary

# 初中版
python daily-science-kids/scripts/generate.py --grade junior_high

# 保存到文件
python daily-science-kids/scripts/generate.py --grade elementary -o today.md
```

### 4. 查看使用历史

```bash
python daily-science-kids/scripts/generate.py --history
```

## 安装到 OpenClaw

```bash
# 在 OpenClaw 中执行
帮我安装这个 skill: /path/to/daily-science-kids
```

或手动复制到 skills 目录：

```bash
cp -r daily-science-kids ~/.openclaw/skills/
```

安装后，通过以下方式触发：

```
/科普时间
/今日知识
今天给孩子讲什么
```

## 定时推送（GitHub Actions）

复制以下工作流到 `.github/workflows/daily-science.yml`：

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
      - run: python daily-science-kids/scripts/generate.py --grade elementary -o output.md
      - run: |
          CONTENT=$(cat output.md | python -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
          curl -X POST "$WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"msgtype\": \"markdown\", \"markdown\": {\"content\": $CONTENT}}"
        env:
          WEBHOOK_URL: ${{ secrets.WEBHOOK_URL }}
```

配置企业微信/飞书机器人 webhook URL 到仓库 Secrets 中。

## 文件说明

| 文件 | 说明 |
|------|------|
| `SKILL.md` | OpenClaw 核心指令文件 |
| `SOUL.md` | 人格、语气、安全规则 |
| `scripts/generate.py` | 推送生成脚本 |
| `knowledge_base.yaml` | 知识点库（需自行准备） |

## 自定义知识库

`knowledge_base.yaml` 中的每条知识点遵循以下结构：

```yaml
- id: 唯一标识
  category: 学科分类（tech/physics/chemistry/nature/news/english/surprise）
  grade: 适用年级（如"小学-初中"）
  title: 知识点标题
  hook: 开场钩子（"你知道吗？……"）
  explanation: 核心解释/答案
  real_life: 生活中的例子
  fun_fact: 趣味冷知识
  question: 每日思考题
```

## 推送渠道建议

| 渠道 | 难度 | 稳定性 |
|------|------|--------|
| 企业微信机器人 | 低 | 高 |
| 飞书机器人 | 低 | 高 |
| 钉钉机器人 | 低 | 高 |
| 微信（Server酱/wxpusher） | 中 | 中 |
| 邮件（SMTP） | 低 | 高 |

## 许可

MIT
