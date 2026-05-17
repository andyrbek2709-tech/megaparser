interface Slot { day: number; hour: number; avg_engagement: number }

const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export function BestTimeHeatmap({ data }: { data: Slot[] }) {
  const map = new Map(data.map((d) => [`${d.day}-${d.hour}`, d.avg_engagement]))
  const max = Math.max(...data.map((d) => d.avg_engagement), 0.01)

  return (
    <div className="overflow-x-auto">
      <div className="grid" style={{ gridTemplateColumns: `40px repeat(24, 1fr)`, gap: '2px' }}>
        <div />
        {Array.from({ length: 24 }, (_, h) => (
          <div key={h} className="text-center text-xs text-gray-500">{h}</div>
        ))}
        {DAYS.map((day, d) => (
          <>
            <div key={`d-${d}`} className="text-xs text-gray-400 flex items-center">{day}</div>
            {Array.from({ length: 24 }, (_, h) => {
              const val = map.get(`${d}-${h}`) || 0
              const opacity = val / max
              return (
                <div
                  key={`${d}-${h}`}
                  className="h-6 rounded-sm"
                  style={{ backgroundColor: `rgba(99, 102, 241, ${opacity})`, minWidth: '20px' }}
                  title={`${day} ${h}:00 — ${(val * 100).toFixed(2)}%`}
                />
              )
            })}
          </>
        ))}
      </div>
    </div>
  )
}
