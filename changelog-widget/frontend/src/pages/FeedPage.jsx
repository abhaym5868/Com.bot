import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import {
  Button,
  Badge,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Tabs,
  TabsList,
  TabsTab,
  TabsPanel,
} from '../components/ui'
import './FeedPage.css'

const SCHEMA_FIELDS = [
  { field: 'updates', type: 'Array<Object>', desc: 'List of published product update objects' },
  { field: 'updates[].title', type: 'String', desc: 'Title of the changelog entry' },
  { field: 'updates[].slug', type: 'String', desc: 'URL-friendly unique slug identifier' },
  { field: 'updates[].category', type: 'String', desc: 'Category identifier: NEW, IMPROVED, or FIXED' },
  { field: 'updates[].published_at', type: 'String (ISO 8601)', desc: 'UTC timestamp when update was published' },
  { field: 'updates[].cover_image', type: 'String | null', desc: 'Optional uploaded cover image URL' },
  { field: 'total', type: 'Integer', desc: 'Total number of published updates matching criteria' },
  { field: 'page', type: 'Integer', desc: 'Current page number in the paginated set' },
  { field: 'limit', type: 'Integer', desc: 'Maximum number of items returned per page' },
  { field: 'pages', type: 'Integer', desc: 'Total number of pages available' },
]

export default function FeedPage() {
  const [feedData, setFeedData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState(null)
  const [copiedEndpoint, setCopiedEndpoint] = useState(false)
  const [copiedJson, setCopiedJson] = useState(false)
  const [copiedCurl, setCopiedCurl] = useState(false)
  const [copiedJs, setCopiedJs] = useState(false)

  // Try API interactive state
  const [tryLoading, setTryLoading] = useState(false)
  const [tryResult, setTryResult] = useState(null)
  const [tryLatency, setTryLatency] = useState(null)
  const [tryStatus, setTryStatus] = useState(null)
  const [tryCopied, setTryCopied] = useState(false)

  const [activeTab, setActiveTab] = useState('curl')

  const endpointPath = '/api/v1/changelog/feed'
  const absoluteEndpoint = typeof window !== 'undefined'
    ? `${window.location.origin}${endpointPath}`
    : endpointPath

  const fetchFeedData = async () => {
    setLoading(true)
    setFetchError(null)
    try {
      const res = await fetch(endpointPath)
      if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`)
      const data = await res.json()
      setFeedData(data)
    } catch (err) {
      setFetchError(err.message || 'Failed to load feed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFeedData()
  }, [])

  const copyToClipboard = async (text, setCopiedState) => {
    try {
      if (navigator?.clipboard?.writeText && window.isSecureContext) {
        await navigator.clipboard.writeText(text)
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = text
        textArea.style.position = 'fixed'
        textArea.style.left = '-999999px'
        textArea.style.top = '-999999px'
        document.body.appendChild(textArea)
        textArea.focus()
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }
      setCopiedState(true)
      setTimeout(() => setCopiedState(false), 2000)
    } catch (err) {
      console.error('Failed to copy: ', err)
    }
  }

  const handleTryRequest = async () => {
    setTryLoading(true)
    const startTime = performance.now()
    try {
      const res = await fetch(endpointPath)
      const duration = Math.round(performance.now() - startTime)
      const data = await res.json()
      setTryStatus(res.status)
      setTryLatency(duration)
      setTryResult(data)
    } catch (err) {
      const duration = Math.round(performance.now() - startTime)
      setTryStatus('Error')
      setTryLatency(duration)
      setTryResult({ error: err.message })
    } finally {
      setTryLoading(false)
    }
  }

  const curlExample = `curl -X GET "${absoluteEndpoint}" \\
  -H "Accept: application/json"`

  const jsExample = `// Fetch published changelog updates
const response = await fetch("${endpointPath}", {
  headers: { "Accept": "application/json" }
});
const data = await response.json();
console.log(\`Retrieved \${data.total} changelog updates:\`, data.updates);`

  const jsonString = feedData ? JSON.stringify(feedData, null, 2) : ''
  const lineCount = jsonString ? jsonString.split('\n').length : 0
  const jsonByteSize = jsonString ? new Blob([jsonString]).size : 0

  return (
    <main className="feed-page">
      <div className="feed-container">
        {/* 1. Breadcrumb */}
        <nav className="feed-breadcrumb" aria-label="Breadcrumb">
          <Link to="/" className="breadcrumb-link">Home</Link>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Developer API</span>
          <span className="breadcrumb-separator">/</span>
          <span className="breadcrumb-current">Changelog Feed</span>
        </nav>

        {/* 2. Hero Section */}
        <section className="feed-hero">
          <Badge variant="default" className="feed-hero-badge mb-3">
            <span className="hero-badge-dot"></span>
            REST API v1
          </Badge>
          <h1 className="feed-hero-title">Changelog Feed API</h1>
          <p className="feed-hero-subtitle">
            Access real-time published product updates, release notes, and version announcements through a clean, open JSON feed.
          </p>

          <div className="feed-endpoint-box">
            <Badge variant="default" className="endpoint-method-badge">GET</Badge>
            <code className="endpoint-url">{endpointPath}</code>
            <Button
              variant="secondary"
              size="sm"
              className={`feed-btn-copy ${copiedEndpoint ? 'copied' : ''}`}
              onClick={() => copyToClipboard(absoluteEndpoint, setCopiedEndpoint)}
              title="Copy endpoint URL"
            >
              {copiedEndpoint ? '✓ Copied!' : '📋 Copy Endpoint'}
            </Button>
          </div>
        </section>

        {/* 3. API Info Cards using Coss UI Card primitives */}
        <section className="feed-cards-grid">
          <Card className="feed-card">
            <CardHeader className="p-4 pb-2">
              <div className="feed-card-header">
                <span className="feed-card-label">Method</span>
                <span className="feed-card-icon">⚡</span>
              </div>
              <CardTitle className="feed-card-value text-accent">GET</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <p className="feed-card-desc">Idempotent public read operation</p>
            </CardContent>
          </Card>

          <Card className="feed-card">
            <CardHeader className="p-4 pb-2">
              <div className="feed-card-header">
                <span className="feed-card-label">Authentication</span>
                <span className="feed-card-icon">🔓</span>
              </div>
              <CardTitle className="feed-card-value text-success">Public</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <p className="feed-card-desc">No API keys or tokens required</p>
            </CardContent>
          </Card>

          <Card className="feed-card">
            <CardHeader className="p-4 pb-2">
              <div className="feed-card-header">
                <span className="feed-card-label">Format</span>
                <span className="feed-card-icon">📦</span>
              </div>
              <CardTitle className="feed-card-value">JSON</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <p className="feed-card-desc">Content-Type: application/json</p>
            </CardContent>
          </Card>

          <Card className="feed-card">
            <CardHeader className="p-4 pb-2">
              <div className="feed-card-header">
                <span className="feed-card-label">Status</span>
                <span className="feed-status-dot online"></span>
              </div>
              <CardTitle className="feed-card-value text-success">Available</CardTitle>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <p className="feed-card-desc">200 OK • Production live</p>
            </CardContent>
          </Card>
        </section>

        {/* 3.5. Endpoint Information Section using Coss UI Card */}
        <section className="feed-section">
          <Card className="endpoint-specs-card">
            <CardHeader className="endpoint-specs-header">
              <span className="specs-tag">ENDPOINT INFORMATION</span>
              <CardTitle className="specs-title">Endpoint Details</CardTitle>
            </CardHeader>
            <CardContent className="specs-grid">
              <div className="spec-item">
                <span className="spec-label">Endpoint</span>
                <div className="spec-value">
                  <Badge variant="default" className="spec-method">GET</Badge>
                  <code className="spec-code">{endpointPath}</code>
                </div>
              </div>
              <div className="spec-item">
                <span className="spec-label">Description</span>
                <div className="spec-value spec-desc">
                  Returns the latest published changelog updates in reverse chronological order.
                </div>
              </div>
              <div className="spec-item">
                <span className="spec-label">Response</span>
                <div className="spec-value">
                  <code className="spec-code">application/json</code>
                </div>
              </div>
              <div className="spec-item">
                <span className="spec-label">Authentication</span>
                <div className="spec-value">
                  <Badge variant="success" className="spec-auth-badge">Not required (Public)</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 4. Live API Response Viewer */}
        <section className="feed-section">
          <div className="feed-section-header">
            <div>
              <h2 className="feed-section-title">Live API Response</h2>
              <p className="feed-section-subtitle">
                Live output returned by <code>GET {endpointPath}</code> directly from the database.
              </p>
            </div>
            <div className="viewer-actions">
              <Button
                variant="secondary"
                size="sm"
                onClick={fetchFeedData}
                disabled={loading}
                title="Refresh live response"
              >
                <span className={`refresh-icon ${loading ? 'spinning' : ''}`}>↻</span>
                <span>Refresh</span>
              </Button>

              <Button
                variant="secondary"
                size="sm"
                className={copiedJson ? 'btn-copied' : ''}
                onClick={() => copyToClipboard(jsonString, setCopiedJson)}
                disabled={!feedData || loading}
                title="Copy entire JSON response"
              >
                {copiedJson ? '✓ Copied JSON' : '📋 Copy JSON'}
              </Button>
            </div>
          </div>

          <div className="code-viewer-container">
            <div className="code-viewer-topbar">
              <div className="code-viewer-meta">
                <Badge variant="default" className="code-lang-pill">JSON</Badge>
                <Badge variant="success" className="code-status-pill">200 OK</Badge>
                {lineCount > 0 && <span className="code-stat-pill">{lineCount} lines</span>}
                {jsonByteSize > 0 && <span className="code-stat-pill">{(jsonByteSize / 1024).toFixed(1)} KB</span>}
              </div>
              <div className="code-viewer-endpoint-label">
                <span className="viewer-pulse-dot"></span>
                <span>Realtime Backend Data</span>
              </div>
            </div>

            <div className="code-viewer-content">
              {loading && !feedData ? (
                <div className="code-viewer-loading">
                  <div className="feed-spinner"></div>
                  <span>Fetching live feed payload...</span>
                </div>
              ) : fetchError ? (
                <div className="code-viewer-error">
                  <p>⚠️ Error loading feed: {fetchError}</p>
                  <Button variant="secondary" size="sm" onClick={fetchFeedData}>
                    Try Again
                  </Button>
                </div>
              ) : (
                <SyntaxHighlighter
                  language="json"
                  style={oneLight}
                  showLineNumbers={true}
                  wrapLongLines={false}
                  customStyle={{
                    margin: 0,
                    padding: '1.25rem 1rem',
                    fontSize: '0.84rem',
                    fontFamily: 'var(--font-mono)',
                    lineHeight: '1.6',
                    backgroundColor: '#FAFBFC',
                    border: 'none',
                  }}
                  lineNumberStyle={{
                    color: '#9CA3AF',
                    minWidth: '2.5em',
                    paddingRight: '1.2em',
                    userSelect: 'none',
                  }}
                >
                  {jsonString || '{\n  "updates": []\n}'}
                </SyntaxHighlighter>
              )}
            </div>
          </div>
        </section>

        {/* 5. Interactive "Try the API" Sandbox */}
        <section className="feed-section">
          <div className="feed-section-header">
            <div>
              <h2 className="feed-section-title">Try the Endpoint</h2>
              <p className="feed-section-subtitle">
                Dispatch an interactive HTTP request to the live backend and inspect latency and response metrics.
              </p>
            </div>
          </div>

          <Card className="try-api-card">
            <CardContent className="p-0">
              <div className="try-api-request-bar">
                <Badge variant="default" className="try-method-pill">GET</Badge>
                <span className="try-url-input">{endpointPath}</span>
                <Button
                  variant="default"
                  size="sm"
                  className="try-send-btn"
                  onClick={handleTryRequest}
                  disabled={tryLoading}
                >
                  {tryLoading ? (
                    <>
                      <span className="feed-spinner-sm"></span>
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <span>Send Request</span>
                      <span>→</span>
                    </>
                  )}
                </Button>
              </div>

              {tryResult && (
                <div className="try-api-response-panel fade-in">
                  <div className="try-api-meta-row">
                    <div className="try-metric-badge">
                      <span className="metric-label">Status</span>
                      <Badge variant={tryStatus === 200 ? 'success' : 'destructive'}>
                        {tryStatus === 200 ? '200 OK' : tryStatus}
                      </Badge>
                    </div>

                    {tryLatency !== null && (
                      <div className="try-metric-badge">
                        <span className="metric-label">Latency</span>
                        <span className="metric-value text-accent">{tryLatency} ms</span>
                      </div>
                    )}

                    <div className="try-metric-badge">
                      <span className="metric-label">Type</span>
                      <span className="metric-value">application/json</span>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      className="try-copy-btn"
                      onClick={() => copyToClipboard(JSON.stringify(tryResult, null, 2), setTryCopied)}
                    >
                      {tryCopied ? '✓ Copied' : '📋 Copy'}
                    </Button>
                  </div>

                  <div className="try-code-wrapper">
                    <SyntaxHighlighter
                      language="json"
                      style={oneLight}
                      showLineNumbers={true}
                      wrapLongLines={false}
                      customStyle={{
                        margin: 0,
                        padding: '1rem',
                        fontSize: '0.82rem',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: '1.5',
                        backgroundColor: '#FFFFFF',
                        borderRadius: 'var(--radius-md)',
                        maxHeight: '320px',
                      }}
                      lineNumberStyle={{
                        color: '#9CA3AF',
                        minWidth: '2.2em',
                        paddingRight: '1em',
                        userSelect: 'none',
                      }}
                    >
                      {JSON.stringify(tryResult, null, 2)}
                    </SyntaxHighlighter>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </section>

        {/* 6. Code Examples: cURL and JavaScript using Coss UI Tabs */}
        <section className="feed-section">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="feed-section-header">
              <div>
                <h2 className="feed-section-title">Request Code Examples</h2>
                <p className="feed-section-subtitle">
                  Quick copy-paste snippets to integrate the changelog feed into your own frontend, CLI, or CI pipeline.
                </p>
              </div>
              <TabsList>
                <TabsTab value="curl">cURL</TabsTab>
                <TabsTab value="js">JavaScript (Fetch)</TabsTab>
              </TabsList>
            </div>

            <Card className="code-example-card">
              <div className="code-example-topbar">
                <span className="example-lang-tag">
                  {activeTab === 'curl' ? 'BASH / CURL' : 'JAVASCRIPT (ES6+)'}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    if (activeTab === 'curl') {
                      copyToClipboard(curlExample, setCopiedCurl)
                    } else {
                      copyToClipboard(jsExample, setCopiedJs)
                    }
                  }}
                >
                  {(activeTab === 'curl' ? copiedCurl : copiedJs) ? '✓ Copied' : '📋 Copy snippet'}
                </Button>
              </div>

              <TabsPanel value="curl" className="code-example-body">
                <SyntaxHighlighter
                  language="bash"
                  style={oneLight}
                  customStyle={{
                    margin: 0,
                    padding: '1.25rem 1.25rem',
                    fontSize: '0.85rem',
                    fontFamily: 'var(--font-mono)',
                    lineHeight: '1.6',
                    backgroundColor: '#FAFBFC',
                  }}
                >
                  {curlExample}
                </SyntaxHighlighter>
              </TabsPanel>

              <TabsPanel value="js" className="code-example-body">
                <SyntaxHighlighter
                  language="javascript"
                  style={oneLight}
                  customStyle={{
                    margin: 0,
                    padding: '1.25rem 1.25rem',
                    fontSize: '0.85rem',
                    fontFamily: 'var(--font-mono)',
                    lineHeight: '1.6',
                    backgroundColor: '#FAFBFC',
                  }}
                >
                  {jsExample}
                </SyntaxHighlighter>
              </TabsPanel>
            </Card>
          </Tabs>
        </section>

        {/* 7. Response Schema Reference Table */}
        <section className="feed-section">
          <div className="feed-section-header">
            <div>
              <h2 className="feed-section-title">Response Schema</h2>
              <p className="feed-section-subtitle">
                Comprehensive dictionary of properties returned in the JSON payload.
              </p>
            </div>
          </div>

          <Card className="schema-table-card">
            <table className="schema-table">
              <thead>
                <tr>
                  <th scope="col">Field</th>
                  <th scope="col">Type</th>
                  <th scope="col">Description</th>
                </tr>
              </thead>
              <tbody>
                {SCHEMA_FIELDS.map((item) => (
                  <tr key={item.field}>
                    <td className="field-cell">
                      <code>{item.field}</code>
                    </td>
                    <td className="type-cell">
                      <Badge variant="secondary" className="type-badge">{item.type}</Badge>
                    </td>
                    <td className="desc-cell">{item.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </section>

        {/* 8. Endpoint Metadata & Integration Notes */}
        <section className="feed-section feed-meta-section">
          <div className="feed-info-box">
            <div className="info-box-icon">💡</div>
            <div className="info-box-content">
              <h4 className="info-box-title">Integration & Public Access</h4>
              <p className="info-box-text">
                The changelog feed is cached at the HTTP transport layer and does not require authentication.
                Only entries with <code>PUBLISHED</code> status are exposed; drafts are strictly protected behind admin authentication.
                Standard CORS headers are enabled allowing direct invocation from client-side SPAs.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  )
}
