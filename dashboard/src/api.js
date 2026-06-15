import axios from 'axios'
import { authAxios } from './auth'

const BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000/api'
  : '/api'

export const getMetrics          = () => authAxios.get(`${BASE}/metrics`).then(r => r.data)
export const getLogs             = () => authAxios.get(`${BASE}/logs`).then(r => r.data)
export const getDriftEvents      = () => authAxios.get(`${BASE}/drift-events`).then(r => r.data)
export const getDriftTimeline    = () => authAxios.get(`${BASE}/drift-timeline`).then(r => r.data)
export const getComplianceSummary = () => authAxios.get(`${BASE}/compliance-summary`).then(r => r.data)

// ── AI Act Risk Classifier (NOT auth-protected) ───────────────────────────────
export const getRiskQuestions = () => axios.get(`${BASE}/risk/questions`).then(r => r.data)
export const classifyRisk     = (answers) => axios.post(`${BASE}/risk/classify`, answers).then(r => r.data)

// ── Helper: turn a blob response into a browser download ──────────────────────
function triggerDownload(data, filename) {
  const url = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

// ── Compliance report (auth-protected → authAxios) ────────────────────────────
export const downloadReport = async (company = '') => {
  const params = company ? `?company=${encodeURIComponent(company)}` : ''
  const response = await authAxios.get(`${BASE}/report${params}`, { responseType: 'blob' })
  const date = new Date().toISOString().slice(0, 10)
  const slug = company ? `-${company.replace(/\s+/g, '-').toLowerCase()}` : ''
  triggerDownload(response.data, `verispect-compliance-report${slug}-${date}.pdf`)
}

// ── DPIA generator (NOT auth-protected → plain axios) ─────────────────────────
export const downloadDpia = async ({ company, system_name, purpose, model }) => {
  const response = await axios.post(
    `${BASE}/docs/dpia`,
    { company, system_name, purpose, model },
    { responseType: 'blob' }
  )
  const date = new Date().toISOString().slice(0, 10)
  const slug = company ? `-${company.replace(/\s+/g, '-').toLowerCase()}` : ''
  triggerDownload(response.data, `verispect-dpia${slug}-${date}.pdf`)
}
