<template>
  <div ref="editorContainer" class="story-editor" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState, StateEffect, StateField } from '@codemirror/state'
import { Decoration } from '@codemirror/view'
import type { DecorationSet } from '@codemirror/view'
import { inkLanguage, createInkLinter } from './ink-language'

const setErrorLines = StateEffect.define<number[]>()

const errorLineField = StateField.define<DecorationSet>({
  create() { return Decoration.none },
  update(deco, tr) {
    deco = deco.map(tr.changes)
    for (const e of tr.effects) {
      if (e.is(setErrorLines)) {
        const marks = e.value.flatMap((lineNum) => {
          try {
            const line = tr.state.doc.line(lineNum)
            return [Decoration.line({ class: 'cm-error-line' }).range(line.from)]
          } catch {
            return []
          }
        })
        deco = Decoration.set(marks, true)
      }
    }
    return deco
  },
  provide: (f) => EditorView.decorations.from(f),
})

const props = defineProps<{
  modelValue: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  change: []
}>()

const editorContainer = ref<HTMLElement | null>(null)
let view: EditorView | null = null

onMounted(() => {
  if (!editorContainer.value) return

  view = new EditorView({
    state: EditorState.create({
      doc: props.modelValue,
      extensions: [
        basicSetup,
        EditorView.lineWrapping,
        inkLanguage,
        createInkLinter(),
        errorLineField,
        EditorState.readOnly.of(props.readonly ?? false),
        EditorView.theme({
          '&': { height: '100%' },
          '.cm-scroller': { overflow: 'auto' },
          '.cm-error-line': { backgroundColor: '#fff0f0' },
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            emit('update:modelValue', update.state.doc.toString())
            emit('change')
          }
        }),
      ],
    }),
    parent: editorContainer.value,
  })
})

onUnmounted(() => {
  view?.destroy()
})

watch(() => props.modelValue, (newVal) => {
  if (!view) return
  const current = view.state.doc.toString()
  if (current !== newVal) {
    view.dispatch({
      changes: { from: 0, to: current.length, insert: newVal },
    })
  }
})

function setErrors(errors: Array<{ lineNumber: number | null; message: string }>): void {
  if (!view) return
  const lines = errors.map((e) => e.lineNumber).filter((n): n is number => n !== null)
  view.dispatch({ effects: setErrorLines.of(lines) })
}

defineExpose({ setErrors })
</script>

<style scoped>
.story-editor {
  height: 100%;
  overflow: hidden;
}
</style>
