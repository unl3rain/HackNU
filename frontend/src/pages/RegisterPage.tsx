import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { API_BASE } from '../api/client'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
  const res = await axios.post(`${API_BASE}/auth/register`, { email: email.trim().toLowerCase(), password }) as { data: { access_token: string; role: string; email?: string } }
  const token = res.data.access_token
  const role = res.data.role || 'user'
  const emailResp = res.data.email || ''
      localStorage.setItem('token', token)
      localStorage.setItem('role', role)
  if (emailResp) localStorage.setItem('email', emailResp)
      navigate('/dashboard')
    } catch (err: any) {
      if (err?.response?.status === 400) {
        setError('Email уже зарегистрирован')
      } else {
        setError('Ошибка регистрации. Попробуйте позже')
      }
    }
  }

  return (
    <div className="max-w-sm mx-auto p-6 bg-white border rounded-xl shadow-sm">
      <h2 className="text-2xl font-semibold mb-1">Регистрация</h2>
      <p className="text-sm text-gray-500 mb-4">Создайте аккаунт, чтобы откликаться на вакансии.</p>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <label className="text-sm font-medium">Email</label>
        <input className="border rounded p-2" value={email} onChange={(e) => setEmail(e.currentTarget.value)} required />
        <label className="text-sm font-medium">Пароль</label>
        <input type="password" className="border rounded p-2" value={password} onChange={(e) => setPassword(e.currentTarget.value)} required />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <button type="submit" className="px-3 py-2 rounded bg-blue-600 text-white hover:bg-blue-700">Зарегистрироваться</button>
      </form>
    </div>
  )
}
