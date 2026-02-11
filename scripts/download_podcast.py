#!/usr/bin/env python3
"""
下载已生成的 podcast

从之前提交的异步任务中下载 podcast 音频文件
"""
import os
import sys
import json
import pathlib
import argparse
import asyncio
from loguru import logger
from notebooklm import NotebookLMClient


ROOT = pathlib.Path(__file__).resolve().parents[1]
PODCASTS_DIR = ROOT / 'data' / 'podcasts'


def get_storage_state_path() -> str:
    """从环境变量获取 NotebookLM storage_state.json 路径
    
    环境变量: NOTEBOOKLM_STORAGE_STATE
    默认路径: ~/.notebooklm/storage_state.json
    """
    storage_path = os.getenv('NOTEBOOKLM_STORAGE_STATE')
    if storage_path:
        logger.info(f'使用环境变量指定的 storage_state 路径: {storage_path}')
        return storage_path
    
    # 使用默认路径
    default_path = pathlib.Path.home() / '.notebooklm' / 'storage_state.json'
    logger.debug(f'使用默认 storage_state 路径: {default_path}')
    return str(default_path)


async def download_podcast(date_str: str = None, notebook_id: str = None):
    """下载 podcast"""
    
    # 如果提供了日期，从元数据文件中读取 notebook_id
    if date_str and not notebook_id:
        metadata_file = PODCASTS_DIR / f'{date_str}_metadata.json'
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                notebook_id = metadata.get('notebook_id')
                logger.info(f'从元数据文件读取 Notebook ID: {notebook_id}')
        else:
            logger.error(f'未找到 {date_str} 的元数据文件')
            return False
    
    if not notebook_id:
        logger.error('必须提供日期或 Notebook ID')
        return False
    
    # 确定输出文件名
    if date_str:
        output_file = PODCASTS_DIR / f'{date_str}_podcast.mp3'
    else:
        output_file = PODCASTS_DIR / f'{notebook_id[:8]}_podcast.mp3'
    
    logger.info(f'准备下载 Podcast...')
    logger.info(f'  Notebook ID: {notebook_id}')
    logger.info(f'  输出文件: {output_file}')
    
    try:
        storage_path = get_storage_state_path()
        async with await NotebookLMClient.from_storage(storage_path) as client:
            # 检查 artifact 状态
            logger.info('检查 Podcast 生成状态...')
            artifacts = await client.artifacts.list(notebook_id)
            
            if not artifacts:
                logger.error('未找到任何 artifact，可能还在生成中')
                logger.info('请访问 NotebookLM 网页查看状态：')
                logger.info(f'  https://notebooklm.google.com/notebook/{notebook_id}')
                return False
            
            # 直接使用 list_audio 获取音频 artifacts
            logger.debug(f'找到 {len(artifacts)} 个 artifacts')
            audio_artifacts = await client.artifacts.list_audio(notebook_id)
            
            if not audio_artifacts:
                logger.error('未找到音频 artifact，可能还在生成中')
                logger.info('请访问 NotebookLM 网页查看状态：')
                logger.info(f'  https://notebooklm.google.com/notebook/{notebook_id}')
                return False
            
            # 使用最新的音频
            latest_audio = audio_artifacts[0]
            logger.info(f'找到音频 artifact: {latest_audio.id}')
            logger.info(f'  标题: {latest_audio.title}')
            
            # 检查状态
            status = latest_audio.status
            status_str = status.value if hasattr(status, 'value') else str(status)
            logger.info(f'  状态: {status_str}')
            
            if status_str not in ['COMPLETED', 'completed', '3']:
                logger.warning(f'音频还未完成生成，当前状态: {status_str}')
                logger.info('请稍后再试或访问 NotebookLM 查看进度')
                return False
            
            # 下载
            logger.info('开始下载...')
            await client.artifacts.download_audio(
                notebook_id,
                str(output_file),
                artifact_id=latest_audio.id
            )
            
            logger.success(f'✅ Podcast 已下载到: {output_file}')
            logger.info(f'   文件大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB')
            
            # 更新元数据
            if date_str:
                metadata_file = PODCASTS_DIR / f'{date_str}_metadata.json'
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    metadata['status'] = 'completed'
                    metadata['downloaded_at'] = asyncio.get_event_loop().time()
                    metadata['output_file'] = str(output_file)
                    
                    with open(metadata_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return True
            
    except Exception as e:
        logger.error(f'下载失败: {e}')
        return False


async def main():
    parser = argparse.ArgumentParser(description='下载已生成的 podcast')
    parser.add_argument(
        '--date',
        type=str,
        help='日期（格式: YYYY-MM-DD）'
    )
    parser.add_argument(
        '--notebook-id',
        type=str,
        help='Notebook ID'
    )
    
    args = parser.parse_args()
    
    if not args.date and not args.notebook_id:
        # 尝试从最新的元数据文件中读取
        metadata_files = sorted(PODCASTS_DIR.glob('*_metadata.json'), reverse=True)
        if metadata_files:
            latest = metadata_files[0]
            date_str = latest.stem.replace('_metadata', '')
            logger.info(f'未指定日期，使用最新的: {date_str}')
            args.date = date_str
        else:
            logger.error('未找到任何元数据文件')
            logger.info('请使用 --date 或 --notebook-id 指定要下载的 podcast')
            sys.exit(1)
    
    success = await download_podcast(args.date, args.notebook_id)
    
    if success:
        logger.success('🎉 下载完成！')
        sys.exit(0)
    else:
        logger.error('❌ 下载失败')
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
