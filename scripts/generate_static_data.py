#!/usr/bin/env python3
"""
生成Web站点所需的静态数据文件
"""
import os
import json
import pathlib
from datetime import datetime, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data' / 'summaries'
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
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                summaries.append({
                    'date': date_str,
                    'total_items': data.get('total_items', 0),
                    'categories': list(data.get('categories', {}).keys()),
                    'highlights_count': len(data.get('highlights', []))
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
    """复制摘要文件到web/public目录"""
    if not DATA_DIR.exists():
        print('No summaries directory found')
        return
    
    summaries_dir = WEB_PUBLIC / 'summaries'
    summaries_dir.mkdir(exist_ok=True)
    
    count = 0
    for json_file in DATA_DIR.glob('*.json'):
        target = summaries_dir / json_file.name
        target.write_text(json_file.read_text(encoding='utf-8'), encoding='utf-8')
        count += 1
    
    print(f'Copied {count} summary files')


def main():
    """主函数"""
    ensure_dirs()
    generate_index()
    copy_summaries()
    print('Static data generation complete!')


if __name__ == '__main__':
    main()
