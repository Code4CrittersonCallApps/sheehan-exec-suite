"""v2.9.28: patch live dunk-list.html in place (keeps v2926/v2927 layout + sent/collapsed states).
Adds Stead Spin (Farm Spin giving wheel) CTA per segment + goat yoga mentions. Mailto only; sends nothing."""
import re, json, urllib.parse as up, pathlib
P = pathlib.Path(__file__).resolve().parents[1]
H = P/"dunk-list.html"
WHEEL = "https://code4crittersoncallapps.github.io/critters-on-call/giving-wheel/"
BANNED = ["lina ", "lisa licata", "georgia hamilton", "jessica morgan"]
html = H.read_text()
cut = html.find("<details")
head, tail = (html[:cut], html[cut:]) if cut > 0 else (html, "")

def bucket(seg):
    s = seg.split("·")[0].strip().lower()
    if s in ("inbound", "owed"): return "customer"
    if s in ("media", "festival", "chain", "planner"): return "partner"
    if s in ("employer", "hoa/cdd", "school", "senior"): return "prospect"
    return None

YOGA = {"employer": "Goat yoga is a big hit for team days too.",
        "hoa/cdd": "We also do goat yoga, which residents love.",
        "planner": "We also offer goat yoga as an add-on.",
        "festival": "We can add goat yoga sessions as well.",
        "inbound": "", "owed": "We also do goat yoga if that's ever a fit."}
PS = {"customer": "P.S. We have a free Stead Spin giving wheel running this October. Spin for a farm prize (a Gold membership is the top one), no purchase needed: " + WHEEL,
      "prospect": "P.S. Want a taste first? Anyone on your team or in your community can take a free spin on our October giving wheel for a farm prize: " + WHEEL,
      "partner": "P.S. If it's useful for your audience, our free October Stead Spin giving wheel is easy to share, and we're happy to co-promote: " + WHEEL}
stats = {"customer": 0, "prospect": 0, "partner": 0, "yoga": 0, "skipped": 0}
samples = {}
def fix(m):
    art = m.group(0)
    sm = re.search(r'class="seg">([^<]*)', art)
    b = bucket(sm.group(1)) if sm else None
    bm = re.search(r'(body=)([^"]*)', art)
    if not b or not bm or WHEEL in art:
        stats["skipped"] += 1; return art
    body = up.unquote(bm.group(2).replace("&amp;", "&"))
    key = sm.group(1).split("·")[0].strip().lower()
    y = YOGA.get(key, "")
    add = ""
    if y and "goat yoga" not in body.lower():
        add += y + "\n\n"; stats["yoga"] += 1
    add += PS[b] + "\n"
    body = body.rstrip() + "\n\n" + add
    stats[b] += 1
    samples.setdefault(b, body)
    enc = up.quote(body, safe="/")
    art = art[:bm.start(2)] + enc + art[bm.end(2):]
    return art.replace('<div class="sm">', '<div class="sm"><a class="mini" href="%s">Stead Spin</a> ' % WHEEL, 1)
head = re.sub(r'<article class="q".*?</article>', fix, head, flags=re.S)
html = head + tail
low = html.lower()
assert not any(n in low for n in BANNED[1:]), "banned contact present"
html = html.replace("principal-dunk.html?v=2927", "principal-dunk.html?v=2928")
html = re.sub(r'<span class="ver">[^<]*</span>', '<span class="ver">Board v2.9.28 · Oct 10, 2026 · Stead Spin giving wheel in every mailto + goat yoga · ?v=2928</span>', html, count=1)
SPIN = ('<div class="card top" id="spin"><h3>🎡 Spin the wheel — Stead Spin (October giving wheel)</h3>'
        '<div class="meta">Free farm-prize spin, Gold membership is the top prize, closes Oct 31. Every waiting mailto below now ends with a segment P.S. linking it (customers: spin for a prize · prospects: taste first · partners: share/co-promote).</div>'
        '<div class="links"><a class="btn" href="%s" target="_blank" rel="noopener">Spin the wheel</a></div></div>\n' % WHEEL)
html = html.replace('<div class="strip">', SPIN + '<div class="strip">', 1)
H.write_text(html)
waiting = int(re.search(r'<div class="w"><b>(\d+)</b>', html).group(1))
json.dump({"board_version": "Board v2.9.28 · Oct 10, 2026 · Stead Spin in mailtos + goat yoga", "hard_refresh": "?v=2928",
           "no_outbound_send": True, "compose_only": True, "wheel": WHEEL, "waiting": waiting, "patched": stats, "samples": samples},
          open(P/"data/_dunk_v2928_summary.json", "w"), indent=2, ensure_ascii=False)
print(stats, waiting); [print("==", k, "\n" + v) for k, v in samples.items()]
