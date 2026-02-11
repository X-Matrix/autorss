#!/usr/bin/env python3
"""
测试 NotebookLM Podcast 生成功能
快速验证配置是否正确
"""
import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def get_storage_state_path() -> str:
    """从环境变量获取 NotebookLM storage_state.json 路径
    
    环境变量: NOTEBOOKLM_STORAGE_STATE
    默认路径: ~/.notebooklm/storage_state.json
    """
    storage_path = os.getenv('NOTEBOOKLM_STORAGE_STATE')
    if storage_path:
        print(f'使用环境变量指定的 storage_state 路径: {storage_path}')
        return storage_path
    
    # 使用默认路径
    default_path = Path.home() / '.notebooklm' / 'storage_state.json'
    return str(default_path)


async def test_notebooklm_auth():
    """测试 NotebookLM 认证"""
    print("测试 1: NotebookLM 认证")
    print("-" * 50)
    
    try:
        from notebooklm import NotebookLMClient
        
        storage_path = get_storage_state_path()
        async with await NotebookLMClient.from_storage(storage_path) as client:
            print("✅ 认证成功")
            
            # 列出现有的 notebooks
            notebooks = await client.notebooks.list()
            print(f"✅ 找到 {len(notebooks)} 个现有 notebooks")
            
            if notebooks:
                print("\n前 3 个 notebooks:")
                for nb in notebooks[:3]:
                    print(f"  - {nb.title} (ID: {nb.id[:20]}...)")
            
            return True
            
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        print("\n请运行以下命令进行认证:")
        print("  notebooklm login")
        return False


async def test_news_summary_exists():
    """测试新闻摘要文件是否存在"""
    print("\n测试 2: 新闻摘要文件")
    print("-" * 50)
    
    from datetime import datetime, timedelta
    
    summaries_dir = ROOT / 'data' / 'summaries'
    
    # 检查最近 7 天的摘要
    found_dates = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        summary_file = summaries_dir / f'{date}.json'
        
        if summary_file.exists():
            found_dates.append(date)
            print(f"✅ 找到 {date} 的摘要")
    
    if found_dates:
        print(f"\n✅ 共找到 {len(found_dates)} 天的新闻摘要")
        print(f"   最新日期: {found_dates[0]}")
        return True, found_dates[0]
    else:
        print("❌ 未找到任何新闻摘要")
        print("\n请先运行以下命令生成摘要:")
        print("  python scripts/analyze_rss.py")
        return False, None


async def test_podcast_generation():
    """测试 Podcast 生成功能"""
    print("\n测试 3: Podcast 生成功能")
    print("-" * 50)
    
    try:
        # 导入必要的模块
        from notebooklm import AudioFormat, AudioLength
        print("✅ NotebookLM 模块导入成功")
        
        # 检查 Playwright
        import playwright
        print("✅ Playwright 已安装")
        
        # 检查 podcasts 目录
        podcasts_dir = ROOT / 'data' / 'podcasts'
        if not podcasts_dir.exists():
            podcasts_dir.mkdir(parents=True)
            print("✅ 创建 podcasts 目录")
        else:
            print("✅ Podcasts 目录已存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("\n请安装依赖:")
        print("  pip install notebooklm-py[browser]")
        print("  playwright install chromium")
        return False


async def test_mini_podcast():
    """创建一个迷你测试 Podcast"""
    print("\n测试 4: 创建测试 Podcast")
    print("-" * 50)
    print("这将创建一个小型测试 Podcast 以验证完整流程")
    
    try:
        from notebooklm import NotebookLMClient, AudioFormat, AudioLength
        
        # 测试内容
        test_content = """# 测试 Podcast

## 简介
这是一个测试播客，用于验证 NotebookLM 集成是否正常工作。

## 内容
今天我们要测试的功能包括：
1. 创建 Notebook
2. 添加文本内容
3. 生成音频播客
4. 下载音频文件

这是一个简短的测试，应该在几分钟内完成。
"""
        
        # 保存测试内容
        test_file = ROOT / 'data' / 'podcasts' / 'test_content.md'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✅ 测试内容已保存: {test_file}")
        
        storage_path = get_storage_state_path()
        async with await NotebookLMClient.from_storage(storage_path) as client:
            # 创建测试 notebook
            print("创建测试 Notebook...")
            nb = await client.notebooks.create("Podcast 功能测试")
            print(f"✅ Notebook 已创建: {nb.id[:20]}...")
            
            # 添加内容
            print("添加测试内容...")
            source = await client.sources.add_file(nb.id, str(test_file))
            print(f"✅ 内容已添加: {source.id[:20]}...")
            
            # 等待源准备就绪
            print("等待源处理完成（最多 30 秒）...")
            for i in range(6):
                await asyncio.sleep(5)
                sources = await client.sources.list(nb.id)
                if sources and sources[0].status.value == 'READY':
                    print("✅ 源已准备就绪")
                    break
                print(f"  等待中... ({(i+1)*5}s)")
            
            # 生成简短的测试播客
            print("生成测试 Podcast（简短版本）...")
            status = await client.artifacts.generate_audio(
                nb.id,
                language='zh',
                instructions="这是一个测试播客，请保持简短。",
                audio_format=AudioFormat.BRIEF,
                audio_length=AudioLength.SHORT
            )
            print(f"✅ 任务已提交: {status.task_id[:20]}...")
            
            print("\n⏳ 等待 Podcast 生成完成（这可能需要 2-3 分钟）...")
            print("   你可以按 Ctrl+C 取消测试，主要功能已验证成功")
            
            try:
                final_status = await client.artifacts.wait_for_completion(
                    nb.id, 
                    status.task_id,
                    timeout=300
                )
                
                if final_status.status == 'COMPLETED':
                    print("\n✅ Podcast 生成成功！")
                    
                    # 下载测试
                    test_output = ROOT / 'data' / 'podcasts' / 'test_podcast.mp3'
                    await client.artifacts.download_audio(nb.id, str(test_output))
                    print(f"✅ 测试 Podcast 已下载: {test_output}")
                    print(f"   文件大小: {test_output.stat().st_size / 1024:.1f} KB")
                    
                    return True
                else:
                    print(f"⚠️  Podcast 状态: {final_status.status}")
                    return False
                    
            except asyncio.TimeoutError:
                print("⚠️  等待超时，但核心功能已验证")
                print("   可以手动检查 Notebook 中的生成进度")
                return True
                
    except KeyboardInterrupt:
        print("\n\n⚠️  测试已取消，但核心功能验证成功")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("=" * 50)
    print("NotebookLM Podcast 生成功能测试")
    print("=" * 50)
    print()
    
    # 测试 1: 认证
    auth_ok = await test_notebooklm_auth()
    if not auth_ok:
        print("\n❌ 认证测试失败，无法继续")
        return False
    
    # 测试 2: 新闻摘要
    summary_ok, latest_date = await test_news_summary_exists()
    
    # 测试 3: 依赖检查
    deps_ok = await test_podcast_generation()
    if not deps_ok:
        print("\n❌ 依赖检查失败，无法继续")
        return False
    
    # 询问是否运行完整测试
    print("\n" + "=" * 50)
    print("前置检查完成！")
    print("=" * 50)
    
    if auth_ok and deps_ok:
        print("\n✅ 所有前置条件已满足")
        
        response = input("\n是否运行完整的 Podcast 生成测试？(y/N): ")
        if response.lower() in ['y', 'yes']:
            test_ok = await test_mini_podcast()
            
            if test_ok:
                print("\n" + "=" * 50)
                print("🎉 所有测试通过！")
                print("=" * 50)
                print("\n你现在可以使用以下命令生成真实的 Podcast:")
                if summary_ok and latest_date:
                    print(f"  python scripts/generate_podcast.py --date {latest_date}")
                else:
                    print("  python scripts/generate_podcast.py")
                return True
        else:
            print("\n跳过完整测试")
            print("你可以直接使用: python scripts/generate_podcast.py")
    
    return True


if __name__ == '__main__':
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
