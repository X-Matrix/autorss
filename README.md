# AutoRSS - AI驱动的RSS订阅摘要系统

一个使用AI自动整理、分类和翻译RSS订阅内容的系统，配备优雅的Web界面展示每日技术摘要。

## ✨ 特性

- 🤖 **AI智能分析**: 使用Claude LLM自动分类和翻译RSS内容
- 📊 **每日摘要**: 生成结构化的每日技术动态摘要
- �️ **Podcast生成**: 基于NotebookLM将每日新闻转换为专业播客音频
- �🌐 **现代Web界面**: 使用React + TailwindCSS构建的优雅极客风格界面
- ☁️ **自动部署**: GitHub Actions自动化工作流，部署到Cloudflare Pages
- 🔄 **增量更新**: 智能的ETag/Last-Modified支持，避免重复抓取

## 🏗️ 项目结构

```
AutoRss/
├── scripts/
│   ├── fetch_rss.py           # RSS订阅获取脚本
│   ├── analyze_rss.py         # LLM分析脚本
│   ├── generate_podcast.py    # Podcast生成脚本 🆕
│   └── generate_static_data.py # 静态数据生成
├── data/
│   ├── summaries/             # AI生成的每日摘要
│   ├── podcasts/              # 生成的Podcast音频 🆕
│   ├── feed_state.json        # RSS源状态缓存
│   └── rss_history.txt        # 历史记录
├── raw_content/               # 原始RSS数据（按日期组织）
├── rss/                       # RSS源配置文件
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

### 2. 配置RSS源

在 `rss/` 目录下创建 `.xml` 文件，可以是：
- RSS源URL（一行一个URL）
- OPML文件（包含多个RSS源）
- RSS XML内容

示例 `rss/source1.xml`:
```
https://example.com/feed.xml
```

### 3. 设置环境变量

需要设置以下GitHub Secrets:
- `OPENAI_API_KEY`: OpenAI API密钥
- `CLOUDFLARE_API_TOKEN`: Cloudflare Pages部署令牌
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare账户ID

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

- 🚀 [快速开始指南](QUICKSTART_PODCAST.md) - 最简单的使用方法
- 📖 [完整文档](README_PODCAST.md) - 所有功能和配置
- 💡 [使用示例](PODCAST_EXAMPLES.md) - 各种场景的实用示例

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
