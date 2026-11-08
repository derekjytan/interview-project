import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { errorMessage } from '../utils/api'

// Mirrors the seeded users in db/init/02_seed.sql; demo-only credentials.
const DEMO_USERS = [
  { name: 'alice', password: 'alice-password' },
  { name: 'bob', password: 'bob-password' },
  { name: 'carol', password: 'carol-password' },
] as const

export function LoginPage() {
  const { login, signup } = useAuth()
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  const attempt = async (
    action: (name: string, password: string) => Promise<void>,
    loginName: string,
    loginPassword: string,
  ) => {
    setError(null)
    setPending(true)
    try {
      await action(loginName, loginPassword)
    } catch (err) {
      setError(errorMessage(err))
      setPending(false)
    }
  }

  return (
    <div className="login">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          attempt(login, name, password)
        }}
      >
        <label>
          Name
          <input
            autoComplete="username"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={pending}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={pending}
          />
        </label>
        <div className="login-actions">
          <button type="submit" disabled={pending || !name || !password}>
            Sign in
          </button>
          <button
            type="button"
            disabled={pending || !name || !password}
            onClick={() => attempt(signup, name, password)}
          >
            Create account
          </button>
        </div>
      </form>
      {error && <p className="error">{error}</p>}
      <div className="login-quick">
        {DEMO_USERS.map((demo) => (
          <button
            key={demo.name}
            disabled={pending}
            onClick={() => attempt(login, demo.name, demo.password)}
          >
            {demo.name}
          </button>
        ))}
      </div>
    </div>
  )
}
