# ☀️ JIF — 一分钟查期刊影响因子

最轻量的期刊 JIF 查询工具包。3 个文件，零依赖。

## 文件清单

```
jif/
├── jif.sh          # macOS/Linux/WSL 终端脚本
├── jif.ps1         # Windows PowerShell 脚本
└── AI_PROMPT.md    # 传授给 ChatGPT/DeepSeek 等 AI 的系统指令
```

## 用法

### 终端（Bash）

```bash
chmod +x jif.sh
./jif.sh nature
# → Nature Impact Factor 2026: 48.5, Trend, Selectivity

./jif.sh "nucleic acids research"
# → Nucleic Acids Research Impact Factor 2026: 13.1

# 无代理环境
JIF_PROXY="" ./jif.sh bioinformatics
```

### 终端（PowerShell）

```powershell
.\jif.ps1 nature
.\jif.ps1 "nature communications"
```

### AI 助手

复制 `AI_PROMPT.md` 全文 → 粘贴到任意 AI 的系统提示词区域 → 对 AI 说：

```
用JIF查 Nature 的 IF、接收率和审稿速度
用JIF找肠道菌群 5-10 分 Q1 期刊
用JIF查审稿<2个月的生物信息学期刊
```

## 数据源

所有 IF 数据来自 [ManuSights](https://manusights.com/)，对照 Clarivate 2024 JCR 官方数据验证，准确率 100%。

## 依赖

- `curl`（bash）或 `Invoke-WebRequest`（PowerShell）— 均为系统自带
- 中国大陆需配置代理：`export JIF_PROXY=http://127.0.0.1:7890`

## License

MIT
