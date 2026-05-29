<template>
  <div class="embed-player">
    <header class="embed-header">
      <a :href="siteUrl" target="_blank" rel="noopener" class="embed-logo">
        <img v-if="logoUrl" :src="logoUrl" alt="Unfold Studio" class="embed-logo-img">
        <span v-else>unfold.studio</span>
      </a>
      <div class="embed-meta">
        <a v-if="storyUrl" :href="storyUrl" target="_blank" rel="noopener" class="embed-title">{{ title }}</a>
        <span v-else class="embed-title">{{ title }}</span>
        <span v-if="author" class="embed-byline">by <a v-if="authorUrl" :href="authorUrl" target="_blank" rel="noopener" class="embed-author">{{ author }}</a><span v-else>{{ author }}</span></span>
      </div>
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
const siteUrl = config.siteUrl ?? window.location.origin
const storyUrl = config.storyUrl ?? null
const logoUrl = config.logoUrl ?? null
const authorUrl = config.authorUrl ?? null
const title = ref('')
const author = ref('')
const playerContainer = ref<HTMLElement | null>(null)

let player: InkPlayer | null = null
let currentStory: StoryContent | null = null

onMounted(async () => {
  if (!playerContainer.value) return
  player = new InkPlayer(playerContainer.value, config)

  const story = config.storyJson ?? await fetchStory()
  currentStory = story
  title.value = story.title ?? ''
  author.value = story.author ?? ''
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
  flex-shrink: 0;
}

.embed-logo:hover {
  opacity: 1;
}

.embed-logo-img {
  height: 20px;
  width: 20px;
  display: block;
}

.embed-meta {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 6px;
  overflow: hidden;
}

.embed-title {
  color: white;
  font-size: 0.9em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-decoration: none;
  flex-shrink: 0;
}

.embed-title:hover {
  text-decoration: underline;
}

.embed-byline {
  color: rgba(255,255,255,0.7);
  font-size: 0.8em;
  white-space: nowrap;
}

.embed-author {
  color: rgba(255,255,255,0.7);
  text-decoration: none;
}

.embed-author:hover {
  color: white;
  text-decoration: underline;
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
