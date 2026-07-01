/* Deepti AI assistant — self-contained floating chat widget.
   Works on any page. Calls /api/chat (Anthropic, grounded) with a scripted fallback. */
(function () {
  var A = '#C8553D', INK = '#2B2622', CARD = '#FFFDF9', LINE = '#E7DDCD',
      SOFT = '#F3EDE3', MUT = '#6E665C', EMAIL = 'mailto:deepti.dheer1403@gmail.com';

  var CSS =
    '#dd-agent{position:fixed;right:20px;bottom:20px;z-index:2147483000;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}'
  + '#dd-launch{background:' + A + ';color:#fff;border:none;border-radius:999px;padding:13px 20px;font-size:14px;font-weight:600;cursor:pointer;box-shadow:0 10px 30px -10px rgba(200,85,61,.6)}'
  + '#dd-launch:hover{filter:brightness(1.05)}'
  + '#dd-panel{position:absolute;right:0;bottom:60px;width:360px;max-width:calc(100vw - 40px);height:520px;max-height:calc(100vh - 120px);background:' + CARD + ';border:1px solid ' + LINE + ';border-radius:16px;box-shadow:0 24px 60px -20px rgba(60,40,20,.4);display:flex;flex-direction:column;overflow:hidden}'
  + '#dd-panel[hidden]{display:none}'
  + '.dd-head{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid ' + LINE + ';font-weight:600;color:' + INK + ';font-size:14px}'
  + '.dd-close{background:none;border:none;font-size:20px;line-height:1;color:' + MUT + ';cursor:pointer}'
  + '.dd-chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}'
  + '.dd-msg{max-width:90%;padding:11px 14px;border-radius:14px;font-size:14px;line-height:1.5}'
  + '.dd-msg.bot{align-self:flex-start;background:' + SOFT + ';border:1px solid ' + LINE + ';color:' + INK + ';border-bottom-left-radius:4px}'
  + '.dd-msg.user{align-self:flex-end;background:' + A + ';color:#fff;border-bottom-right-radius:4px}'
  + '.dd-msg.typing{color:' + MUT + ';font-style:italic;letter-spacing:3px}'
  + '.dd-msg a.cta{display:inline-block;margin-top:8px;background:' + A + ';color:#fff;padding:7px 12px;border-radius:8px;font-size:12.5px;font-weight:600;text-decoration:none}'
  + '.dd-starters{display:flex;flex-wrap:wrap;gap:7px;padding:0 16px 10px}'
  + '.dd-chip{font-family:inherit;font-size:12.5px;color:' + A + ';background:rgba(200,85,61,.08);border:1px solid ' + LINE + ';border-radius:999px;padding:7px 11px;cursor:pointer}'
  + '.dd-chip:hover{border-color:' + A + '}'
  + '.dd-input{display:flex;gap:7px;padding:12px 16px;border-top:1px solid ' + LINE + '}'
  + '.dd-input input{flex:1;font-family:inherit;font-size:14px;padding:10px 12px;border:1px solid ' + LINE + ';border-radius:10px;outline:none;background:#fff;color:' + INK + '}'
  + '.dd-input input:focus{border-color:' + A + '}'
  + '.dd-input button{background:' + A + ';color:#fff;border:none;border-radius:10px;padding:0 15px;font-weight:600;font-size:13px;cursor:pointer;font-family:inherit}';

  var fb = {
    shipped:  { a: "Over the last decade I've taken products from zero to one at Elastic, Intuit, and NetApp, including an agentic AI platform I took to GA in three months and Intuit Assist, which reached 100M+ customers.", c: null },
    approach: { a: "I start from the customer and work backward, steer with data and clear goals, and use AI to ship faster at higher quality. Customer obsession, evidence over opinion, economics from day one.", c: null },
    tech:     { a: "Very. A technical PM hands-on with RAG, evals, context engineering, and LLM tooling, who prototypes in Claude Code and Cursor and architects alongside engineering.", c: null },
    tradeoff: { a: "On Elastic Agent Builder I shipped monetization in month five before broadening features; on Intuit Assist I accepted a slower rollout to get AI safety and grounding right. I optimize for the one or two bets that move the metric.", c: null },
    agentic:  { a: "I led Elastic's Agent Builder, a zero-to-one agentic platform, and built an AI agent at Intuit that chases overdue invoices and gets businesses paid five days faster.", c: null },
    open:     { a: "Always glad to connect with people building bold AI products. Details like comp and timing are best discussed directly, the fastest way is email or a quick call.", c: ['Email Deepti', EMAIL] }
  };
  function match(t) {
    t = (t || '').toLowerCase();
    if (/(comp|salary|visa|sponsor|relocat|authoriz|why (are you )?leav|notice)/.test(t)) return fb.open;
    if (/(hir|hiring|opportun|\brole|\bjob|avail|open to|reach|contact|email|team|join)/.test(t)) return fb.open;
    if (/(technical|engineer|hands.?on|\bstack\b|architect|code)/.test(t)) return fb.tech;
    if (/(tradeoff|trade-off|hard (call|decision|choice)|failure|differently|mistake)/.test(t)) return fb.tradeoff;
    if (/(agent|agentic|\bai\b|\bllm|\brag\b|gen ?ai|automat|eval|assistant)/.test(t)) return fb.agentic;
    if (/(approach|process|philosoph|how do you|framework|think|prioriti|method)/.test(t)) return fb.approach;
    if (/(ship|built|build|\bwork|product|experien|project|intuit|elastic|netapp|metric|impact|result)/.test(t)) return fb.shipped;
    return null;
  }

  var chatEl, hist = [], live = true;
  function add(text, cls, cta) {
    var d = document.createElement('div');
    d.className = 'dd-msg ' + cls; d.textContent = text;
    if (cta) {
      var a = document.createElement('a');
      a.className = 'cta'; a.href = cta[1]; a.textContent = cta[0] + ' →';
      if (cta[1].slice(-4) === '.pdf') a.setAttribute('download', 'Deepti-Dheer-Resume.pdf');
      a.target = '_blank'; a.rel = 'noopener';
      d.appendChild(document.createElement('br')); d.appendChild(a);
    }
    chatEl.appendChild(d); chatEl.scrollTop = chatEl.scrollHeight; return d;
  }
  function parse(t) {
    var m = t.match(/\[\[action:(?:navigate:\w+|(resume|email))\]\]\s*$/i);
    if (!m) return { clean: t.trim(), cta: null };
    var k = (m[1] || '').toLowerCase(), cta = null;
    if (k === 'resume') cta = ['Download resume', 'resume.pdf'];
    else if (k === 'email') cta = ['Email Deepti', EMAIL];
    return { clean: t.replace(m[0], '').trim(), cta: cta };
  }
  function scripted(t) {
    var r = match(t);
    add(r ? r.a : "Great question. The best next step is a quick chat, reach me by email or LinkedIn.", 'bot', r ? r.c : ['Email Deepti', EMAIL]);
  }
  function ask(text) {
    add(text, 'user'); hist.push({ role: 'user', content: text });
    var ty = add('…', 'bot typing');
    if (live) {
      fetch('/api/chat', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ messages: hist }) })
        .then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(function (d) { if (!d || !d.reply) throw 0; ty.remove(); var p = parse(d.reply); add(p.clean, 'bot', p.cta); hist.push({ role: 'assistant', content: d.reply }); })
        .catch(function () { live = false; ty.remove(); scripted(text); });
    } else { ty.remove(); scripted(text); }
  }

  function init() {
    if (document.getElementById('dd-agent')) return;
    var st = document.createElement('style'); st.textContent = CSS; document.head.appendChild(st);
    var root = document.createElement('div'); root.id = 'dd-agent';
    root.innerHTML =
        '<div id="dd-panel" hidden>'
      +   '<div class="dd-head"><span>Ask the AI assistant</span><button class="dd-close" aria-label="Close">×</button></div>'
      +   '<div class="dd-chat" id="dd-chat"><div class="dd-msg bot">Hi, I am the AI assistant for Deepti, grounded in her real experience. Ask me about her work, approach, or what she is looking for.</div></div>'
      +   '<div class="dd-starters">'
      +     '<button class="dd-chip">Most impactful product?</button>'
      +     '<button class="dd-chip">How technical are you?</button>'
      +     '<button class="dd-chip">A hard tradeoff you made?</button>'
      +     '<button class="dd-chip">Open to new roles?</button>'
      +   '</div>'
      +   '<form class="dd-input" id="dd-form"><input id="dd-in" placeholder="Ask a question..." autocomplete="off"><button type="submit">Send</button></form>'
      + '</div>'
      + '<button id="dd-launch">Ask my AI assistant</button>';
    document.body.appendChild(root);
    chatEl = document.getElementById('dd-chat');
    var panel = document.getElementById('dd-panel');
    document.getElementById('dd-launch').addEventListener('click', function () { panel.hidden = !panel.hidden; if (!panel.hidden) document.getElementById('dd-in').focus(); });
    root.querySelector('.dd-close').addEventListener('click', function () { panel.hidden = true; });
    root.querySelectorAll('.dd-chip').forEach(function (b) { b.addEventListener('click', function () { ask(b.textContent); }); });
    document.getElementById('dd-form').addEventListener('submit', function (e) { e.preventDefault(); var v = document.getElementById('dd-in').value.trim(); if (!v) return; document.getElementById('dd-in').value = ''; ask(v); });
  }
  if (document.readyState === 'loading') window.addEventListener('DOMContentLoaded', function () { setTimeout(init, 700); });
  else setTimeout(init, 700);
})();
