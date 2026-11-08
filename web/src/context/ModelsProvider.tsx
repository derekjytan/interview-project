import { useEffect, useState, type ReactNode } from 'react'
import {
  requestModels,
  UNREACHABLE,
  type ModelOption,
} from '../utils/api'
import { ModelsContext } from './ModelsContext'

export function ModelsProvider({ children }: { children: ReactNode }) {
  const [models, setModels] = useState<ModelOption[]>([])
  const [model, setModel] = useState('')
  const [modelsPending, setModelsPending] = useState(true)
  const [modelsError, setModelsError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    requestModels()
      .then((options) => {
        if (!active) return
        setModels(options)
        setModel(
          options.find((option) => option.is_default)?.id ?? options[0]?.id ?? '',
        )
      })
      .catch(() => {
        if (active) setModelsError(UNREACHABLE)
      })
      .finally(() => {
        if (active) setModelsPending(false)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <ModelsContext
      value={{ models, model, setModel, modelsPending, modelsError }}
    >
      {children}
    </ModelsContext>
  )
}
