# 每日新闻 Podcast 生成指南

## 功能说明

基于 [notebooklm-py](https://github.com/teng-lin/notebooklm-py) 实现，将每日新闻摘要自动转换为专业的播客音频。

## 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装浏览器驱动（用于 NotebookLM 认证）
playwright install chromium
```

## 配置认证

首次使用需要进行 NotebookLM 认证：

```bash
notebooklm login
```

这会打开浏览器，让你登录 Google 账号以授权访问 NotebookLM。认证信息会保存到本地，后续使用无需重复登录。

## 使用方法

### 基本用法

```bash
# 为昨天的新闻生成 podcast（默认）
python scripts/generate_podcast.py

# 为指定日期生成 podcast
python scripts/generate_podcast.py --date 2026-02-10
```

### 高级选项

```bash
# 异步模式：提交任务后立即返回（推荐）
python scripts/generate_podcast.py --date 2026-02-10 --no-wait

# 同步模式：等待生成完成（需要3-5分钟）
python scripts/generate_podcast.py --date 2026-02-10

# 自定义等待超时时间（秒）
python scripts/generate_podcast.py --date 2026-02-10 --timeout 900

# 选择不同的 podcast 格式
python scripts/generate_podcast.py --date 2026-02-10 --format debate

# 调整 podcast 长度
python scripts/generate_podcast.py --date 2026-02-10 --length long

# 完整示例
python scripts/generate_podcast.py \
  --date 2026-02-10 \
  --format deep-dive \
  --length default \
  --language zh \
  --no-wait
```

### 下载异步生成的 Podcast

```bash
# 下载最新的 podcast
python scripts/download_podcast.py

# 下载指定日期的 podcast
python scripts/download_podcast.py --date 2026-02-10

# 使用 notebook ID 下载
python scripts/download_podcast.py --notebook-id abc123def456

# 检查所有 podcast 状态
python scripts/check_podcast_status.py
```

### 参数说明

- `--date`: 指定日期（格式：YYYY-MM-DD），默认为昨天
- `--no-wait`: 异步模式，提交任务后立即返回（推荐用于自动化）
- `--timeout`: 同步模式的超时时间（秒），默认 600
- `--format`: Podcast 格式
  - `deep-dive`: 深度讨论（默认）
  - `brief`: 简要概述
  - `critique`: 批判性分析
  - `debate`: 辩论形式
- `--length`: Podcast 长度
  - `short`: 短版本（约5-10分钟）
  - `default`: 标准版本（约10-15分钟，默认）
  - `long`: 长版本（约15-20分钟）
- `--language`: 语言代码（默认：zh 中文）

## 输出文件

生成的文件保存在 `data/podcasts/` 目录：

- `{date}_podcast.mp3`: 生成的音频文件
- `{date}_metadata.json`: 元数据信息
- `{date}_content.md`: 用于生成的新闻内容（临时文件）

## 工作流程

1. **读取新闻摘要**: 从 `data/summaries/{date}.json` 加载每日新闻
2. **格式化内容**: 将 JSON 格式转换为适合播客的 Markdown 文本
3. **创建 Notebook**: 在 NotebookLM 中创建新的笔记本
4. **添加内容**: 将新闻内容作为源添加到笔记本
5. **生成音频**: 使用 AI 生成专业的播客音频
6. **下载保存**: 将生成的音频文件下载到本地

## 注意事项

1. **生成时间**: 每个 podcast 生成需要 3-5 分钟，请耐心等待
2. **API 限制**: NotebookLM 可能有使用频率限制，建议不要频繁调用
3. **内容质量**: 确保新闻摘要文件存在且格式正确
4. **网络连接**: 需要稳定的网络连接访问 Google NotebookLM
5. **Notebook 保留**: 默认保留生成的 Notebook 供审查，可在脚本中修改为自动删除

## 示例输出

```json
{
  "date": "2026-02-10",
  "notebook_id": "abc123...",
  "task_id": "task_xyz...",
  "audio_format": "deep-dive",
  "audio_length": "default",
  "language": "zh",
  "total_items": 4,
  "categories": ["商业", "新闻", "技术", "设计"],
  "generated_at": "2026-02-10T15:30:00",
  "output_file": "/path/to/podcasts/2026-02-10_podcast.mp3"
}
```

## GitHub Actions 自动化

项目已配置 GitHub Actions 自动化流程，可以自动生成和下载 podcast。

### 配置说明

详细配置请参考：[GitHub Actions Podcast 自动化配置指南](.github/PODCAST_AUTOMATION.md)

**快速配置：**

1. 在本地运行认证：`notebooklm login`
2. 获取认证文件：`cat ~/.notebooklm/storage_state.json`
3. 在 GitHub 仓库 Settings > Secrets 中添加 `NOTEBOOKLM_STORAGE_STATE`
4. 粘贴完整的 JSON 内容作为 secret 值

### 自动化流程

1. **生成 Podcast**: 每日摘要完成后自动触发（异步模式）
2. **下载 Podcast**: 每 12 小时检查并下载已完成的 podcast
3. **手动触发**: 可在 Actions 页面手动触发任意日期的生成

### 手动触发

在 GitHub 仓库的 Actions 页面：

1. 选择 "Generate Daily Podcast" workflow
2. 点击 "Run workflow"
3. 填写参数（可选）
4. 点击运行

## 本地自动化（可选）

也可以将 podcast 生成添加到本地定时任务中：

```bash
# 在 crontab 中添加（每天早上 7:00 生成前一天的 podcast）
0 7 * * * cd /path/to/AutoRss && python scripts/generate_podcast.py
```

## 故障排查

### 认证失败
```bash
# 重新登录
notebooklm login
```

### 找不到新闻摘要
```bash
# 检查摘要文件是否存在
ls data/summaries/

# 先运行新闻分析
python scripts/analyze_rss.py --date 2026-02-10
```

### 生成超时
- 检查网络连接
- 等待后重试
- 可以调整脚本中的 timeout 参数

## 相关资源

- [notebooklm-py GitHub](https://github.com/teng-lin/notebooklm-py)
- [NotebookLM 官方网站](https://notebooklm.google.com/)
- [项目主文档](README.md)
