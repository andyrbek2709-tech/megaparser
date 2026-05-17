import client from './client'
import type { Post } from '../types'

export const postsApi = {
  list: (params?: { status?: string; account_id?: string }) => client.get<Post[]>('/posts', { params }),
  create: (data: Partial<Post>) => client.post<Post>('/posts', data),
  get: (id: string) => client.get<Post>(`/posts/${id}`),
  update: (id: string, data: Partial<Post>) => client.put<Post>(`/posts/${id}`, data),
  delete: (id: string) => client.delete(`/posts/${id}`),
  publishNow: (id: string) => client.post<Post>(`/posts/${id}/publish-now`),
  schedule: (id: string, scheduled_at: string) => client.post<Post>(`/posts/${id}/schedule`, { scheduled_at }),
  metrics: (id: string) => client.get(`/posts/${id}/metrics`),
}
