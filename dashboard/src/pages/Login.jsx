import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../auth'

export default function Login() {
  const navigate = useNavigate()
  const [form, setForm]     = useState({ email: '', password: '' })
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>⚡ Verispect</div>
        <div style={styles.subtitle}>Sign in to your account</div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={submit} style={styles.form}>
          <label style={styles.label}>Email</label>
          <input
            name="email" type="email" required
            value={form.email} onChange={handle}
            style={styles.input} placeholder="you@company.com"
          />

          <label style={styles.label}>Password</label>
          <input
            name="password" type="password" required
            value={form.password} onChange={handle}
            style={styles.input} placeholder="••••••••"
          />

          <button type="submit" disabled={loading} style={styles.btn}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={styles.footer}>
          Don't have an account?{' '}
          <Link to="/register" style={styles.link}>Create one</Link>
        </div>
      </div>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'center',
    justifyContent: 'center', background: '#0f1119',
  },
  card: {
    background: '#1a1d27', border: '1px solid rgba(124,110,255,0.2)',
    borderRadius: '16px', padding: '40px', width: '100%', maxWidth: '400px',
  },
  logo: {
    fontSize: '22px', fontWeight: '700', color: '#7c6eff',
    marginBottom: '6px', textAlign: 'center',
  },
  subtitle: {
    fontSize: '14px', color: '#9ca3af', textAlign: 'center', marginBottom: '28px',
  },
  error: {
    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
    color: '#ef4444', borderRadius: '8px', padding: '10px 14px',
    fontSize: '13px', marginBottom: '16px',
  },
  form: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { fontSize: '12px', fontWeight: '600', color: '#9ca3af', marginTop: '10px' },
  input: {
    background: '#0f1119', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px', padding: '10px 14px', color: '#f9fafb',
    fontSize: '14px', outline: 'none', width: '100%', boxSizing: 'border-box',
  },
  btn: {
    marginTop: '20px', background: 'linear-gradient(135deg, #7c6eff 0%, #a78bfa 100%)',
    color: '#fff', border: 'none', borderRadius: '8px', padding: '12px',
    fontSize: '14px', fontWeight: '600', cursor: 'pointer', width: '100%',
  },
  footer: { marginTop: '20px', textAlign: 'center', fontSize: '13px', color: '#6b7280' },
  link: { color: '#7c6eff', textDecoration: 'none', fontWeight: '600' },
}
