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
import feedparser
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
RSS_DIR = ROOT / 'rss'
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


def parse_source_file(path):
    text = path.read_text(encoding='utf-8').strip()
    if text.startswith('http://') or text.startswith('https://'):
        return ('url', text)
    # try to detect OPML and extract feed URLs
    try:
        root = ET.fromstring(text.encode('utf-8'))
        if root.tag.lower().endswith('opml'):
            urls = []
            for out in root.findall('.//outline'):
                xmlurl = out.attrib.get('xmlUrl') or out.attrib.get('xmlurl')
                if xmlurl:
                    urls.append(xmlurl)
            return ('opml', urls)
    except ET.ParseError:
        pass
    # otherwise treat file content as XML data (single feed)
    return ('xml', text)


def fetch_feed_from_url(url):
    # legacy compatibility: keep simple fetch (not used)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return feedparser.parse(resp.content)
    except Exception as e:
        print(f'Failed to fetch {url}: {e}', file=sys.stderr)
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


def fetch_feed_with_state(url, state):
    headers = {}
    s = state.get(url, {}) or {}
    if s.get('etag'):
        headers['If-None-Match'] = s['etag']
    if s.get('modified'):
        headers['If-Modified-Since'] = s['modified']
    try:
        resp = requests.get(url, timeout=30, headers=headers)
        if resp.status_code == 304:
            return None, s
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
        new_meta = {'etag': resp.headers.get('ETag'), 'modified': resp.headers.get('Last-Modified')}
        return parsed, new_meta
    except Exception as e:
        print(f'Failed to fetch {url}: {e}', file=sys.stderr)
        return None, s


def process_feed(feed, base_dir, seen_hashes, new_hashes):
    """Process feed entries.

    Returns: (added_count, added_hashes_set)
    """
    if not feed:
        return 0, set()
    added = 0
    added_hashes = set()
    for entry in feed.entries:
        unique = entry.get('id') or entry.get('link') or (entry.get('title', '') + entry.get('published', ''))
        h = hashlib.sha256(unique.encode('utf-8')).hexdigest()
        if h in seen_hashes or h in new_hashes or h in added_hashes:
            continue
        
        # 解析发布日期
        published_str = entry.get('published', '')
        if published_str:
            try:
                # 尝试解析日期，保留时区信息
                pub_date = date_parser.parse(published_str)
                # 如果有时区信息，转换为UTC；否则视为本地时间
                if pub_date.tzinfo is not None:
                    # 转换到UTC
                    pub_date_utc = pub_date.astimezone(datetime.timezone.utc)
                    # 使用UTC日期作为文件夹名
                    date_folder = pub_date_utc.strftime('%Y-%m-%d')
                else:
                    # 没有时区信息，使用原始日期
                    date_folder = pub_date.strftime('%Y-%m-%d')
            except Exception as e:
                print(f'Failed to parse date "{published_str}": {e}, using today', file=sys.stderr)
                date_folder = datetime.date.today().isoformat()
        else:
            # 如果没有发布日期，使用今天的日期
            date_folder = datetime.date.today().isoformat()
        
        # 创建日期对应的目录
        target_dir = base_dir / date_folder
        target_dir.mkdir(parents=True, exist_ok=True)
        
        item = {
            'title': entry.get('title'),
            'link': entry.get('link'),
            'published': published_str,
            'summary': entry.get('summary', ''),
            'id': entry.get('id', ''),
        }
        fname = f"{h}.json"
        with open(target_dir / fname, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
        added_hashes.add(h)
        added += 1
    return added, added_hashes


def main():
    ensure_dirs()
    seen = load_history()
    new_hashes = set()

    total_added = 0
    if not RSS_DIR.exists():
        print('rss directory not found; nothing to do')
        return

    state = load_state()

    for src in RSS_DIR.glob('*.xml'):
        kind, payload = parse_source_file(src)
        print(f'Processing source: {src} ({kind})')
        if kind == 'url':
            feed = None
            new_meta = {}
            feed, new_meta = fetch_feed_with_state(payload, state)
            added, added_hashes = process_feed(feed, RAW_DIR, seen, new_hashes)
            if added:
                append_history(added_hashes)
                seen.update(added_hashes)
            # update and persist feed state even if no new items
            if feed is not None:
                state[payload] = new_meta
                save_state(state)
            print(f'Added {added} items from {src.name}')
            total_added += added
        elif kind == 'opml':
            for url in payload:
                print(f'  fetching {url}')
                feed, new_meta = fetch_feed_with_state(url, state)
                if feed is None:
                    print(f'  no change for {url} (skipping)')
                    # still persist state entry if present
                    if url in state:
                        save_state(state)
                    continue
                added, added_hashes = process_feed(feed, RAW_DIR, seen, new_hashes)
                if added:
                    append_history(added_hashes)
                    seen.update(added_hashes)
                    print(f'  Added {added} items from {url}')
                # persist state for this feed
                state[url] = new_meta
                save_state(state)
                total_added += added
        else:
            feed = feedparser.parse(payload)
            added, added_hashes = process_feed(feed, RAW_DIR, seen, new_hashes)
            if added:
                append_history(added_hashes)
                seen.update(added_hashes)
            print(f'Added {added} items from {src.name}')
            total_added += added

    append_history(new_hashes)
    print(f'Total new items: {total_added}')


if __name__ == '__main__':
    main()
