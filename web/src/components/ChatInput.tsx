import { type FormEvent, type ReactNode } from 'react'

type Props = {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  disabled: boolean
  children?: ReactNode
}

/**
 * Message form with a text field and Send button; the text is controlled by
 * the parent (per-conversation drafts) and children (e.g. the model picker)
 * are rendered inside the form ahead of the input. `disabled` blocks both
 * submitting and the Send button.
 */
export function ChatInput({ value, onChange, onSend, disabled, children }: Props) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!value.trim() || disabled) return
    onSend()
  }

  return (
    <form onSubmit={handleSubmit}>
      {children}
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Say something"
        autoFocus
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  )
}
