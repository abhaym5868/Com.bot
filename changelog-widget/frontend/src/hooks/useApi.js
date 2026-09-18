/**
 * hooks/useApi.js
 * ---------------
 * Generic data-fetching hook with loading / error states.
 */
import { useState, useEffect, useCallback } from 'react'

export function useApi(fetchFn, deps = [], options = {}) {
  const { immediate = true, initialData = null } = options
  const [data, setData] = useState(initialData)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn(...args)
      setData(result)
      return result
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'An error occurred'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    if (immediate) execute()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { data, loading, error, execute, setData }
}

export default useApi
