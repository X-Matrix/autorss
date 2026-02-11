# Podcast 生成示例

本文档展示如何使用 `generate_podcast.py` 为每日新闻生成播客的各种场景。

## 前置条件

确保已经完成安装和认证：

```bash
# 方法1：使用安装脚本（推荐）
./setup_podcast.sh

# 方法2：手动安装
pip install -r requirements.txt
playwright install chromium
notebooklm login
```

## 基础示例

### 示例 1：生成昨天的新闻播客

```bash
python scripts/generate_podcast.py
```

输出示例：
```
[INFO] 目标日期: 2026-02-09
[INFO] 成功加载 2026-02-09 的新闻摘要，共 12 条资讯
[INFO] 内容已保存到临时文件：data/podcasts/2026-02-09_content.md
[INFO] 创建 notebook: 每日科技资讯 - 2026-02-09
[SUCCESS] Notebook 已创建: abc123xyz...
[SUCCESS] 内容已添加为源: src_456def...
[INFO] 开始生成 podcast (格式: deep-dive, 长度: default)...
[INFO] 等待生成完成（这可能需要几分钟）...
[SUCCESS] Podcast 生成成功！
[SUCCESS] Podcast 已保存到: data/podcasts/2026-02-09_podcast.mp3
🎉 Podcast 生成完成！
```

### 示例 2：为特定日期生成播客

```bash
python scripts/generate_podcast.py --date 2026-02-10
```

这会为 2026-02-10 的新闻生成播客。

## 格式选择

### 示例 3：深度讨论格式（默认）

适合详细分析和深入探讨：

```bash
python scripts/generate_podcast.py --format deep-dive
```

特点：
- 两位主持人深入讨论每条新闻
- 分析趋势和影响
- 约 10-15 分钟

### 示例 4：简要概述格式

快速浏览当日要闻：

```bash
python scripts/generate_podcast.py --format brief
```

特点：
- 快速概览所有新闻
- 突出关键信息
- 约 5-8 分钟

### 示例 5：批判分析格式

对新闻进行批判性思考：

```bash
python scripts/generate_podcast.py --format critique
```

特点：
- 分析新闻背后的动机
- 质疑和反思
- 多角度看待问题

### 示例 6：辩论格式

两种观点的激烈交锋：

```bash
python scripts/generate_podcast.py --format debate
```

特点：
- 正反两方观点对立
- 激烈但专业的讨论
- 更具娱乐性和启发性

## 长度调整

### 示例 7：短版本（5-10分钟）

适合通勤或短暂休息时收听：

```bash
python scripts/generate_podcast.py --length short
```

### 示例 8：标准版本（10-15分钟）

平衡深度和时长：

```bash
python scripts/generate_podcast.py --length default
```

### 示例 9：长版本（15-20分钟）

深入讨论，适合学习和研究：

```bash
python scripts/generate_podcast.py --length long
```

## 组合使用

### 示例 10：辩论形式 + 长版本

```bash
python scripts/generate_podcast.py \
  --date 2026-02-10 \
  --format debate \
  --length long
```

这会生成一个约 15-20 分钟的辩论式播客，非常适合深入了解复杂议题。

### 示例 11：简要概述 + 短版本

```bash
python scripts/generate_podcast.py \
  --date 2026-02-10 \
  --format brief \
  --length short
```

最快速的每日新闻播报，5 分钟左右完成收听。

### 示例 12：批判分析 + 标准版本

```bash
python scripts/generate_podcast.py \
  --date 2026-02-10 \
  --format critique \
  --length default
```

深度思考当日新闻，培养批判性思维。

## 批量生成

### 示例 13：为过去一周生成播客

```bash
#!/bin/bash
# 生成过去7天的播客

for i in {1..7}; do
    date=$(date -v-${i}d +%Y-%m-%d)  # macOS
    # date=$(date -d "${i} days ago" +%Y-%m-%d)  # Linux
    
    echo "生成 $date 的播客..."
    python scripts/generate_podcast.py --date $date --format deep-dive
    
    # 避免请求过于频繁
    sleep 300  # 等待5分钟
done
```

### 示例 14：定时任务

将播客生成添加到 crontab：

```bash
# 编辑 crontab
crontab -e

# 添加任务：每天早上 7:00 生成前一天的播客
0 7 * * * cd /path/to/AutoRss && /usr/bin/python3 scripts/generate_podcast.py >> logs/podcast_$(date +\%Y\%m\%d).log 2>&1
```

## 输出文件说明

生成后会在 `data/podcasts/` 目录下看到：

```
data/podcasts/
├── 2026-02-09_podcast.mp3      # 音频文件（可直接播放）
├── 2026-02-09_metadata.json    # 元数据
└── 2026-02-09_content.md       # 原始内容
```

### 元数据示例

```json
{
  "date": "2026-02-09",
  "notebook_id": "abc123xyz",
  "task_id": "task_456def",
  "audio_format": "deep-dive",
  "audio_length": "default",
  "language": "zh",
  "total_items": 12,
  "categories": ["技术", "AI/机器学习", "开源项目", "科学"],
  "generated_at": "2026-02-10T08:30:45.123456",
  "output_file": "/path/to/data/podcasts/2026-02-09_podcast.mp3"
}
```

## 常见场景

### 场景 1：每日早晨通勤

```bash
# 短版简要概述，快速了解资讯
python scripts/generate_podcast.py --format brief --length short
```

### 场景 2：午休学习

```bash
# 标准深度讨论，平衡时长和深度
python scripts/generate_podcast.py --format deep-dive --length default
```

### 场景 3：周末深度学习

```bash
# 长版批判分析，深入思考
python scripts/generate_podcast.py --format critique --length long
```

### 场景 4：团队分享讨论

```bash
# 辩论格式，激发讨论
python scripts/generate_podcast.py --format debate --length default
```

## 故障处理示例

### 找不到新闻摘要

```bash
# 先检查摘要是否存在
ls data/summaries/2026-02-10.json

# 如果不存在，先生成摘要
python scripts/analyze_rss.py --date 2026-02-10

# 然后再生成播客
python scripts/generate_podcast.py --date 2026-02-10
```

### 认证过期

```bash
# 重新登录
notebooklm login

# 然后重试
python scripts/generate_podcast.py
```

### 网络超时

脚本会自动重试，如果仍然失败：

```bash
# 检查网络连接
ping google.com

# 稍后重试
python scripts/generate_podcast.py --date 2026-02-10
```

## 高级技巧

### 自定义指令（修改脚本）

编辑 `scripts/generate_podcast.py`，找到 `instructions` 变量：

```python
instructions = (
    f"这是 {date_str} 的科技资讯摘要。"
    "请用专业但轻松的语调，为听众呈现今日科技新闻的亮点。"
    "重点突出各个领域的创新动态和重要趋势。"
    "适当加入主持人之间的互动讨论，使内容更生动有趣。"
    # 👇 添加你的自定义指令
    "特别关注 AI 和机器学习相关的内容。"
)
```

### 保留 Notebook 供审查

默认情况下，脚本会保留生成的 Notebook。可以通过 NotebookLM 网页界面查看：

```bash
# 从元数据文件中获取 notebook_id
cat data/podcasts/2026-02-10_metadata.json | grep notebook_id
```

然后访问：`https://notebooklm.google.com/notebook/<notebook_id>`

## 完整工作流示例

### 从 RSS 到 Podcast 的完整流程

```bash
#!/bin/bash
# 完整的每日新闻处理流程

DATE=$(date -v-1d +%Y-%m-%d)  # 昨天的日期

echo "=== 开始处理 $DATE 的新闻 ==="

# 1. 获取 RSS
echo "1. 获取 RSS 订阅..."
python scripts/fetch_rss.py

# 2. AI 分析
echo "2. AI 分析和翻译..."
python scripts/analyze_rss.py --date $DATE

# 3. 生成 Podcast
echo "3. 生成 Podcast..."
python scripts/generate_podcast.py --date $DATE --format deep-dive --length default

# 4. 更新 Web 数据
echo "4. 更新 Web 数据..."
python scripts/generate_static_data.py

echo "=== 完成！==="
echo "Podcast 位置: data/podcasts/${DATE}_podcast.mp3"
```

## 播放和分享

### 本地播放

```bash
# macOS
open data/podcasts/2026-02-10_podcast.mp3

# Linux
xdg-open data/podcasts/2026-02-10_podcast.mp3
```

### 上传到播客平台

生成的 MP3 文件可以上传到：
- Apple Podcasts
- Spotify
- Google Podcasts
- 其他播客托管平台

或者直接分享给朋友！

---

更多信息请参考：
- [完整文档](README_PODCAST.md)
- [NotebookLM 官方文档](https://github.com/teng-lin/notebooklm-py)
