/**
 * services/auditService.js
 * -------------------------
 * API client for fetching admin audit / activity logs.
 */
import api from './api'

export const auditService = {
  async list({ page = 1, limit = 20 } = {}) {
    const res = await api.get('/api/v1/audit', { params: { page, limit } })
    return res.data // { items, total, page, limit, pages }
  },
}

export default auditService
