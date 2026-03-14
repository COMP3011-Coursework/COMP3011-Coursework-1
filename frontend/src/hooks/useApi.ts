import { useCallback, useEffect, useRef, useState } from 'react'

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })
  const mounted = useRef(true)

  const run = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fn()
      if (mounted.current) setState({ data, loading: false, error: null })
    } catch (err) {
      if (mounted.current)
        setState({ data: null, loading: false, error: String(err) })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    mounted.current = true
    run()
    return () => {
      mounted.current = false
    }
  }, [run])

  return { ...state, refetch: run }
}
