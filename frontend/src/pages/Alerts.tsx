import { useState, useEffect } from 'react'
import api from '../services/api'

interface AlertStatus {
  risk_score: number
  risk_level: string
  alert_status: string
  auto_alerts_enabled: boolean
  threshold: number
  last_alert_time: string | null
  can_send_alert: boolean
  time_until_next_alert: number | null
}

interface AlertConfig {
  threshold: number
  cooldown_minutes: number
  email_configured: boolean
  recipients: string[]
}

function getRiskStatusClass(level: string): string {
  switch (level.toLowerCase()) {
    case 'low': return 'text-success'
    case 'moderate': return 'text-warning'
    case 'high':
    case 'critical': return 'text-danger'
    default: return 'text-text-secondary'
  }
}

function getAlertStatusClass(status: string): string {
  switch (status) {
    case 'Normal': return 'text-success'
    case 'High Risk': return 'text-danger'
    case 'Alert Sent': return 'text-warning'
    default: return 'text-text-secondary'
  }
}

function formatTimeRemaining(seconds: number | null): string {
  if (!seconds) return 'Ready'
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes}m ${secs}s`
}

export default function Alerts() {
  const [status, setStatus] = useState<AlertStatus | null>(null)
  const [config, setConfig] = useState<AlertConfig | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    loadData()
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  async function loadData() {
    try {
      setLoading(true)
      const [statusData, configData] = await Promise.all([
        api.getAlertStatus(),
        api.getAlertConfig()
      ])
      setStatus(statusData)
      setConfig(configData)
    } catch (error) {
      console.error('Error loading alert data:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleSendManualAlert() {
    try {
      setSending(true)
      setMessage(null)
      const result = await api.sendManualAlert()
      setMessage({ type: 'success', text: result.message })
      await loadData() // Refresh status
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to send alert' })
    } finally {
      setSending(false)
    }
  }

  async function handleTestEmail() {
    try {
      setSending(true)
      setMessage(null)
      const result = await api.testEmail()
      setMessage({ type: 'success', text: result.message })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to send test email' })
    } finally {
      setSending(false)
    }
  }

  if (loading && !status) {
    return (
      <div className="space-y-8">
        <h1 className="text-2xl font-semibold text-text-primary">Email Alerts</h1>
        <div className="card">
          <p className="text-text-secondary">Loading...</p>
        </div>
      </div>
    )
  }

  const riskScore = status?.risk_score || 0
  const riskLevel = status?.risk_level || 'Low'
  const alertStatus = status?.alert_status || 'Normal'
  const threshold = status?.threshold || 70
  const canSend = status?.can_send_alert ?? true

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-text-primary">Email Alerts</h1>
        <p className="text-sm text-text-muted mt-1">
          Manage automatic and manual email alerts for high-risk situations
        </p>
      </div>

      {/* Message Banner */}
      {message && (
        <div className={`card ${message.type === 'success' ? 'bg-success/10 border-success' : 'bg-danger/10 border-danger'}`}>
          <p className={`text-sm ${message.type === 'success' ? 'text-success' : 'text-danger'}`}>
            {message.text}
          </p>
        </div>
      )}

      {/* Current Status */}
      <div className="grid grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-text-primary">Current Risk Score</span>
            <span className={`text-lg font-semibold ${getRiskStatusClass(riskLevel)}`}>
              {riskScore.toFixed(1)}
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-text-muted">
              <span>Risk Level</span>
              <span className={getRiskStatusClass(riskLevel)}>{riskLevel}</span>
            </div>
            <div className="h-2 bg-surface rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  riskScore >= threshold ? 'bg-danger' : riskScore >= threshold * 0.7 ? 'bg-warning' : 'bg-success'
                }`}
                style={{ width: `${Math.min(riskScore, 100)}%` }}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-text-primary">Alert Status</span>
            <span className={`text-sm font-semibold ${getAlertStatusClass(alertStatus)}`}>
              {alertStatus}
            </span>
          </div>
          <div className="space-y-2 text-xs text-text-muted">
            <div className="flex items-center justify-between">
              <span>Auto-alerts</span>
              <span className={status?.auto_alerts_enabled ? 'text-success' : 'text-text-muted'}>
                {status?.auto_alerts_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            {status?.last_alert_time && (
              <div className="flex items-center justify-between">
                <span>Last Alert</span>
                <span>{new Date(status.last_alert_time).toLocaleString()}</span>
              </div>
            )}
            {status?.time_until_next_alert && (
              <div className="flex items-center justify-between">
                <span>Cooldown</span>
                <span>{formatTimeRemaining(status.time_until_next_alert)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Configuration */}
      {config && (
        <div className="card">
          <h2 className="section-title mb-4">Configuration</h2>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="text-xs text-text-muted mb-1">Alert Threshold</div>
              <div className="text-lg font-semibold text-text-primary">{config.threshold}</div>
              <div className="text-xs text-text-muted mt-1">
                Auto-alerts trigger when risk score exceeds this value
              </div>
            </div>
            <div>
              <div className="text-xs text-text-muted mb-1">Cooldown Period</div>
              <div className="text-lg font-semibold text-text-primary">{config.cooldown_minutes} minutes</div>
              <div className="text-xs text-text-muted mt-1">
                Minimum time between alerts
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-border">
            <div className="text-xs text-text-muted mb-1">Email Configuration</div>
            <div className={`text-sm ${config.email_configured ? 'text-success' : 'text-danger'}`}>
              {config.email_configured ? '✓ Configured' : '✗ Not configured'}
            </div>
            {config.recipients.length > 0 && (
              <div className="text-xs text-text-muted mt-2">
                Recipients: {config.recipients.join(', ')}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="card">
        <h2 className="section-title mb-4">Actions</h2>
        <div className="flex gap-4">
          <button
            onClick={handleSendManualAlert}
            disabled={!canSend || sending || !config?.email_configured}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? 'Sending...' : 'Send Alert Manually'}
          </button>
          <button
            onClick={handleTestEmail}
            disabled={sending || !config?.email_configured}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? 'Sending...' : 'Test Email'}
          </button>
        </div>
        {!canSend && (
          <p className="text-xs text-warning mt-2">
            Alert cooldown active. Please wait before sending another alert.
          </p>
        )}
        {!config?.email_configured && (
          <p className="text-xs text-danger mt-2">
            Email configuration incomplete. Please configure email settings in the backend.
          </p>
        )}
      </div>

      {/* Info */}
      <div className="card bg-surface border-border">
        <h3 className="text-sm font-medium text-text-primary mb-2">About Email Alerts</h3>
        <ul className="text-xs text-text-muted space-y-1 list-disc list-inside">
          <li>Automatic alerts are sent when the risk score exceeds the threshold ({threshold})</li>
          <li>Manual alerts can be sent at any time (subject to cooldown period)</li>
          <li>Alerts are sent to configured recipients only</li>
          <li>This system is for academic and demonstration purposes only</li>
        </ul>
      </div>
    </div>
  )
}
