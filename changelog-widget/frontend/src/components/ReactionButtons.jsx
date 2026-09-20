/**
 * components/ReactionButtons.jsx
 * ──────────────────────────────
 * Interactive reaction bar for changelog updates.
 * Supports ❤️, 🎉, 🚀 emojis.
 *
 * Features:
 * - Displays live reaction counts
 * - Highlights when current user has reacted
 * - 1-click reaction toggle (add or remove)
 * - Optimistic real-time UI updates without page reloads
 * - Prompts unauthenticated visitors to log in
 */
import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { reactionService } from '../services/reactionService'
import { Button } from './ui'
import './ReactionButtons.css'

const DEFAULT_REACTIONS = [
  { reaction: '❤️', count: 0, user_reacted: false, user_reaction_id: null },
  { reaction: '🎉', count: 0, user_reacted: false, user_reaction_id: null },
  { reaction: '🚀', count: 0, user_reacted: false, user_reaction_id: null },
]

export default function ReactionButtons({ changelogId }) {
  const { user } = useAuth()
  const [reactions, setReactions] = useState(DEFAULT_REACTIONS)
  const [loading, setLoading] = useState(true)
  const [authPrompt, setAuthPrompt] = useState(false)
  const [busyEmoji, setBusyEmoji] = useState(null)

  const fetchReactions = useCallback(async () => {
    if (!changelogId) return
    try {
      const data = await reactionService.getForChangelog(changelogId)
      if (data?.reactions) {
        setReactions(data.reactions)
      }
    } catch {
      // Fall back to default structure silently
    } finally {
      setLoading(false)
    }
  }, [changelogId])

  useEffect(() => {
    fetchReactions()
  }, [fetchReactions, user])

  const handleReactionClick = async (item) => {
    if (!user) {
      setAuthPrompt(true)
      setTimeout(() => setAuthPrompt(false), 3500)
      return
    }

    if (busyEmoji) return // Prevent rapid spam
    setBusyEmoji(item.reaction)

    const prevReactions = [...reactions]
    const wasReacted = item.user_reacted
    const reactionId = item.user_reaction_id

    // Optimistic UI Update
    setReactions((current) =>
      current.map((r) => {
        if (r.reaction === item.reaction) {
          return {
            ...r,
            user_reacted: !wasReacted,
            count: wasReacted ? Math.max(0, r.count - 1) : r.count + 1,
          }
        }
        return r
      })
    )

    try {
      if (wasReacted && reactionId) {
        // Remove reaction
        await reactionService.remove(reactionId)
        // Refresh to guarantee sync
        setReactions((current) =>
          current.map((r) =>
            r.reaction === item.reaction ? { ...r, user_reaction_id: null } : r
          )
        )
      } else {
        // Add reaction
        const res = await reactionService.add(changelogId, item.reaction)
        setReactions((current) =>
          current.map((r) =>
            r.reaction === item.reaction ? { ...r, user_reaction_id: res.id } : r
          )
        )
      }
    } catch {
      // Revert optimistic update on failure
      setReactions(prevReactions)
    } finally {
      setBusyEmoji(null)
    }
  }

  return (
    <div className="reaction-container">
      <div className="reaction-group" role="group" aria-label="Changelog reactions">
        {reactions.map((r) => {
          const isActive = r.user_reacted
          return (
            <Button
              key={r.reaction}
              type="button"
              variant="ghost"
              className={`reaction-btn ${isActive ? 'active' : ''} ${
                busyEmoji === r.reaction ? 'busy' : ''
              }`}
              onClick={() => handleReactionClick(r)}
              disabled={loading || busyEmoji === r.reaction}
              title={
                !user
                  ? 'Sign in to react'
                  : isActive
                  ? `Remove ${r.reaction} reaction`
                  : `React with ${r.reaction}`
              }
            >
              <span className="reaction-emoji">{r.reaction}</span>
              <span className="reaction-count">{r.count}</span>
            </Button>
          )
        })}
      </div>

      {/* Auth prompt tooltip if non-logged in visitor clicks */}
      {authPrompt && (
        <div className="reaction-auth-prompt fade-in">
          <span>
            Please <Link to="/login">sign in</Link> to leave a reaction.
          </span>
        </div>
      )}
    </div>
  )
}
