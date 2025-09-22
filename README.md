# Chat Platform

A lean FastAPI backend and a tiny Streamlit front-end that let you:

- register/login with JWT  
- create “agents” (projects) per user  
- attach prompts (system/assistant/user) to an agent  
- chat with an agent via OpenAI, Groq, OpenRouter, or a built-in mock  
- optionally upload files to OpenAI’s Files API and keep the file id  

It’s small on purpose, so you can extend it.

## What’s inside

- FastAPI for HTTP APIs  
- SQLAlchemy models and SQLite by default  
- JWT (password hashing with bcrypt)  
- Providers: OpenAI (Responses API), OpenRouter, Groq, Mock  
- Streamlit UI for demoing: login, create/select agent, add prompt, upload, chat

## Local setup (Windows / PowerShell)

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env and add any provider keys you’ll actually use

Run the API:

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

Docs: http://127.0.0.1:8000/docs

Run the UI (optional):

$env:API_BASE = "http://127.0.0.1:8000"
streamlit run streamlit_app.py

Environment variables

Create .env from .env.example and set what you need.

APP_NAME=Chat Platform
JWT_SECRET=change-me
JWT_ALG=HS256
JWT_EXPIRE_MIN=60
DATABASE_URL=sqlite:///./chat.db

# Pick one or more providers; leave empty if you’ll use "mock"
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

OPENROUTER_API_KEY=
OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct

GROQ_API_KEY=
Tip: if you don’t have keys/quota, create an agent with provider=mock and the whole flow still works.

API at a glance
Area	Method	Path	Notes
Health	GET	/health	simple liveness check
Auth	POST	/auth/register	{email, password}
	POST	/auth/login	returns access_token (JWT)
	GET	/auth/me	current user
Projects	POST	/projects	{name, provider, model?}
	GET	/projects	list my projects
Prompts	POST	/projects/{id}/prompts	{role, content}
	GET	/projects/{id}/prompts	list prompts
Chat	POST	/projects/{id}/chat	{message}
Files*	GET	/projects/{id}/files	list uploaded file refs
	POST	/projects/{id}/files	multipart(form-data) upload

* Files use OpenAI Files API if you configured OPENAI_API_KEY.

Quick curl walkthrough
# register
curl -s -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secret123"}'

# login
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"secret123"}' | jq -r .access_token)

# create a mock agent (no keys needed)
PROJECT=$(curl -s -X POST http://127.0.0.1:8000/projects \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Mock Agent","provider":"mock"}')
PID=$(echo "$PROJECT" | jq -r .id)

# add system prompt
curl -s -X POST http://127.0.0.1:8000/projects/$PID/prompts \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"role":"system","content":"You are a helpful assistant."}'

# chat
curl -s -X POST http://127.0.0.1:8000/projects/$PID/chat \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message":"Say hi in one sentence."}'

Streamlit UI

left sidebar: register/login

create/select project

add a prompt

upload a file (optional)

chat in the right panel

Set API_BASE if your API isn’t on localhost:

$env:API_BASE = "https://your-api-host.onrender.com"
streamlit run streamlit_app.py

Docker (optional)

Dockerfile and docker-compose.yml are included. Quick run:

docker compose up --build
# API at http://127.0.0.1:8000/docs


For Postgres, set DATABASE_URL to a Postgres URI and enable the db service in compose.

Notes on security and limits

Passwords are hashed (bcrypt)

JWT auth with expiry

Project ownership checks on every project-scoped route

Keep real keys out of git; use .env locally or host env vars

Mock provider is great for demos and CI
