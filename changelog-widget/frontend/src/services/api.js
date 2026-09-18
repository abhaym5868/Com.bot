/**
 * services/api.js
 * ----------------
 * Centralised Axios API client.
 * - Base URL from environment or Vite proxy
 * - withCredentials: true → sends httpOnly cookies on every request
 * - Request interceptor: attaches access_token if stored in localStorage
 *   (used as a fallback for Swagger / mobile clients)
 * - Response interceptor: on 401, attempts silent token refresh once,
 *   then redirects to /login on failure
 */

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,   // Send httpOnly cookies on cross-origin requests
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// ── Request interceptor: attach stored Bearer token (for API clients) ──
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Track if a refresh is already in-flight to avoid concurrent retries ──
let _refreshing = false
let _refreshQueue = []

function processQueue(error) {
  _refreshQueue.forEach((cb) => {
    if (error) cb.reject(error)
    else cb.resolve()
  })
  _refreshQueue = []
}

// ── Response interceptor: 401 → refresh token rotation ──
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Skip refresh for auth endpoints themselves to avoid loops
    const isAuthEndpoint = originalRequest?.url?.includes('/api/v1/auth/')
    if (
      error.response?.status === 401 &&
      !originalRequest._retried &&
      !isAuthEndpoint
    ) {
      if (_refreshing) {
        // Queue request while refresh is in-flight
        return new Promise((resolve, reject) => {
          _refreshQueue.push({ resolve, reject })
        })
          .then(() => api(originalRequest))
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retried = true
      _refreshing = true

      try {
        const res = await api.post('/api/v1/auth/refresh')
        const newToken = res.data?.access_token
        if (newToken) {
          localStorage.setItem('access_token', newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
        localStorage.removeItem('access_token')
        // Redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        return Promise.reject(refreshError)
      } finally {
        _refreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
