# Persona chat: build sheet (for Claude Cowork Design)

The agent is already persona-aware and job-description-aware. You only build the front end: a role selector plus the starter chips below.

## How to wire it (one line)

When a category or role is selected, set the global:

```js
window.__persona = 'hiring_manager';   // use a key from the tables below
```

That is all. The chat bridge already sends `persona` to `/api/chat` on every message, and the agent branches tone, depth and next step. Before anything is selected, the persona is `general`.

(Fallback, if setting a global is awkward: prepend `Persona: hiring_manager.` to the message text. The agent detects that too.)

---

## State 1: zero state (nothing selected)

Show the category options, a live input box, and these four chips. Persona key: `general`.

- Give me the 30-second version
- What has she shipped?
- What is she building now?
- How does she use AI day to day?

Input placeholder: **"Ask anything, or paste a job description for a fit read..."**

A job description pasted here works immediately; no role needs to be chosen first.

---

## State 2: a category is chosen, but not yet a role

| L0 category | persona key |
|---|---|
| Hiring | `hiring` |
| Building | `building` |
| Community | `community` |
| Something else | `general` (role discovery) |

**Hiring** chips (all real, high-frequency interview questions):
- Tell me about yourself
- Walk me through your flagship project, and the lessons
- How do you measure success for an AI product?
- Is she a fit for our role? (paste a job description)

**Building** chips:
- How does she build agentic AI products?
- How technical is she?
- How does she manage the cost and return of large language models?
- Is she open to advising or collaborating?

**Community** chips:
- What does she speak and write about?
- What excites her about generative AI at the moment?
- How do I break into AI product management?
- Does she mentor or teach?

---

## State 3: a specific role is chosen

| L0 | L1 role | persona key |
|----|---------|-------------|
| **Hiring** | Recruiter / talent partner | `recruiter` |
| | Hiring manager | `hiring_manager` |
| | Executive (VP / Head of Product) | `executive` |
| **Building** | Product manager (peer) | `pm_peer` |
| | Founder / startup | `founder` |
| | Engineer or data scientist | `engineer` |
| **Community** | Student / aspiring AI PM | `student` |
| | Speaker, organizer or media | `speaker` |

**Recruiter**
- What is her level and scope?
- What are her must-have skills?
- What is she looking for in her next role?
- Paste a job description for a fit read

**Hiring manager**
- A disagreement with engineering, and how she resolved it
- How does she prioritize when everything is a priority?
- How did she know the generative AI product was ready to ship?
- Build or buy, and how does she manage the cost of large language models?

**Executive**
- What business impact has she driven?
- How does she run a platform on which many teams depend?
- How does she build a platform roadmap?
- What is her point of view on AI strategy?

**Product manager (peer)**
- How does she build agentic AI products?
- What does accuracy actually mean to her, and how does she measure it?
- How does she prioritize when everything is a priority?
- What is her product superpower?

**Founder / startup**
- How would she go from zero to one with an AI product?
- What is the fastest path to an agentic MVP?
- How does she manage the cost and return of large language models?
- Is she open to advising?

**Engineer or data scientist**
- How does she approach RAG, and how did she evaluate its accuracy?
- How did she raise accuracy from 80% to more than 90%?
- Which models and retrievers did she use?
- How does she catch hallucinations in production?

**Student / aspiring AI PM**
- How do I break into AI product management?
- How did she come to AI product management?
- What should I learn first?
- Does she mentor?

**Speaker, organizer or media**
- What does she speak and write about?
- What excites her about generative AI at the moment?
- Where has she spoken?
- Is she available to speak or to write?

---

## Design notes

- **Never force a choice.** The input box is live from the first screen. The category options are an offer, not a gate.
- **Always show the current role, and let them switch.**
- **"Not listed" is a first-class option.** It starts a one-question discovery, then maps to the closest role.
- **The job-description reply is a card, not a chat bubble**: match level, requirements met, strongest evidence, one honest gap, next step.

## Nothing to change on the backend

`api/chat.js` holds the grounding, the zero state, the three category personas, all eight role personas, the sensitive-topic guardrails, role discovery, and job-description handling. Verify with `agent-evals.md` before publishing.
