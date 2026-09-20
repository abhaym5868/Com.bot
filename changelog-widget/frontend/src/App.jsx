/**
 * App.jsx
 * ───────
 * Application entry point and routing hierarchy.
 * Routes:
 * - /                 -> TimelinePage (Public changelog feed)
 * - /changelog/:slug  -> ChangelogDetailPage (Single post view)
 * - /updates/:slug    -> ChangelogDetailPage (SEO friendly alias)
 * - /feed             -> FeedPage (Public JSON / RSS feed inspector)
 * - /login            -> LoginPage
 * - /signup           -> SignupPage
 * - /admin            -> AdminDashboardPage (Protected, Admin only)
 * - /admin/analytics  -> AnalyticsDashboardPage (Protected, Admin only)
 * - /admin/activity   -> ActivityLogPage (Protected, Admin only)
 * - /admin/widget     -> WidgetConfigPage (Protected, Admin only)
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import TimelinePage from './pages/TimelinePage'
import ChangelogDetailPage from './pages/ChangelogDetailPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import AnalyticsDashboardPage from './pages/AnalyticsDashboardPage'
import ActivityLogPage from './pages/ActivityLogPage'
import WidgetConfigPage from './pages/WidgetConfigPage'
import FeedPage from './pages/FeedPage'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="app-shell">
          <Navbar />
          <div className="app-content">
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<TimelinePage />} />
              <Route path="/feed" element={<FeedPage />} />
              <Route path="/changelog/:slug" element={<ChangelogDetailPage />} />
              <Route path="/updates/:slug" element={<ChangelogDetailPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/signup" element={<SignupPage />} />

              {/* Protected admin dashboard */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute adminOnly>
                    <AdminDashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/analytics"
                element={
                  <ProtectedRoute adminOnly>
                    <AnalyticsDashboardPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/activity"
                element={
                  <ProtectedRoute adminOnly>
                    <ActivityLogPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/widget"
                element={
                  <ProtectedRoute adminOnly>
                    <WidgetConfigPage />
                  </ProtectedRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}
