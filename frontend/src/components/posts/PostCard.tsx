import type { Post } from '../../types'

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-700 text-gray-300',
  scheduled: 'bg-blue-900 text-blue-300',
  published: 'bg-green-900 text-green-300',
  failed: 'bg-red-900 text-red-300',
}

export function PostCard({ post, onClick }: { post: Post; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className="bg-gray-900 border border-gray-800 rounded-xl p-4 cursor-pointer hover:border-indigo-500 transition-colors"
    >
      {post.image_url && (
        <img src={post.image_url} alt="" className="w-full h-40 object-cover rounded-lg mb-3" />
      )}
      <p className="text-sm text-gray-300 line-clamp-3">{post.content_text || 'No content'}</p>
      <div className="flex items-center justify-between mt-3">
        <span className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[post.status] || STATUS_COLORS.draft}`}>
          {post.status}
        </span>
        {post.scheduled_at && (
          <span className="text-xs text-gray-500">
            {new Date(post.scheduled_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  )
}
