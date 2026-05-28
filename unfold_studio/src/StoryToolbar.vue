<template>
  <div class="story-toolbar">
    <button v-if="editable" @click="$emit('save')">Save</button>
    <button v-if="!editable" @click="$emit('replay')">Replay</button>
    <button v-if="editable" @click="$emit('fork')">Fork</button>
    <button v-if="editable && !shared" @click="$emit('share')">Share</button>
    <button v-if="editable && shared" @click="$emit('unshare')">Unshare</button>
    <button @click="toggleCode">{{ showCode ? 'Hide code' : 'Show code' }}</button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  editable: boolean
  shared?: boolean
}>()

const emit = defineEmits<{
  save: []
  replay: []
  fork: []
  share: []
  unshare: []
  'toggle-code': [visible: boolean]
}>()

const showCode = ref(true)

function toggleCode(): void {
  showCode.value = !showCode.value
  emit('toggle-code', showCode.value)
}
</script>
