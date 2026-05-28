import { InkPlayer } from './player'
import type { StoryContent } from './types'

function mapErrors(story: StoryContent): Array<{ lineNumber: number | null; message: string }> {
  return (story.errors ?? []).map((e) => ({ lineNumber: e.line, message: e.message }))
}

async function init(): Promise<void> {
  const config = window.__UNFOLD__

  if (config.debugMode) {
    window.__UNFOLD_DEBUG__ = { config }
  }

  const player = new InkPlayer('.innerText', config)

  // fetch_story equivalent
  const storyRes = await fetch(config.urls.json)
  const story = (await storyRes.json()) as StoryContent

  // wire up editor if editable
  if (config.editable) {
    const saveBtn = document.getElementById('save_story')
    if (saveBtn) {
      saveBtn.addEventListener('click', async (e) => {
        e.preventDefault()
        // EditorView.getInk() not yet implemented; will be added in Phase 10
      })
    }
  }

  const replayBtn = document.getElementById('replay_story')
  if (replayBtn) {
    replayBtn.addEventListener('click', (e) => {
      e.preventDefault()
      player.stop()
      void player.play(story)
    })
  }

  const showCodeBtn = document.getElementById('show_code')
  if (showCodeBtn) {
    showCodeBtn.addEventListener('click', (e) => {
      e.preventDefault()
      document.querySelector('.twopane.solo')?.classList.remove('solo')
      document.getElementById('show_code_opt')?.style.setProperty('display', 'none')
      document.getElementById('hide_code_opt')?.style.removeProperty('display')
    })
  }

  const hideCodeBtn = document.getElementById('hide_code')
  if (hideCodeBtn) {
    hideCodeBtn.addEventListener('click', (e) => {
      e.preventDefault()
      document.querySelector('.twopane')?.classList.add('solo')
      document.getElementById('show_code_opt')?.style.removeProperty('display')
      document.getElementById('hide_code_opt')?.style.setProperty('display', 'none')
    })
  }

  if (story.status === 'error') {
    document.querySelector('.twopane.solo')?.classList.remove('solo')
    document.getElementById('show_code_opt')?.style.setProperty('display', 'none')
    document.getElementById('hide_code_opt')?.style.removeProperty('display')
  }

  void player.play(story)
}

document.addEventListener('DOMContentLoaded', () => { void init() })
