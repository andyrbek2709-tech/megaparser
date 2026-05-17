import client from './client'

export interface GenerationRequest {
  topic: string
  platform: string
  tone: string
  style_hints: string[]
  account_id?: string
}

export interface GeneratedContent {
  text: string
  image_prompt: string
  image_url: string | null
  hashtags: string[]
  estimated_engagement: number
}

export const generationApi = {
  generate: (data: GenerationRequest) => client.post<GeneratedContent>('/generation/generate', data),
  regenerate: (postId: string, opts: { regenerate_text: boolean; regenerate_image: boolean }) =>
    client.post<GeneratedContent>(`/generation/regenerate/${postId}`, opts),
  batch: (data: { account_id: string; topics: string[]; platform: string; tone: string }) =>
    client.post<GeneratedContent[]>('/generation/batch', data),
}
