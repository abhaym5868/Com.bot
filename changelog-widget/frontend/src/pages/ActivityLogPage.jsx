/**
 * pages/ActivityLogPage.jsx
 * ─────────────────────────
 * Admin audit / activity trail.
 * Displays who did what and when across changelog mutations:
 * - Creates, Updates, Publishes, Deletes, Pins, Unpins
 * - Paginated table with formatted timestamps and action badges
 */
import { useState, useEffect, useCallback } from 'react'
import AdminSidebar from '../components/AdminSidebar'
import auditService from '../services/auditService'
import { Card, Badge, Button } from '../components/ui'
import './AdminDashboardPage.css'

export default function ActivityLogPage() {
  const [logs, setLogs] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchLogs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await auditService.list({ page, limit: 20 })
      setLogs(data.items || [])
      setTotal(data.total || 0)
      setPages(data.pages || 1)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load activity logs.')
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  const formatActionBadge = (action) => {
    const act = (action || '').toUpperCase()
    if (act.includes('CREATE')) return <Badge variant="new">CREATE</Badge>
    if (act.includes('PUBLISH')) return <Badge variant="improved">PUBLISH</Badge>
    if (act.includes('DELETE')) return <Badge variant="fixed">DELETE</Badge>
    if (act.includes('PIN')) return <Badge variant="neutral">PIN</Badge>
    if (act.includes('UPDATE')) return <Badge variant="neutral">UPDATE</Badge>
    return <Badge variant="neutral">{action}</Badge>
  }

  return (
    <div className="admin-layout">
      <AdminSidebar />

      <main className="admin-content">
        <div className="admin-header-bar">
          <div>
            <h1 className="admin-page-title">Activity & Audit Log</h1>
            <p className="admin-page-subtitle">
              Detailed chronological record of administrator actions and content modifications.
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={fetchLogs} disabled={loading}>
            🔄 Refresh
          </Button>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '20px' }}>
            {error}
          </div>
        )}

        <Card style={{ padding: '0', overflow: 'hidden' }}>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Admin</th>
                  <th>Action</th>
                  <th>Resource Target</th>
                  <th>Resource ID</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} style={{ padding: '48px', textAlign: 'center' }}>
                      <div className="spinner spinner-lg" style={{ margin: '0 auto 12px' }} />
                      <p style={{ color: 'var(--color-text-muted)', fontSize: '14px', margin: 0 }}>Loading activity logs…</p>
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="admin-table-empty">
                      No activity logs recorded yet.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id}>
                      <td style={{ color: 'var(--color-text-secondary)', fontSize: '0.8125rem', whiteSpace: 'nowrap' }}>
                        {log.timestamp ? new Date(log.timestamp).toLocaleString() : '—'}
                      </td>
                      <td>
                        <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                          {log.user_name || 'Admin'}
                        </span>
                      </td>
                      <td>{formatActionBadge(log.action)}</td>
                      <td>
                        <span style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>
                          {log.resource_title || log.resource_type || '—'}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        {log.resource_id ? `${log.resource_id.slice(0, 8)}…` : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {pages > 1 && (
            <div className="admin-pagination" style={{ padding: '16px' }}>
              <span className="pagination-info">
                Page {page} of {pages} ({total} actions recorded)
              </span>
              <div className="pagination-controls">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1 || loading}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= pages || loading}
                  onClick={() => setPage((p) => Math.min(pages, p + 1))}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </Card>
      </main>
    </div>
  )
}
