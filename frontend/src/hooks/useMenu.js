import { useState, useEffect } from 'react'
import { menuApi } from '../api/menuApi'

export function useMenu(reelId) {
  const [menu, setMenu] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!reelId) return
    setLoading(true)
    menuApi
      .getByReel(reelId)
      .then(setMenu)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [reelId])

  return { menu, loading, error }
}
