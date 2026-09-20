/**
 * services/analyticsService.js
 * -----------------------------
 * API methods for analytics: recording page views and fetching dashboard metrics.
 */
import api from './api'

export const analyticsService = {
  async recordView(changelogId) {
    if (!changelogId) return { recorded: false }
    try {
      const res = await api.post(`/api/v1/analytics/view/${changelogId}`)
      return res.data
    } catch {
      // View recording should never crash the frontend
      return { recorded: false }
    }
  },

  async getDashboard() {
    const res = await api.get('/api/v1/analytics/dashboard')
    return res.data
  },

  async getUpdatePerformance(limit = 20) {
    const res = await api.get('/api/v1/analytics/updates', { params: { limit } })
    return res.data
  },
}

export default analyticsService
