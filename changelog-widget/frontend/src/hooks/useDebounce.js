/**
 * hooks/useDebounce.js
 * ────────────────────
 * Debounces a fast-changing value by specified delay in milliseconds.
 * Prevents spamming API calls on every keystroke.
 */
import { useState, useEffect } from 'react'

export function useDebounce(value, delay = 400) {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(timer)
    }
  }, [value, delay])

  return debouncedValue
}

export default useDebounce
