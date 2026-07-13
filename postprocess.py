#!/usr/bin/env python3
"""
Make a fresh Claude Design export of index.html production-ready.

A design export ships a *scripted* chat: it matches questions against a handful
of regexes and falls back to a canned line. It does not know about /api/chat.
This script re-applies everything the export drops:

  1. SEO / social metadata (title, viewport, description, Open Graph, favicon, JSON-LD)
  2. The four locked zero-state conversation starters
  3. The agent bridge: chips keep their rich scripted cards, but any free-text
     miss or pasted job description calls /api/chat with the visitor's persona
  4. The resume link (the export points it at the homepage, not the PDF)
  5. Dashes: Deepti does not use em or en dashes

Idempotent. Run it after every export:

    python3 postprocess.py            # ./index.html in place
    python3 postprocess.py other.html
"""
import re, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "index.html"

META = '''<title>Deepti Dheer, AI Product Leader | AI Product Manager, Agentic AI & LLMs</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Portfolio of Deepti Dheer, an AI Product Leader shipping generative and agentic AI products to 100M+ users. Agentic AI, LLMs, RAG, evals, pricing, and zero-to-one product strategy.">
<link rel="canonical" href="https://www.deeptidheer.com/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23C8553D'/%3E%3Ctext x='32' y='45' font-family='Georgia,serif' font-size='32' font-weight='bold' fill='white' text-anchor='middle'%3EDD%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.deeptidheer.com/">
<meta property="og:title" content="Deepti Dheer, AI Product Leader">
<meta property="og:description" content="AI Product Leader shipping generative and agentic AI products to 100M+ users.">
<meta property="og:image" content="https://www.deeptidheer.com/og-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Deepti Dheer, AI Product Leader">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Deepti Dheer, AI Product Leader">
<meta name="twitter:description" content="AI Product Leader shipping generative and agentic AI products to 100M+ users.">
<meta name="twitter:image" content="https://www.deeptidheer.com/og-card.jpg">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Person","name":"Deepti Dheer","jobTitle":"AI Product Leader","url":"https://www.deeptidheer.com/","sameAs":["https://www.linkedin.com/in/deeptidheer/"],"knowsAbout":["Agentic AI","Generative AI","Product Management","RAG","LLMs","AI Evaluations","Conversational AI","Go-to-Market Strategy"],"alumniOf":"University of San Francisco","address":{"@type":"PostalAddress","addressLocality":"San Francisco Bay Area","addressRegion":"CA","addressCountry":"US"}}</script>'''

# The design's app source is JSON-escaped inside <script type="__bundler/template">,
# so every patch is matched and written in that escaped form.
def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

STARTERS = ['Give me the 30-second version', 'What has she shipped?',
            'What is she building now?', 'How does she use AI day to day?']

OLD_CHIPS = """bottomChips = ["What's her most impactful product?", 'What is she looking for?', 'Show me her skills'].map((t) => ({ text: t, onClick: () => this.freeAsk(t) }));"""
NEW_CHIPS = ("bottomChips = [" + ", ".join("'%s'" % s for s in STARTERS) +
             "].map((t) => ({ text: t, onClick: () => this.askLive(t) }));")

OLD_SEND = """    let id = builderId;
    if (!id) id = this.isJD(t) ? 'jd' : (this.route(t) || cfg.fallback);
    const answers = (this.BUILDERS[id] || this.BUILDERS.fallback)();
    this.setState((s) => ({ messages: [...s.messages, { isUser: true, text: t }], draft: '' }));"""
NEW_SEND = """    let id = builderId; let live = false;
    if (!id) { if (this.isJD(t)) { id = 'jd'; live = true; } else { const r = this.route(t); if (r) { id = r; } else { id = cfg.fallback; live = true; } } }
    const answers = (this.BUILDERS[id] || this.BUILDERS.fallback)();
    this.setState((s) => ({ messages: [...s.messages, { isUser: true, text: t }], draft: '' }));
    if (live) { this.askAgent(t, answers, cfg); return; }"""

AGENT = """  PERSONA_MAP = { recruiter: 'recruiter', hm: 'hiring_manager', exec: 'executive', founder: 'founder', engineer: 'engineer', pmpeer: 'pm_peer', organizer: 'speaker', writer: 'speaker', mentee: 'student', general: 'general' };

  askLive(text) {
    const t = (text || '').trim();
    if (!t || this.state.thinking) return;
    const role = this.state.role || 'general';
    const cfg = this.ROLES[role];
    this.setState((s) => ({ messages: [...s.messages, { isUser: true, text: t }], draft: '', role: role, picking: null }));
    this.askAgent(t, this.BUILDERS.fallback(), cfg);
  }

  askAgent(t, fallbackMsgs, cfg) {
    const steps = cfg.think;
    clearInterval(this._t);
    this.setState({ thinking: true, thinkStep: 0 });
    this._t = setInterval(() => { this.setState((s) => ({ thinkStep: (s.thinkStep + 1) % (steps.length + 1) })); }, 520);
    const finish = (msgs) => { clearInterval(this._t); this.setState((s) => ({ thinking: false, thinkStep: 0, messages: [...s.messages, ...msgs] })); };
    const persona = this.PERSONA_MAP[this.state.role] || 'general';
    const timer = setTimeout(() => { finish(fallbackMsgs); }, 20000);
    let settled = false;
    fetch('/api/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ persona: persona, messages: [{ role: 'user', content: t }] }) })
      .then((r) => { if (!r.ok) throw new Error('http'); return r.json(); })
      .then((d) => {
        if (settled) return;
        let txt = (d && (d.reply || d.text || d.message)) ? String(d.reply || d.text || d.message) : '';
        const wantsResume = /\\[\\[action:resume\\]\\]/i.test(txt);
        txt = txt.replace(/\\[\\[action:[^\\]]*\\]\\]/gi, '').trim();
        if (!txt) throw new Error('empty');
        const parts = txt.split(/\\n\\s*\\n/).map((p) => p.replace(/\\s+/g, ' ').trim()).filter(Boolean);
        const lead = parts.length > 1 ? parts.shift() : '';
        const msgs = [{ isText: true, lead: lead, paras: parts.length ? parts : [txt] }];
        if (wantsResume) msgs.push({ isActions: true, lead: 'Her resume, if it is useful:', actions: [ { text: 'Read online', href: this.RESUME_URL }, { text: 'Download PDF', href: this.RESUME_URL } ] });
        settled = true; clearTimeout(timer); finish(msgs);
      })
      .catch(() => { if (settled) return; settled = true; clearTimeout(timer); finish(fallbackMsgs); });
  }

  send(text, builderId) {"""

DASHES = [
 ("into agentic products people use and pay for — blank page to GA.", "into agentic products people use and pay for, from blank page to GA."),
 ("Thanks{{ leadFirstName }} — I'll pass this", "Thanks{{ leadFirstName }}. I'll pass this"),
 ("So I can tailor this — who am I speaking with?", "So I can tailor this: who am I speaking with?"),
 ("Got it — you're hiring.", "Got it, you're hiring."),
 ("Nice — you're building something.", "Nice, you're building something."),
 ("Love it — what brings you?", "Love it. What brings you?"),
 ("Recruiter mode — a fast screen", "Recruiter mode: a fast screen"),
 ("or a project — or paste a JD", "or a project, or paste a JD"),
 ("Executive mode — strategy, business impact", "Executive mode: strategy, business impact"),
 ("impact, or scale — or paste a JD", "impact, or scale, or paste a JD"),
 ("Builder mode — let's talk shop:", "Builder mode. Let's talk shop:"),
 ("Founder mode — how she takes", "Founder mode: how she takes"),
 ("PM-to-PM — happy to get into craft:", "PM-to-PM. Happy to get into craft:"),
 ("Ask about craft — scoping, evals, metrics", "Ask about craft: scoping, evals, metrics"),
 ("For events & podcasts — here is what", "For events & podcasts, here is what"),
 ("For press & writing — I can share", "For press & writing, I can share"),
 ("For students & mentees — happy to share", "For students & mentees, happy to share"),
 ("Ask me anything about Deepti — her work,", "Ask me anything about Deepti: her work,"),
 ("Short answer — a strong Senior,", "Short answer: a strong Senior,"),
 ("lead: 'Yes — actively open right now.'", "lead: 'Yes, actively open right now.'"),
 ("1 · She ships — Agent Builder", "1 · She ships. Agent Builder"),
 ("2 · She moves numbers — +11 pts CSAT", "2 · She moves numbers. +11 pts CSAT"),
 ("3 · Reach — AI she shipped", "3 · Reach. AI she shipped"),
 ("100M+ customers at Intuit — it lifted CSAT", "100M+ customers at Intuit. It lifted CSAT"),
 ("A representative one — capability vs. cost", "A representative one: capability vs. cost"),
 ("runaway token cost — both fatal", "runaway token cost, both fatal"),
 ("grew +79% MoM — because the thing people", "grew +79% MoM, because the thing people"),
 ("indicators are the business — CSAT, contact rate", "indicators are the business: CSAT, contact rate"),
 ("represents the work externally — C-suite reviews and conference stages.", "represents the work externally, in C-suite reviews and on conference stages."),
 ("let evals and experiments — not opinions — decide what ships.", "let evals and experiments, not opinions, decide what ships."),
 ("Intuit Assist before scale — which is how it landed", "Intuit Assist before scale, which is how it landed"),
 ("a measurable goal — not a feature list — and sequences", "a measurable goal, not a feature list, and sequences"),
 ("not afterthoughts — that is how Intuit Assist", "not afterthoughts, and that is how Intuit Assist"),
 ("over a broad, flaky one — protecting reliability", "over a broad, flaky one, protecting reliability"),
 ("token economics designed in — 40% lower token cost at GA.", "token economics designed in, giving 40% lower token cost at GA."),
 ("Evals are her quality bar — and her tie-breaker.", "Evals are her quality bar, and her tie-breaker."),
 ("running AI at scale — from executive reviews", "running AI at scale, from executive reviews"),
 ("measure what matters — grounded in shipping", "measure what matters, grounded in shipping"),
 ("riskiest unknowns first — cost and reliability — and made weekly evals", "riskiest unknowns first, cost and reliability, and made weekly evals"),
 ("over a broad-but-flaky one — protecting trust and unit cost", "over a broad-but-flaky one, protecting trust and unit cost"),
 ("unit economics are the product — not a follow-up.", "unit economics are the product, not a follow-up."),
 ("pressure to ship broadly — narrow-and-trustworthy beats", "pressure to ship broadly. Narrow-and-trustworthy beats"),
 ("support couldn't scale — inside a traditionally sales-led org", "support couldn't scale, inside a traditionally sales-led org"),
 ("with real metrics — concept", "with real metrics: concept"),
 ("regulated specifics — she ramps fast", "regulated specifics. She ramps fast"),
 ("what she is looking for — or you can paste a job description", "what she is looking for, or you can paste a job description"),
 ("title: 'Agent Builder — an agentic conversational AI platform'", "title: 'Agent Builder: an agentic conversational AI platform'"),
 ("monetization over breadth — shipping hosted", "monetization over breadth, shipping hosted"),
 ("biggest unlock wasn't a feature — it was unifying", "biggest unlock wasn't a feature. It was unifying"),
 ("the product rather than coverage — enriching models", "the product rather than coverage, enriching models"),
 ("paras: ['Sure — which role should I tailor for?']", "paras: ['Sure, which role should I tailor for?']"),
 ("paras: ['Happy to re-tailor — who am I speaking with?']", "paras: ['Happy to re-tailor. Who am I speaking with?']"),
 ("paras: ['No problem — who am I speaking with?']", "paras: ['No problem. Who am I speaking with?']"),
 ("her resume — how would you like it?", "her resume. How would you like it?"),
 ("So I can tailor this — pick one, or just ask", "So I can tailor this: pick one, or just ask"),
]


def main():
    h = open(PATH, encoding="utf-8").read()
    log, warn = [], []

    def patch(label, old, new):
        nonlocal h
        o, n = esc(old), esc(new)
        if n in h:
            log.append(label + ": already applied")
        elif o in h:
            h = h.replace(o, n)
            log.append(label + ": applied")
        else:
            warn.append(label + ": PATTERN NOT FOUND, the design may have changed")

    if 'property="og:title"' in h:
        log.append("metadata: already applied")
    else:
        if re.search(r"<title>.*?</title>", h, flags=re.S):
            h = re.sub(r"<title>.*?</title>", META, h, count=1, flags=re.S)
        else:
            h = h.replace("<head>", "<head>\n" + META, 1)
        log.append("metadata: applied")

    patch("zero-state starters", OLD_CHIPS, NEW_CHIPS)
    patch("agent methods", "  send(text, builderId) {", AGENT)
    patch("send() routes misses to the agent", OLD_SEND, NEW_SEND)
    patch("resume link",
          "RESUME_URL = 'https://www.deeptidheer.com';",
          "RESUME_URL = 'https://www.deeptidheer.com/resume.pdf';")

    fixed = 0
    for old, new in DASHES:
        eo = esc(old)
        if eo in h:
            h = h.replace(eo, esc(new))
            fixed += 1
    h, dates = re.subn(r"(\d{4})\s*–\s*(\d{4}|Present)", r"\1 to \2", h)
    log.append("dashes: %d rewritten, %d date ranges" % (fixed, dates))

    open(PATH, "w", encoding="utf-8").write(h)

    print("Post-processed", PATH)
    for l in log:
        print("  -", l)
    for w in warn:
        print("  ! ", w)
    left = len(re.findall(r"[—–]", h))
    print("  - dashes remaining: %d (expected 5, all inside the vendor bundler's code comments)" % left)
    if warn:
        sys.exit(1)


if __name__ == "__main__":
    main()
