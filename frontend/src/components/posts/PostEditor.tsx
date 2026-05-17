import { useState } from 'react'
import type { Post } from '../../types'
import { postsApi } from '../../api/posts'

interface Props {
  post: Post
  onClose: () => void
  onSaved: () => void
}

export function PostEditor({ post, onClose, onSaved }: Props) {
  const [text, setText] = useState(post.content_text || '')
  const [saving, setSaving] = useState(false)

  const save = async () => {
    setSaving(true)
    try {
      await postsApi.update(post.id, { content_text: text })
      onSaved()
      onClose()
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl">
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <h2 className="text-lg font-semibold">Edit Post</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">✕</button>
        </div>
        <div className="p-6 space-y-4">
          {post.image_url && (
            <img src={post.image_url} alt="" className="w-full h-48 object-cover rounded-lg" />
          )}
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm resize-none focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="flex justify-end gap-3 p-6 border-t border-gray-800">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-400 hover:text-white">Cancel</button>
          <button
            onClick={save}
            disabled={saving}
            className="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
