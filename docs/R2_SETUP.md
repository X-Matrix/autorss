# R2 存储配置说明

## 创建 R2 存储桶

1. 登录 Cloudflare Dashboard
2. 进入 **R2** 部分
3. 创建新的存储桶，命名为 `autorss-podcast`

## 配置公共访问

### 方法 1: 使用自定义域名（推荐）

1. 在 R2 存储桶设置中，点击 **Settings** > **Public Access**
2. 绑定自定义域名（如 `podcast.yourdomain.com`）
3. 在 `web/.env` 中设置：
   ```
   VITE_R2_PODCAST_URL=https://podcast.yourdomain.com
   ```

### 方法 2: 使用 R2.dev 子域名

1. 在 R2 存储桶设置中启用 **R2.dev subdomain**
2. 将获得类似 `https://pub-xxxxx.r2.dev` 的 URL
3. 在 `web/.env` 中设置该 URL

## GitHub Actions 配置

需要在 GitHub 仓库设置中添加以下 Secrets:

- `CLOUDFLARE_R2_API_TOKEN`: Cloudflare R2 专用 API Token（需要有 R2 写入权限）
- `CLOUDFLARE_API_TOKEN`: Cloudflare Pages API Token（用于部署）
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare Account ID
- `R2_PODCAST_URL`: R2 公共访问 URL（如 https://pdcstcdv.1cup.cafe）

### 创建 R2 API Token

1. 登录 Cloudflare Dashboard
2. 进入 **My Profile** > **API Tokens**
3. 点击 **Create Token**
4. 选择 **Create Custom Token**
5. 权限配置：
   - **Account** > **R2** > **Edit**
6. 账户资源：选择你的账户
7. 创建并复制 Token，添加到 GitHub Secrets

## 本地测试上传

```bash
# 安装 wrangler
npm install -g wrangler

# 登录
wrangler login

# 上传测试文件
wrangler r2 object put autorss-podcast/test.mp3 --file data/podcasts/2026-02-10_podcast.mp3

# 列出文件
wrangler r2 object list autorss-podcast
```

## 部署流程

1. 生成静态数据（不包含 podcast 文件）
2. 上传 podcast 文件到 R2
3. 构建前端应用
4. 部署到 Cloudflare Pages

前端会通过配置的 R2 URL 访问 podcast 文件。
