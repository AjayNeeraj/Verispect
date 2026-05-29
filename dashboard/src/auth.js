import axios from 'axios'

const BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : ''

// ── Token storage ─────────────────────────────────────────────────────────────
export const getToken  = ()        => localStorage.getItem('vs_token')
export const setToken  = (token)   => localStorage.setItem('vs_token', token)
export const clearToken = ()       => localStorage.removeItem('vs_token')

export const getUser   = ()        => {
  try { return JSON.parse(localStorage.getItem('vs_user') || 'null') }
  catch { return null }
}
export const setUser   = (user)    => localStorage.setItem('vs_user', JSON.stringify(user))
export const clearUser = ()        => localStorage.removeItem('vs_user')

export const isLoggedIn = ()       => !!getToken()

export const logout = () => {
  clearToken()
  clearUser()
  window.location.href = '/login'
}

// ── Axios instance with auth header ──────────────────────────────────────────
export const authAxios = axios.create({ baseURL: BASE })

authAxios.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

authAxios.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearToken()
      clearUser()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth API calls ────────────────────────────────────────────────────────────
export const register = async (company_name, email, password) => {
  const res = await axios.post(`${BASE}/auth/register`, { company_name, email, password })
  setToken(res.data.token)
  setUser({ company_name: res.data.company_name, email: res.data.email, plan: 'free' })
  return res.data
}

export const login = async (email, password) => {
  const res = await axios.post(`${BASE}/auth/login`, { email, password })
  setToken(res.data.token)
  setUser({ company_name: res.data.company_name, email: res.data.email, plan: res.data.plan })
  return res.data
}

export const getMe = () => authAxios.get('/auth/me').then(r => r.data)

// ── Key management ────────────────────────────────────────────────────────────
export const getKeys    = ()         => authAxios.get('/api/keys').then(r => r.data)
export const createKey  = (name)     => authAxios.post('/api/keys', { name }).then(r => r.data)
export const revokeKey  = (keyId)    => authAxios.delete(`/api/keys/${keyId}`).then(r => r.data)
