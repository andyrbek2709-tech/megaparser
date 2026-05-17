import { useState } from 'react'
import { generationApi, type GeneratedContent, type GenerationRequest } from '../api/generation'
import { GenerationForm } from '../components/generation/GenerationForm'
import { ContentPreview } from '../components/generation/ContentPreview'
import { SchedulePicker } from '../components/posts/SchedulePicker'
import { postsApi } from '../api/posts'

export default function Generator() {
  const [loading, setLoading] = useState(false)
  const [content, setContent] = useState<GeneratedContent | null>(null)
  const [scheduleTime, setScheduleTime] = useState('')
  const [lastParams, setLastParams] = useState<GenerationRequest | null>(null)
  const [savedPostId, setSavedPostId] = useState<string | null>(null)

  const generate = async (data: GenerationRequest) => {
    setLoading(true)
    setContent(null)
    setLastParams(data)
    try {
      const res = await generationApi.generate(data)
      setContent(res.data)
    } finally {
      setLoading(false)
    }
  }

  const saveAsDraft = async () => {
    if (!content) return
    const res = await postsApi.create({
      content_text: content.text,
      image_url: content.image_url || undefined,
      generation_params: lastParams as Record<string, unknown>,
    })
    setSavedPostId(res.data.id)
  }

  const schedulePost = async () => {
    if (!content || !scheduleTime) return
    let postId = savedPostId
    if (!postId) {
      const res = await postsApi.create({
        content_text: content.text,
        image_url: content.image_url || undefined,
        generation_params: lastParams as Record<string, unknown>,
      })
      postId = res.data.id
    }
    await postsApi.schedule(postId, new Date(scheduleTime).toISOString())
    alert('Post scheduled!')
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Content Generator</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm font-medium text-gray-400 mb-4">Generation Parameters</h2>
          <GenerationForm onSubmit={generate} loading={loading} />
        </div>
        <div className="space-y-4">
          {content && (
            <>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="text-sm font-medium text-gray-400 mb-4">Preview</h2>
                <ContentPreview content={content} />
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3">
                <SchedulePicker value={scheduleTime} onChange={setScheduleTime} />
                <div className="flex gap-3">
                  <button onClick={saveAsDraft} className="flex-1 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded-lg">Save Draft</button>
                  <button onClick={schedulePost} disabled={!scheduleTime} className="flex-1 py-2 text-sm bg-indigo-600 hover:bg-indigo-700 rounded-lg disabled:opacity-50">Schedule</button>
                </div>
              </div>
            </>
          )}
          {!content && !loading && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-500">
              <div className="text-4xl mb-3">✨</div>
              <p className="text-sm">Fill in the form and generate your first post</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
