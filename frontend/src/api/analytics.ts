import client from './client'

export const analyticsApi = {
  overview: () => client.get('/analytics/overview'),
  engagementTrend: (params?: { account_id?: string; days?: number }) => client.get('/analytics/engagement-trend', { params }),
  bestTimes: () => client.get('/analytics/best-times'),
  topPosts: (limit?: number) => client.get('/analytics/top-posts', { params: { limit } }),
  contentPerformance: () => client.get('/analytics/content-performance'),
  exportCsv: () => client.post('/analytics/export', {}, { responseType: 'blob' }),
}
