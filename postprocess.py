#!/usr/bin/env python3
"""
Post-process a fresh design export (index.html) so it's production-ready.
Re-applies the two pieces of "wiring" that a design-tool export does not include:
  1. SEO / social metadata (title, viewport, description, Open Graph, favicon, JSON-LD)
  2. The chat bridge: window.claude.complete -> your own /api/chat agent (with fallback)

Safe to run repeatedly (idempotent): it skips anything already applied.

Usage:
    python3 postprocess.py            # processes ./index.html in place
    python3 postprocess.py somefile.html
"""
import re, sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "index.html"

META = '''<title>Deepti Dheer, AI Product Leader | AI Product Manager, Agentic AI & LLMs</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Portfolio of Deepti Dheer, an AI Product Leader shipping Generative and Agentic AI products to 100M+ users. Agentic AI, LLMs, RAG, evals, pricing, and 0-to-1 product strategy.">
<link rel="canonical" href="https://www.deeptidheer.com/">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23C8553D'/%3E%3Ctext x='32' y='45' font-family='Georgia,serif' font-size='32' font-weight='bold' fill='white' text-anchor='middle'%3EDD%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.deeptidheer.com/">
<meta property="og:title" content="Deepti Dheer, AI Product Leader">
<meta property="og:description" content="AI Product Leader shipping Generative and Agentic AI products to 100M+ users. Agentic AI, LLMs, RAG, and 0-to-1 product strategy.">
<meta property="og:image" content="https://www.deeptidheer.com/og-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Deepti Dheer, AI Product Leader">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Deepti Dheer, AI Product Leader">
<meta name="twitter:description" content="AI Product Leader shipping Generative and Agentic AI products to 100M+ users.">
<meta name="twitter:image" content="https://www.deeptidheer.com/og-card.jpg">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Person","name":"Deepti Dheer","jobTitle":"AI Product Leader","url":"https://www.deeptidheer.com/","sameAs":["https://www.linkedin.com/in/deeptidheer/"],"knowsAbout":["Agentic AI","Generative AI","Product Management","RAG","LLMs","AI Evaluations","Conversational AI","Go-to-Market Strategy"],"alumniOf":"University of San Francisco","address":{"@type":"PostalAddress","addressLocality":"San Francisco Bay Area","addressRegion":"CA","addressCountry":"US"}}</script>'''

BRIDGE = r'''<script>
/* Bridge: the design's chat calls window.claude.complete(prompt).
   Route it to Deepti's own agent (/api/chat) with a scripted fallback. */
(function(){
  function lastRecruiter(p){
    var lines=String(p).split(/\n/), last='';
    for(var i=0;i<lines.length;i++){var m=lines[i].match(/^\s*Recruiter:\s*(.+)/i); if(m) last=m[1];}
    return (last||String(p)).toLowerCase();
  }
  function fallback(p){
    var q=lastRecruiter(p);
    if(/comp|salary|visa|sponsor|relocat|authoriz|why (are you )?leav|notice/.test(q)) return "Always glad to connect. Details like compensation and timing are best discussed directly, the fastest way is email or a quick call at deepti.dheer1403@gmail.com.";
    if(/technical|engineer|hands.?on|stack|architect|\bcode\b/.test(q)) return "Very. Deepti is a technical PM, hands-on with RAG, evals, context engineering, and LLM tooling, who prototypes in Claude Code and Cursor and architects alongside engineering.";
    if(/tradeoff|trade-off|hard (call|decision|choice)|failure|differently|mistake/.test(q)) return "On Elastic Agent Builder she shipped monetization in month five before broadening features; on Intuit Assist she accepted a slower rollout to get AI safety and grounding right. She optimizes for the one or two bets that move the metric.";
    if(/agent|agentic|\bai\b|\bllm\b|\brag\b|gen ?ai|automat|\beval/.test(q)) return "She led Elastic's Agent Builder, a zero-to-one agentic platform, and built an AI agent at Intuit that chases overdue invoices and gets businesses paid five days faster.";
    if(/approach|process|philosoph|how do you|framework|think|prioriti|method/.test(q)) return "She starts from the customer and works backward, steers with data and clear goals, and uses AI to ship faster at higher quality: customer obsession, evidence over opinion, economics from day one.";
    if(/measure|success|metric|kpi|north ?star/.test(q)) return "She sets a clear north-star metric (like digital help resolution rate for Intuit Assist) with health and guardrail metrics such as helpfulness, fallback rate, escalation, and CSAT, then validates with rigorous A/B testing.";
    if(/ship|built|build|\bwork|product|experien|project|intuit|elastic|netapp|metric|impact|result/.test(q)) return "Over the last decade she has taken products from zero to one at Elastic, Intuit, and NetApp, including an agentic AI platform taken to GA in three months and Intuit Assist, which reached 100M+ customers.";
    return "Great question. The best next step is a quick chat, reach Deepti at deepti.dheer1403@gmail.com.";
  }
  window.claude = window.claude || {};
  window.claude.complete = async function(prompt){
    try{
      var r = await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({messages:[{role:'user',content:String(prompt)}],persona:(window.__persona||'')})});
      if(!r.ok) throw new Error('http');
      var d = await r.json();
      var t = (d && d.reply) ? String(d.reply) : '';
      t = t.replace(/\[\[action:[^\]]*\]\]\s*$/i,'').trim();
      if(!t) throw new Error('empty');
      return t;
    }catch(e){ return fallback(prompt); }
  };
})();
</script>'''

def main():
    h = open(PATH, encoding="utf-8").read()
    changed = []

    # 1) Metadata (idempotent: keyed on og:title)
    if 'property="og:title"' not in h:
        if re.search(r"<title>.*?</title>", h, flags=re.S):
            h = re.sub(r"<title>.*?</title>", META, h, count=1, flags=re.S)
        else:  # no title at all -> put block right after <head>
            h = h.replace("<head>", "<head>\n" + META, 1)
        changed.append("metadata (title, viewport, description, OG, favicon, JSON-LD)")
    else:
        changed.append("metadata: already present (skipped)")

    # 2) Chat bridge (idempotent: keyed on window.claude)
    if "window.claude" not in h:
        i = h.rfind("</head>")
        if i != -1:
            h = h[:i] + BRIDGE + "\n" + h[i:]
            changed.append("chat bridge (window.claude -> /api/chat)")
        else:
            changed.append("chat bridge: NO </head> found, NOT applied")
    else:
        changed.append("chat bridge: already present (skipped)")

    open(PATH, "w", encoding="utf-8").write(h)
    print("Post-processed", PATH)
    for c in changed:
        print("  -", c)

if __name__ == "__main__":
    main()
