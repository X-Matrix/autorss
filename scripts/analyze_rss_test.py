#!/usr/bin/env python3
"""
测试版本的分析脚本，不需要API密钥，生成示例数据用于开发
"""
import os
import sys
import json
import pathlib
import datetime
from typing import List, Dict, Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'raw_content'
DATA_DIR = ROOT / 'data'
SUMMARIES_DIR = DATA_DIR / 'summaries'


def ensure_dirs():
    """确保必要的目录存在"""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_items(date_str: str) -> List[Dict[str, Any]]:
    """加载指定日期的所有原始RSS条目"""
    date_dir = RAW_DIR / date_str
    if not date_dir.exists():
        return []
    
    items = []
    for json_file in date_dir.glob('*.json'):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items.append(data)
        except Exception as e:
            print(f'Failed to load {json_file}: {e}', file=sys.stderr)
    
    return items


def simple_categorize(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    简单的分类逻辑（用于测试）
    """
    if not items:
        return {
            "date": datetime.date.today().isoformat(),
            "total_items": 0,
            "categories": {},
            "summary": "今日无新内容",
            "highlights": []
        }
    
    # 简单分类：基于关键词
    categories = {
        "技术": [],
        "科学": [],
        "其他": []
    }
    
    tech_keywords = ['programming', 'code', 'software', 'web', 'app', 'tech', 'ai', 'ml', 'python', 'javascript', 'react']
    science_keywords = ['science', 'research', 'study', 'nasa', 'space', 'physics', 'chemistry']
    
    for item in items:
        title = (item.get('title', '') + ' ' + item.get('summary', '')).lower()
        
        categorized = False
        for keyword in tech_keywords:
            if keyword in title:
                categories['技术'].append({
                    'title': item.get('title', 'N/A'),
                    'title_zh': item.get('title', 'N/A'),
                    'link': item.get('link', 'N/A'),
                    'summary': item.get('summary', 'N/A')[:200],
                    'summary_zh': item.get('summary', 'N/A')[:200],
                    'published': item.get('published', '')
                })
                categorized = True
                break
        
        if not categorized:
            for keyword in science_keywords:
                if keyword in title:
                    categories['科学'].append({
                        'title': item.get('title', 'N/A'),
                        'title_zh': item.get('title', 'N/A'),
                        'link': item.get('link', 'N/A'),
                        'summary': item.get('summary', 'N/A')[:200],
                        'summary_zh': item.get('summary', 'N/A')[:200],
                        'published': item.get('published', '')
                    })
                    categorized = True
                    break
        
        if not categorized:
            categories['其他'].append({
                'title': item.get('title', 'N/A'),
                'title_zh': item.get('title', 'N/A'),
                'link': item.get('link', 'N/A'),
                'summary': item.get('summary', 'N/A')[:200],
                'summary_zh': item.get('summary', 'N/A')[:200],
                'published': item.get('published', '')
            })
    
    # 移除空分类
    categories = {k: v for k, v in categories.items() if v}
    
    # 生成简单的亮点
    highlights = []
    for i, item in enumerate(items[:5]):
        highlights.append(f"{item.get('title', 'N/A')}")
    
    return {
        "date": datetime.date.today().isoformat(),
        "total_items": len(items),
        "categories": categories,
        "category_summaries": {
            cat: f"今日{cat}类共有{len(items)}条内容"
            for cat, items in categories.items()
        },
        "highlights": highlights,
        "daily_summary": f"今日共收集{len(items)}条RSS内容，涵盖{len(categories)}个分类。这是使用简单分类生成的测试摘要，实际使用时请配置ANTHROPIC_API_KEY以获得AI驱动的智能分析。"
    }


def save_summary(summary: Dict[str, Any], date_str: str):
    """保存分析结果到文件"""
    output_file = SUMMARIES_DIR / f'{date_str}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f'总结已保存到: {output_file}')


def main():
    """主函数"""
    ensure_dirs()
    
    # 获取要处理的日期（默认为昨天）
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date_str = yesterday.isoformat()
    
    print(f'正在分析日期: {date_str}')
    print('⚠️  使用测试模式（简单分类），若要使用AI分析，请设置ANTHROPIC_API_KEY并运行analyze_rss.py')
    
    # 加载原始数据
    items = load_raw_items(date_str)
    print(f'找到 {len(items)} 条RSS条目')
    
    if not items:
        print('没有数据需要分析')
        return
    
    # 简单分类
    print('正在进行简单分类...')
    summary = simple_categorize(items)
    
    # 保存结果
    save_summary(summary, date_str)
    
    # 打印简要信息
    print(f'\n分析完成！')
    print(f'总条目数: {summary["total_items"]}')
    print(f'分类数: {len(summary.get("categories", {}))}')
    print(f'亮点数: {len(summary.get("highlights", []))}')


if __name__ == '__main__':
    main()
