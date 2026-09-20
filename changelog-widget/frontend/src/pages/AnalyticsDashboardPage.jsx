/**
 * pages/AnalyticsDashboardPage.jsx
 * ────────────────────────────────
 * Real-time analytics dashboard for Changelog performance:
 * - Aggregate statistics (Total Views, Reactions, Published, Scheduled)
 * - Reaction sentiment breakdown
 * - Top 5 most viewed & most reacted updates
 * - Per-update performance table
 */
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import AdminSidebar from '../components/AdminSidebar'
import analyticsService from '../services/analyticsService'
import { Card, Badge, Button } from '../components/ui'
import './AdminDashboardPage.css'
import './AnalyticsDashboardPage.css'

export default function AnalyticsDashboardPage() {
  const [stats, setStats] = useState(null)
  const [performance, setPerformance] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadData = async () => {
    setLoading(true)
    setError(null)
    try {
      const [dashData, perfData] = await Promise.all([
        analyticsService.getDashboard(),
        analyticsService.getUpdatePerformance(20),
      ])
      setStats(dashData)
      setPerformance(perfData || [])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load analytics data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  return (
    <div className="admin-layout">
      <AdminSidebar />

      <main className="admin-content">
        <div className="admin-header-bar">
          <div>
            <h1 className="admin-page-title">Analytics & Engagement</h1>
            <p className="admin-page-subtitle">
              Monitor readership, views, and visitor sentiment across your product updates.
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={loadData} disabled={loading}>
            🔄 Refresh Metrics
          </Button>
        </div>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '20px' }}>
            {error}
          </div>
        )}

        {loading ? (
          <div className="admin-empty-state" style={{ padding: '60px' }}>
            <div className="spinner spinner-lg" style={{ marginBottom: '16px' }} />
            <p style={{ color: 'var(--color-text-muted)' }}>Loading analytics & engagement metrics…</p>
          </div>
        ) : stats ? (
          <div className="analytics-content">
            {/* Stat Cards Grid */}
            <div className="metrics-grid">
              <Card className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Total Views</span>
                  <span className="metric-icon">👁️</span>
                </div>
                <div className="metric-value">{stats.total_views.toLocaleString()}</div>
                <div className="metric-hint">Anonymous readers tracked</div>
              </Card>

              <Card className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Total Reactions</span>
                  <span className="metric-icon">❤️</span>
                </div>
                <div className="metric-value">{stats.total_reactions.toLocaleString()}</div>
                <div className="metric-hint">Across all published posts</div>
              </Card>

              <Card className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Published Updates</span>
                  <span className="metric-icon">🚀</span>
                </div>
                <div className="metric-value">{stats.total_published}</div>
                <div className="metric-hint">{stats.total_scheduled} scheduled, {stats.total_draft} drafts</div>
              </Card>

              <Card className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">Avg. Reactions / Post</span>
                  <span className="metric-icon">📈</span>
                </div>
                <div className="metric-value">
                  {stats.total_published > 0
                    ? (stats.total_reactions / stats.total_published).toFixed(1)
                    : '0.0'}
                </div>
                <div className="metric-hint">Engagement ratio</div>
              </Card>
            </div>

            {/* Reaction Breakdown & Top Posts */}
            <div className="analytics-row">
              {/* Reactions distribution */}
              <Card className="analytics-box">
                <h3 className="box-title">Reaction Breakdown</h3>
                <div className="reaction-breakdown-list">
                  {Object.entries(stats.reaction_distribution || {}).length === 0 ? (
                    <p className="empty-hint">No reactions recorded yet.</p>
                  ) : (
                    Object.entries(stats.reaction_distribution).map(([emoji, count]) => {
                      const pct = stats.total_reactions > 0
                        ? Math.round((count / stats.total_reactions) * 100)
                        : 0
                      return (
                        <div key={emoji} className="reaction-stat-row">
                          <span className="reaction-emoji-badge">{emoji}</span>
                          <div className="reaction-bar-wrap">
                            <div className="reaction-bar-fill" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="reaction-count">{count} ({pct}%)</span>
                        </div>
                      )
                    })
                  )}
                </div>
              </Card>

              {/* Most Viewed Posts */}
              <Card className="analytics-box">
                <h3 className="box-title">Top Viewed Updates</h3>
                {stats.most_viewed?.length === 0 ? (
                  <p className="empty-hint">No page views recorded yet.</p>
                ) : (
                  <ul className="top-posts-list">
                    {stats.most_viewed.map((post) => (
                      <li key={post.id} className="top-post-item">
                        <Link to={`/changelog/${post.slug}`} className="top-post-title" target="_blank">
                          {post.title}
                        </Link>
                        <span className="top-post-count">👁️ {post.view_count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            </div>

            {/* Per-update Performance Table */}
            <Card className="performance-table-card">
              <h3 className="box-title" style={{ marginBottom: '16px' }}>Update Performance (Last 20)</h3>
              <div className="admin-table-wrapper">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Update Title</th>
                      <th>Category</th>
                      <th>Views</th>
                      <th>Reactions</th>
                      <th>Published</th>
                    </tr>
                  </thead>
                  <tbody>
                    {performance.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="admin-table-empty">
                          No published updates found.
                        </td>
                      </tr>
                    ) : (
                      performance.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <Link to={`/changelog/${item.slug}`} className="item-title-link" target="_blank">
                              {item.title}
                            </Link>
                            {item.version && (
                              <span className="version-pill" style={{ marginLeft: '8px' }}>
                                {item.version}
                              </span>
                            )}
                          </td>
                          <td>
                            <Badge variant={item.category?.toLowerCase() || 'neutral'}>
                              #{item.category}
                            </Badge>
                          </td>
                          <td>
                            <span className="view-badge">👁️ {item.views}</span>
                          </td>
                          <td>
                            <span className="reaction-badge">❤️ {item.total_reactions}</span>
                          </td>
                          <td style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
                            {item.published_at ? new Date(item.published_at).toLocaleDateString() : '—'}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        ) : null}
      </main>
    </div>
  )
}
