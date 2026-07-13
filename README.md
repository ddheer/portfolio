# deeptidheer.com

Personal portfolio for **Deepti Dheer** (AI Product Leader), with a conversational AI agent grounded in her real experience.

**Live:** https://www.deeptidheer.com

---

## What this is

- A single-page portfolio, exported as a bundled HTML file from **Claude Cowork Design**.
- A **serverless AI agent** (`api/chat.js`) that answers visitors' questions about Deepti's work, grounded in her real roles and metrics, with guardrails on sensitive topics.
- Hosted on **Vercel**. The domain is registered at GoDaddy with nameservers pointing to Vercel.

---

## Files

| File | Purpose |
| --- | --- |
| `index.html` | The site. A bundled export from Claude Design, post-processed to add SEO metadata and the chat bridge. Do not hand-edit the design; re-export it instead. |
| `api/chat.js` | Vercel serverless function powering the agent. Calls Claude, grounded in Deepti's career context, with guardrails and lightweight actions (resume, email). **Must live inside `api/`** so Vercel serves it at `/api/chat`. |
| `postprocess.py` | Re-applies the "wiring" that a fresh design export always drops: SEO metadata and the chat bridge. Idempotent, safe to run repeatedly. |
| `resume.pdf` | Served at `/resume.pdf`. The site's "Download resume" button points here. Filename must stay lowercase. |
| `og-card.jpg` | 1200x630 social preview image referenced by the Open Graph tags. |
| `headshot.jpg` | Profile photo. |
| `agent-evals.md` | A 20-question eval set (happy path, sensitive, robustness) to verify the agent before publishing. |
| `persona-setup.md` | Notes for the recruiter / hiring-manager persona experience. |

---

## How the chat works

The design's chat calls `window.claude.complete(prompt)`, a helper that **only exists inside the Claude Design preview**. In production that function is undefined, so every message would fail.

`postprocess.py` injects a small bridge that defines `window.claude.complete` and routes it to **`/api/chat`** (your own Anthropic key), with a scripted fallback if the API is unavailable. That is why the site still answers sensibly even when the key is not set.

---

## Setup and deploy

1. The Vercel project is connected to this repo and auto-deploys on push to `main`.
2. Add the API key in **Vercel → Settings → Environment Variables**:
   ```
   ANTHROPIC_API_KEY = sk-ant-...
   ```
   Create the key at console.anthropic.com (billing must be enabled). **Never commit the key.**
3. Push to `main`. Vercel builds and deploys.

---

## Iterating on the design

This is the loop to follow every time:

1. Make changes in **Claude Cowork Design**.
2. Export and save the result as **`index.html`** in this repo, replacing the existing one.
3. Run the post-processor:
   ```bash
   python3 postprocess.py index.html
   ```
4. Commit and push. Vercel deploys.

A fresh export always ships with `<title>Bundled Page</title>`, no meta tags, and a chat that cannot work in production. **Step 3 fixes all of that.** Skipping it will break the chat and the SEO.

---

## Testing

**Locally (UI + fallback):** open `index.html` in a browser. The interface and the scripted fallback answers work. The live agent will not, because `/api/chat` needs a server.

**Locally with the real agent:**
```bash
npm i -g vercel
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
vercel dev
```

**Verify the agent:** work through `agent-evals.md`, especially the sensitive questions (compensation, work authorization, reasons for leaving). Confirm the guardrails hold before sharing the link widely.

---

## Gotchas

- `api/chat.js` must be **inside the `api/` folder**, not the repo root, or Vercel will not run it and the chat falls back to scripted answers.
- `resume.pdf` must be **lowercase and at the root**, or the download button 404s.
- Content (metrics, titles, dates) should match the resume. **The resume is the source of truth.**
- If the chat answers only in short, generic lines, the API key is missing or the function did not deploy.
