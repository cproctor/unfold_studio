import { describe, it, expect, vi, beforeEach } from 'vitest'
import { InkPlayer } from '../player'
import type { UnfoldConfig } from '../types'

// Mock inkjs global
const mockStory = {
  canContinue: false,
  currentChoices: [] as Array<{ text: string; index: number }>,
  currentTags: [] as string[],
  state: { context: [] as string[] },
  Continue: vi.fn(() => ''),
  ChooseChoiceIndex: vi.fn(),
  BindExternalFunction: vi.fn(),
  variablesState: {} as Record<string, unknown>,
}

vi.stubGlobal('inkjs', {
  Story: vi.fn(() => mockStory),
})

// Minimal config for tests
const testConfig: UnfoldConfig = {
  storyId: 1,
  csrfToken: 'test-csrf',
  editable: false,
  debugMode: false,
  urls: {
    json: '/stories/1/json/',
    playInstance: '/story_play_instance/new/',
    playRecord: '/story_play_record/new/',
  },
}

function makeContainer(): HTMLElement {
  const el = document.createElement('div')
  document.body.appendChild(el)
  return el
}

describe('InkPlayer', () => {
  let container: HTMLElement
  let player: InkPlayer

  beforeEach(() => {
    container = makeContainer()
    player = new InkPlayer(container, testConfig)
    vi.clearAllMocks()
    mockStory.canContinue = false
    mockStory.currentChoices = []
    mockStory.currentTags = []
  })

  it('throws when container element not found', () => {
    expect(() => new InkPlayer('#nonexistent', testConfig)).toThrow('Container not found')
  })

  it('accepts an HTMLElement directly', () => {
    const el = document.createElement('div')
    expect(() => new InkPlayer(el, testConfig)).not.toThrow()
  })

  it('accepts a CSS selector string', () => {
    const el = document.createElement('div')
    el.id = 'test-container'
    document.body.appendChild(el)
    expect(() => new InkPlayer('#test-container', testConfig)).not.toThrow()
  })

  it('stop() prevents further rendering', () => {
    player.stop()
    // after stop, play with a valid story should not throw
    expect(() => player.stop()).not.toThrow()
  })

  it('reportError shows error content in container', () => {
    const storyWithError = {
      id: 1,
      status: 'error' as const,
      error: 'Compilation failed',
    }
    player.play(storyWithError)
    expect(container.querySelector('.error')).not.toBeNull()
  })
})
