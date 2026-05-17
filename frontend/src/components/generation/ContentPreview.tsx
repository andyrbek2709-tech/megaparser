import type { GeneratedContent } from '../../api/generation'

export function ContentPreview({ content }: { content: GeneratedContent }) {
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-xl p-5 space-y-4">
      {content.image_url && (
        <img src={content.image_url} alt="Generated" className="w-full rounded-lg max-h-64 object-cover" />
      )}
      <p className="text-sm text-gray-200 whitespace-pre-wrap">{content.text}</p>
      {content.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {content.hashtags.map((h) => (
            <span key={h} className="text-xs text-indigo-400">{h}</span>
          ))}
        </div>
      )}
      <div className="text-xs text-gray-500">
        Estimated engagement: <span className="text-indigo-400">{(content.estimated_engagement * 100).toFixed(2)}%</span>
      </div>
    </div>
  )
}
