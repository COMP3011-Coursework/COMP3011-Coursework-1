import { apiFetch } from './client'
import type { AuthToken } from '../types'

export function login(username: string, password: string): Promise<AuthToken> {
  const body = new URLSearchParams({ username, password })
  return fetch(
    `${import.meta.env.VITE_API_URL ?? '/api/v1'}/auth/login`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    },
  ).then(async (res) => {
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail ?? 'Login failed')
    }
    return res.json()
  })
}

export function register(
  username: string,
  email: string,
  password: string,
): Promise<{ id: number; username: string }> {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  })
}
