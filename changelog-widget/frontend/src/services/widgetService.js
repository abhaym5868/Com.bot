/**
 * services/widgetService.js
 * -------------------------
 * Client for reading and persisting widget studio configuration.
 */
import api from './api'

export const widgetService = {
  async getConfig() {
    const res = await api.get('/api/v1/widget/config')
    return res.data
  },

  async updateConfig(payload) {
    const res = await api.put('/api/v1/widget/config', payload)
    return res.data
  },
}

export default widgetService
