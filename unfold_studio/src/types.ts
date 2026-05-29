export interface StoryContent {
  id: number
  title?: string
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
  shared?: boolean
  debugMode: boolean
  storyJson?: StoryContent
  urls: {
    json: string
    compile?: string
    generate?: string
    getNextDir?: string
    playInstance: string
    playRecord: string
    fork?: string
    share?: string
    unshare?: string
  }
}
