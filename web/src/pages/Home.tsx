import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { DayIndexEntry } from '../types';
import { FileText, ChevronRight, Hash, AudioLines, Share2 } from 'lucide-react';

export default function Home() {
  const [days, setDays] = useState<DayIndexEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/data/index.json')
      .then(res => res.json())
      .then(data => {
        setDays(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load index', err);
        setLoading(false);
      });
  }, []);

  // 分享功能
  const handleShare = async () => {
    const shareData = {
      title: 'arXiv AI Daily - 每日论文精选',
      text: '由 AI 精心筛选和翻译的 arXiv AI 领域最新研究论文',
      url: window.location.href
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // 降级处理：复制链接到剪贴板
        await navigator.clipboard.writeText(window.location.href);
        alert('链接已复制到剪贴板！');
      }
    } catch (err) {
      console.error('分享失败:', err);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center text-zinc-500 font-mono">
        正在获取知识库...
      </div>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-16 text-center">
        <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-4 tracking-tight">arXiv AI 每日论文精选</h1>
        <p className="text-zinc-600 dark:text-zinc-500 max-w-lg mx-auto font-mono text-sm mb-6">
           由 AI 精心筛选和翻译的 arXiv AI 领域最新研究论文
        </p>
        <button
          onClick={handleShare}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-500 border border-emerald-200 dark:border-emerald-800/50 rounded-lg hover:bg-emerald-500/20 dark:hover:bg-emerald-500/30 transition-all group"
          title="分享网站"
        >
          <Share2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
          <span className="text-sm font-medium">分享网站</span>
        </button>
      </div>

      <div className="relative border-l-2 border-zinc-200 dark:border-zinc-800 ml-4 md:ml-12 space-y-12">
        {days.map((day, index) => (
          <div key={day.date} className="relative pl-8 md:pl-12">
             {/* Timeline Dot */}
            <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full border-4 border-zinc-50 dark:border-zinc-950 ${index === 0 ? 'bg-emerald-500' : 'bg-zinc-300 dark:bg-zinc-700'}`}></div>
            
            <div className="flex flex-col sm:flex-row sm:items-baseline gap-2 mb-2">
              <span className={`font-mono font-bold text-xl ${index === 0 ? 'text-emerald-600 dark:text-emerald-500' : 'text-zinc-900 dark:text-zinc-100'}`}>
                {day.date}
              </span>
              <span className="text-xs text-zinc-500 font-mono">
                {day.total_items} 篇论文
              </span>
              {day.has_podcast && (
                <span className="ml-2 inline-flex items-center gap-1 text-[10px] bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                  <AudioLines className="w-3 h-3" />
                  Podcast
                </span>
              )}
            </div>

            <Link  
              to={`/day/${day.date}`}
              className="block group relative bg-zinc-50 dark:bg-zinc-900/30 border border-zinc-200 dark:border-zinc-800 rounded-xl p-6 hover:shadow-lg dark:hover:bg-zinc-900/50 hover:border-emerald-500/30 dark:hover:border-emerald-500/30 transition-all duration-300"
            >
              
              <div className="flex flex-wrap gap-2 mb-4">
                {day.categories.slice(0, 5).map(cat => (
                  <span key={cat} className="inline-flex items-center gap-1 text-[10px] uppercase font-bold px-2 py-1 rounded bg-zinc-200/50 dark:bg-zinc-800/50 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-700/50">
                    <Hash className="w-3 h-3 opacity-50" />
                    {cat}
                  </span>
                ))}
                {day.categories.length > 5 && (
                  <span className="text-[10px] text-zinc-400 px-1 py-1">+{day.categories.length - 5} 更多</span>
                )}
              </div>

              {day.daily_summary ? (
                <p className="text-sm text-zinc-600 dark:text-zinc-400 mb-6 leading-relaxed font-sans">
                  {day.daily_summary}
                </p>
              ) : (
                <p className="text-sm text-zinc-400/50 italic mb-6">暂无摘要</p>
              )}
              
              <div className="flex items-center justify-between mt-auto pt-4 border-t border-zinc-100 dark:border-zinc-800/50">
                 <div className="flex items-center gap-2 text-xs text-zinc-500 font-mono group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">
                    <FileText className="w-3 h-3" />
                    <span>阅读详情</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-300 dark:text-zinc-600 group-hover:translate-x-1 group-hover:text-emerald-500 transition-all" />
              </div>
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}
