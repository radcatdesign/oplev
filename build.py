#!/usr/bin/env python3
"""Build the OpLev site into self-contained HTML pages.

Edit content/cases.json, src/site.css or src/site.js, then run:
    python3 build.py
Outputs index.html, pricing.html, work.html, start.html and work/<case>.html at the repo root.
Optional: python3 build.py --preview PATH writes an artifact-ready copy of the home page.
"""
import json, sys, pathlib
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent
CASES = json.loads((ROOT / 'content' / 'cases.json').read_text())
CSS = (ROOT / 'src' / 'site.css').read_text()
JS = (ROOT / 'src' / 'site.js').read_text()

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

PAINS = [
    ('Everything still runs through me.', 'an operating system'),
    ('I pay for a stack of apps and still live in spreadsheets.', 'one platform'),
    ('Leads come in at night and sit until Monday.', 'lead capture tools'),
    ('Only one person knows how that part works.', 'a shared system'),
    ("I can't take a week off.", 'work agents'),
    ('People keep asking if they can use what I built.', 'a commercial license'),
]

FOR = [
    ('clinic', 'Clinics + practices', 'Smoother visits for clients. Less admin for you.',
     ['Intake, booking and follow-up that run on their own', 'Notes, records and reports in one place',
      'An assistant trained on your own material'],
     ['adessa-mind', 'art-of-practice']),
    ('brand', 'Product brands', "Answer every buyer's question and capture the order.",
     ['A store that answers questions and takes orders', 'Tools that let buyers see it and price it',
      'Orders, stock and wholesale handled by agents'],
     ['element-glo', 'mawa']),
    ('agency', 'Agencies + service firms', 'Deliver the same great work without you in every thread.',
     ['Client onboarding that runs itself', 'Launch checks and reports your team can trust',
      'Your method, packaged so you can sell it'],
     ['fit-funnels']),
    ('creator', 'Creators + media', 'Keep making things. Let the busywork run itself.',
     ['A release pipeline for every channel', 'An inbox sorted into fans, partners and deals',
      'Licensing and partnership requests routed'],
     ['jason-stephenson']),
    ('startup', 'Startups', 'Run lean from day one, and turn what works into a product.',
     ['Ops that scale before your headcount does', 'Investor updates that draft themselves',
      'Software you can license to others'],
     ['mawa', 'art-of-practice']),
]

CMP_HEAD = ('Off-the-shelf apps', 'Agency build', 'OpLev license')
CMP = [
    ('Built around how you work', 'No. You work around it.', 'Yes', 'Yes'),
    ('How you pay', 'Per app, per seat, every month', 'A big build fee, then hourly fixes', 'One monthly license'),
    ('Who keeps it running', 'You do', 'You, or a developer you hire', 'We do'),
    ('Gets better over time', 'On their roadmap, not yours', 'Only when you pay for it', 'Updates included'),
    ('Can you sell it', 'No', 'Depends on your contract', 'Yes, with a commercial license'),
]

F_TYPE = [('clinic', 'Clinic or practice'), ('brand', 'Product brand'), ('agency', 'Agency or service firm'),
          ('creator', 'Creator or media'), ('startup', 'Startup'), ('other', 'Something else')]
F_TEAM = [('1', 'Just me'), ('2-5', '2 to 5'), ('6-20', '6 to 20'), ('21-50', '21 to 50'), ('50', '50+')]
F_BUILD = [('system', 'Operating system'), ('agents', 'Work agents'), ('lead', 'Lead capture tools'),
           ('unsure', 'Not sure yet')]
F_LICENSE = [('one', 'One function / $5k'), ('core', 'Core ops / $10k'), ('company', 'Whole company / $15k+'),
             ('unsure', 'Not sure yet')]
F_RESALE = [('yes', 'Yes'), ('later', 'Maybe later'), ('no', 'No')]
F_TIMING = [('month', 'This month'), ('quarter', 'This quarter'), ('exploring', 'Just exploring')]


# ---------- shared shell ----------

def nav_items(p, home):
    a = (lambda h: h) if home else (lambda h: p + 'index.html' + h)
    return [
        ('work', 'Work', p + 'work.html', '~/oplev/work'),
        ('model', 'How it works', a('#model'), '~/oplev/model'),
        ('pricing', 'Pricing', p + 'pricing.html', '~/oplev/pricing'),
        ('contact', 'Contact', p + 'start.html', '~/oplev/start'),
    ]


def shell_top(p, home, active):
    items = nav_items(p, home)
    cur = lambda k: ' aria-current="page"' if k == active else ''
    links = ''.join(f'\n      <a href="{h}"{cur(k)}>{t}</a>' for k, t, h, _ in items)
    menu = ''.join(
        f'\n        <li><a href="{h}"{cur(k)}><span class="mn">{i + 1:02d}</span>'
        f'<span class="mt">{t}</span><span class="mp">{pth}</span></a></li>'
        for i, (k, t, h, pth) in enumerate(items))
    brand = '#hero' if home else p + 'index.html'
    return f'''<div class="loader" id="loader" aria-hidden="true">
  <div class="ld-top">
    <span class="brand">{MARK}OPLEV</span>
    <span class="label">oplev / build {BUILD}</span>
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
      <span>Custom software, licensed</span>
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


def cta(title, text, p):
    return f'''
<section class="sec" id="next" aria-labelledby="next-h">
  <div class="wrap stack">
    <p class="eyebrow">~/oplev/start</p>
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


def inquiry(level='h2'):
    first = level == 'h1'
    hid = 'h1' if first else 'start-h'
    cursor = '<span class="cursor" aria-hidden="true"></span>' if first else ''
    cls = 'inq-page' if first else 'sec'
    return f'''
<section class="{cls}" id="start" aria-labelledby="{hid}">
  <div class="wrap inq-wrap">
    <div class="inq-side">
      <p class="eyebrow">~/oplev/start</p>
      <{level} class="{level}" id="{hid}">Tell us what still runs through you.{cursor}</{level}>
      <p class="lede">Two minutes. We read every one, and Andre or Matt replies personally.</p>
      <ol class="next">
        <li><span class="nx-n" aria-hidden="true">01</span><div><h3 class="h3">We read it</h3><p>A real reply from one of the two people who will build your system.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">02</span><div><h3 class="h3">A short call</h3><p>We talk through what still runs through you and what it costs you.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">03</span><div><h3 class="h3">Your OpLev Score</h3><p>Your team answers a few questions with Mira. We show you where to build first.</p></div></li>
        <li><span class="nx-n" aria-hidden="true">04</span><div><h3 class="h3">Your build plan</h3><p>What we'd build, which license fits, and what you can sell later.</p></div></li>
      </ol>
      <p class="label inq-alt">Prefer email? <span class="sel">{EMAIL}</span></p>
    </div>
    <form class="inq" action="/api/inquiry" method="post" novalidate data-email="{EMAIL}" aria-label="Project inquiry">
      <div class="inq-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">~/oplev/start/inquiry</span><span class="label">* required</span></div>
      <div class="inq-grid">
        <label class="fl"><span class="label" data-err="add your name">Name *</span><input class="inp" id="inq-name" name="name" autocomplete="name" maxlength="120" required></label>
        <label class="fl"><span class="label" data-err="add a valid email">Email *</span><input class="inp" id="inq-email" name="email" type="email" autocomplete="email" maxlength="200" required></label>
      </div>
      <label class="fl"><span class="label">Company</span><input class="inp" id="inq-company" name="company" autocomplete="organization" maxlength="160"></label>
      <fieldset class="fs"><legend class="label">What kind of business?</legend><div class="opts">{opts('type', F_TYPE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">Team size</legend><div class="opts">{opts('team', F_TEAM)}</div></fieldset>
      <label class="fl"><span class="label" data-err="tell us a little">What still runs through you? *</span><textarea class="inp" id="inq-message" name="message" rows="5" maxlength="4000" required placeholder="The work that only happens when you're there."></textarea></label>
      <fieldset class="fs"><legend class="label">What should we build?</legend><div class="opts">{opts('build', F_BUILD, 'checkbox')}</div></fieldset>
      <fieldset class="fs"><legend class="label">Which license are you thinking?</legend><div class="opts">{opts('license', F_LICENSE)}</div></fieldset>
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
        f'<button class="tab" type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{E(t)}</button>'
        for i, (k, t, _, _, _) in enumerate(FOR))
    panels = ''
    for i, (k, t, pitch, items, cases) in enumerate(FOR):
        lis = ''.join(f'<li>{E(x)}</li>' for x in items)
        seen = ''.join(
            f'<a href="{case_href(BY_ID[cid])}">{mini(BY_ID[cid], SEED[cid], "")}<span class="h3">{E(BY_ID[cid]["name"])}</span><span class="go">{ARR_R}</span></a>'
            for cid in cases if cid in BY_ID)
        panels += f'''
      <div class="fpanel" role="tabpanel" id="panel-{k}" aria-labelledby="tab-{k}"{'' if i == 0 else ' hidden'}>
        <div class="fp-l">
          <span class="label">what we'd build</span>
          <h3 class="h3 fp-name">{E(t)}</h3>
          <p class="fp-pitch">{E(pitch)}</p>
          <ul class="rowlist">{lis}</ul>
        </div>
        <div class="fp-r">
          <span class="label">seen in</span>
          <div class="seen">{seen}</div>
          <a class="btn" href="start.html#{k}">Start a project {ARR_R}</a>
        </div>
      </div>'''
    body = f'''
<section class="hero" id="hero">
  <canvas class="field" id="field" aria-hidden="true"></canvas>
  <div class="wrap">
    <span class="readout label" id="readout" aria-hidden="true">x 0000 · y 0000</span>
    <p class="eyebrow">~/oplev/systems</p>
    <h1 class="h1" id="h1">We build the systems your business runs on.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">OpLev builds custom software, work agents and lead capture tools for small businesses and startups. You license it monthly, we keep it running and improving, and if it works for you, you can sell it to others.</p>
    <div class="actions">
      <a class="btn" href="#work">See the work {ARR_D}</a>
      <a class="btn ghost" href="#start">Start a project {ARR_R}</a>
    </div>
    <nav class="hindex" aria-label="Case index"><span class="lab">index /</span>{hindex}</nav>
  </div>
</section>

<section class="sec" id="work" aria-labelledby="work-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/work</p>
        <h2 class="h2" id="work-h">Recent builds.</h2>
      </div>
      <a class="btn ghost" href="work.html">All work {ARR_R}</a>
    </div>
    <div class="work">
      <div class="cell"><div class="rows">{rows}
      </div></div>
      <div class="cell preview-cell">
        <div class="preview" id="preview">
          <div class="pv-top"><p class="eyebrow pv-path">~/oplev/work/{E(c0['id'])}</p><span class="label pv-num">case 01 / {n:02d}</span></div>
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
    <div class="tk-set"><b>custom software</b><i>/</i><span>intake</span><i>/</i><span>booking</span><i>/</i><span>onboarding</span><i>/</i><span>dashboards</span><i>/</i><b>work agents</b><i>/</i><span>approvals</span><i>/</i><span>reporting</span><i>/</i><span>inbox triage</span><i>/</i><b>lead capture tools</b><i>/</i><span>calculators</span><i>/</i><span>visualizers</span><i>/</i><b>commercial licenses</b><i>/</i></div>
  </div>
</div>

<section class="sec" id="familiar" aria-labelledby="familiar-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">~/oplev/familiar</p>
      <h2 class="h2" id="familiar-h">Sound familiar?</h2>
      <p class="lede">If you've said any of these this month, we should talk.</p>
      <div class="actions"><a class="btn ghost" href="#start">Tell us yours {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <ul class="check pains" data-anim>{pains}
      </ul>
    </div>
  </div>
</section>

<section class="sec" id="build" aria-labelledby="build-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/build</p>
        <h2 class="h2" id="build-h">What we build.</h2>
      </div>
      <p class="label">systems / agents / tools</p>
    </div>
    <ul class="offer">
      <li class="svc"><svg class="px" data-icon="system" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Operating systems</h3><p>Custom software for how your business runs: workflows, records and dashboards your team uses every day.</p></li>
      <li class="svc"><svg class="px" data-icon="agent" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Work agents</h3><p>Agents that take the repeat work off your team and ask a person before anything important goes out.</p></li>
      <li class="svc"><svg class="px" data-icon="lead" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Lead capture tools</h3><p>Calculators, visualizers and planners that answer a buyer's question on your site and capture the lead while they use it.</p></li>
    </ul>
  </div>
</section>

<section class="sec" id="for" aria-labelledby="for-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/for</p>
        <h2 class="h2" id="for-h">Built for businesses like yours.</h2>
      </div>
      <p class="label">pick yours</p>
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
        <p class="eyebrow">~/oplev/model</p>
        <h2 class="h2" id="model-h">Run it. Grow it. Sell it.</h2>
        <p class="lede">You don't buy software from us and watch it go stale. You license it, and we keep it running and improving for as long as you use it.</p>
      </div>
      <p class="label">the oplev license</p>
    </div>
    <ol class="model">
      <li class="mcell"><span class="num" aria-hidden="true">01</span><h3 class="h3">Run it</h3><p>We build software around how your business works and keep it running. One monthly license covers hosting, fixes and updates.</p></li>
      <li class="mcell"><span class="num" aria-hidden="true">02</span><h3 class="h3">Grow it</h3><p>It keeps getting better. Add systems and agents as you grow, and move up a license when you need more.</p></li>
      <li class="mcell"><span class="num" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>If it works for you, it will work for businesses like yours. A commercial license lets you sell it to them.</p></li>
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
        <p class="eyebrow">~/oplev/method</p>
        <h2 class="h2" id="method-h">How a build runs.</h2>
      </div>
      <p class="label">discuss / build / launch / measure</p>
    </div>
    <ol class="steps">
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">01</span><svg class="px" data-icon="discuss" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Discuss</h3><p>We talk with the people doing the work, with help from Mira, our AI interviewer, and map how it actually gets done.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">02</span><svg class="px" data-icon="build" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Build</h3><p>We build the software around it: tools, dashboards, agents and the lead tools on your site.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">03</span><svg class="px" data-icon="implement" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Launch</h3><p>We roll it out with your team one piece at a time, until it runs without you in the middle.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">04</span><svg class="px" data-icon="measure" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Measure</h3><p>We score it. The OpLev Score shows how much of the business runs without leaning on one person, and where to build next.</p></li>
    </ol>
  </div>
</section>
''' + inquiry('h2')
    return page('OpLev', 'OpLev builds custom software, work agents and lead capture tools for small businesses and startups. License it monthly, and sell it to others if you want.',
                body, p='', home=True, active=None, mode=mode)


# ---------- pricing ----------

def plan(n, slug, name, amt, who, inc, btn):
    lis = ''.join(f'\n          <li>{E(x)}</li>' for x in inc)
    return f'''
      <article class="plan" aria-labelledby="p{n}">
        <div class="plan-top"><span class="label">license {n:02d} / 03</span></div>
        <div class="plan-id">
          <h3 class="h3" id="p{n}">{name}</h3>
          <p class="price"><span class="amt">{amt}</span><span class="per">/ month</span></p>
        </div>
        <p class="for">{who}</p>
        <ul class="inc">{lis}
        </ul>
        <a class="btn" href="start.html#{slug}">{btn} {ARR_R}</a>
      </article>'''


def pricing():
    plans = (plan(1, 'one', 'One function', '$5k', 'One part of the business needs to stop running through you.',
                  ['License for one custom system', 'Up to 2 work agents', 'Hosting, maintenance and updates',
                   'Monthly OpLev Score', 'Monthly working session', 'Async support, reply within a business day'],
                  'Start with one')
             + plan(2, 'core', 'Core ops', '$10k', "A growing team where the work lives in a few people's heads.",
                    ['License for up to 3 custom systems', 'Up to 6 work agents', 'Team interviews with Mira',
                     'Monthly OpLev Score with your team', 'Hosting, maintenance and updates',
                     'Weekly working session', 'Same-day support'],
                    'Start core ops')
             + plan(3, 'company', 'Whole company', '$15k+', 'You want the whole operation running on one platform.',
                    ['License for every system we build you', 'Custom agents, scoped with you',
                     'A searchable company knowledge base', 'OpLev Score across teams and roles',
                     'Hosting, maintenance and updates', 'Weekly sessions and on-call support',
                     'Priced by team size and scope'],
                    'Talk to us'))
    lic = f'''
      <article class="lic" aria-labelledby="lic-h">
        <div class="lic-l">
          <span class="label">add-on / any license</span>
          <h3 class="h3" id="lic-h">Commercial license</h3>
          <p>Built something other businesses would pay for? A commercial license gives you the right to sell the software to them.</p>
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
    <p class="eyebrow">~/oplev/pricing</p>
    <h1 class="h1" id="h1">Custom software. One monthly license.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">We build software around how your business works. We own the code, host it, fix it and keep improving it, so it never goes stale. You pay one monthly license. And if other businesses want what you have, a commercial license lets you sell it to them.</p>
    <div class="every model-row">
      <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Run it</h3><p>Your software, built and kept running by us.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">02</span><h3 class="h3">Grow it</h3><p>Updates included. Move up a license as you grow.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>Add a commercial license and sell it to others.</p></div>
    </div>
  </div>
</section>

<section class="sec band" id="plans" aria-labelledby="plans-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/licenses</p>
        <h2 class="h2" id="plans-h">Pick the scope. We run the software.</h2>
      </div>
      <p class="label">usd / billed monthly</p>
    </div>
    <div class="plans">{plans}{lic}
    </div>
    <div class="fine">
      <p class="label">license billed monthly</p>
      <p class="label">hosting + maintenance included</p>
      <p class="label">resale by commercial license</p>
    </div>
  </div>
</section>

<section class="sec" id="why" aria-labelledby="why-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/why</p>
        <h2 class="h2" id="why-h">Why license it?</h2>
        <p class="lede">Off-the-shelf apps make you work their way. A one-off build is yours to babysit. A license gets you software made for you, kept running by the people who built it.</p>
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
      <p class="eyebrow">~/oplev/resale</p>
      <h2 class="h2" id="resale-h">Your system could be a product.</h2>
      <p class="lede">The way you run your business is worth something to everyone who runs one like it. Prove it works in yours, then sell it to them.</p>
      <div class="actions"><a class="btn" href="start.html#resale">Ask about resale {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <div class="every one-col">
        <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Prove it</h3><p>Run it in your own business first. That's your proof it works.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">02</span><h3 class="h3">License it</h3><p>Add a commercial license. We price it per deal, based on how you plan to sell.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>Offer it to businesses like yours. The software keeps running on our side.</p></div>
      </div>{example}
    </div>
  </div>
</section>

<section class="sec" id="questions" aria-labelledby="q-h">
  <div class="wrap qa">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/questions</p>
        <h2 class="h2" id="q-h">Questions.</h2>
      </div>
    </div>
    <div class="faq">
      <details open>
        <summary><span class="h3">Why license it instead of buying it?</span></summary>
        <p class="a">Software you buy starts aging the day it ships. Someone has to host it, fix it and keep it current, and that usually means hiring a developer. With a license, that's our job, and the software keeps getting better.</p>
      </details>
      <details>
        <summary><span class="h3">Who owns the software?</span></summary>
        <p class="a">OpLev does. You license it, and we host, maintain and improve it while you use it. Your business data stays yours.</p>
      </details>
      <details>
        <summary><span class="h3">Can we ask for changes?</span></summary>
        <p class="a">Yes. Updates are part of the license, and your working sessions are where we decide what to build next.</p>
      </details>
      <details>
        <summary><span class="h3">What is a commercial license?</span></summary>
        <p class="a">It gives you the right to sell the software to businesses like yours. Add it to any license. We price it per deal, based on how you plan to sell.</p>
      </details>
      <details>
        <summary><span class="h3">Where do we start?</span></summary>
        <p class="a">Send us a note. We set up a short call, then run the OpLev Score with your team to find where to build first and which license fits.</p>
      </details>
      <details>
        <summary><span class="h3">What does the + on Whole company mean?</span></summary>
        <p class="a">It starts at $15k a month and goes up with team size and the number of systems we build. We quote it after the OpLev Score, so you know the number before you commit.</p>
      </details>
      <details>
        <summary><span class="h3">Can we change licenses?</span></summary>
        <p class="a">Yes. Move up or down at the start of any month.</p>
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
    <p class="eyebrow">~/oplev/start</p>
    <h2 class="h2" id="next-h">Not sure which license fits?</h2>
    <p class="lede">Tell us what still runs through you. We'll tell you which license fits, even if the answer is none of them.</p>
    <div class="actions">
      <a class="btn" href="start.html">Start a project {ARR_R}</a>
      <a class="btn ghost" href="work.html">See the work {ARR_R}</a>
    </div>
  </div>
</section>'''
    return page('OpLev Pricing', 'Custom software for one monthly license, from $5k a month with hosting, maintenance and updates included. Add a commercial license to sell it to others.',
                body, p='', active='pricing')


# ---------- start ----------

def start():
    return page('Start a Project | OpLev', 'Tell OpLev what still runs through you. Andre or Matt replies personally.',
                inquiry('h1'), p='', active='contact')


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
          <div class="card-foot"><span class="label">{E(c['built'])}</span><span class="label go">Open {ARR_R}</span></div>
        </div>
      </a>''' for i, c in enumerate(CASES))
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><p class="eyebrow">~/oplev/work</p><span class="label">{n:02d} cases</span></div>
    <h1 class="h1" id="h1">Systems we've built.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">Custom software, work agents and lead capture tools for founders and small teams. Each case shows the problem, what we built and a sample run.</p>
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
    if c.get('stack') and not c.get('facts'):
        facts.append(('Stack', c['stack']))
    facts_html = ''.join(f'\n      <div><dt class="label">{k}</dt><dd>{E(v)}</dd></div>' for k, v in facts)
    note = f'\n    <p class="label case-note">{E(c["note"])}</p>' if c.get('note') else ''
    data = json.dumps({'cmd': c['cmd'], 'run': c['run']}).replace('</', '<\\/')
    path = f'~/oplev/work/{c["id"]}'
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><a class="label" href="{p}work.html">{ARR_L} All work</a><span class="label">case {seed:02d} / {n:02d}</span></div>
    <p class="eyebrow">{path}</p>
    <h1 class="h1" id="h1">{E(c['name'])}<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">{E(c['line'])}</p>
    <dl class="facts f{len(facts)}">{facts_html}
    </dl>
    {thumb(c, seed, p)}{note}
  </div>
</section>

<section class="sec" id="before" aria-labelledby="before-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">{path}/before</p>
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
        <p class="eyebrow">{path}/system</p>
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
        <p class="eyebrow">{path}/run</p>
        <h2 class="h2" id="run-h">Watch it run.</h2>
      </div>
      <p class="label">sample run / illustrative</p>
    </div>
    <div class="pane" id="pane" data-state="idle">
      <div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">{path}/run</span><span class="label">sample run</span></div>
      <div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows"></div></div>
      <div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div>
    </div>
  </div>
</section>

<section class="sec" id="results" aria-labelledby="results-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">{path}/results</p>
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
    out = {'index.html': home(), 'pricing.html': pricing(), 'work.html': work(), 'start.html': start()}
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
