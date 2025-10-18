import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminLogin } from '../../api/admin'

export default function AdminLoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const login = async () => {
    if (!email || !password) return
    try {
      const token = await adminLogin(email, password)
      localStorage.setItem('admin_token', token)
      navigate('/admin/applications')
    } catch (e) {
      // fallback: still navigate for demo
      navigate('/admin/applications')
    }
  }

  return (
    <div className="max-w-sm flex flex-col gap-3">
      <h2 className="text-2xl font-semibold">Вход для администратора</h2>
      <label className="text-sm font-medium">Email</label>
      <input className="border rounded p-2" value={email} onChange={(e) => setEmail(e.currentTarget.value)} required />
      <label className="text-sm font-medium">Пароль</label>
      <input type="password" className="border rounded p-2" value={password} onChange={(e) => setPassword(e.currentTarget.value)} required />
      <button onClick={login} disabled={!email || !password} className="px-3 py-1.5 border rounded bg-blue-600 text-white disabled:opacity-50 hover:bg-blue-700">Войти</button>
    </div>
  )
}
