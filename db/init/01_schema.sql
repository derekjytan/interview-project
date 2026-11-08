CREATE TABLE users (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        text NOT NULL UNIQUE,
  -- Plaintext for demo purposes only; see service/auth.py `authenticate`.
  password    text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE user_sessions (
  token       text PRIMARY KEY,
  user_id     uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE conversations (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  title       text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  archived_at timestamptz
);

CREATE TABLE conversation_messages (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id  uuid NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
  role             text NOT NULL CHECK (role IN ('AI', 'HUMAN')),
  content          text NOT NULL,
  -- clock_timestamp(), not now(): now() is fixed per transaction, so rows
  -- inserted together would tie and lose their order.
  created_at       timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX conversation_messages_conversation_idx
  ON conversation_messages (conversation_id, created_at);
