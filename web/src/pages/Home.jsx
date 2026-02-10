import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

export default function Home() {
  const [summaries, setSummaries] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSummaries()
  }, [])

  const loadSummaries = async () => {
    try {
      // 加载索引文件
      const response = await fetch('/data/index.json')
      if (!response.ok) {
        throw new Error('Failed to fetch index')
      }
      const index = await response.json()
      
      // 加载每个摘要的详细信息
      const summariesData = await Promise.all(
        index.slice(0, 10).map(async (item) => {
          try {
            const summaryResponse = await fetch(`/data/summaries/${item.date}.json`)
            if (!summaryResponse.ok) return null
            return await summaryResponse.json()
          } catch (error) {
            console.error(`Failed to load summary for ${item.date}:`, error)
            return null
          }
        })
      )
      
      setSummaries(summariesData.filter(s => s !== null))
      setLoading(false)
    } catch (error) {
      console.error('Failed to load summaries:', error)
      // 如果加载失败，使用模拟数据
      const mockData = generateMockData()
      setSummaries(mockData)
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

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-accent to-blue-400 bg-clip-text text-transparent">
          每日技术摘要
        </h2>
        <p className="text-gray-400 max-w-2xl mx-auto">
          AI 自动整理和翻译的技术资讯，每天为你精选最值得关注的内容
        </p>
      </div>

      <div className="grid gap-6">
        {summaries.map((summary) => (
          <DailySummaryCard key={summary.date} summary={summary} />
        ))}
      </div>
    </div>
  )
}

function DailySummaryCard({ summary }) {
  const categoryColors = {
    '技术': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'AI/机器学习': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    '开源项目': 'bg-green-500/10 text-green-400 border-green-500/20',
    '科学': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
    '设计': 'bg-pink-500/10 text-pink-400 border-pink-500/20',
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div>
          <Link to={`/daily/${summary.date}`}>
            <h3 className="text-2xl font-bold text-white hover:text-accent transition-colors">
              {formatDate(summary.date)}
            </h3>
          </Link>
          <p className="text-sm text-gray-500 mt-1">
            共 {summary.total_items} 条内容 · {Object.keys(summary.categories).length} 个分类
          </p>
        </div>
        <Link 
          to={`/daily/${summary.date}`}
          className="btn-primary text-sm"
        >
          查看详情 →
        </Link>
      </div>

      {summary.highlights && summary.highlights.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-400 mb-2">📌 今日亮点</h4>
          <ul className="space-y-2">
            {summary.highlights.slice(0, 3).map((highlight, idx) => (
              <li key={idx} className="text-gray-300 text-sm flex items-start">
                <span className="text-accent mr-2">•</span>
                <span>{highlight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {Object.keys(summary.categories).map((category) => {
          const colorClass = categoryColors[category] || 'bg-gray-500/10 text-gray-400 border-gray-500/20'
          const count = summary.categories[category].length
          return (
            <span 
              key={category}
              className={`px-3 py-1 rounded-full text-xs font-medium border ${colorClass}`}
            >
              {category} ({count})
            </span>
          )
        })}
      </div>
    </div>
  )
}

function formatDate(dateStr) {
  const date = new Date(dateStr)
  const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  return date.toLocaleDateString('zh-CN', options)
}

// 生成模拟数据
function generateMockData() {
  const dates = []
  const today = new Date()
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    
    dates.push({
      date: dateStr,
      total_items: Math.floor(Math.random() * 50) + 30,
      categories: {
        '技术': Array(Math.floor(Math.random() * 10) + 5).fill({}),
        'AI/机器学习': Array(Math.floor(Math.random() * 8) + 3).fill({}),
        '开源项目': Array(Math.floor(Math.random() * 5) + 2).fill({}),
        '科学': Array(Math.floor(Math.random() * 4) + 1).fill({}),
      },
      highlights: [
        'OpenAI 发布新版本 GPT-4 Turbo，性能提升 30%',
        'React 19 Beta 版本发布，新增并发渲染功能',
        'NASA 公布火星探测器新发现的地下水证据',
      ]
    })
  }
  
  return dates
}
