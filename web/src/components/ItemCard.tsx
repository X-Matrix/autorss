import type { FeedItem } from '../types';
import { ExternalLink, Calendar } from 'lucide-react';
import { formatPublishedDate } from '../utils/dateFormat';

export default function ItemCard({ item }: { item: FeedItem }) {
  return (
    <article className="bg-zinc-50 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/60 rounded-xl p-5 hover:border-emerald-500/40 hover:bg-zinc-100 dark:hover:bg-zinc-900/60 transition-all group shadow-sm">
      <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-100 mb-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 leading-tight">
        <a href={item.link} target="_blank" rel="noopener noreferrer" className="block">
          {item.title_zh || item.title}
        </a>
      </h3>
      {item.title_zh && item.title !== item.title_zh && (
        <h4 className="text-xs text-zinc-500 dark:text-zinc-500 mb-4 font-mono line-clamp-1 opacity-70">{item.title}</h4>
      )}
      
      <p className="text-zinc-600 dark:text-zinc-300 leading-relaxed text-sm mb-4 line-clamp-4">
        {item.summary_zh || item.summary}
      </p>
      
      <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800/50 flex justify-between items-center mt-auto">
         <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-600 font-mono">
           <Calendar className="w-3 h-3" />
           <span>{formatPublishedDate(item.published)}</span>
         </div>
         <a href={item.link} target="_blank" rel="noopener noreferrer" 
            className="text-emerald-600 dark:text-emerald-500 hover:text-emerald-500 dark:hover:text-emerald-400 inline-flex items-center gap-1 text-xs uppercase tracking-wider font-bold transition-colors">
            Source <ExternalLink className="w-3 h-3" />
         </a>
      </div>
    </article>
  );
}
