/**
 * services/authService.js
 * -----------------------
 * Auth API methods wrapping the FastAPI /api/v1/auth/* endpoints.
 */
import api from './api'

export const authService = {
  async signup(name, email, password) {
    const res = await api.post('/api/v1/auth/signup', { name, email, password })
    return res.data
  },

  async login(email, password) {
    const res = await api.post('/api/v1/auth/login', { email, password })
    return res.data
  },

  async logout() {
    const res = await api.post('/api/v1/auth/logout')
    return res.data
  },

  async getMe() {
    const res = await api.get('/api/v1/auth/me')
    return res.data
  },

  async refresh() {
    const res = await api.post('/api/v1/auth/refresh')
    return res.data
  },

  async getCsrf() {
    const res = await api.get('/api/v1/auth/csrf')
    return res.data
  },

  async forgotPassword(email) {
    const res = await api.post('/api/v1/auth/forgot-password', { email })
    return res.data
  },

  async resetPassword(token, newPassword) {
    const res = await api.post('/api/v1/auth/reset-password', { token, new_password: newPassword })
    return res.data
  },

  async verifyEmail(token) {
    const res = await api.post('/api/v1/auth/verify-email', { token })
    return res.data
  },
}

export default authService
