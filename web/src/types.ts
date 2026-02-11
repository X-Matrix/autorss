export interface FeedItem {
    title: string;
    title_zh: string;
    link: string;
    summary: string;
    summary_zh: string;
    published: string;
}

export interface DailySummary {
    date: string;
    total_items: number;
    categories: Record<string, FeedItem[]>;
    category_summaries: Record<string, string>;
    highlights?: FeedItem[];
    has_podcast?: boolean;
}

export interface DayIndexEntry {
    date: string;
    total_items: number;
    categories: string[];
    highlights_count: number;
    daily_summary: string;
    has_podcast?: boolean;
}
