# AutoRSS - AI驱动的arXiv论文摘要系统

一个使用AI自动整理、分类和翻译arXiv AI论文的系统，配备优雅的Web界面展示每日技术摘要。

## ✨ 特性

- 🤖 **AI智能分析**: 使用Claude LLM自动分类和翻译arXiv论文内容
- 📊 **每日摘要**: 生成结构化的每日AI研究动态摘要
- 🎙️ **Podcast生成**: 基于NotebookLM将每日论文转换为专业播客音频
- 🌐 **现代Web界面**: 使用React + TailwindCSS构建的优雅极客风格界面
- ☁️ **自动部署**: GitHub Actions自动化工作流，部署到Cloudflare Pages
- 📚 **arXiv数据源**: 自动从arXiv API获取最新AI领域论文（cs.AI类别）

## 🏗️ 项目结构

```
AutoRss/
├── scripts/
│   ├── fetch_rss.py           # arXiv论文获取脚本
│   ├── analyze_rss.py         # LLM分析脚本
│   ├── generate_podcast.py    # Podcast生成脚本 🆕
│   └── generate_static_data.py # 静态数据生成
├── data/
│   ├── summaries/             # AI生成的每日摘要
│   ├── podcasts/              # 生成的Podcast音频 🆕
│   └── rss_history.txt        # 历史记录
├── raw_content/               # 原始arXiv论文数据（按日期组织）
├── web/                       # React Web应用
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── public/
└── .github/workflows/         # GitHub Actions工作流
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd AutoRss
```

### 2. 数据源配置

本系统自动从 arXiv API 获取最新的 AI 领域论文（cs.AI 类别）。

数据源配置在 [scripts/fetch_rss.py](scripts/fetch_rss.py) 中：
```python
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_QUERY_PARAMS = {
    'search_query': '(cat:cs.AI)',
    'sortBy': 'lastUpdatedDate',
    'sortOrder': 'descending',
    'start': 0,
    'max_results': 100
}
```

如需自定义查询条件，可修改 `ARXIV_QUERY_PARAMS`：
- `search_query`: 搜索条件（例如：`cat:cs.AI` 表示计算机科学AI类别）
- `max_results`: 每次获取的论文数量（最大2000）
- `sortBy`: 排序方式（`lastUpdatedDate`、`submittedDate`、`relevance`）

### 3. 设置环境变量（Secrets / 本地环境）

以下为推荐的 Secrets 与本地环境配置说明。将 GitHub Actions 所需的敏感信息添加到 GitHub 仓库设置 -> `Settings` -> `Secrets and variables` -> `Actions` 中。

- **必填（GitHub Secrets）**:
  - `OPENAI_API_KEY`: 用于调用 OpenAI 或其它 LLM 提供商的 API Key（例如以 `sk-...` 开头的密钥）。
  - `CLOUDFLARE_API_TOKEN`: Cloudflare Pages 的部署令牌。建议创建最小权限的令牌，仅包含 Pages 部署所需权限。
  - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare 账户 ID（可在 Cloudflare 仪表板的账户概览中找到）。

- **可选/扩展（根据使用的服务添加）**:
  - `NOTEBOOKLM_API_KEY`：如果使用 NotebookLM 的 API/服务时需要添加。
  - 其他第三方服务的 API Key（例如语音合成、存储、翻译服务等），请按需添加并在 CI 中以 `${{ secrets.NAME }}` 方式引用。

- **本地开发（临时环境变量）**:
  - 直接在终端导出（临时生效）：
    ```bash
    export OPENAI_API_KEY=your_api_key
    export CLOUDFLARE_API_TOKEN=your_cloudflare_token
    export CLOUDFLARE_ACCOUNT_ID=your_account_id
    ```
  - 使用 `.env` 文件（不要将其提交到仓库）：
    ```text
    OPENAI_API_KEY=your_api_key
    CLOUDFLARE_API_TOKEN=your_cloudflare_token
    CLOUDFLARE_ACCOUNT_ID=your_account_id
    ```
    然后在当前 shell 中加载：
    ```bash
    source .env
    ```
  - 也可使用 `direnv`、`dotenv` 等工具自动加载本地环境变量。

- **安全建议**:
  - 永远不要将密钥或凭据提交到版本库；使用 GitHub Secrets 存储并在 Actions 中注入。
  - 为部署或 API 密钥设定最小权限；如果服务支持，启用域名/IP 白名单与速率限制。
  - 在 CI/日志中不要打印完整密钥，必要时打印已掩码或校验信息（如长度、前后几位）。

- **在 GitHub Actions 中使用**:
  - 在 workflow 文件中通过 `${{ secrets.OPENAI_API_KEY }}` 使用密钥；示例：
    ```yaml
    - name: Run analysis
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: python scripts/analyze_rss.py
    ```

- **常见问题**:
  - 找不到 `CLOUDFLARE_ACCOUNT_ID`：登录 Cloudflare -> 仪表板 -> 账户概览（Account Overview）可查看 Account ID。
  - 需要在本地模拟 GitHub Secrets？ 推荐使用本地环境变量或 `.env`，并确保 `.gitignore` 忽略 `.env`。

### 仓库中使用到的 Secrets

下面列出当前仓库 `.github/workflows` 中实际使用到的 Secrets 名称、用途与简要建议：

- `OPENAI_API_KEY`:
  - 用途：在 `Daily RSS Summary` workflow 中用于调用 LLM（分析摘要）。
  - 建议：只给予模型调用权限，定期轮换密钥。

- `NOTEBOOKLM_STORAGE_STATE`:
  - 用途：在 `Generate Daily Podcast`、`Download Pending Podcasts` workflows 中，用作 NotebookLM 的 storage state（工作流中以 `NOTEBOOKLM_STORAGE_STATE` 内容写入到 `~/.notebooklm/storage_state.json`）。
  - 建议：将其作为敏感 JSON 内容存储，权限最小化，设置文件权限为 `600`。

- `CLOUDFLARE_API_TOKEN`:
  - 用途：在 `Build and Deploy` workflow 中用于 Cloudflare Pages 发布（`cloudflare/pages-action`）。
  - 建议：创建最小权限的 API 令牌，仅包含 Pages 部署权限，避免包含过多账户级权限。

- `CLOUDFLARE_ACCOUNT_ID`:
  - 用途：Cloudflare 账户标识，`Build and Deploy` 与 R2 上传步骤需要用到。
  - 建议：非秘密信息也可存为 Secret，便于在 workflow 中统一管理。

- `CLOUDFLARE_R2_API_TOKEN`:
  - 用途：在 `Build and Deploy` workflow 中用于将 podcast 上传到 R2（通过 `wrangler`）。
  - 建议：仅授予 R2 写入权限并可限制为特定命名空间。

- `R2_PODCAST_URL`:
  - 用途：在构建前注入到前端构建环境以生成指向 R2 的静态资源 URL（`VITE_R2_PODCAST_URL`）。
  - 建议：作为构建时变量使用，不在客户端代码中暴露敏感令牌。

- `SLACK_WEBHOOK`:
  - 用途：在 `Fetch RSS feeds` workflow 中用于发送 Slack 通知。
  - 建议：仅用于 webhook 通知，不要打印到日志中。


### 4. 本地开发

#### 运行RSS采集
```bash
pip install -r requirements.txt
python scripts/fetch_rss.py
```

#### 运行AI分析
```bash
export OPENAI_API_KEY=your_api_key
python scripts/analyze_rss.py
```

#### 启动Web开发服务器
```bash
cd web
npm install
npm run dev
```

访问 http://localhost:5173

### 5. 部署

推送到GitHub主分支会自动触发部署流程：
1. 获取RSS数据
2. AI分析生成摘要
3. 构建React应用
4. 部署到Cloudflare Pages

## 📋 工作流

### 每日自动运行 (UTC 00:00)

1. **fetch_rss.py**: 抓取RSS源，保存到 `raw_content/YYYY-MM-DD/`
2. **analyze_rss.py**: 使用Claude分析，生成摘要到 `data/summaries/`
3. **GitHub Actions**: 提交更新并触发部署

### 手动运行

```bash
# 获取RSS
python scripts/fetch_rss.py

# 分析特定日期
python scripts/analyze_rss.py 2026-02-09

# 🆕 生成Podcast
python scripts/generate_podcast.py --date 2026-02-09

# 生成Web静态数据
python scripts/generate_static_data.py

# 构建Web应用
cd web && npm run build
```

## 🎙️ Podcast 生成

基于 [NotebookLM](https://github.com/teng-lin/notebooklm-py) 将每日新闻转换为专业播客音频。

### 快速开始

```bash
# 一键安装和配置
./setup_podcast.sh

# 异步生成（推荐）- 立即返回，后台生成
python scripts/generate_podcast.py --no-wait

# 等待 5-10 分钟后下载
python scripts/download_podcast.py

# 收听
open data/podcasts/2026-02-10_podcast.mp3
```

### 功能特性

- ✅ 支持多种格式：深度讨论、简要概述、批判分析、辩论形式
- ✅ 可调节长度：短版、标准版、长版
- ✅ 异步模式：提交后即可返回，无需等待
- ✅ 多语言支持（默认中文）
- ✅ 自动化生成高质量AI语音
- ✅ 保存完整元数据

### 详细文档

- 🚀 [快速开始指南](./docs/QUICKSTART_PODCAST.md) - 最简单的使用方法
- 📖 [完整文档](./docs/README_PODCAST.md) - 所有功能和配置
- 💡 [使用示例](./docs/PODCAST_EXAMPLES.md) - 各种场景的实用示例

## 🎨 Web界面特性

- 📱 响应式设计，支持移动端
- 🌙 暗色主题，护眼舒适
- 🔍 分类浏览和筛选
- 🌐 中英文切换显示
- ⚡ 静态站点，加载快速
- 🎯 极简设计，专注内容

## 🛠️ 技术栈

### 后端
- Python 3.11+
- feedparser: RSS解析
- openai: OpenAI API
- requests: HTTP请求

### 前端
- React 18
- React Router: 路由
- TailwindCSS: 样式
- Vite: 构建工具

### 部署
- GitHub Actions: CI/CD
- Cloudflare Pages: 静态托管

## 📝 配置说明

### RSS源格式

支持三种格式：

1. **URL列表** (`source.xml`):
```
https://blog.example.com/feed.xml
```

2. **OPML文件**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
  <body>
    <outline text="Blog" xmlUrl="https://example.com/feed.xml"/>
  </body>
</opml>
```

3. **RSS XML内容**: 直接粘贴RSS XML

### LLM分析输出

生成的JSON格式：
```json
{
  "date": "2026-02-09",
  "total_items": 45,
  "categories": {
    "技术": [...],
    "AI/机器学习": [...]
  },
  "category_summaries": {
    "技术": "今日技术类内容摘要..."
  },
  "highlights": ["亮点1", "亮点2"],
  "daily_summary": "整体总结..."
}
```

## 🔧 自定义

### 修改LLM提示词

编辑 `scripts/analyze_rss.py` 中的 `prompt` 变量来调整分类和总结风格。

### 自定义Web样式

修改 `web/tailwind.config.js` 来调整颜色主题和样式。

### 调整抓取频率

编辑 `.github/workflows/daily_summary.yml` 中的 `cron` 表达式。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系

如有问题，请提交Issue或联系维护者。
