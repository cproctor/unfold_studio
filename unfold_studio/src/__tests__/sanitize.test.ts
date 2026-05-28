import { describe, it, expect } from 'vitest'
import { sanitizeStoryText } from '../sanitize'

describe('sanitizeStoryText', () => {
  it('passes through plain text unchanged', () => {
    expect(sanitizeStoryText('Hello, world!')).toBe('Hello, world!')
  })

  it('allows safe tags', () => {
    const input = '<b>bold</b> and <em>emphasis</em>'
    const result = sanitizeStoryText(input)
    expect(result).toContain('<b>bold</b>')
    expect(result).toContain('<em>emphasis</em>')
  })

  it('strips script tags', () => {
    const input = '<script>alert("xss")</script>Hello'
    const result = sanitizeStoryText(input)
    expect(result).not.toContain('<script>')
    expect(result).toContain('Hello')
  })

  it('strips event handlers', () => {
    const input = '<b onclick="alert(1)">click me</b>'
    const result = sanitizeStoryText(input)
    expect(result).not.toContain('onclick')
  })

  it('strips javascript: links', () => {
    const input = '<a href="javascript:alert(1)">click</a>'
    const result = sanitizeStoryText(input)
    expect(result).not.toContain('javascript:')
  })

  it('allows safe anchor tags', () => {
    const input = '<a href="https://example.com">link</a>'
    const result = sanitizeStoryText(input)
    expect(result).toContain('<a')
    expect(result).toContain('href')
  })
})
