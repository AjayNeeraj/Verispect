import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getRiskQuestions, classifyRisk } from '../api'
import { getUser, logout } from '../auth'

// Risk-level → visual treatment
const RISK_CONFIG = {
  'HIGH-RISK':    { color: '#ef4444', bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.35)',  icon: '⛔' },
  'PROHIBITED':   { color: '#ef4444', bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.35)',  icon: '🚫' },
  'LIMITED-RISK': { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.35)', icon: '⚠️' },
  'MINIMAL-RISK': { color: '#10b981', bg: 'rgba(16,185,129,0.12)', border: 'rgba(16,185,129,0.35)', icon: '✓' },
}

function NavHeader() {
  return (
    <div className="app-header">
      <Link to="/dashboard" className="app-header-logo" style={{ textDecoration: 'none' }}>
        <span>⚡</span> Verispect
      </Link>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link to="/dashboard" style={navLinkStyle}>Dashboard</Link>
        <Link to="/risk" style={{ ...navLinkStyle, ...navLinkActive }}>Risk Classifier</Link>
        <Link to="/audit" style={navLinkStyle}>Audit Pack</Link>
        <Link to="/account" style={navLinkStyle}>⚙ Account</Link>
        <button onClick={logout} style={signOutStyle}>Sign Out</button>
      </div>
    </div>
  )
}

export default function RiskClassifier() {
  const user = getUser() || {}
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers]     = useState({})
  const [result, setResult]       = useState(null)
  const [loading, setLoading]     = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError]         = useState('')

  useEffect(() => {
    getRiskQuestions()
      .then(qs => {
        setQuestions(qs)
        // default every question to "No" so the answers object is complete
        setAnswers(Object.fromEntries(qs.map(q => [q.key, false])))
      })
      .catch(() => setError('Could not load the questionnaire. Is the API running?'))
      .finally(() => setLoading(false))
  }, [])

  const setAnswer = (key, value) => setAnswers(a => ({ ...a, [key]: value }))

  const handleClassify = async () => {
    setSubmitting(true)
    setError('')
    try {
      setResult(await classifyRisk(answers))
      // surface the result
      setTimeout(() => document.getElementById('risk-result')?.scrollIntoView({ behavior: 'smooth' }), 60)
    } catch {
      setError('Classification failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleReset = () => {
    setAnswers(Object.fromEntries(questions.map(q => [q.key, false])))
    setResult(null)
    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const cfg = result ? (RISK_CONFIG[result.risk_level] || RISK_CONFIG['MINIMAL-RISK']) : null
  const answeredYes = Object.values(answers).filter(Boolean).length

  return (
    <div className="app">
      <NavHeader />
      <div className="app-container" style={{ maxWidth: '1100px' }}>
        {/* Intro */}
        <div className="card card-highlighted" style={{ marginBottom: '32px', padding: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '10px' }}>AI Act Risk Classifier</h1>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.6', maxWidth: '760px' }}>
            Answer a few questions about your AI system. Verispect maps your answers to the EU AI Act
            (Regulation 2024/1689), determines your risk tier, identifies the matched Annex III
            categories, and lists the obligations that apply — and how we cover them.
          </p>
        </div>

        {error && <div style={errorBox}>{error}</div>}

        {loading ? (
          <div className="loading"><div className="spinner" /> Loading questionnaire…</div>
        ) : (
          <div className="card" style={{ marginBottom: '32px' }}>
            <div className="section-title">
              <div className="section-icon">📝</div>
              Questionnaire
              <span style={{ marginLeft: 'auto', fontSize: '13px', color: 'var(--text-muted)', fontWeight: 500, textTransform: 'none', letterSpacing: 0 }}>
                {answeredYes} marked “Yes”
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {questions.map((q, i) => (
                <div key={q.key} style={questionRow}>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flex: 1 }}>
                    <span style={questionNum}>{i + 1}</span>
                    <span style={{ fontSize: '14px', lineHeight: '1.4' }}>{q.question}</span>
                  </div>
                  <YesNoToggle value={answers[q.key]} onChange={v => setAnswer(q.key, v)} />
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button onClick={handleClassify} disabled={submitting} style={primaryBtn}>
                {submitting ? 'Classifying…' : 'Classify My System'}
              </button>
              {(result || answeredYes > 0) && (
                <button onClick={handleReset} style={ghostBtn}>Reset</button>
              )}
            </div>
          </div>
        )}

        {/* Result */}
        {result && cfg && (
          <div id="risk-result" style={{ marginBottom: '40px' }}>
            {/* Big risk badge */}
            <div
              className="card"
              style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, marginBottom: '24px', padding: '28px' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
                <div style={{ ...riskBadge, color: cfg.color, borderColor: cfg.border, background: 'rgba(0,0,0,0.18)' }}>
                  <span style={{ fontSize: '28px' }}>{cfg.icon}</span>
                  <span>{result.risk_level}</span>
                </div>
                <p style={{ flex: 1, minWidth: '260px', fontSize: '15px', lineHeight: '1.6', color: 'var(--text)' }}>
                  {result.headline}
                </p>
              </div>
            </div>

            {/* Prohibited flags (Art. 5) */}
            {result.prohibited?.length > 0 && (
              <div className="card" style={{ marginBottom: '24px', border: '1px solid rgba(239,68,68,0.35)' }}>
                <div className="section-title"><div className="section-icon">🚫</div>Prohibited-Practice Flags (Art. 5)</div>
                <ul style={{ paddingLeft: '20px', color: '#fca5a5', lineHeight: '1.8', fontSize: '14px' }}>
                  {result.prohibited.map((p, i) => <li key={i}>{p}</li>)}
                </ul>
              </div>
            )}

            {/* Matched Annex III categories */}
            <div className="card" style={{ marginBottom: '24px' }}>
              <div className="section-title"><div className="section-icon">🎯</div>Matched Annex III Categories</div>
              {result.categories?.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {result.categories.map((c, i) => (
                    <div key={i} style={categoryCard}>
                      <div style={{ fontWeight: '600', color: 'var(--primary)', marginBottom: '4px', fontSize: '14px' }}>{c.category}</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5' }}>{c.description}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{ padding: '32px 20px' }}>
                  <div className="empty-icon">✓</div>
                  <div className="empty-text">No high-risk Annex III category matched</div>
                  <div className="empty-subtext">Your system falls outside the listed high-risk domains.</div>
                </div>
              )}
            </div>

            {/* Obligations table */}
            {result.obligations?.length > 0 && (
              <div className="card">
                <div className="section-title"><div className="section-icon">📋</div>Obligations That Apply</div>
                <div className="table-container">
                  <table className="table">
                    <thead>
                      <tr>
                        <th style={{ width: '90px' }}>Article</th>
                        <th>Requirement</th>
                        <th>Verispect Coverage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.obligations.map((o, i) => (
                        <tr key={i}>
                          <td><span className="badge">{o.article}</span></td>
                          <td style={{ fontWeight: '500' }}>{o.requirement}</td>
                          <td style={{ color: 'var(--text-muted)' }}>{o.verispect}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '16px', lineHeight: '1.5' }}>
                  This is decision-support, not legal advice or certification. The operator remains responsible
                  for conformity. Generate the full record and DPIA from the{' '}
                  <Link to="/audit" style={{ color: 'var(--primary)' }}>Audit Pack</Link>.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

/* ===== Yes / No segmented toggle ===== */
function YesNoToggle({ value, onChange }) {
  return (
    <div style={toggleWrap}>
      <button
        onClick={() => onChange(true)}
        style={{
          ...toggleBtn,
          ...(value === true ? { background: 'var(--primary)', color: '#fff' } : {}),
        }}
      >
        Yes
      </button>
      <button
        onClick={() => onChange(false)}
        style={{
          ...toggleBtn,
          ...(value === false ? { background: 'rgba(255,255,255,0.12)', color: 'var(--text)' } : {}),
        }}
      >
        No
      </button>
    </div>
  )
}

// ── inline styles (kept local; theme tokens via CSS vars) ─────────────────────
const navLinkStyle = {
  color: 'var(--text-muted)', textDecoration: 'none', fontSize: '13px', fontWeight: 600,
  padding: '7px 12px', borderRadius: '8px',
}
const navLinkActive = {
  color: '#a78bfa', background: 'rgba(124,110,255,0.15)', border: '1px solid rgba(124,110,255,0.3)',
}
const signOutStyle = {
  background: 'transparent', border: '1px solid rgba(255,255,255,0.1)', color: '#6b7280',
  borderRadius: '8px', padding: '7px 14px', fontSize: '13px', cursor: 'pointer',
  textTransform: 'none', letterSpacing: 0, fontWeight: 600,
}
const questionRow = {
  display: 'flex', alignItems: 'center', gap: '16px', justifyContent: 'space-between',
  padding: '14px 16px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)',
  border: '1px solid var(--border)',
}
const questionNum = {
  flexShrink: 0, width: '24px', height: '24px', borderRadius: '6px',
  background: 'rgba(124,110,255,0.15)', color: 'var(--primary)', fontSize: '12px', fontWeight: 700,
  display: 'flex', alignItems: 'center', justifyContent: 'center',
}
const toggleWrap = {
  display: 'inline-flex', flexShrink: 0, background: 'rgba(0,0,0,0.25)',
  borderRadius: '8px', padding: '3px', border: '1px solid var(--border)',
}
const toggleBtn = {
  border: 'none', background: 'transparent', color: 'var(--text-muted)',
  padding: '6px 18px', fontSize: '13px', fontWeight: 600, cursor: 'pointer',
  borderRadius: '6px', textTransform: 'none', letterSpacing: 0, transition: 'all 0.15s ease',
}
const primaryBtn = {
  background: 'linear-gradient(135deg, #7c6eff 0%, #a78bfa 100%)', color: '#fff', border: 'none',
  borderRadius: '8px', padding: '12px 28px', fontSize: '14px', fontWeight: 600, cursor: 'pointer',
  textTransform: 'none', letterSpacing: 0,
}
const ghostBtn = {
  background: 'transparent', border: '1px solid rgba(255,255,255,0.12)', color: 'var(--text-muted)',
  borderRadius: '8px', padding: '12px 24px', fontSize: '14px', fontWeight: 600, cursor: 'pointer',
  textTransform: 'none', letterSpacing: 0,
}
const riskBadge = {
  display: 'inline-flex', alignItems: 'center', gap: '12px', fontSize: '24px', fontWeight: 800,
  padding: '14px 24px', borderRadius: '12px', border: '1px solid', letterSpacing: '0.5px',
}
const categoryCard = {
  background: 'rgba(124,110,255,0.06)', border: '1px solid var(--border)',
  borderRadius: '10px', padding: '14px 16px',
}
const errorBox = {
  background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444',
  borderRadius: '8px', padding: '12px 16px', fontSize: '13px', marginBottom: '24px',
}
