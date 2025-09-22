# Architecture 

## Domain
- Users authenticate via JWT (register/login/me).
- Users own Projects.
- Each Project has Prompts (system/assistant/user) and Messages (chat history).
- Optional: Files uploaded per Project (stored provider-side; we keep file_id).

## API
- FastAPI app with modular routers:
  - auth: register/login/me
  - projects: create/list/delete
  - prompts: add/list per project
  - chat: send message to provider (OpenAI / OpenRouter / Groq / mock)
  - files: list/upload (OpenAI Files API)
- SQLAlchemy models: User, Project, Prompt, Message, FileRef.
- SQLite dev DB (swap to Postgres by changing DATABASE_URL).
- Security: bcrypt password hashing, JWT bearer, per-user ownership checks.

## Providers
- Single entrypoint `llm_response(provider, model, system_prompt, user_text)`.
- openai: Responses API
- openrouter: Chat Completions
- groq: OpenAI-compatible Chat Completions
- mock: local reply (no keys) — useful for demos/tests.

## Non-functional
- Extensible: add routers/providers without touching existing ones.
- Scalable: stateless API; DB/queue can be externalized.
- Performance: async I/O to LLMs; minimal payloads.
- Reliability: clear 4xx/5xx error mapping; upstream errors surfaced as 502.
- Security: hashed passwords; tokens; project ownership enforced.
