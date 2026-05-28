export interface StoryContent {
  id: number
  status: 'ok' | 'error'
  compiled?: string
  errors?: Array<{ line: number | null; message: string }>
  error?: string
  ink?: string
}

export interface UnfoldConfig {
  storyId: number
  csrfToken: string
  editable: boolean
  debugMode: boolean
  urls: {
    json: string
    compile: string
    generate: string
    getNextDir: string
    playInstance: string
    playRecord: string
  }
}
