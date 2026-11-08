import { Archive } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useConversations } from '../context/ConversationsContext'
import { errorMessage } from '../utils/api'

/**
 * Left rail listing non-archived conversations from context. Each entry has a
 * hover archive icon button (archived conversations disappear from the list and
 * can't be restored). "+ New chat" creates and opens a conversation; errors
 * from either action show beneath the button. Entries are labeled by title
 * (or "New chat" until the first exchange sets one); the open conversation is
 * highlighted.
 */
export function Sidebar() {
  const {
    conversations,
    conversationId,
    navigate,
    openNewConversation,
    archiveConversation,
  } = useConversations()
  const { user, logout } = useAuth()
  const [error, setError] = useState<string | null>(null)

  const runAction = async (action: () => Promise<unknown>) => {
    setError(null)
    try {
      await action()
    } catch (err) {
      setError(errorMessage(err))
    }
  }

  return (
    <aside className="sidebar">
      <button className="new-chat" onClick={() => runAction(openNewConversation)}>
        + New chat
      </button>
      {error && <p className="error">{error}</p>}
      <nav className="conversation-list">
        {conversations
          .filter((conversation) => conversation.archived_at === null)
          .map((conversation) => {
            const title = conversation.title ?? 'New chat'
            return (
              <div
                key={conversation.id}
                className={
                  conversation.id === conversationId
                    ? 'conversation-item active'
                    : 'conversation-item'
                }
              >
                <button
                  className="conversation-title"
                  onClick={() => navigate(conversation.id)}
                >
                  {title}
                </button>
                <button
                  className="archive"
                  aria-label={`Archive ${title}`}
                  title="Archive"
                  onClick={() =>
                    runAction(() => archiveConversation(conversation.id))
                  }
                >
                  <Archive size={16} aria-hidden />
                </button>
              </div>
            )
          })}
      </nav>
      <footer className="sidebar-footer">
        <span className="user-name">{user?.name}</span>
        <button onClick={() => runAction(logout)}>Log out</button>
      </footer>
    </aside>
  )
}
