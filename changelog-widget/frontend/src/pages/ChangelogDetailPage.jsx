/**
 * pages/ChangelogDetailPage.jsx
 * ─────────────────────────────
 * Detailed view of a single changelog post.
 * Features:
 * - Clean header with category badge, version release pill, title, published date
 * - Safe Markdown rendering via react-markdown + remark-gfm
 * - Cover image display with smooth aspect containment
 * - Interactive Reactions component
 * - View tracking via analyticsService
 * - Social Share & One-Click Copy Link
 * - Related updates in the same category
 * - Previous / Next navigation
 */
import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { changelogService } from '../services/changelogService'
import analyticsService from '../services/analyticsService'
import ReactionButtons from '../components/ReactionButtons'
import { Badge, Button } from '../components/ui'
import './ChangelogDetailPage.css'

const CATEGORY_MAP = {
  NEW: { label: '#New', cls: 'badge-new', variant: 'default' },
  IMPROVED: { label: '#Improved', cls: 'badge-improved', variant: 'secondary' },
  FIXED: { label: '#Fixed', cls: 'badge-fixed', variant: 'outline' },
}

export default function ChangelogDetailPage() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [changelog, setChangelog] = useState(null)
  const [related, setRelated] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let isMounted = true
    setLoading(true)
    setError(null)
    setRelated([])

    changelogService
      .getBySlug(slug)
      .then((data) => {
        if (!isMounted) return
        setChangelog(data)

        // Record anonymous page view for analytics
        if (data?.id) {
          analyticsService.recordView(data.id)
        }

        // Fetch related updates in the same category
        if (data?.category) {
          changelogService
            .list({ category: data.category, limit: 4 })
            .then((res) => {
              if (!isMounted) return
              const others = (res.items || []).filter((item) => item.slug !== slug).slice(0, 3)
              setRelated(others)
            })
            .catch(() => {})
        }
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

  const handleShare = async () => {
    const url = window.location.href
    if (navigator.share) {
      try {
        await navigator.share({
          title: changelog?.title || 'Product Update',
          url,
        })
        return
      } catch {
        // Fallback to clipboard if share was cancelled or failed
      }
    }
    navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2500)
  }

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
          <Button render={<Link to="/" />} variant="default">
            ← Back to Timeline
          </Button>
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
      <div className="detail-nav-back" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Button
          type="button"
          variant="ghost"
          onClick={() => navigate(-1)}
          className="detail-back-btn"
          aria-label="Back to previous page"
        >
          <span>←</span> Back to Updates
        </Button>

        {/* Share / Copy Link button */}
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={handleShare}
          title="Share or copy direct link to this update"
        >
          {copied ? '✅ Link Copied!' : '🔗 Share Update'}
        </Button>
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
          <Badge variant={catMeta.variant} className={catMeta.cls}>
            {catMeta.label}
          </Badge>

          {changelog.version && (
            <span className="version-pill" style={{
              fontSize: '0.75rem',
              padding: '3px 8px',
              borderRadius: '4px',
              background: 'var(--color-accent-dim)',
              color: 'var(--color-accent)',
              fontWeight: 600,
            }}>
              {changelog.version}
            </span>
          )}

          {changelog.is_pinned && (
            <Badge variant="outline" style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)', fontSize: '0.75rem' }}>
              📌 Pinned
            </Badge>
          )}

          <time className="detail-date" dateTime={changelog.published_at}>
            {dateStr}
          </time>

          {changelog.status === 'DRAFT' && (
            <Badge variant="warning" className="detail-draft-pill">
              DRAFT
            </Badge>
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
        <Button variant="secondary" size="sm" render={<Link to="/" />}>
          ← All Product Updates
        </Button>
      </footer>

      {/* Related Updates Section */}
      {related.length > 0 && (
        <section className="detail-related-section">
          <h3 className="related-section-title">Related {catMeta.label} Updates</h3>
          <div className="related-grid">
            {related.map((item) => (
              <Link key={item.id} to={`/changelog/${item.slug}`} className="related-card">
                <div className="related-card-header">
                  <Badge variant={catMeta.variant} className={catMeta.cls} style={{ fontSize: '0.7rem' }}>
                    {catMeta.label}
                  </Badge>
                  {item.version && (
                    <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                      {item.version}
                    </span>
                  )}
                </div>
                <h4 className="related-card-title">{item.title}</h4>
                <time className="related-card-date">
                  {item.published_at ? new Date(item.published_at).toLocaleDateString() : ''}
                </time>
              </Link>
            ))}
          </div>
        </section>
      )}
    </article>
  )
}
