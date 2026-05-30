import { StoryAPI, AuthRequiredError } from './api'
import { sanitizeStoryText } from './sanitize'
import type { StoryContent, UnfoldConfig } from './types'

function uuid(): string {
  return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, (c) => {
    const num = +c
    return (num ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (num / 4)))).toString(16)
  })
}

export class InkPlayer {
  private container: HTMLElement
  private timeouts: ReturnType<typeof setTimeout>[] = []
  private currentStoryPoint = 0
  private aiSeed: number | null = null
  private generateInProgress = false
  private generatePrompt = ''
  private continueFunctionCalled = false
  private inputFunctionCalled = false
  private pendingInputValue: string | null = null
  private currentTargetKnot = ''
  private inputBoxToInsert: HTMLElement | null = null
  private storyPlayInstanceUUID = ''
  private story: InstanceType<typeof inkjs.Story> | null = null
  private running = false
  private content: StoryContent | null = null
  private api: StoryAPI
  private config: UnfoldConfig

  constructor(container: HTMLElement | string, config: UnfoldConfig) {
    const el = typeof container === 'string'
      ? document.querySelector<HTMLElement>(container)
      : container
    if (!el) throw new Error(`Container not found: ${container}`)
    this.container = el
    this.config = config
    this.api = new StoryAPI(config)
  }

  private bindExternalFunctions(story: InstanceType<typeof inkjs.Story>): void {
    story.BindExternalFunction('random', () => Math.random())
    story.BindExternalFunction('random_integer', (low: unknown, high: unknown) =>
      (low as number) + Math.floor(Math.random() * ((high as number) - (low as number))))
    story.BindExternalFunction('ln', (x: unknown) => Math.log(x as number))
    story.BindExternalFunction('log2', (x: unknown) => Math.log2(x as number))
    story.BindExternalFunction('round', (x: unknown) => Math.round(x as number))
    story.BindExternalFunction('floor', (x: unknown) => Math.floor(x as number))
    story.BindExternalFunction('ceiling', (x: unknown) => Math.ceil(x as number))
    story.BindExternalFunction('SEED_AI', (seed: unknown) => {
      this.aiSeed = seed as number
      return ''
    })
    story.BindExternalFunction('continue_function', (targetKnot: unknown) => {
      const knotObj = targetKnot as { _componentsString: string }
      this.continueFunctionCalled = true
      this.currentTargetKnot = knotObj._componentsString
      this.scheduleInputBoxForContinue()
      return ''
    })
    story.BindExternalFunction('input', (placeholder: unknown = 'Enter text...') => {
      // If we have a pending value (user just submitted), return it so inkjs assigns it.
      if (this.pendingInputValue !== null) {
        const val = this.pendingInputValue
        this.pendingInputValue = null
        return val
      }
      this.inputFunctionCalled = true
      this.scheduleInputBox(placeholder as string)
      return ''
    })
    story.BindExternalFunction('generate', (promptText: unknown) => {
      this.generateInProgress = true
      this.generatePrompt = promptText as string
      return ''
    })
  }

  play(content: StoryContent): void {
    this.prepareToPlay()
    this.content = content
    this.aiSeed = null
    if (content.status !== 'ok' || !content.compiled) {
      this.reportError(content.error ?? 'Unknown error')
      return
    }
    this.story = new inkjs.Story(content.compiled)
    this.bindExternalFunctions(this.story)
    this.running = true
    void this.createStoryPlayInstanceAndContinueStory(content.id)
  }

  private async generateAndInsertInDOM(promptText: string, staggerIdx = 0): Promise<void> {
    const nonce = uuid()
    const loadingSpan = `<span id="${nonce}" data-loaded="false">Loading...</span>`
    this.addContent({ text: loadingSpan, tags: [] }, staggerIdx)

    let data: { result: string }
    try {
      data = await this.api.generate(promptText, [], this.aiSeed)
    } catch (err) {
      const el = document.getElementById(nonce)
      if (el) el.remove()
      if (err instanceof AuthRequiredError) {
        this.reportError('Sign in to use AI features in this story.')
      } else {
        this.reportError(err instanceof Error ? err.message : String(err))
      }
      return
    }

    const el = document.getElementById(nonce)
    if (el) {
      el.innerHTML = sanitizeStoryText(data.result)
    } else {
      console.warn(`InkPlayer: could not find loading span #${nonce} after generate returned`)
    }

    this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), 'AI_GENERATED_TEXT', data.result)
    this.generateInProgress = false
  }

  private static readonly MAX_STEPS = 5000

  async continueStory(): Promise<void> {
    const storyPlayInstanceUUID = this.getStoryPlayInstanceUUID()
    this.renderWillStart()
    if (!this.running || !this.story) return

    this.story.state.context = []
    let steps = 0
    let staggerIdx = 0
    while (this.story.canContinue) {
      if (++steps > InkPlayer.MAX_STEPS) {
        this.reportError('Possible infinite loop: the story ran more than 5000 steps without reaching a choice or end.')
        return
      }
      try {
        const stateBefore = this.story.state.ToJson()
        const text = this.story.Continue()
        const tags = this.story.currentTags.slice()
        const content = { text, tags }
        if (this.inputFunctionCalled) {
          // Roll back so the next continueStory() re-executes input() and gets pendingInputValue.
          this.story.state.LoadJson(stateBefore)
          this.renderScheduledInputBox(staggerIdx)
          this.renderDidEnd()
          return
        }
        if (this.continueFunctionCalled) {
          this.renderScheduledInputBox(staggerIdx)
          this.continueFunctionCalled = false
          this.renderDidEnd()
          return
        }
        if (this.generateInProgress) {
          await this.generateAndInsertInDOM(this.generatePrompt, staggerIdx++)
        }
        if (tags.includes('context')) {
          this.story.state.context.push(text)
        }
        this.addContent(content, staggerIdx++)
        this.createStoryPlayRecord(storyPlayInstanceUUID, 'AUTHORS_TEXT', content)
      } catch (err) {
        this.reportError(err instanceof Error ? err.message : String(err))
        return
      }
    }
    if (!this.running) return

    const choices = this.story.currentChoices.map((c) => c.text)
    this.createStoryPlayRecord(storyPlayInstanceUUID, 'AUTHORS_CHOICE_LIST', choices)
    if (this.story.currentChoices.length > 0) {
      this.story.currentChoices.forEach((choice, i) => this.addChoice(choice, staggerIdx + i))
    }
    this.renderDidEnd()
  }

  stop(): void {
    this.timeouts.forEach(clearTimeout)
    this.running = false
  }

  private createStoryPlayRecord(storyPlayInstanceUUID: string, dataType: string, data: unknown): void {
    if (
      data === null ||
      data === undefined ||
      (typeof data === 'string' && data.trim() === '') ||
      (Array.isArray(data) && data.length === 0)
    ) return
    this.currentStoryPoint += 1
    void this.api.createStoryPlayRecord(storyPlayInstanceUUID, dataType, data, this.currentStoryPoint)
  }

  private async createStoryPlayInstanceAndContinueStory(storyId: number): Promise<void> {
    const response = await this.api.createStoryPlayInstance(storyId)
    this.storyPlayInstanceUUID = response.story_play_instance_uuid
    await this.continueStory()
  }

  private scheduleInputBox(placeholder: string): void {
    const eventHandler = (userInput: string) => {
      this.inputFunctionCalled = false
      this.pendingInputValue = userInput
      this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), 'READERS_ENTERED_TEXT', userInput)
      this.running = true
      void this.continueStory()
    }
    this.inputBoxToInsert = this.createInputForm('AUTHORS_INPUT_BOX', eventHandler, placeholder, false)
  }

  private scheduleInputBoxForContinue(placeholder = 'what would you like to do next?'): void {
    const eventHandler = (userInput: string) => {
      this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), 'READERS_CONTINUE_ENTERED_TEXT', userInput)
      void this.handleUserInputForContinue(userInput)
    }
    this.inputBoxToInsert = this.createInputForm('AUTHORS_CONTINUE_INPUT_BOX', eventHandler, placeholder)
  }

  private createInputForm(formType: string, eventHandler: (input: string) => void, placeholder: string, showInputAfterSubmit = true): HTMLElement {
    const formContainer = document.createElement('div')
    formContainer.classList.add('input-container')

    const formElement = document.createElement('form')
    const inputElement = document.createElement('textarea')
    inputElement.placeholder = placeholder
    inputElement.required = true
    inputElement.rows = 3
    inputElement.style.resize = 'vertical'
    inputElement.addEventListener('input', function () {
      this.style.height = 'auto'
      this.style.height = this.scrollHeight + 'px'
    })
    inputElement.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        formElement.requestSubmit()
      }
    })

    const buttonElement = document.createElement('button')
    buttonElement.type = 'submit'
    buttonElement.innerText = 'Submit'

    formElement.appendChild(inputElement)
    formElement.appendChild(buttonElement)
    formElement.addEventListener('submit', (event) => {
      event.preventDefault()
      const userInput = inputElement.value.trim()
      if (showInputAfterSubmit) {
        const p = document.createElement('p')
        p.classList.add('regular-text', 'story-content', 'show')
        p.textContent = userInput
        formContainer.replaceWith(p)
      } else {
        formContainer.remove()
      }
      eventHandler(userInput)
    })

    this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), formType, { placeholder })
    formContainer.appendChild(formElement)
    return formContainer
  }

  private async handleUserInputForContinue(userInput: string): Promise<void> {
    const targetKnotName = this.currentTargetKnot
    const loadingEl = document.createElement('p')
    loadingEl.classList.add('continue-loading', 'story-content')
    loadingEl.textContent = 'Continuing…'
    this.container.appendChild(loadingEl)
    let response: Awaited<ReturnType<StoryAPI['getNextDirection']>>
    try {
      response = await this.api.getNextDirection(userInput, this.getStoryPlayInstanceUUID(), targetKnotName, this.aiSeed)
    } catch (err) {
      loadingEl.remove()
      if (err instanceof AuthRequiredError) {
        this.reportError('Sign in to use AI features in this story.')
      } else {
        this.reportError(err instanceof Error ? err.message : String(err))
      }
      return
    }
    loadingEl.remove()
    const nextDirectionJson = response.result

    switch (nextDirectionJson.direction) {
      case 'NEEDS_INPUT': {
        const content = (nextDirectionJson.content as { guidance_text: string })
        this.addContent({ text: content.guidance_text, tags: [] })
        this.scheduleInputBoxForContinue()
        this.renderScheduledInputBox()
        break
      }
      case 'DIRECT_CONTINUE':
        await this.continueStory()
        break
      case 'BRIDGE_AND_CONTINUE': {
        const content = (nextDirectionJson.content as { bridge_text: string })
        this.addContent({ text: content.bridge_text, tags: ['bridge'] })
        this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), 'AI_GENERATED_TEXT', content.bridge_text)
        await this.continueStory()
        break
      }
      case 'INVALID_USER_INPUT':
        this.scheduleInputBoxForContinue('Input was not valid... Tell again')
        this.renderScheduledInputBox()
        break
      default:
        console.error('Unexpected direction:', nextDirectionJson)
    }
  }

  private getStoryPlayInstanceUUID(): string {
    return this.storyPlayInstanceUUID
  }

  // DOM event handlers
  private renderScheduledInputBox(staggerIdx = 0): void {
    if (this.inputBoxToInsert) {
      const el = this.inputBoxToInsert
      this.container.appendChild(el)
      this.timeouts.push(setTimeout(() => el.classList.add('show'), 200 * staggerIdx))
      this.inputBoxToInsert = null
    }
  }

  private prepareToPlay(): void {
    this.container.innerHTML = ''
    const scrollContainer = document.querySelector<HTMLElement>('.scrollContainer')
    if (scrollContainer) scrollContainer.scrollTop = 0
  }

  private addContent(content: { text: string; tags: string[] }, i = 0): void {
    if (content.tags.includes('context')) return

    let wrapper: HTMLElement | null = null
    let clear: HTMLElement | null = null

    if (content.tags.includes('text-me')) {
      wrapper = document.createElement('div')
      wrapper.classList.add('sms', 'text-me', 'story-content')
      const p = document.createElement('p')
      p.innerHTML = sanitizeStoryText(content.text)
      wrapper.appendChild(p)
      clear = document.createElement('div')
      clear.classList.add('clear')
      this.container.appendChild(wrapper)
      this.container.appendChild(clear)
      this.timeouts.push(setTimeout(() => wrapper!.classList.add('show'), 200 * i))
    } else if (content.tags.includes('text-them')) {
      wrapper = document.createElement('div')
      wrapper.classList.add('sms', 'text-them', 'story-content')
      const p = document.createElement('p')
      p.innerHTML = sanitizeStoryText(content.text)
      wrapper.appendChild(p)
      clear = document.createElement('div')
      clear.classList.add('clear')
      this.container.appendChild(wrapper)
      this.container.appendChild(clear)
      this.timeouts.push(setTimeout(() => wrapper!.classList.add('show'), 200 * i))
    } else if (content.tags.includes('clear')) {
      const storyText = this.container.querySelectorAll('.story-content')
      storyText.forEach((el) => el.parentNode?.removeChild(el))
    } else {
      const p = document.createElement('p')
      p.classList.add('regular-text', 'story-content')
      p.innerHTML = sanitizeStoryText(content.text)
      this.container.appendChild(p)
      this.timeouts.push(setTimeout(() => p.classList.add('show'), 200 * i))
    }
  }

  private addChoice(choice: { text: string; index: number }, staggerIdx = 0): void {
    const p = document.createElement('p')
    p.classList.add('choice')
    p.innerHTML = `<a href='#'>${sanitizeStoryText(choice.text)}</a>`
    this.container.appendChild(p)
    this.timeouts.push(setTimeout(() => p.classList.add('show'), 200 * staggerIdx))
    const a = p.querySelector('a')
    a?.addEventListener('click', (event) => {
      event.preventDefault()
      this.choose(choice.index)
    })
  }

  private choose(i: number): void {
    if (!this.story) return
    const chosenChoice = this.story.currentChoices[i].text
    this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), 'READERS_CHOSEN_CHOICE', chosenChoice)
    this.story.ChooseChoiceIndex(i)
    void this.continueStory()
  }

  private renderWillStart(): void {
    const existingChoices = this.container.querySelectorAll('p.choice')
    existingChoices.forEach((c) => c.parentNode?.removeChild(c))
  }

  private renderDidEnd(): void {
    const scrollWrapper = document.querySelector<HTMLElement>('.scrollContainer')
    if (!scrollWrapper) return
    const start = scrollWrapper.scrollTop
    const end = scrollWrapper.scrollHeight - scrollWrapper.clientHeight
    const dist = end - start
    const duration = 300 + 300 * dist / 100
    let startTime: number | null = null
    function step(time: number): void {
      if (startTime === null) startTime = time
      const t = (time - startTime) / duration
      const lerp = 3 * t * t - 2 * t * t * t
      scrollWrapper!.scrollTop = start + lerp * dist
      if (t < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }

  private reportError(message: string): void {
    this.stop()
    const p = document.createElement('pre')
    p.classList.add('error')
    p.innerHTML = sanitizeStoryText(message)
    this.container.appendChild(p)
  }
}
