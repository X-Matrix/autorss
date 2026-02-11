#!/usr/bin/env python3
"""
检查 Podcast 生成状态

快速查看哪些日期的 Podcast 正在生成、已完成或失败
"""
import json
import pathlib
from datetime import datetime, timedelta
from loguru import logger


ROOT = pathlib.Path(__file__).resolve().parents[1]
PODCASTS_DIR = ROOT / 'data' / 'podcasts'


def check_podcast_status():
    """检查所有 Podcast 的状态"""
    
    if not PODCASTS_DIR.exists():
        logger.warning('Podcasts 目录不存在')
        return
    
    # 查找所有元数据文件
    metadata_files = sorted(PODCASTS_DIR.glob('*_metadata.json'))
    
    if not metadata_files:
        logger.info('未找到任何 Podcast 元数据')
        return
    
    print("\n" + "=" * 80)
    print("Podcast 状态检查")
    print("=" * 80 + "\n")
    
    generating = []
    completed = []
    timeout = []
    
    for metadata_file in metadata_files:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        date = metadata.get('date', 'Unknown')
        status = metadata.get('status', 'unknown')
        notebook_id = metadata.get('notebook_id', 'N/A')
        task_id = metadata.get('task_id', 'N/A')
        audio_format = metadata.get('audio_format', 'N/A')
        total_items = metadata.get('total_items', 0)
        
        # 检查音频文件是否存在
        audio_file = PODCASTS_DIR / f'{date}_podcast.mp3'
        has_audio = audio_file.exists()
        
        info = {
            'date': date,
            'status': status,
            'notebook_id': notebook_id,
            'task_id': task_id,
            'format': audio_format,
            'items': total_items,
            'has_audio': has_audio
        }
        
        if has_audio or status == 'completed':
            completed.append(info)
        elif status in ['generating', 'timeout_but_generating']:
            if status == 'timeout_but_generating':
                timeout.append(info)
            else:
                generating.append(info)
        else:
            generating.append(info)
    
    # 显示统计
    print(f"📊 总计: {len(metadata_files)} 个 Podcast")
    print(f"   ✅ 已完成: {len(completed)}")
    print(f"   ⏳ 生成中: {len(generating)}")
    print(f"   ⚠️  超时但可能完成: {len(timeout)}")
    print()
    
    # 显示详情
    if completed:
        print("=" * 80)
        print("✅ 已完成的 Podcast")
        print("=" * 80)
        for info in completed:
            size_mb = (PODCASTS_DIR / f"{info['date']}_podcast.mp3").stat().st_size / 1024 / 1024 if info['has_audio'] else 0
            print(f"\n📅 {info['date']}")
            print(f"   格式: {info['format']}")
            print(f"   新闻数: {info['items']} 条")
            if info['has_audio']:
                print(f"   文件: {size_mb:.2f} MB")
                print(f"   播放: open data/podcasts/{info['date']}_podcast.mp3")
        print()
    
    if generating:
        print("=" * 80)
        print("⏳ 生成中的 Podcast")
        print("=" * 80)
        for info in generating:
            print(f"\n📅 {info['date']}")
            print(f"   格式: {info['format']}")
            print(f"   新闻数: {info['items']} 条")
            print(f"   Notebook: {info['notebook_id'][:20]}...")
            print(f"   下载: python scripts/download_podcast.py --date {info['date']}")
            print(f"   查看: https://notebooklm.google.com/notebook/{info['notebook_id']}")
        print()
    
    if timeout:
        print("=" * 80)
        print("⚠️  超时但可能已完成")
        print("=" * 80)
        for info in timeout:
            print(f"\n📅 {info['date']}")
            print(f"   格式: {info['format']}")
            print(f"   新闻数: {info['items']} 条")
            print(f"   尝试下载: python scripts/download_podcast.py --date {info['date']}")
            print(f"   查看状态: https://notebooklm.google.com/notebook/{info['notebook_id']}")
        print()
    
    # 建议
    print("=" * 80)
    print("💡 建议操作")
    print("=" * 80)
    
    if generating or timeout:
        print("\n对于生成中或超时的 Podcast:")
        print("1. 访问 NotebookLM 网页查看实际状态")
        print("2. 如果已完成，运行下载脚本")
        print("3. 如果失败，可以重新生成")
    
    if completed:
        print("\n已完成的 Podcast:")
        print("1. 可以直接收听")
        print("2. 可以分享给朋友")
        print("3. 可以上传到播客平台")
    
    # 检查最近的摘要
    summaries_dir = ROOT / 'data' / 'summaries'
    if summaries_dir.exists():
        recent_summaries = sorted(summaries_dir.glob('*.json'), reverse=True)[:3]
        if recent_summaries:
            print("\n最近的新闻摘要（可生成 Podcast）:")
            for summary_file in recent_summaries:
                date = summary_file.stem
                # 检查是否已有 Podcast
                has_podcast = any(m['date'] == date for m in completed + generating + timeout)
                status_icon = "✅" if has_podcast else "⭕"
                print(f"   {status_icon} {date}")
            
            # 建议生成
            no_podcast = [s.stem for s in recent_summaries 
                         if not any(m['date'] == s.stem for m in completed + generating + timeout)]
            if no_podcast:
                print(f"\n可以为以下日期生成 Podcast:")
                for date in no_podcast:
                    print(f"   python scripts/generate_podcast.py --date {date} --no-wait")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    check_podcast_status()
