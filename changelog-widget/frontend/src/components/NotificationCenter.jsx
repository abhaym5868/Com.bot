import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { notificationService } from '../services/notificationService'
import { Button, Badge, Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetBody } from './ui'
import './NotificationCenter.css'

export default function NotificationCenter() {
  const { user } = useAuth()
  const [isOpen, setIsOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [recentUpdates, setRecentUpdates] = useState([])
  const [loading, setLoading] = useState(false)

  // Fetch unread count & recent updates
  const fetchNotifications = useCallback(async () => {
    setLoading(true)
    try {
      const data = await notificationService.getNotifications(6)
      setUnreadCount(data.unread_count || 0)
      setRecentUpdates(data.recent_updates || [])
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchNotifications()
    // Poll periodically every 45s for fresh updates
    const interval = setInterval(fetchNotifications, 45000)
    return () => clearInterval(interval)
  }, [fetchNotifications, user])

  // When drawer opens, mark notifications as read if authenticated
  const handleOpenDrawer = async () => {
    setIsOpen(true)
    if (user && unreadCount > 0) {
      try {
        await notificationService.markAsRead()
        setUnreadCount(0)
      } catch {
        // Silently continue
      }
    }
  }

  const handleCloseDrawer = () => {
    setIsOpen(false)
  }

  return (
    <>
      {/* Header Bell Trigger Button */}
      <button
        type="button"
        className={`notif-trigger-btn ${unreadCount > 0 ? 'notif-trigger-pill' : ''}`}
        onClick={handleOpenDrawer}
        aria-label={`What's New notifications, ${unreadCount} unread`}
        title="What's New"
      >
        <span className="notif-bell-icon">🔔</span>
        {unreadCount > 0 && (
          <span className="notif-pill-count">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Slide-over Drawer using Coss UI Sheet */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent>
          <SheetHeader>
            <div className="notif-drawer-title-group">
              <span className="notif-header-icon">✨</span>
              <div>
                <SheetTitle>What&apos;s New</SheetTitle>
                <SheetDescription>Latest product announcements</SheetDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              className="notif-close-btn"
              onClick={handleCloseDrawer}
              aria-label="Close drawer"
            >
              ✕
            </Button>
          </SheetHeader>

          <SheetBody>
            {loading && recentUpdates.length === 0 ? (
              <div className="notif-empty-state">
                <span className="notif-empty-icon">⏳</span>
                <h3>Loading...</h3>
                <p>Fetching the latest product updates for you.</p>
              </div>
            ) : recentUpdates.length === 0 ? (
              <div className="notif-empty-state">
                <span className="notif-empty-icon">🎉</span>
                <h3>You&apos;re all caught up!</h3>
                <p>No new updates announced yet. Check back soon for exciting releases.</p>
              </div>
            ) : (
              <div className="notif-updates-list">
                {recentUpdates.map((item) => {
                  const formattedDate = item.published_at
                    ? new Date(item.published_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                      })
                    : ''

                  const excerpt = item.content_markdown
                    ? item.content_markdown
                        .replace(/[#*`_~]/g, '')
                        .slice(0, 100) + (item.content_markdown.length > 100 ? '…' : '')
                    : ''

                  const categoryVariant =
                    item.category === 'NEW'
                      ? 'success'
                      : item.category === 'FIXED'
                      ? 'warning'
                      : 'default'

                  return (
                    <article key={item.id} className="notif-card">
                      <div className="notif-card-meta">
                        <Badge variant={categoryVariant} className="notif-card-tag">
                          #{item.category || 'NEW'}
                        </Badge>
                        {formattedDate && (
                          <span className="notif-card-date">{formattedDate}</span>
                        )}
                      </div>

                      <h4 className="notif-card-title">
                        <Link
                          to={`/changelog/${item.slug}`}
                          onClick={handleCloseDrawer}
                        >
                          {item.title}
                        </Link>
                      </h4>

                      {excerpt && <p className="notif-card-excerpt">{excerpt}</p>}

                      <Link
                        to={`/changelog/${item.slug}`}
                        className="notif-card-readmore"
                        onClick={handleCloseDrawer}
                      >
                        Read full update →
                      </Link>
                    </article>
                  )
                })}
              </div>
            )}
          </SheetBody>

          <div className="notif-drawer-footer">
            <Button
              variant="secondary"
              size="sm"
              className="notif-view-all-btn w-full"
              render={<Link to="/" onClick={handleCloseDrawer} />}
            >
              View Full Timeline
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}
