import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import type { DailySummary } from '../types';
import ItemCard from '../components/ItemCard';
import { ArrowLeft, Tag, Info, Headphones } from 'lucide-react';
import { getPodcastUrl } from '../config';

export default function DayView() {
  const { date } = useParams<{ date: string }>();
  const [data, setData] = useState<DailySummary | null>(null);
  const [loading, setLoading] = useState(true);

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
      })
      .catch(err => {
        console.error('Failed to load day', err);
        setLoading(false);
      });
  }, [date]);

  if (loading) {
    return <div className="p-12 text-center text-zinc-500 font-mono">正在加载数据...</div>;
  }

  if (!data) {
    return <div className="p-12 text-center text-zinc-500">未找到今日数据。</div>;
  }

  return (
    <main className="container mx-auto px-4 py-8 max-w-5xl">
      <Link to="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-emerald-600 dark:hover:text-emerald-500 mb-8 font-mono text-sm transition-colors">
        <ArrowLeft className="w-4 h-4" />
        返回首页
      </Link>

      <header className="mb-12 border-b border-zinc-200 dark:border-zinc-800 pb-8">
        <h1 className="text-4xl font-bold text-zinc-900 dark:text-zinc-100 mb-2 font-mono">{data.date}</h1>
        <p className="text-zinc-600 dark:text-zinc-500">
          共处理 <span className="text-emerald-600 dark:text-emerald-500 font-bold">{data.total_items}</span> 条内容，涵盖 <span className="text-emerald-600 dark:text-emerald-500 font-bold">{Object.keys(data.categories).length}</span> 个分类。
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
    </main>
  );
}
