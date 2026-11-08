import { useState, type ReactNode } from 'react'
import {
  login as requestLogin,
  logout as requestLogout,
  signup as requestSignup,
} from '../utils/api'
import { readSession, writeSession, type Session } from '../utils/session'
import { AuthContext } from './AuthContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState(readSession)

  const updateSession = (next: Session | null) => {
    writeSession(next)
    setSession(next)
  }

  const login = async (name: string, password: string) =>
    updateSession(await requestLogin(name, password))

  const signup = async (name: string, password: string) =>
    updateSession(await requestSignup(name, password))

  // Drop the local session even if the server call fails.
  const logout = async () => {
    await requestLogout().catch(() => {})
    updateSession(null)
  }

  return (
    <AuthContext
      value={{ user: session?.user ?? null, login, signup, logout }}
    >
      {children}
    </AuthContext>
  )
}
