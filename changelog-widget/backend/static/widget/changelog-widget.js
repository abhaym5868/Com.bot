/**
 * Changelog & Product Updates — Standalone Embeddable Widget
 * ---------------------------------------------------------
 * Zero-dependency, Shadow-DOM isolated JavaScript widget.
 *
 * Usage:
 * <script
 *   src="https://your-domain.com/static/widget/changelog-widget.js"
 *   data-api="https://your-domain.com"
 *   data-position="bottom-right"
 *   data-theme="auto"
 *   data-accent="#4f6ef7"
 *   data-text="What's New"
 *   defer
 * ></script>
 */

(function () {
  'use strict';

  if (window.__CW_WIDGET_INITIALIZED__) return;
  window.__CW_WIDGET_INITIALIZED__ = true;

  // ── Find Script & Configuration ──────────────────────────────────────────
  const currentScript =
    document.currentScript ||
    document.querySelector('script[src*="changelog-widget.js"]');

  const apiBase = (
    currentScript?.getAttribute('data-api') ||
    window.location.origin
  ).replace(/\/$/, '');

  const position = currentScript?.getAttribute('data-position') || 'bottom-right';
  const themeSetting = currentScript?.getAttribute('data-theme') || 'auto';
  const accentColor = currentScript?.getAttribute('data-accent') || '#4f6ef7';
  const launcherText = currentScript?.getAttribute('data-text') || "What's New";
  const launcherStyle = currentScript?.getAttribute('data-style') || 'pill';
  const borderRadius = currentScript?.getAttribute('data-radius') || '9999';

  // Determine theme
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark =
    themeSetting === 'dark' || (themeSetting === 'auto' && prefersDark);

  // ── State ────────────────────────────────────────────────────────────────
  let isOpen = false;
  let updates = [];
  let unreadCount = 0;
  const STORAGE_KEY = 'cw_last_read_ts';

  function getLastReadTimestamp() {
    try {
      return localStorage.getItem(STORAGE_KEY) || '1970-01-01T00:00:00.000Z';
    } catch {
      return '1970-01-01T00:00:00.000Z';
    }
  }

  function setLastReadTimestamp(ts) {
    try {
      localStorage.setItem(STORAGE_KEY, ts || new Date().toISOString());
    } catch {}
  }

  // ── Shadow DOM Host ───────────────────────────────────────────────────────
  const host = document.createElement('div');
  host.id = 'cw-widget-host';
  document.body.appendChild(host);
  const shadow = host.attachShadow({ mode: 'open' });

  // ── Styles ────────────────────────────────────────────────────────────────
  const style = document.createElement('style');
  style.textContent = `
    :host {
      --cw-accent: ${accentColor};
      --cw-bg: ${isDark ? '#18181b' : '#ffffff'};
      --cw-bg-subtle: ${isDark ? '#27272a' : '#f4f4f5'};
      --cw-border: ${isDark ? '#3f3f46' : '#e4e4e7'};
      --cw-text: ${isDark ? '#f4f4f5' : '#18181b'};
      --cw-text-muted: ${isDark ? '#a1a1aa' : '#71717a'};
      --cw-badge-new-bg: ${isDark ? '#1e3a8a' : '#eff6ff'};
      --cw-badge-new-text: ${isDark ? '#93c5fd' : '#2563eb'};
      --cw-badge-imp-bg: ${isDark ? '#3b1d54' : '#fdf4ff'};
      --cw-badge-imp-text: ${isDark ? '#d8b4fe' : '#9333ea'};
      --cw-badge-fix-bg: ${isDark ? '#27272a' : '#f4f4f5'};
      --cw-badge-fix-text: ${isDark ? '#e4e4e7' : '#52525b'};
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      font-size: 14px;
      color: var(--cw-text);
      z-index: 999999;
      position: relative;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    /* ── Launcher Button ── */
    .cw-launcher {
      position: fixed;
      ${position.includes('left') ? 'left: 20px;' : 'right: 20px;'}
      ${position.includes('top') ? 'top: 20px;' : 'bottom: 20px;'}
      z-index: 999999;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: ${launcherStyle === 'circular' ? '12px' : '10px 18px'};
      border-radius: ${launcherStyle === 'circular' ? '50%' : borderRadius + 'px'};
      background-color: var(--cw-accent);
      color: #ffffff;
      font-size: 14px;
      font-weight: 600;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
      transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s ease;
      user-select: none;
    }
    .cw-launcher:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.28);
    }
    .cw-launcher:active {
      transform: translateY(0);
    }

    .cw-launcher-badge {
      background-color: #ef4444;
      color: #ffffff;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 9999px;
      margin-left: 2px;
      min-width: 18px;
      text-align: center;
    }

    /* ── Backdrop ── */
    .cw-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(2px);
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.25s ease, visibility 0.25s ease;
      z-index: 999998;
    }
    .cw-backdrop.open {
      opacity: 1;
      visibility: visible;
    }

    /* ── Slide Drawer ── */
    .cw-drawer {
      position: fixed;
      top: 0;
      bottom: 0;
      ${position.includes('left') ? 'left: 0;' : 'right: 0;'}
      width: 100%;
      max-width: 440px;
      background-color: var(--cw-bg);
      border-${position.includes('left') ? 'right' : 'left'}: 1px solid var(--cw-border);
      box-shadow: 0 0 30px rgba(0, 0, 0, 0.25);
      z-index: 999999;
      display: flex;
      flex-direction: column;
      transform: translateX(${position.includes('left') ? '-100%' : '100%'});
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .cw-drawer.open {
      transform: translateX(0);
    }

    /* ── Drawer Header ── */
    .cw-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--cw-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--cw-bg);
    }
    .cw-header-title-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .cw-header-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--cw-text);
    }
    .cw-close-btn {
      background: transparent;
      border: none;
      color: var(--cw-text-muted);
      cursor: pointer;
      font-size: 20px;
      width: 32px;
      height: 32px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s ease, color 0.15s ease;
    }
    .cw-close-btn:hover {
      background: var(--cw-bg-subtle);
      color: var(--cw-text);
    }

    /* ── Drawer Content / Feed ── */
    .cw-body {
      flex: 1;
      overflow-y: auto;
      padding: 16px 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .cw-card {
      padding: 16px;
      background: var(--cw-bg-subtle);
      border: 1px solid var(--cw-border);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .cw-card-meta {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    .cw-badge {
      display: inline-block;
      font-size: 11px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
    }
    .cw-badge-new {
      background: var(--cw-badge-new-bg);
      color: var(--cw-badge-new-text);
    }
    .cw-badge-improved {
      background: var(--cw-badge-imp-bg);
      color: var(--cw-badge-imp-text);
    }
    .cw-badge-fixed {
      background: var(--cw-badge-fix-bg);
      color: var(--cw-badge-fix-text);
    }

    .cw-version {
      font-size: 11px;
      font-weight: 600;
      color: var(--cw-accent);
      background: rgba(79, 110, 247, 0.12);
      padding: 2px 6px;
      border-radius: 4px;
    }

    .cw-date {
      font-size: 12px;
      color: var(--cw-text-muted);
    }

    .cw-card-title {
      font-size: 15px;
      font-weight: 600;
      color: var(--cw-text);
      line-height: 1.35;
      text-decoration: none;
    }
    .cw-card-title:hover {
      color: var(--cw-accent);
    }

    .cw-card-cover {
      width: 100%;
      max-height: 160px;
      border-radius: 6px;
      object-fit: cover;
      margin-top: 4px;
    }

    .cw-card-link {
      font-size: 12px;
      font-weight: 600;
      color: var(--cw-accent);
      text-decoration: none;
      align-self: flex-start;
      margin-top: 4px;
    }
    .cw-card-link:hover {
      text-decoration: underline;
    }

    /* ── Empty & Loading ── */
    .cw-empty {
      text-align: center;
      padding: 40px 20px;
      color: var(--cw-text-muted);
    }

    /* ── Footer ── */
    .cw-footer {
      padding: 12px 20px;
      border-top: 1px solid var(--cw-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--cw-bg);
      font-size: 12px;
    }
    .cw-footer-link {
      color: var(--cw-accent);
      text-decoration: none;
      font-weight: 600;
    }
    .cw-mark-read {
      background: transparent;
      border: none;
      color: var(--cw-text-muted);
      cursor: pointer;
      font-size: 12px;
    }
    .cw-mark-read:hover {
      color: var(--cw-text);
      text-decoration: underline;
    }
  `;
  shadow.appendChild(style);

  // ── Render Structure ──
  const container = document.createElement('div');
  container.innerHTML = `
    <button class="cw-launcher" id="cw-launcher-btn" aria-label="Open What's New">
      ${launcherStyle !== 'minimalist' ? '<span>⚡</span>' : ''}
      ${launcherStyle !== 'circular' ? `<span>${launcherText}</span>` : ''}
      <span class="cw-launcher-badge" id="cw-badge" style="display: none;">0</span>
    </button>

    <div class="cw-backdrop" id="cw-backdrop"></div>

    <div class="cw-drawer" id="cw-drawer" role="dialog" aria-modal="true">
      <div class="cw-header">
        <div class="cw-header-title-wrap">
          <span>⚡</span>
          <span class="cw-header-title">What's New</span>
        </div>
        <button class="cw-close-btn" id="cw-close-btn" aria-label="Close">✕</button>
      </div>

      <div class="cw-body" id="cw-body">
        <div class="cw-empty">Loading product updates…</div>
      </div>

      <div class="cw-footer">
        <button class="cw-mark-read" id="cw-mark-read">Mark all as read</button>
        <a class="cw-footer-link" id="cw-full-link" href="#" target="_blank">View full changelog →</a>
      </div>
    </div>
  `;
  shadow.appendChild(container);

  // ── DOM References ──
  const launcherBtn = shadow.getElementById('cw-launcher-btn');
  const badgeEl = shadow.getElementById('cw-badge');
  const backdropEl = shadow.getElementById('cw-backdrop');
  const drawerEl = shadow.getElementById('cw-drawer');
  const closeBtn = shadow.getElementById('cw-close-btn');
  const bodyEl = shadow.getElementById('cw-body');
  const markReadBtn = shadow.getElementById('cw-mark-read');
  const fullLink = shadow.getElementById('cw-full-link');

  fullLink.href = apiBase.includes('8000') ? 'http://localhost:5173/' : apiBase;

  // ── Open / Close Drawer ──
  function toggleDrawer(open) {
    isOpen = open !== undefined ? open : !isOpen;
    if (isOpen) {
      drawerEl.classList.add('open');
      backdropEl.classList.add('open');
      markAllAsRead();
    } else {
      drawerEl.classList.remove('open');
      backdropEl.classList.remove('open');
    }
  }

  function markAllAsRead() {
    if (updates.length > 0) {
      setLastReadTimestamp(updates[0].published_at);
      unreadCount = 0;
      updateBadge();
    }
  }

  function updateBadge() {
    if (unreadCount > 0) {
      badgeEl.textContent = unreadCount > 9 ? '9+' : String(unreadCount);
      badgeEl.style.display = 'inline-block';
    } else {
      badgeEl.style.display = 'none';
    }
  }

  // ── Fetch Updates ──
  async function loadUpdates() {
    try {
      const res = await fetch(`${apiBase}/api/v1/changelog/feed?limit=10`);
      if (!res.ok) throw new Error('Failed to fetch feed');
      const data = await res.json();
      updates = data.updates || [];

      // Calculate unread updates since last read timestamp
      const lastRead = new Date(getLastReadTimestamp());
      unreadCount = updates.filter(
        (u) => u.published_at && new Date(u.published_at) > lastRead
      ).length;
      updateBadge();

      renderUpdates();
    } catch (err) {
      bodyEl.innerHTML = '<div class="cw-empty">Unable to load product updates.</div>';
    }
  }

  function renderUpdates() {
    if (updates.length === 0) {
      bodyEl.innerHTML = '<div class="cw-empty">No product updates published yet.</div>';
      return;
    }

    bodyEl.innerHTML = updates
      .map((item) => {
        const cat = (item.category || 'NEW').toLowerCase();
        const dateStr = item.published_at
          ? new Date(item.published_at).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
            })
          : '';
        const detailUrl = `${fullLink.href}changelog/${item.slug}`;

        return `
          <div class="cw-card">
            <div class="cw-card-meta">
              <div style="display: flex; align-items: center; gap: 6px;">
                <span class="cw-badge cw-badge-${cat}">#${item.category}</span>
                ${item.version ? `<span class="cw-version">${item.version}</span>` : ''}
              </div>
              <span class="cw-date">${dateStr}</span>
            </div>

            <a class="cw-card-title" href="${detailUrl}" target="_blank">
              ${escapeHtml(item.title)}
            </a>

            ${
              item.cover_image
                ? `<img class="cw-card-cover" src="${escapeHtml(item.cover_image)}" alt="" />`
                : ''
            }

            <a class="cw-card-link" href="${detailUrl}" target="_blank">
              Read notes →
            </a>
          </div>
        `;
      })
      .join('');
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ── Event Listeners ──
  launcherBtn.addEventListener('click', () => toggleDrawer(true));
  closeBtn.addEventListener('click', () => toggleDrawer(false));
  backdropEl.addEventListener('click', () => toggleDrawer(false));
  markReadBtn.addEventListener('click', () => {
    markAllAsRead();
    toggleDrawer(false);
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isOpen) {
      toggleDrawer(false);
    }
  });

  // Initial load
  loadUpdates();
})();
