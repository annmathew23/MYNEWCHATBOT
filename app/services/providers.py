import os
import httpx
from app.core.settings import settings

OPENAI_BASE = "https://api.openai.com/v1"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
GROQ_BASE = "https://api.groq.com/openai/v1"  # OpenAI-compatible

def _extract_text_from_responses_api(data: dict) -> str:
    if "output_text" in data and data["output_text"]:
        return data["output_text"]
    out = data.get("output")
    if isinstance(out, dict):
        content = out.get("content")
        if isinstance(content, list):
            texts = []
            for part in content:
                if isinstance(part, dict):
                    t = part.get("text")
                    if t:
                        texts.append(t)
            if texts:
                return "\n".join(texts)
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message") or {}
        if "content" in msg:
            return msg["content"]
    return str(data)

async def openai_response(model: str, system_prompt: str, user_text: str) -> str:
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    payload = {
        "model": model or settings.openai_model,
        "instructions": system_prompt or "You are a helpful assistant.",
        "input": user_text,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OPENAI_BASE}/responses", headers=headers, json=payload)
        r.raise_for_status()
        return _extract_text_from_responses_api(r.json())

async def openrouter_response(model: str, system_prompt: str, user_text: str) -> str:
    key = settings.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    use_model = model or settings.openrouter_model or "meta-llama/llama-3.1-8b-instruct"
    payload = {
        "model": use_model,
        "messages": [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": user_text},
        ]
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        # Optional but nice for OpenRouter analytics:
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Chat Platform",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OPENROUTER_BASE}/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

async def groq_response(model: str, system_prompt: str, user_text: str) -> str:
    key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY not set")
    use_model = model or "llama-3.3-70b-versatile"
    payload = {
        "model": use_model,
        "messages": [
            {"role": "system", "content": system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": user_text},
        ]
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{GROQ_BASE}/chat/completions", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

async def mock_response(model: str, system_prompt: str, user_text: str) -> str:
    return f"(mock) [{model or 'demo-model'}] {system_prompt[:40]}... | Replying to: {user_text}"

async def llm_response(provider: str, model: str | None, system_prompt: str, user_text: str) -> str:
    p = (provider or "openai").lower()
    if p == "openai":
        return await openai_response(model or settings.openai_model, system_prompt, user_text)
    if p == "openrouter":
        return await openrouter_response(model or settings.openrouter_model, system_prompt, user_text)
    if p == "groq":
        return await groq_response(model, system_prompt, user_text)
    if p == "mock":
        return await mock_response(model, system_prompt, user_text)
    # default to openai
    return await openai_response(model or settings.openai_model, system_prompt, user_text)
