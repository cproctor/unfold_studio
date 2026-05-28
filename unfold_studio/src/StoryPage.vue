<template>
  <div class="story-page">
    <StoryToolbar
      :editable="config.editable"
      :shared="shared"
      @save="handleSave"
      @replay="handleReplay"
      @fork="handleFork"
      @share="handleShare"
      @unshare="handleUnshare"
      @toggle-code="handleToggleCode"
    />
    <div class="twopane" :class="{ solo: !showCode }">
      <div v-show="showCode && config.editable" id="editor">
        <StoryEditor v-model="inkContent" />
      </div>
      <div v-if="showCode && config.editable" class="split"></div>
      <div id="player">
        <div class="scrollContainer">
          <div ref="playerContainer" class="innerText active"></div>
          <div class="hiddenBuffer">
            <div class="innerText"></div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="errors.length" class="compile-errors">
      <p v-for="err in errors" :key="err.message" class="error">
        <span v-if="err.lineNumber !== null">Line {{ err.lineNumber }}: </span>{{ err.message }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { InkPlayer } from './player'
import { StoryAPI } from './api'
import StoryEditor from './StoryEditor.vue'
import StoryToolbar from './StoryToolbar.vue'
import type { StoryContent, UnfoldConfig } from './types'

const config: UnfoldConfig = window.__UNFOLD__

const inkContent = ref('')
const shared = ref(config.shared ?? false)
const showCode = ref(config.editable)
const errors = ref<Array<{ lineNumber: number | null; message: string }>>([])
const playerContainer = ref<HTMLElement | null>(null)

let player: InkPlayer | null = null
let currentStory: StoryContent | null = null
const api = new StoryAPI(config)

onMounted(async () => {
  if (!playerContainer.value) return
  player = new InkPlayer(playerContainer.value, config)

  const story = config.storyJson ?? await fetchStory()
  currentStory = story
  inkContent.value = story.ink ?? ''
  showCode.value = config.editable && story.status === 'error'
  void player.play(story)
})

onUnmounted(() => {
  player?.stop()
})

async function fetchStory(): Promise<StoryContent> {
  const res = await fetch(config.urls.json)
  return res.json() as Promise<StoryContent>
}

async function handleSave(): Promise<void> {
  errors.value = []
  const result = await api.compileStory(inkContent.value) as StoryContent
  currentStory = result
  errors.value = (result.errors ?? []).map((e) => ({ lineNumber: e.line ?? null, message: e.message }))
  if (result.status === 'ok') {
    player?.stop()
    void player?.play(result)
  }
}

function handleReplay(): void {
  if (currentStory) {
    player?.stop()
    void player?.play(currentStory)
  }
}

async function handleFork(): Promise<void> {
  if (!config.urls.fork) return
  const res = await api.formPost(config.urls.fork)
  window.location.href = res.url
}

async function handleShare(): Promise<void> {
  if (!config.urls.share) return
  await api.formPost(config.urls.share)
  shared.value = true
}

async function handleUnshare(): Promise<void> {
  if (!config.urls.unshare) return
  await api.formPost(config.urls.unshare)
  shared.value = false
}

function handleToggleCode(visible: boolean): void {
  showCode.value = visible
}
</script>

<style scoped>
.story-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.twopane {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.twopane.solo #editor {
  display: none;
}

.twopane.solo .split {
  display: none;
}

#editor {
  flex: 1;
  overflow: hidden;
}

.split {
  width: 4px;
  background: #ccc;
  cursor: col-resize;
}

#player {
  flex: 1;
  overflow: hidden;
}

.compile-errors {
  padding: 8px;
  background: #fff0f0;
  border-top: 1px solid #f99;
}

.compile-errors .error {
  color: #c00;
  margin: 4px 0;
}
</style>
