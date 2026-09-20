/**
 * pages/AdminDashboardPage.jsx
 * ────────────────────────────
 * Admin management dashboard for changelog posts.
 * Includes:
 * - Admin Sidebar with navigation & statistics
 * - Filterable changelog list table (category, status, search, pagination)
 * - Actions: Edit, Delete, Quick-Publish
 * - Seamless integration with MarkdownStudio for creating/editing posts
 */
import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { changelogService } from '../services/changelogService'
import MarkdownStudio from '../components/MarkdownStudio'
import { Button, Input, Select, Badge, Card } from '../components/ui'
import './AdminDashboardPage.css'

export default function AdminDashboardPage() {
  const { user, logout } = useAuth()

  // State
  const [changelogs, setChangelogs] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionMessage, setActionMessage] = useState(null)

  // Filters
  const [statusFilter, setStatusFilter] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  // Studio Mode: null | 'create' | changelog object for 'edit'
  const [studioTarget, setStudioTarget] = useState(null)
  const [isSaving, setIsSaving] = useState(false)

  // Fetch changelogs
  const fetchChangelogs = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await changelogService.list({
        page,
        limit: 10,
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
        search: searchQuery || undefined,
      })
      setChangelogs(data.items || [])
      setTotal(data.total || 0)
      setPages(data.pages || 1)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load changelogs.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter, categoryFilter, searchQuery])

  useEffect(() => {
    fetchChangelogs()
  }, [fetchChangelogs])

  // Clear toast notifications after 4 seconds
  useEffect(() => {
    if (actionMessage) {
      const timer = setTimeout(() => setActionMessage(null), 4000)
      return () => clearTimeout(timer)
    }
  }, [actionMessage])

  // CRUD Handlers
  const handlePublishClick = async (item) => {
    try {
      await changelogService.publish(item.id)
      setActionMessage({ type: 'success', text: `"${item.title}" is now published!` })
      fetchChangelogs()
    } catch (err) {
      setActionMessage({
        type: 'error',
        text: err?.response?.data?.detail || 'Failed to publish update.',
      })
    }
  }

  const handleDeleteClick = async (item) => {
    if (!window.confirm(`Are you sure you want to delete "${item.title}"? This cannot be undone.`)) {
      return
    }
    try {
      await changelogService.remove(item.id)
      setActionMessage({ type: 'success', text: `Deleted "${item.title}".` })
      fetchChangelogs()
    } catch (err) {
      setActionMessage({
        type: 'error',
        text: err?.response?.data?.detail || 'Failed to delete update.',
      })
    }
  }

  // Markdown Studio save / publish
  const handleStudioSave = async (payload) => {
    setIsSaving(true)
    try {
      if (studioTarget && studioTarget !== 'create') {
        // Edit mode
        await changelogService.update(studioTarget.id, payload)
        setActionMessage({ type: 'success', text: 'Changelog updated successfully.' })
      } else {
        // Create mode
        await changelogService.create(payload)
        setActionMessage({
          type: 'success',
          text: payload.status === 'PUBLISHED' ? 'Update created & published!' : 'Draft created successfully.',
        })
      }
      setStudioTarget(null)
      fetchChangelogs()
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to save changelog. Please check your fields.')
    } finally {
      setIsSaving(false)
    }
  }

  // If Markdown Studio is active, render it full screen
  if (studioTarget !== null) {
    return (
      <MarkdownStudio
        initialData={studioTarget === 'create' ? null : studioTarget}
        onSave={(data) => handleStudioSave({ ...data, status: 'DRAFT' })}
        onPublish={(data) => handleStudioSave({ ...data, status: 'PUBLISHED' })}
        onCancel={() => setStudioTarget(null)}
        isSaving={isSaving}
      />
    )
  }

  // Count stats
  const publishedCount = changelogs.filter((c) => c.status === 'PUBLISHED').length
  const draftCount = changelogs.filter((c) => c.status === 'DRAFT').length

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className="admin-sidebar">
        <div className="admin-sidebar-header">
          <span className="sidebar-logo">⚡</span>
          <div>
            <h3 className="sidebar-title">Admin Studio</h3>
            <p className="sidebar-subtitle">Product Changelogs</p>
          </div>
        </div>

        <nav className="admin-sidebar-nav">
          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() => {
              setStatusFilter('')
              setCategoryFilter('')
              setPage(1)
            }}
          >
            📋 All Updates
          </button>
          <button
            type="button"
            className={`sidebar-nav-item ${statusFilter === 'PUBLISHED' ? 'active' : ''}`}
            onClick={() => {
              setStatusFilter('PUBLISHED')
              setPage(1)
            }}
          >
            🚀 Published ({publishedCount})
          </button>
          <button
            type="button"
            className={`sidebar-nav-item ${statusFilter === 'DRAFT' ? 'active' : ''}`}
            onClick={() => {
              setStatusFilter('DRAFT')
              setPage(1)
            }}
          >
            📝 Drafts ({draftCount})
          </button>
        </nav>

        <div className="admin-sidebar-footer">
          <div className="admin-user-info">
            <span className="user-avatar">{user?.name ? user.name.charAt(0).toUpperCase() : 'A'}</span>
            <div className="user-details">
              <span className="user-name">{user?.name || 'Administrator'}</span>
              <span className="user-role">Role: {user?.role || 'admin'}</span>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={logout} title="Sign out">
            🚪 Logout
          </Button>
        </div>
      </aside>

      {/* Main Admin Content Area */}
      <main className="admin-content">
        {/* Banner Alert Toast */}
        {actionMessage && (
          <div className={`admin-toast alert alert-${actionMessage.type === 'error' ? 'error' : 'success'} fade-in`}>
            <span>{actionMessage.type === 'error' ? '⚠️' : '✅'}</span>
            <span>{actionMessage.text}</span>
          </div>
        )}

        {/* Header Bar */}
        <header className="admin-header">
          <div>
            <h1 className="admin-page-title">Changelog Updates</h1>
            <p className="admin-page-subtitle">
              Manage product announcements, draft release notes, and publish updates.
            </p>
          </div>
          <div className="admin-header-actions">
            <Button
              variant="secondary"
              size="sm"
              render={<Link to="/" target="_blank" rel="noreferrer" />}
            >
              🌐 View Public Feed
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => setStudioTarget('create')}
            >
              ✨ Create Update
            </Button>
          </div>
        </header>

        {/* Admin KPI Stat Cards */}
        <div className="admin-stats-grid">
          <Card className="admin-stat-card">
            <div className="stat-icon-wrapper stat-icon-purple">📊</div>
            <div className="stat-content">
              <span className="stat-label">Total Updates</span>
              <strong className="stat-value">{total}</strong>
            </div>
          </Card>
          <Card className="admin-stat-card">
            <div className="stat-icon-wrapper stat-icon-green">🚀</div>
            <div className="stat-content">
              <span className="stat-label">Published</span>
              <strong className="stat-value">{publishedCount}</strong>
            </div>
          </Card>
          <Card className="admin-stat-card">
            <div className="stat-icon-wrapper stat-icon-amber">📝</div>
            <div className="stat-content">
              <span className="stat-label">Drafts</span>
              <strong className="stat-value">{draftCount}</strong>
            </div>
          </Card>
        </div>

        {/* Filters and Controls */}
        <div className="admin-controls-card">
          <div className="controls-search">
            <Input
              type="text"
              className="input-sm"
              placeholder="Search updates by title..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setPage(1)
              }}
            />
          </div>

          <div className="controls-filters">
            <Select
              className="select-sm"
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All Categories</option>
              <option value="NEW">New Feature</option>
              <option value="IMPROVED">Improvement</option>
              <option value="FIXED">Bug Fix</option>
            </Select>

            <Select
              className="select-sm"
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value)
                setPage(1)
              }}
            >
              <option value="">All Statuses</option>
              <option value="PUBLISHED">Published</option>
              <option value="DRAFT">Draft</option>
            </Select>
          </div>
        </div>

        {/* Table / List */}
        <Card className="admin-table-wrapper">
          {loading ? (
            <div className="admin-empty-state">
              <div className="spinner spinner-lg" style={{ marginBottom: '16px' }} />
              <p style={{ color: 'var(--color-text-muted)', fontSize: '14px' }}>Loading changelogs…</p>
            </div>
          ) : error ? (
            <div className="admin-empty-state">
              <span className="empty-icon">⚠️</span>
              <h3 style={{ color: 'var(--color-danger)' }}>Failed to load</h3>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '16px', fontSize: '13px' }}>{error}</p>
              <Button variant="secondary" size="sm" onClick={fetchChangelogs}>
                Retry
              </Button>
            </div>
          ) : changelogs.length === 0 ? (
            <div className="admin-empty-state">
              <span className="empty-icon">📭</span>
              <h3>No updates found</h3>
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '16px' }}>
                {searchQuery || statusFilter || categoryFilter
                  ? 'No updates match the selected filters.'
                  : 'Start by creating your first changelog entry.'}
              </p>
              <Button
                variant="default"
                size="sm"
                onClick={() => setStudioTarget('create')}
              >
                Create First Update
              </Button>
            </div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Published Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {changelogs.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div className="table-title-cell">
                        <strong className="item-title">{item.title}</strong>
                        <span className="item-slug">/{item.slug}</span>
                      </div>
                    </td>
                    <td>
                      <Badge
                        variant={
                          item.category === 'NEW'
                            ? 'default'
                            : item.category === 'IMPROVED'
                            ? 'secondary'
                            : 'outline'
                        }
                        className={`badge-${item.category.toLowerCase()}`}
                      >
                        {item.category}
                      </Badge>
                    </td>
                    <td>
                      <Badge
                        variant={item.status === 'PUBLISHED' ? 'success' : 'warning'}
                        className={`status-pill ${
                          item.status === 'PUBLISHED' ? 'status-published' : 'status-draft'
                        }`}
                      >
                        {item.status}
                      </Badge>
                    </td>
                    <td className="table-date-cell">
                      {item.published_at
                        ? new Date(item.published_at).toLocaleDateString(undefined, {
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric',
                          })
                        : '—'}
                    </td>
                    <td>
                      <div className="table-actions">
                        {item.status === 'DRAFT' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-success"
                            onClick={() => handlePublishClick(item)}
                            title="Publish this update"
                          >
                            🚀 Publish
                          </Button>
                        )}
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => setStudioTarget(item)}
                          title="Edit update"
                        >
                          ✏️ Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteClick(item)}
                          title="Delete update"
                        >
                          🗑️
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Pagination */}
          {pages > 1 && (
            <div className="admin-pagination">
              <span className="admin-pagination-info">
                Page {page} of {pages} &mdash; {total} total update{total !== 1 ? 's' : ''}
              </span>
              <div className="admin-pagination-buttons">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  ← Prev
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next →
                </Button>
              </div>
            </div>
          )}
        </Card>
      </main>
    </div>
  )
}
