# Persona chat: build sheet (for Claude Cowork Design)

The agent is already persona-aware. You only build the front end: a role selector + the starter chips.

## 0. Zero state (before any role is picked)

The entry screen must be useful on its own. Show the L0 options and a live input box, plus these four starter chips. Anyone can tap them without declaring a role. The last one softly routes into the Hiring personas.

- What has she shipped?
- What is she working on now?
- How does she build AI products?
- Is she open to new roles?

Persona to send while nothing is selected: `general`. The agent answers neutrally, then lightly offers to tailor. If a job description is pasted here, it offers to switch to recruiter or hiring manager rather than guessing.

## 1. The selector (L0 then L1)

Open neutral, show L0, let anyone switch at any time. Never force a choice.

| L0 | L1 roles | persona key to send |
|----|----------|---------------------|
| **Hiring** | Recruiter / talent partner | `recruiter` |
| | Hiring manager | `hiring_manager` |
| | Executive (VP / Head of Product) | `executive` |
| **Building** | Product manager (peer) | `pm_peer` |
| | Founder / startup | `founder` |
| | Engineer or data scientist | `engineer` |
| **Community** | Student / aspiring AI PM | `student` |
| | Speaker, organizer, or media | `speaker` |
| **Something else** | (role discovery) | `general` |

## 2. Wire the persona (one line)

When a role is selected, set the global:

```js
window.__persona = 'hiring_manager';   // use the key from the table
```

That is all. The chat bridge already sends `persona` to `/api/chat` on every message, and the agent branches tone, depth, and next step. Default before any selection: `general`.

(Fallback if setting a global is awkward: prepend `Persona: hiring_manager.` to the message text. The agent detects that too.)

## 3. Starter chips per role (4 each)

**Recruiter**
- Is she the right level and fit?
- What are her must-have skills?
- Is she open to new roles?
- Paste a job description for a quick match

**Hiring manager**
- Walk me through her most impactful product
- A hard tradeoff she made?
- How does she measure AI success?
- How does she lead across teams?

**Executive**
- What business impact has she driven?
- How does she operate at org scale?
- What is her POV on AI strategy?
- Could she lead a platform org?

**Product manager (peer)**
- How do you build agentic AI products?
- How do you run evals?
- How do you prioritize?
- What is your AI-native workflow?

**Founder / startup**
- How would you go 0-to-1 with AI?
- How do you keep AI costs sane?
- Fastest path to an agentic MVP?
- Is she open to advising?

**Engineer / data scientist**
- How technical is she?
- How does she design context and RAG?
- How does she partner with engineering?
- What does she own versus the team?

**Student / aspiring AI PM**
- How do I break into AI PM?
- What should I learn first?
- What should I build for my portfolio?
- Does she mentor?

**Speaker / organizer / media**
- What does she speak about?
- Where has she spoken?
- Is she available to speak?
- Can she write for us?

## 4. Nothing to change on the backend
`api/chat.js` holds the grounding, all 8 persona blocks (tone, depth, canonical answers, next step), the sensitive-topic guardrails, role discovery, and job-description handling. Verify with `agent-evals.md` before publishing.
