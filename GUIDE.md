# AutoRSS 使用指南

## 📖 目录

1. [快速开始](#快速开始)
2. [配置RSS源](#配置rss源)
3. [运行分析](#运行分析)
4. [Web开发](#web开发)
5. [部署到Cloudflare Pages](#部署到cloudflare-pages)
6. [常见问题](#常见问题)

## 快速开始

### 方式一：使用启动脚本（推荐）

```bash
./start.sh
```

这个脚本会自动：
1. 安装Python依赖
2. 获取RSS数据
3. 运行分析（如果设置了API密钥）
4. 生成静态数据
5. 启动Web开发服务器

### 方式二：手动步骤

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 获取RSS数据
python scripts/fetch_rss.py

# 3. 测试分析（不需要API密钥）
python scripts/analyze_rss_test.py

# 或使用AI分析（需要API密钥）
export ANTHROPIC_API_KEY=your_key_here
python scripts/analyze_rss.py

# 4. 生成Web数据
python scripts/generate_static_data.py

# 5. 启动Web服务
cd web
npm install
npm run dev
```

## 配置RSS源

### 方法1: 单个RSS源URL

在 `rss/` 目录创建 `.xml` 文件，内容为RSS源URL：

```bash
echo "https://blog.example.com/feed.xml" > rss/myblog.xml
```

### 方法2: OPML文件（推荐，支持多个源）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
  <head>
    <title>My RSS Feeds</title>
  </head>
  <body>
    <outline text="Tech Blogs" title="Tech Blogs">
      <outline text="Hacker News" xmlUrl="https://news.ycombinator.com/rss"/>
      <outline text="Paul Graham" xmlUrl="http://www.aaronswartz.com/2002/feeds/pgessays.rss"/>
      <outline text="MIT News" xmlUrl="https://news.mit.edu/rss/feed"/>
    </outline>
  </body>
</opml>
```

保存为 `rss/feeds.xml`

### 方法3: 直接粘贴RSS XML内容

将RSS XML内容直接保存到 `rss/source.xml`

## 运行分析

### 测试模式（无需API密钥）

```bash
# 分析昨天的数据
python scripts/analyze_rss_test.py

# 分析指定日期
python scripts/analyze_rss_test.py 2026-02-09
```

测试模式使用简单的关键词分类，适合开发和测试。

### AI模式（需要OpenAI API密钥）

1. 获取API密钥：访问 https://platform.openai.com/api-keys

2. 设置环境变量：
```bash
export OPENAI_API_KEY=sk-xxxxx
```

3. 运行分析：
```bash
# 分析昨天的数据
python scripts/analyze_rss.py

# 分析指定日期
python scripts/analyze_rss.py 2026-02-09
```

AI模式会：
- 智能分类（技术、科学、AI/ML等）
- 中英文翻译
- 生成每日总结
- 提取关键亮点
- 为每个分类生成摘要

**注意**: 现在使用 OpenAI GPT-4 模型，确保你的API密钥有足够的额度。

## Web开发

### 本地开发

```bash
cd web
npm install
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
cd web
npm run build
```

构建输出在 `web/dist/` 目录

### 预览生产构建

```bash
cd web
npm run preview
```

## 部署到Cloudflare Pages

### 方式一：通过GitHub Actions自动部署（推荐）

1. **设置GitHub Secrets**

   在仓库设置中添加以下Secrets：
   
   - `ANTHROPIC_API_KEY`: Claude API密钥
   - `CLOUDFLARE_API_TOKEN`: Cloudflare API令牌
   - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare账户ID

2. **获取Cloudflare凭证**

   ```bash
   # 登录Cloudflare仪表板
   # 1. API Token: 
   #    - 访问 https://dash.cloudflare.com/profile/api-tokens
   #    - 创建Token，选择 "Edit Cloudflare Workers" 模板
   #    - 或使用 "Create Custom Token" 并给予 Cloudflare Pages 权限
   
   # 2. Account ID:
   #    - 访问 https://dash.cloudflare.com/
   #    - 在右侧栏查看 Account ID
   ```

3. **推送到GitHub**

   ```bash
   git add .
   git commit -m "Setup AutoRSS"
   git push origin main
   ```

   GitHub Actions会自动运行并部署。

### 方式二：手动部署

1. **安装Wrangler CLI**

   ```bash
   npm install -g wrangler
   ```

2. **登录Cloudflare**

   ```bash
   wrangler login
   ```

3. **创建Pages项目**

   ```bash
   cd web
   npm run build
   wrangler pages publish dist --project-name=autorss
   ```

### 配置自定义域名

1. 在Cloudflare Pages仪表板选择项目
2. 点击 "Custom domains"
3. 添加你的域名
4. 更新DNS记录指向Cloudflare

## 常见问题

### Q: RSS获取失败？

**A:** 检查以下几点：
- RSS源URL是否正确
- 网络连接是否正常
- 是否有防火墙阻止
- RSS源是否需要认证

### Q: AI分析报错？

**A:** 
- 确认已设置 `OPENAI_API_KEY`
- 检查API密钥是否有效
- 确认账户有足够的额度（GPT-4需要付费账户）
- 如果内容过多，可能需要调整分析的条目数量
- 可以尝试使用更便宜的模型如 `gpt-3.5-turbo`（修改analyze_rss.py中的model参数）

### Q: Web界面显示空白？

**A:**
1. 确认已运行 `generate_static_data.py`
2. 检查 `web/public/data/` 目录是否有数据
3. 查看浏览器控制台错误信息

### Q: 如何修改分类逻辑？

**A:** 编辑 `scripts/analyze_rss.py` 中的提示词（prompt），指定你想要的分类。

### Q: 如何调整抓取频率？

**A:** 编辑 `.github/workflows/daily_summary.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天UTC 00:00
  # 改为
  - cron: '0 */6 * * *'  # 每6小时一次
```

### Q: 可以使用其他LLM吗？

**A:** 可以！修改 `scripts/analyze_rss.py`，替换为你喜欢的LLM API（如OpenAI、Google Gemini等）。

### Q: 如何备份数据？

**A:** 
```bash
# 备份所有数据
tar -czf autorss-backup-$(date +%Y%m%d).tar.gz data/ raw_content/

# 仅备份摘要
tar -czf summaries-backup-$(date +%Y%m%d).tar.gz data/summaries/
```

## 进阶配置

### 自定义Web主题

编辑 `web/tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'dark': '#your-bg-color',
      'accent': '#your-accent-color',
    }
  }
}
```

### 添加更多页面

1. 在 `web/src/pages/` 创建新组件
2. 在 `web/src/App.jsx` 添加路由
3. 在 `web/src/components/Layout.jsx` 添加导航

### 集成RSS阅读器

可以扩展功能，添加：
- 全文获取
- 图片缓存
- 离线阅读
- 收藏功能
- 搜索功能

## 贡献

欢迎提交Issue和PR！

## 支持

- 📧 Email: your@email.com
- 💬 GitHub Issues: https://github.com/yourusername/AutoRss/issues
- 📚 文档: https://your-docs-site.com
