/**
 * pages/TimelinePage.jsx
 * ─────────────────────
 * Public changelog timeline page.
 * Displays published product updates in reverse chronological order.
 *
 * Features:
 * - Reverse chronological order
 * - Debounced search input (400ms) querying title & content_markdown
 * - Category filter tabs: All, #New, #Improved, #Fixed
 * - Changelog cards with cover image, category badge, publication date,
 *   full rendered Markdown content (with code blocks, headings, lists)
 * - Detail page link (/changelog/:slug)
 * - Loading state, empty state, error state with retry
 * - Real backend data without hardcoding
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { changelogService } from '../services/changelogService'
import { useDebounce } from '../hooks/useDebounce'
import ReactionButtons from '../components/ReactionButtons'
import { Badge, Button, Input } from '../components/ui'
import './TimelinePage.css'

const FILTER_TAGS = [
  { value: '', label: 'All' },
  { value: 'NEW', label: '#New', badgeCls: 'badge-new', variant: 'default' },
  { value: 'IMPROVED', label: '#Improved', badgeCls: 'badge-improved', variant: 'secondary' },
  { value: 'FIXED', label: '#Fixed', badgeCls: 'badge-fixed', variant: 'outline' },
]

const safeUrlTransform = (url) => {
  if (!url) return ''
  const trimmed = url.trim().toLowerCase()
  if (
    trimmed.startsWith('javascript:') ||
    trimmed.startsWith('data:') ||
    trimmed.startsWith('vbscript:')
  ) {
    return '#'
  }
  return url
}

function CategoryBadge({ category }) {
  const cat = category?.toUpperCase() || 'NEW'
  const tag = FILTER_TAGS.find((f) => f.value === cat)
  const label = tag ? tag.label : `#${category}`
  const variant = tag?.variant || 'default'

  return <Badge variant={variant} className={`badge ${tag?.badgeCls || 'badge-new'}`}>{label}</Badge>
}

function ChangelogCard({ item }) {
  const formattedDate = item.published_at
    ? new Date(item.published_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null

  return (
    <article className="timeline-card fade-in">
      {/* Optional Cover Image */}
      {item.cover_image && (
        <div className="timeline-card-cover">
          <Link to={`/changelog/${item.slug}`}>
            <img
              src={item.cover_image}
              alt={item.title}
              onError={(e) => {
                e.target.style.display = 'none'
              }}
            />
          </Link>
        </div>
      )}

      <div className="timeline-card-body">
        {/* Metadata: Category Badge, Version, Pinned & Publication Date */}
        <div className="timeline-card-meta">
          <CategoryBadge category={item.category} />
          {item.version && (
            <span className="version-pill" style={{
              fontSize: '0.75rem',
              padding: '2px 7px',
              borderRadius: '4px',
              background: 'var(--color-accent-dim)',
              color: 'var(--color-accent)',
              fontWeight: 600,
            }}>
              {item.version}
            </span>
          )}
          {item.is_pinned && (
            <Badge variant="outline" style={{ borderColor: 'var(--color-accent)', color: 'var(--color-accent)', fontSize: '0.75rem' }}>
              📌 Pinned
            </Badge>
          )}
          {formattedDate && (
            <time className="timeline-date" dateTime={item.published_at}>
              {formattedDate}
            </time>
          )}
        </div>

        {/* Title linking to detail page */}
        <h2 className="timeline-card-title">
          <Link to={`/changelog/${item.slug}`}>{item.title}</Link>
        </h2>

        {/* Rendered Markdown Content with Code Blocks & Formatting */}
        <div className="markdown-body timeline-card-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            urlTransform={safeUrlTransform}
            components={{
              a: ({ href, children, ...props }) => {
                const safeHref = safeUrlTransform(href)
                return (
                  <a href={safeHref} target="_blank" rel="noopener noreferrer" {...props}>
                    {children}
                  </a>
                )
              },
            }}
          >
            {item.content_markdown || ''}
          </ReactMarkdown>
        </div>

        {/* Card Footer / Reactions & Detail Page Link */}
        <div className="timeline-card-footer">
          <ReactionButtons changelogId={item.id} />
          <Link to={`/changelog/${item.slug}`} className="timeline-card-link">
            Permalink & Details →
          </Link>
        </div>
      </div>
    </article>
  )
}

function TimelineSkeleton() {
  return (
    <div className="timeline-feed">
      {[1, 2, 3].map((n) => (
        <div key={n} className="skeleton-card fade-in">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="skeleton skeleton-badge" />
            <div className="skeleton" style={{ width: '110px', height: '14px', borderRadius: '4px' }} />
          </div>
          <div className="skeleton skeleton-title" style={{ marginTop: '4px' }} />
          <div className="skeleton skeleton-line" style={{ width: '92%' }} />
          <div className="skeleton skeleton-line" style={{ width: '84%' }} />
          <div className="skeleton skeleton-line" style={{ width: '65%' }} />
          <div style={{ display: 'flex', gap: '10px', marginTop: '8px', paddingTop: '12px', borderTop: '1px solid var(--color-border)' }}>
            <div className="skeleton" style={{ width: '58px', height: '32px', borderRadius: '8px' }} />
            <div className="skeleton" style={{ width: '58px', height: '32px', borderRadius: '8px' }} />
            <div className="skeleton" style={{ width: '58px', height: '32px', borderRadius: '8px' }} />
          </div>
        </div>
      ))}
    </div>
  )
}

export default function TimelinePage() {
  const [searchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const debouncedSearch = useDebounce(searchInput, 400) // 400ms debounce
  const searchInputRef = useRef(null)

  const [changelogs, setChangelogs] = useState([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Sync URL search params to search input and focus if requested
  useEffect(() => {
    const q = searchParams.get('search') || searchParams.get('q')
    if (q !== null && q !== undefined) {
      setSearchInput(q)
    }
    if (searchParams.get('focus') === 'search' || q) {
      setTimeout(() => {
        if (searchInputRef.current) {
          searchInputRef.current.focus()
          searchInputRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
      }, 100)
    }
  }, [searchParams])

  const fetchTimeline = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await changelogService.list({
        page,
        limit: 10,
        category: category || undefined,
        search: debouncedSearch.trim() || undefined,
      })
      setChangelogs(data.items || [])
      setTotal(data.total || 0)
      setPages(data.pages || 1)
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          'Unable to connect to the backend server. Please verify your connection.'
      )
    } finally {
      setLoading(false)
    }
  }, [page, category, debouncedSearch])

  // Reset page when category or search changes
  useEffect(() => {
    setPage(1)
  }, [category, debouncedSearch])

  useEffect(() => {
    fetchTimeline()
  }, [fetchTimeline])

  const clearSearch = () => {
    setSearchInput('')
  }

  return (
    <main className="timeline-page">
      <div className="timeline-container">
        {/* Header Hero */}
        <header className="timeline-hero">
          <div className="timeline-hero-top">
            <span className="timeline-hero-badge">✨ Live Changelog</span>
            <Link
              to="/feed"
              className="timeline-feed-pill"
              title="View Developer JSON Feed API"
            >
              <span>📡 JSON Feed API</span>
            </Link>
          </div>
          <h1 className="timeline-title">Product Updates</h1>
          <p className="timeline-subtitle">
            All the latest features, enhancements, and performance improvements shipped to production.
          </p>
        </header>

        {/* Search & Filter Bar */}
        <div className="timeline-controls-bar">
          {/* Debounced Search Input */}
          <div className="timeline-search-wrapper">
            <span className="search-icon">🔍</span>
            <Input
              ref={searchInputRef}
              id="timeline-search-input"
              type="text"
              className="timeline-search-input"
              placeholder="Search updates by title or keyword…"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              aria-label="Search changelogs"
            />
            {searchInput && (
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                className="search-clear-btn"
                onClick={clearSearch}
                title="Clear search"
              >
                ✕
              </Button>
            )}
          </div>

          {/* Filter Navigation: All, #New, #Improved, #Fixed */}
          <nav className="timeline-filters" aria-label="Filter updates by category">
            {FILTER_TAGS.map((tag) => (
              <Button
                key={tag.value}
                type="button"
                variant={category === tag.value ? 'default' : 'secondary'}
                size="sm"
                className={`filter-btn ${category === tag.value ? 'active' : ''}`}
                onClick={() => setCategory(tag.value)}
              >
                {tag.label}
              </Button>
            ))}
          </nav>
        </div>

        {/* Search Active Indicator */}
        {debouncedSearch.trim() && (
          <div className="search-active-pill fade-in">
            <span>
              Search results for <strong>&ldquo;{debouncedSearch.trim()}&rdquo;</strong>
              {' '}({total} {total === 1 ? 'match' : 'matches'})
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={clearSearch}
              style={{ padding: '2px 8px', fontSize: '12px' }}
            >
              Reset
            </Button>
          </div>
        )}

        {/* ── State: Loading (Skeleton) ── */}
        {loading && <TimelineSkeleton />}

        {/* ── State: Error ── */}
        {!loading && error && (
          <div className="timeline-error-state card">
            <span className="error-icon">⚠️</span>
            <h3>Failed to load updates</h3>
            <p className="error-detail">{error}</p>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={fetchTimeline}
            >
              🔄 Try Again
            </Button>
          </div>
        )}

        {/* ── State: Empty ── */}
        {!loading && !error && changelogs.length === 0 && (
          <div className="timeline-empty-state card">
            <span className="empty-icon">🔍</span>
            <h3>No updates found</h3>
            <p className="empty-text">
              {debouncedSearch.trim()
                ? `No changelog updates matched "${debouncedSearch.trim()}"${category ? ` in category #${category.toLowerCase()}` : ''}.`
                : category
                ? `No published updates categorized under #${category.toLowerCase()}.`
                : 'There are no published updates available yet.'}
            </p>
            {(debouncedSearch.trim() || category) && (
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                {debouncedSearch.trim() && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={clearSearch}
                  >
                    Clear Search
                  </Button>
                )}
                {category && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => setCategory('')}
                  >
                    Clear Category Filter
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── State: Changelog Cards (Reverse Chronological) ── */}
        {!loading && !error && changelogs.length > 0 && (
          <div className="timeline-feed">
            {changelogs.map((item) => (
              <ChangelogCard key={item.id} item={item} />
            ))}
          </div>
        )}

        {/* ── Pagination ── */}
        {!loading && !error && pages > 1 && (
          <nav className="pagination" aria-label="Timeline pagination">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => {
                setPage((p) => p - 1)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
            >
              ← Newer
            </Button>
            <span className="pagination-info">
              Page {page} of {pages} ({total} total)
            </span>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={page >= pages}
              onClick={() => {
                setPage((p) => p + 1)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
            >
              Older →
            </Button>
          </nav>
        )}
      </div>
    </main>
  )
}
