import axios from 'axios'

export type Vacancy = {
  id: number
  title: string
  city: string
  description: string
  min_experience_years: number
  employment_type: string
  education_level?: string | null
  languages?: string[] | null
  salary_min?: number | null
  salary_max?: number | null
  currency?: string | null
  skills?: string[] | null
}

export type CreateApplicationResponse = {
  application_id: number
  chat_token: string
  ws_url: string 
}

export const API_BASE = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8002/api/v1'

function deriveWsBase(apiBase: string) {
  const u = new URL(apiBase)
  const protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${u.host}`
}

export const WS_BASE = deriveWsBase(API_BASE)

export function buildWsUrl(wsPath: string) {
  return `${WS_BASE}${wsPath}`
}

export async function getVacancies(): Promise<Vacancy[]> {
  const res = await axios.get(`${API_BASE}/vacancies`)
  return res.data as Vacancy[]
}

export async function getVacancy(id: number): Promise<Vacancy> {
  const res = await axios.get(`${API_BASE}/vacancies/${id}`)
  return res.data as Vacancy
}

export async function deleteVacancy(id: number): Promise<void> {
  const token = localStorage.getItem('token') || undefined
  await axios.delete(`${API_BASE}/vacancies/${id}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
}

export async function createApplication(params: {
  vacancy_id: number
  candidate_name: string
  candidate_email: string
  cv: File
}): Promise<CreateApplicationResponse> {
  const fd = new FormData()
  fd.append('vacancy_id', String(params.vacancy_id))
  fd.append('candidate_name', params.candidate_name)
  fd.append('candidate_email', params.candidate_email)
  fd.append('cv', params.cv)

  const res = await axios.post(`${API_BASE}/applications`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data as CreateApplicationResponse
}
