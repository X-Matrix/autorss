# Podcast R2 迁移完成

## 已完成的修改

### 1. GitHub Actions 工作流 (`.github/workflows/deploy.yml`)
- ✅ 添加了上传 podcast 到 R2 的步骤
- ✅ 配置了 Wrangler CLI
- ✅ 添加了环境变量支持

### 2. 静态数据生成脚本 (`scripts/generate_static_data.py`)
- ✅ 移除了复制 podcast 到 `web/public` 的逻辑
- ✅ Podcast 文件现在直接从 R2 加载

### 3. 前端配置
- ✅ 创建了 `web/src/config.ts` 配置文件
- ✅ 创建了 `web/.env.example` 环境变量示例
- ✅ 修改了 `DayView.tsx` 使用 R2 URL
- ✅ 更新了 `.gitignore` 忽略环境变量文件

### 4. 文档
- ✅ 创建了 `R2_SETUP.md` 配置说明
- ✅ 创建了 `wrangler.toml` 配置文件

## 需要的后续操作

### 1. 在 Cloudflare 创建 R2 存储桶
```bash
# 登录 Cloudflare Dashboard
# 创建名为 autorss-podcast 的 R2 存储桶
```

### 2. 配置 R2 公共访问
两个选项：
- **选项 A**: 绑定自定义域名（推荐，如 `podcast.yourdomain.com`）
- **选项 B**: 启用 R2.dev 子域名

### 3. 在 GitHub 添加 Secrets
- `CLOUDFLARE_R2_API_TOKEN` - R2 专用 API Token（需要有 R2 写入权限）
- `CLOUDFLARE_API_TOKEN` - Pages 部署 API Token
- `CLOUDFLARE_ACCOUNT_ID` - Cloudflare 账户 ID  
- `R2_PODCAST_URL` - R2 的公共访问 URL（https://pdcstcdv.1cup.cafe）

### 4. 创建本地环境配置
```bash
cd web
cp .env.example .env
# 编辑 .env，填入 R2 URL
```

### 5. 在 Cloudflare Pages 创建项目
- 项目名：`autorss`

## 测试部署

1. 提交并推送代码
2. 检查 GitHub Actions 运行状态
3. 验证 podcast 文件是否上传到 R2
4. 访问网站确认音频播放正常

详细配置步骤请参考 [R2_SETUP.md](R2_SETUP.md)
