import { useState, useEffect } from 'react'
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import NotificationCenter from './NotificationCenter'
import { Button, Badge, Kbd, Menu, MenuTrigger, MenuPopup, MenuItem, MenuSeparator, Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetBody } from './ui'
import './Navbar.css'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [isMobileOpen, setIsMobileOpen] = useState(false)

  // Global Cmd+K / Ctrl+K search shortcut
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        triggerSearchFocus()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [location.pathname])

  // Close mobile drawer on route change
  useEffect(() => {
    setIsMobileOpen(false)
  }, [location.pathname])

  const triggerSearchFocus = () => {
    if (location.pathname === '/') {
      const el = document.getElementById('timeline-search-input')
      if (el) {
        el.focus()
        el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    } else {
      navigate('/?focus=search')
    }
    setIsMobileOpen(false)
  }

  const handleLogout = async () => {
    setIsMobileOpen(false)
    await logout()
    navigate('/login')
  }

  const avatarInitial = user?.name ? user.name[0].toUpperCase() : 'U'

  return (
    <header className="navbar">
      <div className="navbar-inner">
        {/* Left: Brand Logo & Navigation */}
        <div className="navbar-left">
          <Link to="/" className="navbar-brand" aria-label="Changelog Home">
            <div className="navbar-logo-badge">
              <span className="navbar-logo-icon">⚡</span>
            </div>
            <span className="navbar-logo-text">Changelog</span>
          </Link>

          {/* Navigation Links (Desktop) */}
          <nav className="navbar-nav-links" aria-label="Main Navigation">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `navbar-link ${isActive ? 'navbar-link-active' : ''}`
              }
            >
              Updates
            </NavLink>

            <NavLink
              to="/feed"
              className={({ isActive }) =>
                `navbar-link ${isActive ? 'navbar-link-active' : ''}`
              }
            >
              API
            </NavLink>
          </nav>
        </div>

        {/* Right: Search Pill + Notification Bell + Coss UI Menu Profile */}
        <div className="navbar-right">
          {/* Search Pill */}
          <button
            type="button"
            className="navbar-search-pill"
            onClick={triggerSearchFocus}
            title="Search updates (⌘K)"
            aria-label="Search updates"
          >
            <span className="search-pill-icon">🔍</span>
            <span className="search-pill-text">Search…</span>
            <Kbd className="search-pill-kbd">⌘K</Kbd>
          </button>

          {/* Notification Bell (Preserving What's New logic) */}
          <NotificationCenter />

          {/* User Profile / Auth State using Coss UI Menu */}
          {user ? (
            <Menu>
              <MenuTrigger
                className="navbar-profile-trigger"
                aria-label={`User menu for ${user.name}`}
              >
                <div className="navbar-avatar">
                  {avatarInitial}
                </div>
                <span className="navbar-user-name-short">{user.name}</span>
                <span className="navbar-chevron-icon">▾</span>
              </MenuTrigger>

              <MenuPopup sideOffset={8}>
                <div className="dropdown-user-header">
                  <div className="dropdown-avatar">{avatarInitial}</div>
                  <div className="dropdown-user-details">
                    <div className="dropdown-user-name">{user.name}</div>
                    <div className="dropdown-user-email">{user.email}</div>
                    <Badge variant="default" className="dropdown-role-pill">
                      {isAdmin ? 'ADMINISTRATOR' : 'MEMBER'}
                    </Badge>
                  </div>
                </div>

                <MenuSeparator />

                <MenuItem
                  onClick={() => navigate('/')}
                >
                  <span className="dropdown-item-icon">📰</span>
                  <span>Product Updates</span>
                </MenuItem>

                <MenuItem
                  onClick={() => navigate('/feed')}
                >
                  <span className="dropdown-item-icon">📡</span>
                  <span>Developer API</span>
                </MenuItem>

                {isAdmin && (
                  <MenuItem
                    onClick={() => navigate('/admin')}
                    className="dropdown-item-admin"
                  >
                    <span className="dropdown-item-icon">⚙️</span>
                    <span>Admin Dashboard</span>
                  </MenuItem>
                )}

                <MenuSeparator />

                <MenuItem
                  variant="destructive"
                  onClick={handleLogout}
                >
                  <span className="dropdown-item-icon">🚪</span>
                  <span>Sign out</span>
                </MenuItem>
              </MenuPopup>
            </Menu>
          ) : (
            <div className="navbar-auth-group">
              <Button
                variant="ghost"
                size="sm"
                className="navbar-auth-btn"
                render={<Link to="/login" />}
              >
                Sign in
              </Button>
              <Button
                variant="default"
                size="sm"
                className="navbar-auth-btn"
                render={<Link to="/signup" />}
              >
                Sign up
              </Button>
            </div>
          )}

          {/* Mobile Navigation Drawer using Coss UI Sheet */}
          <Sheet open={isMobileOpen} onOpenChange={setIsMobileOpen}>
            <SheetTrigger
              className="navbar-mobile-toggle"
              aria-label="Toggle navigation menu"
            >
              <span className="mobile-toggle-icon">☰</span>
            </SheetTrigger>

            <SheetContent>
              <SheetHeader>
                <div className="navbar-brand">
                  <div className="navbar-logo-badge">
                    <span className="navbar-logo-icon">⚡</span>
                  </div>
                  <span className="navbar-logo-text">Changelog</span>
                </div>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => setIsMobileOpen(false)}
                  aria-label="Close menu"
                >
                  ✕
                </Button>
              </SheetHeader>

              <SheetBody>
                {/* Mobile Search Button */}
                <div className="mobile-menu-search">
                  <button
                    type="button"
                    className="mobile-search-bar"
                    onClick={triggerSearchFocus}
                  >
                    <span>🔍</span>
                    <span>Search product updates…</span>
                  </button>
                </div>

                {/* Mobile Nav Links */}
                <div className="mobile-nav-links">
                  <NavLink
                    to="/"
                    end
                    className={({ isActive }) =>
                      `mobile-nav-link ${isActive ? 'active' : ''}`
                    }
                    onClick={() => setIsMobileOpen(false)}
                  >
                    <span className="mobile-nav-icon">📰</span>
                    <span>Updates</span>
                  </NavLink>

                  <NavLink
                    to="/feed"
                    className={({ isActive }) =>
                      `mobile-nav-link ${isActive ? 'active' : ''}`
                    }
                    onClick={() => setIsMobileOpen(false)}
                  >
                    <span className="mobile-nav-icon">📡</span>
                    <span>Developer API</span>
                  </NavLink>

                  {isAdmin && (
                    <NavLink
                      to="/admin"
                      className={({ isActive }) =>
                        `mobile-nav-link ${isActive ? 'active' : ''}`
                      }
                      onClick={() => setIsMobileOpen(false)}
                    >
                      <span className="mobile-nav-icon">⚙️</span>
                      <span>Admin Dashboard</span>
                    </NavLink>
                  )}
                </div>

                {/* Mobile User / Auth Footer */}
                <div className="mobile-menu-footer">
                  {user ? (
                    <div className="mobile-user-card">
                      <div className="mobile-user-info">
                        <div className="navbar-avatar">{avatarInitial}</div>
                        <div className="mobile-user-text">
                          <span className="mobile-user-name">{user.name}</span>
                          <span className="mobile-user-email">{user.email}</span>
                          <Badge variant="default" className="w-fit mt-1">
                            {isAdmin ? 'ADMINISTRATOR' : 'MEMBER'}
                          </Badge>
                        </div>
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="mobile-signout-btn"
                        onClick={handleLogout}
                      >
                        Sign out
                      </Button>
                    </div>
                  ) : (
                    <div className="mobile-auth-buttons">
                      <Button
                        variant="secondary"
                        className="w-full"
                        render={<Link to="/login" onClick={() => setIsMobileOpen(false)} />}
                      >
                        Sign in
                      </Button>
                      <Button
                        variant="default"
                        className="w-full"
                        render={<Link to="/signup" onClick={() => setIsMobileOpen(false)} />}
                      >
                        Sign up
                      </Button>
                    </div>
                  )}
                </div>
              </SheetBody>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
