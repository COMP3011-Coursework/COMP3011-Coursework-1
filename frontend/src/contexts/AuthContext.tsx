import { createContext, useCallback, useContext, useEffect, useState } from 'react'

interface AuthState {
  token: string | null
  username: string | null
}

interface AuthContextValue extends AuthState {
  login: (token: string, username: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(() => ({
    token: localStorage.getItem('token'),
    username: localStorage.getItem('username'),
  }))

  useEffect(() => {
    if (state.token) {
      localStorage.setItem('token', state.token)
      localStorage.setItem('username', state.username ?? '')
    } else {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
    }
  }, [state])

  const login = useCallback((token: string, username: string) => {
    setState({ token, username })
  }, [])

  const logout = useCallback(() => {
    setState({ token: null, username: null })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
