<template>
  <div class="story-toolbar">
    <span v-if="editable">[<button @click="$emit('save')">Save</button>]</span>
    <span v-if="!editable">[<button @click="$emit('replay')">Replay</button>]</span>
    <span v-if="editable">[<button @click="$emit('fork')">Fork</button>]</span>
    <span v-if="editable && !shared">[<button @click="$emit('share')">Share</button>]</span>
    <span v-if="editable && shared">[<button @click="$emit('unshare')">Unshare</button>]</span>
    <span>[<button @click="toggleCode">{{ showCode ? 'Hide code' : 'Show code' }}</button>]</span>
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

<style scoped>
.story-toolbar {
  display: contents;
}

.story-toolbar button {
  border: none;
  background: none;
  display: inline;
  color: #3498db;
  cursor: pointer;
  padding: 0;
  margin: 0;
  font-family: inherit;
  font-size: inherit;
}

.story-toolbar button:hover {
  text-decoration: underline;
}
</style>
