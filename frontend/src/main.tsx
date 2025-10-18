import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import EmployerVacancyCreatePage from './pages/employer/EmployerVacancyCreatePage'
import EmployerApplicationsPage from './pages/employer/EmployerApplicationsPage'
function ProtectedRoute({ element }: { element: JSX.Element }) {
  const token = localStorage.getItem('token')
  return token ? element : (<LoginPage />)
}

function RoleRoute({ element, roles }: { element: JSX.Element, roles: string[] }) {
  const token = localStorage.getItem('token')
  const role = (localStorage.getItem('role') || '').toLowerCase()
  return token && roles.map(r => r.toLowerCase()).includes(role) ? element : (<LoginPage />)
}
import VacanciesPage from './pages/VacanciesPage'
import VacancyDetailsPage from './pages/VacancyDetailsPage'
import ApplyPage from './pages/ApplyPage'
import AdminApplicationsPage from './pages/admin/AdminApplicationsPage'
import AdminLoginPage from './pages/admin/AdminLoginPage'

const router = createBrowserRouter([
  { path: '/', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  {
    path: '/',
    element: <App />,
    children: [
      { path: 'dashboard', element: <ProtectedRoute element={<DashboardPage />} /> },
      { path: 'vacancies/:id', element: <ProtectedRoute element={<VacancyDetailsPage />} /> },
      { path: 'apply/:id', element: <ProtectedRoute element={<ApplyPage />} /> },
      { path: 'admin/login', element: <AdminLoginPage /> },
      { path: 'admin/applications', element: <AdminApplicationsPage /> },
      { path: 'vacancies', element: <ProtectedRoute element={<VacanciesPage />} /> },
      { path: 'employer/vacancies/new', element: <RoleRoute roles={['admin','employer']} element={<EmployerVacancyCreatePage />} /> },
  { path: 'employer/applications', element: <RoleRoute roles={['admin','employer']} element={<EmployerApplicationsPage />} /> },
    ],
  },
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
