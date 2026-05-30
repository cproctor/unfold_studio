<template>
  <div class="story-toolbar">
    <template v-if="editable">[<button @click="$emit('save')">Save</button>]</template>
    <template v-if="!editable">[<button @click="$emit('replay')">Replay</button>]</template>
    <template v-if="editable">[<button @click="$emit('fork')">Fork</button>]</template>
    <template v-if="editable && !shared">[<button @click="$emit('share')">Share</button>]</template>
    <template v-if="editable && shared">[<button @click="$emit('unshare')">Unshare</button>]</template>
    [<button @click="toggleCode">{{ showCode ? 'Hide code' : 'Show code' }}</button>]
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
  padding: 4px 0;
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
