# 快速开始：生成每日新闻 Podcast

## 🚀 推荐工作流（异步模式）

### 1. 生成 Podcast（异步）

```bash
# 为今天的新闻生成 podcast（后台运行）
python scripts/generate_podcast.py --no-wait

# 输出示例：
# ✅ Notebook 已创建: 4e1df1ff-...
# ✅ 内容已添加为源
# 🚀 异步模式：Podcast 正在后台生成
#    Notebook ID: 4e1df1ff-6076-4932-9821-5156019f73af
#    访问: https://notebooklm.google.com/notebook/4e1df1ff-...
```

### 2. 等待生成（约 5-10 分钟）

你可以：
- ☕ 喝杯咖啡
- 📧 查看邮件  
- 💻 继续其他工作

### 3. 下载 Podcast

```bash
# 方式1: 使用日期下载（推荐）
python scripts/download_podcast.py --date 2026-02-10

# 方式2: 使用 Notebook ID
python scripts/download_podcast.py --notebook-id 4e1df1ff-6076-4932-9821-5156019f73af

# 方式3: 不指定参数，自动下载最新的
python scripts/download_podcast.py
```

### 4. 收听

```bash
# macOS
open data/podcasts/2026-02-10_podcast.mp3

# Linux
xdg-open data/podcasts/2026-02-10_podcast.mp3
```

---

## 📝 同步模式（等待完成）

如果你想等待生成完成后直接下载：

```bash
# 默认超时 10 分钟
python scripts/generate_podcast.py --date 2026-02-10

# 自定义超时 15 分钟
python scripts/generate_podcast.py --date 2026-02-10 --timeout 900
```

**注意**：同步模式可能会超时，建议使用异步模式。

---

## 🎨 自定义选项

### 不同格式

```bash
# 简要概述（最快）
python scripts/generate_podcast.py --format brief --no-wait

# 批判分析
python scripts/generate_podcast.py --format critique --no-wait

# 辩论形式（最有趣）
python scripts/generate_podcast.py --format debate --no-wait
```

### 不同长度

```bash
# 短版（5-10分钟）
python scripts/generate_podcast.py --length short --no-wait

# 长版（15-20分钟）
python scripts/generate_podcast.py --length long --no-wait
```

### 组合使用

```bash
# 辩论形式 + 长版本
python scripts/generate_podcast.py \
  --format debate \
  --length long \
  --no-wait
```

---

## 🔍 查看进度

### 方法1：访问 NotebookLM 网页

从生成时的输出中复制 URL，例如：
```
https://notebooklm.google.com/notebook/4e1df1ff-6076-4932-9821-5156019f73af
```

### 方法2：检查元数据文件

```bash
# 查看元数据
cat data/podcasts/2026-02-10_metadata.json

# 提取 Notebook ID
cat data/podcasts/2026-02-10_metadata.json | grep notebook_id
```

---

## ⚡ 自动化

### 每日定时生成

添加到 crontab：

```bash
# 编辑 crontab
crontab -e

# 每天早上 7:00 生成前一天的 podcast（异步）
0 7 * * * cd /path/to/AutoRss && python scripts/generate_podcast.py --no-wait >> logs/podcast.log 2>&1

# 每天早上 7:30 下载（给生成 30 分钟时间）
30 7 * * * cd /path/to/AutoRss && python scripts/download_podcast.py >> logs/podcast_download.log 2>&1
```

---

## 🛠️ 故障排查

### 问题1：找不到新闻摘要

```bash
# 先生成摘要
python scripts/analyze_rss.py --date 2026-02-10

# 然后生成 podcast
python scripts/generate_podcast.py --date 2026-02-10 --no-wait
```

### 问题2：下载时未找到音频

可能还在生成中，请：
1. 访问 NotebookLM 网页查看进度
2. 等待几分钟后重试下载

### 问题3：认证失败

```bash
# 重新登录
notebooklm login

# 重试
python scripts/generate_podcast.py --no-wait
```

---

## 📊 完整工作流示例

```bash
#!/bin/bash
# 每日新闻处理完整流程

DATE=$(date -v-1d +%Y-%m-%d)  # 昨天（macOS）
# DATE=$(date -d "1 day ago" +%Y-%m-%d)  # 昨天（Linux）

echo "=== 处理 $DATE 的新闻 ==="

# 1. 获取 RSS
python scripts/fetch_rss.py

# 2. AI 分析
python scripts/analyze_rss.py --date $DATE

# 3. 生成 Podcast（异步）
python scripts/generate_podcast.py --date $DATE --format deep-dive --no-wait

# 4. 更新 Web 数据
python scripts/generate_static_data.py

echo "=== Podcast 正在后台生成，稍后可下载 ==="
echo "下载命令: python scripts/download_podcast.py --date $DATE"
```

---

## 💡 提示

1. **首次使用**：运行 `./setup_podcast.sh` 进行一键安装和配置
2. **推荐格式**：日常收听用 `brief` 或 `deep-dive`，深度学习用 `critique` 或 `debate`
3. **异步优先**：使用 `--no-wait` 可避免长时间等待
4. **批量生成**：可以同时提交多个日期的生成任务
5. **保留 Notebook**：方便后续重新下载或查看

---

查看更多示例：[PODCAST_EXAMPLES.md](PODCAST_EXAMPLES.md)  
完整文档：[README_PODCAST.md](README_PODCAST.md)
