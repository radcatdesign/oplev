// Vercel serverless function: POST /api/inquiry
// Emails each inquiry through Resend. Set these in Vercel > Settings > Environment Variables:
//   RESEND_API_KEY  your Resend API key
//   INQUIRY_TO      where inquiries go (comma-separated for several)
//   INQUIRY_FROM    optional sender, e.g. "OpLev <site@yourdomain.com>" (domain must be verified in Resend)
// Without RESEND_API_KEY and INQUIRY_TO it answers 503 and the page shows an email fallback.

const MAX = { name: 120, email: 200, company: 160, type: 80, type_other: 80, team: 40, license: 80, resale: 40, timing: 60, message: 4000 };
const LABELS = { company: 'Company', type: 'Business', team: 'Team size', build: 'Build', license: 'License', resale: 'Sell to others', timing: 'Start' };

const clean = (v, n) => String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, n);
const esc = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function parse(req) {
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  return b && typeof b === 'object' ? b : {};
}

function validate(b) {
  const v = {};
  for (const k of Object.keys(MAX)) v[k] = clean(b[k], MAX[k]);
  v.build = (Array.isArray(b.build) ? b.build : b.build ? [b.build] : []).map(x => clean(x, 40)).filter(Boolean).slice(0, 6).join(', ');
  v.name = v.name.replace(/[\r\n]+/g, ' ');
  v.company = v.company.replace(/[\r\n]+/g, ' ');
  v.type_other = v.type_other.replace(/[\r\n]+/g, ' ');
  if (v.type_other) v.type = v.type ? `${v.type}: ${v.type_other}` : v.type_other;
  if (!v.name || !v.message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.email)) {
    return { error: 'Add your name, a valid email and what still runs through you.' };
  }
  return { v };
}

function render(v) {
  const rows = Object.keys(LABELS).filter(k => v[k]).map(k => [LABELS[k], v[k]]);
  const text = `${v.name} <${v.email}>\n\n` + rows.map(([l, x]) => `${l}: ${x}`).join('\n') + `\n\nWhat still runs through them:\n${v.message}\n`;
  const html = `<div style="font-family:ui-monospace,Menlo,monospace;font-size:13px;line-height:1.6;color:#111">`
    + `<p><b>${esc(v.name)}</b> &lt;${esc(v.email)}&gt;</p>`
    + `<table cellpadding="4" style="border-collapse:collapse">${rows.map(([l, x]) => `<tr><td style="color:#666">${esc(l)}</td><td>${esc(x)}</td></tr>`).join('')}</table>`
    + `<p style="margin-top:16px;color:#666">What still runs through them:</p><p style="white-space:pre-wrap">${esc(v.message)}</p></div>`;
  return { text, html };
}

async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Use POST.' });
  }
  const b = parse(req);
  if (clean(b.company_url, 200)) return res.status(200).json({ ok: true }); // honeypot: quietly drop bots
  const { v, error } = validate(b);
  if (error) return res.status(400).json({ ok: false, error });

  const key = process.env.RESEND_API_KEY;
  const to = (process.env.INQUIRY_TO || '').split(',').map(s => s.trim()).filter(Boolean);
  if (!key || !to.length) return res.status(503).json({ ok: false, error: 'Inquiry email is not set up yet.' });

  const { text, html } = render(v);
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: process.env.INQUIRY_FROM || 'OpLev <onboarding@resend.dev>',
        to,
        reply_to: v.email,
        subject: `New inquiry: ${v.company || v.name}`,
        text,
        html,
      }),
    });
    if (!r.ok) return res.status(502).json({ ok: false, error: 'Could not send right now.' });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(502).json({ ok: false, error: 'Could not send right now.' });
  }
}

module.exports = handler;
module.exports._test = { validate, render };
