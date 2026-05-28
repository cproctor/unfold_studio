import type { UnfoldConfig } from './types'

// Ambient declarations for globals injected by server-rendered templates

declare namespace inkjs {
  class Story {
    constructor(jsonString: string)
    canContinue: boolean
    currentChoices: Array<{ text: string; index: number }>
    currentTags: string[]
    state: { context: string[] }
    Continue(): string
    ChooseChoiceIndex(index: number): void
    BindExternalFunction(name: string, fn: (...args: unknown[]) => unknown): void
    variablesState: Record<string, unknown>
  }
}

declare interface Window {
  __UNFOLD__: UnfoldConfig
  __UNFOLD_DEBUG__?: Record<string, unknown>
}
