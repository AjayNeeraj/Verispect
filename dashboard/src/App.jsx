import { useState, useEffect } from 'react'
import { getMetrics, getLogs, getDriftEvents, getDriftTimeline, getComplianceSummary } from './api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts'
import './index.css'

const CATEGORY_LABELS = {
  gender: 'Gender',
  age: 'Age',
  race_ethnicity: 'Race / Ethnicity',
  nationality: 'Nationality',
  disability: 'Disability',
  parental: 'Parental Status',
  socioeconomic: 'Socioeconomic',
  consistency: 'Consistency',
}

const SEVERITY_CONFIG = {
  none: { label: 'None', color: '#10b981', className: 'severity-none' },
  low: { label: 'Low', color: '#f59e0b', className: 'severity-low' },
  medium: { label: 'Medium', color: '#f97316', className: 'severity-medium' },
  high: { label: 'High', color: '#ef4444', className: 'severity-high' },
}

function getDriftColor(score) {
  if (score == null) return '#6b7280'
  if (score < 0.10) return '#10b981'
  if (score < 0.18) return '#f59e0b'
  return '#ef4444'
}

function getComplianceColor(score) {
  if (score == null) return '#6b7280'
  if (score >= 90) return '#10b981'
  if (score >= 75) return '#f59e0b'
  return '#ef4444'
}

/* ===== Compliance Ring ===== */
function ComplianceRing({ score }) {
  const radius = 58
  const stroke = 8
  const circumference = 2 * Math.PI * radius
  const pct = score != null ? score / 100 : 0
  const offset = circumference * (1 - pct)
  const color = getComplianceColor(score)

  return (
    <div className="compliance-score-ring">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth={stroke} />
        <circle
          cx="70" cy="70" r={radius} fill="none"
          stroke={color} strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="compliance-score-value">
        <div className="compliance-score-number" style={{ color }}>
          {score != null ? score : '—'}
        </div>
        <div className="compliance-score-label">Score</div>
      </div>
    </div>
  )
}

/* ===== Metric Card ===== */
function MetricCard({ label, value, sub, accentColor }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value" style={accentColor ? { color: accentColor } : {}}>{value}</div>
      {sub && <div className="metric-sub">{sub}</div>}
    </div>
  )
}

/* ===== Severity Badge ===== */
function SeverityBadge({ severity }) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.none
  return <span className={`severity-badge ${config.className}`}>{config.label}</span>
}

/* ===== Main App ===== */
export default function App() {
  const [metrics, setMetrics] = useState(null)
  const [logs, setLogs] = useState([])
  const [driftEvents, setDriftEvents] = useState([])
  const [timeline, setTimeline] = useState([])
  const [compliance, setCompliance] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const [m, l, d, t, c] = await Promise.all([
        getMetrics(), getLogs(), getDriftEvents(), getDriftTimeline(), getComplianceSummary()
      ])
      setMetrics(m)
      setLogs(l)
      setDriftEvents(d)
      setTimeline(t.map((row, i) => ({ ...row, index: i + 1 })))
      setCompliance(c)
    } catch (e) {
      console.error('API error:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) {
    return (
      <div className="app" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '16px', background: 'linear-gradient(135deg, #7c6eff 0%, #a78bfa 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Verispect</div>
          <div className="spinner" style={{ margin: '0 auto', marginBottom: '16px' }}></div>
          <div style={{ color: '#9ca3af' }}>Loading compliance dashboard...</div>
        </div>
      </div>
    )
  }

  const biasData = compliance?.categories
    ? Object.entries(compliance.categories).map(([key, val]) => ({
        category: CATEGORY_LABELS[key] || key,
        avg_drift: val.avg_drift,
      }))
    : []

  return (
    <div className="app">
      {/* Header */}
      <div className="app-header">
        <div className="app-header-logo">
          <span>⚡</span> Verispect
        </div>
        <div className="app-header-status">
          <div className="status-dot"></div>
          Live Monitoring
        </div>
      </div>

      {/* Container */}
      <div className="app-container">
        {/* Compliance Hero */}
        <div className="card card-highlighted" style={{ marginBottom: '40px', padding: '40px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '40px', alignItems: 'center' }}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <ComplianceRing score={compliance?.compliance_score} />
            </div>
            <div>
              <h2 style={{ fontSize: '28px', fontWeight: '600', marginBottom: '12px' }}>Compliance Health Dashboard</h2>
              <p style={{ color: '#9ca3af', marginBottom: '20px', lineHeight: '1.6' }}>
                Verispect monitors your AI models for behavioral drift and bias across {Object.keys(compliance?.categories || {}).length} protected categories.
                {compliance?.total_probes > 0 
                  ? ` ${compliance.total_probes} test probes have been executed.`
                  : ' Start by proxying your API calls through Verispect.'}
              </p>
              {metrics && (
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                  <div className="badge">{metrics.total_calls} API Calls</div>
                  <div className="badge">{metrics.total_probes} Probes</div>
                  <div className="badge">{metrics.total_flagged} Drift Events</div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div style={{ marginBottom: '40px' }}>
          <div className="section-title">
            <div className="section-icon">📊</div>
            Key Metrics
          </div>
          <div className="grid grid-4">
            <MetricCard
              label="Total API Calls"
              value={metrics?.total_calls ?? '0'}
              sub="Proxied through Verispect"
            />
            <MetricCard
              label="Test Probes"
              value={metrics?.total_probes ?? '0'}
              sub="Automated canary tests"
              accentColor="#7c6eff"
            />
            <MetricCard
              label="Drift Events"
              value={metrics?.total_flagged ?? '0'}
              sub="Threshold violations"
              accentColor={metrics?.total_flagged > 0 ? '#ef4444' : '#10b981'}
            />
            <MetricCard
              label="Avg Drift Score"
              value={metrics?.avg_drift?.toFixed(3) ?? '0.000'}
              sub="0=Stable · 1=Drifted"
              accentColor="#f59e0b"
            />
          </div>
        </div>

        {/* Bias Analysis & Timeline */}
        <div style={{ marginBottom: '40px' }}>
          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* Bias by Category */}
            <div className="card">
              <div className="section-title">
                <div className="section-icon">🎯</div>
                Bias by Category
              </div>
              {biasData.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📈</div>
                  <div className="empty-text">No drift data yet</div>
                  <div className="empty-subtext">Fire test probes to analyze bias</div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {biasData.map((item) => {
                    const barColor = getDriftColor(item.avg_drift)
                    const widthPct = Math.min((item.avg_drift / 0.5) * 100, 100)
                    return (
                      <div key={item.category}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '13px' }}>
                          <span style={{ fontWeight: '500' }}>{item.category}</span>
                          <span style={{ color: barColor, fontWeight: '600' }}>{item.avg_drift.toFixed(4)}</span>
                        </div>
                        <div style={{ height: '6px', background: 'rgba(124, 110, 255, 0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${widthPct}%`, background: barColor, transition: 'width 0.3s ease' }}></div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {/* Drift Timeline */}
            <div className="card">
              <div className="section-title">
                <div className="section-icon">📉</div>
                Drift Timeline
              </div>
              {timeline.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📊</div>
                  <div className="empty-text">No timeline data</div>
                  <div className="empty-subtext">Make calls through Verispect</div>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={timeline}>
                    <XAxis dataKey="index" stroke="#9ca3af" fontSize={11} />
                    <YAxis stroke="#9ca3af" fontSize={11} domain={[0, 0.5]} />
                    <Tooltip 
                      contentStyle={{ background: '#0f1119', border: '1px solid rgba(124,110,255,0.2)', borderRadius: '8px' }}
                      labelStyle={{ color: '#9ca3af' }}
                    />
                    <ReferenceLine y={0.18} stroke="#ef4444" strokeDasharray="4 4" label="Threshold" />
                    <Line
                      type="monotone"
                      dataKey="drift_score"
                      stroke="#7c6eff"
                      strokeWidth={2}
                      dot={{ fill: '#7c6eff', r: 3 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        {/* Drift Events */}
        <div style={{ marginBottom: '40px' }}>
          <div className="section-title">
            <div className="section-icon">🚨</div>
            Drift Events {driftEvents.length > 0 && <span style={{ color: '#ef4444', marginLeft: '8px' }}>({driftEvents.length})</span>}
          </div>
          <div className="card">
            {driftEvents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">✓</div>
                <div className="empty-text">No drift events detected</div>
                <div className="empty-subtext">Model is behaving consistently</div>
              </div>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Category</th>
                      <th>Severity</th>
                      <th>Drift Score</th>
                      <th>Model</th>
                    </tr>
                  </thead>
                  <tbody>
                    {driftEvents.slice(0, 10).map(row => (
                      <tr key={row.id}>
                        <td>{new Date(row.created_at).toLocaleString()}</td>
                        <td><span className="badge">{CATEGORY_LABELS[row.probe_category] || row.probe_category || '—'}</span></td>
                        <td>{row.severity ? <SeverityBadge severity={row.severity} /> : '—'}</td>
                        <td style={{ fontWeight: '600', color: getDriftColor(row.drift_score) }}>{row.drift_score?.toFixed(4)}</td>
                        <td>{row.model}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Call Log */}
        <div>
          <div className="section-title">
            <div className="section-icon">📋</div>
            Recent Calls {logs.length > 0 && <span style={{ color: '#9ca3af' }}>(last {logs.length})</span>}
          </div>
          <div className="card">
            {logs.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <div className="empty-text">No calls logged yet</div>
                <div className="empty-subtext">Start proxying API calls through Verispect</div>
              </div>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Model</th>
                      <th>Type</th>
                      <th>Category</th>
                      <th>Tokens</th>
                      <th>Latency</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.slice(0, 20).map(row => (
                      <tr key={row.id}>
                        <td style={{ fontSize: '12px', color: '#9ca3af' }}>{new Date(row.created_at).toLocaleString()}</td>
                        <td style={{ fontWeight: '500' }}>{row.model}</td>
                        <td>
                          <span className="badge" style={{ fontSize: '10px' }}>
                            {row.is_canary ? '🔬 Probe' : '⚙️ Real'}
                          </span>
                        </td>
                        <td>
                          {row.probe_category 
                            ? <span className="badge">{CATEGORY_LABELS[row.probe_category]}</span>
                            : '—'}
                        </td>
                        <td>{(row.prompt_tokens || 0) + (row.completion_tokens || 0)}</td>
                        <td style={{ color: '#9ca3af' }}>{row.latency_ms}ms</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
