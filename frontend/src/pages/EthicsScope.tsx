export default function EthicsScope() {
  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <header className="border-b border-border pb-6 mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">
          Ethics & Scope
        </h1>
        <p className="text-sm text-text-muted mt-2">
          System guidelines, limitations, and ethical framework
        </p>
      </header>

      {/* Content */}
      <article className="space-y-10">
        {/* System Scope */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            System Scope
          </h2>
          <div className="space-y-3 text-text-secondary leading-relaxed">
            <p>
              The National Intelligence System (NIS) is designed to analyze public discourse 
              at scale, providing actionable insights for policy awareness and strategic communication. 
              The system operates within strict ethical boundaries.
            </p>
            <p>
              <strong className="text-text-primary">What NIS analyzes:</strong>
            </p>
            <ul className="list-disc list-inside space-y-1 text-sm pl-2">
              <li>Publicly available social media content (Reddit, public forums)</li>
              <li>Aggregated sentiment and emotion patterns</li>
              <li>Topic clustering and trend identification</li>
              <li>Potential coordinated inauthentic behavior patterns</li>
            </ul>
          </div>
        </section>

        {/* What NIS Does Not Do */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Boundaries
          </h2>
          <div className="space-y-3 text-text-secondary leading-relaxed">
            <p className="text-sm">NIS explicitly does <strong className="text-danger">not</strong>:</p>
            <ul className="space-y-2 text-sm">
              <li className="flex gap-2">
                <span className="text-danger">×</span>
                <span>Identify, track, or profile individual users</span>
              </li>
              <li className="flex gap-2">
                <span className="text-danger">×</span>
                <span>Access private messages, closed groups, or protected content</span>
              </li>
              <li className="flex gap-2">
                <span className="text-danger">×</span>
                <span>Make predictions about individual behavior</span>
              </li>
              <li className="flex gap-2">
                <span className="text-danger">×</span>
                <span>Store personally identifiable information (PII)</span>
              </li>
              <li className="flex gap-2">
                <span className="text-danger">×</span>
                <span>Provide automated enforcement or takedown capabilities</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Ethical Framework */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Ethical Framework
          </h2>
          <div className="space-y-4 text-text-secondary leading-relaxed text-sm">
            <div>
              <h3 className="font-medium text-text-primary mb-1">Transparency</h3>
              <p>
                All data sources are documented. Analysis methodologies are explainable. 
                System limitations are clearly communicated.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-text-primary mb-1">Privacy by Design</h3>
              <p>
                Data is aggregated and anonymized at ingestion. No individual-level tracking 
                is performed. Author identifiers are hashed or removed.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-text-primary mb-1">Human Oversight</h3>
              <p>
                All insights require human interpretation. The system provides analysis, 
                not decisions. Policy recommendations must be validated by qualified analysts.
              </p>
            </div>
            <div>
              <h3 className="font-medium text-text-primary mb-1">Proportionality</h3>
              <p>
                Analysis is limited to what is necessary for the stated purpose. 
                Data retention is minimized. Access is logged and audited.
              </p>
            </div>
          </div>
        </section>

        {/* Data Handling */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Data Handling
          </h2>
          <div className="space-y-3 text-text-secondary leading-relaxed text-sm">
            <p>
              <strong className="text-text-primary">Sources:</strong> Public Reddit posts and comments 
              from designated subreddits, Google Trends data for keyword interest.
            </p>
            <p>
              <strong className="text-text-primary">Processing:</strong> Text is cleaned, deduplicated, 
              and processed through NLP pipelines. No raw content is stored long-term.
            </p>
            <p>
              <strong className="text-text-primary">Retention:</strong> Aggregated metrics are retained. 
              Raw content is processed and discarded within 24 hours.
            </p>
          </div>
        </section>

        {/* Limitations */}
        <section>
          <h2 className="text-lg font-medium text-text-primary mb-3">
            Known Limitations
          </h2>
          <ul className="space-y-2 text-sm text-text-secondary">
            <li className="flex gap-2">
              <span className="text-warning">!</span>
              <span>Sentiment analysis has inherent accuracy limitations (~85% on benchmark data)</span>
            </li>
            <li className="flex gap-2">
              <span className="text-warning">!</span>
              <span>Reddit demographics may not represent general population</span>
            </li>
            <li className="flex gap-2">
              <span className="text-warning">!</span>
              <span>Sarcasm and nuanced language may be misclassified</span>
            </li>
            <li className="flex gap-2">
              <span className="text-warning">!</span>
              <span>Coordination detection may produce false positives for organic viral content</span>
            </li>
          </ul>
        </section>
      </article>

      {/* Footer */}
      <footer className="border-t border-border mt-12 pt-6 text-xs text-text-muted">
        <p>
          This system is a hackathon demonstration project. It is not affiliated with 
          any government agency. All analysis is performed on publicly available data 
          in compliance with platform terms of service.
        </p>
      </footer>
    </div>
  )
}
