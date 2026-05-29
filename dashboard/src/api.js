import { authAxios } from './auth'

const BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000/api'
  : '/api'

export const getMetrics          = () => authAxios.get(`${BASE}/metrics`).then(r => r.data)
export const getLogs             = () => authAxios.get(`${BASE}/logs`).then(r => r.data)
export const getDriftEvents      = () => authAxios.get(`${BASE}/drift-events`).then(r => r.data)
export const getDriftTimeline    = () => authAxios.get(`${BASE}/drift-timeline`).then(r => r.data)
export const getComplianceSummary = () => authAxios.get(`${BASE}/compliance-summary`).then(r => r.data)

export const downloadReport = async (company = '') => {
  const params = company ? `?company=${encodeURIComponent(company)}` : ''
  const response = await axios.get(`${BASE}/report${params}`, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  const date = new Date().toISOString().slice(0, 10)
  const slug = company ? `-${company.replace(/\s+/g, '-').toLowerCase()}` : ''
  link.setAttribute('download', `verispect-compliance-report${slug}-${date}.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}