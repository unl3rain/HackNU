import { useEffect, useMemo, useState } from 'react'
import { ChatMessage, AdminApplication, listAdminApplications, listApplicationMessages, getApplicationDetails, type AdminApplicationDetails, deleteApplication } from '../../api/admin'

export default function AdminApplicationsPage() {
  const [range, setRange] = useState<[number, number]>([0, 100])
  const [vacancy, setVacancy] = useState<string | null>(null)
  const [apps, setApps] = useState<AdminApplication[]>([])
  const [opened, setOpened] = useState(false)
  const [selectedApp, setSelectedApp] = useState<AdminApplication | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [details, setDetails] = useState<AdminApplicationDetails | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('admin_token') || undefined
    listAdminApplications(token).then(setApps).catch(() => setApps([]))
  }, [])
  const removeApp = async (id: number) => {
    if (!confirm('Удалить отклик?')) return
    const token = localStorage.getItem('admin_token') || undefined
    await deleteApplication(id, token)
    const refreshed = await listAdminApplications(token)
    setApps(refreshed)
  }

  const filtered = useMemo(() => {
    return apps.filter((a) => (a.score ?? 0) >= range[0] && (a.score ?? 0) <= range[1] && (!vacancy || a.vacancyTitle === vacancy))
  }, [apps, range, vacancy])

  const openChat = async (app: AdminApplication) => {
    setSelectedApp(app)
    setOpened(true)
    const token = localStorage.getItem('admin_token') || undefined
    const msgs = await listApplicationMessages(app.id, token)
    setMessages(msgs)
    try {
      const d = await getApplicationDetails(app.id, token)
      setDetails(d)
    } catch {
      setDetails(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-2xl font-semibold">Отклики</h2>
      <div className="flex gap-6 items-end flex-wrap">
        <div>
          <div className="text-sm text-gray-500">Фильтр по релевантности</div>
          <div className="flex items-center gap-2 mt-1">
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={range[0]}
              onChange={(e) => setRange([Number(e.target.value), range[1]])}
            />
            <span className="text-sm">{range[0]}%</span>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={range[1]}
              onChange={(e) => setRange([range[0], Number(e.target.value)])}
            />
            <span className="text-sm">{range[1]}%</span>
          </div>
        </div>
        <div>
          <label className="text-sm text-gray-500">Вакансия</label>
          <select
            className="block border rounded p-2 min-w-[220px]"
            value={vacancy ?? ''}
            onChange={(e) => setVacancy(e.target.value || null)}
          >
            <option value="">Все</option>
            {[...new Set(apps.map(a => a.vacancyTitle))].map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>
      </div>

      {filtered.map((a) => (
        <div key={a.id} className="border rounded p-4 shadow-sm flex items-start justify-between">
          <div>
            <div className="font-semibold">{a.candidate}</div>
            <div className="text-sm text-gray-500">{a.vacancyTitle}</div>
            <div className="flex gap-2 mt-2 flex-wrap">
              {a.mismatches.length === 0 ? (
                <span className="text-xs px-2 py-1 rounded bg-green-50 text-green-700 border border-green-300">Хорошее совпадение</span>
              ) : (
                a.mismatches.map((m, i) => (
                  <span key={i} className="text-xs px-2 py-1 rounded bg-orange-50 text-orange-700 border border-orange-300">{m}</span>
                ))
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-sm px-2 py-1 rounded border ${
              (a.score ?? 0) >= 80 ? 'bg-green-50 text-green-700 border-green-300' : (a.score ?? 0) >= 60 ? 'bg-yellow-50 text-yellow-700 border-yellow-300' : 'bg-red-50 text-red-700 border-red-300'
            }`}>{a.score ?? 0}%</span>
            <button className="text-blue-600 underline" onClick={() => openChat(a)}>История чата</button>
            <button className="text-red-600 underline" onClick={() => removeApp(a.id)}>Удалить</button>
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
                {details.mismatches.length > 0 && <div className="text-sm">Несоответствия: {details.mismatches.join(', ')}</div>}
                {details.cv_url && <a className="text-blue-600 underline" href={details.cv_url} target="_blank">Скачать резюме (PDF)</a>}
                {details.summary_text && (
                  <div className="text-sm">Итоговый вывод: {details.summary_text}</div>
                )}
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
