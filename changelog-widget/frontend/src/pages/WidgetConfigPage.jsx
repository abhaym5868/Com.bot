/**
 * pages/WidgetConfigPage.jsx
 * ──────────────────────────
 * Widget Studio: Professional Embed & Customization Suite
 * - 6-Tab Customization Panel (General, Appearance, Position, Content, Behavior, Advanced CSS)
 * - Preset Profiles (Minimal, Modern, Professional, Compact, Announcement)
 * - Realistic Customer SaaS Dashboard Live Interactive Preview (Desktop / Tablet / Mobile)
 * - Multi-Framework Snippet Generator (HTML, React, Next.js, Vue)
 * - Persistent Backend Storage via widgetService (/api/v1/widget/config)
 */
import { useState, useEffect } from 'react'
import AdminSidebar from '../components/AdminSidebar'
import { widgetService } from '../services/widgetService'
import { Card, Button, Input, Select, Badge } from '../components/ui'
import './AdminDashboardPage.css'
import './WidgetStudio.css'

const DEFAULT_CONFIG = {
  widget_name: "What's New",
  launcher_text: "What's New",
  launcher_style: 'pill',
  launcher_size: 'md',
  icon: 'sparkle',
  position: 'bottom-right',
  offset_x: 24,
  offset_y: 24,
  theme: 'auto',
  accent_color: '#6366F1',
  border_radius: 12,
  shadow: 'medium',
  animation: 'subtle',
  show_badge: true,
  show_count: true,
  max_notifications: 5,
  title: "What's New",
  subtitle: 'Latest product announcements',
  show_category: true,
  show_date: true,
  show_cover_image: true,
  show_reactions: true,
  show_read_more: true,
  max_visible_updates: 5,
  open_behavior: 'drawer',
  close_on_outside_click: true,
  close_on_esc: true,
  mark_read_on_open: true,
  auto_open: false,
  auto_open_delay: 5,
  custom_css: '',
}

const PRESETS = {
  modern: {
    launcher_style: 'pill',
    launcher_text: "What's New",
    icon: 'sparkle',
    theme: 'auto',
    accent_color: '#6366F1',
    border_radius: 12,
    shadow: 'medium',
    animation: 'subtle',
    open_behavior: 'drawer',
  },
  minimal: {
    launcher_style: 'minimalist',
    launcher_text: 'Updates',
    icon: 'bell',
    theme: 'auto',
    accent_color: '#0F172A',
    border_radius: 6,
    shadow: 'soft',
    animation: 'none',
    open_behavior: 'drawer',
  },
  professional: {
    launcher_style: 'pill',
    launcher_text: 'Release Notes',
    icon: 'megaphone',
    theme: 'light',
    accent_color: '#2563EB',
    border_radius: 8,
    shadow: 'medium',
    animation: 'subtle',
    open_behavior: 'modal',
  },
  compact: {
    launcher_style: 'circular',
    launcher_text: '',
    icon: 'sparkle',
    theme: 'dark',
    accent_color: '#10B981',
    border_radius: 9999,
    shadow: 'elevated',
    animation: 'pulse',
    open_behavior: 'popover',
  },
  announcement: {
    launcher_style: 'badge-only',
    launcher_text: 'NEW UPDATE',
    icon: 'rocket',
    theme: 'auto',
    accent_color: '#F59E0B',
    border_radius: 9999,
    shadow: 'medium',
    animation: 'subtle',
    auto_open: false,
  },
}

export default function WidgetConfigPage() {
  const [config, setConfig] = useState(DEFAULT_CONFIG)
  const [activeTab, setActiveTab] = useState('general')
  const [activePreset, setActivePreset] = useState('modern')
  const [deviceMode, setDeviceMode] = useState('desktop')
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [activeFramework, setActiveFramework] = useState('html')
  const [isSaving, setIsSaving] = useState(false)
  const [savedSuccess, setSavedSuccess] = useState(false)
  const [copied, setCopied] = useState(false)

  // API base URL for script src
  const apiBase = window.location.origin.includes('5173')
    ? 'http://localhost:8000'
    : window.location.origin

  // Fetch initial config from backend
  useEffect(() => {
    let mounted = true
    async function loadConfig() {
      try {
        const data = await widgetService.getConfig()
        if (mounted && data) {
          setConfig((prev) => ({ ...prev, ...data }))
        }
      } catch {
        // Fallback to default config
      }
    }
    loadConfig()
    return () => {
      mounted = false
    }
  }, [])

  const handleChange = (field, value) => {
    setConfig((prev) => ({ ...prev, [field]: value }))
    setActivePreset(null)
  }

  const applyPreset = (key) => {
    if (!PRESETS[key]) return
    setActivePreset(key)
    setConfig((prev) => ({ ...prev, ...PRESETS[key] }))
  }

  const handleReset = () => {
    setConfig(DEFAULT_CONFIG)
    setActivePreset('modern')
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSavedSuccess(false)
    try {
      await widgetService.updateConfig(config)
      setSavedSuccess(true)
      setTimeout(() => setSavedSuccess(false), 3000)
    } catch {
      alert('Failed to save widget configuration. Please check backend connection.')
    } finally {
      setIsSaving(false)
    }
  }

  // Icons map
  const iconEmoji = {
    sparkle: '⚡',
    bell: '🔔',
    megaphone: '📣',
    star: '⭐',
    rocket: '🚀',
  }[config.icon] || '⚡'

  // Code generator snippets
  const getEmbedSnippet = () => {
    if (activeFramework === 'html') {
      return `<!-- Antigravity Changelog Widget -->
<script
  src="${apiBase}/static/widget/changelog-widget.js"
  data-api="${apiBase}"
  data-position="${config.position}"
  data-theme="${config.theme}"
  data-accent="${config.accent_color}"
  data-text="${config.launcher_text}"
  data-style="${config.launcher_style}"
  data-radius="${config.border_radius}"
  defer
></script>`
    }

    if (activeFramework === 'react') {
      return `import { useEffect } from 'react';

export function ChangelogWidget() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '${apiBase}/static/widget/changelog-widget.js';
    script.setAttribute('data-api', '${apiBase}');
    script.setAttribute('data-position', '${config.position}');
    script.setAttribute('data-theme', '${config.theme}');
    script.setAttribute('data-accent', '${config.accent_color}');
    script.setAttribute('data-text', '${config.launcher_text}');
    script.defer = true;
    document.body.appendChild(script);

    return () => {
      document.getElementById('cw-widget-host')?.remove();
    };
  }, []);

  return null;
}`
    }

    if (activeFramework === 'nextjs') {
      return `import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Script
          src="${apiBase}/static/widget/changelog-widget.js"
          data-api="${apiBase}"
          data-position="${config.position}"
          data-theme="${config.theme}"
          data-accent="${config.accent_color}"
          data-text="${config.launcher_text}"
          strategy="lazyOnload"
        />
      </body>
    </html>
  );
}`
    }

    if (activeFramework === 'vue') {
      return `<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  const script = document.createElement('script');
  script.src = '${apiBase}/static/widget/changelog-widget.js';
  script.setAttribute('data-api', '${apiBase}');
  script.setAttribute('data-position', '${config.position}');
  script.setAttribute('data-theme', '${config.theme}');
  script.setAttribute('data-accent', '${config.accent_color}');
  script.setAttribute('data-text', '${config.launcher_text}');
  script.defer = true;
  document.body.appendChild(script);
});
</script>`
    }
  }

  const handleCopyCode = () => {
    navigator.clipboard.writeText(getEmbedSnippet())
    setCopied(true)
    setTimeout(() => setCopied(false), 2500)
  }

  // Device width calculation
  const deviceWidth =
    deviceMode === 'desktop' ? '100%' : deviceMode === 'tablet' ? '640px' : '360px'

  // Shadow calculation for preview
  const shadowStyles = {
    none: 'none',
    soft: '0 2px 8px rgba(0, 0, 0, 0.1)',
    medium: '0 4px 16px rgba(0, 0, 0, 0.18)',
    elevated: '0 8px 28px rgba(0, 0, 0, 0.28)',
  }[config.shadow] || '0 4px 16px rgba(0, 0, 0, 0.18)'

  // Mock demo changelog items
  const mockUpdates = [
    {
      id: 1,
      title: 'Real-time Analytics 2.0',
      category: 'NEW',
      date: 'Today',
      summary: 'Track live events and reader retention with 60fps graphs.',
    },
    {
      id: 2,
      title: 'Command Palette (⌘K) & Keyboard Shortcuts',
      category: 'IMPROVED',
      date: 'Yesterday',
      summary: 'Instantly jump across all updates and admin views.',
    },
    {
      id: 3,
      title: 'Resolved OAuth Token Refresh Timing Bug',
      category: 'FIXED',
      date: '3 days ago',
      summary: 'Prevented premature session logouts during long edits.',
    },
  ]

  return (
    <div className="admin-layout">
      <AdminSidebar />

      <main className="admin-content">
        {/* Header Bar */}
        <div className="admin-header-bar">
          <div>
            <h1 className="admin-page-title">Widget Studio</h1>
            <p className="admin-page-subtitle">
              Design, customize, and embed a live &ldquo;What&rsquo;s New&rdquo; drawer onto your SaaS product.
            </p>
          </div>
          <div className="admin-header-actions">
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
            >
              ↺ Reset
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={handleSave}
              disabled={isSaving}
            >
              {isSaving ? 'Saving…' : savedSuccess ? 'Saved ✓' : 'Save Configuration'}
            </Button>
          </div>
        </div>

        <div className="studio-container">
          {/* Top Presets Bar */}
          <div className="studio-presets-bar">
            <div className="presets-left">
              <span className="presets-label">Presets:</span>
              {Object.keys(PRESETS).map((key) => (
                <button
                  key={key}
                  type="button"
                  className={`preset-chip ${activePreset === key ? 'active' : ''}`}
                  onClick={() => applyPreset(key)}
                >
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </button>
              ))}
            </div>

            <div className="presets-right">
              {savedSuccess && (
                <Badge variant="default" style={{ background: 'var(--color-success)', color: '#fff' }}>
                  Configuration Saved to Cloud!
                </Badge>
              )}
            </div>
          </div>

          {/* Two-Column Workspace: Config Panel (Left) & Live Preview + Code (Right) */}
          <div className="studio-grid">
            {/* Left: 6-Tab Configuration Panel */}
            <div className="studio-config-panel">
              <div className="studio-tabs-header">
                {[
                  { id: 'general', label: 'General' },
                  { id: 'appearance', label: 'Appearance' },
                  { id: 'position', label: 'Position' },
                  { id: 'content', label: 'Content' },
                  { id: 'behavior', label: 'Behavior' },
                  { id: 'advanced', label: 'Custom CSS' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    className={`studio-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab 1: General */}
              {activeTab === 'general' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Widget Name</label>
                    <Input
                      value={config.widget_name}
                      onChange={(e) => handleChange('widget_name', e.target.value)}
                      placeholder="e.g. Acme Product Updates"
                    />
                    <span className="config-hint">Internal identifier for this widget setup.</span>
                  </div>

                  <div className="config-field">
                    <label className="config-label">Launcher Text</label>
                    <Input
                      value={config.launcher_text}
                      onChange={(e) => handleChange('launcher_text', e.target.value)}
                      placeholder="e.g. What's New"
                    />
                  </div>

                  <div className="config-field">
                    <label className="config-label">Launcher Style</label>
                    <Select
                      value={config.launcher_style}
                      onChange={(e) => handleChange('launcher_style', e.target.value)}
                    >
                      <option value="pill">Pill (Icon + Text + Badge)</option>
                      <option value="circular">Circular (Icon Only)</option>
                      <option value="minimalist">Minimalist (Text Only)</option>
                      <option value="badge-only">Badge Only (Subtle)</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <label className="config-label">Launcher Size</label>
                    <Select
                      value={config.launcher_size}
                      onChange={(e) => handleChange('launcher_size', e.target.value)}
                    >
                      <option value="sm">Small (Compact)</option>
                      <option value="md">Medium (Standard)</option>
                      <option value="lg">Large (Prominent)</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <label className="config-label">Launcher Icon</label>
                    <div className="icon-select-grid">
                      {[
                        { id: 'sparkle', label: 'Sparkle', emoji: '⚡' },
                        { id: 'bell', label: 'Bell', emoji: '🔔' },
                        { id: 'megaphone', label: 'Megaphone', emoji: '📣' },
                        { id: 'star', label: 'Star', emoji: '⭐' },
                        { id: 'rocket', label: 'Rocket', emoji: '🚀' },
                      ].map((item) => (
                        <button
                          key={item.id}
                          type="button"
                          className={`icon-select-btn ${config.icon === item.id ? 'active' : ''}`}
                          onClick={() => handleChange('icon', item.id)}
                        >
                          <span>{item.emoji}</span>
                          <span className="icon-select-name">{item.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Appearance */}
              {activeTab === 'appearance' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Theme Mode</label>
                    <Select
                      value={config.theme}
                      onChange={(e) => handleChange('theme', e.target.value)}
                    >
                      <option value="auto">Auto (Matches User System Scheme)</option>
                      <option value="light">Force Light Theme</option>
                      <option value="dark">Force Dark Theme</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <label className="config-label">Brand Accent Color</label>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <input
                        type="color"
                        value={config.accent_color}
                        onChange={(e) => handleChange('accent_color', e.target.value)}
                        style={{
                          width: '42px',
                          height: '38px',
                          border: '1px solid var(--color-border)',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          background: 'none',
                        }}
                      />
                      <Input
                        value={config.accent_color}
                        onChange={(e) => handleChange('accent_color', e.target.value)}
                        style={{ fontFamily: 'monospace' }}
                      />
                    </div>
                    {/* Quick Swatches */}
                    <div className="swatches-grid">
                      {['#6366F1', '#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#0F172A'].map((hex) => (
                        <button
                          key={hex}
                          type="button"
                          className={`swatch-btn ${config.accent_color === hex ? 'active' : ''}`}
                          style={{ backgroundColor: hex }}
                          onClick={() => handleChange('accent_color', hex)}
                          title={hex}
                        />
                      ))}
                    </div>
                  </div>

                  <div className="config-field">
                    <div className="config-label">
                      <span>Border Radius</span>
                      <span style={{ fontFamily: 'monospace' }}>{config.border_radius}px</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="24"
                      value={config.border_radius}
                      onChange={(e) => handleChange('border_radius', parseInt(e.target.value, 10))}
                      style={{ width: '100%', cursor: 'pointer' }}
                    />
                  </div>

                  <div className="config-field">
                    <label className="config-label">Box Shadow Depth</label>
                    <Select
                      value={config.shadow}
                      onChange={(e) => handleChange('shadow', e.target.value)}
                    >
                      <option value="none">None (Flat)</option>
                      <option value="soft">Soft & Subtle</option>
                      <option value="medium">Medium (Realistic)</option>
                      <option value="elevated">Elevated (Deep)</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <label className="config-label">Hover Animation</label>
                    <Select
                      value={config.animation}
                      onChange={(e) => handleChange('animation', e.target.value)}
                    >
                      <option value="none">None</option>
                      <option value="subtle">Subtle Lift</option>
                      <option value="pulse">Soft Pulse</option>
                      <option value="bounce">Subtle Bounce</option>
                    </Select>
                  </div>
                </div>
              )}

              {/* Tab 3: Position */}
              {activeTab === 'position' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Screen Anchor Position</label>
                    <Select
                      value={config.position}
                      onChange={(e) => handleChange('position', e.target.value)}
                    >
                      <option value="bottom-right">Bottom Right (Recommended)</option>
                      <option value="bottom-left">Bottom Left</option>
                      <option value="top-right">Top Right</option>
                      <option value="top-left">Top Left</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <div className="config-label">
                      <span>Horizontal Offset</span>
                      <span style={{ fontFamily: 'monospace' }}>{config.offset_x}px</span>
                    </div>
                    <input
                      type="range"
                      min="8"
                      max="80"
                      value={config.offset_x}
                      onChange={(e) => handleChange('offset_x', parseInt(e.target.value, 10))}
                      style={{ width: '100%', cursor: 'pointer' }}
                    />
                  </div>

                  <div className="config-field">
                    <div className="config-label">
                      <span>Vertical Offset</span>
                      <span style={{ fontFamily: 'monospace' }}>{config.offset_y}px</span>
                    </div>
                    <input
                      type="range"
                      min="8"
                      max="80"
                      value={config.offset_y}
                      onChange={(e) => handleChange('offset_y', parseInt(e.target.value, 10))}
                      style={{ width: '100%', cursor: 'pointer' }}
                    />
                  </div>
                </div>
              )}

              {/* Tab 4: Content */}
              {activeTab === 'content' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Drawer Title</label>
                    <Input
                      value={config.title}
                      onChange={(e) => handleChange('title', e.target.value)}
                      placeholder="What's New"
                    />
                  </div>

                  <div className="config-field">
                    <label className="config-label">Drawer Subtitle</label>
                    <Input
                      value={config.subtitle}
                      onChange={(e) => handleChange('subtitle', e.target.value)}
                      placeholder="Latest product announcements"
                    />
                  </div>

                  <div className="config-field">
                    <label className="config-label">Max Visible Updates</label>
                    <Select
                      value={config.max_visible_updates}
                      onChange={(e) => handleChange('max_visible_updates', parseInt(e.target.value, 10))}
                    >
                      <option value="3">3 Recent Updates</option>
                      <option value="5">5 Recent Updates</option>
                      <option value="10">10 Recent Updates</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <label className="config-label" style={{ marginBottom: '8px' }}>Content Display Elements</label>
                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Category Tag Badge</span>
                        <span className="switch-subtitle">Displays #New, #Improved, or #Fixed</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.show_category}
                        onChange={(e) => handleChange('show_category', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Publication Date</span>
                        <span className="switch-subtitle">Displays formatted release date</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.show_date}
                        onChange={(e) => handleChange('show_date', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Interactive Reactions</span>
                        <span className="switch-subtitle">Allow readers to react with ❤️ 🎉 🚀</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.show_reactions}
                        onChange={(e) => handleChange('show_reactions', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Read Full Update Link</span>
                        <span className="switch-subtitle">Links directly to the changelog permalink</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.show_read_more}
                        onChange={(e) => handleChange('show_read_more', e.target.checked)}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: Behavior */}
              {activeTab === 'behavior' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Display Mode</label>
                    <Select
                      value={config.open_behavior}
                      onChange={(e) => handleChange('open_behavior', e.target.value)}
                    >
                      <option value="drawer">Slide-over Drawer (Right Side)</option>
                      <option value="modal">Centered Modal Dialog</option>
                      <option value="popover">Floating Anchor Popover</option>
                    </Select>
                  </div>

                  <div className="config-field">
                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Unread Counter Pill</span>
                        <span className="switch-subtitle">Show numeric badge when new updates exist</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.show_badge}
                        onChange={(e) => handleChange('show_badge', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Close on Outside Click</span>
                        <span className="switch-subtitle">Dismiss when clicking away</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.close_on_outside_click}
                        onChange={(e) => handleChange('close_on_outside_click', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Close on ESC Key</span>
                        <span className="switch-subtitle">Dismiss when pressing escape</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.close_on_esc}
                        onChange={(e) => handleChange('close_on_esc', e.target.checked)}
                      />
                    </div>

                    <div className="config-switch-row">
                      <div className="config-switch-text">
                        <span className="switch-title">Mark Read on Open</span>
                        <span className="switch-subtitle">Clears unread badge once opened</span>
                      </div>
                      <input
                        type="checkbox"
                        checked={config.mark_read_on_open}
                        onChange={(e) => handleChange('mark_read_on_open', e.target.checked)}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 6: Custom CSS */}
              {activeTab === 'advanced' && (
                <div className="studio-tab-content fade-in">
                  <div className="config-field">
                    <label className="config-label">Scoped Shadow DOM CSS</label>
                    <textarea
                      rows={12}
                      value={config.custom_css}
                      onChange={(e) => handleChange('custom_css', e.target.value)}
                      placeholder={`/* Custom widget overrides */\n.cw-launcher {\n  letter-spacing: 0.05em;\n}\n.cw-drawer {\n  backdrop-filter: blur(12px);\n}`}
                      style={{
                        width: '100%',
                        fontFamily: 'var(--font-mono)',
                        fontSize: '0.8125rem',
                        padding: '12px',
                        background: 'var(--color-bg)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 'var(--radius-md)',
                        color: 'var(--color-text-primary)',
                      }}
                    />
                    <span className="config-hint">
                      Applied inside the widget&apos;s isolated Shadow DOM root.
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Right: Customer SaaS Dashboard Live Interactive Preview & Embed Snippet */}
            <div className="studio-preview-column">
              {/* Preview Card */}
              <div className="preview-canvas-card">
                <div className="preview-top-toolbar">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                      Live Interactive Preview
                    </span>
                    <Badge variant="outline" style={{ fontSize: '0.6875rem' }}>
                      Click Widget to Toggle Drawer
                    </Badge>
                  </div>

                  <div className="device-switcher">
                    {[
                      { id: 'desktop', label: '🖥️ Desktop' },
                      { id: 'tablet', label: '📱 Tablet' },
                      { id: 'mobile', label: '📲 Mobile' },
                    ].map((dev) => (
                      <button
                        key={dev.id}
                        type="button"
                        className={`device-btn ${deviceMode === dev.id ? 'active' : ''}`}
                        onClick={() => setDeviceMode(dev.id)}
                      >
                        {dev.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Simulated Customer App Viewport */}
                <div className="preview-viewport-wrap">
                  <div
                    className={`mock-app-window ${config.theme === 'dark' ? 'theme-dark' : ''}`}
                    style={{ width: deviceWidth }}
                  >
                    {/* Mock App Header */}
                    <div className="mock-app-header">
                      <div className="mock-header-brand">
                        <div className="mock-header-pill" style={{ background: config.accent_color }} />
                        <span>Acme SaaS Dashboard</span>
                      </div>
                      <div className="mock-header-user">
                        <div className="mock-avatar" />
                      </div>
                    </div>

                    {/* Mock App Body */}
                    <div className="mock-app-body">
                      {deviceMode !== 'mobile' && (
                        <div className="mock-app-sidebar">
                          <div className="mock-nav-item active" style={{ background: config.accent_color }} />
                          <div className="mock-nav-item" />
                          <div className="mock-nav-item" />
                          <div className="mock-nav-item" />
                        </div>
                      )}

                      <div className="mock-app-content">
                        <div className="mock-stats-row">
                          <div className="mock-stat-box">
                            <span className="mock-stat-title">Monthly Revenue</span>
                            <strong className="mock-stat-num">$48,250</strong>
                          </div>
                          <div className="mock-stat-box">
                            <span className="mock-stat-title">Active Users</span>
                            <strong className="mock-stat-num">1,842</strong>
                          </div>
                          <div className="mock-stat-box">
                            <span className="mock-stat-title">Uptime</span>
                            <strong className="mock-stat-num">99.98%</strong>
                          </div>
                        </div>

                        <div className="mock-table">
                          <div className="mock-table-row" style={{ width: '70%' }} />
                          <div className="mock-table-row" style={{ width: '90%' }} />
                          <div className="mock-table-row" style={{ width: '60%' }} />
                          <div className="mock-table-row" style={{ width: '85%' }} />
                        </div>
                      </div>

                      {/* Live Simulated Widget Launcher inside Mock App */}
                      <button
                        type="button"
                        className="mock-widget-launcher"
                        onClick={() => setIsDrawerOpen((prev) => !prev)}
                        style={{
                          [config.position.includes('bottom') ? 'bottom' : 'top']: `${Math.min(config.offset_y, 40)}px`,
                          [config.position.includes('right') ? 'right' : 'left']: `${Math.min(config.offset_x, 40)}px`,
                          backgroundColor: config.accent_color,
                          color: '#ffffff',
                          borderRadius:
                            config.launcher_style === 'circular'
                              ? '50%'
                              : `${config.border_radius}px`,
                          padding:
                            config.launcher_style === 'circular'
                              ? '10px'
                              : config.launcher_size === 'sm'
                              ? '6px 12px'
                              : config.launcher_size === 'lg'
                              ? '12px 20px'
                              : '8px 16px',
                          border: 'none',
                          boxShadow: shadowStyles,
                          fontSize: config.launcher_size === 'sm' ? '0.75rem' : '0.875rem',
                          fontWeight: 600,
                        }}
                      >
                        {config.launcher_style !== 'minimalist' && <span>{iconEmoji}</span>}
                        {config.launcher_style !== 'circular' && (
                          <span>{config.launcher_text || "What's New"}</span>
                        )}
                        {config.show_badge && (
                          <span className="mock-widget-badge">2</span>
                        )}
                      </button>

                      {/* Live Opened Changelog Drawer inside Mock App */}
                      {isDrawerOpen && (
                        <div className="mock-widget-drawer">
                          <div className="mock-drawer-header">
                            <div>
                              <div>{config.title || "What's New"}</div>
                              <div style={{ fontSize: '0.6875rem', opacity: 0.7, fontWeight: 400 }}>
                                {config.subtitle}
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="icon-sm"
                              onClick={() => setIsDrawerOpen(false)}
                            >
                              ✕
                            </Button>
                          </div>

                          <div className="mock-drawer-body">
                            {mockUpdates.slice(0, config.max_visible_updates).map((item) => (
                              <div key={item.id} className="mock-update-card">
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  {config.show_category && (
                                    <Badge
                                      variant={item.category === 'NEW' ? 'default' : 'secondary'}
                                      style={{ fontSize: '0.625rem', padding: '1px 5px' }}
                                    >
                                      #{item.category}
                                    </Badge>
                                  )}
                                  {config.show_date && (
                                    <span style={{ fontSize: '0.6875rem', opacity: 0.6 }}>{item.date}</span>
                                  )}
                                </div>
                                <span style={{ fontSize: '0.75rem', fontWeight: 600 }}>{item.title}</span>
                                <p style={{ fontSize: '0.6875rem', opacity: 0.8, margin: 0 }}>{item.summary}</p>
                                {config.show_reactions && (
                                  <div style={{ display: 'flex', gap: '4px', marginTop: '4px' }}>
                                    <span style={{ fontSize: '0.6875rem' }}>❤️ 12</span>
                                    <span style={{ fontSize: '0.6875rem' }}>🚀 8</span>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Multi-Framework Embed Code Snippet */}
              <div className="embed-code-card">
                <div className="embed-tabs-bar">
                  <div className="embed-tabs-list">
                    {[
                      { id: 'html', label: 'HTML / Script' },
                      { id: 'react', label: 'React' },
                      { id: 'nextjs', label: 'Next.js' },
                      { id: 'vue', label: 'Vue 3' },
                    ].map((fw) => (
                      <button
                        key={fw.id}
                        type="button"
                        className={`embed-tab-btn ${activeFramework === fw.id ? 'active' : ''}`}
                        onClick={() => setActiveFramework(fw.id)}
                      >
                        {fw.label}
                      </button>
                    ))}
                  </div>

                  <Button
                    variant="default"
                    size="sm"
                    onClick={handleCopyCode}
                  >
                    {copied ? '✅ Copied to Clipboard!' : '📋 Copy Code'}
                  </Button>
                </div>

                <pre className="embed-snippet-pre">{getEmbedSnippet()}</pre>

                {/* 3-Step Installation Guide */}
                <div className="install-steps-grid">
                  <div className="install-step-card">
                    <div className="step-number">1</div>
                    <div className="step-body">
                      <span className="step-title">Copy Snippet</span>
                      <span className="step-desc">Select your frontend framework and copy the code snippet above.</span>
                    </div>
                  </div>

                  <div className="install-step-card">
                    <div className="step-number">2</div>
                    <div className="step-body">
                      <span className="step-title">Paste in Template</span>
                      <span className="step-desc">Insert the script before &lt;/body&gt; or in your root application layout.</span>
                    </div>
                  </div>

                  <div className="install-step-card">
                    <div className="step-number">3</div>
                    <div className="step-body">
                      <span className="step-title">Auto Updates</span>
                      <span className="step-desc">Whenever you publish a release, the badge will update automatically!</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
