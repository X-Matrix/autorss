# Web开发指南

## 本地开发

1. 安装依赖:
```bash
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

3. 构建生产版本:
```bash
npm run build
```

## 数据加载

Web应用从 `/public/data/` 目录加载静态JSON文件：

- `/data/index.json`: 包含所有日期的索引
- `/data/summaries/{date}.json`: 每日摘要详情

这些文件由 `scripts/generate_static_data.py` 自动生成。

## 部署

应用构建后的 `dist/` 目录可以部署到任何静态托管服务，如：
- Cloudflare Pages
- Vercel
- Netlify
- GitHub Pages

## 自定义

### 颜色主题

编辑 `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      'dark': '#your-color',
      'accent': '#your-color',
    }
  }
}
```

### 字体

在 `index.html` 中修改Google Fonts链接，然后在 `tailwind.config.js` 中更新 `fontFamily`。
