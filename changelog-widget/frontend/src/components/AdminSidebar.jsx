/**
 * components/AdminSidebar.jsx
 * ────────────────────────────
 * Unified collapsible sidebar for all admin views:
 * - Updates / Markdown Studio (/admin)
 * - Analytics Dashboard (/admin/analytics)
 * - Activity Log (/admin/activity)
 * - Widget Studio (/admin/widget)
 * Supports collapsing with localStorage persistence.
 */
import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from './ui'

export default function AdminSidebar({ children }) {
  const { user, logout } = useAuth()
  const [isCollapsed, setIsCollapsed] = useState(() => {
    try {
      return localStorage.getItem('cw_admin_sidebar_collapsed') === 'true'
    } catch {
      return false
    }
  })

  const toggleCollapse = () => {
    setIsCollapsed((prev) => {
      const next = !prev
      try {
        localStorage.setItem('cw_admin_sidebar_collapsed', String(next))
      } catch {}
      return next
    })
  }

  const navItems = [
    { label: 'Updates', icon: '📋', path: '/admin', end: true },
    { label: 'Analytics', icon: '📊', path: '/admin/analytics', end: false },
    { label: 'Activity Log', icon: '📜', path: '/admin/activity', end: false },
    { label: 'Widget Studio', icon: '🧩', path: '/admin/widget', end: false },
  ]

  const userInitial = user?.name ? user.name.charAt(0).toUpperCase() : 'A'

  return (
    <aside
      className={`admin-sidebar ${isCollapsed ? 'admin-sidebar-collapsed' : ''}`}
      aria-label="Admin Navigation"
    >
      <div className="admin-sidebar-header">
        <div className="sidebar-brand-group">
          <span className="sidebar-logo">⚡</span>
          {!isCollapsed && (
            <div className="sidebar-title-group">
              <h3 className="sidebar-title">Admin Studio</h3>
              <p className="sidebar-subtitle">Product Changelogs</p>
            </div>
          )}
        </div>
        <button
          type="button"
          className="sidebar-collapse-btn"
          onClick={toggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '»' : '«'}
        </button>
      </div>

      <nav className="admin-sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            title={isCollapsed ? item.label : undefined}
            className={({ isActive }) =>
              `sidebar-nav-item ${isActive ? 'active' : ''} ${isCollapsed ? 'collapsed' : ''}`
            }
          >
            <span className="sidebar-nav-icon">{item.icon}</span>
            {!isCollapsed && <span className="sidebar-nav-label">{item.label}</span>}
          </NavLink>
        ))}

        {children && !isCollapsed && (
          <div className="sidebar-extra-children">
            {children}
          </div>
        )}
      </nav>

      <div className="admin-sidebar-footer">
        <div className="admin-user-info" title={isCollapsed ? `${user?.name} (${user?.email})` : undefined}>
          <span className="user-avatar">{userInitial}</span>
          {!isCollapsed && (
            <div className="user-details">
              <span className="user-name">{user?.name || 'Administrator'}</span>
              <span className="user-role">Role: {user?.role || 'admin'}</span>
            </div>
          )}
        </div>
        <Button
          variant="ghost"
          size={isCollapsed ? 'icon-sm' : 'sm'}
          onClick={logout}
          title="Sign out"
          className="sidebar-logout-btn"
        >
          <span>🚪</span>
          {!isCollapsed && <span>Logout</span>}
        </Button>
      </div>
    </aside>
  )
}
