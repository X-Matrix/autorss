#!/usr/bin/env python3
"""
使用 NotebookLM 为每日新闻生成 podcast

基于 https://github.com/teng-lin/notebooklm-py 实现
将每日新闻摘要转换为引人入胜的播客内容
"""
import os
import sys
import json
import pathlib
import argparse
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from notebooklm import NotebookLMClient


ROOT = pathlib.Path(__file__).resolve().parents[1]
SUMMARIES_DIR = ROOT / 'data' / 'summaries'
PODCASTS_DIR = ROOT / 'data' / 'podcasts'


def ensure_dirs():
    """确保必要的目录存在"""
    PODCASTS_DIR.mkdir(parents=True, exist_ok=True)


def load_summary(date_str: str) -> dict:
    """加载指定日期的新闻摘要"""
    summary_file = SUMMARIES_DIR / f'{date_str}.json'
    if not summary_file.exists():
        raise FileNotFoundError(f'未找到 {date_str} 的新闻摘要文件')
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_news_for_podcast(summary: dict) -> str:
    """将新闻摘要格式化为适合生成 podcast 的文本内容"""
    date = summary.get('date', 'Unknown')
    total_items = summary.get('total_items', 0)
    categories = summary.get('categories', {})
    category_summaries = summary.get('category_summaries', {})
    
    # 构建内容文本
    content_parts = [
        f"# {date} 每日科技资讯播客",
        f"\n## 概览\n今日共收集 {total_items} 条资讯，涵盖以下领域：\n",
    ]
    
    # 添加各分类摘要
    if category_summaries:
        content_parts.append("\n## 分类概览\n")
        for cat, summary_text in category_summaries.items():
            content_parts.append(f"### {cat}\n{summary_text}\n")
    
    # 添加详细内容
    content_parts.append("\n## 详细资讯\n")
    for category, items in categories.items():
        if not items:
            continue
        
        content_parts.append(f"\n### {category} ({len(items)}条)\n")
        for idx, item in enumerate(items, 1):
            title = item.get('title_zh') or item.get('title', 'N/A')
            summary_text = item.get('summary_zh') or item.get('summary', 'N/A')
            link = item.get('link', '')
            published = item.get('published', '')
            
            content_parts.append(
                f"\n{idx}. **{title}**\n"
                f"   - 来源：{link}\n"
                f"   - 发布时间：{published}\n"
                f"   - 摘要：{summary_text}\n"
            )
    
    return '\n'.join(content_parts)


async def generate_podcast_for_date(date_str: str, audio_format: str = 'deep-dive', 
                                   audio_length: str = 'default', language: str = 'zh',
                                   wait_for_completion: bool = True, timeout: int = 600):
    """为指定日期的新闻生成 podcast
    
    Args:
        date_str: 日期字符串
        audio_format: podcast 格式
        audio_length: podcast 长度
        language: 语言代码
        wait_for_completion: 是否等待生成完成
        timeout: 超时时间（秒）
    """
    
    logger.info(f'开始为 {date_str} 生成 podcast...')
    
    # 加载新闻摘要
    try:
        summary = load_summary(date_str)
        logger.info(f'成功加载 {date_str} 的新闻摘要，共 {summary.get("total_items", 0)} 条资讯')
    except FileNotFoundError as e:
        logger.error(str(e))
        return False
    
    # 格式化内容
    news_content = format_news_for_podcast(summary)
    
    # 创建临时文本文件供 NotebookLM 使用
    temp_file = PODCASTS_DIR / f'{date_str}_content.md'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(news_content)
    logger.info(f'内容已保存到临时文件：{temp_file}')
    
    # 使用 NotebookLM API 生成 podcast
    async with await NotebookLMClient.from_storage() as client:
        # 创建一个新的 notebook
        notebook_title = f'每日科技资讯 - {date_str}'
        logger.info(f'创建 notebook: {notebook_title}')
        nb = await client.notebooks.create(notebook_title)
        logger.success(f'Notebook 已创建: {nb.id}')
        
        try:
            # 添加新闻内容作为源
            logger.info('正在添加新闻内容作为源...')
            source = await client.sources.add_file(
                nb.id, 
                str(temp_file)
            )
            logger.success(f'内容已添加为源: {source.id}')
            
            # 等待源处理完成
            logger.info('等待源处理完成...')
            max_wait = 60  # 最多等待60秒
            wait_time = 0
            while wait_time < max_wait:
                sources = await client.sources.list(nb.id)
                if sources:
                    # status 可能是字符串、整数或枚举，需要兼容处理
                    status = sources[0].status
                    status_str = status.value if hasattr(status, 'value') else str(status)
                    logger.debug(f'源状态: {status_str}')
                    if status_str == 'READY' or status_str == '2':  # 2 是 READY 的状态码
                        logger.success('源已准备就绪')
                        break
                await asyncio.sleep(5)
                wait_time += 5
                logger.info(f'等待中... ({wait_time}s/{max_wait}s)')
            
            if wait_time >= max_wait:
                logger.warning('源处理超时，但继续尝试生成 podcast')
            
            # 生成 podcast 指令
            instructions = (
                f"这是 {date_str} 的科技资讯摘要。"
                "请用专业但轻松的语调，为听众呈现今日科技新闻的亮点。"
                "重点突出各个领域的创新动态和重要趋势。"
                "适当加入主持人之间的互动讨论，使内容更生动有趣。"
            )
            
            # 映射音频格式
            from notebooklm import AudioFormat, AudioLength
            format_map = {
                'deep-dive': AudioFormat.DEEP_DIVE,
                'brief': AudioFormat.BRIEF,
                'critique': AudioFormat.CRITIQUE,
                'debate': AudioFormat.DEBATE
            }
            length_map = {
                'short': AudioLength.SHORT,
                'default': AudioLength.DEFAULT,
                'long': AudioLength.LONG
            }
            
            logger.info(f'开始生成 podcast (格式: {audio_format}, 长度: {audio_length})...')
            status = await client.artifacts.generate_audio(
                nb.id,
                language=language,
                instructions=instructions,
                audio_format=format_map.get(audio_format, AudioFormat.DEEP_DIVE),
                audio_length=length_map.get(audio_length, AudioLength.DEFAULT)
            )
            
            logger.info(f'Podcast 生成任务已提交，task_id: {status.task_id}')
            
            if not wait_for_completion:
                # 异步模式：不等待完成
                logger.info('🚀 异步模式：Podcast 正在后台生成')
                logger.info(f'   Notebook ID: {nb.id}')
                logger.info(f'   Task ID: {status.task_id}')
                logger.info('\n稍后可以使用以下命令下载：')
                logger.info(f'   notebooklm download audio ./data/podcasts/{date_str}_podcast.mp3 -n {nb.id}')
                logger.info('\n或访问 NotebookLM 网页查看进度：')
                logger.info(f'   https://notebooklm.google.com/notebook/{nb.id}')
                
                # 保存元数据
                metadata = {
                    'date': date_str,
                    'notebook_id': nb.id,
                    'task_id': status.task_id,
                    'audio_format': audio_format,
                    'audio_length': audio_length,
                    'language': language,
                    'total_items': summary.get('total_items', 0),
                    'categories': list(summary.get('categories', {}).keys()),
                    'status': 'generating',
                    'submitted_at': datetime.now().isoformat()
                }
                
                metadata_file = PODCASTS_DIR / f'{date_str}_metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                logger.info(f'元数据已保存到: {metadata_file}')
                
                return True
            
            # 同步模式：等待完成
            logger.info(f'等待生成完成（最多 {timeout} 秒，这可能需要几分钟）...')
            logger.info('💡 提示：下次可以使用 --no-wait 参数异步生成')
            
            # 等待生成完成
            try:
                final_status = await client.artifacts.wait_for_completion(
                    nb.id, 
                    status.task_id,
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.warning(f'⏱️  等待超时（{timeout}秒），但生成任务仍在进行中')
                logger.info(f'\nNotebook ID: {nb.id}')
                logger.info(f'Task ID: {status.task_id}')
                logger.info('\n你可以：')
                logger.info('1. 访问 NotebookLM 网页查看进度：')
                logger.info(f'   https://notebooklm.google.com/notebook/{nb.id}')
                logger.info('2. 稍后使用命令下载：')
                logger.info(f'   notebooklm download audio ./data/podcasts/{date_str}_podcast.mp3 -n {nb.id}')
                
                # 保存元数据
                metadata = {
                    'date': date_str,
                    'notebook_id': nb.id,
                    'task_id': status.task_id,
                    'audio_format': audio_format,
                    'audio_length': audio_length,
                    'language': language,
                    'total_items': summary.get('total_items', 0),
                    'categories': list(summary.get('categories', {}).keys()),
                    'status': 'timeout_but_generating',
                    'submitted_at': datetime.now().isoformat(),
                    'timeout_at': datetime.now().isoformat()
                }
                
                metadata_file = PODCASTS_DIR / f'{date_str}_metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return True  # 任务已提交，视为成功
            
            if final_status.status == 'COMPLETED':
                logger.success('Podcast 生成成功！')
                
                # 下载 podcast
                output_file = PODCASTS_DIR / f'{date_str}_podcast.mp3'
                logger.info(f'正在下载 podcast 到 {output_file}...')
                await client.artifacts.download_audio(nb.id, str(output_file))
                logger.success(f'Podcast 已保存到: {output_file}')
                
                # 保存元数据
                metadata = {
                    'date': date_str,
                    'notebook_id': nb.id,
                    'task_id': status.task_id,
                    'audio_format': audio_format,
                    'audio_length': audio_length,
                    'language': language,
                    'total_items': summary.get('total_items', 0),
                    'categories': list(summary.get('categories', {}).keys()),
                    'generated_at': datetime.now().isoformat(),
                    'output_file': str(output_file)
                }
                
                metadata_file = PODCASTS_DIR / f'{date_str}_metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                logger.info(f'元数据已保存到: {metadata_file}')
                
                return True
            else:
                logger.error(f'Podcast 生成失败，状态: {final_status.status}')
                return False
                
        except Exception as e:
            logger.error(f'生成 podcast 时出错: {e}')
            raise
        finally:
            # 可选：删除临时 notebook（如果需要保留可以注释掉）
            # logger.info(f'清理 notebook: {nb.id}')
            # await client.notebooks.delete(nb.id)
            # logger.info('Notebook 已删除')
            logger.info(f'Notebook 保留用于审查: {nb.id}')


async def main():
    parser = argparse.ArgumentParser(description='为每日新闻生成 podcast')
    parser.add_argument(
        '--date', 
        type=str, 
        help='日期（格式: YYYY-MM-DD），默认为昨天'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['deep-dive', 'brief', 'critique', 'debate'],
        default='deep-dive',
        help='Podcast 格式 (默认: deep-dive)'
    )
    parser.add_argument(
        '--length',
        type=str,
        choices=['short', 'default', 'long'],
        default='default',
        help='Podcast 长度 (默认: default)'
    )
    parser.add_argument(
        '--language',
        type=str,
        default='zh',
        help='语言代码 (默认: zh 中文)'
    )
    parser.add_argument(
        '--no-wait',
        action='store_true',
        help='异步模式：提交任务后立即返回，不等待生成完成'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='等待超时时间（秒，默认: 600）'
    )
    
    args = parser.parse_args()
    
    # 确保目录存在
    ensure_dirs()
    
    # 确定日期
    if args.date:
        date_str = args.date
    else:
        # 默认使用昨天的日期
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    
    logger.info(f'目标日期: {date_str}')
    
    # 生成 podcast
    try:
        success = await generate_podcast_for_date(
            date_str, 
            audio_format=args.format,
            audio_length=args.length,
            language=args.language,
            wait_for_completion=not args.no_wait,
            timeout=args.timeout
        )
        
        if success:
            logger.success('🎉 Podcast 生成完成！')
            sys.exit(0)
        else:
            logger.error('❌ Podcast 生成失败')
            sys.exit(1)
            
    except Exception as e:
        logger.exception(f'发生错误: {e}')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
