import { createContext, useContext } from 'react'
import type { ConversationWithMessages } from '../utils/api'

export type ConversationsContextValue = {
  conversationId: string | null
  navigate: (id: string) => void
  conversations: ConversationWithMessages[]
  activeConversation: ConversationWithMessages | undefined
  conversationNotFound: boolean
  refreshConversations: () => Promise<void>
  openNewConversation: () => Promise<string>
  archiveConversation: (id: string) => Promise<void>
}

export const ConversationsContext =
  createContext<ConversationsContextValue | null>(null)

export function useConversations(): ConversationsContextValue {
  const value = useContext(ConversationsContext)
  if (value === null) {
    throw new Error('useConversations must be used inside <ConversationsProvider>')
  }
  return value
}
