import axios from 'axios'
import { API_BASE } from './client'

export type EmployerApp = {
  id: number
  vacancyTitle: string
  candidate: string
  score: number | null
}

export type EmployerAppDetails = {
  id: number
  vacancyTitle: string | null
  candidate_name: string
  candidate_email: string
  relevance_score: number | null
  cv_url: string
  created_at: string
}

export async function listMyApplications(token: string): Promise<EmployerApp[]> {
  const res = await axios.get(`${API_BASE}/employer/applications`, { headers: { Authorization: `Bearer ${token}` } })
  return res.data as EmployerApp[]
}

export async function getMyApplicationDetails(applicationId: number, token: string): Promise<EmployerAppDetails> {
  const res = await axios.get(`${API_BASE}/employer/applications/${applicationId}`, { headers: { Authorization: `Bearer ${token}` } })
  return res.data as EmployerAppDetails
}

export type ChatMessage = { id: number, session_id: number, sender: string, content: string, created_at: string }

export async function listMyApplicationMessages(applicationId: number, token: string): Promise<ChatMessage[]> {
  const res = await axios.get(`${API_BASE}/employer/applications/${applicationId}/messages`, { headers: { Authorization: `Bearer ${token}` } })
  return res.data as ChatMessage[]
}
