# Daily GuGuWen — 每日小古文推送

基于凯叔《每日小古文》本地资源，每天自动生成一首古文推送（原文 + 出处 + 图卡 + 讲解音频）。

## 资源要求

你需要有凯叔《每日小古文》的两个本地文件夹：

| 文件夹 | 内容 | 示例 |
|--------|------|------|
| `每日小古文音频/` | MP3 讲解音频，376集 | `001《论语》：不怨天，不尤人.mp3` |
| `图片/` | 图卡 JPG，每集3张（大卡/小卡/长文稿） | `001不怨天，不尤人/大卡.jpg` |

## 快速开始

### 1. 建立索引（只需执行一次）

```bash
python scripts/indexer.py \
  --audio "D:/Download/百度网盘下载/每日小古文音频" \
  --images "D:/Download/百度网盘下载/图片" \
  --output index.json
```

索引会自动匹配编号，输出统计：
```
索引完成: 共 365 首
  有音频+图片: 300
  仅有音频: 65
```

### 2. 生成今日推送

```bash
python scripts/generate.py --index index.json -o today.md
```

### 3. 查看输出

```bash
cat today.md
```

## 高级用法

```bash
# 指定编号
python scripts/generate.py --index index.json --number 42 -o today.md

# 随机一首（避免重复）
python scripts/generate.py --index index.json --random -o today.md

# 明天的推送
python scripts/generate.py --index index.json --day tomorrow -o tomorrow.md

# 昨天的推送
python scripts/generate.py --index index.json --day yesterday -o yesterday.md
```

## 安装到 OpenClaw

```bash
# 手动复制
xcopy /E /I daily-guguwen %USERPROFILE%\.openclaw\skills\daily-guguwen
```

然后在 OpenClaw 中触发：

```
/小古文
今天的小古文
推一首古文
```

## 定时推送

参考 `SKILL.md` 中的 GitHub Actions 配置，每天早上7点自动生成并推送到家长微信。

## 推送示例

```markdown
📜 每日小古文 · 第1集

**出处**：《论语》
**原文**：不怨天，不尤人

![大卡](D:/Download/百度网盘下载/图片/.../大卡.jpg)
![长文稿](D:/Download/百度网盘下载/图片/.../长文稿.jpg)

🎧 [点击收听讲解音频](file://D:/Download/百度网盘下载/每日小古文音频/...)

---
📝 今日任务
1. 大声朗读原文3遍
2. 理解意思后能用自己的话讲给家人听
3. 想一想：生活中什么时候可以用到这句话？
```

## 常见问题

**Q: 索引器报错找不到图片？**
确保图片目录路径正确，且子文件夹命名包含编号前缀（如 `001` `241` `251`）。

**Q: 推送里的图片链接在手机上打不开？**
图片引用的是本地文件路径。要推送到手机，需要：
1. 将图片上传到图床/云存储获取公开URL
2. 或使用支持本地文件转发的机器人（如企业微信上传临时素材API）

**Q: 音频能直接嵌入推送吗？**
大多数推送渠道（飞书/企业微信/钉钉）支持 Markdown 但不支持本地音频链接。建议：
- 将音频上传到云存储获取URL
- 或使用机器人 API 上传语音素材

## 许可

MIT