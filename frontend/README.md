# Agent Harness Pro Web UI

This is the Next.js + React dashboard for Agent Harness Pro. It talks to the Python FastAPI backend and does not contain model API keys.

## Install and run

```powershell
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`. Start FastAPI from the repository root first:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Production build

```powershell
npm run build
npm run start
```

## Environment

`NEXT_PUBLIC_API_URL` points to FastAPI. Only non-secret configuration belongs in this file. Keep `GEMINI_API_KEY` in the Python project's root `.env` file.
