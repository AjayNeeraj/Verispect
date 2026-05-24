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

/* ===== Compliance Score Ring (SVG) ===== */
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
        <div className="compliance-score-label">
          {score != null ? 'Score' : 'No Data'}
        </div>
      </div>
    </div>
  )
}

/* ===== Metric Card ===== */
function MetricCard({ label, value, sub, accentColor }) {
  return (
    <div className="metric-card" style={accentColor ? { borderColor: accentColor + '22' } : {}}>
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

/* ===== Custom Tooltip for Charts ===== */
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null
  return (
    <div style={{
      background: '#0f1119', border: '1px solid rgba(124,110,255,0.2)',
      borderRadius: '8px', padding: '10px 14px', fontSize: '12px'
    }}>
      <div style={{ color: '#6b7280', marginBottom: 4 }}>Probe #{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color, fontWeight: 600 }}>
          {p.name}: {typeof p.value === 'number' ? p.value.toFixed(4) : p.value}
        </div>
      ))}
    </div>
  )
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
      <div className="loading-screen">
        <div className="loading-logo">Verispect</div>
        <div className="loading-text">Loading compliance data...</div>
      </div>
    )
  }

  // Build bias breakdown data from compliance categories
  const biasData = compliance?.categories
    ? Object.entries(compliance.categories).map(([key, val]) => ({
        category: CATEGORY_LABELS[key] || key,
        avg_drift: val.avg_drift,
        probes_run: val.probes_run,
        flagged: val.flagged,
      }))
    : []

  return (
    <div className="app">
      {/* ===== Header ===== */}
      <div className="header">
        <div className="logo">Verispect</div>
        <div className="header-right">
          <span className="badge">AI Hiring Compliance</span>
          <span className="badge badge-eu">EU AI Act Ready</span>
          <button className="refresh-btn" onClick={() => { setLoading(true); load() }}>
            Refresh
          </button>
        </div>
      </div>

      <div className="main">
        {/* ===== Compliance Score Hero ===== */}
        <div className="compliance-hero">
          <ComplianceRing score={compliance?.compliance_score} />
          <div className="compliance-info">
            <h2>Compliance Health</h2>
            <p>
              Verispect continuously monitors your AI model for behavioral drift and bias across
              {' '}{Object.keys(compliance?.categories || {}).length} protected categories.
              {compliance?.total_probes > 0
                ? ` ${compliance.total_probes} probes have been fired, with ${compliance.total_flagged} flagged events.`
                : ' Run test calls through Verispect to start generating compliance data.'}
            </p>
            {compliance?.severity_distribution && Object.keys(compliance.severity_distribution).length > 0 && (
              <div className="compliance-badges">
                {Object.entries(compliance.severity_distribution).map(([sev, count]) => (
                  <span key={sev} className={`severity-badge ${SEVERITY_CONFIG[sev]?.className || ''}`}>
                    {SEVERITY_CONFIG[sev]?.label || sev}: {count}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ===== Metric Cards ===== */}
        <div className="metrics-row">
          <MetricCard
            label="Total API Calls"
            value={metrics?.total_calls ?? 0}
            sub="Proxied through Verispect"
          />
          <MetricCard
            label="Probes Fired"
            value={metrics?.total_probes ?? 0}
            sub="10% sample rate"
            accentColor="#7c6eff"
          />
          <MetricCard
            label="Drift Events"
            value={metrics?.total_flagged ?? 0}
            sub="Flagged responses"
            accentColor={metrics?.total_flagged > 0 ? '#ef4444' : '#10b981'}
          />
          <MetricCard
            label="Avg Drift Score"
            value={metrics?.avg_drift?.toFixed(4) ?? '0.0000'}
            sub="0 = stable · 1 = drifted"
            accentColor="#f59e0b"
          />
        </div>

        {/* ===== Two Column: Bias Breakdown + Drift Timeline ===== */}
        <div className="two-col">
          {/* Bias Breakdown */}
          <div className="section">
            <div className="section-title">
              Bias Breakdown by Category
            </div>
            {biasData.length === 0 ? (
              <div className="no-data">No probe data yet — fire test calls to generate bias analysis</div>
            ) : (
              biasData.map((item) => {
                const barColor = getDriftColor(item.avg_drift)
                const widthPct = Math.min((item.avg_drift / 0.5) * 100, 100)
                return (
                  <div className="bias-category" key={item.category}>
                    <div className="bias-category-label">{item.category}</div>
                    <div className="bias-bar-track">
                      <div
                        className="bias-bar-fill"
                        style={{ width: `${widthPct}%`, background: barColor }}
                      />
                    </div>
                    <div className="bias-bar-value" style={{ color: barColor }}>
                      {item.avg_drift.toFixed(4)}
                    </div>
                  </div>
                )
              })
            )}
          </div>

          {/* Drift Timeline */}
          <div className="section">
            <div className="section-title">Drift Score Timeline</div>
            {timeline.length === 0 ? (
              <div className="no-data">No probe data yet — make API calls through Verispect to generate data</div>
            ) : (
              <ResponsiveContainer width="100%" height={biasData.length > 4 ? 280 : 220}>
                <LineChart data={timeline}>
                  <XAxis dataKey="index" stroke="#333" fontSize={11} />
                  <YAxis stroke="#333" fontSize={11} domain={[0, 0.5]} />
                  <Tooltip content={<ChartTooltip />} />
                  <ReferenceLine
                    y={0.18}
                    stroke="#ef4444"
                    strokeDasharray="4 4"
                    label={{ value: 'Threshold', fill: '#ef4444', fontSize: 11 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="drift_score"
                    name="Drift Score"
                    stroke="#7c6eff"
                    strokeWidth={2}
                    dot={{ fill: '#7c6eff', r: 3 }}
                    activeDot={{ r: 5, stroke: '#7c6eff', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* ===== Drift Events Table ===== */}
        <div className="section">
          <div className="section-title">
            Drift Events
            {driftEvents.length > 0 && <span className="count">({driftEvents.length})</span>}
          </div>
          {driftEvents.length === 0 ? (
            <div className="no-data">No drift events — model is behaving consistently ✓</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Probe</th>
                    <th>Category</th>
                    <th>Severity</th>
                    <th>Drift Score</th>
                    <th>Model</th>
                    <th>Response</th>
                  </tr>
                </thead>
                <tbody>
                  {driftEvents.map(row => (
                    <tr key={row.id}>
                      <td>{row.created_at}</td>
                      <td><span className="canary-badge">{row.probe_id}</span></td>
                      <td><span className="category-badge">{CATEGORY_LABELS[row.probe_category] || row.probe_category || '—'}</span></td>
                      <td>{row.severity ? <SeverityBadge severity={row.severity} /> : '—'}</td>
                      <td><span className="status-flagged">{row.drift_score?.toFixed(4)}</span></td>
                      <td>{row.model}</td>
                      <td>{row.response}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* ===== Full Call Log ===== */}
        <div className="section">
          <div className="section-title">
            Call Log
            <span className="count">(last 100)</span>
          </div>
          {logs.length === 0 ? (
            <div className="no-data">No calls logged yet</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Model</th>
                    <th>Type</th>
                    <th>Category</th>
                    <th>Tokens</th>
                    <th>Latency</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(row => (
                    <tr key={row.id}>
                      <td>{row.created_at}</td>
                      <td>{row.model}</td>
                      <td>
                        {row.is_canary
                          ? <span className="canary-badge">canary</span>
                          : <span style={{ color: '#6b7280' }}>real</span>}
                      </td>
                      <td>
                        {row.probe_category
                          ? <span className="category-badge">{CATEGORY_LABELS[row.probe_category] || row.probe_category}</span>
                          : '—'}
                      </td>
                      <td>{(row.prompt_tokens || 0) + (row.completion_tokens || 0)}</td>
                      <td>{row.latency_ms}ms</td>
                      <td>
                        {row.flagged
                          ? <SeverityBadge severity={row.severity || 'high'} />
                          : <span className="status-ok">ok</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}