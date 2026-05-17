import { useEffect, useState } from 'react'
import { format, startOfWeek, addDays } from 'date-fns'
import { usePostStore } from '../store/postStore'
import { PostEditor } from '../components/posts/PostEditor'
import type { Post } from '../types'

export default function ContentCalendar() {
  const { posts, fetchPosts } = usePostStore()
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const weekStart = startOfWeek(new Date())
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i))

  useEffect(() => { fetchPosts() }, [])

  const postsByDay = (day: Date) =>
    posts.filter((p) => p.scheduled_at && format(new Date(p.scheduled_at), 'yyyy-MM-dd') === format(day, 'yyyy-MM-dd'))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Content Calendar</h1>
      <div className="grid grid-cols-7 gap-3">
        {days.map((day) => (
          <div key={day.toISOString()} className="bg-gray-900 border border-gray-800 rounded-xl p-3">
            <div className="text-xs font-medium text-gray-400 mb-2">
              <div>{format(day, 'EEE')}</div>
              <div className="text-lg text-white">{format(day, 'd')}</div>
            </div>
            <div className="space-y-1">
              {postsByDay(day).map((post) => (
                <div
                  key={post.id}
                  onClick={() => setSelectedPost(post)}
                  className="text-xs p-2 rounded-lg bg-indigo-900/50 text-indigo-300 cursor-pointer hover:bg-indigo-900 truncate"
                >
                  {post.content_text?.slice(0, 30) || 'No text'}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {selectedPost && (
        <PostEditor post={selectedPost} onClose={() => setSelectedPost(null)} onSaved={fetchPosts} />
      )}
    </div>
  )
}
