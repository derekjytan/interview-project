import { Redirect, Route, Switch, useRoute } from 'wouter'
import './App.css'
import { ChatInput } from './components/ChatInput'
import { LoginPage } from './components/LoginPage'
import { MessageList } from './components/MessageList'
import { ModelSelect } from './components/ModelSelect'
import { Sidebar } from './components/Sidebar'
import { useAuth } from './context/AuthContext'
import { AuthProvider } from './context/AuthProvider'
import { useConversations } from './context/ConversationsContext'
import { useModels } from './context/ModelsContext'
import { WidgetProvider } from './context/WidgetProvider'
import { useThread } from './hooks/useThread'

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Switch>
      <Route path="/login">
        {user ? <Redirect to="/" replace /> : <LoginPage />}
      </Route>
      <Route>
        {user ? <ChatPage userId={user.id} /> : <Redirect to="/login" replace />}
      </Route>
    </Switch>
  )
}

// One catch-all Route for both chat URLs, so ChatApp (and useThread's pending
// state) isn't remounted when the first send moves "/" to "/chat/:id".
function ChatPage({ userId }: { userId: string }) {
  const [isRoot] = useRoute('/')
  const [isChat] = useRoute('/chat/:id')
  if (!isRoot && !isChat) return <Redirect to="/" replace />
  return (
    <WidgetProvider key={userId}>
      <ChatApp />
    </WidgetProvider>
  )
}

function ChatApp() {
  const { conversationNotFound, activeConversation } = useConversations()
  const { model, modelsError } = useModels()
  const {
    messages,
    pending,
    pendingContent,
    sendError,
    draft,
    setDraft,
    send,
  } = useThread()
  const error = sendError ?? modelsError
  const archived = Boolean(activeConversation?.archived_at)

  return (
    <div className="app">
      <Sidebar />
      <main className="main">
        {conversationNotFound ? (
          <div className="not-found" role="alert">
            <p className="error">This conversation doesn't exist.</p>
            <p>Pick a conversation from the sidebar or start a new chat.</p>
          </div>
        ) : (
          <>
            <MessageList
              messages={messages}
              pending={pending}
              pendingContent={pendingContent}
            />
            {error && <p className="error">{error}</p>}
            {archived ? (
              <p className="archived-notice">
                This conversation is archived and is read-only.
              </p>
            ) : (
              <ChatInput
                value={draft}
                onChange={setDraft}
                onSend={send}
                disabled={pending || !model}
              >
                <ModelSelect disabled={pending} />
              </ChatInput>
            )}
          </>
        )}
      </main>
    </div>
  )
}
