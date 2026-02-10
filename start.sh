#!/bin/bash

echo "🚀 AutoRSS 快速启动脚本"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装Node.js"
    exit 1
fi

echo "✅ Python和Node.js已安装"

# 安装Python依赖
echo ""
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 运行RSS抓取
echo ""
echo "📡 获取RSS数据..."
python3 scripts/fetch_rss.py

# 检查是否设置了API密钥
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  未设置 OPENAI_API_KEY 环境变量"
    echo "请运行: export OPENAI_API_KEY=your_api_key"
    echo "跳过AI分析步骤..."
else
    echo ""
    echo "🤖 运行AI分析..."
    python3 scripts/analyze_rss.py
fi

# 生成静态数据
echo ""
echo "📊 生成Web静态数据..."
python3 scripts/generate_static_data.py

# 安装Web依赖
echo ""
echo "📦 安装Web依赖..."
cd web
npm install

# 启动开发服务器
echo ""
echo "✨ 启动Web开发服务器..."
echo "访问: http://localhost:5173"
echo ""
npm run dev
