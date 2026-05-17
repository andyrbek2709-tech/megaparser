interface Props {
  value: string
  onChange: (value: string) => void
}

export function SchedulePicker({ value, onChange }: Props) {
  return (
    <div className="space-y-1">
      <label className="text-xs text-gray-400">Schedule for</label>
      <input
        type="datetime-local"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500"
      />
    </div>
  )
}
