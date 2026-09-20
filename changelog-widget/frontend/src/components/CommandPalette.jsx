import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { changelogService } from '../services/changelogService'
import { useAuth } from '../context/AuthContext'
import { Badge, Kbd } from './ui'
import './CommandPalette.css'

export default function CommandPalette({ isOpen, onClose }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)
  const listRef = useRef(null)
  const navigate = useNavigate()
  const { isAdmin } = useAuth()

  // Static navigation routes
  const navItems = [
    { id: 'nav-updates', title: 'Product Updates Timeline', type: 'page', icon: '📰', path: '/' },
    { id: 'nav-feed', title: 'API & Developer Feed', type: 'page', icon: '📡', path: '/feed' },
    ...(isAdmin
      ? [
          { id: 'nav-admin', title: 'Admin Studio — Manage Changelogs', type: 'page', icon: '⚙️', path: '/admin' },
          { id: 'nav-analytics', title: 'Analytics Dashboard', type: 'page', icon: '📊', path: '/admin/analytics' },
          { id: 'nav-activity', title: 'Activity & Audit Log', type: 'page', icon: '📜', path: '/admin/activity' },
          { id: 'nav-widget', title: 'Widget Studio & Embeds', type: 'page', icon: '🧩', path: '/admin/widget' },
        ]
      : []),
  ]

  // Category shortcuts
  const categoryShortcuts = [
    { id: 'cat-new', title: 'Filter: #New Features', type: 'filter', icon: '✨', path: '/?category=NEW' },
    { id: 'cat-imp', title: 'Filter: #Improvements', type: 'filter', icon: '⚡', path: '/?category=IMPROVED' },
    { id: 'cat-fix', title: 'Filter: #Bug Fixes', type: 'filter', icon: '🛠️', path: '/?category=FIXED' },
  ]

  // Search changelogs when query changes
  useEffect(() => {
    if (!isOpen) return

    let isMounted = true
    if (!query.trim()) {
      setResults([])
      setLoading(false)
      setSelectedIndex(0)
      return
    }

    setLoading(true)
    const timer = setTimeout(async () => {
      try {
        const data = await changelogService.list({ search: query.trim(), limit: 6 })
        if (isMounted) {
          const items = (data.items || []).map((item) => ({
            id: `changelog-${item.id}`,
            title: item.title,
            type: 'changelog',
            category: item.category,
            version: item.version,
            icon: item.category === 'NEW' ? '✨' : item.category === 'IMPROVED' ? '⚡' : '🛠️',
            path: `/?id=${item.id}`,
          }))
          setResults(items)
          setSelectedIndex(0)
        }
      } catch {
        if (isMounted) setResults([])
      } finally {
        if (isMounted) setLoading(false)
      }
    }, 150)

    return () => {
      isMounted = false
      clearTimeout(timer)
    }
  }, [query, isOpen])

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setResults([])
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Active items list: search results or quick links
  const activeList = query.trim()
    ? [
        ...results,
        ...navItems.filter((i) => i.title.toLowerCase().includes(query.toLowerCase())),
        ...categoryShortcuts.filter((i) => i.title.toLowerCase().includes(query.toLowerCase())),
      ]
    : [...navItems, ...categoryShortcuts]

  // Selection navigation handler
  const handleSelect = useCallback(
    (item) => {
      if (!item) return
      onClose()
      navigate(item.path)
    },
    [navigate, onClose]
  )

  // Keyboard navigation inside modal
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex((prev) => (prev + 1 < activeList.length ? prev + 1 : 0))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex((prev) => (prev - 1 >= 0 ? prev - 1 : activeList.length - 1))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (activeList[selectedIndex]) {
          handleSelect(activeList[selectedIndex])
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, activeList, selectedIndex, handleSelect, onClose])

  // Scroll active item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedEl = listRef.current.querySelector('.cmd-item-selected')
      if (selectedEl) {
        selectedEl.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex])

  if (!isOpen) return null

  return (
    <div className="cmd-backdrop" onClick={onClose} role="dialog" aria-modal="true" aria-label="Command search palette">
      <div className="cmd-modal" onClick={(e) => e.stopPropagation()}>
        {/* Search Input Bar */}
        <div className="cmd-input-wrapper">
          <span className="cmd-search-icon">🔍</span>
          <input
            ref={inputRef}
            type="text"
            className="cmd-input"
            placeholder="Type a command, search updates, or jump to page..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {query && (
            <button
              type="button"
              className="cmd-clear-btn"
              onClick={() => setQuery('')}
              aria-label="Clear search"
            >
              ✕
            </button>
          )}
          <Kbd className="cmd-kbd-esc">ESC</Kbd>
        </div>

        {/* Results & Quick Nav List */}
        <div className="cmd-body" ref={listRef}>
          {loading && (
            <div className="cmd-loading">
              <span className="cmd-spinner">◌</span>
              <span>Searching updates...</span>
            </div>
          )}

          {!loading && activeList.length === 0 && (
            <div className="cmd-empty">
              <span>No results found for &ldquo;{query}&rdquo;</span>
            </div>
          )}

          {!loading && activeList.length > 0 && (
            <div className="cmd-group">
              <div className="cmd-group-label">
                {query.trim() ? 'Search Results & Suggestions' : 'Quick Navigation & Shortcuts'}
              </div>
              <ul className="cmd-list">
                {activeList.map((item, index) => {
                  const isSelected = index === selectedIndex
                  return (
                    <li
                      key={item.id}
                      className={`cmd-item ${isSelected ? 'cmd-item-selected' : ''}`}
                      onClick={() => handleSelect(item)}
                      onMouseEnter={() => setSelectedIndex(index)}
                    >
                      <div className="cmd-item-left">
                        <span className="cmd-item-icon">{item.icon}</span>
                        <div className="cmd-item-text">
                          <span className="cmd-item-title">{item.title}</span>
                          {item.version && (
                            <Badge variant="outline" className="cmd-version-badge">
                              {item.version}
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="cmd-item-right">
                        {item.category && (
                          <Badge
                            variant={item.category === 'NEW' ? 'default' : item.category === 'IMPROVED' ? 'secondary' : 'outline'}
                            className="cmd-category-badge"
                          >
                            #{item.category}
                          </Badge>
                        )}
                        <span className="cmd-item-arrow">↵</span>
                      </div>
                    </li>
                  )
                })}
              </ul>
            </div>
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="cmd-footer">
          <div className="cmd-footer-shortcuts">
            <span><Kbd>↑</Kbd> <Kbd>↓</Kbd> Navigate</span>
            <span><Kbd>↵</Kbd> Select</span>
            <span><Kbd>ESC</Kbd> Close</span>
          </div>
          <span className="cmd-footer-brand">Antigravity Changelog</span>
        </div>
      </div>
    </div>
  )
}
