/**
 * pages/ChangelogDetailPage.jsx
 * ─────────────────────────────
 * Detailed view of a single changelog post.
 * Features:
 * - Clean header with category badge, title, published date
 * - Safe Markdown rendering via react-markdown + remark-gfm
 * - Cover image display with smooth aspect containment
 * - Skeleton loading state and error handling
 * - Interactive Reactions component
 */
import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { changelogService } from '../services/changelogService'
import ReactionButtons from '../components/ReactionButtons'
import './ChangelogDetailPage.css'

const CATEGORY_MAP = {
  NEW: { label: '#New', cls: 'badge-new' },
  IMPROVED: { label: '#Improved', cls: 'badge-improved' },
  FIXED: { label: '#Fixed', cls: 'badge-fixed' },
}

export default function ChangelogDetailPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [changelog, setChangelog] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)

    changelogService
      .getBySlug(slug)
      .then((data) => {
        if (isMounted) setChangelog(data)
      })
      .catch((err) => {
        if (isMounted) {
          setError(err?.response?.data?.detail || 'Changelog update not found.')
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [slug])

  if (loading) {
    return (
      <div className="detail-page-container">
        <div className="skeleton" style={{ width: '80px', height: '32px', marginBottom: '24px' }} />
        <div className="skeleton skeleton-cover" style={{ height: '320px', marginBottom: '32px' }} />
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <div className="skeleton skeleton-badge" />
          <div className="skeleton" style={{ width: '120px', height: '18px' }} />
        </div>
        <div className="skeleton skeleton-title" style={{ width: '85%', height: '38px', marginBottom: '24px' }} />
        <div className="skeleton skeleton-line" style={{ width: '100%', marginBottom: '12px' }} />
        <div className="skeleton skeleton-line" style={{ width: '92%', marginBottom: '12px' }} />
        <div className="skeleton skeleton-line" style={{ width: '75%', marginBottom: '12px' }} />
      </div>
    )
  }

  if (error || !changelog) {
    return (
      <div className="detail-page-container">
        <div className="detail-not-found-card fade-in">
          <span className="detail-not-found-icon">🔍</span>
          <h2 className="detail-not-found-title">Update Not Found</h2>
          <p className="detail-not-found-text">
            {error || 'This changelog entry does not exist or has not been published.'}
          </p>
          <Link to="/" className="btn btn-primary">
            ← Back to Timeline
          </Link>
        </div>
      </div>
    )
  }

  const catMeta = CATEGORY_MAP[changelog.category] || CATEGORY_MAP.NEW
  const dateStr = changelog.published_at
    ? new Date(changelog.published_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Draft'

  return (
    <article className="detail-page-container fade-in">
      <div className="detail-nav-back">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="detail-back-btn"
          aria-label="Back to previous page"
        >
          <span>←</span> Back to Updates
        </button>
      </div>

      {changelog.cover_image && (
        <div className="detail-cover-container">
          <img
            src={changelog.cover_image}
            alt={changelog.title}
            className="detail-cover-image"
            onError={(e) => {
              e.target.parentElement.style.display = 'none'
            }}
          />
        </div>
      )}

      <header className="detail-header">
        <div className="detail-meta-row">
          <span className={`badge ${catMeta.cls}`}>
            {catMeta.label}
          </span>
          <time className="detail-date" dateTime={changelog.published_at}>
            {dateStr}
          </time>
          {changelog.status === 'DRAFT' && (
            <span className="detail-draft-pill">
              DRAFT
            </span>
          )}
        </div>

        <h1 className="detail-title">
          {changelog.title}
        </h1>
      </header>

      <div className="markdown-body detail-content">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {changelog.content_markdown || ''}
        </ReactMarkdown>
      </div>

      <footer className="detail-footer">
        <ReactionButtons changelogId={changelog.id} />
        <Link to="/" className="btn btn-secondary btn-sm">
          ← All Product Updates
        </Link>
      </footer>
    </article>
  )
}
