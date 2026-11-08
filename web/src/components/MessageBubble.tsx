import type { ReactNode } from 'react'
import type { Role } from '../utils/api'

const ROLE_CLASS: Record<Role, string> = {
  HUMAN: 'human',
  AI: 'ai',
}

type Props = { role: Role; pending?: boolean; children: ReactNode }

/**
 * A single chat row styled by role (`human`/`ai` class). `pending` adds a
 * muted style for the placeholder shown while the AI reply is in flight.
 */
export function MessageBubble({ role, pending = false, children }: Props) {
  return (
    <li
      className={['bubble', ROLE_CLASS[role], pending && 'pending']
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </li>
  )
}
