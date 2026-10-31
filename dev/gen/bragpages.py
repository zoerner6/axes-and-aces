import json,html
O='/tmp/claude-0/-home-user/8da1ae95-9ac9-5639-830a-e1825fc256be/scratchpad/'
L=json.load(open('/tmp/claude-0/og.json')); SITE='https://axesandaces.com/'
for o in L:
    t=html.escape(o['title']); d=html.escape(o['sub'])
    open(O+f"site/b/{o['key']}.html",'w').write(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{t} · Axes &amp; Aces</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:type" content="website"><meta property="og:site_name" content="Axes &amp; Aces">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d} Play free in your browser.">
<meta property="og:image" content="{SITE}b/{o['key']}.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{SITE}b/{o['key']}.html"><meta name="twitter:card" content="summary_large_image"><link rel="canonical" href="{SITE}">
<script>location.replace("{SITE}"+(location.search||"?")+(location.search?"&":"")+"ref={o['key']}");</script>
<noscript><meta http-equiv="refresh" content="0;url={SITE}?ref={o['key']}"></noscript>
<style>body{{background:#14100d;color:#f3e6c8;font:18px system-ui;display:grid;place-items:center;min-height:100vh;margin:0}}a{{color:#f2b632}}</style></head>
<body><p>Loading <a href="{SITE}">Axes &amp; Aces</a>...</p></body></html>''')
print(len(L))
