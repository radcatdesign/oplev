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

This writes `index.html`, `pricing.html`, `work.html` and `work/<case>.html`.

## Case images

Put an image in `img/` and set `"img": "img/adessa-mind.jpg"` on that case. It replaces the generated placeholder everywhere the case appears.

## Optional case fields

`stack`, `note`, `count`, `before_title`, `before_label`, `results_title`, `results_label`. Leave `results` empty to show "result to add" slots.
