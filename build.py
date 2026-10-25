#!/usr/bin/env python3
"""Build the OpLev site into self-contained HTML pages.

Edit content/cases.json, src/site.css or src/site.js, then run:
    python3 build.py
Outputs index.html, pricing.html, work.html, start.html, setups.html, setups/<type>.html,
app.html (the Console demo) and work/<case>.html at the repo root.
Optional: python3 build.py --preview PATH writes an artifact-ready copy of the home page.
"""
import json, sys, pathlib
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent
CASES = json.loads((ROOT / 'content' / 'cases.json').read_text())
CSS = (ROOT / 'src' / 'site.css').read_text()
JS = (ROOT / 'src' / 'site.js').read_text()
APP_CSS = (ROOT / 'src' / 'app.css').read_text()
APP_JS = (ROOT / 'src' / 'app.js').read_text()
SETUPS = json.loads((ROOT / 'content' / 'setups.json').read_text())
SETUP = {x['id']: x for x in SETUPS}
LICENSES = {'one': {'name': 'One engine', 'price': '$5k', 'count': 1},
            'core': {'name': 'Two engines', 'price': '$10k', 'count': 2},
            'company': {'name': 'All three', 'price': '$15k+', 'count': 3}}

EMAIL = 'hello@oplev.com'
LOCATION = 'Bend, Oregon'
BUILD = '2026.10'
FONTS = ('https://fonts.googleapis.com/css2?family=Doto:wght@900&family=Geist:wght@300..600'
         '&family=Martian+Mono:wdth,wght@75..112.5,100..800&display=swap')
SEED = {c['id']: i + 1 for i, c in enumerate(CASES)}
BY_ID = {c['id']: c for c in CASES}


def E(s):
    return escape(str(s), quote=True)


def svg(d):
    return ('<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.4" '
            'aria-hidden="true"><path d="' + d + '"/></svg>')


ARR_R = svg('M2.5 7h9M8 3.5 11.5 7 8 10.5')
ARR_L = svg('M11.5 7h-9M6 3.5 2.5 7 6 10.5')
ARR_D = svg('M7 2.5v9M3.5 8 7 11.5 10.5 8')
COPY = svg('M4.5 4.5V2h7.5v7.5H9.5M2 4.5h7.5V12H2z')
MARK = ('<svg class="mark" viewBox="0 0 10 10" aria-hidden="true"><path fill="#F2F2EF" '
        'd="M0 0h10v2H0zM0 8h10v2H0zM0 2h2v6H0zM8 2h2v6H8zM4 4h2v2H4z"/></svg>')
BOOT = ("(function(){var d=document.documentElement,rm=false,seen=false;"
        "try{rm=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}"
        "try{seen=sessionStorage.getItem('oplev-boot')==='1'}catch(e){}"
        "d.classList.add(rm?'rm':(seen?'booted':'is-loading'))})();")
TICKS = '<span class="tk a"></span><span class="tk b"></span><span class="tk c"></span><span class="tk d"></span>'


# ---------- content ----------

ENGINES = [
    ('ops', 'Ops', 'system', 'Stay organized', 'Keeps your schedule, clients, orders and numbers in one place.',
     ['Your schedule, clients and orders in one place', 'A daily summary of what needs you',
      'One place your team can look up how things are done', 'A score that shows what still depends on you'],
     ['adessa-mind', 'art-of-practice']),
    ('agents', 'Agents', 'agent', 'Handle the busywork', 'Answers, books, reminds and follows up, and checks with you first.',
     ['Answers new inquiries and books appointments', 'Sends reminders and follow-ups',
      'Drafts replies and reports for you to check', 'Asks before anything important goes out'],
     ['adessa-mind', 'jason-stephenson']),
    ('leads', 'Leads', 'lead', 'Win more customers', 'Turns website visitors into real conversations.',
     ['Price calculators and quote tools', 'A helper on your site that answers questions any hour',
      'Quotes customers can accept online', 'Every new lead saved with the full conversation'],
     ['element-glo']),
]
ENGINE_NAME = {k: n for k, n, *_ in ENGINES}

PLAYS = [
    ('leads', 'when a form or chat comes in', 'Fast replies to new leads', 'Answers in minutes with the right info and a link to book, day or night.'),
    ('leads', 'on your website', 'Instant price quotes', 'Customers price the job themselves, and you get their details.'),
    ('leads', 'on your website', 'Preview before buying', 'Customers see what the finished result will look like before they call.'),
    ('agents', '3 days after a quote', 'Quote follow-ups', 'Checks in on open quotes before they go cold.'),
    ('agents', 'when someone misses an appointment', 'Missed appointment rebooking', 'Reaches out the same day and offers a new time.'),
    ('agents', '7 days after an invoice is due', 'Unpaid invoice reminders', 'Polite reminders first, then a heads-up to you.'),
    ('agents', 'after a job is done', 'Review requests', 'Asks happy customers for a review at the right moment.'),
    ('agents', 'first of the month', 'Monthly investor update', "Drafts the update from the month's numbers for you to edit."),
    ('ops', 'every morning at 6', 'Morning summary', 'What happened overnight and what needs you, on one screen.'),
    ('ops', 'every Monday', 'Weekly numbers', 'Sales, open jobs and money in, without building a report.'),
    ('ops', 'when someone joins', 'New hire setup', 'Accounts, guides and first-week tasks, set up the same way every time.'),
    ('ops', 'when stock runs low', 'Low stock alerts', 'Drafts the reorder before you run out, then waits for your OK.'),
]

NIGHT = {
    'cmd': 'Last night, 10pm to 7am',
    'run': [
        ['22:41:07', '@leads', 'visitor priced a project with the calculator', 'lead saved'],
        ['22:41:09', '@ops', 'lead added to the pipeline with the estimate', 'linked'],
        ['22:43:30', '@agents', 'drafted a reply with the estimate', 'drafted'],
        ['23:58:12', '@agents', 'sorted 14 messages into clients, vendors and noise', 'sorted'],
        ['01:12:40', '@ops', 'invoice paid, client record updated', 'reconciled'],
        ['03:30:00', '@agents', 'flagged a late invoice for follow-up', 'queued'],
        ['05:45:00', '@ops', 'morning summary ready: 1 approval, 2 new leads', 'ready'],
        ['06:58:21', 'you', 'approve reply to the new lead', 'pending', 'need'],
        ['07:04:02', 'you', 'approved over coffee', 'ok', 'me'],
        ['07:04:04', '@agents', 'sent the reply and a booking link', 'sent'],
    ],
}

PAINS = [
    ('Everything still runs through me.', 'the Ops engine'),
    ('I pay for a stack of apps and still live in spreadsheets.', 'one system'),
    ('Leads come in at night and sit until Monday.', 'the Leads engine'),
    ('Only one person knows how that part works.', 'the Ops engine'),
    ("I can't take a week off.", 'the Agents engine'),
    ('People keep asking if they can use what I built.', 'a resale license'),
]

CMP_HEAD = ('Off-the-shelf apps', 'One-off agency build', 'OpLev, monthly')
CMP = [
    ('Built around how you work', 'No. You work around it.', 'Yes', 'Yes'),
    ('How you pay', 'Per app, per person, every month', 'A big build fee, then hourly fixes', 'One monthly price'),
    ('Who keeps it running', 'You do', 'You, or a developer you hire', 'We do'),
    ('Gets better over time', 'On their roadmap, not yours', 'Only when you pay for it', 'Updates included'),
    ('Can you sell it', 'No', 'Depends on your contract', 'Yes, with a resale license'),
]

F_TYPE = [('clinic', 'Clinic or practice'), ('brand', 'Product brand'), ('agency', 'Agency or service firm'),
          ('creator', 'Creator or media'), ('startup', 'Startup'), ('other', 'Something else')]
F_TEAM = [('1', 'Just me'), ('2-5', '2 to 5'), ('6-20', '6 to 20'), ('21-50', '21 to 50'), ('50', '50+')]
F_BUILD = [('ops', 'Staying organized (Ops)'), ('agents', 'Busywork and follow-ups (Agents)'), ('leads', 'Getting more customers (Leads)'),
           ('unsure', 'Not sure yet')]
F_LICENSE = [('one', 'One engine / $5k'), ('core', 'Two engines / $10k'), ('company', 'All three / $15k+'),
             ('unsure', 'Not sure yet')]
F_RESALE = [('yes', 'Yes'), ('later', 'Maybe later'), ('no', 'No')]
F_TIMING = [('month', 'This month'), ('quarter', 'This quarter'), ('exploring', 'Just exploring')]


# ---------- shared shell ----------

def nav_items(p, home):
    a = (lambda h: h) if home else (lambda h: p + 'index.html' + h)
    return [
        ('work', 'Work', p + 'work.html', 'case studies', False),
        ('engines', 'How it works', a('#engines'), 'the engines', False),
        ('setups', "Who it's for", p + 'setups.html', 'by business', False),
        ('pricing', 'Pricing', p + 'pricing.html', 'plans', False),
        ('demo', 'Demo', p + 'app.html', 'try it', False),
        ('contact', 'Contact', p + 'start.html', 'get in touch', True),
    ]


def shell_top(p, home, active):
    items = nav_items(p, home)
    cur = lambda k: ' aria-current="page"' if k == active else ''
    links = ''.join(f'\n      <a href="{h}"{cur(k)}>{t}</a>' for k, t, h, _, menu_only in items if not menu_only)
    menu = ''.join(
        f'\n        <li><a href="{h}"{cur(k)}><span class="mn">{i + 1:02d}</span>'
        f'<span class="mt">{t}</span><span class="mp">{pth}</span></a></li>'
        for i, (k, t, h, pth, _m) in enumerate(items))
    brand = '#hero' if home else p + 'index.html'
    return f'''<div class="loader" id="loader" aria-hidden="true">
  <div class="ld-top">
    <span class="brand">{MARK}OPLEV</span>
    <span class="label">oplev / loading</span>
  </div>
  <div class="ld-bot">
    <div class="ld-row">
      <pre class="ld-log" id="ld-log"></pre>
      <div class="ld-n" id="ld-n">000</div>
    </div>
    <div class="ld-track"><div class="ld-fill" id="ld-fill"></div></div>
  </div>
</div>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="{brand}" aria-label="OpLev home">{MARK}<span class="brand-t">OPLEV</span></a>
    <nav class="links" aria-label="Sections">{links}
    </nav>
    <div class="nav-r">
      <span class="clock" data-clock></span>
      <a class="btn btn-sm nav-cta" href="{p}start.html">Start a project</a>
      <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="bars" aria-hidden="true"></span><span class="mb-t">Menu</span></button>
    </div>
  </div>
</header>

<div class="menu" id="menu" hidden>
  <div class="wrap">
    <nav aria-label="Menu">
      <ul class="menu-list">{menu}
      </ul>
    </nav>
    <div class="menu-foot label"><span>{EMAIL}</span><span class="clock" data-clock></span></div>
  </div>
</div>
'''


def shell_bottom():
    return f'''
<footer class="foot">
  <div class="wrap">
    <p class="wm" id="wm"><span id="wm-t">OPLEV</span></p>
    <div class="frow label">
      <span>OpLev</span>
      <span>Ops / Agents / Leads</span>
      <span>{E(LOCATION)}</span>
      <span class="clock" data-clock></span>
      <span data-year>2026</span>
    </div>
  </div>
</footer>
'''


def page(title, desc, body, p='', home=False, active=None, data='', mode='full'):
    head = (f'<title>{E(title)}</title>\n'
            f'<meta name="description" content="{E(desc)}">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<script>{BOOT}</script>\n'
            f'<style>\n{CSS}</style>\n')
    content = (shell_top(p, home, active) + '\n<main>\n' + body + '\n</main>\n' + shell_bottom()
               + data + f'\n<script>\n{JS}</script>\n')
    if mode == 'artifact':
        head = head.replace('</title>\n', '</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n', 1)
        return head + '\n' + content
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + '</head>\n<body>\n' + content + '</body>\n</html>\n')


# ---------- parts ----------

def mini(c, seed, p):
    inner = (f'<img src="{E(p + c["img"])}" alt="">' if c.get('img')
             else f'<canvas data-seed="{seed}"></canvas>')
    return f'<span class="mini" aria-hidden="true">{inner}</span>'


def thumb(c, seed, p, tags=True):
    if c.get('img'):
        return f'<figure class="thumb"><img src="{E(p + c["img"])}" alt="{E(c["name"])} case image" loading="lazy"></figure>'
    t = TICKS + ('<span class="tag tl label">case image / placeholder</span>'
                 '<span class="tag br label">1600 x 900</span>' if tags else '')
    return (f'<figure class="thumb" role="img" aria-label="Placeholder image for the {E(c["name"])} case">'
            f'<canvas data-seed="{seed}"></canvas>{t}</figure>')


def case_href(c, p=''):
    return f'{p}work/{c["id"]}.html'


def etags(keys, extra=''):
    if not keys:
        return ''
    return f'<span class="etags{extra}">' + ''.join(
        f'<span class="etag e-{k}">{ENGINE_NAME[k]}</span>' for k in keys if k in ENGINE_NAME) + '</span>'


def cta(title, text, p):
    return f'''
<section class="sec" id="next" aria-labelledby="next-h">
  <div class="wrap stack">
    <p class="eyebrow">Next step</p>
    <h2 class="h2" id="next-h">{title}</h2>
    <p class="lede">{text}</p>
    <div class="actions">
      <a class="btn" href="{p}start.html">Start a project {ARR_R}</a>
      <a class="btn ghost" href="{p}pricing.html">See licenses {ARR_R}</a>
    </div>
  </div>
</section>'''


def opts(name, items, kind='radio'):
    return ''.join(
        f'<label class="opt"><input type="{kind}" id="inq-{name}-{v}" name="{name}" value="{E(t)}"><span>{E(t)}</span></label>'
        for v, t in items)


def inquiry(level='h2', heading='Tell us what still runs through you.',
            lede='Two minutes. We read every one, and Andre or Matt replies personally.'):
    first = level == 'h1'
    hid = 'h1' if first else 'start-h'
    cursor = '<span class="cursor" aria-hidden="true"></span>' if first else ''
    cls = 'inq-page' if first else 'sec'
    return f'''
<section class="{cls}" id="start" aria-labelledby="{hid}">
  <div class="wrap inq-wrap">
    <div class="inq-side">
      <p class="eyebrow">Start a project</p>
      <{level} class="{level}" id="{hid}">{heading}{cursor}</{level}>
      <p class="lede">{lede}</p>
      <ol class="next">
        <li><span class="nx-n" aria-hidden="true">01</span><div><h3 class="h3">We read it</h3><p>A real reply from one of the two people who will build your system.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">02</span><div><h3 class="h3">A short call</h3><p>We talk through what still runs through you and what it costs you.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">03</span><div><h3 class="h3">Where to start</h3><p>We look at what still depends on you and pick the first thing to fix.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">04</span><div><h3 class="h3">Your plan</h3><p>What we'd build, what it costs each month, and when it goes live.</p></div></li>
      </ol>
      <p class="label inq-alt">Prefer email? <span class="sel">{EMAIL}</span></p>
    </div>
    <form class="inq" action="/api/inquiry" method="post" novalidate data-email="{EMAIL}" aria-label="Project inquiry">
      <div class="inq-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">New project</span><span class="label">* required</span></div>
      <div class="inq-grid">
        <label class="fl"><span class="label" data-err="add your name">Name *</span><input class="inp" id="inq-name" name="name" autocomplete="name" maxlength="120" required></label>
        <label class="fl"><span class="label" data-err="add a valid email">Email *</span><input class="inp" id="inq-email" name="email" type="email" autocomplete="email" maxlength="200" required></label>
      </div>
      <label class="fl"><span class="label">Company</span><input class="inp" id="inq-company" name="company" autocomplete="organization" maxlength="160"></label>
      <fieldset class="fs"><legend class="label">What kind of business?</legend><div class="opts">{opts('type', F_TYPE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">Team size</legend><div class="opts">{opts('team', F_TEAM)}</div></fieldset>
      <label class="fl"><span class="label" data-err="tell us a little">What still runs through you? *</span><textarea class="inp" id="inq-message" name="message" rows="5" maxlength="4000" required placeholder="The work that only happens when you're there."></textarea></label>
      <fieldset class="fs"><legend class="label">What do you need help with?</legend><div class="opts">{opts('build', F_BUILD, 'checkbox')}</div></fieldset>
      <fieldset class="fs"><legend class="label">Which plan sounds right?</legend><div class="opts">{opts('license', F_LICENSE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">Would you want to sell it to others one day?</legend><div class="opts">{opts('resale', F_RESALE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">When do you want to start?</legend><div class="opts">{opts('timing', F_TIMING)}</div></fieldset>
      <div class="hp" aria-hidden="true"><label>Leave this empty <input id="inq-hp" name="company_url" tabindex="-1" autocomplete="off"></label></div>
      <div class="inq-foot"><button class="btn" type="submit">Send inquiry {ARR_R}</button><p class="label">No mailing list. Just a reply.</p></div>
      <div class="inq-status" aria-live="polite" hidden></div>
    </form>
  </div>
</section>'''


# ---------- home ----------

def home(mode='full'):
    n = len(CASES)
    hindex = ''.join(
        (f'<i aria-hidden="true">/</i>' if i else '') +
        f'<a href="{case_href(c)}"><span>{i + 1:02d}</span>{E(c["name"])}</a>'
        for i, c in enumerate(CASES))
    rows = ''.join(
        f'''
          <a class="case-row{' on' if i == 0 else ''}" href="{case_href(c)}" data-seed="{i + 1}" data-id="{E(c['id'])}" data-n="{i + 1:02d}" data-name="{E(c['name'])}" data-sum="{E(c['summary'])}" data-img="{E(c.get('img', ''))}">
            <span class="n">{i + 1:02d}</span>{mini(c, i + 1, '')}<span class="nm h3">{E(c['name'])}</span><span class="mt label">{E(c['focus'])}</span>
            <span class="ln">{E(c['line'])}</span>
          </a>''' for i, c in enumerate(CASES))
    c0 = CASES[0]
    pv_fig = (f'<figure class="thumb" role="img" aria-label="Case image preview"><canvas data-seed="1"></canvas>'
              f'<img alt="" hidden>{TICKS}<span class="tag tl label">case image / placeholder</span>'
              f'<span class="tag br label">1600 x 900</span></figure>')
    pains = ''.join(
        f'\n        <li class="ck" data-by="{E(by)}"><span class="b">[ ]</span><span class="txw"><span class="tx">“{E(t)}”</span></span><span class="by label"></span></li>'
        for t, by in PAINS)
    tabs = ''.join(
        f'<button class="tab" type="button" role="tab" id="tab-{x["id"]}" aria-controls="panel-{x["id"]}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{E(x["type"])}</button>'
        for i, x in enumerate(SETUPS))
    panels = ''
    for i, x in enumerate(SETUPS):
        k = x['id']
        lis = ''.join(f'<li>{E(u[2])}<span class="rl-tag">{etags([u[0]])}</span></li>' for u in x['uses'][:4])
        seen = ''.join(
            f'<a href="{case_href(BY_ID[cid])}">{mini(BY_ID[cid], SEED[cid], "")}<span class="h3">{E(BY_ID[cid]["name"])}</span><span class="go">{ARR_R}</span></a>'
            for cid in x['cases'] if cid in BY_ID)
        L = LICENSES[x['license']]
        panels += f'''
      <div class="fpanel" role="tabpanel" id="panel-{k}" aria-labelledby="tab-{k}"{'' if i == 0 else ' hidden'}>
        <div class="fp-l">
          <div class="fp-top"><span class="label">{E(L['name'])} / {E(L['price'])} a month</span>{etags(x['engines'])}</div>
          <h3 class="h3 fp-name">{E(x['name'])}</h3>
          <p class="fp-pitch">{E(x['pitch'])}</p>
          <ul class="rowlist">{lis}</ul>
        </div>
        <div class="fp-r">
          <span class="label">our work for</span>
          <div class="seen">{seen}</div>
          <div class="actions fp-act"><a class="btn" href="setups/{k}.html">See the setup {ARR_R}</a><a class="btn ghost" href="app.html#{k}">Try the demo {ARR_R}</a></div>
        </div>
      </div>'''
    engines = ''.join(f'''
      <article class="eng e-{k}" id="engine-{k}">
        <div class="eng-top"><svg class="px" data-icon="{icon}" viewBox="0 0 50 50" aria-hidden="true"></svg><span class="label">engine {i + 1}</span></div>
        <h3 class="eng-name">{E(name)}</h3>
        <p class="eng-triad">{E(triad)}</p>
        <p class="eng-line">{E(line)}</p>
        <ul class="rowlist">{''.join(f'<li>{E(x)}</li>' for x in caps)}</ul>
        <div class="eng-seen"><span class="label">see it in</span>{''.join(f'<a href="{case_href(BY_ID[cid])}">{E(BY_ID[cid]["name"])}</a>' for cid in seen if cid in BY_ID)}</div>
      </article>''' for i, (k, name, icon, triad, line, caps, seen) in enumerate(ENGINES))
    filters = '<button class="tab" type="button" aria-pressed="true" data-f="all">All</button>' + ''.join(
        f'<button class="tab e-{k}" type="button" aria-pressed="false" data-f="{k}">{E(name)}</button>' for k, name, *_ in ENGINES)
    plays = ''.join(f'''
      <li class="play e-{k}" data-e="{k}"><div class="play-top">{etags([k])}<span class="label play-trig">{E(trig)}</span></div><h3 class="h3">{E(title)}</h3><p>{E(desc)}</p></li>'''
                    for k, trig, title, desc in PLAYS)
    night = json.dumps(NIGHT).replace('</', '<\\/')
    body = f'''
<section class="hero" id="hero">
  <canvas class="field" id="field" aria-hidden="true"></canvas>
  <div class="wrap">
    <span class="readout label" id="readout" aria-hidden="true">x 0000 · y 0000</span>
    <p class="eyebrow">Software for small businesses</p>
    <h1 class="h1" id="h1">Your business shouldn't need you for everything.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">We build software that takes the busywork off your plate: answering new leads, booking, reminders, follow-ups and reports. It comes in three engines, <span class="e-ops ec">Ops</span>, <span class="e-agents ec">Agents</span> and <span class="e-leads ec">Leads</span>. You pay monthly, we keep it running, and if it works for you, you can even sell it to others.</p>
    <div class="actions">
      <a class="btn" href="#work">See the work {ARR_D}</a>
      <a class="btn ghost" href="#start">Start a project {ARR_R}</a>
    </div>
    <nav class="hindex" aria-label="Case index"><span class="lab">recent work /</span>{hindex}</nav>
  </div>
</section>

<section class="sec" id="work" aria-labelledby="work-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Recent work</p>
        <h2 class="h2" id="work-h">Recent builds.</h2>
      </div>
      <a class="btn ghost" href="work.html">All work {ARR_R}</a>
    </div>
    <div class="work">
      <div class="cell"><div class="rows">{rows}
      </div></div>
      <div class="cell preview-cell">
        <div class="preview" id="preview">
          <div class="pv-top"><p class="eyebrow pv-path">Case study</p><span class="label pv-num">case 01 / {n:02d}</span></div>
          {pv_fig}
          <div class="pv-body">
            <h3 class="h3 pv-name">{E(c0['name'])}</h3>
            <p class="pv-sum">{E(c0['summary'])}</p>
            <a class="btn ghost pv-go" href="{case_href(c0)}">Open case {ARR_R}</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="ticker" aria-hidden="true">
  <div class="tk-track" id="tk-track">
    <div class="tk-set"><b>booking</b><i>/</i><span>reminders</span><i>/</i><span>follow-ups</span><i>/</i><b>price quotes</b><i>/</i><span>unpaid invoices</span><i>/</i><span>reviews</span><i>/</i><b>morning summary</b><i>/</i><span>weekly numbers</span><i>/</i><span>new hires</span><i>/</i><b>new leads</b><i>/</i><span>answers any hour</span><i>/</i></div>
  </div>
</div>

<section class="sec" id="familiar" aria-labelledby="familiar-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Sound familiar?</p>
      <h2 class="h2" id="familiar-h">You started a business. Then it became a job.</h2>
      <p class="lede">If you've said any of these this month, we should talk.</p>
      <div class="actions"><a class="btn ghost" href="#start">Tell us yours {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <ul class="check pains" data-anim>{pains}
      </ul>
    </div>
  </div>
</section>

<section class="sec" id="engines" aria-labelledby="engines-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How it works</p>
        <h2 class="h2" id="engines-h">One system. Three engines.</h2>
        <p class="lede">Start with one or use all three. They share the same information, so nothing gets typed in twice.</p>
      </div>
      <p class="label"><span class="e-ops ec">Ops</span> / <span class="e-agents ec">Agents</span> / <span class="e-leads ec">Leads</span></p>
    </div>
    <div class="engines">{engines}
    </div>
  </div>
</section>

<section class="sec" id="overnight" aria-labelledby="night-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">While you sleep</p>
        <h2 class="h2" id="night-h">You slept. Your engines didn't.</h2>
        <p class="lede">A night with all three engines running. Anything important waits for you in the morning summary.</p>
      </div>
      <p class="label">example</p>
    </div>
    <div class="pane" data-src="night-data" data-state="idle">
      <div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">Last night</span><span class="label">example</span></div>
      <div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows"></div></div>
      <div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div>
    </div>
    <script type="application/json" id="night-data">{night}</script>
  </div>
</section>

<section class="sec" id="plays" aria-labelledby="plays-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">What it handles</p>
        <h2 class="h2" id="plays-h">Jobs it takes off your plate.</h2>
        <p class="lede">A few of the jobs the engines handle for you. Each one runs at the right moment, and we set it up around how you work.</p>
      </div>
      <p class="label">{len(PLAYS)} examples</p>
    </div>
    <div class="tabs filters" role="group" aria-label="Filter by engine">{filters}</div>
    <ul class="plays">{plays}
    </ul>
  </div>
</section>

<section class="sec" id="for" aria-labelledby="for-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Who it's for</p>
        <h2 class="h2" id="for-h">Built for businesses like yours.</h2>
        <p class="lede">Each setup is ready-made for one kind of business. Pick yours, then try it in the demo.</p>
      </div>
      <a class="btn ghost" href="setups.html">All setups {ARR_R}</a>
    </div>
    <div class="picker" data-tabs>
      <div class="tabs" role="tablist" aria-label="Business type">{tabs}</div>{panels}
    </div>
  </div>
</section>

<section class="sec band" id="model" aria-labelledby="model-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How pricing works</p>
        <h2 class="h2" id="model-h">Run it. Grow it. Sell it.</h2>
        <p class="lede">You don't buy software that goes out of date. You pay monthly, and we keep it running and improving for as long as you use it.</p>
      </div>
      <p class="label">simple monthly pricing</p>
    </div>
    <ol class="model">
      <li class="mcell"><span class="num" aria-hidden="true">01</span><h3 class="h3">Run it</h3><p>We build it around how your business works and keep it running. One monthly price covers hosting, fixes and updates.</p></li>
      <li class="mcell"><span class="num" aria-hidden="true">02</span><h3 class="h3">Grow it</h3><p>Add more as you grow. Your plan grows with you.</p></li>
      <li class="mcell"><span class="num" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>If it works for you, it will work for businesses like yours. A resale license lets you sell it to them.</p></li>
    </ol>
    <div class="kicker">
      <p class="kicker-t">Most software is a cost. Yours can earn.</p>
      <div class="actions"><a class="btn" href="pricing.html">See licenses {ARR_R}</a><a class="btn ghost" href="#start">Start a project {ARR_R}</a></div>
    </div>
  </div>
</section>

<section class="sec" id="method" aria-labelledby="method-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How we work together</p>
        <h2 class="h2" id="method-h">How a build runs.</h2>
      </div>
      <p class="label">discuss / build / launch / measure</p>
    </div>
    <ol class="steps">
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">01</span><svg class="px" data-icon="discuss" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Discuss</h3><p>We talk with you and your team and see how the work really gets done.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">02</span><svg class="px" data-icon="build" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Build</h3><p>We build the software around it and connect it to the tools you already use.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">03</span><svg class="px" data-icon="implement" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Launch</h3><p>We roll it out with your team one piece at a time, until it runs without you in the middle.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">04</span><svg class="px" data-icon="measure" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Measure</h3><p>We track a simple score that shows how much of the business runs without you, and what to fix next.</p></li>
    </ol>
  </div>
</section>
''' + inquiry('h2', 'Stop being the system.',
              'Tell us what still runs through you. Two minutes. Andre or Matt replies personally.')
    return page('OpLev', 'Three engines for small businesses and startups: Ops, Agents and Leads. Built around you, licensed monthly, and yours to sell to others.',
                body, p='', home=True, active=None, mode=mode)


# ---------- pricing ----------

def access(n):
    status = {1: 'pick one', 2: 'pick two', 3: 'included'}[n]
    hint = {1: 'pick 1', 2: 'pick 2', 3: 'all included'}[n]
    meter = ''.join(f'<span class="seg{" on" if i < n else ""}"></span>' for i in range(3))
    rows = ''.join(
        f'<li class="e-{k}{" inc" if n == 3 else ""}"><span class="mk" aria-hidden="true"></span><span class="an">{E(name)}</span>'
        f'<span class="at">{E(triad)}</span><span class="as">{status}</span></li>'
        for k, name, _icon, triad, *_ in ENGINES)
    return f'''
        <div class="access" aria-label="Engine access: {n} of 3">
          <div class="access-hd"><span class="label">engines</span><span class="meter" aria-hidden="true">{meter}</span><span class="label">{n} of 3 / {hint}</span></div>
          <ul class="access-list">{rows}</ul>
        </div>'''


def fits(slug, p=''):
    xs = [x for x in SETUPS if x['license'] == slug]
    if not xs:
        return ''
    return '\n        <p class="label fits">good for: ' + ' / '.join(f'<a href="{p}setups/{x["id"]}.html">{E(x["name"])}</a>' for x in xs) + '</p>'


def plan(n, slug, name, amt, who, inc, btn):
    lis = ''.join(f'\n          <li>{E(x)}</li>' for x in inc)
    return f'''
      <article class="plan" aria-labelledby="p{n}">
        <div class="plan-top"><span class="label">plan {n} of 3</span></div>
        <div class="plan-id">
          <h3 class="h3" id="p{n}">{name}</h3>
          <p class="price"><span class="amt">{amt}</span><span class="per">/ month</span></p>
        </div>
        <p class="for">{who}</p>{access(n)}{fits(slug)}
        <ul class="inc">{lis}
        </ul>
        <a class="btn" href="start.html#{slug}">{btn} {ARR_R}</a>
      </article>'''


def engmap():
    cols = ''
    for k, name, _icon, triad, line, caps, _seen in ENGINES:
        plays = ''.join(f'<li>{E(t)}</li>' for e, _trig, t, _d in PLAYS if e == k)
        cols += f'''
      <div class="em e-{k}">
        <span class="label">engine</span>
        <h3 class="em-name">{E(name)}</h3>
        <p class="em-triad">{E(triad)}</p>
        <p class="em-line">{E(line)}</p>
        <ul class="em-caps">{''.join(f'<li>{E(x)}</li>' for x in caps)}</ul>
        <p class="label em-pl">handles</p>
        <ul class="em-plays">{plays}</ul>
      </div>'''
    return f'''
    <div class="engmap-hd"><p class="eyebrow">What you get</p><h3 class="h3">What each engine does.</h3></div>
    <div class="engmap">{cols}
    </div>'''


def pricing():
    plans = (plan(1, 'one', 'One engine', '$5k', 'Start with the engine closest to your biggest bottleneck.',
                  ['Built around your business', 'Automations set up for how you work',
                   'We host it, fix it and update it', 'A monthly progress score', 'A monthly check-in call',
                   'Email support, reply within a business day'],
                  'Start with one')
             + plan(2, 'core', 'Two engines', '$10k', 'Two engines that feed each other, so nothing falls between them.',
                    ['Your two engines, working together', 'Automations across both', 'We interview your team',
                     'A monthly progress score', 'We host it, fix it and update it',
                     'A weekly check-in call', 'Same-day support'],
                    'Start with two')
             + plan(3, 'company', 'All three', '$15k+', 'The full system, built around your whole business.',
                    ['All three engines, working together', 'Custom tools built for you',
                     'One place your team can look up how things are done', 'A progress score for every team',
                     'We host it, fix it and update it', 'Weekly calls and on-call support',
                     'Price depends on team size'],
                    'Talk to us'))
    lic = f'''
      <article class="lic" aria-labelledby="lic-h">
        <div class="lic-l">
          <span class="label">add to any plan</span>
          <h3 class="h3" id="lic-h">Resale license</h3>
          <p>Built something other businesses would pay for? A resale license lets you sell it to them.</p>
        </div>
        <div class="lic-r">
          <p class="price"><span class="amt">Quoted</span><span class="per">/ per deal</span></p>
          <a class="btn" href="start.html#resale">Ask about resale {ARR_R}</a>
        </div>
      </article>'''
    head = ''.join(f'<span class="cmp-h{" us" if i == 2 else ""}" role="columnheader">{E(h)}</span>' for i, h in enumerate(CMP_HEAD))
    cmp_rows = ''.join(
        f'\n      <div class="cmp-row" role="row"><span class="cmp-k" role="rowheader">{E(k)}</span>'
        + ''.join(f'<span class="cmp-v{" us" if i == 2 else ""}" role="cell" data-l="{E(CMP_HEAD[i])}">{E(v)}</span>'
                  for i, v in enumerate(vals))
        + '</div>'
        for k, *vals in CMP)
    aop = BY_ID.get('art-of-practice')
    example = (f'''
      <a class="example" href="{case_href(aop)}">{mini(aop, SEED['art-of-practice'], '')}<span class="ex-b"><span class="label">example</span><span class="h3">Art of Practice</span><span class="ex-t">Built from one practitioner's needs, for every practitioner like her.</span></span><span class="go">{ARR_R}</span></a>'''
               if aop else '')
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <p class="eyebrow">Pricing</p>
    <h1 class="h1" id="h1">Three engines. One monthly license.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">Pick one, two or all three engines. We build them around your business, then host them, fix them and keep improving them. Want to sell what we build to other businesses? Add a resale license.</p>
    <div class="every model-row">
      <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Run it</h3><p>Your engines, built and kept running by us.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">02</span><h3 class="h3">Grow it</h3><p>Updates included. Add engines as you grow.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>Add a resale license and sell it to others.</p></div>
    </div>
  </div>
</section>

<section class="sec band" id="plans" aria-labelledby="plans-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Plans</p>
        <h2 class="h2" id="plans-h">Pick your engines. We run them.</h2>
      </div>
      <p class="label">usd / billed monthly</p>
    </div>
    <div class="plans">{plans}{lic}
    </div>
    <div class="fine">
      <p class="label">billed monthly</p>
      <p class="label">hosting and fixes included</p>
      <p class="label">resale license available</p>
    </div>{engmap()}
  </div>
</section>

<section class="sec" id="why" aria-labelledby="why-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Why monthly</p>
        <h2 class="h2" id="why-h">Why pay monthly?</h2>
        <p class="lede">Off-the-shelf apps make you work their way. A one-off build is yours to fix. Paying monthly gets you software made for you, kept running by the people who built it.</p>
      </div>
    </div>
    <div class="cmp" role="table" aria-label="Off-the-shelf apps, an agency build and an OpLev license compared">
      <div class="cmp-row cmp-head" role="row"><span role="columnheader"><span class="sr">What matters</span></span>{head}</div>{cmp_rows}
    </div>
  </div>
</section>

<section class="sec" id="resale" aria-labelledby="resale-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Resale</p>
      <h2 class="h2" id="resale-h">Your system could be a product.</h2>
      <p class="lede">The way you run your business is worth something to everyone who runs one like it. Prove it works in yours, then sell it to them.</p>
      <div class="actions"><a class="btn" href="start.html#resale">Ask about resale {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <div class="every one-col">
        <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Prove it</h3><p>Run it in your own business first. That's your proof it works.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">02</span><h3 class="h3">License it</h3><p>Add a resale license. We price it based on how you plan to sell.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>Offer it to businesses like yours. The software keeps running on our side.</p></div>
      </div>{example}
    </div>
  </div>
</section>

<section class="sec" id="questions" aria-labelledby="q-h">
  <div class="wrap qa">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Questions</p>
        <h2 class="h2" id="q-h">Questions.</h2>
      </div>
    </div>
    <div class="faq">
      <details open>
        <summary><span class="h3">Why pay monthly instead of buying it?</span></summary>
        <p class="a">Software you buy starts aging the day it ships. Someone has to host it, fix it and keep it current, and that usually means hiring a developer. With a license, that's our job, and the software keeps getting better.</p>
      </details>
      <details>
        <summary><span class="h3">Who owns the software?</span></summary>
        <p class="a">OpLev does. You license it, and we host, maintain and improve it while you use it. Your business data stays yours.</p>
      </details>
      <details>
        <summary><span class="h3">Can we ask for changes?</span></summary>
        <p class="a">Yes. Changes and updates are included. We decide what to build next on your check-in calls.</p>
      </details>
      <details>
        <summary><span class="h3">What is a resale license?</span></summary>
        <p class="a">It lets you sell the software to businesses like yours. Add it to any plan. We price it based on how you plan to sell.</p>
      </details>
      <details>
        <summary><span class="h3">Which engine should we start with?</span></summary>
        <p class="a">The one closest to your biggest bottleneck. If leads slip, Leads. If your team is buried in follow-up, Agents. If nobody else knows how things run, Ops. We will help you decide on the first call.</p>
      </details>
      <details>
        <summary><span class="h3">Where do we start?</span></summary>
        <p class="a">Send us a note. We'll set up a short call, look at what still depends on you, and tell you where to start and which plan fits.</p>
      </details>
      <details>
        <summary><span class="h3">What does the + on All three mean?</span></summary>
        <p class="a">It starts at $15k a month and goes up with team size and how much we build into each engine. We quote it after our first call, so you know the number before you commit.</p>
      </details>
      <details>
        <summary><span class="h3">Can we change licenses?</span></summary>
        <p class="a">Yes. Add an engine or move down at the start of any month.</p>
      </details>
      <details>
        <summary><span class="h3">Do we even need this?</span></summary>
        <p class="a">Maybe not. If the business runs fine while you take two weeks off, keep your money. We'll tell you that on the first call.</p>
      </details>
    </div>
  </div>
</section>

<section class="sec" id="next" aria-labelledby="next-h">
  <div class="wrap stack">
    <p class="eyebrow">Next step</p>
    <h2 class="h2" id="next-h">Not sure which plan fits?</h2>
    <p class="lede">Tell us what still runs through you. We'll tell you which plan fits, even if the answer is none of them.</p>
    <div class="actions">
      <a class="btn" href="start.html">Start a project {ARR_R}</a>
      <a class="btn ghost" href="work.html">See the work {ARR_R}</a>
    </div>
  </div>
</section>'''
    return page('OpLev Pricing', 'License one engine from $5k a month, two for $10k or all three from $15k, with hosting, maintenance and updates included. Add a resale license to sell it to others.',
                body, p='', active='pricing')


# ---------- start ----------

def start():
    return page('Start a Project | OpLev', 'Tell OpLev what still runs through you. Andre or Matt replies personally.',
                inquiry('h1'), p='', active='contact')


# ---------- setups ----------

def access_for(keys):
    rows = ''.join(
        f'<li class="e-{k}{" inc" if k in keys else ""}"><span class="mk" aria-hidden="true"></span><span class="an">{E(name)}</span>'
        f'<span class="at">{E(triad)}</span><span class="as">{"included" if k in keys else "add any time"}</span></li>'
        for k, name, _i, triad, *_ in ENGINES)
    meter = ''.join(f'<span class="seg{" on" if i < len(keys) else ""}"></span>' for i in range(3))
    return f'''<div class="access"><div class="access-hd"><span class="label">engines</span><span class="meter" aria-hidden="true">{meter}</span><span class="label">{len(keys)} of 3</span></div><ul class="access-list">{rows}</ul></div>'''


def setups_index():
    cards = ''
    for i, x in enumerate(SETUPS):
        L = LICENSES[x['license']]
        uses = ''.join(f'<li>{E(u[2])}</li>' for u in x['uses'][:3])
        cards += f'''
      <a class="card setup-card" href="setups/{x['id']}.html">
        <div class="card-top"><span class="label">{E(x['type'])}</span>{etags(x['engines'])}</div>
        <h2 class="h3 card-name">{E(x['name'])}</h2>
        <p class="card-line">{E(x['pitch'])}</p>
        <ul class="rowlist">{uses}</ul>
        <div class="card-foot"><span class="label">{E(L['name'])} / {E(L['price'])} a month</span><span class="label go">Open {ARR_R}</span></div>
      </a>'''
    cards += f'''
      <a class="card setup-card custom" href="start.html">
        <div class="card-top"><span class="label">something else</span></div>
        <h2 class="h3 card-name">Custom setup</h2>
        <p class="card-line">Your business doesn't fit a box? We build a setup around how you work, on any mix of engines.</p>
        <div class="card-foot"><span class="label">from $5k a month</span><span class="label go">Talk to us {ARR_R}</span></div>
      </a>'''
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><p class="eyebrow">Who it's for</p><span class="label">{len(SETUPS):02d} setups</span></div>
    <h1 class="h1" id="h1">A setup for your kind of business.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">Each setup is ready-made for one kind of business. Pick yours, try it in the demo, then we tailor it to you.</p>
    <div class="actions"><a class="btn" href="app.html">Open the demo {ARR_R}</a><a class="btn ghost" href="pricing.html">See licenses {ARR_R}</a></div>
    <div class="cards">{cards}
    </div>
  </div>
</section>''' + cta('Want to see yours running?', 'Tell us what still runs through you. We will pick the setup and show you where we would start.', '')
    return page('OpLev Setups', 'Engine setups for clinics, product brands, agencies, creators and startups. Each one is ready-made for one kind of business, and you can try it in the demo.',
                body, p='', active='setups')


def setup_page(i):
    x = SETUPS[i]
    p = '../'
    L = LICENSES[x['license']]
    n = len(SETUPS)
    k = x['id']
    uses = ''.join(f'''
      <li class="play e-{e}" data-e="{e}"><div class="play-top">{etags([e])}<span class="label play-trig">{E(trig)}</span></div><h3 class="h3">{E(t)}</h3><p>{E(d)}</p></li>''' for e, trig, t, d in x['uses'])
    seen = ''.join(
        f'<a href="{case_href(BY_ID[cid], p)}">{mini(BY_ID[cid], SEED[cid], p)}<span class="h3">{E(BY_ID[cid]["name"])}</span><span class="go">{ARR_R}</span></a>'
        for cid in x['cases'] if cid in BY_ID)
    eng_names = ' + '.join(ENGINE_NAME[e] for e in x['engines'])
    missing = [ENGINE_NAME[e] for e, *_ in ENGINES if e not in x['engines']]
    prv, nxt = SETUPS[(i - 1) % n], SETUPS[(i + 1) % n]
    day = json.dumps({'cmd': f"A day at {x['demo']['biz']}", 'run': x['day']}).replace('</', '<\\/')
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><a class="label" href="{p}setups.html">{ARR_L} All setups</a><span class="label">setup {i + 1:02d} / {n:02d}</span></div>
    <p class="eyebrow">For {E(x['type'].lower())}</p>
    <h1 class="h1" id="h1">The {E(x['name'])}<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">{E(x['pitch'])}</p>
    <dl class="facts f4">
      <div><dt class="label">For</dt><dd>{E(x['for'])}</dd></div>
      <div><dt class="label">Engines</dt><dd>{etags(x['engines'])}</dd></div>
      <div><dt class="label">License</dt><dd>{E(L['name'])} / {E(L['price'])} a month</dd></div>
      <div><dt class="label">Connects</dt><dd>{E(', '.join(x['connects']))}</dd></div>
    </dl>
    <div class="actions"><a class="btn" href="{p}start.html#{k}">Start with this setup {ARR_R}</a><a class="btn ghost" href="{p}app.html#{k}">Try the demo {ARR_R}</a></div>
  </div>
</section>

<section class="sec" id="uses" aria-labelledby="uses-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">What it handles</p>
        <h2 class="h2" id="uses-h">Jobs it takes off your plate.</h2>
        <p class="lede">We set each one up with you and adjust them as you go.</p>
      </div>
      <p class="label">{len(x['uses'])} jobs</p>
    </div>
    <ul class="plays plays-top">{uses}
    </ul>
  </div>
</section>

<section class="sec" id="day" aria-labelledby="day-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">A typical day</p>
        <h2 class="h2" id="day-h">A day with the {E(x['name'])}.</h2>
      </div>
      <p class="label">example</p>
    </div>
    <div class="pane" data-src="day-data" data-state="idle" style="max-width:none">
      <div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">A typical day</span><span class="label">example</span></div>
      <div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows"></div></div>
      <div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div>
    </div>
    <script type="application/json" id="day-data">{day}</script>
  </div>
</section>

<section class="sec band" id="access" aria-labelledby="access-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">What's included</p>
      <h2 class="h2" id="access-h">Runs on {E(eng_names)}.</h2>
      <p class="lede">The {E(x['name'])} fits the {E(L['name'])} license at {E(L['price'])} a month, with hosting, maintenance and updates included.{(' Add ' + ' or '.join(missing) + ' any time.') if missing else ''}</p>
      <div class="actions"><a class="btn" href="{p}pricing.html">See licenses {ARR_R}</a></div>
    </div>
    <div class="split-r">{access_for(x['engines'])}
      <div class="tool-row"><span class="label">connects to</span>{''.join(f'<span class="tool">{E(c)}</span>' for c in x['connects'])}</div>
    </div>
  </div>
</section>

<section class="sec" id="demo" aria-labelledby="demo-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Try it</p>
      <h2 class="h2" id="demo-h">Try it with sample data.</h2>
      <p class="lede">Open the Console as a sample {E(x['type'].lower().rstrip('s').replace(' + ', ' or '))} business. Approve drafts, turn automations on and off, and watch it work.</p>
      <div class="actions"><a class="btn" href="{p}app.html#{k}">Open the demo {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <span class="label">our work for</span>
      <div class="seen">{seen}</div>
      <nav class="pager" aria-label="More setups">
        <a class="pg prev" href="{prv['id']}.html"><span class="label">{ARR_L} Previous</span><span class="h3">{E(prv['name'])}</span></a>
        <a class="pg next" href="{nxt['id']}.html"><span class="label">Next {ARR_R}</span><span class="h3">{E(nxt['name'])}</span></a>
      </nav>
    </div>
  </div>
</section>''' + cta(f'Start with the {E(x["name"])}.', 'Tell us about your business. We will tune the setup to how you work and show you where we would start.', p)
    return page(f'{x["name"]} | OpLev', f'The OpLev {x["name"]} for {x["type"].lower()}: {x["pitch"]}', body, p=p, active='setups')


# ---------- console app ----------

def app_page():
    data = {'engines': [{'id': k, 'name': n, 'triad': t, 'line': l, 'caps': c} for k, n, _i, t, l, c, _s in ENGINES],
            'plays': PLAYS, 'setups': SETUPS, 'licenses': LICENSES}
    blob = json.dumps(data).replace('</', '<\\/')
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>OpLev Console</title>\n'
            '<meta name="description" content="The OpLev Console: set up, monitor and work with your Ops, Agents and Leads engines. Demo with sample data.">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<style>\n{CSS}\n{APP_CSS}</style>\n</head>\n<body>\n'
            '<div id="app" class="app"><noscript><p style="padding:24px">The OpLev Console needs JavaScript.</p></noscript></div>\n'
            f'<script type="application/json" id="app-data">{blob}</script>\n'
            f'<script>\n{APP_JS}</script>\n</body>\n</html>\n')


# ---------- work index ----------

def work():
    n = len(CASES)
    cards = ''.join(f'''
      <a class="card" href="{case_href(c)}">
        {thumb(c, i + 1, '', tags=False)}
        <div class="card-b">
          <div class="card-top"><span class="label">case {i + 1:02d}</span><span class="label">{E(c['focus'])}</span></div>
          <h2 class="h3 card-name">{E(c['name'])}</h2>
          <p class="card-line">{E(c['line'])}</p>
          {etags(c.get('engines'))}
          <div class="card-foot"><span class="label">{E(c['built'])}</span><span class="label go">Open {ARR_R}</span></div>
        </div>
      </a>''' for i, c in enumerate(CASES))
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><p class="eyebrow">Our work</p><span class="label">{n:02d} cases</span></div>
    <h1 class="h1" id="h1">Systems we've built.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">Software we built for founders and small teams. Each one shows the problem, what we built and how it works day to day.</p>
    <div class="cards">{cards}
    </div>
  </div>
</section>''' + cta('Want one of these running for you?',
                    'Tell us what still runs through you. We will show you where we would start.', '')
    return page('OpLev Work', 'Case studies: custom software, work agents and lead capture tools OpLev has built for founders and small teams.',
                body, p='', active='work')


# ---------- case pages ----------

def case(i):
    c = CASES[i]
    n = len(CASES)
    p = '../'
    seed = i + 1
    prv, nxt = CASES[(i - 1) % n], CASES[(i + 1) % n]
    checks = ''.join(
        f'\n          <li class="ck" data-by="{E(by)}"><span class="b">[ ]</span><span class="txw"><span class="tx">{E(t)}</span></span><span class="by label">open</span></li>'
        for t, by in c['before'])
    checklist = (f'''
      <div>
        <p class="label">{E(c.get('before_label', 'Before'))}</p>
        <ul class="check" data-anim style="margin-top:14px">{checks}
        </ul>
      </div>''' if c['before'] else '')
    built = ''.join(
        f'\n      <li><span class="label kind {E(k)}">{E(k)}</span><h3 class="h3">{E(t)}</h3><p>{E(d)}</p></li>'
        for k, t, d in c['system'])
    kinds = {}
    for k, _, _ in c['system']:
        kinds[k] = kinds.get(k, 0) + 1
    count = c.get('count') or ' / '.join(f'{v} {k}{"s" if v > 1 else ""}' for k, v in kinds.items())
    results = c.get('results') or []
    if results:
        res = ''.join(f'\n      <div class="rcell"><span class="rcell-v">{E(v)}</span><span class="label">{E(l)}</span></div>'
                      for v, l in results)
        res_label = c.get('results_label', 'reported by the client')
    else:
        res = ''.join('\n      <div class="rcell todo"><span class="rcell-v">[ metric ]</span><span class="label">result to add</span></div>'
                      for _ in range(3))
        res_label = 'to be added'
    res_title = c.get('results_title', 'Results.')
    facts = [tuple(f) for f in c['facts']] if c.get('facts') else [('Focus', c['focus']), ('Built', c['built']), ('Includes', c['includes'])]
    facts = [f for f in facts if f[0] != 'Stack']
    facts_html = ''.join(f'\n      <div><dt class="label">{k}</dt><dd>{E(v)}</dd></div>' for k, v in facts)
    note = f'\n    <p class="label case-note">{E(c["note"])}</p>' if c.get('note') else ''
    data = json.dumps({'cmd': c['cmd'], 'run': c['run']}).replace('</', '<\\/')
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><a class="label" href="{p}work.html">{ARR_L} All work</a><span class="label">case {seed:02d} / {n:02d}</span></div>
    <p class="eyebrow">Case study</p>
    <h1 class="h1" id="h1">{E(c['name'])}<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">{E(c['line'])}</p>
    {etags(c.get('engines'), ' case-tags')}
    <dl class="facts f{len(facts)}">{facts_html}
    </dl>
    {thumb(c, seed, p)}{note}
  </div>
</section>

<section class="sec" id="before" aria-labelledby="before-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">The story</p>
      <h2 class="h2" id="before-h">{E(c.get('before_title', 'What was breaking.'))}</h2>
    </div>
    <div class="split-r">
      <p class="lede">{E(c['summary'])}</p>{checklist}
    </div>
  </div>
</section>

<section class="sec" id="built" aria-labelledby="built-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">What we built</p>
        <h2 class="h2" id="built-h">What we built.</h2>
      </div>
      <p class="label">{E(count)}</p>
    </div>
    <ul class="built">{built}
    </ul>
  </div>
</section>

<section class="sec" id="run" aria-labelledby="run-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How it works</p>
        <h2 class="h2" id="run-h">Watch it run.</h2>
      </div>
      <p class="label">example</p>
    </div>
    <div class="pane" id="pane" data-src="case-data" data-state="idle">
      <div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">Example</span><span class="label">example</span></div>
      <div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows"></div></div>
      <div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div>
    </div>
  </div>
</section>

<section class="sec" id="results" aria-labelledby="results-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Results</p>
        <h2 class="h2" id="results-h">{E(res_title)}</h2>
      </div>
      <p class="label">{res_label}</p>
    </div>
    <div class="results">{res}
    </div>
  </div>
</section>

<section class="sec" id="more" aria-label="More cases">
  <div class="wrap">
    <nav class="pager" aria-label="More cases">
      <a class="pg prev" href="{prv['id']}.html"><span class="label">{ARR_L} Previous case</span><span class="pg-row">{mini(prv, (i - 1) % n + 1, p)}<span class="h3">{E(prv['name'])}</span></span></a>
      <a class="pg next" href="{nxt['id']}.html"><span class="label">Next case {ARR_R}</span><span class="pg-row">{mini(nxt, (i + 1) % n + 1, p)}<span class="h3">{E(nxt['name'])}</span></span></a>
    </nav>
  </div>
</section>''' + cta('Want this running in your business?',
                    'Tell us what still runs through you. We will show you where we would start.', p)
    data_tag = f'\n<script type="application/json" id="case-data">{data}</script>'
    return page(f'{c["name"]} | OpLev', f'{c["name"]}: {c["line"]}', body, p=p, active='work', data=data_tag)


# ---------- write ----------

def main():
    out = {'index.html': home(), 'pricing.html': pricing(), 'work.html': work(), 'start.html': start(),
           'setups.html': setups_index(), 'app.html': app_page()}
    for i, x in enumerate(SETUPS):
        out[f'setups/{x["id"]}.html'] = setup_page(i)
    for i, c in enumerate(CASES):
        out[f'work/{c["id"]}.html'] = case(i)
    for rel, html in out.items():
        f = ROOT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html)
        print(f'wrote {rel} ({len(html) // 1024} KB)')
    if '--preview' in sys.argv:
        dest = pathlib.Path(sys.argv[sys.argv.index('--preview') + 1])
        dest.write_text(home(mode='artifact'))
        print(f'wrote preview {dest}')


if __name__ == '__main__':
    main()
