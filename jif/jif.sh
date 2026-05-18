#!/bin/bash
# jif.sh — 一行命令查期刊 JIF（Journal Impact Factor）
# 数据源: ManuSights (manusights.com)
# 用法: ./jif.sh <期刊名>
# 示例: ./jif.sh nature
#       ./jif.sh "nature communications"
#       ./jif.sh bioinformatics

set -e

JOURNAL="${1:-}"
if [ -z "$JOURNAL" ]; then
  echo "用法: jif <期刊名>"
  echo "示例: jif nature"
  echo "      jif \"nature communications\""
  exit 1
fi

# slug: 全小写 + 空格转连字符
SLUG=$(echo "$JOURNAL" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

# 代理设置（如需）
PROXY="${JIF_PROXY:-http://127.0.0.1:7890}"
CURL_OPTS="-sL --max-time 15"
if [ -n "$JIF_PROXY" ]; then
  CURL_OPTS="$CURL_OPTS -x $PROXY"
fi

RESULT=$(curl $CURL_OPTS "https://manusights.com/blog/${SLUG}-impact-factor" 2>/dev/null | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')

if echo "$RESULT" | grep -q "Journal Guides"; then
  echo "❌ 期刊未收录: $JOURNAL"
  echo "💡 尝试搜索: site:manusights.com $JOURNAL impact factor"
  exit 1
fi

echo "$RESULT"
