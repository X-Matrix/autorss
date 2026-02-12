import type { FeedItem } from '../types';
import { ExternalLink, Calendar, Users, FileText, Tag } from 'lucide-react';
import { formatPublishedDate } from '../utils/dateFormat';

export default function ItemCard({ item }: { item: FeedItem }) {
  return (
    <article className="bg-white dark:bg-zinc-900/60 border border-zinc-200 dark:border-zinc-800/60 rounded-lg p-5 hover:border-emerald-500/40 hover:shadow-md transition-all group">
      <h3 className="font-bold text-lg text-zinc-900 dark:text-zinc-100 mb-1 group-hover:text-emerald-600 dark:group-hover:text-emerald-400 leading-tight">
        <a href={item.link} target="_blank" rel="noopener noreferrer" className="block">
          {item.title_zh || item.title}
        </a>
      </h3>
      {item.title_zh && item.title !== item.title_zh && (
        <h4 className="text-xs text-zinc-500 dark:text-zinc-500 mb-3 font-mono line-clamp-2 opacity-70 italic">{item.title}</h4>
      )}
      
      {/* 作者信息 */}
      {item.authors && item.authors.length > 0 && (
        <div className="flex items-center gap-1.5 text-xs text-zinc-600 dark:text-zinc-400 mb-3">
          <Users className="w-3.5 h-3.5 shrink-0" />
          <span className="line-clamp-1">
            {item.authors.slice(0, 3).join(', ')}
            {item.authors.length > 3 && ` 等 ${item.authors.length} 位作者`}
          </span>
        </div>
      )}

      {/* arXiv分类标签 */}
      {item.categories && item.categories.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {item.categories.slice(0, 4).map((cat, idx) => (
            <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-xs rounded-full border border-emerald-200 dark:border-emerald-800/40">
              <Tag className="w-2.5 h-2.5" />
              {cat}
            </span>
          ))}
        </div>
      )}
      
      <p className="text-zinc-600 dark:text-zinc-300 leading-relaxed text-sm mb-4 line-clamp-4 group-hover:line-clamp-none transition-all">
        {item.summary_zh || item.summary}
      </p>
      
      <div className="pt-3 border-t border-zinc-200 dark:border-zinc-800/50 flex justify-between items-center mt-auto gap-3">
         <div className="flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-600 font-mono">
           <Calendar className="w-3 h-3" />
           <span>{formatPublishedDate(item.published)}</span>
         </div>
         <div className="flex items-center gap-2">
           {item.pdf_link && (
             <a href={item.pdf_link} target="_blank" rel="noopener noreferrer" 
                className="text-rose-600 dark:text-rose-500 hover:text-rose-500 dark:hover:text-rose-400 inline-flex items-center gap-1 text-xs uppercase tracking-wider font-bold transition-colors">
                <FileText className="w-3 h-3" /> PDF
             </a>
           )}
           <a href={item.link} target="_blank" rel="noopener noreferrer" 
              className="text-emerald-600 dark:text-emerald-500 hover:text-emerald-500 dark:hover:text-emerald-400 inline-flex items-center gap-1 text-xs uppercase tracking-wider font-bold transition-colors">
              arXiv <ExternalLink className="w-3 h-3" />
           </a>
         </div>
      </div>
    </article>
  );
}
