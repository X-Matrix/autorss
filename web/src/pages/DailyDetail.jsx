import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

export default function DailyDetail() {
  const { date } = useParams()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeCategory, setActiveCategory] = useState(null)

  useEffect(() => {
    loadSummary()
  }, [date])

  const loadSummary = async () => {
    try {
      // 从静态文件加载
      const response = await fetch(`/data/summaries/${date}.json`)
      if (!response.ok) {
        throw new Error('Summary not found')
      }
      const data = await response.json()
      setSummary(data)
      if (data.categories) {
        setActiveCategory(Object.keys(data.categories)[0])
      }
      setLoading(false)
    } catch (error) {
      console.error('Failed to load summary:', error)
      // 如果加载失败，使用模拟数据
      const mockData = generateMockDetailData(date)
      setSummary(mockData)
      if (mockData.categories) {
        setActiveCategory(Object.keys(mockData.categories)[0])
      }
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-accent text-lg">加载中...</div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="text-center py-16">
        <p className="text-gray-400">未找到该日期的数据</p>
        <Link to="/" className="link mt-4 inline-block">返回首页</Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* 头部 */}
      <div>
        <Link to="/" className="text-accent hover:text-accent-dark inline-flex items-center mb-4">
          ← 返回首页
        </Link>
        <h2 className="text-4xl font-bold text-white mb-2">
          {formatDate(summary.date)}
        </h2>
        <p className="text-gray-400">
          共 {summary.total_items} 条内容 · {Object.keys(summary.categories || {}).length} 个分类
        </p>
      </div>

      {/* 每日总结 */}
      {summary.daily_summary && (
        <div className="card">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <span className="mr-2">📝</span>
            每日总结
          </h3>
          <div className="prose prose-invert max-w-none">
            <p className="text-gray-300 leading-relaxed whitespace-pre-line">
              {summary.daily_summary}
            </p>
          </div>
        </div>
      )}

      {/* 亮点 */}
      {summary.highlights && summary.highlights.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center">
            <span className="mr-2">✨</span>
            今日亮点
          </h3>
          <ul className="space-y-3">
            {summary.highlights.map((highlight, idx) => (
              <li key={idx} className="flex items-start text-gray-300">
                <span className="text-accent font-bold mr-3 mt-1">{idx + 1}.</span>
                <span>{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 分类内容 */}
      <div className="card">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center">
          <span className="mr-2">📂</span>
          分类内容
        </h3>

        {/* 分类标签 */}
        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-700 pb-4">
          {Object.keys(summary.categories || {}).map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeCategory === category
                  ? 'bg-accent text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {category} ({summary.categories[category].length})
            </button>
          ))}
        </div>

        {/* 分类摘要 */}
        {summary.category_summaries && summary.category_summaries[activeCategory] && (
          <div className="bg-dark p-4 rounded-lg mb-6 border-l-4 border-accent">
            <p className="text-gray-300 text-sm italic">
              {summary.category_summaries[activeCategory]}
            </p>
          </div>
        )}

        {/* 文章列表 */}
        <div className="space-y-4">
          {summary.categories[activeCategory]?.map((item, idx) => (
            <ArticleCard key={idx} item={item} />
          ))}
        </div>
      </div>
    </div>
  )
}

function ArticleCard({ item }) {
  const [showOriginal, setShowOriginal] = useState(false)

  return (
    <div className="bg-dark p-4 rounded-lg border border-gray-700 hover:border-accent transition-all">
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-lg font-semibold text-white flex-1">
          {showOriginal ? item.title : (item.title_zh || item.title)}
        </h4>
        <button
          onClick={() => setShowOriginal(!showOriginal)}
          className="ml-4 text-xs text-gray-500 hover:text-accent transition-colors"
        >
          {showOriginal ? '中文' : '原文'}
        </button>
      </div>
      
      <p className="text-gray-400 text-sm mb-3 line-clamp-2">
        {showOriginal ? item.summary : (item.summary_zh || item.summary)}
      </p>
      
      <div className="flex items-center justify-between">
        <a 
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
          className="link text-sm"
        >
          阅读原文 →
        </a>
        {item.published && (
          <span className="text-xs text-gray-600">
            {new Date(item.published).toLocaleDateString('zh-CN')}
          </span>
        )}
      </div>
    </div>
  )
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return date.toLocaleDateString('zh-CN', options)
}

// 生成模拟详细数据
function generateMockDetailData(date) {
  return {
    date: date,
    total_items: 45,
    daily_summary: `今天的技术资讯涵盖了多个领域的重要进展。在AI领域，OpenAI发布了GPT-4的最新更新，性能和效率都有显著提升。开源社区也异常活跃，多个流行项目发布了重大版本更新。

科学研究方面，NASA公布了火星探测的新发现，为人类未来的星际探索提供了重要参考。同时，量子计算领域也取得了突破性进展。

总体而言，今天的技术动态展现了科技持续快速发展的趋势，值得持续关注。`,
    highlights: [
      'OpenAI 发布 GPT-4 Turbo 新版本，推理速度提升 30%，成本降低 50%',
      'React 19 Beta 版本发布，引入革命性的并发渲染和服务器组件',
      'NASA 火星探测器发现地下冰层证据，为未来载人任务提供支持',
      'GitHub Copilot 新增多语言支持，代码建议准确率提升至 85%',
      '量子计算突破：Google 实现 1000 量子比特处理器',
    ],
    categories: {
      '技术': [
        {
          title: 'Introducing GPT-4 Turbo',
          title_zh: 'GPT-4 Turbo 发布',
          link: 'https://openai.com/blog/gpt-4-turbo',
          summary: 'OpenAI announces GPT-4 Turbo with improved performance and lower costs.',
          summary_zh: 'OpenAI 宣布推出 GPT-4 Turbo，性能提升，成本降低。',
          published: new Date().toISOString(),
        },
        {
          title: 'The Future of Web Development',
          title_zh: 'Web 开发的未来',
          link: 'https://example.com/web-future',
          summary: 'Exploring emerging trends in web development for 2026.',
          summary_zh: '探索 2026 年 Web 开发的新兴趋势。',
          published: new Date().toISOString(),
        },
      ],
      'AI/机器学习': [
        {
          title: 'New Advances in Neural Networks',
          title_zh: '神经网络的新进展',
          link: 'https://example.com/neural-nets',
          summary: 'Researchers achieve breakthrough in deep learning efficiency.',
          summary_zh: '研究人员在深度学习效率方面取得突破。',
          published: new Date().toISOString(),
        },
      ],
      '开源项目': [
        {
          title: 'React 19 Beta Release',
          title_zh: 'React 19 Beta 版本发布',
          link: 'https://react.dev/blog/2024/04/25/react-19',
          summary: 'React 19 introduces new features for better performance.',
          summary_zh: 'React 19 引入新特性以提升性能。',
          published: new Date().toISOString(),
        },
      ],
      '科学': [
        {
          title: 'Mars Water Discovery',
          title_zh: '火星水资源发现',
          link: 'https://nasa.gov/mars',
          summary: 'NASA rover finds evidence of underground ice on Mars.',
          summary_zh: 'NASA 探测器在火星发现地下冰层证据。',
          published: new Date().toISOString(),
        },
      ],
    },
    category_summaries: {
      '技术': '今日技术类内容主要聚焦于AI和Web开发领域的最新进展，包括多个重要工具和框架的更新。',
      'AI/机器学习': 'AI领域持续活跃，深度学习和大语言模型都有新的突破。',
      '开源项目': '开源社区发布了多个重要项目的新版本，为开发者带来更好的工具。',
      '科学': '科学研究方面，太空探索和量子计算领域都有重要发现。',
    }
  }
}
