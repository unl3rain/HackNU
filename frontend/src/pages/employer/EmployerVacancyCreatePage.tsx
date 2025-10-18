import { useState } from 'react'
import axios from 'axios'
import { API_BASE } from '../../api/client'

export default function EmployerVacancyCreatePage() {
  const [title, setTitle] = useState('')
  const [city, setCity] = useState('')
  const [description, setDescription] = useState('')
  const [minExp, setMinExp] = useState(0)
  const [empType, setEmpType] = useState('full-time')
  const [skills, setSkills] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMessage(null)
    try {
      const token = localStorage.getItem('token')
      const payload = {
        title,
        city,
        description,
        min_experience_years: Number(minExp),
        employment_type: empType,
        education_level: null,
        languages: null,
        salary_min: null,
        salary_max: null,
        currency: null,
        skills: skills.split(',').map(s => s.trim()).filter(Boolean),
      }
      const res = await axios.post(`${API_BASE}/vacancies`, payload, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      })
      setMessage(`Создана вакансия #${res.data.id}`)
      setTitle(''); setCity(''); setDescription(''); setMinExp(0); setEmpType('full-time'); setSkills('')
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || 'Ошибка создания вакансии')
    }
  }

  return (
    <div className="max-w-lg">
      <h2 className="text-2xl font-semibold mb-3">Новая вакансия</h2>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <label className="text-sm">Название</label>
        <input className="border rounded p-2" value={title} onChange={e => setTitle(e.currentTarget.value)} required />
        <label className="text-sm">Город</label>
        <input className="border rounded p-2" value={city} onChange={e => setCity(e.currentTarget.value)} required />
        <label className="text-sm">Описание</label>
        <textarea className="border rounded p-2" value={description} onChange={e => setDescription(e.currentTarget.value)} required />
        <div className="flex gap-3">
          <div>
            <label className="text-sm">Опыт (лет)</label>
            <input type="number" className="border rounded p-2 w-28" value={minExp} onChange={e => setMinExp(Number(e.currentTarget.value))} />
          </div>
          <div>
            <label className="text-sm">Тип занятости</label>
            <select className="border rounded p-2" value={empType} onChange={e => setEmpType(e.currentTarget.value)}>
              <option value="full-time">full-time</option>
              <option value="part-time">part-time</option>
              <option value="contract">contract</option>
            </select>
          </div>
        </div>
        <label className="text-sm">Навыки (через запятую)</label>
        <input className="border rounded p-2" value={skills} onChange={e => setSkills(e.currentTarget.value)} />
        <button type="submit" className="px-3 py-1.5 border rounded bg-blue-600 text-white hover:bg-blue-700">Создать</button>
        {message && <div className="text-sm text-gray-700">{message}</div>}
      </form>
    </div>
  )
}
