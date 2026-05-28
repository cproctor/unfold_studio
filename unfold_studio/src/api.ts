import type { UnfoldConfig } from './types'

export class StoryAPI {
  private csrfToken: string
  private urls: UnfoldConfig['urls']

  constructor(config: UnfoldConfig) {
    this.csrfToken = config.csrfToken
    this.urls = config.urls
  }

  private headers(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'X-CSRFToken': this.csrfToken,
    }
  }

  async fetchStory(): Promise<Record<string, unknown>> {
    const res = await fetch(this.urls.json)
    if (!res.ok) throw new Error(`Failed to fetch story: ${res.status}`)
    return res.json()
  }

  async compileStory(ink: string): Promise<Record<string, unknown>> {
    const res = await fetch(this.urls.compile, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ ink }),
    })
    if (!res.ok) throw new Error(`Compile failed: ${res.status}`)
    return res.json()
  }

  async generate(promptText: string, contextArray: string[], aiSeed: number | null): Promise<{ result: string }> {
    const res = await fetch(this.urls.generate, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ prompt: promptText, context_array: contextArray, ai_seed: aiSeed }),
    })
    if (!res.ok) throw new Error(`Generate failed: ${res.status}`)
    return res.json()
  }

  async getNextDirection(userInput: string, storyPlayInstanceUUID: string, targetKnotName: string, aiSeed: number | null): Promise<{ result: { direction: string; content: Record<string, unknown> } }> {
    const res = await fetch(this.urls.getNextDir, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ user_input: userInput, story_play_instance_uuid: storyPlayInstanceUUID, target_knot_name: targetKnotName, ai_seed: aiSeed }),
    })
    if (!res.ok) throw new Error(`GetNextDirection failed: ${res.status}`)
    return res.json()
  }

  async createStoryPlayInstance(storyId: number): Promise<{ story_play_instance_uuid: string }> {
    const res = await fetch(this.urls.playInstance, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ story_id: storyId }),
    })
    if (!res.ok) throw new Error(`CreateStoryPlayInstance failed: ${res.status}`)
    return res.json()
  }

  async createStoryPlayRecord(storyPlayInstanceUUID: string, dataType: string, data: unknown, storyPoint: number): Promise<void> {
    await fetch(this.urls.playRecord, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({ story_play_instance_uuid: storyPlayInstanceUUID, data_type: dataType, data, story_point: storyPoint }),
    })
  }
}
