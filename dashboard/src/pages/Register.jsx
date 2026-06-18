import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../auth'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm]       = useState({ company_name: '', email: '', password: '' })
  const [newKey, setNewKey]   = useState('')   // shown once after registration
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)

  const handle = (e) => setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    setLoading(true)
    try {
      const data = await register(form.company_name, form.email, form.password)
      setNewKey(data.api_key)
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  // After registration — show the API key before redirecting
  if (newKey) {
    return (
      <div style={styles.page}>
        <div style={{ ...styles.card, maxWidth: '480px' }}>
          <img src="/logo-full.svg" alt="Verispect" height="36" style={{display:'block',margin:'0 auto 8px'}}/>
          <div style={{ ...styles.subtitle, color: '#10b981', fontSize: '16px', fontWeight: '600' }}>
            Account created!
          </div>
          <p style={{ color: '#9ca3af', fontSize: '13px', marginBottom: '16px' }}>
            Your first API key has been generated. <strong style={{ color: '#ef4444' }}>Copy it now</strong> — it will not be shown again.
          </p>
          <div style={styles.keyBox}>
            <code style={{ fontSize: '13px', wordBreak: 'break-all', color: '#7c6eff' }}>{newKey}</code>
          </div>
          <button
            onClick={() => navigator.clipboard.writeText(newKey)}
            style={{ ...styles.btn, background: '#1f2937', marginBottom: '12px' }}
          >
            📋 Copy Key
          </button>
          <button onClick={() => navigate('/dashboard')} style={styles.btn}>
            Go to Dashboard →
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>⚡ Verispect</div>
        <div style={styles.subtitle}>Create your account</div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={submit} style={styles.form}>
          <label style={styles.label}>Company Name</label>
          <input
            name="company_name" type="text" required
            value={form.company_name} onChange={handle}
            style={styles.input} placeholder="Acme Corp"
          />

          <label style={styles.label}>Work Email</label>
          <input
            name="email" type="email" required
            value={form.email} onChange={handle}
            style={styles.input} placeholder="you@company.com"
          />

          <label style={styles.label}>Password</label>
          <input
            name="password" type="password" required
            value={form.password} onChange={handle}
            style={styles.input} placeholder="Min. 8 characters"
          />

          <button type="submit" disabled={loading} style={styles.btn}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div style={styles.footer}>
          Already have an account?{' '}
          <Link to="/login" style={styles.link}>Sign in</Link>
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
    marginTop: '12px', background: 'linear-gradient(135deg, #7c6eff 0%, #a78bfa 100%)',
    color: '#fff', border: 'none', borderRadius: '8px', padding: '12px',
    fontSize: '14px', fontWeight: '600', cursor: 'pointer', width: '100%',
  },
  keyBox: {
    background: '#0f1119', border: '1px solid rgba(124,110,255,0.3)',
    borderRadius: '8px', padding: '14px', marginBottom: '12px', wordBreak: 'break-all',
  },
  footer: { marginTop: '20px', textAlign: 'center', fontSize: '13px', color: '#6b7280' },
  link: { color: '#7c6eff', textDecoration: 'none', fontWeight: '600' },
}
