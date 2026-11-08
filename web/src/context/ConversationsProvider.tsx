import { useEffect, useState, type ReactNode } from 'react'
import { useLocation, useRoute } from 'wouter'
import {
  archiveConversation as requestArchiveConversation,
  createConversation,
  requestConversations,
  type ConversationWithMessages,
} from '../utils/api'
import { ConversationsContext } from './ConversationsContext'

export function ConversationsProvider({ children }: { children: ReactNode }) {
  const [, params] = useRoute('/chat/:id')
  const [, setLocation] = useLocation()
  const conversationId = params?.id ?? null
  const navigate = (id: string) => setLocation(`/chat/${id}`)
  const [conversations, setConversations] = useState<
    ConversationWithMessages[]
  >([])
  const [loaded, setLoaded] = useState(false)

  const refreshConversations = () =>
    requestConversations()
      .then((list) => {
        setConversations(list)
        setLoaded(true)
      })
      .catch(() => {})

  // Refresh before navigating so the new id is already in the list (no not-found flash).
  const openNewConversation = async () => {
    const id = await createConversation()
    await refreshConversations()
    navigate(id)
    return id
  }

  const archiveConversation = async (id: string) => {
    await requestArchiveConversation(id)
    await refreshConversations()
  }

  useEffect(() => {
    refreshConversations()
  }, [])

  const activeConversation = conversations.find(
    ({ id }) => id === conversationId,
  )
  const conversationNotFound =
    conversationId !== null && loaded && activeConversation === undefined

  return (
    <ConversationsContext
      value={{
        conversationId,
        navigate,
        conversations,
        activeConversation,
        conversationNotFound,
        refreshConversations,
        openNewConversation,
        archiveConversation,
      }}
    >
      {children}
    </ConversationsContext>
  )
}
