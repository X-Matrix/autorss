#!/usr/bin/env python3
"""
生成Web站点所需的静态数据文件
"""
import os
import json
import pathlib
import shutil
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'summaries'
PODCASTS_DIR = ROOT / 'data' / 'podcasts'
WEB_PUBLIC = ROOT / 'web' / 'public' / 'data'


def ensure_dirs():
    """确保目录存在"""
    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)


def generate_index():
    """生成索引文件，列出所有可用的日期"""
    if not DATA_DIR.exists():
        return []
    
    summaries = []
    for json_file in sorted(DATA_DIR.glob('*.json'), reverse=True):
        date_str = json_file.stem
        
        has_podcast = False
        if (PODCASTS_DIR / f'{date_str}_podcast.mp3').exists():
            has_podcast = True
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                summaries.append({
                    'date': date_str,
                    'total_items': data.get('total_items', 0),
                    'categories': list(data.get('categories', {}).keys()),
                    'highlights_count': len(data.get('highlights', [])),
                    'daily_summary': data.get('daily_summary', ''),
                    'has_podcast': has_podcast
                })
        except Exception as e:
            print(f'Failed to process {json_file}: {e}')
    
    # 保存索引文件
    index_file = WEB_PUBLIC / 'index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)
    
    print(f'Generated index with {len(summaries)} entries')
    return summaries


def copy_summaries():
    """复制摘要文件到web/public目录，并注入has_podcast字段和修正date字段"""
    if not DATA_DIR.exists():
        print('No summaries directory found')
        return
    
    summaries_dir = WEB_PUBLIC / 'summaries'
    summaries_dir.mkdir(exist_ok=True)
    
    count = 0
    for json_file in DATA_DIR.glob('*.json'):
        target = summaries_dir / json_file.name
        
        # 读取原始数据
        data = json.loads(json_file.read_text(encoding='utf-8'))
        
        # 检查podcast是否存在
        date_str = json_file.stem
        podcast_file = PODCASTS_DIR / f'{date_str}_podcast.mp3'
        data['has_podcast'] = podcast_file.exists()
        
        # 修正date字段，确保与文件名一致
        data['date'] = date_str
        
        # 写入目标文件
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        count += 1
    
    print(f'Copied {count} summary files')


def copy_podcasts():
    """复制播客文件到web/public目录"""
    if not PODCASTS_DIR.exists():
        return
    
    podcasts_dir = WEB_PUBLIC / 'podcasts'
    podcasts_dir.mkdir(exist_ok=True)
    
    count = 0
    for audio_file in PODCASTS_DIR.glob('*_podcast.mp3'):
        target = podcasts_dir / audio_file.name
        shutil.copy2(audio_file, target)
        count += 1
    
    print(f'Copied {count} podcast files')


def main():
    """主函数"""
    ensure_dirs()
    generate_index()
    copy_summaries()
    copy_podcasts()
    print('Static data generation complete!')


if __name__ == '__main__':
    main()
