import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getVacancies, type Vacancy, deleteVacancy } from '../api/client'

export default function VacanciesPage() {
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const role = (localStorage.getItem('role') || '').toLowerCase()
  useEffect(() => {
    getVacancies().then(setVacancies)
  }, [])

  const formatSalary = (v: Vacancy) => v.salary_max ? `${v.salary_max.toLocaleString()}${v.currency ? ' ' + v.currency : ''}` : '—'
  return (
    <div className="flex flex-col gap-4">
      {vacancies.map((v) => (
        <div key={v.id} className="bg-white border rounded-xl p-4 hover:shadow-card transition-shadow">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="text-lg font-semibold">{v.title}</div>
                <span className="text-xs text-gray-400">{v.employment_type}</span>
              </div>
              <div className="text-sm text-gray-500">{v.city} • Опыт: {v.min_experience_years}+ лет</div>
              <div className="flex flex-wrap gap-2">
                {(v.skills || []).map((s) => (
                  <span key={s} className="text-xs px-2 py-1 rounded border bg-gray-50 text-gray-700">{s}</span>
                ))}
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              <div className="text-sm text-gray-500">&nbsp;</div>
              <div className="text-lg font-semibold text-gray-900">{formatSalary(v)}</div>
              <div className="flex gap-2">
                <Link to={`/vacancies/${v.id}`} className="px-3 py-1.5 border rounded hover:bg-gray-50">Подробнее</Link>
                <Link to={`/apply/${v.id}`} className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Откликнуться</Link>
                {(role === 'admin' || role === 'employer') && (
                  <button
                    onClick={async () => {
                      if (!confirm('Удалить вакансию?')) return
                      await deleteVacancy(v.id)
                      setVacancies((prev) => prev.filter((x) => x.id !== v.id))
                    }}
                    className="px-3 py-1.5 rounded border text-red-600 hover:bg-red-50"
                  >
                    Удалить
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
