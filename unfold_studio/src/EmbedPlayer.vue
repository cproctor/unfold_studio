<template>
  <div class="embed-player">
    <header class="embed-header">
      <a :href="siteUrl" target="_blank" class="embed-logo">unfold.studio</a>
      <span class="embed-title">{{ title }}</span>
      <button class="embed-replay" @click="handleReplay">Replay</button>
    </header>
    <div class="embed-content">
      <div class="scrollContainer">
        <div ref="playerContainer" class="innerText active"></div>
        <div class="hiddenBuffer">
          <div class="innerText"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { InkPlayer } from './player'
import type { StoryContent, UnfoldConfig } from './types'

const config: UnfoldConfig = window.__UNFOLD__
const siteUrl = window.location.origin
const title = ref('')
const playerContainer = ref<HTMLElement | null>(null)

let player: InkPlayer | null = null
let currentStory: StoryContent | null = null

onMounted(async () => {
  if (!playerContainer.value) return
  player = new InkPlayer(playerContainer.value, config)

  const story = config.storyJson ?? await fetchStory()
  currentStory = story
  void player.play(story)
})

onUnmounted(() => {
  player?.stop()
})

async function fetchStory(): Promise<StoryContent> {
  const res = await fetch(config.urls.json)
  return res.json() as Promise<StoryContent>
}

function handleReplay(): void {
  if (currentStory) {
    player?.stop()
    void player?.play(currentStory)
  }
}
</script>

<style scoped>
.embed-player {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.embed-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  background: #444;
  flex-shrink: 0;
}

.embed-logo {
  color: white;
  text-decoration: none;
  font-size: 0.85em;
  opacity: 0.8;
}

.embed-logo:hover {
  opacity: 1;
}

.embed-title {
  flex: 1;
  color: white;
  font-size: 0.9em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.embed-replay {
  background: none;
  border: 1px solid rgba(255,255,255,0.5);
  color: white;
  padding: 2px 8px;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.8em;
  border-radius: 3px;
}

.embed-replay:hover {
  background: rgba(255,255,255,0.1);
}

.embed-content {
  flex: 1;
  overflow: hidden;
}

.scrollContainer {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
}
</style>
