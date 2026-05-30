import { StreamLanguage, type StreamParser } from '@codemirror/language'
import { linter, type Diagnostic } from '@codemirror/lint'

// Ink scripting language mode for CodeMirror 6.
// Originally ported from the Ace ink mode (Inky editor); expanded with patterns
// from the pixi-vn-ink-vscode TextMate grammar (MIT, DRincs-Productions).

interface InkState {
  inBlockComment: boolean
  braceDepth: number
  afterDivert: boolean  // true immediately after -> or <-, so the knot name gets its own token
}

const inkParser: StreamParser<InkState> = {
  startState: () => ({ inBlockComment: false, braceDepth: 0, afterDivert: false }),

  token(stream, state) {
    // ── Knot reference (immediately after -> or <-) ───────────────────────
    if (state.afterDivert) {
      state.afterDivert = false
      if (stream.match(/(?:END|DONE)\b/)) return 'keyword'
      if (stream.match(/[a-zA-Z_]\w*(?:\.\w+)*/)) return 'variableName'
      // not an identifier — fall through to normal tokenisation
    }

    // ── Block comments ────────────────────────────────────────────────────
    if (state.inBlockComment) {
      if (stream.match(/.*?\*\//)) {
        state.inBlockComment = false
      } else {
        stream.skipToEnd()
      }
      return 'comment'
    }
    if (stream.match('/*')) {
      state.inBlockComment = true
      return 'comment'
    }

    // ── Line comments ─────────────────────────────────────────────────────
    if (stream.match('//')) {
      stream.skipToEnd()
      return 'comment'
    }

    // ── TODO ──────────────────────────────────────────────────────────────
    if (stream.match(/^\s*TODO:/)) {
      stream.skipToEnd()
      return 'meta'
    }

    // ── INCLUDE statements ────────────────────────────────────────────────
    if (stream.match(/^\s*INCLUDE\b/)) {
      stream.skipToEnd()
      return 'keyword'
    }

    // ── Declarations: VAR, CONST, TEMP, LIST ──────────────────────────────
    if (stream.match(/^\s*(?:VAR|CONST|TEMP|LIST)\b/)) {
      return 'keyword'
    }

    // ── Function knot declaration: === function name(...) ═══ ─────────────
    if (stream.match(/^\s*={2,}\s*function\b/)) {
      stream.match(/\s+\w+\s*(?:\([^)]*\))?\s*=*/)
      return 'keyword'
    }

    // ── Knot / stitch declarations: === name === or = name ────────────────
    if (stream.match(/^\s*={2,}/)) {
      stream.match(/\s*\w+\s*(?:\([^)]*\))?\s*=*/)
      return 'def'
    }
    if (stream.match(/^\s*=/)) {
      stream.match(/\s*\w+\s*(?:\([^)]*\))?/)
      return 'def'
    }

    // ── Tags: # anything to end of line ───────────────────────────────────
    if (stream.match(/#/)) {
      stream.skipToEnd()
      return 'meta'
    }

    // ── Tunnel return ->-> ────────────────────────────────────────────────
    if (stream.match('->->')) {
      return 'keyword'
    }

    // ── Divert -> ─────────────────────────────────────────────────────────
    if (stream.match('->')) {
      stream.eatSpace()
      state.afterDivert = true
      return 'operator'
    }

    // ── Thread <- ─────────────────────────────────────────────────────────
    if (stream.match('<-')) {
      stream.eatSpace()
      state.afterDivert = true
      return 'operator'
    }

    // ── Glue <> ───────────────────────────────────────────────────────────
    if (stream.match('<>')) {
      return 'operator'
    }

    // ── Tilde logic: ~ ────────────────────────────────────────────────────
    if (stream.match(/^\s*~/)) {
      stream.skipToEnd()
      return 'attribute'
    }

    // ── Choices: * or + (possibly multiple, possibly with label) ──────────
    if (stream.match(/^\s*[*+](\s*[*+])*/)) {
      stream.match(/\s*\(\w+\)/)
      return 'operator'
    }

    // ── Gathers: - (possibly multiple, possibly with label) ───────────────
    if (stream.match(/^\s*-(?!>)(\s*-(?!>))*/)) {
      stream.match(/\s*\(\w+\)/)
      return 'operator'
    }

    // ── Curly braces (conditionals, sequences, interpolation) ─────────────
    if (stream.match('{')) {
      state.braceDepth++
      return 'bracket'
    }
    if (stream.match('}')) {
      if (state.braceDepth > 0) state.braceDepth--
      return 'bracket'
    }

    // ── Pipe separator inside sequences ───────────────────────────────────
    if (state.braceDepth > 0 && stream.match('|')) {
      return 'bracket'
    }

    // ── Sequence modifiers at start of { block ────────────────────────────
    if (state.braceDepth > 0 && stream.match(/^[&!~]/)) {
      return 'bracket'
    }

    // ── Strings (only inside expressions, not plain prose) ────────────────
    if (state.braceDepth > 0 && stream.match(/"(?:[^"\\]|\\.)*"/)) {
      return 'string'
    }

    // ── Numbers ───────────────────────────────────────────────────────────
    if (stream.match(/\d+\.?\d*/)) {
      return 'number'
    }

    // ── Keywords ──────────────────────────────────────────────────────────
    if (stream.match(/\b(?:END|DONE)\b/)) {
      return 'keyword'
    }
    // Flow-control constructs (only meaningful in code context)
    if (stream.match(/\b(?:continue|agent)\b/)) {
      return 'keyword'
    }
    // Expression keywords (only inside {} where they're syntactically meaningful)
    if (state.braceDepth > 0 && stream.match(/\b(?:else|elseif|if|not|and|or|true|false|stopping|cycle|shuffle|once|loop)\b/)) {
      return 'keyword'
    }

    // ── Built-in functions ────────────────────────────────────────────────
    // Standard Ink built-ins (uppercase)
    if (stream.match(/\b(?:POW|RANDOM|INT|FLOOR|FLOAT|CEILING|CHOICE_COUNT|TURNS|TURNS_SINCE|SEED_RANDOM|READ_COUNT|MOVE_TO_FLOW|START_STORY|SNAP_SHOT|RESTORE_SNAPSHOT|FORGET_SNAPSHOT)\b/)) {
      return 'builtin'
    }
    // Unfold Studio external functions
    if (stream.match(/\b(?:input|generate|continue_function|SEED_AI|ln|log2|random_gaussian|random_integer|random|round|floor|ceiling)\b/)) {
      return 'builtin'
    }

    stream.next()
    return null
  },
}

export const inkLanguage = StreamLanguage.define(inkParser)

// Linter: flags divert targets that don't match any defined knot or stitch.
// Disabled when the story has INCLUDE statements (knots may be defined externally).
export function createInkLinter() {
  return linter((view) => {
    const text = view.state.doc.toString()

    if (/^\s*INCLUDE\b/m.test(text)) return []

    // Collect all defined knot/stitch names (seed with built-ins that look like knot targets)
    const defined = new Set<string>(['END', 'DONE', 'continue', 'agent', 'continue_function'])
    for (const m of text.matchAll(/^\s*={1,}\s*(?:function\s+)?(\w+)/gm)) {
      defined.add(m[1])
    }

    const diagnostics: Diagnostic[] = []
    for (const m of text.matchAll(/->(?!>)\s*([a-zA-Z_]\w*)(?:\.\w+)*/g)) {
      const name = m[1]
      if (defined.has(name)) continue
      const from = m.index! + m[0].indexOf(name)
      diagnostics.push({
        from,
        to: from + name.length,
        severity: 'error',
        message: `Knot "${name}" is not defined`,
      })
    }

    return diagnostics
  })
}
