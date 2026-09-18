/**
 * services/authService.js
 * -----------------------
 * Auth API methods wrapping the FastAPI /api/v1/auth/* endpoints.
 */
import api from './api'

export const authService = {
  async signup(name, email, password) {
    const res = await api.post('/api/v1/auth/signup', { name, email, password })
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token)
    }
    return res.data
  },

  async login(email, password) {
    const res = await api.post('/api/v1/auth/login', { email, password })
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token)
    }
    return res.data
  },

  async logout(refreshToken) {
    try {
      await api.post('/api/v1/auth/logout', { refresh_token: refreshToken })
    } finally {
      localStorage.removeItem('access_token')
    }
  },

  async getMe() {
    const res = await api.get('/api/v1/auth/me')
    return res.data
  },

  async refresh(refreshToken) {
    const res = await api.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token)
    }
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
