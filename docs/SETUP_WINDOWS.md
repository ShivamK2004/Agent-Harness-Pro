# Windows Setup Guide

## Prerequisites

- Python 3.10 or newer (Python 3.13 works with the project dependencies).
- Node.js 20.9 or newer and npm for the Next.js dashboard.
- PowerShell or Windows Terminal.
- Ollama is optional; Gemini requires a Google AI Studio API key.

## Install the Python backend

Run from the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If Python 3.13 is not installed, replace `-3.13` with an installed version, for example `-3.10`. Start in `LLM_PROVIDER=mock` mode before configuring a real model.

## Run the Next.js frontend (primary UI)

Open a second terminal in the project root:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`. The frontend uses `NEXT_PUBLIC_API_URL` from `frontend/.env.local`; the default is `http://127.0.0.1:8000`.

## Run FastAPI

In the first terminal, from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
```

API documentation: `http://127.0.0.1:8000/docs`. Start FastAPI before using the frontend.

## Gemini configuration

Create a key through [Google AI Studio](https://aistudio.google.com/apikey) and add it only to the repository-root `.env` file:

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Never put model credentials in `frontend/.env.local` or commit them to GitHub. Verify the available model and API limits in your AI Studio account.

## Ollama configuration

Install Ollama from [ollama.com](https://ollama.com/). Pull a model if it is not installed:

```powershell
ollama pull llama3:latest
ollama list
```

Configure the root `.env`:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT_SECONDS=180
```

Ollama must be running locally. The adapter first tries `/api/chat` and falls back to `/api/generate` if the chat endpoint returns HTTP 404 or 405.

## Tests

```powershell
python -m pytest -q
```

The unit tests use mocks and do not require a Gemini key or a running Ollama instance.

## Optional legacy Streamlit interface

The original Streamlit app is kept as a fallback:

```powershell
streamlit run app\streamlit_app.py
```

Open `http://localhost:8501`.

## Common problems

- **Gemini key missing:** check the root `.env` file name and key variable, then restart FastAPI.
- **Ollama connection refused:** check `ollama list`, confirm Ollama is running, and test `http://localhost:11434/api/tags`.
- **Ollama model not found:** set `OLLAMA_MODEL` to the exact name printed by `ollama list`.
- **Frontend cannot reach backend:** start FastAPI, open `/health`, and check `NEXT_PUBLIC_API_URL`.
- **CORS error:** use `http://localhost:3000` or `http://127.0.0.1:3000`; configure exact deployed origins before deployment.
- **Module not found:** activate `.venv` and run `pip install -r requirements.txt`.
- **Port busy:** use a different API port and update `NEXT_PUBLIC_API_URL`, or stop the process using the default port.
