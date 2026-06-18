import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getUser, logout, getKeys, createKey, revokeKey } from '../auth'
import { downloadReport } from '../api'

export default function Account() {
  const user = getUser() || {}
  const [keys, setKeys]         = useState([])
  const [newKeyData, setNewKeyData] = useState(null)  // shown once after creation
  const [keyName, setKeyName]   = useState('')
  const [loading, setLoading]   = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError]       = useState('')

  const loadKeys = async () => {
    try {
      setKeys(await getKeys())
    } catch {
      setError('Failed to load API keys.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadKeys() }, [])

  const handleCreate = async () => {
    if (!keyName.trim()) return
    setCreating(true)
    setNewKeyData(null)
    try {
      const data = await createKey(keyName.trim())
      setNewKeyData(data)
      setKeyName('')
      await loadKeys()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create key.')
    } finally {
      setCreating(false)
    }
  }

  const handleRevoke = async (keyId) => {
    if (!confirm('Revoke this API key? Any SDK using it will stop working immediately.')) return
    try {
      await revokeKey(keyId)
      await loadKeys()
    } catch {
      setError('Failed to revoke key.')
    }
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <Link to="/dashboard" style={styles.logo}><img src="/logo-full.svg" alt="Verispect" height="32" style={{display:'block'}}/></Link>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <Link to="/dashboard" style={styles.navLink}>Dashboard</Link>
          <button onClick={logout} style={styles.logoutBtn}>Sign Out</button>
        </div>
      </div>

      <div style={styles.container}>
        {/* Profile */}
        <div style={styles.card}>
          <div style={styles.sectionTitle}>Company Profile</div>
          <div style={styles.profileRow}>
            <div style={styles.avatar}>{(user.company_name || 'V')[0].toUpperCase()}</div>
            <div>
              <div style={styles.companyName}>{user.company_name || '—'}</div>
              <div style={styles.email}>{user.email || '—'}</div>
              <div style={styles.planBadge}>{(user.plan || 'free').toUpperCase()} PLAN</div>
            </div>
          </div>
        </div>

        {/* API Keys */}
        <div style={styles.card}>
          <div style={styles.sectionTitle}>API Keys</div>
          <p style={styles.hint}>
            Use these keys in the Verispect SDK: <code style={styles.code}>wrap(client, verispect_key="vs_live_...")</code>
          </p>

          {error && <div style={styles.error}>{error}</div>}

          {/* New key reveal */}
          {newKeyData && (
            <div style={styles.newKeyBox}>
              <div style={{ fontWeight: '600', color: '#10b981', marginBottom: '8px' }}>
                ✓ Key created — copy it now, it won't be shown again
              </div>
              <code style={styles.keyCode}>{newKeyData.key_value}</code>
              <button
                onClick={() => navigator.clipboard.writeText(newKeyData.key_value)}
                style={styles.copyBtn}
              >
                📋 Copy
              </button>
            </div>
          )}

          {/* Key list */}
          {loading ? (
            <div style={styles.hint}>Loading...</div>
          ) : (
            <div style={styles.keyList}>
              {keys.filter(k => k.is_active).map(k => (
                <div key={k.id} style={styles.keyRow}>
                  <div>
                    <div style={styles.keyName}>{k.name}</div>
                    <div style={styles.keyPreview}>{k.key_preview}</div>
                    <div style={styles.keyMeta}>
                      Created {new Date(k.created_at).toLocaleDateString()}
                      {k.last_used_at && ` · Last used ${new Date(k.last_used_at).toLocaleDateString()}`}
                    </div>
                  </div>
                  <button onClick={() => handleRevoke(k.id)} style={styles.revokeBtn}>
                    Revoke
                  </button>
                </div>
              ))}
              {keys.filter(k => k.is_active).length === 0 && (
                <div style={styles.hint}>No active keys. Create one below.</div>
              )}
            </div>
          )}

          {/* Create key */}
          <div style={styles.createRow}>
            <input
              value={keyName}
              onChange={e => setKeyName(e.target.value)}
              placeholder="Key name (e.g. Production)"
              style={styles.input}
              onKeyDown={e => e.key === 'Enter' && handleCreate()}
            />
            <button onClick={handleCreate} disabled={creating || !keyName.trim()} style={styles.createBtn}>
              {creating ? '...' : '+ Generate Key'}
            </button>
          </div>
        </div>

        {/* Quick start */}
        <div style={styles.card}>
          <div style={styles.sectionTitle}>Quick Start</div>
          <pre style={styles.codeBlock}>{`pip install verispect-sdk

from openai import OpenAI
from verispect import wrap

client = wrap(
    OpenAI(api_key="sk-..."),
    verispect_key="vs_live_YOUR_KEY"
)

# Use exactly as before — nothing else changes
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "..."}]
)`}</pre>
        </div>

        {/* Reports */}
        <div style={styles.card}>
          <div style={styles.sectionTitle}>Compliance Reports</div>
          <p style={styles.hint}>
            Generate a branded PDF report for your company — suitable for regulators, boards, and auditors.
          </p>
          <button onClick={() => downloadReport(user.company_name)} style={styles.reportBtn}>
            📄 Download Compliance Report
          </button>
        </div>
      </div>
    </div>
  )
}

const styles = {
  page:        { minHeight: '100vh', background: '#0f1119', color: '#f9fafb' },
  header:      {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    padding: '16px 32px', borderBottom: '1px solid rgba(255,255,255,0.06)',
    background: '#1a1d27',
  },
  logo:        { color: '#7c6eff', fontWeight: '700', fontSize: '18px', textDecoration: 'none' },
  navLink:     { color: '#9ca3af', textDecoration: 'none', fontSize: '14px' },
  logoutBtn:   {
    background: 'transparent', border: '1px solid rgba(255,255,255,0.1)',
    color: '#9ca3af', borderRadius: '6px', padding: '6px 14px',
    fontSize: '13px', cursor: 'pointer',
  },
  container:   { maxWidth: '760px', margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: '24px' },
  card:        {
    background: '#1a1d27', border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: '12px', padding: '28px',
  },
  sectionTitle:{ fontSize: '16px', fontWeight: '700', marginBottom: '16px', color: '#f9fafb' },
  profileRow:  { display: 'flex', gap: '16px', alignItems: 'center' },
  avatar:      {
    width: '52px', height: '52px', borderRadius: '12px',
    background: 'linear-gradient(135deg,#7c6eff,#a78bfa)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '22px', fontWeight: '700', color: '#fff', flexShrink: 0,
  },
  companyName: { fontSize: '18px', fontWeight: '600', marginBottom: '4px' },
  email:       { fontSize: '13px', color: '#9ca3af', marginBottom: '8px' },
  planBadge:   {
    display: 'inline-block', background: 'rgba(124,110,255,0.15)',
    color: '#7c6eff', borderRadius: '4px', padding: '2px 8px',
    fontSize: '11px', fontWeight: '700',
  },
  hint:        { fontSize: '13px', color: '#6b7280', marginBottom: '12px' },
  code:        { background: '#0f1119', padding: '2px 6px', borderRadius: '4px', fontSize: '12px', color: '#a78bfa' },
  error:       {
    background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
    color: '#ef4444', borderRadius: '8px', padding: '10px 14px',
    fontSize: '13px', marginBottom: '12px',
  },
  newKeyBox:   {
    background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.25)',
    borderRadius: '8px', padding: '14px', marginBottom: '16px',
  },
  keyCode:     { display: 'block', color: '#7c6eff', fontSize: '13px', wordBreak: 'break-all', margin: '8px 0' },
  copyBtn:     {
    background: '#0f1119', border: '1px solid rgba(255,255,255,0.1)',
    color: '#9ca3af', borderRadius: '6px', padding: '6px 12px',
    fontSize: '12px', cursor: 'pointer',
  },
  keyList:     { display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' },
  keyRow:      {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    background: '#0f1119', border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: '8px', padding: '12px 16px',
  },
  keyName:     { fontSize: '14px', fontWeight: '600', marginBottom: '2px' },
  keyPreview:  { fontSize: '12px', color: '#7c6eff', fontFamily: 'monospace', marginBottom: '2px' },
  keyMeta:     { fontSize: '11px', color: '#6b7280' },
  revokeBtn:   {
    background: 'transparent', border: '1px solid rgba(239,68,68,0.3)',
    color: '#ef4444', borderRadius: '6px', padding: '5px 12px',
    fontSize: '12px', cursor: 'pointer',
  },
  createRow:   { display: 'flex', gap: '10px' },
  input:       {
    flex: 1, background: '#0f1119', border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '8px', padding: '9px 14px', color: '#f9fafb',
    fontSize: '13px', outline: 'none',
  },
  createBtn:   {
    background: 'linear-gradient(135deg,#7c6eff,#a78bfa)',
    color: '#fff', border: 'none', borderRadius: '8px',
    padding: '9px 18px', fontSize: '13px', fontWeight: '600', cursor: 'pointer',
    whiteSpace: 'nowrap',
  },
  codeBlock:   {
    background: '#0f1119', border: '1px solid rgba(255,255,255,0.06)',
    borderRadius: '8px', padding: '16px', fontSize: '12px',
    color: '#a78bfa', overflowX: 'auto', lineHeight: '1.6',
    fontFamily: 'monospace',
  },
  reportBtn:   {
    background: 'linear-gradient(135deg,#7c6eff,#a78bfa)',
    color: '#fff', border: 'none', borderRadius: '8px',
    padding: '10px 20px', fontSize: '13px', fontWeight: '600', cursor: 'pointer',
  },
}
