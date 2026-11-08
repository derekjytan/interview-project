import type { ReactNode } from 'react'
import { ConversationsProvider } from './ConversationsProvider'
import { ModelsProvider } from './ModelsProvider'

export function WidgetProvider({ children }: { children: ReactNode }) {
  return (
    <ModelsProvider>
      <ConversationsProvider>{children}</ConversationsProvider>
    </ModelsProvider>
  )
}
