# OpLev site

Static site. Every page is a self-contained HTML file, so Vercel serves the repo as is (preset: Other, no build command).

## Edit

- Case studies: `content/cases.json`
- Styles: `src/site.css`
- Behavior: `src/site.js`
- Page copy and layout: `build.py`

Then rebuild and commit the output:

```
python3 build.py
```

This writes `index.html`, `pricing.html`, `work.html`, `start.html` and `work/<case>.html`.

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

Links can preselect answers: `start.html#clinic`, `#brand`, `#agency`, `#creator`, `#startup` set the business type; `#one`, `#core`, `#company` set the license; `#resale` sets resale to yes.

`.vercelignore` keeps `build.py`, `src/`, `content/` and this README off the live site.
