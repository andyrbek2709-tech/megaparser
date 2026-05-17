import { create } from 'zustand'
import type { Post } from '../types'
import { postsApi } from '../api/posts'

interface PostState {
  posts: Post[]
  loading: boolean
  fetchPosts: (params?: { status?: string; account_id?: string }) => Promise<void>
}

export const usePostStore = create<PostState>((set) => ({
  posts: [],
  loading: false,
  fetchPosts: async (params) => {
    set({ loading: true })
    try {
      const res = await postsApi.list(params)
      set({ posts: res.data })
    } finally {
      set({ loading: false })
    }
  },
}))
