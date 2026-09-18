/**
 * services/notificationService.js
 * ───────────────────────────────
 * API client methods for What's New Notification Center:
 * - getNotifications(limit)
 * - markAsRead()
 */
import api from './api'

export const notificationService = {
  async getNotifications(limit = 5) {
    const res = await api.get('/api/v1/notifications', { params: { limit } })
    return res.data // { unread_count, last_viewed_changelog_date, recent_updates }
  },

  async markAsRead() {
    const res = await api.post('/api/v1/notifications/mark-read')
    return res.data // { unread_count: 0, last_viewed_changelog_date, message }
  },
}

export default notificationService
