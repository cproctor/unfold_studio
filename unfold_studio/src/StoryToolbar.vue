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
const props = defineProps<{
  editable: boolean
  shared?: boolean
  showCode?: boolean
}>()

const emit = defineEmits<{
  save: []
  replay: []
  fork: []
  share: []
  unshare: []
  'toggle-code': [visible: boolean]
}>()

function toggleCode(): void {
  emit('toggle-code', !props.showCode)
}
</script>
