import { useEffect, useState } from 'react'
import client from '../api/client'
import type { SocialAccount } from '../types'

const PLATFORM_ICONS: Record<string, string> = {
  instagram: '📸',
  youtube: '▶️',
  reddit: '🤖',
}

export default function Accounts() {
  const [accounts, setAccounts] = useState<SocialAccount[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client.get<SocialAccount[]>('/accounts').then((r) => {
      setAccounts(r.data)
      setLoading(false)
    })
  }, [])

  const connectInstagram = async () => {
    const res = await client.post<{ auth_url: string }>('/accounts/instagram/connect')
    window.location.href = res.data.auth_url
  }

  const disconnect = async (id: string) => {
    await client.delete(`/accounts/${id}`)
    setAccounts(accounts.filter((a) => a.id !== id))
  }

  const isExpiringSoon = (account: SocialAccount) => {
    if (!account.token_expires_at) return false
    const diff = new Date(account.token_expires_at).getTime() - Date.now()
    return diff < 7 * 24 * 3600 * 1000
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Connected Accounts</h1>
        <button
          onClick={connectInstagram}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium"
        >
          + Connect Instagram
        </button>
      </div>

      {loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : accounts.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-500">
          <div className="text-4xl mb-3">🔗</div>
          <p>No accounts connected yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {accounts.map((account) => (
            <div key={account.id} className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center gap-4">
              <div className="text-3xl">{PLATFORM_ICONS[account.platform] || '🌐'}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{account.username || account.platform}</span>
                  <span className="text-xs px-2 py-0.5 bg-gray-700 rounded-full text-gray-300">{account.account_type}</span>
                  {isExpiringSoon(account) && (
                    <span className="text-xs px-2 py-0.5 bg-yellow-900 text-yellow-300 rounded-full">Token expiring soon</span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-0.5 capitalize">{account.platform}</p>
              </div>
              <button
                onClick={() => disconnect(account.id)}
                className="text-sm text-red-400 hover:text-red-300"
              >
                Disconnect
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
