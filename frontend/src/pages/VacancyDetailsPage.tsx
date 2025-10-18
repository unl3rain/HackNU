import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getVacancy, type Vacancy } from '../api/client'

export default function VacancyDetailsPage() {
  const { id } = useParams()
  const [vacancy, setVacancy] = useState<Vacancy | null>(null)
  useEffect(() => {
    if (id) getVacancy(Number(id)).then(setVacancy)
  }, [id])

  if (!vacancy) return <div>Загрузка…</div>

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 space-y-4">
        <h2 className="text-3xl font-semibold tracking-tight">{vacancy.title}</h2>
        <div className="text-sm text-gray-500">{vacancy.city} • {vacancy.employment_type}</div>
        <div className="flex flex-wrap gap-2">
          {(vacancy.skills || []).map((s) => (
            <span key={s} className="text-xs px-2 py-1 rounded border bg-gray-50 text-gray-700">{s}</span>
          ))}
        </div>
        <div className="space-y-2">
          <div><span className="font-semibold">Experience:</span> {vacancy.min_experience_years}–{vacancy.min_experience_years + 2} years</div>
          {vacancy.salary_max && (
            <div><span className="font-semibold">Salary:</span> ${vacancy.salary_max}</div>
          )}
          <div className="prose max-w-none leading-relaxed">{vacancy.description}</div>
        </div>
        <div>
          <Link to={`/apply/${vacancy.id}`} className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Apply for this job</Link>
        </div>
      </div>
      <aside className="space-y-3">
        <div className="bg-white border rounded-xl p-4 shadow-sm">
          <div className="text-lg font-semibold mb-2">Job summary</div>
          <div className="text-sm text-gray-700 space-y-1">
            <div><span className="text-gray-500">Type:</span> {vacancy.employment_type}</div>
            <div><span className="text-gray-500">Location:</span> {vacancy.city}</div>
            {vacancy.salary_max && (
              <div><span className="text-gray-500">Salary:</span> ${vacancy.salary_max}</div>
            )}
          </div>
          <div className="mt-3">
            <div className="text-sm text-gray-500 mb-1">Tags:</div>
            <div className="flex flex-wrap gap-2">
              {(vacancy.skills || []).map((s) => (
                <span key={s} className="text-xs px-2 py-1 rounded border bg-gray-50 text-gray-700">{s}</span>
              ))}
            </div>
          </div>
        </div>
      </aside>
    </div>
  )
}
