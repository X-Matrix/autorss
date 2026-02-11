# GitHub Actions Podcast 自动化配置指南

本项目使用 GitHub Actions 自动生成和下载 podcast。

## 配置 GitHub Secrets

需要在 GitHub 仓库的 Settings > Secrets and variables > Actions 中配置以下 secrets：

### 1. NOTEBOOKLM_STORAGE_STATE ⚠️ 存储的是 JSON 内容，不是路径

这个 Secret 存储的是 NotebookLM 认证状态文件的**完整 JSON 内容**（不是文件路径）。

**获取方式：**

1. 在本地安装 notebooklm-py 和 Playwright：
   ```bash
   pip install notebooklm-py[browser]
   playwright install chromium
   ```

2. 运行 NotebookLM 认证（仅在本地运行一次）：
   ```bash
   notebooklm login
   ```

3. 认证成功后，读取存储的认证信息的**完整 JSON 内容**：
   ```bash
   cat ~/.notebooklm/storage_state.json
   ```

4. 复制整个 JSON 内容（包括所有的 cookies、origins、localStorage 等认证信息）

5. 在 GitHub 仓库中配置 Secret：
   - 进入 Settings > Secrets and variables > Actions
   - 点击 "New repository secret"
   - Name: `NOTEBOOKLM_STORAGE_STATE`
   - Value: 粘贴刚才复制的**完整 JSON 内容**（不是文件路径）
   - 点击 "Add secret"

**工作原理：**
```yaml
# GitHub Actions workflow 中
- name: Setup NotebookLM storage state
  env:
    NOTEBOOKLM_STORAGE_STATE_CONTENT: ${{ secrets.NOTEBOOKLM_STORAGE_STATE }}
  run: |
    mkdir -p ~/.notebooklm
    # 将 JSON 内容写入文件
    echo "$NOTEBOOKLM_STORAGE_STATE_CONTENT" > ~/.notebooklm/storage_state.json
    chmod 600 ~/.notebooklm/storage_state.json
```

**重要说明：**
- ✅ Secret 中存储的是 **JSON 文件内容**，不是路径
- ✅ GitHub Actions 将内容写入 `~/.notebooklm/storage_state.json`
- ✅ Python 脚本使用默认路径读取该文件
- ✅ **不需要**在 GitHub Actions 中安装 Playwright
- ✅ 本地认证只需运行一次，获取 JSON 内容后即可

**安全提示：** 
- 这个文件包含敏感的认证信息，不要公开分享
- 定期更新（建议每月重新认证一次）
- 如果认证失效，需要重新运行 `notebooklm login` 并更新 secret

### 2. OPENAI_API_KEY (已有)

用于 RSS 摘要分析，应该已经配置。

## Workflows 说明

### 1. Generate Daily Podcast (`generate_podcast.yml`)

**触发条件：**
- 自动：Daily RSS Summary workflow 完成后
- 手动：在 Actions 页面手动触发

**功能：**
- 为昨天的新闻生成 podcast
- 默认使用异步模式（提交任务后立即返回）
- 保存 metadata 用于后续下载

**手动触发选项：**
- `date`: 指定日期 (YYYY-MM-DD)
- `wait`: 是否等待生成完成（默认 false）

### 2. Download Pending Podcasts (`download_podcasts.yml`)

**触发条件：**
- 自动：每 12 小时运行一次
- 手动：在 Actions 页面手动触发

**功能：**
- 检查所有待下载的 podcast
- 尝试下载已完成生成的 podcast
- 更新静态数据文件

### 3. 完整流程

```
Fetch RSS feeds (每小时)
    ↓
Daily RSS Summary (RSS 更新后)
    ↓
Generate Daily Podcast (Summary 完成后)
    ↓
Download Pending Podcasts (每 12 小时)
```

## 手动触发示例

### 1. 生成特定日期的 Podcast

1. 进入 Actions > Generate Daily Podcast
2. 点击 "Run workflow"
3. 填写参数：
   - date: `2026-02-10`
   - wait: 选择是否等待完成
4. 点击 "Run workflow"

### 2. 下载待处理的 Podcasts

1. 进入 Actions > Download Pending Podcasts
2. 点击 "Run workflow"
3. 点击 "Run workflow"（无需参数）

## 故障排查

### Workflow 失败

1. **认证失败**
   - 检查 `NOTEBOOKLM_STORAGE_STATE` secret 是否正确配置
   - 在本地重新运行 `notebooklm login` 并更新 secret
   - 确认 storage_state.json 的 JSON 格式完整且有效

2. **依赖安装失败**
   - GitHub Actions 会自动从 requirements.txt 安装依赖
   - 不需要安装 Playwright，认证数据直接从 secret 中获取
   - 如果失败，检查 requirements.txt 是否正确

3. **Podcast 生成超时**
   - 默认使用异步模式，不会超时
   - 如果使用同步模式（wait=true），可能需要等待较长时间
   - 异步模式建议使用定时下载 workflow 来获取结果

### 本地测试

```bash
# 设置环境变量（如果使用非默认路径）
export NOTEBOOKLM_STORAGE_STATE=~/.notebooklm/storage_state.json

# 生成 podcast（异步）
python scripts/generate_podcast.py --date 2026-02-10 --no-wait

# 下载 podcast
python scripts/download_podcast.py --date 2026-02-10

# 检查状态
python scripts/check_podcast_status.py
```

## 文件结构

```
data/
  podcasts/
    2026-02-10_metadata.json  # 生成任务元数据
    2026-02-10_podcast.mp3    # 下载的音频文件
    2026-02-10_content.md     # 临时内容文件
web/
  public/
    data/
      podcasts/
        2026-02-10_podcast.mp3  # Web 访问的音频文件
```

## 注意事项

1. **认证有效期**：NotebookLM 的认证可能会过期，需要定期更新
2. **配额限制**：注意 NotebookLM 的使用配额
3. **存储空间**：音频文件较大，注意 Git 仓库大小
4. **并发限制**：避免同时生成多个 podcast

## 监控和通知

可以在 GitHub Actions 设置中启用邮件通知：
- Settings > Notifications > Actions
- 勾选 "Send notifications for failed workflows only"
