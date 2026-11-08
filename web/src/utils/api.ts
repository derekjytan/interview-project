import { readSession, type Session } from './session'

export type Role = 'AI' | 'HUMAN'

export type Conversation = {
  id: string
  title: string | null
  created_at: string
  updated_at: string
  archived_at: string | null
}

export type ConversationMessage = {
  id: string
  conversation_id: string
  role: Role
  content: string
  created_at: string
}

export type ConversationWithMessages = Conversation & {
  messages: ConversationMessage[]
}

export type ModelOption = {
  id: string
  name: string
  description: string
  is_default: boolean
}

export class ApiError extends Error {
  constructor(
    public status: number,
    detail: string | null,
  ) {
    super(detail ?? `Request failed with ${status}`)
  }
}

const readDetail = async (res: Response): Promise<string | null> => {
  const body: unknown = await res.json().catch(() => null)
  if (
    body !== null &&
    typeof body === 'object' &&
    'detail' in body &&
    typeof body.detail === 'string'
  ) {
    return body.detail
  }
  return null
}

const check = async (res: Response): Promise<Response> => {
  if (!res.ok) throw new ApiError(res.status, await readDetail(res))
  return res
}

export const UNREACHABLE =
  'Could not reach the API. It may still be starting — wait a moment and try again.'

export const errorMessage = (error: unknown) =>
  error instanceof ApiError ? error.message : UNREACHABLE

export const fetchWithAuth = (input: RequestInfo | URL, init?: RequestInit) => {
  const headers = new Headers(init?.headers)
  const token = readSession()?.token
  if (token) headers.set('Authorization', `Bearer ${token}`)
  return fetch(input, { ...init, headers })
}

export async function requestModels(): Promise<ModelOption[]> {
  const res = await fetch('/api/models')
  return (await check(res)).json()
}

export async function login(name: string, password: string): Promise<Session> {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, password }),
  })
  return (await check(res)).json()
}

export async function signup(
  name: string,
  password: string,
): Promise<Session> {
  const res = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, password }),
  })
  return (await check(res)).json()
}

export async function logout(): Promise<void> {
  await check(await fetchWithAuth('/api/auth/logout', { method: 'POST' }))
}

export async function requestConversations(): Promise<
  ConversationWithMessages[]
> {
  const res = await fetchWithAuth('/api/conversations')
  return (await check(res)).json()
}

export async function createConversation(): Promise<string> {
  const res = await fetchWithAuth('/api/conversation', { method: 'POST' })
  const body: { id: string } = await (await check(res)).json()
  return body.id
}

export async function archiveConversation(id: string): Promise<void> {
  await check(
    await fetchWithAuth(`/api/conversation/${id}/archive`, { method: 'POST' }),
  )
}

export async function requestCompletion(
  id: string,
  content: string,
  model: string,
): Promise<ConversationMessage[]> {
  const res = await fetchWithAuth(`/api/chat/completion/${id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, model }),
  })
  return (await check(res)).json()
}
