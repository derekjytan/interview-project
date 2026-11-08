export type User = { id: string; name: string }
export type Session = { token: string; user: User }

const STORAGE_KEY = 'session'

export const readSession = (): Session | null => {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  return stored ? JSON.parse(stored) : null
}

export const writeSession = (session: Session | null) =>
  session
    ? sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session))
    : sessionStorage.removeItem(STORAGE_KEY)
