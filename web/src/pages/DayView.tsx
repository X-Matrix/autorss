import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { DailySummary } from '../types';
import ItemCard from '../components/ItemCard';
import { ArrowLeft, Tag, Info, Headphones, List, ChevronLeft, ChevronRight, Share2 } from 'lucide-react';
import { getPodcastUrl } from '../config';

export default function DayView() {
  const { date } = useParams<{ date: string }>();
  const [data, setData] = useState<DailySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<string>('');
  const [isOutlineOpen, setIsOutlineOpen] = useState(true);

  useEffect(() => {
    if (!date) return;
    
    fetch(`/data/summaries/${date}.json`)
      .then(res => {
        if (!res.ok) throw new Error('Not found');
        return res.json();
      })
      .then(data => {
        setData(data);
        setLoading(false);
        // 更新页面标题
        document.title = `${date} - arXiv AI 每日论文精选`;
      })
      .catch(err => {
        console.error('Failed to load day', err);
        setLoading(false);
      });
  }, [date]);

  // 分享功能
  const handleShare = async () => {
    const shareData = {
      title: `arXiv AI Daily - ${date}`,
      text: `查看 ${date} 的 AI 论文精选，共 ${data?.total_items || 0} 篇论文`,
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

  useEffect(() => {
    const handleScroll = () => {
      if (!data) return;
      
      const sections = Object.keys(data.categories);
      const scrollPosition = window.scrollY + 200;

      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const offsetTop = element.offsetTop;
          const offsetBottom = offsetTop + element.offsetHeight;
          
          if (scrollPosition >= offsetTop && scrollPosition < offsetBottom) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // 初始调用
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [data]);

  const scrollToSection = (category: string) => {
    const element = document.getElementById(category);
    if (element) {
      const offset = 100;
      const elementPosition = element.offsetTop - offset;
      window.scrollTo({
        top: elementPosition,
        behavior: 'smooth'
      });
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-zinc-500 font-mono">正在加载数据...</div>;
  }

  if (!data) {
    return <div className="p-12 text-center text-zinc-500">未找到今日数据。</div>;
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-7xl">
      <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-emerald-600 dark:hover:text-emerald-500 mb-8 font-mono text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" />
        返回首页
      </Link>

      <div className="flex gap-8 relative">
        {/* 左侧导航 */}
        <aside className={`hidden lg:block shrink-0 transition-all duration-300 ${isOutlineOpen ? 'w-64' : 'w-0 opacity-0 overflow-hidden'}`}>
          <div className={`sticky top-24 space-y-2 ${isOutlineOpen ? 'block' : 'hidden'}`}>
            <div className="flex items-center justify-between mb-4 px-3 text-zinc-700 dark:text-zinc-300">
              <div className="flex items-center gap-2">
                <List className="w-4 h-4" />
                <h3 className="font-bold text-sm uppercase tracking-wider">研究方向</h3>
              </div>
              <button
                onClick={() => setIsOutlineOpen(false)}
                className="p-1 rounded-md hover:bg-zinc-200 dark:hover:bg-zinc-800 transition-colors group"
                title="收起导航"
              >
                <ChevronLeft className="w-4 h-4 text-zinc-500 dark:text-zinc-400 group-hover:text-zinc-700 dark:group-hover:text-zinc-200" />
              </button>
            </div>
            <nav className="space-y-1">
              {data && Object.entries(data.categories).map(([category, items]) => (
                <button
                  key={category}
                  onClick={() => scrollToSection(category)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${
                    activeSection === category
                      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 font-medium border-l-2 border-emerald-500'
                      : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/50 border-l-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate">{category}</span>
                    <span className="text-xs opacity-60 shrink-0">{items.length}</span>
                  </div>
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* 展开按钮 - 仅在收起时显示 */}
        {!isOutlineOpen && (
          <button
            onClick={() => setIsOutlineOpen(true)}
            className="hidden lg:flex fixed left-4 top-32 z-10 items-center gap-2 px-3 py-2 bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-500 border border-emerald-200 dark:border-emerald-800/50 rounded-lg shadow-sm hover:shadow-md hover:bg-emerald-500/20 dark:hover:bg-emerald-500/30 transition-all group"
            title="展开导航"
          >
            <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            <span className="text-xs font-medium">导航</span>
          </button>
        )}

        {/* 主内容区 */}
        <div className="flex-1 min-w-0">
          <header className="mb-12 border-b border-zinc-200 dark:border-zinc-800 pb-8">
            <div className="flex items-start justify-between gap-4 mb-4">
              <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 font-mono">{data.date}</h1>
              <button
                onClick={handleShare}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-500 border border-emerald-200 dark:border-emerald-800/50 rounded-lg hover:bg-emerald-500/20 dark:hover:bg-emerald-500/30 transition-all group"
                title="分享此页面"
              >
                <Share2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
                <span className="text-sm font-medium">分享</span>
              </button>
            </div>
            <p className="text-zinc-600 dark:text-zinc-500">
              共处理 <span className="text-emerald-600 dark:text-emerald-500 font-bold">{data.total_items}</span> 篇arXiv论文，涵盖 <span className="text-emerald-600 dark:text-emerald-500 font-bold">{Object.keys(data.categories).length}</span> 个研究方向。
            </p>
          </header>

          {data.has_podcast && (
            <section className="mb-12 bg-indigo-50 dark:bg-indigo-900/10 border border-indigo-100 dark:border-indigo-800/30 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Headphones className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                <h2 className="text-xl font-bold text-indigo-900 dark:text-indigo-100">今日播客</h2>
              </div>
              <audio controls className="w-full">
                <source src={getPodcastUrl(data.date)} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            </section>
          )}

          {/* Daily Summary Section intentionally added if needed, but keeping user request minimal for now */}
          
          <div className="space-y-16">
            {Object.entries(data.categories).map(([category, items]) => (
              <section key={category} id={category} className="scroll-mt-24">
                <div className="flex items-center gap-3 mb-6">
                  <Tag className="w-5 h-5 text-emerald-600 dark:text-emerald-500" />
                  <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">{category}</h2>
                </div>

                {data.category_summaries[category] && (
                  <div className="mb-8 bg-zinc-100 dark:bg-zinc-900/40 border-l-2 border-emerald-500/50 p-4 rounded-r-lg">
                    <div className="flex items-start gap-3">
                      <Info className="w-5 h-5 text-emerald-600/80 dark:text-emerald-500/80 mt-0.5 shrink-0" />
                      <p className="text-zinc-600 dark:text-zinc-300 italic text-sm leading-relaxed">
                        {data.category_summaries[category]}
                      </p>
                    </div>
                  </div>
                )}

                <div className="grid gap-6 md:grid-cols-2">
                  {items.map((item, idx) => (
                    <ItemCard key={idx} item={item} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
