import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-dark">
      <header className="border-b border-gray-800 bg-dark-lighter sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-accent to-accent-dark rounded-lg flex items-center justify-center">
                <span className="text-2xl font-bold">📡</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white font-mono">AutoRSS</h1>
                <p className="text-xs text-gray-400">每日技术摘要</p>
              </div>
            </Link>
            
            <nav className="flex items-center space-x-6">
              <Link to="/" className="text-gray-300 hover:text-accent transition-colors">
                首页
              </Link>
              <a 
                href="https://github.com/yourusername/AutoRss" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-300 hover:text-accent transition-colors"
              >
                GitHub
              </a>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="max-w-6xl mx-auto px-4 py-8">
        {children}
      </main>
      
      <footer className="border-t border-gray-800 mt-16 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>由 AI 驱动的 RSS 订阅摘要服务</p>
          <p className="mt-2">使用 React + TailwindCSS 构建 · 部署于 Cloudflare Pages</p>
        </div>
      </footer>
    </div>
  )
}
