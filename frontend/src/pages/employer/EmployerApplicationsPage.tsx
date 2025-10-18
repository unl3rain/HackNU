import { useEffect, useMemo, useState } from 'react'
import { listMyApplications, getMyApplicationDetails, listMyApplicationMessages, type EmployerApp, type EmployerAppDetails, type ChatMessage } from '../../api/employer'

export default function EmployerApplicationsPage() {
  const [apps, setApps] = useState<EmployerApp[]>([])
  const [opened, setOpened] = useState(false)
  const [selectedApp, setSelectedApp] = useState<EmployerApp | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [details, setDetails] = useState<EmployerAppDetails | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('token') || ''
    if (!token) return
    listMyApplications(token).then(setApps).catch(() => setApps([]))
  }, [])

  const openChat = async (app: EmployerApp) => {
    setSelectedApp(app)
    setOpened(true)
    const token = localStorage.getItem('token') || ''
    const msgs = await listMyApplicationMessages(app.id, token)
    setMessages(msgs)
    try {
  const d = await getMyApplicationDetails(app.id, token)
      setDetails(d)
    } catch {
      setDetails(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl font-semibold">Отклики на мои вакансии</h2>

      {apps.map((a) => (
        <div key={a.id} className="border rounded p-4 shadow-sm flex items-start justify-between">
          <div>
            <div className="font-semibold">{a.candidate}</div>
            <div className="text-sm text-gray-500">{a.vacancyTitle}</div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-sm px-2 py-1 rounded border ${
              (a.score ?? 0) >= 80 ? 'bg-green-50 text-green-700 border-green-300' : (a.score ?? 0) >= 60 ? 'bg-yellow-50 text-yellow-700 border-yellow-300' : 'bg-red-50 text-red-700 border-red-300'
            }`}>{a.score ?? 0}%</span>
            <button className="text-blue-600 underline" onClick={() => openChat(a)}>История чата</button>
          </div>
        </div>
      ))}

      {opened && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/30" onClick={() => setOpened(false)} />
          <div className="absolute right-0 top-0 h-full w-full max-w-2xl bg-white shadow-xl p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold">{selectedApp ? `Отклик #${selectedApp.id}` : 'Отклик'}</h3>
              <button onClick={() => setOpened(false)} className="w-8 h-8 rounded hover:bg-gray-100">×</button>
            </div>
            {details && (
              <div className="space-y-1 mb-3">
                <div className="font-semibold">{details.candidate_name} • {details.candidate_email}</div>
                <div className="text-sm text-gray-600">Вакансия: {details.vacancyTitle || '-'}</div>
                <div className="text-sm">Скор: {details.relevance_score ?? 0}%</div>
                {details.cv_url && <a className="text-blue-600 underline" href={details.cv_url} target="_blank">Скачать резюме (PDF)</a>}
                <hr className="my-2" />
              </div>
            )}
            <div className="font-semibold mb-2">История чата</div>
            {messages.length === 0 ? (
              <div className="text-sm text-gray-500">Нет сообщений</div>
            ) : (
              <div className="flex flex-col gap-2">
                {messages.map((m) => (
                  <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className="max-w-[90%]">
                      <div className={`rounded px-2 py-1 ${m.sender === 'user' ? 'bg-blue-50' : 'bg-gray-100'}`}>
                        <div className="text-xs text-gray-500">{new Date(m.created_at).toLocaleString()} • {m.sender}</div>
                        <div className="text-sm">{m.content}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
