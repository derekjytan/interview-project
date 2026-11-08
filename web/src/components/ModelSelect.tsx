import { useModels } from '../context/ModelsContext'

/**
 * Dropdown of available chat models, read from context. Disabled while
 * `disabled`, while models are loading, or when none were returned; shows
 * loading/empty placeholder options for those states.
 */
export function ModelSelect({ disabled }: { disabled: boolean }) {
  const { models, model, setModel, modelsPending } = useModels()

  return (
    <select
      className="model-select"
      aria-label="Model"
      value={model}
      onChange={(event) => setModel(event.target.value)}
      disabled={disabled || modelsPending || models.length === 0}
    >
      {modelsPending && <option value="">Loading models…</option>}
      {!modelsPending && models.length === 0 && (
        <option value="">No models available</option>
      )}
      {models.map((option) => (
        <option key={option.id} value={option.id} title={option.description}>
          {option.name}
        </option>
      ))}
    </select>
  )
}
