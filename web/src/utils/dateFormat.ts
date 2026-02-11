/**
 * 格式化发布时间为统一格式: YYYY-MM-DD HH:mm:ss
 */
export function formatPublishedDate(dateStr: string): string {
  if (!dateStr || dateStr === "发布时间未提供" || dateStr === "Unknown Date") {
    return "发布时间未提供";
  }

  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr; // 如果解析失败，返回原始字符串
    }

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateStr; // 出错时返回原始字符串
  }
}
