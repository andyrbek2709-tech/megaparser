export interface Post {
  id: string
  social_account_id: string | null
  user_id: string | null
  status: 'draft' | 'scheduled' | 'published' | 'failed'
  content_text: string | null
  image_url: string | null
  scheduled_at: string | null
  published_at: string | null
  generation_params: Record<string, unknown>
  created_at: string
  error_message: string | null
}

export interface SocialAccount {
  id: string
  platform: 'instagram' | 'youtube' | 'reddit'
  username: string | null
  account_type: string | null
  is_active: boolean
  token_expires_at: string | null
}

export interface PostMetrics {
  id: string
  post_id: string
  collected_at: string
  likes: number
  comments: number
  shares: number
  saves: number
  reach: number
  impressions: number
  engagement_rate: number
}
