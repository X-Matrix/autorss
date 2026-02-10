#!/usr/bin/env python3
"""
使用LLM分析RSS数据，进行分类和翻译，生成每日总结和摘要。
"""
import os
import sys
import json
import pathlib
import datetime
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
from loguru import logger


ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / 'raw_content'
DATA_DIR = ROOT / 'data'
SUMMARIES_DIR = DATA_DIR / 'summaries'


def ensure_dirs():
    """确保必要的目录存在"""
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / 'logs').mkdir(parents=True, exist_ok=True)


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
            logger.warning(f'Failed to load {json_file}: {e}')
    
    return items


async def analyze_batch(batch_items: List[Dict[str, Any]], batch_num: int, client: AsyncOpenAI) -> Dict[str, Any]:
    """
    异步分析一个批次的RSS条目
    """
    if not batch_items:
        return {"categories": {}, "highlights": []}
    
    # 准备发送给LLM的数据
    items_text = "\n\n".join([
        f"标题: {item.get('title', 'N/A')}\n"
        f"链接: {item.get('link', 'N/A')}\n"
        f"摘要: {item.get('summary', 'N/A')[:200]}"
        for item in batch_items
    ])
    
    prompt = f"""请分析以下{len(batch_items)}条RSS内容，完成以下任务：

1. 将这些内容分类到合适的类别（如：技术、科学、商业、设计、AI/机器学习、开源项目、新闻等）
2. 对每条内容的标题和摘要进行中文翻译（如果原文是英文）
3. 选出最值得关注的亮点（2-3个）

请以JSON格式返回结果，格式如下：
{{
    "categories": {{
        "类别名称": [
            {{
                "title": "原标题",
                "title_zh": "中文标题",
                "link": "链接",
                "summary": "原摘要",
                "summary_zh": "中文摘要",
                "published": "发布时间"
            }}
        ]
    }},
    "highlights": [
        "亮点1：xxx",
        "亮点2：xxx"
    ]
}}

RSS内容：

{items_text}
"""
    
    try:
        logger.info(f'批次 {batch_num}: 正在分析 {len(batch_items)} 条内容...')
        response = await client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=4000,
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "你是一个专业的技术内容分析助手，擅长分类和总结技术资讯。请始终以JSON格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        logger.debug(f'批次 {batch_num}: API调用成功，使用token数: {response.usage.total_tokens}')
        
        # 提取JSON响应
        response_text = response.choices[0].message.content
        
        # 解析JSON
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response_text)
        
        logger.success(f'批次 {batch_num}: 分析完成')
        return result
        
    except Exception as e:
        logger.error(f'批次 {batch_num}: 分析失败 - {e}')
        # 返回简单分类
        return {
            "categories": {
                "未分类": [
                    {
                        "title": item.get('title', 'N/A'),
                        "title_zh": item.get('title', 'N/A'),
                        "link": item.get('link', 'N/A'),
                        "summary": item.get('summary', 'N/A'),
                        "summary_zh": item.get('summary', 'N/A'),
                        "published": item.get('published', '')
                    }
                    for item in batch_items
                ]
            },
            "highlights": []
        }


async def categorize_and_translate(items: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    """
    使用LLM对RSS条目进行分批异步分析和翻译
    """
    if not items:
        return {
            "date": datetime.date.today().isoformat(),
            "total_items": 0,
            "categories": {},
            "category_summaries": {},
            "summary": "今日无新内容",
            "highlights": []
        }
    
    # 创建异步客户端
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )
    
    # 分批处理，每批20条
    batch_size = 20
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    logger.info(f'共 {len(items)} 条内容，分为 {len(batches)} 个批次进行并发分析')
    
    # 并发处理所有批次
    tasks = [analyze_batch(batch, i+1, client) for i, batch in enumerate(batches)]
    batch_results = await asyncio.gather(*tasks)
    
    # 合并所有批次结果
    merged_categories = {}
    all_highlights = []
    
    for result in batch_results:
        # 合并分类
        for category, items_list in result.get('categories', {}).items():
            if category not in merged_categories:
                merged_categories[category] = []
            merged_categories[category].extend(items_list)
        
        # 收集亮点
        all_highlights.extend(result.get('highlights', []))
    
    # 生成整体总结（使用第一批的部分内容作为代表）
    logger.info('正在生成整体总结...')
    summary_prompt = f"""基于今天收集的{len(items)}条技术资讯，已分为{len(merged_categories)}个类别：
{', '.join(merged_categories.keys())}

请生成：
1. 每个类别的简短总结
2. 整体的每日总结（2-3段）

返回JSON格式：
{{
    "category_summaries": {{
        "类别名称": "该类别的简短总结"
    }},
    "daily_summary": "今日总结文本（2-3段）"
}}
"""
    
    try:
        summary_response = await client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=2000,
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "你是一个专业的技术内容总结助手。请以JSON格式返回结果。"},
                {"role": "user", "content": summary_prompt}
            ]
        )
        
        summary_text = summary_response.choices[0].message.content
        import re
        json_match = re.search(r'\{.*\}', summary_text, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group())
        else:
            summary_data = json.loads(summary_text)
        
        category_summaries = summary_data.get('category_summaries', {})
        daily_summary = summary_data.get('daily_summary', f'今日共收集{len(items)}条内容，涵盖{len(merged_categories)}个分类。')
        
        logger.success('整体总结生成完成')
        
    except Exception as e:
        logger.warning(f'总结生成失败: {e}，使用默认总结')
        category_summaries = {cat: f'今日{cat}类共有{len(items)}条内容' for cat, items in merged_categories.items()}
        daily_summary = f'今日共收集{len(items)}条内容，涵盖{len(merged_categories)}个分类。'
    
    # 返回最终结果
    return {
        "date": datetime.date.today().isoformat(),
        "total_items": len(items),
        "categories": merged_categories,
        "category_summaries": category_summaries,
        "highlights": all_highlights[:10],  # 只保留前10个亮点
        "daily_summary": daily_summary
    }


def save_summary(summary: Dict[str, Any], date_str: str):
    """保存分析结果到文件"""
    output_file = SUMMARIES_DIR / f'{date_str}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    logger.success(f'总结已保存到: {output_file}')


async def async_main():
    """异步主函数"""
    # 从环境变量获取API密钥
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error('请设置环境变量 OPENAI_API_KEY')
        sys.exit(1)
    
    # 获取要处理的日期（默认为昨天）
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        date_str = yesterday.isoformat()
    
    logger.info(f'正在分析日期: {date_str}')
    
    # 加载原始数据
    items = load_raw_items(date_str)
    logger.info(f'找到 {len(items)} 条RSS条目')
    
    if not items:
        logger.warning('没有数据需要分析')
        return
    
    # 使用LLM分析（异步并发）
    logger.info('正在使用LLM进行分批异步分析...')
    summary = await categorize_and_translate(items, api_key)
    
    # 保存结果
    save_summary(summary, date_str)
    
    # 打印简要信息
    logger.success('分析完成！')
    logger.info(f'总条目数: {summary["total_items"]}')
    logger.info(f'分类数: {len(summary.get("categories", {}))}')
    logger.info(f'亮点数: {len(summary.get("highlights", []))}')


def main():
    """主函数"""
    # 配置logger
    logger.remove()  # 移除默认handler
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
    logger.add(DATA_DIR / 'logs' / 'analyze_{time:YYYY-MM-DD}.log', rotation="00:00", retention="30 days", encoding='utf-8')
    
    ensure_dirs()
    
    # 运行异步主函数
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
