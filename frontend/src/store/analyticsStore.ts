import { create } from 'zustand'
import { analyticsApi } from '../api/analytics'

interface AnalyticsState {
  overview: Record<string, unknown> | null
  trend: unknown[]
  loading: boolean
  fetchOverview: () => Promise<void>
  fetchTrend: (days?: number) => Promise<void>
}

export const useAnalyticsStore = create<AnalyticsState>((set) => ({
  overview: null,
  trend: [],
  loading: false,
  fetchOverview: async () => {
    const res = await analyticsApi.overview()
    set({ overview: res.data })
  },
  fetchTrend: async (days = 30) => {
    set({ loading: true })
    try {
      const res = await analyticsApi.engagementTrend({ days })
      set({ trend: res.data })
    } finally {
      set({ loading: false })
    }
  },
}))
