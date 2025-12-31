import { useState, useEffect } from 'react'
import api from '../services/api'
import type { PolicyBrief } from '../types'
import { mockPolicyBrief } from '../data/mockData'

export default function PolicyBriefPage() {
  const [brief, setBrief] = useState<PolicyBrief>(mockPolicyBrief)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const result = await api.getBrief()
      setBrief(result)
      setLoading(false)
    }
    fetchData()
  }, [])

  const generatedDate = new Date(brief.generated_at).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-text-muted">
        Loading policy brief...
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Document Header */}
      <header className="border-b border-border pb-6 mb-8">
        <div className="flex items-start justify-between">
          <div>
            <p className="section-title mb-2">Policy Brief</p>
            <h1 className="text-2xl font-semibold text-text-primary">
              National Discourse Intelligence Report
            </h1>
          </div>
          <div className="text-right text-xs text-text-muted">
            <p>Generated</p>
            <p className="font-mono">{generatedDate}</p>
          </div>
        </div>
      </header>

      {/* Document Body */}
      <article className="space-y-8">
        {/* Executive Summary */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Executive Summary
          </h2>
          <p className="text-text-secondary leading-relaxed">
            {brief.executive_summary}
          </p>
        </section>

        {/* Recommended Actions */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Recommended Actions
          </h2>
          <ul className="space-y-3">
            {brief.recommended_actions.map((action, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="text-text-muted font-mono text-sm">
                  {String(idx + 1).padStart(2, '0')}
                </span>
                <span className="text-text-secondary leading-relaxed">
                  {action}
                </span>
              </li>
            ))}
          </ul>
        </section>

        {/* Responsible Ministries */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Responsible Institutions
          </h2>
          <ul className="space-y-2">
            {brief.responsible_ministries.map((ministry) => (
              <li key={ministry} className="flex items-center gap-2 text-text-secondary">
                <span className="w-1 h-1 bg-accent rounded-full" />
                {ministry}
              </li>
            ))}
          </ul>
        </section>
      </article>

      {/* Document Footer */}
      <footer className="border-t border-border mt-12 pt-6">
        <div className="flex items-center justify-between text-xs text-text-muted">
          <span>Classification: UNCLASSIFIED / DEMO</span>
          <span>National Intelligence System • Public Discourse Analytics</span>
        </div>
        <p className="text-xs text-text-muted mt-4 leading-relaxed">
          This brief is automatically generated based on current discourse analysis. 
          It should be reviewed by qualified analysts before any policy action. 
          The system provides insights, not recommendations—human judgment is essential.
        </p>
      </footer>
    </div>
  )
}
