import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAnalyticsStore } from '../store/analyticsStore'
import { EngagementChart } from '../components/charts/EngagementChart'
import { PostPerformanceChart } from '../components/charts/PostPerformanceChart'

export default function Dashboard() {
  const navigate = useNavigate()
  const { overview, trend, fetchOverview, fetchTrend } = useAnalyticsStore()

  useEffect(() => {
    fetchOverview()
    fetchTrend(30)
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <button
          onClick={() => navigate('/generate')}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium"
        >
          ✨ Generate Post
        </button>
      </div>

      {overview && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: 'Posts This Week', value: (overview as Record<string, unknown>).total_posts_week as number },
            { label: 'Avg Engagement', value: `${(((overview as Record<string, unknown>).avg_engagement_rate as number) * 100).toFixed(2)}%` },
            { label: 'Predicted Next', value: `${(((overview as Record<string, unknown>).predicted_next_engagement as number) * 100).toFixed(2)}%` },
            { label: 'Status', value: 'Active' },
          ].map((stat) => (
            <div key={stat.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <p className="text-xs text-gray-400">{stat.label}</p>
              <p className="text-2xl font-bold mt-1 text-indigo-400">{stat.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Engagement Trend (30d)</h2>
          <EngagementChart data={trend as Array<{ date: string; avg_engagement_rate: number }>} />
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Posts per Day (30d)</h2>
          <PostPerformanceChart data={trend as Array<{ date: string; post_count: number }>} />
        </div>
      </div>
    </div>
  )
}
