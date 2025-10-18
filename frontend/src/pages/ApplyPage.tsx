import { useState } from 'react'
import { useParams } from 'react-router-dom'
import ChatWidget from '../components/ChatWidget'
import { createApplication } from '../api/client'

export default function ApplyPage() {
  const { id } = useParams()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [wsUrl, setWsUrl] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!file || !id) return
    try {
      setSubmitting(true)
      const res = await createApplication({
        vacancy_id: Number(id),
        candidate_name: name,
        candidate_email: email,
        cv: file,
      })
  setWsUrl(res.ws_url)
  setChatOpen(true)
    } catch (e: any) {
      console.error(e)
      alert(e?.response?.data?.detail || 'Ошибка отправки отклика')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="flex flex-col gap-3 max-w-xl bg-white border rounded-xl p-5 shadow-sm">
        <h2 className="text-2xl font-semibold">Отклик на вакансию #{id}</h2>
        <p className="text-sm text-gray-500">Заполните форму и загрузите PDF-резюме.</p>
        <label className="text-sm font-medium">Имя</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.currentTarget.value)}
          required
          className="border rounded p-2"
        />
        <label className="text-sm font-medium">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.currentTarget.value)}
          required
          className="border rounded p-2"
        />
        <label className="text-sm font-medium">Резюме (PDF)</label>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.currentTarget.files?.[0] || null)}
          required
          className="border rounded p-2"
        />
        <button
          onClick={submit}
          disabled={!file || !name || !email || submitting}
          className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? 'Отправка…' : 'Отправить отклик'}
        </button>
      </div>
      <div>
        <ChatWidget open={chatOpen} onClose={() => setChatOpen(false)} wsPath={wsUrl || undefined} initialStatus="Идёт оценка портфолио…" />
      </div>
    </div>
  )
}
