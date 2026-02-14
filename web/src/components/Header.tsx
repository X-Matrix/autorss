import { Link } from 'react-router-dom';
import { Sun, Moon } from 'lucide-react';
import { useState, useEffect } from 'react';

export function Header() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('theme');
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      if (stored === 'dark' || (!stored && systemDark)) {
        setIsDark(true);
        document.documentElement.classList.add('dark');
      } else {
        setIsDark(false);
        document.documentElement.classList.remove('dark');
      }
    } catch (e) {
      console.error(e);
    }
  }, []);

  const toggleTheme = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setIsDark(false);
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setIsDark(true);
    }
  };

  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white/80 dark:bg-zinc-950/80 backdrop-blur top-0 sticky z-50 transition-colors duration-300">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="p-0.5 rounded-md bg-transparent">
            <img src="/icon.png" alt="Espresso" className="w-8 h-8 rounded-md" />
          </div>
          <span className="font-mono font-bold text-lg text-zinc-900 dark:text-zinc-100 tracking-tighter">
            Espresso
          </span>
        </Link>
        <div className="flex items-center gap-4">
           <button 
             onClick={toggleTheme}
             className="p-2 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400 transition-colors cursor-pointer"
             aria-label="Toggle theme"
           >
             {isDark ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
           </button>
           <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 dark:text-zinc-500">
              <span>v1.0.0</span>
           </div>
        </div>
      </div>
    </header>
  );
}
