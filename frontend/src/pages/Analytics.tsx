import { useEffect, useState } from 'react'
import { analyticsApi } from '../api/analytics'
import { useAnalyticsStore } from '../store/analyticsStore'
import { EngagementChart } from '../components/charts/EngagementChart'
import { BestTimeHeatmap } from '../components/charts/BestTimeHeatmap'

export default function Analytics() {
  const { trend, fetchTrend } = useAnalyticsStore()
  const [days, setDays] = useState(30)
  const [bestTimes, setBestTimes] = useState([])
  const [topPosts, setTopPosts] = useState([])

  useEffect(() => { fetchTrend(days) }, [days])
  useEffect(() => {
    analyticsApi.bestTimes().then((r) => setBestTimes(r.data))
    analyticsApi.topPosts(10).then((r) => setTopPosts(r.data))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics</h1>
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1 text-sm rounded-lg ${days === d ? 'bg-indigo-600' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-sm font-medium text-gray-400 mb-4">Engagement Trend</h2>
        <EngagementChart data={trend as Array<{ date: string; avg_engagement_rate: number }>} />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-sm font-medium text-gray-400 mb-4">Best Posting Times</h2>
        <BestTimeHeatmap data={bestTimes} />
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-sm font-medium text-gray-400 mb-4">Top Posts</h2>
        <div className="space-y-3">
          {(topPosts as Array<Record<string, unknown>>).map((post) => (
            <div key={post.id as string} className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">
              {post.image_url && <img src={post.image_url as string} alt="" className="w-12 h-12 rounded-lg object-cover" />}
              <p className="flex-1 text-sm text-gray-300 line-clamp-2">{post.content_text as string}</p>
              <span className="text-sm font-medium text-indigo-400">{((post.engagement_rate as number) * 100).toFixed(2)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
