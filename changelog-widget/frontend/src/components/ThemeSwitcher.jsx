/**
 * components/ThemeSwitcher.jsx
 * ─────────────────────────────
 * Multi-option theme switcher:
 * - Light (☀️), Dark (🌙), System (💻)
 * - Auto-detects system color scheme changes when set to System
 * - Syncs both documentElement data-theme and 'dark' CSS class
 * - Persists preference in localStorage ('cw_theme_mode' & 'cw_theme')
 */
import { useState, useEffect } from 'react'
import { Menu, MenuTrigger, MenuPopup, MenuItem } from './ui'

export default function ThemeSwitcher() {
  const [themeMode, setThemeMode] = useState(() => {
    try {
      return localStorage.getItem('cw_theme_mode') || 'system'
    } catch {
      return 'system'
    }
  })

  // Apply theme to document
  useEffect(() => {
    const applyTheme = (mode) => {
      const root = document.documentElement
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      const isDark = mode === 'dark' || (mode === 'system' && prefersDark)

      if (isDark) {
        root.setAttribute('data-theme', 'dark')
        root.classList.add('dark')
        try {
          localStorage.setItem('cw_theme', 'dark')
        } catch {}
      } else {
        root.setAttribute('data-theme', 'light')
        root.classList.remove('dark')
        try {
          localStorage.setItem('cw_theme', 'light')
        } catch {}
      }
    }

    applyTheme(themeMode)
    try {
      localStorage.setItem('cw_theme_mode', themeMode)
    } catch {}

    // Listen for system changes if in system mode
    if (themeMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      const handleChange = () => applyTheme('system')
      mediaQuery.addEventListener('change', handleChange)
      return () => mediaQuery.removeEventListener('change', handleChange)
    }
  }, [themeMode])

  const iconForMode = {
    light: '☀️',
    dark: '🌙',
    system: '💻',
  }

  return (
    <Menu>
      <MenuTrigger
        className="theme-switcher-btn"
        aria-label={`Theme mode: ${themeMode}`}
        title={`Theme: ${themeMode.charAt(0).toUpperCase() + themeMode.slice(1)}`}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '34px',
          height: '34px',
          borderRadius: 'var(--radius-md)',
          background: 'transparent',
          border: '1px solid var(--color-border)',
          color: 'var(--color-text-secondary)',
          cursor: 'pointer',
          fontSize: '14px',
          transition: 'all var(--transition-base)',
        }}
      >
        <span>{iconForMode[themeMode] || '💻'}</span>
      </MenuTrigger>

      <MenuPopup sideOffset={8} style={{ minWidth: '130px', padding: '4px' }}>
        <MenuItem
          onClick={() => setThemeMode('light')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            fontSize: '0.8125rem',
            padding: '6px 10px',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontWeight: themeMode === 'light' ? 600 : 400,
            color: themeMode === 'light' ? 'var(--color-accent)' : 'var(--color-text-primary)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>☀️</span> Light
          </span>
          {themeMode === 'light' && <span style={{ fontSize: '11px' }}>✓</span>}
        </MenuItem>

        <MenuItem
          onClick={() => setThemeMode('dark')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            fontSize: '0.8125rem',
            padding: '6px 10px',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontWeight: themeMode === 'dark' ? 600 : 400,
            color: themeMode === 'dark' ? 'var(--color-accent)' : 'var(--color-text-primary)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>🌙</span> Dark
          </span>
          {themeMode === 'dark' && <span style={{ fontSize: '11px' }}>✓</span>}
        </MenuItem>

        <MenuItem
          onClick={() => setThemeMode('system')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '8px',
            fontSize: '0.8125rem',
            padding: '6px 10px',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontWeight: themeMode === 'system' ? 600 : 400,
            color: themeMode === 'system' ? 'var(--color-accent)' : 'var(--color-text-primary)',
          }}
        >
          <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>💻</span> System
          </span>
          {themeMode === 'system' && <span style={{ fontSize: '11px' }}>✓</span>}
        </MenuItem>
      </MenuPopup>
    </Menu>
  )
}
