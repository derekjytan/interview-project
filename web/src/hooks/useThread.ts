import { useState } from 'react'
import { useConversations } from '../context/ConversationsContext'
import { useModels } from '../context/ModelsContext'
import { errorMessage, requestCompletion } from '../utils/api'

type ThreadState = {
  draft: string
  pendingContent: string | null
  sendError: string | null
}
const EMPTY_THREAD: ThreadState = {
  draft: '',
  pendingContent: null,
  sendError: null,
}
// Key for the unsaved conversation shown before the first send creates one.
const NEW_THREAD = 'new'

export function useThread() {
  const {
    conversationId,
    activeConversation,
    openNewConversation,
    refreshConversations,
  } = useConversations()
  const { model } = useModels()
  const [threads, setThreads] = useState<Record<string, ThreadState>>({})

  const updateThread = (
    key: string,
    update: (thread: ThreadState) => Partial<ThreadState>,
  ) =>
    setThreads((current) => {
      const thread = current[key] ?? EMPTY_THREAD
      return { ...current, [key]: { ...thread, ...update(thread) } }
    })
  const threadKey = conversationId ?? NEW_THREAD
  const thread = threads[threadKey] ?? EMPTY_THREAD
  const pending = thread.pendingContent !== null
  const setDraft = (draft: string) => updateThread(threadKey, () => ({ draft }))

  const send = async () => {
    const content = thread.draft.trim()
    if (!content || !model || pending) return
    updateThread(threadKey, () => ({ draft: '', sendError: null }))

    let id = conversationId
    if (id === null) {
      try {
        id = await openNewConversation()
      } catch (err) {
        updateThread(NEW_THREAD, () => ({
          draft: content,
          sendError: errorMessage(err),
        }))
        return
      }
    }

    const sentId = id
    updateThread(sentId, () => ({ pendingContent: content }))
    try {
      await requestCompletion(sentId, content, model)
      // Clear pending only after the refreshed list (with the exchange) lands, to avoid a flicker.
      await refreshConversations()
      updateThread(sentId, () => ({ pendingContent: null }))
    } catch (err) {
      // Don't clobber anything typed while the request was in flight.
      updateThread(sentId, (current) => ({
        pendingContent: null,
        sendError: errorMessage(err),
        draft: current.draft || content,
      }))
    }
  }

  return {
    messages: activeConversation?.messages ?? [],
    pending,
    pendingContent: thread.pendingContent ?? '',
    sendError: thread.sendError,
    draft: thread.draft,
    setDraft,
    send,
  }
}
