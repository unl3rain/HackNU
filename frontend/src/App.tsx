import { Link, Outlet, useLocation, useNavigate, NavLink } from 'react-router-dom'
import { useEffect, useState } from 'react'

export default function App() {
  const [open, setOpen] = useState(false)
  const [authed, setAuthed] = useState<boolean>(!!localStorage.getItem('token'))
  const [role, setRole] = useState<string | null>(null)
  const location = useLocation()
  const navigate = useNavigate()

  useEffect(() => {
    const t = localStorage.getItem('token')
    const r = localStorage.getItem('role')
    setAuthed(!!t)
    setRole(r)
  }, [location.key])

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    navigate('/')
  }

  return (
    <div className="min-h-screen">
      <header className="h-16 border-b bg-white/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-6xl mx-auto h-full px-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button className="sm:hidden p-1 rounded hover:bg-gray-100" onClick={() => setOpen(!open)} aria-label="toggle nav">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6"><path fillRule="evenodd" d="M3.75 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5H4.5a.75.75 0 0 1-.75-.75Zm0 6a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5H4.5a.75.75 0 0 1-.75-.75Zm0 6a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5H4.5a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" /></svg>
            </button>
            <h1 className="text-2xl font-semibold tracking-tight">
              <Link to={authed ? ((role || '').toLowerCase() === 'admin' ? '/admin/applications' : '/vacancies') : '/'}>
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-sky-500">SmartBot</span>
              </Link>
            </h1>
          </div>
          <nav className="text-sm flex items-center gap-3">
            {authed ? (
              <>
                <span className="text-gray-600 text-xs">{localStorage.getItem('email') || role || 'user'}</span>
                <Link to="/dashboard" className="px-3 py-1.5 border rounded hover:bg-gray-50">Личный кабинет</Link>
                <button onClick={logout} className="px-3 py-1.5 rounded bg-blue-600 text-white hover:bg-blue-700">Выйти</button>
              </>
            ) : (
              <Link to="/" className="hover:underline">Войти</Link>
            )}
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-6 flex gap-6">
        <aside className={`w-60 shrink-0 ${open ? 'block' : 'hidden'} sm:block`}>
          <div className="bg-white border rounded-xl p-3 shadow-sm">
            <nav className="flex flex-col gap-1 text-sm">
              <NavLink to="/vacancies" className={({isActive}) => `px-2 py-1 rounded hover:bg-gray-50 ${isActive ? 'bg-gray-100 font-medium' : ''}`}>Вакансии</NavLink>
              {(role || '').toLowerCase() !== 'admin' && (role || '').toLowerCase() !== 'employer' ? null : (
                <>
                  <NavLink to="/employer/vacancies/new" className={({isActive}) => `px-2 py-1 rounded hover:bg-gray-50 ${isActive ? 'bg-gray-100 font-medium' : ''}`}>Новая вакансия</NavLink>
                  <NavLink to="/employer/applications" className={({isActive}) => `px-2 py-1 rounded hover:bg-gray-50 ${isActive ? 'bg-gray-100 font-medium' : ''}`}>Отклики на мои</NavLink>
                </>
              )}
            </nav>
          </div>
        </aside>
        <main className="flex-1">
          <div className="bg-white border rounded-xl p-5 shadow-sm">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
