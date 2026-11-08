import { createContext, useContext } from 'react'
import type { ModelOption } from '../utils/api'

export type ModelsContextValue = {
  models: ModelOption[]
  model: string
  setModel: (id: string) => void
  modelsPending: boolean
  modelsError: string | null
}

export const ModelsContext = createContext<ModelsContextValue | null>(null)

export function useModels(): ModelsContextValue {
  const value = useContext(ModelsContext)
  if (value === null) {
    throw new Error('useModels must be used inside <ModelsProvider>')
  }
  return value
}
