import { useEffect, useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../api/client'
import { Link } from 'react-router-dom'

type MyApp = { id: number; vacancy_id: number; vacancy_title: string; relevance_score?: number | null; status?: string | null; created_at?: string | null }

export default function DashboardPage() {
  const [me, setMe] = useState<{email: string, role: string} | null>(null)
  const [apps, setApps] = useState<MyApp[] | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return
    axios.get(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setMe(res.data))
      .catch(() => setMe(null))
    axios.get(`${API_BASE}/applications/mine`, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => setApps(res.data))
      .catch(() => setApps([]))
  }, [])

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-3xl font-semibold">Главная</h2>
      <div className="text-sm text-gray-500">Поиск вакансий, управление профилем и быстрый доступ к ключевым разделам платформы.</div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <div className="text-lg font-semibold mb-1">Вакансии</div>
          <div className="text-sm text-gray-600 mb-3">Просмотреть все доступные вакансии.</div>
          <Link to="/vacancies" className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Открыть</Link>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <div className="text-lg font-semibold mb-1">Профиль</div>
          <div className="text-sm text-gray-600 mb-3">Загрузите резюме и управляйте данными аккаунта.</div>
          <Link to="/dashboard" className="px-3 py-1.5 rounded border hover:bg-gray-50">Перейти</Link>
        </div>
      </div>

      <div className="text-lg font-semibold">Последние отклики</div>
      {apps === null ? (
        <div className="text-sm text-gray-500">Загрузка откликов…</div>
      ) : apps.length === 0 ? (
        <div className="text-sm text-gray-500">Пока нет откликов. Перейдите в раздел <Link className="text-blue-600 underline" to="/vacancies">вакансий</Link> и подайте свой первый отклик.</div>
      ) : (
        <ul className="divide-y bg-white border rounded-lg">
          {apps.map(a => (
            <li key={a.id} className="p-3 flex items-center justify-between gap-3">
              <div>
                <div className="font-medium">{a.vacancy_title}</div>
                <div className="text-xs text-gray-500">ID отклика: {a.id} • Балл: {a.relevance_score ?? '—'} • Статус: {a.status ?? 'new'}</div>
              </div>
              <Link to={`/vacancies/${a.vacancy_id}`} className="text-blue-600 hover:underline text-sm">К вакансии</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
