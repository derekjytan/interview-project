import type { ConversationMessage } from '../utils/api'
import { MessageBubble } from './MessageBubble'

type Props = {
  messages: ConversationMessage[]
  pending: boolean
  pendingContent: string
}

/**
 * The ordered list of saved messages. While `pending`, appends the in-flight
 * human message (`pendingContent`) plus an "…" AI placeholder bubble, since
 * neither row exists on the server yet.
 */
export function MessageList({ messages, pending, pendingContent }: Props) {
  return (
    <ol className="messages">
      {messages.map((message) => (
        <MessageBubble key={message.id} role={message.role}>
          {message.content}
        </MessageBubble>
      ))}
      {pending && (
        <>
          <MessageBubble role="HUMAN">{pendingContent}</MessageBubble>
          <MessageBubble role="AI" pending>
            …
          </MessageBubble>
        </>
      )}
    </ol>
  )
}
