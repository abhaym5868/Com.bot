/**
 * services/changelogService.js
 * ----------------------------
 * Changelog CRUD API methods wrapping /api/v1/changelog/* endpoints.
 */
import api from './api'

export const changelogService = {
  async list({ page = 1, limit = 10, status, category, search } = {}) {
    const params = { page, limit }
    if (status) params.status = status
    if (category) params.category = category
    if (search) params.search = search
    const res = await api.get('/api/v1/changelog', { params })
    return res.data   // { items, total, page, limit, pages }
  },

  async getBySlug(slug) {
    const res = await api.get(`/api/v1/changelog/${slug}`)
    return res.data
  },

  async create(payload) {
    const res = await api.post('/api/v1/changelog', payload)
    return res.data
  },

  async update(id, payload) {
    const res = await api.put(`/api/v1/changelog/${id}`, payload)
    return res.data
  },

  async publish(id) {
    const res = await api.post(`/api/v1/changelog/${id}/publish`)
    return res.data
  },

  async remove(id) {
    const res = await api.delete(`/api/v1/changelog/${id}`)
    return res.data
  },

  async pin(id) {
    const res = await api.post(`/api/v1/changelog/${id}/pin`)
    return res.data
  },

  async unpin(id) {
    const res = await api.post(`/api/v1/changelog/${id}/unpin`)
    return res.data
  },

  async uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/api/v1/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return res.data // { url, filename, size_bytes, content_type }
  },
}

export default changelogService
