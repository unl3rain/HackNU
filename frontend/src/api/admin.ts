import axios from 'axios'
import { API_BASE } from './client'

export type AdminApplication = {
  id: number
  vacancyTitle: string
  candidate: string
  score: number | null
  mismatches: string[]
}

export type ChatMessage = {
  id: number
  session_id: number
  sender: 'bot' | 'user' | 'system' | string
  content: string
  created_at: string
}

export async function adminLogin(email: string, password: string): Promise<string> {
  const res = await axios.post(`${API_BASE}/admin/login`, { email, password })
  return res.data.access_token as string
}

export async function listAdminApplications(token?: string): Promise<AdminApplication[]> {
  const res = await axios.get(`${API_BASE}/admin/applications`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  return res.data as AdminApplication[]
}

export async function listApplicationMessages(applicationId: number, token?: string): Promise<ChatMessage[]> {
  const res = await axios.get(`${API_BASE}/admin/applications/${applicationId}/messages`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  return res.data as ChatMessage[]
}

export type AdminApplicationDetails = {
  id: number
  vacancyTitle: string | null
  candidate_name: string
  candidate_email: string
  relevance_score: number | null
  mismatches: string[]
  summary_text: string | null
  cv_url: string
  created_at: string
}

export async function getApplicationDetails(applicationId: number, token?: string): Promise<AdminApplicationDetails> {
  const res = await axios.get(`${API_BASE}/admin/applications/${applicationId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
  return res.data as AdminApplicationDetails
}

export async function deleteApplication(applicationId: number, token?: string): Promise<void> {
  await axios.delete(`${API_BASE}/applications/${applicationId}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  })
}
