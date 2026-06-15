import { useState } from 'react'
import { Link } from 'react-router-dom'
import { downloadReport, downloadDpia } from '../api'
import { getUser, logout } from '../auth'

function NavHeader() {
  return (
    <div className="app-header">
      <Link to="/dashboard" className="app-header-logo" style={{ textDecoration: 'none' }}>
        <span>⚡</span> Verispect
      </Link>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Link to="/dashboard" style={navLinkStyle}>Dashboard</Link>
        <Link to="/risk" style={navLinkStyle}>Risk Classifier</Link>
        <Link to="/audit" style={{ ...navLinkStyle, ...navLinkActive }}>Audit Pack</Link>
        <Link to="/account" style={navLinkStyle}>⚙ Account</Link>
        <button onClick={logout} style={signOutStyle}>Sign Out</button>
      </div>
    </div>
  )
}

export default function AuditPack() {
  const user = getUser() || {}

  const [reportState, setReportState] = useState({ loading: false, error: '', done: false })
  const [dpiaState, setDpiaState]     = useState({ loading: false, error: '', done: false })

  const [form, setForm] = useState({
    company: user.company_name || '',
    system_name: 'AI Decision System',
    purpose: 'automated decision support',
    model: 'gpt-4o-mini',
  })
  const setField = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleReport = async () => {
    setReportState({ loading: true, error: '', done: false })
    try {
      await downloadReport(user.company_name)
      setReportState({ loading: false, error: '', done: true })
    } catch {
      setReportState({ loading: false, error: 'Could not generate the report. Please sign in again and retry.', done: false })
    }
  }

  const handleDpia = async () => {
    setDpiaState({ loading: true, error: '', done: false })
    try {
      await downloadDpia(form)
      setDpiaState({ loading: false, error: '', done: true })
    } catch {
      setDpiaState({ loading: false, error: 'Could not generate the DPIA. Please try again.', done: false })
    }
  }

  return (
    <div className="app">
      <NavHeader />
      <div className="app-container" style={{ maxWidth: '1100px' }}>
        {/* Intro */}
        <div className="card card-highlighted" style={{ marginBottom: '32px', padding: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '10px' }}>Audit Pack</h1>
          <p style={{ color: 'var(--text-muted)', lineHeight: '1.6', maxWidth: '760px' }}>
            Generate regulator-ready documentation in seconds, pre-populated with your live monitoring
            evidence. Suitable for boards, auditors, and EU AI Act conformity files.
          </p>
        </div>

        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '24px', marginBottom: 0 }}>
          {/* Compliance Report */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="section-title"><div className="section-icon">📄</div>Compliance Report</div>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: '1.6', marginBottom: '20px', flex: 1 }}>
              A branded PDF summarising your bias and drift monitoring across every protected
              characteristic — your headline evidence of continuous oversight (Art. 9, Art. 72).
            </p>
            <ul style={featureList}>
              <li>Overall compliance score &amp; probe counts</li>
              <li>Per-characteristic bias breakdown</li>
              <li>Drift events &amp; methodology</li>
            </ul>
            {reportState.error && <div style={errorBox}>{reportState.error}</div>}
            {reportState.done && <div style={successBox}>✓ Report downloaded.</div>}
            <button onClick={handleReport} disabled={reportState.loading} style={primaryBtn}>
              {reportState.loading ? 'Generating…' : '📄 Generate Compliance Report'}
            </button>
            <p style={hintText}>Authenticated · uses your account’s monitoring data.</p>
          </div>

          {/* DPIA */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="section-title"><div className="section-icon">🛡️</div>DPIA &amp; Technical Documentation</div>
            <p style={{ color: 'var(--text-muted)', fontSize: '14px', lineHeight: '1.6', marginBottom: '20px' }}>
              A full Data Protection Impact Assessment + Annex IV technical documentation, populated
              with your real monitoring evidence (GDPR Art. 35 · AI Act Art. 11).
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
              <Field label="Company / Operator" value={form.company} onChange={v => setField('company', v)} placeholder="Acme HR GmbH" />
              <Field label="System name" value={form.system_name} onChange={v => setField('system_name', v)} placeholder="CandidateRank AI" />
              <Field label="Purpose" value={form.purpose} onChange={v => setField('purpose', v)} placeholder="automated candidate screening" />
              <Field label="Model" value={form.model} onChange={v => setField('model', v)} placeholder="gpt-4o-mini" />
            </div>

            {dpiaState.error && <div style={errorBox}>{dpiaState.error}</div>}
            {dpiaState.done && <div style={successBox}>✓ DPIA downloaded.</div>}
            <button onClick={handleDpia} disabled={dpiaState.loading} style={{ ...primaryBtn, marginTop: 'auto' }}>
              {dpiaState.loading ? 'Generating…' : '🛡️ Generate DPIA'}
            </button>
          </div>
        </div>

        <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '24px', lineHeight: '1.5' }}>
          These documents are decision-support, not legal advice or certification. The operator remains
          responsible for conformity. Not sure of your risk tier? Run the{' '}
          <Link to="/risk" style={{ color: 'var(--primary)' }}>AI Act Risk Classifier</Link> first.
        </p>
      </div>
    </div>
  )
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <label style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>{label}</span>
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={inputStyle}
      />
    </label>
  )
}

// ── inline styles ─────────────────────────────────────────────────────────────
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
const primaryBtn = {
  background: 'linear-gradient(135deg, #7c6eff 0%, #a78bfa 100%)', color: '#fff', border: 'none',
  borderRadius: '8px', padding: '12px 24px', fontSize: '14px', fontWeight: 600, cursor: 'pointer',
  textTransform: 'none', letterSpacing: 0, width: '100%',
}
const inputStyle = {
  background: 'var(--dark)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px',
  padding: '10px 14px', color: 'var(--text)', fontSize: '13px', outline: 'none', width: '100%',
}
const featureList = {
  listStyle: 'none', padding: 0, margin: '0 0 20px 0', display: 'flex', flexDirection: 'column', gap: '8px',
  fontSize: '13px', color: 'var(--text-muted)',
}
const hintText = { fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px', textAlign: 'center' }
const errorBox = {
  background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#ef4444',
  borderRadius: '8px', padding: '10px 14px', fontSize: '13px', marginBottom: '12px',
}
const successBox = {
  background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', color: '#10b981',
  borderRadius: '8px', padding: '10px 14px', fontSize: '13px', marginBottom: '12px',
}
