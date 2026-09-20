/**
 * context/AuthContext.jsx
 * -----------------------
 * Global authentication state provider.
 * Exposes: user, loading, login, signup, logout, isAdmin
 */
import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)  // true on first mount (checking session)
  const [error, setError] = useState(null)

  // Attempt to restore session from existing httpOnly cookie
  const restoreSession = useCallback(async () => {
    try {
      const me = await authService.getMe()
      setUser(me)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    restoreSession()
  }, [restoreSession])

  const login = async (email, password) => {
    setError(null)
    const data = await authService.login(email, password)
    setUser(data.user)
    return data
  }

  const signup = async (name, email, password) => {
    setError(null)
    const data = await authService.signup(name, email, password)
    setUser(data.user)
    return data
  }

  const logout = async () => {
    try {
      await authService.logout()
    } finally {
      setUser(null)
    }
  }

  const isAdmin = user?.role === 'admin'

  return (
    <AuthContext.Provider value={{ user, loading, error, login, signup, logout, isAdmin, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}

export default AuthContext
