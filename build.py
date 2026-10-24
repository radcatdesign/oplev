#!/usr/bin/env python3
"""Build the OpLev site into self-contained HTML pages.

Edit content/cases.json, src/site.css or src/site.js, then run:
    python3 build.py
Outputs index.html, pricing.html, work.html and work/<case>.html at the repo root.
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


# ---------- shared shell ----------

def nav_items(p, home):
    a = (lambda h: h) if home else (lambda h: p + 'index.html' + h)
    return [
        ('work', 'Work', p + 'work.html', '~/oplev/work'),
        ('method', 'Method', a('#method'), '~/oplev/method'),
        ('pricing', 'Pricing', p + 'pricing.html', '~/oplev/pricing'),
        ('contact', 'Contact', a('#contact'), '~/oplev/contact'),
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
    contact = items[3][2]
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
      <a class="btn btn-sm nav-cta" href="{contact}">Start a project</a>
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
      <span>Systems, agents + lead tools</span>
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
<section class="sec" id="start" aria-labelledby="start-h">
  <div class="wrap stack">
    <p class="eyebrow">~/oplev/start</p>
    <h2 class="h2" id="start-h">{title}</h2>
    <p class="lede">{text}</p>
    <div class="actions">
      <a class="btn" href="{p}index.html#contact">Start a project {ARR_R}</a>
      <a class="btn ghost" href="{p}pricing.html">See pricing {ARR_R}</a>
    </div>
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
    body = f'''
<section class="hero" id="hero">
  <canvas class="field" id="field" aria-hidden="true"></canvas>
  <div class="wrap">
    <span class="readout label" id="readout" aria-hidden="true">x 0000 · y 0000</span>
    <p class="eyebrow">~/oplev/systems</p>
    <h1 class="h1" id="h1">We build the systems your business runs on.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">OpLev builds custom operating systems, work agents and lead capture tools for small businesses and startups. We write down how your best people work, build it into the tools you already use, and hand the repeat work to agents that ask before they act.</p>
    <div class="actions">
      <a class="btn" href="#work">See the work {ARR_D}</a>
      <a class="btn ghost" href="#contact">Start a project {ARR_R}</a>
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
    <div class="tk-set"><b>operating systems</b><i>/</i><span>intake</span><i>/</i><span>booking</span><i>/</i><span>onboarding</span><i>/</i><span>follow-up</span><i>/</i><span>playbooks</span><i>/</i><b>work agents</b><i>/</i><span>approvals</span><i>/</i><span>reporting</span><i>/</i><span>inbox triage</span><i>/</i><b>lead capture tools</b><i>/</i><span>calculators</span><i>/</i><span>visualizers</span><i>/</i><span>planners</span><i>/</i></div>
  </div>
</div>

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
      <li class="svc"><svg class="px" data-icon="system" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Operating systems</h3><p>How your business runs, written down: playbooks, workflows and dashboards your team actually uses.</p></li>
      <li class="svc"><svg class="px" data-icon="agent" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Work agents</h3><p>Agents that take the repeat work off your team and ask a person before anything important goes out.</p></li>
      <li class="svc"><svg class="px" data-icon="lead" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">Lead capture tools</h3><p>Calculators, visualizers and planners that answer a buyer's question on your site and capture the lead while they use it.</p></li>
    </ul>
  </div>
</section>

<section class="sec" id="method" aria-labelledby="method-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/method</p>
        <h2 class="h2" id="method-h">How a build runs.</h2>
      </div>
      <p class="label">discuss / build / implement / measure</p>
    </div>
    <ol class="steps">
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">01</span><svg class="px" data-icon="discuss" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Discuss</h3><p>We interview the people doing the work, with help from Mira, our AI interviewer, and map how it actually gets done.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">02</span><svg class="px" data-icon="build" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Build</h3><p>We write it down and build it into your tools: playbooks, workflows, dashboards, agents and the lead tools on your site.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">03</span><svg class="px" data-icon="implement" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Implement</h3><p>We roll it out with your team one function at a time, until it holds without us in the room.</p></li>
      <li class="step"><div class="step-top"><span class="num" aria-hidden="true">04</span><svg class="px" data-icon="measure" viewBox="0 0 50 50" aria-hidden="true"></svg></div><h3 class="h3">Measure</h3><p>We score it. The OpLev Score shows how much of the business runs without leaning on one person, and where to build next.</p></li>
    </ol>
  </div>
</section>

<section class="sec band" id="ownership" aria-labelledby="own-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/ownership</p>
        <h2 class="h2" id="own-h">You own everything we build.</h2>
      </div>
      <p class="label">no lock-in</p>
    </div>
    <div class="terms">
      <div class="term"><h3 class="h3">It lives in your accounts.</h3><p>Docs, workflows and agents run in your tools, under your logins.</p></div>
      <div class="term"><h3 class="h3">Agents ask before they act.</h3><p>Anything that touches a customer, money or a contract waits for a person to approve it.</p></div>
      <div class="term"><h3 class="h3">Every action leaves a log.</h3><p>You can see what each agent did, when it did it and what it was working from.</p></div>
      <div class="term"><h3 class="h3">Stay because it works.</h3><p>After the build, support is month to month. Leave when it stops being useful. The system stays yours.</p></div>
    </div>
  </div>
</section>

<section class="sec" id="contact" aria-labelledby="contact-h">
  <div class="wrap stack">
    <p class="eyebrow">~/oplev/contact</p>
    <h2 class="h2" id="contact-h">Tell us what still runs on you.</h2>
    <p class="lede">Send a short note about the work that only happens when you're there. We'll reply with where we'd start.</p>
    <div class="mail">
      <span class="addr" id="addr">{EMAIL}</span>
      <button class="btn" id="copy" type="button">Copy email {COPY}</button>
      <span class="label" id="copied" aria-live="polite"></span>
    </div>
  </div>
</section>'''
    return page('OpLev', 'OpLev builds custom operating systems and work agents for small businesses and startups.',
                body, p='', home=True, active=None, mode=mode)


# ---------- pricing ----------

def plan(n, name, amt, who, inc, btn):
    lis = ''.join(f'\n          <li>{E(x)}</li>' for x in inc)
    return f'''
      <article class="plan" aria-labelledby="p{n}">
        <div class="plan-top"><span class="label">plan {n:02d} / 03</span></div>
        <div class="plan-id">
          <h3 class="h3" id="p{n}">{name}</h3>
          <p class="price"><span class="amt">{amt}</span><span class="per">/ month</span></p>
        </div>
        <p class="for">{who}</p>
        <ul class="inc">{lis}
        </ul>
        <a class="btn" href="index.html#contact">{btn} {ARR_R}</a>
      </article>'''


def pricing():
    plans = (plan(1, 'One function', '$5k', 'One part of the business needs to stop running through you.',
                  ['One function written down and built out', 'Up to 2 work agents', 'Playbooks for that function',
                   'Monthly OpLev Score', 'Monthly working session', 'Async support, reply within a business day'],
                  'Start with one')
             + plan(2, 'Core ops', '$10k', "A growing team where the work lives in a few people's heads.",
                    ['Up to 3 functions written down and built out', 'Up to 6 work agents', 'Team interviews with Mira',
                     'Dashboards for each function', 'Monthly OpLev Score, scored with your team',
                     'Weekly working session', 'Same-day support'],
                    'Start core ops')
             + plan(3, 'Whole company', '$15k+', 'You want the whole operation written down and running.',
                    ['Every function', 'Custom agents, scoped with you', 'A searchable company knowledge base',
                     'OpLev Score across teams and roles', 'Weekly sessions and on-call support',
                     'Priced by team size and scope'],
                    'Talk to us'))
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <p class="eyebrow">~/oplev/pricing</p>
    <h1 class="h1" id="h1">One monthly fee. No lock-in.<span class="cursor" aria-hidden="true"></span></h1>
    <p class="lede">Every plan covers the build, the agents and the two of us keeping them running. Plans are month to month, and everything we build is yours.</p>
  </div>
</section>

<section class="sec band" id="plans" aria-labelledby="plans-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/plans</p>
        <h2 class="h2" id="plans-h">Pick the scope. We do the work.</h2>
      </div>
      <p class="label">usd / billed monthly</p>
    </div>
    <div class="plans">{plans}
    </div>
    <div class="fine">
      <p class="label">month to month</p>
      <p class="label">switch plans any month</p>
      <p class="label">you own all of it</p>
    </div>
  </div>
</section>

<section class="sec" id="every" aria-labelledby="every-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">~/oplev/plans/all</p>
        <h2 class="h2" id="every-h">In every plan.</h2>
      </div>
    </div>
    <div class="every">
      <div class="ev"><span class="b" aria-hidden="true">[x]</span><h3 class="h3">Built in your tools</h3><p>We work in the software you already pay for. No new platform to learn.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">[x]</span><h3 class="h3">Agents ask first</h3><p>Anything that touches a customer, money or a contract waits for a person to approve it.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">[x]</span><h3 class="h3">You own it</h3><p>Docs, workflows and agents live in your accounts and keep running if you leave.</p></div>
      <div class="ev"><span class="b" aria-hidden="true">[x]</span><h3 class="h3">Founders on the work</h3><p>Andre and Matt do the work themselves. No account managers in between.</p></div>
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
        <summary><span class="h3">Where do we start?</span></summary>
        <p class="a">With the OpLev Score. Your team answers a short set of questions with Mira, and we show you where the business leans on one person. That tells us which plan fits.</p>
      </details>
      <details>
        <summary><span class="h3">Do we even need this?</span></summary>
        <p class="a">Maybe not. If the business runs fine while you take two weeks off, keep your money. We'll tell you that on the first call.</p>
      </details>
      <details>
        <summary><span class="h3">What does the + on Whole company mean?</span></summary>
        <p class="a">It starts at $15k a month and goes up with team size and the number of functions we take on. We quote it after the OpLev Score, so you know the number before you commit.</p>
      </details>
      <details>
        <summary><span class="h3">Can we change plans?</span></summary>
        <p class="a">Yes. Move up or down at the start of any month.</p>
      </details>
      <details>
        <summary><span class="h3">What happens if we stop?</span></summary>
        <p class="a">Everything stays. The playbooks, workflows and agents live in your accounts, so they keep running without us.</p>
      </details>
    </div>
  </div>
</section>
''' + f'''
<section class="sec" id="start" aria-labelledby="start-h">
  <div class="wrap stack">
    <p class="eyebrow">~/oplev/start</p>
    <h2 class="h2" id="start-h">Not sure which plan fits?</h2>
    <p class="lede">Start with the OpLev Score. We'll tell you which plan fits, even if the answer is none of them.</p>
    <div class="actions">
      <a class="btn" href="index.html#contact">Start a project {ARR_R}</a>
      <a class="btn ghost" href="work.html">See the work {ARR_R}</a>
    </div>
  </div>
</section>'''
    return page('OpLev Pricing', 'OpLev plans start at $5k a month. Month to month, and you own everything we build.',
                body, p='', active='pricing')


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
    <p class="lede">Operating systems, work agents and lead capture tools for founders and small teams. Each case shows the problem, what we built and a sample run.</p>
    <div class="cards">{cards}
    </div>
  </div>
</section>''' + cta('Want one of these running for you?',
                    'Tell us what still runs through you. We will show you where we would start.', '')
    return page('OpLev Work', 'Case studies: operating systems and work agents OpLev has built for founders and small teams.',
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
    facts = [('Focus', c['focus']), ('Built', c['built']), ('Includes', c['includes'])]
    if c.get('stack'):
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
    out = {'index.html': home(), 'pricing.html': pricing(), 'work.html': work()}
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
