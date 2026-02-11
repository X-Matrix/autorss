#!/usr/bin/env python3
"""
检查 GitHub Actions workflow 状态和待处理的任务
"""
import json
import pathlib
from datetime import datetime, timedelta
from loguru import logger


ROOT = pathlib.Path(__file__).resolve().parents[1]
PODCASTS_DIR = ROOT / 'data' / 'podcasts'


def check_local_status():
    """检查本地 podcast 状态"""
    print("\n" + "=" * 80)
    print("本地 Podcast 状态")
    print("=" * 80 + "\n")
    
    if not PODCASTS_DIR.exists():
        print("❌ Podcasts 目录不存在")
        return
    
    # 查找所有元数据文件
    metadata_files = sorted(PODCASTS_DIR.glob('*_metadata.json'), reverse=True)
    
    if not metadata_files:
        print("⚠️  未找到任何 podcast 元数据")
        return
    
    # 统计状态
    stats = {
        'completed': [],
        'generating': [],
        'timeout': [],
        'unknown': []
    }
    
    for metadata_file in metadata_files:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        date = metadata.get('date', 'Unknown')
        status = metadata.get('status', 'unknown')
        
        # 检查音频文件是否存在
        audio_file = PODCASTS_DIR / f'{date}_podcast.mp3'
        has_audio = audio_file.exists()
        
        if has_audio:
            stats['completed'].append(date)
        elif status in ['generating', 'timeout_but_generating']:
            stats['generating'].append(date)
        else:
            stats['unknown'].append(date)
    
    # 显示统计
    print(f"📊 总计: {len(metadata_files)} 个任务\n")
    
    if stats['completed']:
        print(f"✅ 已完成: {len(stats['completed'])} 个")
        for date in stats['completed'][:5]:  # 只显示最近5个
            print(f"   - {date}")
        if len(stats['completed']) > 5:
            print(f"   ... 还有 {len(stats['completed']) - 5} 个")
        print()
    
    if stats['generating']:
        print(f"⏳ 生成中: {len(stats['generating'])} 个")
        for date in stats['generating']:
            print(f"   - {date} (可运行下载脚本尝试获取)")
        print()
    
    if stats['unknown']:
        print(f"❓ 未知状态: {len(stats['unknown'])} 个")
        for date in stats['unknown']:
            print(f"   - {date}")
        print()
    
    # 提供建议
    print("💡 建议操作:")
    if stats['generating']:
        print("   • 运行下载脚本尝试获取生成中的 podcast:")
        print("     python scripts/download_podcast.py")
    
    if len(stats['completed']) > 0:
        print("   • 更新 Web 静态数据:")
        print("     python scripts/generate_static_data.py")
    
    print()


def check_github_actions_tips():
    """显示 GitHub Actions 提示"""
    print("=" * 80)
    print("GitHub Actions 检查")
    print("=" * 80 + "\n")
    
    print("🔗 在 GitHub 上查看 workflow 状态:")
    print("   https://github.com/YOUR_USERNAME/YOUR_REPO/actions\n")
    
    print("📋 可用的 workflows:")
    print("   1. Generate Daily Podcast - 生成每日 podcast")
    print("   2. Download Pending Podcasts - 下载待处理的 podcast")
    print("   3. Daily RSS Summary - 每日新闻摘要\n")
    
    print("🚀 手动触发 workflow:")
    print("   • 进入 Actions 页面")
    print("   • 选择对应的 workflow")
    print("   • 点击 'Run workflow'")
    print("   • 填写参数（如需要）")
    print("   • 点击 'Run workflow' 按钮\n")
    
    print("🔐 配置检查清单:")
    print("   ✓ 是否已配置 NOTEBOOKLM_STORAGE_STATE secret?")
    print("   ✓ storage_state.json 是否有效（未过期）?")
    print("   ✓ 是否已启用 Actions（Settings > Actions > General）?\n")


def check_recent_summaries():
    """检查最近的新闻摘要"""
    print("=" * 80)
    print("新闻摘要检查")
    print("=" * 80 + "\n")
    
    summaries_dir = ROOT / 'data' / 'summaries'
    
    if not summaries_dir.exists():
        print("❌ 摘要目录不存在")
        return
    
    # 检查最近7天
    recent_summaries = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        summary_file = summaries_dir / f'{date}.json'
        
        if summary_file.exists():
            recent_summaries.append(date)
    
    if recent_summaries:
        print(f"✅ 最近 7 天有 {len(recent_summaries)} 个摘要:")
        for date in recent_summaries:
            # 检查是否有对应的 podcast
            podcast_file = PODCASTS_DIR / f'{date}_podcast.mp3'
            status = "🎧" if podcast_file.exists() else "⏳"
            print(f"   {status} {date}")
        print()
    else:
        print("⚠️  最近 7 天没有新闻摘要")
        print("   运行: python scripts/analyze_rss.py\n")


def main():
    """主函数"""
    print("\n" + "🎙️  AutoRss Podcast 状态检查" + "\n")
    
    check_recent_summaries()
    check_local_status()
    check_github_actions_tips()
    
    print("=" * 80)
    print("详细配置文档: .github/PODCAST_AUTOMATION.md")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
