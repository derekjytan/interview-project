import { createContext, useContext } from 'react'
import type { User } from '../utils/session'

export type AuthContextValue = {
  user: User | null
  login: (name: string, password: string) => Promise<void>
  signup: (name: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext)
  if (value === null) {
    throw new Error('useAuth must be used inside <AuthProvider>')
  }
  return value
}
