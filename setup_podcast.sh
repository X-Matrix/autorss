#!/bin/bash
# 快速开始 - 安装和配置 NotebookLM Podcast 生成功能

echo "=== NotebookLM Podcast 生成器 - 安装向导 ==="
echo ""

# 检查 Python 版本
echo "1. 检查 Python 版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ 未找到 Python3，请先安装 Python 3.10 或更高版本"
    exit 1
fi
echo "✅ Python 已安装"
echo ""

# 安装依赖
echo "2. 安装 Python 依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"
echo ""

# 安装 Playwright 浏览器
echo "3. 安装 Playwright Chromium 浏览器..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "❌ Playwright 安装失败"
    exit 1
fi
echo "✅ Playwright 安装完成"
echo ""

# NotebookLM 认证
echo "4. NotebookLM 认证配置"
echo "即将打开浏览器进行 Google 账号登录..."
echo "请在浏览器中完成登录后返回此处"
read -p "按回车键继续..."

notebooklm login
if [ $? -ne 0 ]; then
    echo "❌ 认证失败，请重试"
    exit 1
fi
echo "✅ 认证完成"
echo ""

# 创建必要目录
echo "5. 创建必要的目录..."
mkdir -p data/podcasts
echo "✅ 目录创建完成"
echo ""

echo "========================================="
echo "🎉 安装完成！"
echo ""
echo "现在可以生成 podcast 了："
echo ""
echo "  # 为昨天的新闻生成 podcast"
echo "  python scripts/generate_podcast.py"
echo ""
echo "  # 为指定日期生成 podcast"
echo "  python scripts/generate_podcast.py --date 2026-02-10"
echo ""
echo "  # 使用辩论格式的长版本"
echo "  python scripts/generate_podcast.py --format debate --length long"
echo ""
echo "查看完整文档: cat README_PODCAST.md"
echo "========================================="
