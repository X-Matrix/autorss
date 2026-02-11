/**
 * 应用配置
 */

// R2 存储桶的公共访问域名
// 需要在 Cloudflare R2 中为 autorss-podcast 存储桶配置自定义域名或使用公共访问 URL
export const R2_PODCAST_BASE_URL = import.meta.env.VITE_R2_PODCAST_URL || 'https://pdcstcdv.1cup.cafe';

// 获取播客文件的完整 URL
export function getPodcastUrl(date: string): string {
    return `${R2_PODCAST_BASE_URL}/${date}_podcast.mp3`;
}
