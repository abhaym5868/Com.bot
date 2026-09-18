/**
 * components/ProtectedRoute.jsx
 * ─────────────────────────────
 * Guards routes: redirects to /login if unauthenticated.
 * adminOnly: additionally checks for admin role.
 */
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="page-loader">
        <div className="spinner spinner-lg" />
        <span>Verifying session…</span>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (adminOnly && user.role !== 'admin') {
    return <Navigate to="/" replace />
  }

  return children
}
