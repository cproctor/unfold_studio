import DOMPurify from 'dompurify'

export function sanitizeStoryText(html: string): string {
  return DOMPurify.sanitize(html, { ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'br', 'span', 'p'] })
}
