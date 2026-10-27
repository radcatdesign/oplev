# OpLev site

Static site. Every page is a self-contained HTML file, so Vercel serves the repo as is (preset: Other, no build command).

## Edit

- Case studies: `content/cases.json`
- Who it's for: `content/icps.json`. Each business type gets a landing page at `for/<id>.html`, a spot in the "Who it's for" mega menu, the home page list and the pricing "common for" lines. Groups set the menu columns.
- Industry tools: the add-ons that plug into each engine. Each business type in `content/icps.json` lists its tools: `jobs` (tools with a step-by-step walkthrough in `jobs.json`) plus `extra` (more tools per engine, name and one line). They show on the home page tool picker, each landing page and the pricing page.
- Example dashboard sample data: `content/setups.json`
- Job walkthroughs (what happens when a job runs): `content/jobs.json`, keyed by job title. Use `id:Title` for a version specific to one business type (a landing page id from `icps.json`, or a setup id).
- Marketplace listings: `content/marketplace.json` (currently example listings)
- Client spots shown across the site: `CAPACITY` at the top of `build.py`. Keep it set to your real numbers.
- Console: `src/app.css`, `src/app.js`
- Styles: `src/site.css`
- Behavior: `src/site.js`
- Page copy and layout: `build.py`

Then rebuild and commit the output:

```
python3 build.py
```

This writes `index.html`, `how-it-works.html`, `pricing.html`, `work.html`, `start.html`, `for.html`, `for/<business>.html`, `marketplace.html`, `marketplace/<os>.html`, `app.html` and `work/<case>.html`.

## Case images

Put an image in `img/` and set `"img": "img/adessa-mind.jpg"` on that case. It replaces the generated placeholder everywhere the case appears.

## Optional case fields

`facts`, `stack`, `note`, `count`, `before_title`, `before_label`, `results_title`, `results_label`. Leave `results` empty to show "result to add" slots.

## Inquiry form

The form on the home page and `/start` posts to `api/inquiry.js`, a Vercel function that emails each inquiry through Resend. Add these in Vercel, under Settings, Environment Variables, then redeploy:

- `RESEND_API_KEY`: your Resend API key
- `INQUIRY_TO`: where inquiries go, comma-separated for more than one
- `INQUIRY_FROM`: optional sender like `OpLev <site@yourdomain.com>` (the domain must be verified in Resend)

Until those are set, the form shows the visitor a ready-to-copy note and the email address instead.

Links can preselect answers: `start.html#os-practice` marks the application as about that marketplace OS; `start.html#clinic`, `#field`, `#brand`, `#agency`, `#creator`, `#startup` set the business type; `#one`, `#core`, `#company` set the plan; `#resale` sets resale to yes.

`.vercelignore` keeps `build.py`, `src/`, `content/` and this README off the live site.

## Example dashboard (`/app`)

`app.html` is an example of the dashboard OpLev builds for a client, shown for a made-up business with sample data: home, needs your OK, activity, engine pages, automations, inquiries, records, progress score and settings. Changes stay in the visitor's browser.

Open it as a business type with `app.html#clinic`, `#brand`, `#agency`, `#creator` or `#startup`. Landing pages with a `demo` set in `icps.json` link to their example.

`content/setups.json` holds the example dashboard's sample businesses. The old `setups.html` and `setups/<type>.html` addresses redirect to `/for` (see `vercel.json`).

## The characters

There are four engines, each with an element and a tile character: Ops is water (the organizer), Agents is earth (the helpers), Leads is fire (the go-getter) and Marketing is wind (the messenger). Engines, elements and element icons live in `ENGINES`, `ELEMENT` and `ELEM_TILES` in `build.py`. Their sprites and lines live in `BOTS` and `BOT_LINES` at the top of `src/site.js`, their one-line bios in `BOT_ROLE` in `build.py`. They show up on the home page engine strips and next to their names in every activity log.

## Footer wordmark

The OPLEV wordmark is drawn as tiles taken from Doto's own capitals (`GLYPHS` in `build.py`), so each tile can blink to an engine color on hover.
