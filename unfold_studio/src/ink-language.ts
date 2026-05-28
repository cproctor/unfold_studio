import { StreamLanguage, type StreamParser } from '@codemirror/language'

// Ink scripting language mode for CodeMirror 6
// Ported from static/lib/inky/ace-ink-mode/ace-ink.js

const inkParser: StreamParser<{ inComment: boolean }> = {
  startState: () => ({ inComment: false }),

  token(stream, state) {
    if (state.inComment) {
      if (stream.match(/.*\*\//)) {
        state.inComment = false
        return 'comment'
      }
      stream.skipToEnd()
      return 'comment'
    }

    // Block comments
    if (stream.match('/*')) {
      state.inComment = true
      return 'comment'
    }

    // Line comments
    if (stream.match('//')) {
      stream.skipToEnd()
      return 'comment'
    }

    // TODO comments
    if (stream.match(/^\s*TODO\b/)) {
      stream.skipToEnd()
      return 'meta'
    }

    // Knot declarations: === knot_name ===
    if (stream.match(/^={2,}/)) {
      stream.match(/\s*(function\s+)?\w+\s*(?:\([\w,\s->]*\))?\s*=*/i)
      return 'keyword'
    }

    // Stitch declarations: = stitch_name
    if (stream.match(/^=/)) {
      stream.match(/\s*\w+\s*(?:\([\w,\s->]*\))?/)
      return 'def'
    }

    // Choices: * or +
    if (stream.match(/^[\s]*[\*\+]/)) {
      return 'operator'
    }

    // Gather: -
    if (stream.match(/^[\s]*-(?!>)/)) {
      return 'operator'
    }

    // Divert: ->
    if (stream.match('->')) {
      stream.match(/\s*[\w.]+/)
      return 'link'
    }

    // Tags: #
    if (stream.match(/#\w+/)) {
      return 'meta'
    }

    // Variables: VAR, CONST, TEMP
    if (stream.match(/\b(?:VAR|CONST|TEMP)\b/)) {
      return 'keyword'
    }

    // Logic: ~
    if (stream.match(/^~\s*/)) {
      return 'comment'
    }

    // Inline curly braces (conditionals/sequences)
    if (stream.match('{') || stream.match('}')) {
      return 'bracket'
    }

    // Strings
    if (stream.match(/"(?:[^"\\]|\\.)*"/)) {
      return 'string'
    }

    // Numbers
    if (stream.match(/\d+\.?\d*/)) {
      return 'number'
    }

    // Keywords
    if (stream.match(/\b(?:else|elseif|if|not|and|or|true|false|stopping|cycle|shuffle)\b/)) {
      return 'keyword'
    }

    stream.next()
    return null
  },
}

export const inkLanguage = StreamLanguage.define(inkParser)
