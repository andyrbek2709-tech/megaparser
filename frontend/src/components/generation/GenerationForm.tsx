import { useState } from 'react'
import type { GenerationRequest } from '../../api/generation'

interface Props {
  onSubmit: (data: GenerationRequest) => void
  loading: boolean
}

const PLATFORMS = ['instagram', 'youtube', 'reddit']
const TONES = ['professional', 'casual', 'humorous', 'inspirational']

export function GenerationForm({ onSubmit, loading }: Props) {
  const [topic, setTopic] = useState('')
  const [platform, setPlatform] = useState('instagram')
  const [tone, setTone] = useState('casual')
  const [styleInput, setStyleInput] = useState('')
  const [styleHints, setStyleHints] = useState<string[]>([])

  const addHint = () => {
    if (styleInput.trim() && !styleHints.includes(styleInput.trim())) {
      setStyleHints([...styleHints, styleInput.trim()])
      setStyleInput('')
    }
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({ topic, platform, tone, style_hints: styleHints })
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <label className="block text-sm text-gray-400 mb-1">Topic</label>
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. Morning productivity tips"
          required
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Platform</label>
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          >
            {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Tone</label>
          <select
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          >
            {TONES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-400 mb-1">Style hints</label>
        <div className="flex gap-2">
          <input
            value={styleInput}
            onChange={(e) => setStyleInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addHint())}
            placeholder="e.g. minimalist, bright colors"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
          />
          <button type="button" onClick={addHint} className="px-3 py-2 bg-gray-700 rounded-lg text-sm hover:bg-gray-600">Add</button>
        </div>
        <div className="flex flex-wrap gap-2 mt-2">
          {styleHints.map((h) => (
            <span key={h} className="flex items-center gap-1 text-xs bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded-full">
              {h}
              <button type="button" onClick={() => setStyleHints(styleHints.filter((x) => x !== h))}>✕</button>
            </span>
          ))}
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium disabled:opacity-50 transition-colors"
      >
        {loading ? 'Generating...' : '✨ Generate Content'}
      </button>
    </form>
  )
}
