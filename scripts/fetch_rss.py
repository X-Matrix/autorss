#!/usr/bin/env python3
import os
import sys
import hashlib
import json
import datetime
import pathlib
import re
from dateutil import parser as date_parser

import requests
import xml.etree.ElementTree as ET


# arXiv API configuration
ARXIV_API_URL = "https://export.arxiv.org/api/query"
ARXIV_QUERY_PARAMS = {
    'search_query': '(cat:cs.AI)',
    'sortBy': 'lastUpdatedDate',
    'sortOrder': 'descending',
    'start': 0,
    'max_results': 100
}

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'raw_content'
DATA_DIR = ROOT / 'data'
HISTORY_FILE = DATA_DIR / 'rss_history.txt'
STATE_FILE = DATA_DIR / 'feed_state.json'


def ensure_dirs():
    RAW_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)


def load_history():
    if not HISTORY_FILE.exists():
        return set()
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())


def append_history(hashes):
    if not hashes:
        return
    with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
        for h in hashes:
            f.write(h + '\n')


def sanitize_filename(s):
    s = s.strip()
    s = re.sub(r'[^0-9A-Za-z\-_. ]+', '_', s)
    return s[:200]


def fetch_arxiv_papers():
    """
    从 arXiv API 获取最新的 AI 论文
    """
    try:
        params = ARXIV_QUERY_PARAMS.copy()
        resp = requests.get(ARXIV_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        
        # 解析 Atom XML feed
        root = ET.fromstring(resp.content)
        
        # arXiv API 使用 Atom 格式
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entries = []
        for entry in root.findall('atom:entry', ns):
            # 提取论文信息
            paper = {
                'id': entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else '',
                'title': entry.find('atom:title', ns).text if entry.find('atom:title', ns) is not None else '',
                'summary': entry.find('atom:summary', ns).text if entry.find('atom:summary', ns) is not None else '',
                'published': entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else '',
                'updated': entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else '',
                'link': '',
                'authors': []
            }
            
            # 获取论文链接
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    paper['pdf_link'] = link.get('href', '')
                elif link.get('rel') == 'alternate':
                    paper['link'] = link.get('href', '')
            
            # 获取作者
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    paper['authors'].append(name.text)
            
            # 获取分类
            categories = []
            for category in entry.findall('atom:category', ns):
                term = category.get('term')
                if term:
                    categories.append(term)
            paper['categories'] = categories
            
            entries.append(paper)
        
        print(f'成功获取 {len(entries)} 篇 arXiv 论文')
        return entries
        
    except Exception as e:
        print(f'Failed to fetch arXiv papers: {e}', file=sys.stderr)
        return None


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_state(state):
    try:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f'Failed to save state: {e}', file=sys.stderr)


def process_arxiv_entries(entries, base_dir, seen_hashes, new_hashes, filter_yesterday=True):
    """处理 arXiv 论文条目
    
    Args:
        entries: arXiv 论文条目列表
        base_dir: 保存目录
        seen_hashes: 已处理的哈希集合
        new_hashes: 新增的哈希集合
        filter_yesterday: 是否只保留昨天发布的论文（基于 published 字段）
    
    Returns: (added_count, added_hashes_set, filtered_count)
    """
    if not entries:
        return 0, set(), 0
    
    added = 0
    filtered = 0
    added_hashes = set()
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    
    for entry in entries:
        # 使用论文ID作为唯一标识
        unique = entry.get('id', '')
        if not unique:
            continue
            
        h = hashlib.sha256(unique.encode('utf-8')).hexdigest()
        if h in seen_hashes or h in new_hashes or h in added_hashes:
            continue
        
        # 检查发布日期是否为昨天
        if filter_yesterday:
            published_str = entry.get('published', '')
            if published_str:
                try:
                    pub_date = date_parser.parse(published_str)
                    if pub_date.tzinfo is not None:
                        pub_date_utc = pub_date.astimezone(datetime.timezone.utc)
                        pub_day = pub_date_utc.date()
                    else:
                        pub_day = pub_date.date()
                    
                    # 只保留昨天发布的论文
                    if pub_day != yesterday:
                        filtered += 1
                        continue
                except Exception as e:
                    print(f'Failed to parse published date "{published_str}": {e}', file=sys.stderr)
                    filtered += 1
                    continue
            else:
                # 没有发布日期，跳过
                filtered += 1
                continue
        
        # 解析日期用于文件夹名（使用 updated 字段，因为它更能反映最新状态）
        date_str = entry.get('updated') or entry.get('published', '')
        if date_str:
            try:
                pub_date = date_parser.parse(date_str)
                if pub_date.tzinfo is not None:
                    pub_date_utc = pub_date.astimezone(datetime.timezone.utc)
                    date_folder = pub_date_utc.strftime('%Y-%m-%d')
                else:
                    date_folder = pub_date.strftime('%Y-%m-%d')
            except Exception as e:
                print(f'Failed to parse date "{date_str}": {e}, using today', file=sys.stderr)
                date_folder = today.isoformat()
        else:
            date_folder = today.isoformat()
        
        # 创建日期对应的目录
        target_dir = base_dir / date_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 构造条目数据（格式与原RSS保持一致，便于后续分析）
        item = {
            'title': entry.get('title', '').replace('\n', ' ').strip(),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'updated': entry.get('updated', ''),
            'summary': entry.get('summary', '').replace('\n', ' ').strip(),
            'id': entry.get('id', ''),
            'authors': entry.get('authors', []),
            'categories': entry.get('categories', []),
            'pdf_link': entry.get('pdf_link', ''),
        }
        
        fname = f"{h}.json"
        with open(target_dir / fname, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
        
        added_hashes.add(h)
        added += 1
    
    return added, added_hashes, filtered


def main():
    ensure_dirs()
    seen = load_history()
    new_hashes = set()

    print('从 arXiv API 获取最新 AI 论文...')
    
    # 获取 arXiv 论文
    entries = fetch_arxiv_papers()
    
    if entries is None:
        print('获取 arXiv 数据失败')
        return
    
    # 处理论文条目（只保留昨天发布的）
    added, added_hashes, filtered = process_arxiv_entries(entries, RAW_DIR, seen, new_hashes, filter_yesterday=True)
    
    if added:
        append_history(added_hashes)
        seen.update(added_hashes)
    
    print(f'成功添加 {added} 篇昨日发布的新论文')
    print(f'过滤掉 {filtered} 篇非昨日发布的论文')
    print(f'总计处理: {len(entries)} 篇论文')


if __name__ == '__main__':
    main()
