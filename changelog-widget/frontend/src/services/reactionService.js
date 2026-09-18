/**
 * services/reactionService.js
 * ───────────────────────────
 * API client methods for changelog reactions:
 * - add(changelogId, reaction)
 * - remove(reactionId)
 * - getForChangelog(changelogId)
 */
import api from './api'

export const reactionService = {
  async add(changelogId, reaction) {
    const res = await api.post('/api/v1/reactions', {
      changelog_id: changelogId,
      reaction,
    })
    return res.data // { id, user_id, changelog_id, reaction, created_at }
  },

  async remove(reactionId) {
    const res = await api.delete(`/api/v1/reactions/${reactionId}`)
    return res.data // { message }
  },

  async getForChangelog(changelogId) {
    const res = await api.get(`/api/v1/reactions/changelog/${changelogId}`)
    return res.data // { changelog_id, reactions: [{ reaction, count, user_reacted, user_reaction_id }] }
  },
}

export default reactionService
