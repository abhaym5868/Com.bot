/**
 * services/api.js
 * ----------------
 * Centralised Axios API client.
 * - Base URL from environment or Vite proxy
 * - withCredentials: true → sends httpOnly cookies on every request
 * - Request interceptor: attaches X-CSRF-Token from cookie for state-changing requests
 * - Response interceptor: on 401, attempts silent token refresh once via httpOnly refresh cookie
 */

import axios from 'axios'

// In development with Vite proxy, use relative path so cookies are same-origin on localhost
const BASE_URL = import.meta.env.DEV ? '' : (import.meta.env.VITE_API_BASE_URL || '')

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,   // Send httpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Helper to read cookie by name
function getCookie(name) {
  if (typeof document === 'undefined') return null
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

// ── Request interceptor: attach X-CSRF-Token for state-changing methods ──
api.interceptors.request.use(
  (config) => {
    const method = (config.method || '').toLowerCase()
    if (['post', 'put', 'patch', 'delete'].includes(method)) {
      const csrfToken = getCookie('csrf_token')
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
      }
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

    // Skip refresh for auth endpoints that cannot be refreshed or would loop
    const url = originalRequest?.url || ''
    const isAuthLoopEndpoint =
      url.includes('/api/v1/auth/refresh') ||
      url.includes('/api/v1/auth/login') ||
      url.includes('/api/v1/auth/logout') ||
      url.includes('/api/v1/auth/signup')

    if (
      error.response?.status === 401 &&
      !originalRequest._retried &&
      !isAuthLoopEndpoint
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
        // Silent token refresh via httpOnly refresh_token cookie
        await api.post('/api/v1/auth/refresh')
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
        // If refresh fails with 401, session has expired -> dispatch event
        if (typeof window !== 'undefined' && refreshError.response?.status === 401) {
          window.dispatchEvent(new CustomEvent('auth:session-expired'))
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
