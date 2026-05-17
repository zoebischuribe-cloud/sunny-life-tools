---
name: daily-guguwen
description: 每日小古文推送 Skill。从本地凯叔每日小古文资源库中自动匹配音频+图卡，每天推送一首古文原文、出处、讲解音频和配图。
keywords:
  - 古文
  - 小古文
  - 每日推送
  - 语文
  - 凯叔
  - 教育
  - 传统文化
license: MIT
---

# Daily GuGuWen — 每日小古文推送

从本地凯叔《每日小古文》资源库中，每天自动选一首古文，输出包含原文、出处、图卡和音频路径的推送文案。

## 触发方式

自然语言触发：
- `/小古文`
- `/每日古文`
- `今天的小古文`
- `推一首古文`

## 前置要求

1. **建立索引**（首次使用必须执行）：

```bash
python daily-guguwen/scripts/indexer.py \
  --audio "D:/Download/百度网盘下载/每日小古文音频" \
  --images "D:/Download/百度网盘下载/图片" \
  --output daily-guguwen/index.json
```

2. **索引完成后**，即可生成每日推送：

```bash
# 生成今日推送
python daily-guguwen/scripts/generate.py --index daily-guguwen/index.json -o today.md

# 指定编号
python daily-guguwen/scripts/generate.py --index daily-guguwen/index.json --number 42 -o today.md

# 随机一首
python daily-guguwen/scripts/generate.py --index daily-guguwen/index.json --random -o today.md
```

## 工作原理

```
音频目录  +  图片目录
   |            |
   v            v
 indexer.py  (扫描匹配)
       |
       v
  index.json  (编号→音频→图卡映射)
       |
       v
 generate.py  (按日期/编号/随机选择)
       |
       v
  Markdown推送  (原文+出处+图卡+音频路径)
```

### 音频文件名解析

格式：`001《论语》：不怨天，不尤人.mp3`
- 编号：001
- 出处：《论语》
- 原文：不怨天，不尤人

### 图片匹配规则

按编号在图片目录中递归查找匹配的图卡文件夹：
- `001不怨天，不尤人`
- `241德不孤（图卡）`
- `251虽不能至（图卡）`（在 `251-300集` 子目录中）

每张图卡含3张图片：
- **大卡** — 主展示图
- **小卡** — 缩略图/手机屏保
- **长文稿** — 完整讲解文稿配图

## 输出格式

```markdown
📜 每日小古文 · 第42集

**出处**：《史记》
**原文**：飞鸟尽，良弓藏

![大卡](D:/Download/百度网盘下载/图片/.../大卡.jpg)
![长文稿](D:/Download/百度网盘下载/图片/.../长文稿.jpg)

🎧 [点击收听讲解音频](file://D:/Download/百度网盘下载/每日小古文音频/...)

---
📝 今日任务
1. 大声朗读原文3遍
2. 理解意思后能用自己的话讲给家人听
3. 想一想：生活中什么时候可以用到这句话？

---
📋 家长备注
- 本集编号：42
- 图片文件夹：...
- 音频文件：...
```

## 定时推送配置（GitHub Actions）

```yaml
name: Daily GuGuWen
on:
  schedule:
    - cron: '0 23 * * *'  # UTC 23:00 = 北京时间早7点
  workflow_dispatch:

jobs:
  push:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: python daily-guguwen/scripts/generate.py --index daily-guguwen/index.json -o output.md
      # 此处添加推送到微信/飞书的步骤
```

## 文件结构

```
daily-guguwen/
├── SKILL.md              # 本文件
├── README.md             # 使用说明
├── index.json            # 生成的索引（运行 indexer.py 后生成）
├── .history.json         # 播放历史（自动生成）
└── scripts/
    ├── indexer.py        # 资源扫描索引器
    └── generate.py       # 推送生成器
```

## 注意事项

1. 索引文件 `index.json` 只需在资源变动时重新生成
2. 图片引用的是本地绝对路径，在推送时需要根据实际渠道调整（如上传图床获取URL）
3. 音频为本地文件路径，企业微信/飞书机器人不支持直接发送本地文件，需上传后获取URL