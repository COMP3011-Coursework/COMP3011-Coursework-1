# Is this project possible to deploy on vercel?

**Session ID:** `6f5ece28-dc4c-4593-8ab6-62a2e8b776df`  
**Started:** 2026-03-16 21:22 UTC  
**Ended:** 2026-03-16 21:22 UTC  
**Source:** Claude Code (local session log)

---

## **Human** _2026-03-16 21:22 UTC_

Is this project possible to deploy on vercel?

---

## **Assistant** _2026-03-16 21:22 UTC_

*[Tool call: `Glob` — `**/*`]*

---

## **Assistant** _2026-03-16 21:22 UTC_

*[Tool call: `Read` — `/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Coursework 1/COMP3011-Coursework-1/README.md`]*

---

## **Assistant** _2026-03-16 21:22 UTC_

*[Tool call: `Glob` — `*.{json,toml,cfg,ini,txt,yaml,yml}`]*

---

## **Assistant** _2026-03-16 21:22 UTC_

*[Tool call: `Glob` — `backend/*.{json,toml,cfg,txt}`]*

---

## **Assistant** _2026-03-16 21:22 UTC_

**Partially yes**, but with significant caveats:

**Frontend (React/Vite)** — Works perfectly on Vercel. It's a standard Vite build outputting static files, which is exactly what Vercel is designed for.

**Backend (FastAPI + PostgreSQL)** — Technically deployable via Vercel's Python serverless functions, but there are blockers:

1. **MCP server at `/mcp/sse`** — This uses Server-Sent Events (SSE), which requires a persistent, long-lived HTTP connection. Vercel's serverless functions have a max execution timeout (60s on Pro, 10s on Hobby) and aren't designed for streaming connections like SSE. This is likely a **hard blocker**.

2. **Async SQLAlchemy + connection pooling** — Serverless functions spin up/down per request, which fights against connection pools. You'd need to configure for serverless (e.g., `NullPool`), which is doable but requires code changes.

3. **No Docker support** — Your current deployment uses Docker Compose. Vercel doesn't run containers.

4. **PostgreSQL** — Vercel doesn't host it natively (though Vercel Postgres exists, powered by Neon). You'd need an external DB like Neon, Supabase, or Railway.

**Better alternatives for this stack:**

| Service | Suitable for |
|---|---|
| **Railway** | Full app (backend + Postgres), supports long-running processes, Docker |
| **Render** | Same — free tier available, supports SSE |
| **Fly.io** | Docker-based, persistent connections, great for FastAPI + SSE |
| **Vercel (frontend) + Railway/Render (backend)** | Best of both worlds |

The SSE requirement for the MCP server rules out pure Vercel deployment unless you're willing to drop or redesign that feature.

---
