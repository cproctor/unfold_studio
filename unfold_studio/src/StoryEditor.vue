<template>
  <div ref="editorContainer" class="story-editor"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
import { EditorState } from '@codemirror/state'
import { inkLanguage } from './ink-language'

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
        inkLanguage,
        EditorState.readOnly.of(props.readonly ?? false),
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
  // Error display via CodeMirror linting — to be added in a future iteration
  // For now, errors are shown in the player panel
}

defineExpose({ setErrors })
</script>

<style scoped>
.story-editor {
  height: 100%;
  overflow: auto;
}
</style>
