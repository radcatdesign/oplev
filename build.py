#!/usr/bin/env python3
"""Build the OpLev site into self-contained HTML pages.

Edit content/cases.json, src/site.css or src/site.js, then run:
    python3 build.py
Outputs index.html, pricing.html, work.html, start.html, for.html, for/<business>.html,
app.html (an example client dashboard) and work/<case>.html at the repo root.
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
JOBS = json.loads((ROOT / 'content' / 'jobs.json').read_text())
MARKET = json.loads((ROOT / 'content' / 'marketplace.json').read_text())
MARKET_BY = {x['id']: x for x in MARKET}
_ICPS = json.loads((ROOT / 'content' / 'icps.json').read_text())
GROUPS = _ICPS['groups']
ICPS = _ICPS['items']
ICP = {x['id']: x for x in ICPS}
GROUP = {g['id']: g for g in GROUPS}
SETUP_GROUP = {'clinic': 'health', 'brand': 'brands', 'agency': 'firms', 'creator': 'founders', 'startup': 'founders'}


def icps_in(gid):
    return [x for x in ICPS if x['group'] == gid]

MARKET_TYPES = [('clinic', 'Clinics'), ('brand', 'Brands'), ('agency', 'Agencies'), ('creator', 'Creators'),
                ('startup', 'Startups'), ('services', 'Services')]
LICENSES = {'one': {'name': 'One engine', 'price': '$5k', 'count': 1},
            'core': {'name': 'Two engines', 'price': '$10k', 'count': 2},
            'company': {'name': 'Three or more', 'price': '$15k+', 'count': 3}}

EMAIL = 'hello@oplev.com'
# Client capacity shown across the site. Set these to your real numbers.
CAPACITY = {'window': 'Q1 2027', 'total': 4, 'open': 2}
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
    ('marketing', 'Marketing', 'wind', 'Get the word out', 'Emails and landing pages that keep your name in front of the right people.',
     ['Newsletters and email series, sent from your own domain', 'Landing pages with forms that turn visitors into leads',
      'A brand kit, so every email and page looks like you', 'Page tests and search setup that show what works'],
     ['fit-funnels']),
]
ENGINE_NAME = {k: n for k, n, *_ in ENGINES}
NE = len(ENGINES)
# how each engine connects to the website everything grows from
SITE_LINK = {
    'leads': ('site to leads', 'Quotes, calculators and fast replies turn visitors into real conversations.'),
    'agents': ('site to agents', 'Answers everyone who reaches out through the site, and books the visit.'),
    'ops': ('site to ops', 'Every booking, order and form from the site lands in one place.'),
    'marketing': ('back to the site', 'Emails, pages and search keep sending people back.'),
}
# every engine has an element
ELEMENT = {'ops': 'Water', 'agents': 'Earth', 'leads': 'Fire', 'marketing': 'Wind'}
ELEM_TILES = {
    'ops': ['...#...', '..###..', '.#####.', '#######', '##.####', '#######', '.#####.'],
    'agents': ['....###', '..#####', '.######', '.#####.', '.####..', '#.#....', '#......'],
    'leads': ['..#....', '..##...', '.###.#.', '.#####.', '###.###', '##...##', '.#####.'],
    'marketing': ['#####..', '.....#.', '####..#', '......#', '######.', '.......', '###....'],
}


def elem(k, cls=''):
    t = ELEM_TILES[k]
    rects = ''.join(f'<rect x="{x * 10 + .5}" y="{y * 10 + .5}" width="9" height="9"/>'
                    for y, row in enumerate(t) for x, c in enumerate(row) if c == '#')
    return f'<svg class="elem e-{k}{cls}" viewBox="0 0 70 70" aria-hidden="true">{rects}</svg>'
# each engine is a character: a name, a role and a temper
BOT_ROLE = {
    'ops': ('The organizer', 'Calm and steady, like water. Gets into every corner of the business and keeps it all flowing. Up at 6 with your day sorted.'),
    'agents': ('The helpers', 'Solid as a mountain range. There are a few of them, they do the heavy lifting every shift, and they always ask before sending anything new.'),
    'leads': ('The go-getter', 'All fire. First to say hi, answers at 10pm, remembers every name and never lets a quote go cold.'),
    'marketing': ('The messenger', 'Quick as the wind. Carries your name further: emails from your own domain, landing pages that capture leads, and tests that show what works.'),
}


def bot_card(k):
    n = 3 if k == 'agents' else 1
    bots = ''.join(f'<span class="bot" data-bot="{k}"></span>' for _ in range(n))
    return (f'<button class="bot-card e-{k}" type="button" aria-label="Say hi to {ENGINE_NAME[k]}">'
            f'<span class="bot-stage n{n}">{bots}</span><span class="bot-say" aria-live="polite"></span></button>')

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
    ('marketing', 'when someone joins your list', 'Welcome series', 'Welcome emails on a schedule, with a one-time offer code. Nobody gets the same series twice.'),
    ('marketing', 'once a month', 'Monthly newsletter', 'Built from your brand kit, tested on your team, then sent from your own domain.'),
    ('marketing', 'when you need a page', 'Landing page from a brief', 'Describe the page and it builds it, with a form that turns visitors into leads.'),
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
        ['04:10:00', '@marketing', 'welcome email 2 to 3 new subscribers', 'sent'],
        ['05:45:00', '@ops', 'morning summary ready: 1 approval, 2 new leads', 'ready'],
        ['06:58:21', 'you', 'approve reply to the new lead', 'pending', 'need'],
        ['07:04:02', 'you', 'approved over coffee', 'ok', 'me'],
        ['07:04:04', '@agents', 'sent the reply and a booking link', 'sent'],
    ],
}

# what owners tell us, and what fixes it: an engine key, 'system' (all of them together) or 'resale'
PAINS = [
    ('Everything still runs through me.', 'ops'),
    ('Our website looks fine and does nothing.', 'site'),
    ('I pay for a stack of apps and still live in spreadsheets.', 'system'),
    ('Leads come in at night and sit until Monday.', 'leads'),
    ("I can't take a week off.", 'agents'),
    ("Nobody's heard of us outside of referrals.", 'marketing'),
    ('Only one person knows how that part works.', 'ops'),
    ('I answer the same five questions every day.', 'agents'),
    ('People keep asking if they can use what I built.', 'resale'),
]
QMARK = ['##.##', '##.##', '.#..#', '#..#.']


def qmark():
    rects = ''.join(f'<rect x="{x * 10 + .5}" y="{y * 10 + .5}" width="9" height="9"/>'
                    for y, row in enumerate(QMARK) for x, c in enumerate(row) if c == '#')
    return f'<svg class="sc-qm" viewBox="0 0 50 40" aria-hidden="true">{rects}</svg>'


def pain_card(i, text, k):
    if k in ENGINE_NAME:
        icon, who, cls = f'<span class="bot bot-xs" data-bot="{k}"></span>', f'{ENGINE_NAME[k]}', f'e-{k}'
    elif k == 'site':
        icon, who, cls = '<span class="sc-site" aria-hidden="true"><i></i></span>', 'A website that sells', 'e-sys'
    elif k == 'system':
        icon, who, cls = edots([e for e, *_ in ENGINES]), 'All four, as one system', 'e-sys'
    else:
        icon, who, cls = '<span class="sc-lic" aria-hidden="true"></span>', 'A resale license', 'e-sys'
    return (f'\n        <li class="say-card {cls}"><div class="sc-top"><span class="label">{i + 1:02d}</span>{qmark()}</div>'
            f'<q class="sc-q">{E(text)}</q><div class="sc-ft"><span class="label">fixed by</span><span class="sc-by">{icon}{E(who)}</span></div></li>')

CMP_HEAD = ('Off-the-shelf apps', 'A typical agency', 'OpLev')
CMP = [
    ('Starts with a website that sells', 'No. You bring your own.', 'Sometimes, as a separate project', 'Yes. Everything runs off it'),
    ('Built around how you work', 'No. You work around it.', 'Yes', 'Yes'),
    ('How you pay', 'Per app, per person, every month', 'A big build fee, then hourly fixes', 'One monthly price'),
    ('Who keeps it running', 'You do', 'You, or a developer you hire', 'We do, every month'),
    ('Gets better over time', 'On their roadmap, not yours', 'Only when you pay for it', 'Updates included'),
    ('Can you sell it', 'No', 'Depends on your contract', 'Yes, with a resale license'),
]

F_TYPE = [('clinic', 'Health or wellness'), ('field', 'Home or field service'), ('brand', 'Product brand'),
          ('agency', 'Agency or firm'), ('creator', 'Creator or coach'), ('startup', 'Startup'), ('other', 'Something else')]
F_TEAM = [('1', 'Just me'), ('2-5', '2 to 5'), ('6-20', '6 to 20'), ('21-50', '21 to 50'), ('50', '50+')]
F_BUILD = [('ops', 'Staying organized (Ops)'), ('agents', 'Busywork and follow-ups (Agents)'), ('leads', 'Getting more customers (Leads)'),
           ('marketing', 'Getting the word out (Marketing)'),
           ('unsure', 'Not sure yet')]
F_LICENSE = [('one', 'One engine / $5k'), ('core', 'Two engines / $10k'), ('company', 'Three or more / $15k+'),
             ('unsure', 'Not sure yet')]
F_RESALE = [('yes', 'Yes'), ('later', 'Maybe later'), ('no', 'No')]
F_TIMING = [('month', 'This month'), ('quarter', 'This quarter'), ('exploring', 'Just exploring')]


# ---------- shared shell ----------

def nav_items(p, home):
    a = (lambda h: h) if home else (lambda h: p + 'index.html' + h)
    return [
        ('work', 'Work', p + 'work.html', 'case studies', False),
        ('how', 'How it works', p + 'how-it-works.html', 'start to finish', False),
        ('for', "Who it's for", p + 'for.html', f'{len(ICPS)} businesses', False),
        ('market', 'Marketplace', p + 'marketplace.html', 'ready-made systems', False),
        ('pricing', 'Pricing', p + 'pricing.html', 'how we charge', False),
        ('contact', 'Apply', p + 'start.html', 'limited spots', True),
    ]


def edots(keys):
    return '<span class="edots" aria-hidden="true">' + ''.join(f'<i class="e-{k}"></i>' for k in keys) + '</span>'


def mega(p):
    cols = ''.join(f'''
        <div class="mg-col">
          <a class="mg-g label" href="{p}for.html#{g['id']}"><span>{gi + 1:02d}</span>{E(g['name'])}</a>
          <ul>{''.join(f'<li><a href="{p}for/{x["id"]}.html"><span class="mg-n">{E(x["name"])}</span>{edots(x["engines"])}</a></li>' for x in icps_in(g['id']))}</ul>
        </div>''' for gi, g in enumerate(GROUPS))
    return f'''
  <div class="mega" id="mega" hidden>
    <div class="wrap">
      <div class="mg-grid">{cols}
      </div>
      <div class="mg-ft">
        <p class="mg-ft-t">Not on the list? Every build starts from how you work, so tell us about yours.</p>
        <div class="mg-ft-r"><span class="mg-key label">{''.join(f'{edots([k])}{n} ' for k, n, *_ in ENGINES)}</span><a class="label mg-all" href="{p}for.html">See all {len(ICPS)} {ARR_R}</a><a class="btn btn-sm" href="{p}start.html">Apply</a></div>
      </div>
    </div>
  </div>'''


def menu_for(p):
    groups = ''.join(
        f'<div class="mf-g"><p class="label">{E(g["name"])}</p><ul>'
        + ''.join(f'<li><a href="{p}for/{x["id"]}.html">{E(x["name"])}</a></li>' for x in icps_in(g['id']))
        + '</ul></div>' for g in GROUPS)
    return f'<div class="menu-for" id="menu-for" hidden>{groups}<a class="label mf-all" href="{p}for.html">See all {len(ICPS)} {ARR_R}</a></div>'


def shell_top(p, home, active):
    items = nav_items(p, home)
    cur = lambda k: ' aria-current="page"' if k == active else ''
    links = ''.join(
        (f'\n      <button class="links-btn" id="mega-btn" type="button" aria-expanded="false" aria-controls="mega"'
         f'{" data-current" if k == active else ""}>{t}<i class="chev" aria-hidden="true"></i></button>') if k == 'for' else
        f'\n      <a href="{h}"{cur(k)}>{t}</a>'
        for k, t, h, _, menu_only in items if not menu_only)
    menu = ''.join(
        (f'\n        <li class="menu-sub"><button class="menu-sub-btn" type="button" aria-expanded="false" aria-controls="menu-for">'
         f'<span class="mn">{i + 1:02d}</span><span class="mt">{t}</span><span class="mp">{pth}<i class="pm" aria-hidden="true"></i></span></button>'
         f'{menu_for(p)}</li>') if k == 'for' else
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
      <a class="spots-pill" href="{p}start.html"><span class="dot" aria-hidden="true"></span>{CAPACITY['open']} spots open</a>
      <a class="btn btn-sm nav-cta" href="{p}start.html">Apply</a>
      <button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="bars" aria-hidden="true"></span><span class="mb-t">Menu</span></button>
    </div>
  </div>{mega(p)}
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


# Doto 900 capitals, read from the font: 5x7 tiles on a 6-column advance
GLYPHS = {
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'P': ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '.#.#.', '..#..'],
}


def wordmark_svg(word='OPLEV'):
    groups = ''
    for i, ch in enumerate(word):
        ox = i * 600
        tiles = ''.join(f'<rect class="t" x="{ox + c * 100 + 5}" y="{r * 100 + 5}" width="90" height="90"/>'
                        for r, row in enumerate(GLYPHS[ch]) for c, v in enumerate(row) if v == '#')
        groups += f'<g class="wm-l">{tiles}</g>'
    w = (len(word) - 1) * 600 + 500
    return f'<svg class="wm-svg" id="wm-t" viewBox="5 5 {w - 10} 690" aria-hidden="true">{groups}</svg>'


def shell_bottom():
    return f'''
<footer class="foot">
  <div class="wrap">
    <p class="wm" id="wm" role="img" aria-label="OpLev">{wordmark_svg()}</p>
    <div class="frow label">
      <span>OpLev</span>
      <span>The business engine that operates itself.</span>
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


def spots(cls=''):
    c = CAPACITY
    segs = ''.join(f'<i class="{"taken" if i < c["total"] - c["open"] else "open"}"></i>' for i in range(c['total']))
    return (f'<div class="spots{cls}"><span class="sp-meter" aria-hidden="true">{segs}</span>'
            f'<span class="label">{E(c["window"])} / <b>{c["open"]} of {c["total"]} client spots open</b></span></div>')


def job_of(title, sid=None):
    j = None
    for s in (sid if isinstance(sid, (list, tuple)) else [sid]):
        if s and f'{s}:{title}' in JOBS:
            j = JOBS[f'{s}:{title}']
            break
    j = j or JOBS.get(title)
    assert j, f'no walkthrough for job: {title}'
    return j


def job_cards(items, sid=None, p='', extra_cls='', start=None, demo=None):
    """Clickable job cards plus the data the walkthrough sheet plays."""
    cards, data = [], []
    for i, (e, trig, title, desc) in enumerate(items):
        j = job_of(title, sid)
        data.append({'e': e, 'name': ENGINE_NAME[e], 'trig': trig, 'title': title, 'desc': desc,
                     'ex': j['ex'], 'steps': j['steps'], 'you': j['you'], 'get': j['get']})
        cards.append(f'''
      <li class="play e-{e}" data-e="{e}"><div class="play-top">{etags([e])}<span class="label play-trig">{E(trig)}</span></div><h3 class="h3"><button class="play-open" type="button" data-job="{i}" aria-haspopup="dialog">{E(title)}</button></h3><p>{E(desc)}</p><span class="play-go label" aria-hidden="true">see how it works {ARR_R}</span></li>''')
    sid1 = sid if isinstance(sid, str) else None
    start = start or (f'{p}start.html' + (f'#{sid1}' if sid1 else ''))
    demo = demo or (f'{p}app.html' + (f'#{sid1}' if sid1 else ''))
    blob = json.dumps({'start': start, 'demo': demo, 'jobs': data}).replace('</', '<\\/')
    return (f'<ul class="plays{extra_cls}" data-jobs="jobs-data">' + ''.join(cards) + '\n    </ul>\n'
            f'    <script type="application/json" id="jobs-data">{blob}</script>')


def site_mock(domain='yourbusiness.com', cls=''):
    return f'''<figure class="site-mock{cls}" aria-label="Your website">
          <div class="sm-bar"><i></i><i></i><i></i><span>{E(domain)}</span></div>
          <div class="sm-body">
            <div class="sm-nav"><b></b><i></i><i></i><i></i><em>Book now</em></div>
            <div class="sm-hero"><p class="sm-h">Your headline, written to sell.</p><p class="sm-p"></p><p class="sm-p s"></p><span class="sm-cta">Get a price</span></div>
            <div class="sm-row">
              <div class="sm-card sm-calc"><span class="label">instant price</span><div class="sm-sl"><i></i></div><b class="sm-amt">$<span data-sm-amt>1,240</span></b></div>
              <div class="sm-card sm-form"><span class="label">talk to us</span><i></i><i></i><em>Send</em></div>
            </div>
          </div>
        </figure>'''


def site_section(eyebrow, heading, lede, hid='site-h'):
    order = ['leads', 'agents', 'ops', 'marketing']
    nodes = ''.join(
        f'<div class="sn e-{k}"><div class="sn-hd"><span class="bot bot-xs" data-bot="{k}"></span><b>{E(ENGINE_NAME[k])}</b>'
        f'<span class="label">{E(ELEMENT[k].lower())}</span></div><p>{E(SITE_LINK[k][1])}</p><span class="label sn-flow">{E(SITE_LINK[k][0])}</span></div>'
        for k in order)
    stems = ''.join(
        f'<path class="stem e-{k}{" up" if k == "marketing" else ""}" d="M500 0 C 500 60, {x} 50, {x} 120" vector-effect="non-scaling-stroke"/>'
        for k, x in zip(order, (125, 375, 625, 875)))
    return f'''
<section class="sec site-sec" id="website" aria-labelledby="{hid}">
  <div class="wrap">
    <div class="site-hd">
      <div class="head-l">
        <p class="eyebrow">{eyebrow}</p>
        <h2 class="h2" id="{hid}">{heading}</h2>
      </div>
      <p class="lede">{lede}</p>
    </div>
    <div class="site-map">
      <div class="site-stage">
        <ul class="site-notes">
          <li><b>Fast</b><span>Loads before people lose interest.</span></li>
          <li><b>Found</b><span>Set up for Google and AI search.</span></li>
        </ul>
        {site_mock()}
        <ul class="site-notes">
          <li><b>Convincing</b><span>Design and words that make the case.</span></li>
          <li><b>Converting</b><span>Every page ends in a next step, and we test what works.</span></li>
        </ul>
      </div>
      <svg class="stems" viewBox="0 0 1000 120" preserveAspectRatio="none" aria-hidden="true">{stems}</svg>
      <div class="site-nodes">{nodes}</div>
    </div>
  </div>
</section>
'''


# ---------- the build walkthrough on home ----------
# a made-up business per industry, for the website mock: (name, headline, button)
SITE_COPY = {
    'med-spas': ('Lumen Aesthetics', 'Look like you. Just rested.', 'Book a consult'),
    'dental': ('Brightside Dental', "A dentist you won't dread.", 'Book a visit'),
    'physical-therapy': ('Juniper Physio', 'Back to the things you love.', 'Book an evaluation'),
    'gyms': ('Ironwood Fitness', 'Your first week is on us.', 'Start a free trial'),
    'pool-service': ('Clearwater Pools', 'A clean pool, every week.', 'Get a price'),
    'hvac-plumbing': ('Northside Heat + Air', 'Fixed today. Priced up front.', 'Request service'),
    'landscaping': ('Greenline Yards', 'A yard you want to be in.', 'Price your project'),
    'contractors': ('Benchmark Builders', 'Remodels done right, on time.', 'Get a ballpark'),
    'ecommerce': ('Fieldday Goods', 'Made to be used every day.', 'Shop now'),
    'food-beverage': ('Sunday Soda Co.', 'Real fruit. Nothing weird.', 'Find a store'),
    'beauty': ('Kindred Skin', 'Skin care that fits your skin.', 'Find your routine'),
    'showrooms': ('Quarry House', "Surfaces you'll love for decades.", 'Price your project'),
    'agencies': ('Northbound Studio', 'Work that moves the numbers.', 'Start a project'),
    'law': ('Hale + Ortiz Law', 'Clear answers. Fast.', 'Free consultation'),
    'accounting': ('Ledgerline CPA', 'Books done. Taxes handled.', 'Book a call'),
    'real-estate': ('Summit Realty', 'Find home faster.', 'See listings'),
    'startups': ('Relay', 'Ship what your users asked for.', 'Join the waitlist'),
    'creators': ('Wren Talks', 'New episodes every Tuesday.', 'Subscribe'),
    'coaches': ('Clear Path Coaching', 'Lead your team with less noise.', 'Book a discovery call'),
    'events': ('Golden Hour Events', 'Weddings that feel like you.', 'Check your date'),
}
# what each engine does on its own, in one line
ENGINE_DOES = {
    'leads': ('It answers every lead.', 'Prices, questions and bookings from your website, answered in minutes, day or night.'),
    'agents': ('It follows up for you.', 'Reminders, rebooking and invoice nudges in your voice. Anything new waits for your OK.'),
    'ops': ('It keeps the day on track.', 'Schedule, clients, orders and numbers stay current. A summary hits your phone at 6am.'),
    'marketing': ('It brings people back.', 'Newsletters and welcome emails from your own domain, and pages that turn visitors into leads.'),
}
BUILD_ORDER = ['leads', 'agents', 'ops', 'marketing']
BUILD_STYLES = [
    ('clean', 'Clean', 'Light, sharp and roomy. Lets the work speak.'),
    ('bold', 'Bold', 'Dark, big type, hard to miss.'),
    ('warm', 'Warm', 'Soft color and serif type. Feels personal.'),
    ('playful', 'Playful', 'Bright blocks and round shapes. Full of energy.'),
]
BUILD_STEPS = [('Set your base', 'step-1'), ('Choose your add-ons', 'step-2'),
               ('Choose your build style', 'step-3'), ('Watch it run', 'step-4')]


def builder(x0):
    data = {
        'icps': {x['id']: {'n': x['name'], 'f': x['form'][0], 'e': x['engines'],
                           'site': SITE_COPY[x['id']],
                           't': {k: [[n, line, 1 if ji is not None else 0] for n, line, ji in v] for k, v in tools_for(x).items()}}
                 for x in ICPS},
        'eng': {k: {'n': ENGINE_NAME[k], 'el': ELEMENT[k]} for k in BUILD_ORDER},
        'styles': {k: n for k, n, _ in BUILD_STYLES},
    }
    blob = json.dumps(data, separators=(',', ':')).replace('</', '<\\/')
    opts_html = ''.join(f'<optgroup label="{E(g["name"])}">' + ''.join(
        f'<option value="{x["id"]}"{" selected" if x is x0 else ""}>{E(x["name"])}</option>' for x in icps_in(g['id'])) + '</optgroup>' for g in GROUPS)
    base = ''.join(f'''
        <button class="bx-eng e-{k}" type="button" data-eng="{k}" aria-pressed="{"true" if k in x0["engines"] else "false"}">
          <span class="bx-eng-top"><span class="bot bot-xs" data-bot="{k}"></span><b>{E(ENGINE_NAME[k])}</b><span class="label">{E(ELEMENT[k].lower())}</span><span class="bx-check" aria-hidden="true"></span></span>
          <span class="bx-eng-h">{E(ENGINE_DOES[k][0])}</span>
          <span class="bx-eng-p">{E(ENGINE_DOES[k][1])}</span>
        </button>''' for k in BUILD_ORDER)
    styles = ''.join(f'''
        <label class="bx-style s-{k}"><input type="radio" name="bx-style" value="{k}"{" checked" if i == 0 else ""}><span class="bx-sw" aria-hidden="true"><i></i><i></i><i></i></span><b>{E(n)}</b><span>{E(d)}</span></label>'''
                     for i, (k, n, d) in enumerate(BUILD_STYLES))
    site0 = SITE_COPY[x0['id']]

    def head(i, title, lede):
        return f'''
      <div class="bs-hd">
        <span class="bs-n" aria-hidden="true">0{i}</span>
        <div class="head-l"><p class="eyebrow">Step {i} of 4</p><h2 class="h2" id="step-{i}-h">{title}</h2></div>
        <p class="lede">{lede}</p>
      </div>'''

    def nxt(i, text):
        return f'<div class="bs-next"><a class="btn ghost" href="#step-{i}">Next: {text} {ARR_D}</a></div>'

    return f'''
<div class="bx" id="build" data-bx>
  <script type="application/json" id="bx-data">{blob}</script>

  <section class="sec bstep" id="step-1" aria-labelledby="step-1-h">
    <div class="wrap">{head(1, 'Set your base.', 'Every engine starts with a website built to sell. Pick your business, then the engines it runs on.')}
      <div class="tpick bx-pick"><label class="tpick-l" for="bx-biz">My business</label><span class="tpick-s"><select id="bx-biz">{opts_html}</select></span></div>
      <div class="bx-base">
        <div class="bx-site">
          <span class="bx-eng-top"><span class="bx-site-ic" aria-hidden="true"><i></i><i></i><i></i></span><b>Website</b><span class="label">always on</span></span>
          <span class="bx-eng-h">It brings them in.</span>
          <span class="bx-eng-p">Designed to sell, fast, and set up for Google and AI search. Everything else runs off it.</span>
        </div>{base}
      </div>
      <div class="bx-total"><span class="bx-meter" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span class="label"><b data-bx-count>{len(x0["engines"])} engines</b> / <b data-bx-price>$15k+</b> a month / website included</span></div>
      {nxt(2, 'choose your add-ons')}
    </div>
  </section>

  <section class="sec bstep" id="step-2" aria-labelledby="step-2-h">
    <div class="wrap">{head(2, 'Choose your add-ons.', 'Tools made for your kind of business. Each one plugs into an engine. Add any, any time.')}
      <div class="bx-tools" id="bx-tools"></div>
      <p class="label bx-note"><b data-bx-tcount>4 add-ons</b> / priced per tool, added monthly</p>
      {nxt(3, 'choose your build style')}
    </div>
  </section>

  <section class="sec bstep" id="step-3" aria-labelledby="step-3-h">
    <div class="wrap">{head(3, 'Choose your build style.', 'How your website looks and feels. We design every site from scratch. This sets the direction.')}
      <div class="bx-look">
        <fieldset class="bx-styles"><legend class="sr">Build style</legend>{styles}
        </fieldset>
        <div class="bx-prev" data-bx-mock="style"></div>
      </div>
      {nxt(4, 'watch it run')}
    </div>
  </section>

  <section class="sec bstep bs-run" id="step-4" aria-labelledby="step-4-h">
    <div class="wrap">{head(4, 'Now watch it run.', 'One day in your business with this build. It does the work. You step in when it asks.')}
      <div class="bx-run">
        <div class="bx-stage">
          <div class="bx-stats">
            <div><span class="label">time</span><b data-bx-clock>5:59am</b></div>
            <div><span class="label">done on its own</span><b data-bx-auto>0</b></div>
            <div><span class="label">needed you</span><b data-bx-you>0</b></div>
          </div>
          <div class="bx-prev" data-bx-mock="run"></div>
        </div>
        <div class="bx-log">
          <div class="bx-log-hd"><span class="label" data-bx-logt>a day at {E(site0[0].lower())}</span><button class="btn bx-play" type="button" data-bx-play>Run the day {ARR_R}</button></div>
          <ol class="bx-rows" data-bx-rows></ol>
          <div class="bx-done" data-bx-done hidden>
            <p class="bx-done-h" data-bx-sum aria-live="polite"></p>
            <div class="actions"><a class="btn" href="start.html#build" data-bx-apply>Apply with this build {ARR_R}</a><button class="btn ghost" type="button" data-bx-again>Run it again {ARR_R}</button></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <div class="bx-bar" data-bx-bar>
    <div class="wrap bx-bar-in">
      <div class="bxb-sum"><span class="label">your build</span><b data-bx-biz>{E(x0['name'])}</b><span class="bxb-meta" data-bx-meta></span></div>
      <div class="bxb-price"><b data-bx-price>$15k+</b><span class="label">a month</span></div>
      <a class="btn bxb-go" href="start.html#build" data-bx-apply><span>Apply<span class="bxb-long"> with this build</span></span> {ARR_R}</a>
    </div>
  </div>
</div>
'''


def tools_for(x):
    """Tools for one kind of business, by engine: (name, line, index of its walkthrough or None)."""
    out = {k: [] for k, *_ in ENGINES}
    for i, (e, _trig, title, desc) in enumerate(x['jobs']):
        out[e].append((title, desc, i))
    for e, items in x.get('extra', {}).items():
        out[e] += [(n, line, None) for n, line in items]
    return out


def tool_cols(x, run=False):
    T = tools_for(x)
    cols = ''
    for k, name, _i, _triad, line, *_ in ENGINES:
        usual = k in x['engines']
        items = ''
        for tname, tline, ji in T[k]:
            live = run and ji is not None
            inner = (f'<span class="label tl-k">+ tool{" / see it run" if live else ""}</span>'
                     f'<b class="tl-n">{E(tname)}</b><span class="tl-d">{E(tline)}</span>')
            items += (f'<li class="tl"><button class="play-open tool-in" type="button" data-job="{ji}" aria-haspopup="dialog">{inner}</button></li>'
                      if live else f'<li class="tl"><div class="tool-in">{inner}</div></li>')
        cols += (f'\n      <div class="tcol e-{k}{" usual" if usual else ""}"><div class="tcol-hd"><span class="bot bot-xs" data-bot="{k}"></span>'
                 f'<b>{E(name)}</b><span class="label">{E(ELEMENT[k].lower())}</span><span class="label tcol-st">{"usually first" if usual else "add any time"}</span></div>'
                 f'<p class="tcol-core"><span class="label">the engine</span>{E(line)}</p><ul class="tlist">{items}</ul></div>')
    return cols


def cta(title, text, p):
    return f'''
<section class="sec" id="next" aria-labelledby="next-h">
  <div class="wrap stack">
    <p class="eyebrow">Next step</p>
    <h2 class="h2" id="next-h">{title}</h2>
    <p class="lede">{text}</p>
    <div class="actions">
      <a class="btn" href="{p}start.html">Apply {ARR_R}</a>
      <a class="btn ghost" href="{p}pricing.html">See pricing {ARR_R}</a>
    </div>
  </div>
</section>'''


def opts(name, items, kind='radio', checked=None):
    return ''.join(
        f'<label class="opt"><input type="{kind}" id="inq-{name}-{v}" name="{name}" value="{E(t)}"{" checked" if v == checked else ""}><span>{E(t)}</span></label>'
        for v, t in items)


def inquiry(level='h2', heading='Apply to work with us.',
            lede="We only take on a few clients at a time, so every build gets our full attention. Tell us about your business. If it's a fit, we'll set up a call.",
            preset=None, other='', src=''):
    first = level == 'h1'
    hid = 'h1' if first else 'start-h'
    cursor = '' if first else ''
    cls = 'inq-page' if first else 'sec'
    return f'''
<section class="{cls}" id="start" aria-labelledby="{hid}">
  <div class="wrap inq-wrap">
    <div class="inq-side">
      <p class="eyebrow">Apply</p>
      <{level} class="{level}" id="{hid}">{heading}{cursor}</{level}>
      <p class="lede">{lede}</p>
      {spots(' inq-spots')}
      <p class="label inq-alt">Prefer email? <span class="sel">{EMAIL}</span></p>
    </div>
    <form class="inq" action="/api/inquiry" method="post" novalidate data-email="{EMAIL}" aria-label="Application">
      <div class="inq-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">Application</span><span class="label">* required</span></div>
      <div class="inq-os" hidden><span class="label">asking about</span><b class="inq-os-n"></b><button class="label inq-os-x" type="button">remove &times;</button><input type="hidden" name="os" id="inq-os" disabled></div>
      <div class="inq-os inq-build" hidden><span class="label">your build</span><b class="inq-os-n"></b><button class="label inq-os-x" type="button">remove &times;</button><input type="hidden" name="setup" disabled></div>
      <script type="application/json" class="os-names">{json.dumps({x['id']: x['name'] for x in MARKET})}</script>
      <div class="inq-grid">
        <label class="fl"><span class="label" data-err="add your name">Name *</span><input class="inp" id="inq-name" name="name" autocomplete="name" maxlength="120" required></label>
        <label class="fl"><span class="label" data-err="add a valid email">Email *</span><input class="inp" id="inq-email" name="email" type="email" autocomplete="email" maxlength="200" required></label>
      </div>
      <label class="fl"><span class="label">Company</span><input class="inp" id="inq-company" name="company" autocomplete="organization" maxlength="160"></label>
      <fieldset class="fs"><legend class="label">What kind of business?</legend><div class="opts">{opts('type', F_TYPE, checked=preset)}</div><label class="fl type-other" hidden><span class="sr">What kind of business is it?</span><input class="inp" id="inq-type-detail" name="type_other" maxlength="80" placeholder="What kind of business is it?" autocomplete="off" value="{E(other)}" disabled></label></fieldset>
      <fieldset class="fs"><legend class="label">Team size</legend><div class="opts">{opts('team', F_TEAM)}</div></fieldset>
      <label class="fl"><span class="label" data-err="tell us a little">What still runs through you? *</span><textarea class="inp" id="inq-message" name="message" rows="5" maxlength="4000" required placeholder="The work that only happens when you're there."></textarea></label>
      <fieldset class="fs"><legend class="label">What do you need help with?</legend><div class="opts">{opts('build', F_BUILD, 'checkbox')}</div></fieldset>
      <fieldset class="fs"><legend class="label">Which plan sounds right?</legend><div class="opts">{opts('license', F_LICENSE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">Would you want to sell it to others one day?</legend><div class="opts">{opts('resale', F_RESALE)}</div></fieldset>
      <fieldset class="fs"><legend class="label">When do you want to start?</legend><div class="opts">{opts('timing', F_TIMING)}</div></fieldset>
      {f'<input type="hidden" name="page" value="{E(src)}">' if src else ''}<div class="hp" aria-hidden="true"><label>Leave this empty <input id="inq-hp" name="company_url" tabindex="-1" autocomplete="off"></label></div>
      <div class="inq-foot"><button class="btn" type="submit">Submit application {ARR_R}</button><p class="label">We reply to every application.</p></div>
      <div class="inq-status" aria-live="polite" hidden></div>
    </form>
  </div>
</section>'''


# ---------- home ----------

def home(mode='full'):
    n = len(CASES)
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
    pains = ''.join(pain_card(i, t, k) for i, (t, k) in enumerate(PAINS))
    say_meter = ''.join('<i></i>' for _ in PAINS)
    steps_html = ''.join(f'<a class="htab" href="#{h}"><b>0{i + 1}</b>{E(t)}</a>' for i, (t, h) in enumerate(BUILD_STEPS))
    body = f'''
<section class="hero" id="hero">
  <canvas class="field" id="field" aria-hidden="true"></canvas>
  <div class="wrap">
    <span class="readout label" id="readout" aria-hidden="true">x 0000 · y 0000</span>
    <p class="eyebrow">Custom built for your business</p>
    <h1 class="h1 h1-x" id="h1" aria-label="The ultimate business engine.">The ultimate business <s class="xo">website</s> engine.</h1>
    <p class="lede">It answers leads, books, follows up and brings people back, on its own. We build it around how you work and keep it tuned.</p>
    {spots(' hero-spots')}
    <div class="actions">
      <a class="btn" href="#step-1">Build your engine {ARR_D}</a>
      <a class="btn ghost" href="start.html">Apply for a spot {ARR_R}</a>
    </div>
    <nav class="htabs hsteps" aria-label="Build your engine in four steps">{steps_html}</nav>
  </div>
</section>
''' + builder(ICP['pool-service']) + f'''
<section class="sec say" id="familiar" aria-labelledby="familiar-h">
  <div class="wrap say-hd">
    <div>
      <p class="eyebrow">Sound familiar?</p>
      <h2 class="say-h" id="familiar-h">You started a business. Then it became a job.</h2>
    </div>
    <div class="say-ctl">
      <span class="label say-n" aria-hidden="true"><b>01</b> / {len(PAINS):02d}</span>
      <button class="say-btn" type="button" data-say="-1" aria-label="Previous">{ARR_L}</button>
      <button class="say-btn" type="button" data-say="1" aria-label="Next">{ARR_R}</button>
    </div>
  </div>
  <ul class="say-rail" tabindex="0" aria-label="Things owners tell us">{pains}
  </ul>
  <div class="wrap">
    <div class="say-meter" aria-hidden="true">{say_meter}</div>
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

<section class="sec close-sec" id="start" aria-labelledby="close-h">
  <div class="wrap close-in">
    {spots(' close-spots')}
    <h2 class="close-h" id="close-h">{CAPACITY['open']} client spots left for {E(CAPACITY['window'])}.</h2>
    <p class="lede">We build it, run it and keep improving it. From $5k a month, website included. We reply to every application.</p>
    <div class="actions"><a class="btn" href="start.html">Apply for a spot {ARR_R}</a><a class="btn ghost" href="pricing.html">See pricing {ARR_R}</a></div>
  </div>
</section>
'''
    return page('OpLev', 'OpLev builds the ultimate business engine, one that operates itself: a website built to convert, plus the engines that answer leads, follow up, run the day and bring customers back. Built around how you work, kept running by us, licensed monthly.',
                body, p='', home=True, active=None, mode=mode)


# ---------- pricing ----------

def access(n):
    status = {1: 'pick one', 2: 'pick two', 3: 'pick 3+'}[n]
    hint = {1: 'pick 1', 2: 'pick 2', 3: f'pick 3 or {NE}'}[n]
    meter = ''.join(f'<span class="seg{" on" if i < n else ""}"></span>' for i in range(NE))
    rows = ''.join(
        f'<li class="e-{k}"><span class="mk" aria-hidden="true"></span><span class="an">{E(name)}</span>'
        f'<span class="at">{E(triad)}</span><span class="as">{status}</span></li>'
        for k, name, _icon, triad, *_ in ENGINES)
    return f'''
        <div class="access" aria-label="Engine access: {n}{'+' if n == 3 else ''} of {NE}">
          <div class="access-hd"><span class="label">engines</span><span class="meter" aria-hidden="true">{meter}</span><span class="label">{hint}</span></div>
          <ul class="access-list">{rows}</ul>
        </div>'''


def fits(slug, p=''):
    xs = [x for x in ICPS if x['license'] == slug]
    if not xs:
        return ''
    more = f' / <a href="{p}for.html">and more</a>' if len(xs) > 4 else ''
    return '\n        <p class="label fits">common for: ' + ' / '.join(f'<a href="{p}for/{x["id"]}.html">{E(x["name"].lower())}</a>' for x in xs[:4]) + more + '</p>'


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
        <span class="label em-el">{elem(k)}{E(ELEMENT[k].lower())}</span>
        <h3 class="em-name">{E(name)}</h3>
        <p class="em-triad">{E(triad)}</p>
        <p class="em-line">{E(line)}</p>
        <ul class="em-caps">{''.join(f'<li>{E(x)}</li>' for x in caps)}</ul>
        <p class="label em-pl">tools we add often</p>
        <ul class="em-plays">{plays}</ul>
      </div>'''
    return f'''
    <div class="engmap-hd"><p class="eyebrow">What you get</p><h3 class="h3">What each engine does.</h3></div>
    <div class="engmap">{cols}
    </div>'''


def pricing():
    plans = (plan(1, 'one', 'One engine', '$5k', 'Start with the engine closest to your biggest bottleneck.',
                  ['Your website, designed and built to convert', 'Built around your business', 'Add industry tools any time',
                   'We host it, fix it and update it', 'A monthly progress score', 'A monthly check-in call',
                   'Email support, reply within a business day'],
                  'Apply for one engine')
             + plan(2, 'core', 'Two engines', '$10k', 'Two engines that feed each other, so nothing falls between them.',
                    ['Your website, designed and built to convert', 'Your two engines, working together', 'Tools that work across both', 'We interview your team',
                     'A monthly progress score', 'We host it, fix it and update it',
                     'A weekly check-in call', 'Same-day support'],
                    'Apply for two engines')
             + plan(3, 'company', 'Three or more', '$15k+', 'Three or all four engines, built around your whole business.',
                    ['Your website, designed and built to convert', 'Three or four engines, working together', 'Custom tools built for you',
                     'One place your team can look up how things are done', 'A progress score for every team',
                     'We host it, fix it and update it', 'Weekly calls and on-call support',
                     'Price depends on team size'],
                    'Apply for three or more'))
    lic = f'''
      <article class="lic lic-tools" aria-labelledby="tools-h">
        <div class="lic-l">
          <span class="label">add to any engine</span>
          <h3 class="h3" id="tools-h">Industry tools</h3>
          <p>Engines are the base. Tools are built for your kind of business and plug into one engine: a price calculator in Leads, treatment reminders in Agents, a route summary in Ops, a welcome series in Marketing. Add as many as you need.</p>
          <a class="label lic-more" href="for.html">See the tools for your industry {ARR_R}</a>
        </div>
        <div class="lic-r">
          <p class="price"><span class="amt">Per tool</span><span class="per">/ added monthly</span></p>
          <a class="btn" href="start.html">Ask about tools {ARR_R}</a>
        </div>
      </article>
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
    <h1 class="h1" id="h1">Your business engine. One monthly license.</h1>
    <p class="lede">We build the engine that runs your business on its own. Every plan starts with your website, designed to convert, plus one to all four engines. We host it, fix it and keep improving it. Want to sell what we build for you to other businesses? Add a resale license.</p>
    <div class="every model-row">
      <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Run it</h3><p>Your business engine, built and kept running by us.</p></div>
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
        <h2 class="h2" id="plans-h">Pick your engines. We build and run them.</h2>
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
        <p class="lede">Off-the-shelf apps make you work their way. A typical agency hands over the build and moves on. With us, you get engines made for you, kept running by the people who built them.</p>
      </div>
    </div>
    <div class="cmp" role="table" aria-label="Off-the-shelf apps, a typical agency and OpLev compared">
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
      <div class="actions"><a class="btn" href="start.html#resale">Ask about resale {ARR_R}</a><a class="btn ghost" href="marketplace.html">See the marketplace {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <div class="every one-col">
        <div class="ev"><span class="b" aria-hidden="true">01</span><h3 class="h3">Prove it</h3><p>Run it in your own business first. That's your proof it works.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">02</span><h3 class="h3">License it</h3><p>Add a resale license. We price it based on how you plan to sell.</p></div>
        <div class="ev"><span class="b" aria-hidden="true">03</span><h3 class="h3">Sell it</h3><p>Offer it to businesses like yours. We keep it running on our side.</p></div>
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
        <p class="a">A build you pay for once starts aging the day it ships. Someone has to host it, fix it and keep it current, and that usually means hiring a developer. With a monthly license, that's our job, and your engines keep getting better.</p>
      </details>
      <details>
        <summary><span class="h3">Who owns what you build?</span></summary>
        <p class="a">We do. You license it, and we host, maintain and improve it while you use it. Your business data stays yours.</p>
      </details>
      <details>
        <summary><span class="h3">Can we ask for changes?</span></summary>
        <p class="a">Yes. Changes and updates are included. We decide what to build next on your check-in calls.</p>
      </details>
      <details>
        <summary><span class="h3">What is a resale license?</span></summary>
        <p class="a">It lets you sell what we built for you to businesses like yours. Add it to any plan. We price it based on how you plan to sell.</p>
      </details>
      <details>
        <summary><span class="h3">Which engine should we start with?</span></summary>
        <p class="a">The one closest to your biggest bottleneck. If leads slip, Leads. If your team is buried in follow-up, Agents. If nobody else knows how things run, Ops. We will help you decide on the first call.</p>
      </details>
      <details>
        <summary><span class="h3">Where do we start?</span></summary>
        <p class="a">Apply. If it's a fit, we'll set up a short call, look at what still depends on you, and tell you where to start and which plan fits.</p>
      </details>
      <details>
        <summary><span class="h3">Why do we have to apply?</span></summary>
        <p class="a">We're a small team and only take on a few clients at a time, so every build gets our full attention. Applying tells us both if it's the right fit before anyone spends money.</p>
      </details>
      <details>
        <summary><span class="h3">What does the + on Three or more mean?</span></summary>
        <p class="a">It starts at $15k a month for three engines and goes up with the fourth engine, your team size and how much we build into each one. We quote it after our first call, so you know the number before you commit.</p>
      </details>
      <details>
        <summary><span class="h3">Is the website included?</span></summary>
        <p class="a">Yes. Every plan starts with your website: designed, built, hosted and kept fast by us. The engines run off it, so it's the first thing we build.</p>
      </details>
      <details>
        <summary><span class="h3">What's a tool?</span></summary>
        <p class="a">Something we add to an engine for your kind of business. A pool company adds a route-based price calculator to Leads. A med spa adds treatment reminders to Agents. A gym adds a free trial page to Marketing. Engines are the base, tools make them yours, and you can add them to any engine at any time.</p>
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
      <a class="btn" href="start.html">Apply {ARR_R}</a>
      <a class="btn ghost" href="work.html">See the work {ARR_R}</a>
    </div>
  </div>
</section>'''
    return page('OpLev Pricing', 'OpLev builds the business engine that operates itself and runs it for a monthly license: one engine from $5k a month, two for $10k, three or more from $15k. Add a resale license to sell them to others.',
                body, p='', active='pricing')


# ---------- start ----------

def start():
    return page('Apply | OpLev', 'Apply to work with OpLev. We take on a few clients at a time so every build gets our full attention.',
                inquiry('h1'), p='', active='contact')


# ---------- setups ----------

def access_for(keys):
    rows = ''.join(
        f'<li class="e-{k}{" inc" if k in keys else ""}"><span class="mk" aria-hidden="true"></span><span class="an">{E(name)}</span>'
        f'<span class="at">{E(triad)}</span><span class="as">{"included" if k in keys else "add any time"}</span></li>'
        for k, name, _i, triad, *_ in ENGINES)
    meter = ''.join(f'<span class="seg{" on" if i < len(keys) else ""}"></span>' for i in range(NE))
    return f'''<div class="access"><div class="access-hd"><span class="label">engines</span><span class="meter" aria-hidden="true">{meter}</span><span class="label">{len(keys)} of {NE}</span></div><ul class="access-list">{rows}</ul></div>'''


def for_index():
    blocks = ''
    for gi, g in enumerate(GROUPS):
        rows = ''.join(f'''
          <li><a href="for/{x['id']}.html"><span class="fr-name">{E(x['name'])}</span><span class="fr-h">{E(x['h1'])}</span>{etags(x['engines'])}<span class="fr-go">{ARR_R}</span></a></li>''' for x in icps_in(g['id']))
        blocks += f'''
    <section class="fgroup" id="{g['id']}" aria-labelledby="g-{g['id']}">
      <div class="fg-hd"><span class="label">{gi + 1:02d} / {len(icps_in(g['id']))} businesses</span><h2 class="fg-name" id="g-{g['id']}">{E(g['name'])}</h2><p>{E(g['line'])}</p></div>
      <ul class="frows">{rows}
      </ul>
    </section>'''
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><p class="eyebrow">Who it's for</p><span class="label">{len(ICPS):02d} kinds of business</span></div>
    <h1 class="h1" id="h1">Pick your business.</h1>
    <p class="lede">Every engine we build is custom. These are the businesses we build for most, with the tools we add to each engine for them. Yours starts from how you work.</p>
    {spots()}
  </div>
</section>

<div class="wrap fgroups">{blocks}
  <a class="fg-else" href="start.html"><span class="label">not on the list</span><span class="fg-else-t">Something else? Tell us how it works.</span><span class="fr-go">{ARR_R}</span></a>
</div>''' + cta('Tell us how yours works.', "Tell us what still runs through you. We'll show you what we'd build and where we'd start.", '')
    return page("Who It's For | OpLev", 'What OpLev builds for clinics, home services, product brands, agencies, firms, startups and creators. Every engine is custom.',
                body, p='', active='for')


def icp_page(x):
    p = '../'
    g = GROUP[x['group']]
    L = LICENSES[x['license']]
    k = x['id']
    acc = x['engines'][0]
    eng_names = ' + '.join(ENGINE_NAME[e] for e in x['engines'])
    demo = f'{p}app.html#{x["demo"]}' if x.get('demo') else None
    jobs = job_cards([tuple(j) for j in x['jobs']], sid=[k, x.get('sid')], p=p, extra_cls=' plays-top lp-jobs',
                     start='#start', demo=demo or f'{p}how-it-works.html')
    jobs_json = jobs[jobs.index('<script'):]
    pains = ''.join(f'\n        <li><q>{E(t)}</q><span class="label lp-by"><span class="bot bot-xs" data-bot="{e}"></span>fixed by {ENGINE_NAME[e]}</span></li>'
                    for t, e in x['pains'])
    day = json.dumps({'cmd': x['day_t'], 'run': x['day']}).replace('</', '<\\/')
    proof = ''
    if x.get('case') and x['case'] in BY_ID:
        c = BY_ID[x['case']]
        proof += f'<a class="lp-link" href="{case_href(c, p)}">{mini(c, SEED[c["id"]], p)}<span><span class="label">our work</span><b>{E(c["name"])}</b></span><span class="go">{ARR_R}</span></a>'
    if x.get('os') and x['os'] in MARKET_BY:
        o = MARKET_BY[x['os']]
        proof += f'<a class="lp-link" href="{p}marketplace/{o["id"]}.html"><span class="lp-ic" aria-hidden="true">{edots(o["engines"])}</span><span><span class="label">or start from</span><b>{E(o["name"])}</b></span><span class="go">{ARR_R}</span></a>'
    if demo:
        proof += f'<a class="lp-link" href="{demo}"><span class="lp-ic" aria-hidden="true">{edots(x["engines"])}</span><span><span class="label">example</span><b>See an example dashboard</b></span><span class="go">{ARR_R}</span></a>'
    proof = f'<div class="lp-links">{proof}</div>' if proof else ''
    tools = ''.join(f'<span class="tool">{E(t)}</span>' for t in x['tools'])
    T = tools_for(x)
    site_facing = lambda j: j is None or any(w in x['jobs'][j][1] for w in ('website', 'form', 'comes in', 'applies'))
    mk_page = [n for n, _l, _j in T['marketing'] if 'page' in n.lower() or 'signup' in n.lower()][:1]
    ag_in = [n for n, _l, j in T['agents'] if j is not None and any(w in x['jobs'][j][1] for w in ('comes in', 'form', 'DM', 'applies'))][:1]
    on_site = ([(n, 'leads') for n, _l, j in T['leads'] if site_facing(j)] + [(n, 'marketing') for n in mk_page]
               + [(n, 'agents') for n in ag_in])
    flow = ''.join(f'<li><span class="lf-n">{E(n)}</span><span class="lf-a" aria-hidden="true">{ARR_R}</span><span class="etag e-{e}">{E(ENGINE_NAME[e])}</span></li>' for n, e in on_site)
    domain = 'your' + x['biz'].replace(' ', '') + '.com'
    same = [y for y in icps_in(g['id']) if y['id'] != k]
    others = ''.join(f'<a href="{y["id"]}.html">{E(y["name"])}</a>' for y in same)
    body = f'''
<section class="top lp-hero" aria-labelledby="h1">
  <div class="wrap lp-in">
    <div class="lp-l">
      <div class="crumbs"><a class="label" href="{p}for.html">{ARR_L} Who it's for</a><a class="label" href="{p}for.html#{g['id']}">{E(g['name'])}</a></div>
      <p class="eyebrow">For {E(x['name'].lower())}</p>
      <h1 class="h1 lp-h1" id="h1">{E(x['h1'])}</h1>
      <p class="lede">{E(x['lede'])} It starts with your website.</p>
      <div class="actions"><a class="btn" href="#start">Apply for a spot {ARR_R}</a><a class="btn ghost" href="#tools">See the tools {ARR_D}</a></div>
      {spots(' lp-spots')}
    </div>
    <div class="lp-r">
      <div class="pane" data-src="lp-day" data-state="idle">
        <div class="pane-hd"><span class="sq"></span><span class="sq"></span><span class="sq"></span><span class="pane-title">{E(x['day_t'])}</span><span class="label">example</span></div>
        <div class="pane-bd"><div class="cmd"><span class="pr">$</span><span class="cmd-tx"></span><span class="caret" aria-hidden="true"></span></div><div class="rows"></div></div>
        <div class="pane-ft"><span class="dot" aria-hidden="true"></span><span class="label st">idle</span><button class="replay" type="button">Replay</button></div>
      </div>
      <script type="application/json" id="lp-day">{day}</script>
    </div>
  </div>
</section>

<section class="sec lp-pains e-{acc}" aria-labelledby="pains-h">
  <div class="wrap">
    <div class="lp-pains-hd"><p class="eyebrow">Sound familiar?</p><h2 class="sr" id="pains-h">Sound familiar?</h2><span class="label">what {E(x['name'].lower())} tell us</span></div>
    <ul class="lp-pains-list">{pains}
    </ul>
  </div>
</section>

<section class="sec lp-site" id="website" aria-labelledby="site-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">It starts with your website</p>
      <h2 class="h2" id="site-h">A website built for {E(x['name'].lower())}.</h2>
      <p class="lede">Fast, beautiful and built to convert. Every visitor gets a next step, and everything they send goes straight into your engines.</p>
    </div>
    <div class="split-r">
      {site_mock(domain, ' sm-sm')}
      <div class="lp-flow-w"><span class="label">on your site</span><ul class="lp-flow">{flow}</ul></div>
    </div>
  </div>
</section>

<section class="sec" id="tools" aria-labelledby="tools-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Tools for {E(x['name'].lower())}</p>
        <h2 class="h2" id="tools-h">What you can add to each engine.</h2>
        <p class="lede">Every engine takes tools built for {E(x['name'].lower())}. Start with the engines you need, then add tools as you grow. Tap any tool marked "see it run" to watch it work, step by step.</p>
      </div>
    </div>
    <div class="tboard" data-jobs="jobs-data">{tool_cols(x, run=True)}
    </div>
    {jobs_json}
  </div>
</section>

<section class="sec band" id="cost" aria-labelledby="cost-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">What it costs</p>
      <h2 class="h2" id="cost-h">Usually {E(eng_names)}. {E(L['price'])} a month.</h2>
      <p class="lede">That covers the engines, hosting, fixes and updates. Tools go on top, one at a time, so you only pay for the ones your {E(x['biz'])} uses.</p>
      <div class="actions"><a class="btn" href="#start">Apply {ARR_R}</a><a class="btn ghost" href="{p}pricing.html">See pricing {ARR_R}</a></div>
    </div>
    <div class="split-r">
      <dl class="lp-facts">
        <div><dt class="label">Best fit</dt><dd>{E(x['fit'])}</dd></div>
        <div><dt class="label">Works with</dt><dd class="tool-row">{tools}</dd></div>
      </dl>{proof}
    </div>
  </div>
</section>
''' + inquiry('h2', f"Apply for one of {CAPACITY['open']} spots.",
                f"Tell us how your {x['biz']} runs today and what still runs through you. If it's a fit, we'll set up a call.",
                preset=x['form'][0], other=x['form'][1], src=f"For {x['name'].lower()} page") + f'''
<nav class="lp-more" aria-label="More in {E(g['name'])}">
  <div class="wrap"><span class="label">also in {E(g['name'].lower())}</span>{others}<a href="{p}for.html">See all {len(ICPS)} {ARR_R}</a></div>
</nav>'''
    return page(f'OpLev for {x["name"]}', f'{x["h1"]} {x["lede"]}', body, p=p, active='for')


def redirect(to, title):
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>{E(title)}</title>\n'
            f'<meta name="robots" content="noindex">\n<link rel="canonical" href="{to}">\n'
            f'<meta http-equiv="refresh" content="0; url={to}">\n</head>\n<body>\n<p><a href="{to}">{E(title)}</a></p>\n</body>\n</html>\n')


# ---------- marketplace ----------

def os_jobs(x):
    """Job tuples (engine, trigger, title, desc) for an OS, taken from its setup or the shared list."""
    pools = ([tuple(u) for u in SETUP[x['sid']]['uses']] if x.get('sid') else []) + list(PLAYS) + [
        tuple(u) for s in SETUPS for u in s['uses']]
    out = []
    for t in x['jobs']:
        hit = next((j for j in pools if j[2] == t), None)
        assert hit, f'no job named {t} for {x["id"]}'
        out.append(hit)
    return out


def os_card(x, p=''):
    i = MARKET.index(x)
    jobs = ''.join(f'<li>{E(t)}</li>' for t in x['jobs'][:3])
    fig = (f'<figure class="thumb" role="img" aria-label="Placeholder image for {E(x["name"])}"><canvas data-seed="{21 + i}"></canvas>{TICKS}'
           f'<span class="tag tl label">os {i + 1:02d}</span><span class="tag br label">example listing</span></figure>')
    return f'''
      <a class="card os-card" href="{p}marketplace/{x['id']}.html" data-e="{x['type']}">
        {fig}
        <div class="card-b">
          <div class="card-top"><span class="label">{E(x['type_label'])}</span>{etags(x['engines'])}</div>
          <h2 class="h3 card-name">{E(x['name'])}</h2>
          <p class="card-line">{E(x['pitch'])}</p>
          <ul class="rowlist">{jobs}</ul>
          <div class="card-foot"><span class="label">price on request</span><span class="label go">View {ARR_R}</span></div>
        </div>
      </a>'''


LICENSE_STEPS = [
    ('Pick one', 'Find an OS built for a business like yours, and see every tool in it.'),
    ('We tailor it', 'We connect it to your tools and set it up with your wording, your prices and your rules.'),
    ('We run it', 'You pay monthly. We host it, fix it and keep it improving. The owner earns on every license.'),
]


SELL_STEPS = [
    ('We build it for you', 'Custom engines, built around how your business runs.'),
    ('It proves itself', "It runs your business first. That's the proof buyers want."),
    ('We list it', 'Your OS goes in the marketplace. We tailor and run it for every buyer.'),
    ('You earn', 'Every business that licenses it pays you, every month.'),
]


def sell_steps():
    return '<div class="every one-col">' + ''.join(
        f'<div class="ev"><span class="b" aria-hidden="true">{i + 1:02d}</span><h3 class="h3">{E(t)}</h3><p>{E(d)}</p></div>'
        for i, (t, d) in enumerate(SELL_STEPS)) + '</div>'


def license_steps(cls=''):
    return f'''<ol class="steps steps-3{cls}">''' + ''.join(
        f'''<li class="step"><div class="step-top"><span class="num" aria-hidden="true">{i + 1:02d}</span></div><h3 class="h3">{E(t)}</h3><p>{E(d)}</p></li>'''
        for i, (t, d) in enumerate(LICENSE_STEPS)) + '</ol>'


def market_index():
    filters = '<button class="tab" type="button" aria-pressed="true" data-f="all">All</button>' + ''.join(
        f'<button class="tab" type="button" aria-pressed="false" data-f="{k}">{E(t)}</button>' for k, t in MARKET_TYPES)
    cards = ''.join(os_card(x) for x in MARKET)
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><p class="eyebrow">Marketplace</p><span class="label">{len(MARKET):02d} example listings</span></div>
    <h1 class="h1" id="h1">Operating systems, ready to license.</h1>
    <p class="lede">Each OS here is a set of engines and industry tools, built by OpLev for a business like yours, then listed by its owner. Pick one, apply, and we tailor it to you and run it every month. Faster than starting from scratch.</p>
    <p class="label mk-note">These are example listings while the first ones go live.</p>
    <div class="tabs filters mk-filters" role="group" aria-label="Filter by business">{filters}</div>
    <div class="cards mk-cards">{cards}
    </div>
  </div>
</section>

<section class="sec band" id="licensing" aria-labelledby="lic-steps-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How licensing works</p>
        <h2 class="h2" id="lic-steps-h">Proven in one business. Tailored for yours.</h2>
      </div>
    </div>
    {license_steps()}
  </div>
</section>

<section class="sec" id="sell" aria-labelledby="sell-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Sell yours</p>
      <h2 class="h2" id="sell-h">Built something that works? List it.</h2>
      <p class="lede">What works for your business will work for businesses like yours. Add a resale license and we list your OS here, run it for every buyer, and you earn on every license.</p>
      <div class="actions"><a class="btn" href="start.html#resale">Ask about resale {ARR_R}</a><a class="btn ghost" href="pricing.html#resale">How resale works {ARR_R}</a></div>
    </div>
    <div class="split-r">
      {sell_steps()}
    </div>
  </div>
</section>''' + cta("Don't see your business?", "We'll build an OS around how yours works. Tell us what still runs through you.", '')
    return page('OS Marketplace | OpLev', 'Operating systems OpLev built for real kinds of business, ready to license. Pick one, we tailor it to you and run it every month.',
                body, p='', active='market')


def market_page(i):
    x = MARKET[i]
    p = '../'
    n = len(MARKET)
    start = f'{p}start.html#os-{x["id"]}'
    demo = f'{p}app.html#{x["sid"]}' if x.get('sid') else None
    jobs = job_cards(os_jobs(x), sid=x.get('sid'), p=p, extra_cls=' plays-top', start=start, demo=demo or f'{p}marketplace.html')
    more = ''.join(os_card(MARKET[(i + k) % n], p) for k in (1, 2, 3))
    acts = f'<a class="btn" href="{start}">Apply for this OS {ARR_R}</a>' + (
        f'<a class="btn ghost" href="{demo}">See an example dashboard {ARR_R}</a>' if demo else '')
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <div class="crumbs"><a class="label" href="{p}marketplace.html">{ARR_L} Marketplace</a><span class="label">os {i + 1:02d} / {n:02d} / example listing</span></div>
    <p class="eyebrow">Operating system for {E(x['type_label'].lower())}</p>
    <h1 class="h1" id="h1">{E(x['name'])}</h1>
    <p class="lede">{E(x['pitch'])}</p>
    <dl class="facts f4">
      <div><dt class="label">For</dt><dd>{E(x['for'])}</dd></div>
      <div><dt class="label">Engines</dt><dd>{etags(x['engines'])}</dd></div>
      <div><dt class="label">Built for</dt><dd>{E(x['built_for'])}</dd></div>
      <div><dt class="label">Price</dt><dd>Monthly license, on request</dd></div>
    </dl>
    <div class="actions">{acts}</div>
  </div>
</section>

<section class="sec" id="inside" aria-labelledby="inside-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">What's inside</p>
        <h2 class="h2" id="inside-h">The tools it comes with.</h2>
        <p class="lede">Tap any tool to see what happens, step by step. We tailor each one to how you work before it goes live.</p>
      </div>
      <p class="label">{len(x['jobs'])} tools</p>
    </div>
    {jobs}
  </div>
</section>

<section class="sec band" id="licensing" aria-labelledby="lic-steps-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">How licensing works</p>
        <h2 class="h2" id="lic-steps-h">Proven in one business. Tailored for yours.</h2>
      </div>
    </div>
    {license_steps()}
  </div>
</section>

<section class="sec" id="more" aria-labelledby="more-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">More in the marketplace</p>
        <h2 class="h2" id="more-h">Other operating systems.</h2>
      </div>
      <a class="btn ghost" href="{p}marketplace.html">See all {ARR_R}</a>
    </div>
    <div class="cards">{more}
    </div>
  </div>
</section>''' + cta(f'Want {E(x["name"])}?', 'Tell us about your business. We will show you how we would tailor it and what it costs.', p)
    return page(f'{x["name"]} | OpLev Marketplace', f'{x["name"]}: {x["pitch"]}', body, p=p, active='market')


# ---------- how it works ----------

PHASES = [
    ('system', 'Apply', 'We only take on a few clients at a time. Tell us about your business and what still runs through you. If it looks like a fit, we set up a call.',
     'Fill in a two-minute application.', 'A reply from the people who would build it.'),
    ('discuss', 'Discuss', 'We get on a call with you and your team and see how the work really gets done: where leads come in, what you answer twice, what only one person knows.',
     'Walk us through a normal week.', 'A plan with what we would build first, the monthly price and a launch date.'),
    ('build', 'Build', 'We design your website first, then build your engines around it and around how you already work, connected to the tools you use, like your calendar, inbox and payments.',
     'Answer our questions and try it early.', 'Engines built for your business, tested on your real work.'),
    ('implement', 'Launch', 'We roll it out one piece at a time. Every tool checks with you first until you trust it, then it runs on its own.',
     'Approve drafts from your phone.', 'Busywork off your plate. Nothing important goes out without your OK.'),
    ('measure', 'Improve', 'Every month we track how much of the business runs without you, then pick the next thing to fix.',
     'Join a short check-in call.', 'Engines that keep getting better for as long as you use them.'),
]
DUO = [
    ('You', ['Tell us how the business runs', 'Approve anything important', 'Tell us what to change', 'Keep your data, always']),
    ('Us', ['Design and build your engines', 'Connect the tools you already use', 'Host, fix and update everything', 'Keep improving it every month']),
]
MONTHLY = [
    ('Hosting, fixes and updates', 'We keep it running. You never hire a developer.'),
    ('Changes when you ask', 'New tools, new rules, new wording. We build them in.'),
    ('A progress score', 'A simple number for how much runs without you.'),
    ('Check-in calls', 'We review what is working and pick what to fix next.'),
    ('Approvals your way', 'You decide what needs your OK and what runs on its own.'),
    ('Your data stays yours', 'Download all of it any time.'),
]


def how_page():
    phases = ''.join(f'''
      <li class="phase">
        <div class="phase-id"><span class="num" aria-hidden="true">{i + 1:02d}</span><svg class="px" data-icon="{icon}" viewBox="0 0 50 50" aria-hidden="true"></svg><h3 class="h3">{E(t)}</h3></div>
        <p class="phase-d">{E(d)}</p>
        <dl class="phase-kv"><div><dt class="label">you</dt><dd>{E(you)}</dd></div><div><dt class="label">you get</dt><dd>{E(get)}</dd></div></dl>
      </li>''' for i, (icon, t, d, you, get) in enumerate(PHASES))
    duo = ''.join(f'''
      <div class="duo-col"><p class="label">{E(who)}</p><ul class="rowlist">{''.join(f'<li>{E(x)}</li>' for x in items)}</ul></div>''' for who, items in DUO)
    monthly = ''.join(f'<div class="ev"><span class="b" aria-hidden="true">{i + 1:02d}</span><h3 class="h3">{E(t)}</h3><p>{E(d)}</p></div>'
                      for i, (t, d) in enumerate(MONTHLY))
    body = f'''
<section class="top" aria-labelledby="h1">
  <div class="wrap">
    <p class="eyebrow">How it works</p>
    <h1 class="h1" id="h1">From first call to a business that runs itself.</h1>
    <p class="lede">We learn how your business runs, build the engine around it and keep it running every month. You talk to the people building it, the whole way.</p>
    <dl class="facts f4">
      <div><dt class="label">You talk to</dt><dd>The people building it</dd></div>
      <div><dt class="label">You pay</dt><dd>One monthly price</dd></div>
      <div><dt class="label">You approve</dt><dd>Anything important</dd></div>
      <div><dt class="label">You keep</dt><dd>Your data, always</dd></div>
    </dl>
  </div>
</section>

<section class="sec" id="process" aria-labelledby="process-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">The process</p>
        <h2 class="h2" id="process-h">Five steps.</h2>
      </div>
      <p class="label">apply / discuss / build / launch / improve</p>
    </div>
    <ol class="phases">{phases}
    </ol>
  </div>
</section>

<section class="sec" id="roles" aria-labelledby="roles-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Who does what</p>
      <h2 class="h2" id="roles-h">You run the business. We run the engines.</h2>
      <p class="lede">Your part takes a few calls and a few taps a day. The rest is on us.</p>
    </div>
    <div class="split-r"><div class="duo">{duo}
    </div></div>
  </div>
</section>

<section class="sec band" id="engines" aria-labelledby="eng-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">What we build</p>
        <h2 class="h2" id="eng-h">Four engines. Four elements.</h2>
        <p class="lede">We build one or all four, then add tools made for your industry. They share the same information, so nothing gets typed in twice.</p>
      </div>
    </div>{engmap()}
  </div>
</section>

<section class="sec" id="monthly" aria-labelledby="monthly-h">
  <div class="wrap">
    <div class="head">
      <div class="head-l">
        <p class="eyebrow">Every month</p>
        <h2 class="h2" id="monthly-h">What your monthly price covers.</h2>
      </div>
      <a class="btn ghost" href="pricing.html">See pricing {ARR_R}</a>
    </div>
    <div class="every">{monthly}
    </div>
  </div>
</section>

<section class="sec" id="resale" aria-labelledby="resale-h">
  <div class="wrap split">
    <div class="head-l">
      <p class="eyebrow">Then sell it</p>
      <h2 class="h2" id="resale-h">Your OS can earn.</h2>
      <p class="lede">What works for you will work for businesses like yours. List it in our marketplace and earn on every license. We run it for every buyer.</p>
      <div class="actions"><a class="btn" href="marketplace.html">Browse the marketplace {ARR_R}</a></div>
    </div>
    <div class="split-r">{sell_steps()}</div>
  </div>
</section>''' + inquiry('h2', 'Ready when you are.')
    return page('How It Works | OpLev', 'How OpLev works: we learn how your business runs, build the engine around it and keep it running every month.',
                body, p='', active='how')


# ---------- console app ----------

def app_page():
    data = {'engines': [{'id': k, 'name': n, 'triad': t, 'line': l, 'caps': c} for k, n, _i, t, l, c, _s in ENGINES],
            'plays': PLAYS, 'setups': SETUPS, 'licenses': LICENSES, 'jobs': JOBS}
    blob = json.dumps(data).replace('</', '<\\/')
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<title>Example Dashboard | OpLev</title>\n'
            '<meta name="description" content="An example of the dashboard OpLev builds into every engine, shown for a made-up business with sample data.">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<style>\n{CSS}\n{APP_CSS}</style>\n</head>\n<body>\n'
            '<div id="app" class="app"><noscript><p style="padding:24px">This example needs JavaScript.</p></noscript></div>\n'
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
    <h1 class="h1" id="h1">What we've built.</h1>
    <p class="lede">Custom engines and tools we've built for founders and small teams. Each one shows the problem, what we built and how it works day to day.</p>
    <div class="cards">{cards}
    </div>
  </div>
</section>''' + cta('Want one of these running for you?',
                    'Tell us what still runs through you. We will show you where we would start.', '')
    return page('OpLev Work', 'Case studies: custom engines, work agents and lead tools OpLev has built for founders and small teams.',
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
    <h1 class="h1" id="h1">{E(c['name'])}</h1>
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
           'for.html': for_index(), 'app.html': app_page(), 'setups.html': redirect('for.html', "Who it's for"),
           'how-it-works.html': how_page(), 'marketplace.html': market_index()}
    for i, x in enumerate(MARKET):
        out[f'marketplace/{x["id"]}.html'] = market_page(i)
    for x in ICPS:
        out[f'for/{x["id"]}.html'] = icp_page(x)
    for x in SETUPS:
        out[f'setups/{x["id"]}.html'] = redirect(f'../for.html#{SETUP_GROUP[x["id"]]}', "Who it's for")
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
