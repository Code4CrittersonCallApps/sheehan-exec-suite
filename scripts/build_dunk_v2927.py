#!/usr/bin/env python3
"""dunk v2.9.26 — phone work queue. Sent catch-up + org-touched. Mailto only. Never auto-send.

Input: the v2.9.25 dunk-list.html (git show b415f60:dunk-list.html) and board JSON.
"""
from __future__ import annotations

import html as H
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_dunk_v2925 as v25  # noqa: E402

ROOT = Path("/workspace/sheehan-exec-suite")
CRIT = Path("/workspace/critters-on-call/exec")
BOARD = ROOT / "data" / "principal_dunk_board.json"
SRC_REV = "b415f60"
HARD = "?v=2926"
AS_OF = "2026-10-04 11:55 PM ET"
BOARD_VER = "Board v2.9.26 · Oct 4, 2026 late ET · Sent catch-up + org-touched + phone work queue (mailto only, never auto-send)"

# New this pass (Gmail in:sent, sheehanhomestead@gmail.com). Times ET.
SENT_NEW = {
    "firstcoastconnect@wjct.org": ("Oct 4, 2026 10:25 PM ET", "Social Shout Out for Local Edutainment/Agritourism Biz?"),
    "news@firstcoastnews.com": ("Oct 4, 2026 10:25 PM ET", "Social Shout Out for Local Edutainment/Agritourism Biz?"),
    "team@folioweekly.com": ("Oct 4, 2026 10:26 PM ET", "Social Shout Out for Local Edutainment/Agritourism Biz?"),
    # card primary is newstips@wjxt.com; Michael sent to the news4jax alias
    "newstips@wjxt.com": ("Oct 4, 2026 10:24 PM ET", "Social Shout Out for Local Eduatainment/Agritourism Biz? (sent to newstips@news4jax.com)"),
    "karin@fruitcove.com": ("Sep 28, 2026 3:57 PM ET", "Forward to Karin on the info@fruitcove.com thread"),
}
SENT = dict(v25.SENT)
SENT.update(SENT_NEW)

# domain -> (address sent, ET time). Gmail in:sent after:2026/09/04.
TOUCHED = {
    "actionnewsjax.com": ("news@actionnewsjax.com", "Sep 30 9:50 AM ET"),
    "agingtrue.org": ("adultdaycare@agingtrue.org", "Oct 4 8:42 PM ET"),
    "aipca.net": ("kbean@aipca.net", "Oct 2 4:25 PM ET"),
    "ascension.org": ("amber.johnson1@ascension.org", "Sep 22 5:51 PM ET"),
    "duvalschools.org": ("brownj5@duvalschools.org", "Sep 29 9:27 AM ET"),
    "coasjc.org": ("caregiving@coasjc.org", "Sep 25 3:51 PM ET"),
    "cimarronegolf.com": ("rshoemaker@cimarronegolf.com", "Sep 25 3:50 PM ET"),
    "cmcjaxfla.com": ("hiddenhills@cmcjaxfla.com", "Sep 24 8:00 AM ET"),
    "firstcoastcms.com": ("service@firstcoastcms.com", "Sep 30 9:22 PM ET"),
    "gmsnf.com": ("ameliawalkmanager@gmsnf.com", "Sep 25 3:21 PM ET"),
    "fsresidential.com": ("kate.trivelpiece@fsresidential.com", "Oct 2 5:44 PM ET"),
    "goddardschools.com": ("cathy.hemphill@goddardschools.com", "Sep 23 7:10 PM ET"),
    "golfclubofamelia.com": ("sregan@golfclubofamelia.com", "Sep 14 5:53 PM ET"),
    "jaxport.com": ("hr@jaxport.com", "Sep 28 10:37 AM ET"),
    "greystar.com": ("risenocatee@greystar.com", "Sep 25 3:47 PM ET"),
    "maymgt.com": ("jsapere@maymgt.com", "Sep 25 3:35 PM ET"),
    "publix.com": ("jacksonvillecr@publix.com", "Sep 30 9:22 PM ET"),
    "rizzetta.com": ("hoavendors@rizzetta.com", "Sep 29 9:41 AM ET"),
    "patriotrail.com": ("josie.curtis@patriotrail.com", "Sep 28 10:37 AM ET"),
    "oakleafresidents.com": ("venuerentals@oakleafresidents.com", "Sep 25 3:37 PM ET"),
    "sjcds.net": ("rtrevett@sjcds.net", "Oct 4 8:39 PM ET"),
    "tlechildcare.com": ("rivercity@tlechildcare.com", "Oct 2 2:36 PM ET"),
    "stjohns.k12.fl.us": ("donny.hoessler@stjohns.k12.fl.us", "Sep 29 9:27 AM ET"),
    "sjrstate.edu": ("angelabrown@sjrstate.edu", "Sep 24 8:00 AM ET"),
    "wjxt.com": ("ekendall@wjxt.com", "Oct 4 10:26 PM ET"),
    "news4jax.com": ("newstips@news4jax.com", "Oct 4 10:24 PM ET"),
    "wjct.org": ("firstcoastconnect@wjct.org", "Oct 4 10:25 PM ET"),
    "firstcoastnews.com": ("news@firstcoastnews.com", "Oct 4 10:25 PM ET"),
    "folioweekly.com": ("team@folioweekly.com", "Oct 4 10:26 PM ET"),
    "vestapropertyservices.com": ("mczmyr@vestapropertyservices.com", "Oct 4 9:02 PM ET"),
}
GENERIC = {"gmail.com", "yahoo.com", "aol.com", "bellsouth.net", "hotmail.com", "outlook.com", "icloud.com", "comcast.net"}
BANNED_TEXT = ("lisa licata", "llicata", "llicatta", "georgia hamilton", "ghamilton", "jessica morgan", "jmorgan@jaxgcc",
               "lihernandez", "lina hernandez", "lina lihernandez", "wynnfieldlakesmanager")

SENT_TODAY = 18  # Gmail in:sent after Oct 4 12:00 AM ET (messages)
OUT_DOMAINS = ("ucf.edu", "fgcu.edu", "nova.edu", "ufl.edu", "fsu.edu", "usf.edu")

SEG_LABEL = {"open": "Owed", "owed": "Owed", "catchall": "Chain", "media": "Media", "schools": "School",
             "senior": "Senior", "hoa": "HOA/CDD", "corporate": "Employer", "festivals": "Festival",
             "planners": "Planner"}
SEG_ORDER = ["media", "schools", "hoa", "senior", "corporate", "festivals", "planners"]


def esc(s):
    return H.escape(s or "", quote=True)


def strip_tags(s):
    t = H.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()
    t = re.sub(r"\s+([.,;:!?)])", r"\1", t)
    return re.sub(r"\(\s+", "(", t)


PHONE_RE = re.compile(r"(\(?\d{3}\)?[-. ]?\d{3}[-. ]\d{4})(\s*x\s?\d+)?")


def tel_of(s):
    m = PHONE_RE.search(s or "")
    if not m:
        return "", ""
    disp = m.group(0).strip()
    digits = re.sub(r"\D", "", m.group(1))
    ext = re.sub(r"\D", "", m.group(2) or "")
    href = "tel:+1" + digits + (";ext=" + ext if ext else "")
    return disp, href


FILLER = {"corporate hq", "field district", "headquarters inbox", "corporate hq (route to family day)",
          "schools/vpk/daycare", "senior", "hoa/cdd", "amenity", "cdd", "hoa", "enterprise", "college", "university"}
BOILER = ("waiting homestead send", "net-new", "compose only", "tap mailto", "never sent", "dedup", "mailto only",
          "not in gmail sent")


def clean_meta(meta_html, email, phone_disp):
    parts = [strip_tags(p) for p in re.split(r"\s·\s", meta_html)]
    out, seen = [], set()
    for p in parts:
        pl = p.lower().strip()
        if not pl or pl == email.lower() or (phone_disp and phone_disp in p):
            continue
        if pl in FILLER or pl in seen:
            continue
        seen.add(pl)
        out.append(p)
    return " · ".join(out[:2])


def short_note(why_htmls):
    for w in why_htmls:
        t = strip_tags(w)
        tl = t.lower()
        if not t or "already sent" in tl and "no mailto" in tl:
            continue
        if any(b in tl[:40] for b in BOILER):
            continue
        t = re.sub(r"^(status:)\s*", "", t, flags=re.I)
        m = re.match(r"(.+?[.!?])(\s|$)", t)
        s = m.group(1) if m else t
        if m and len(s) < 30:
            m2 = re.match(r"(.+?[.!?])(\s|$)", t[len(s):].strip())
            if m2:
                s = s + " " + m2.group(1)
        if len(s) > 150:
            s = s[:147].rsplit(" ", 1)[0] + "…"
        return s
    return ""


def section_bucket(section_title, title):
    st = section_title.lower()
    if st.startswith("open chases") or st.startswith("owed replies"):
        return "open"
    return v25.bucket_for(section_title, title)


def split_head(head):
    out, buf, depth = [], "", 0
    i = 0
    while i < len(head):
        ch = head[i]
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and head.startswith(" · ", i):
            out.append(buf.strip()); buf = ""; i += 3; continue
        buf += ch; i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def parse_card(art, section_title):
    title = v25.title_of(art)
    chip_m = re.search(r'class="chip[^"]*">([^<]+)', art)
    chip = H.unescape(chip_m.group(1)).strip() if chip_m else ""
    h3_inner = re.search(r"<h3>([\s\S]*?)</h3>", art)
    head = strip_tags(re.sub(r'<span class="chip[^"]*">[^<]*</span>', "", h3_inner.group(1))) if h3_inner else title
    bits = split_head(head)
    who = bits[0] if bits else head
    org = " · ".join(bits[1:])
    if who.lower() in ("desk", "no name", "") and org:
        who, org = org, ""
    meta_m = re.search(r'<div class="meta">([\s\S]*?)</div>', art)
    meta = meta_m.group(1) if meta_m else ""
    whys = re.findall(r'<div class="why">([\s\S]*?)</div>', art)
    ems = v25.emails_in(art)
    email = ems[0] if ems else ""
    mailto = ""
    m = re.search(r'href="(mailto:[^"]+)"', art)
    if m:
        mailto = m.group(1)
    extras = re.findall(r'<a class="btn sec" href="([^"]+)">([^<]+)</a>', art)
    phone_disp, tel = tel_of(strip_tags(meta))
    return {
        "section": section_title, "bucket": section_bucket(section_title, title), "title": title, "chip": chip,
        "who": who, "org": org, "email": email, "mailto": mailto, "meta": clean_meta(meta, email, phone_disp),
        "note": short_note(whys), "whys": [strip_tags(w) for w in whys], "phone": phone_disp, "tel": tel,
        "extras": extras, "raw": art,
    }


def area_maps(board):
    amap = {}
    for s in board["sections"]:
        for r in s.get("rows") or []:
            em = (r.get("email") or "").strip().lower()
            if em and r.get("area"):
                amap.setdefault(em, r["area"])
    for r in json.loads(Path("/tmp/new_cands.json").read_text()) if Path("/tmp/new_cands.json").exists() else []:
        em = r["email"].strip().lower()
        if r.get("county") and em not in amap:
            amap[em] = r["county"]
    return amap


def geo(email, amap, text):
    a = (amap.get(email) or "").strip()
    al = a.lower()
    dom = email.split("@")[-1]
    if dom.endswith(OUT_DOMAINS) or al.startswith("farther") or v25.OUT_OF_AREA_COUNTIES & {al.split("·")[0].strip()} - {"flagler"}:
        return 3, (a.split("·")[0].strip() if a else "Out of area")
    if al.startswith(("metro jax", "duval", "st. johns", "st johns", "nassau", "beaches", "jax")):
        lab = a.split("·")[0].strip()
        return 1, ("Jax" if lab.lower().startswith(("metro", "duval", "jax", "beaches")) else lab)
    if al.startswith(("clay", "baker")):
        return 2, a.split("·")[0].strip()
    tl = text.lower()
    for k, lab in (("st. augustine", "St. Johns"), ("ponte vedra", "St. Johns"), ("nocatee", "St. Johns"), ("amelia", "Nassau"),
                   ("fernandina", "Nassau"), ("yulee", "Nassau"), ("orange park", "Clay"), ("oakleaf", "Clay"),
                   ("middleburg", "Clay"), ("fleming", "Clay"), ("green cove", "Clay")):
        if k in tl:
            return (2 if lab == "Clay" else 1), lab
    return 1, "Jax"


def btn_label(c):
    n = c["who"] if c["who"] and not c["who"].lower().startswith(("desk", "campus inbox", "(")) else (c["org"] or c["who"])
    return "Email " + (n[:38] + "…" if len(n) > 40 else n)


def render_fresh(c, idx):
    seg = f'<span class="seg">{esc(c["seg"])}</span>'
    tel = f' · <a class="tel" href="{esc(c["tel"])}">Call {esc(c["phone"])}</a>' if c["tel"] else ""
    extras = "".join(f' <a class="mini" href="{esc(h)}">{esc(t)}</a>' for h, t in c["extras"])
    if c["mailto"]:
        top = f'<a class="mbtn" href="{esc(c["mailto"])}">{esc(btn_label(c))}</a>'
    elif c["tel"]:
        top = f'<a class="mbtn call" href="{esc(c["tel"])}">Call {esc(c["who"])} {esc(c["phone"])}</a>'
    else:
        top = ""
    org = f' · {esc(c["org"])}' if c["org"] else ""
    sub_bits = [f"<b>{esc(c['email'])}</b>"] if c["email"] else []
    if c["meta"]:
        sub_bits.append(esc(c["meta"]))
    note = f'<div class="nt">{esc(c["note"])}</div>' if c.get("note") else ""
    return (f'<article class="q" id="q{idx}">{top}'
            f'<div class="who"><b>{esc(c["who"])}</b>{org} {seg}</div>'
            f'<div class="sm">{" · ".join(sub_bits)}{tel}{extras}</div>{note}</article>')


def render_row(c, tag, tagclass, extra="", keep_mailto=False):
    org = f' · {esc(c["org"])}' if c["org"] else ""
    tel = f' · <a class="tel" href="{esc(c["tel"])}">{esc(c["phone"])}</a>' if c["tel"] else ""
    mail = f' <a class="mini" href="{esc(c["mailto"])}">mailto</a>' if keep_mailto and c["mailto"] else ""
    em = f"<b>{esc(c['email'])}</b>" if c["email"] else "no email"
    ex = f'<div class="nt">{extra}</div>' if extra else ""
    return (f'<div class="row"><span class="chip {tagclass}">{esc(tag)}</span> <b>{esc(c["who"])}</b>{org}'
            f'<div class="sm">{em}{tel}{mail}</div>{ex}</div>')


def details(title, intro, rows, open_=False):
    if not rows:
        return ""
    return (f'<details class="fold"{" open" if open_ else ""}><summary>{esc(title)} <span class="n">{len(rows)}</span></summary>'
            f'<p class="intro">{esc(intro)}</p>' + "\n".join(rows) + "</details>\n")


CSS = """
.strip{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin:0 0 12px}
.strip div{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 4px;text-align:center}
.strip b{display:block;font-size:1.25rem;color:#fff}.strip span{font-size:.62rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.strip .w b{color:#fde68a}.strip .s b{color:#9dffc5}
.grp{font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:16px 0 6px}
.grp i{font-style:normal;color:#c5d0e6}
.q{background:var(--card);border:1px solid #c9a22766;border-radius:12px;padding:10px;margin:0 0 8px}
a.mbtn{display:flex;align-items:center;justify-content:center;min-height:52px;padding:10px 12px;border-radius:10px;background:linear-gradient(180deg,#2f6b4f,#1a3d2e);border:1px solid #3dd68caa;color:#fff;font-weight:800;font-size:1rem;text-decoration:none;margin:0 0 8px}
a.mbtn.call{background:linear-gradient(180deg,#5a4a1a,#2a2210);border-color:#c9a227aa}
.who{font-size:.92rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.seg{display:inline-block;font-size:.62rem;padding:1px 7px;border-radius:999px;border:1px solid #c9a22788;color:#fde68a;vertical-align:middle;margin-left:4px}
.sm{font-size:.76rem;color:var(--muted);margin-top:3px;word-break:break-word}.sm b{color:#c5d0e6;font-weight:600}
a.tel{color:#9dffc5;font-weight:700;text-decoration:none}
a.mini{font-size:.7rem;color:#c5d0e6;border:1px solid var(--line);border-radius:8px;padding:2px 6px;text-decoration:none;margin-left:4px}
.nt{font-size:.74rem;color:#fde68a;margin-top:4px}
details.fold{background:#0e1626;border:1px solid var(--line);border-radius:12px;margin:0 0 8px;padding:0 10px}
details.fold summary{cursor:pointer;padding:12px 0;font-weight:700;font-size:.85rem;color:#c5d0e6;list-style:none}
details.fold summary .n{float:right;color:var(--muted);font-weight:600}
.intro{font-size:.74rem;color:var(--muted);margin:0 0 8px}
.row{border-top:1px solid var(--line);padding:8px 0;font-size:.82rem}
"""


def main():
    raw = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SRC_REV}:dunk-list.html"], text=True)
    board = json.loads(subprocess.check_output(["git", "-C", str(ROOT), "show", f"{SRC_REV}:data/principal_dunk_board.json"], text=True))
    header, footer, sections = v25.parse_sections(raw)
    amap = area_maps(board)

    cards = [parse_card(a, s["title"]) for s in sections for a in s["articles"]]
    fresh, touched, sent, booked, catholic, closed, skipped = [], [], [], [], [], [], []
    removed_dnc, flipped = [], []
    seen = set()
    for c in cards:
        e = c["email"]
        blob = (c["title"] + " " + c["meta"] + " " + e).lower()
        if v25.is_dnc(e, c["title"]) or any(b in blob for b in BANNED_TEXT) or (c["section"].lower().startswith("do not contact")):
            removed_dnc.append({"title": c["title"], "email": e})
            continue
        if e and e in seen:
            continue
        if e:
            seen.add(e)
        b = c["bucket"]
        chipu = c["chip"].upper()
        if b == "scheduled":
            booked.append(c); continue
        if b == "catholic":
            catholic.append(c); continue
        if b == "closed":
            closed.append(c); continue
        if e in SENT_NEW:
            d, sub = SENT_NEW[e]
            c["sent"] = (d, sub)
            sent.append(c)
            flipped.append({"name": c["who"], "org": c["org"], "email": e, "sent_et": d, "subject": sub})
            continue
        if b == "sent" or ("ALREADY SENT" in chipu) or (e in SENT):
            d, sub = SENT.get(e, ("", ""))
            if not d:
                m = re.search(r"ALREADY SENT ([^·]+?ET)", c["chip"] + " " + " ".join(c["whys"]))
                d = m.group(1) if m else "see Gmail Sent"
            c["sent"] = (d, sub)
            sent.append(c); continue
        if not c["mailto"] and not c["tel"]:
            skipped.append(c); continue
        if not c["mailto"] and b not in ("open", "owed"):
            skipped.append(c); continue
        if b == "owed" and not c["mailto"] and "WAITING" in chipu and not e:
            skipped.append(c); continue
        tier, geo_lab = geo(e, amap, c["title"] + " " + c["meta"])
        c["tier"] = tier
        segk = "open" if b in ("open", "owed") else b
        c["segk"] = segk
        c["seg"] = SEG_LABEL.get(segk, "Lead") + ("" if segk in ("open", "catchall") else " · " + geo_lab)
        if segk in ("open", "catchall"):
            c["seg"] = SEG_LABEL[segk] + " · " + geo_lab
        dom = e.split("@")[-1] if e else ""
        if dom and dom not in GENERIC and dom in TOUCHED and TOUCHED[dom][0] != e:
            c["touch"] = TOUCHED[dom]
            touched.append(c); continue
        fresh.append(c)

    pri = {"open": 0, "catchall": 1}
    def key(c):
        if c["segk"] in pri:
            return (pri[c["segk"]], 0, 0)
        return (2 + c["tier"], SEG_ORDER.index(c["segk"]) if c["segk"] in SEG_ORDER else 9, 0)
    fresh_sorted = sorted(enumerate(fresh), key=lambda t: (key(t[1]), t[0]))
    fresh = [c for _, c in fresh_sorted]

    groups = [
        ("1 · Open chases / owed replies", lambda c: c["segk"] == "open"),
        ("2 · Catch-all chains", lambda c: c["segk"] == "catchall"),
        ("3 · Net-new · Jax / St. Johns / Nassau", lambda c: c["segk"] not in pri and c["tier"] == 1),
        ("4 · Net-new · Clay / Baker", lambda c: c["segk"] not in pri and c["tier"] == 2),
        ("5 · Net-new · out of area (last)", lambda c: c["segk"] not in pri and c["tier"] == 3),
    ]
    q_html, idx = [], 0
    for label, f in groups:
        grp = [c for c in fresh if f(c)]
        if not grp:
            continue
        q_html.append(f'<div class="grp">{esc(label)} <i>· {len(grp)}</i></div>')
        for c in grp:
            idx += 1
            q_html.append(render_fresh(c, idx))

    waiting_n = sum(1 for c in fresh if c["mailto"])
    strip = (f'<div class="strip"><div class="w"><b>{waiting_n}</b><span>Waiting</span></div>'
             f'<div class="s"><b>{SENT_TODAY}</b><span>Sent today</span></div>'
             f'<div><b>{len(sent)}</b><span>Sent total</span></div>'
             f'<div><b>{len(booked)}</b><span>Booked</span></div></div>')

    folds = []
    folds.append(details("ALREADY SENT", "Gmail Sent already has these addresses, so there is no mailto.",
                         [render_row(c, "SENT " + c["sent"][0].replace(", 2026", ""), "sent", esc(c["sent"][1])) for c in
                          sorted(sent, key=lambda c: 0 if c["email"] in SENT_NEW else 1)]))
    folds.append(details("ORG ALREADY TOUCHED", "Someone else at this org got mail in the last 30 days; send only if a second contact makes sense.",
                         [render_row(c, "ORG TOUCHED", "low", f"Sent {esc(c['touch'][0])} · {esc(c['touch'][1])}", keep_mailto=True) for c in touched]))
    folds.append(details("SCHEDULED / BOOKED", "On the calendar, so these are not a chase.",
                         [render_row(c, c["chip"] or "BOOKED", "sent", esc(c["note"])) for c in booked]))
    folds.append(details("Catholic · deprioritized", "Diocese insurance makes these low priority, so there is no chase mailto.",
                         [render_row(c, "LOW", "low") for c in catholic]))
    folds.append(details("No-thank-yous", "Closed; no chase.", [render_row(c, c["chip"] or "CLOSED", "closed", esc(c["note"])) for c in closed]))
    folds.append(details("Skipped / no email", "No published email or nothing to send; phone only.",
                         [render_row(c, "NO EMAIL" if not c["email"] else "SKIP", "low", esc(c["note"])) for c in skipped]))

    # header
    header = header.replace("?v=2925", HARD)
    header = header.replace("</style>", CSS + "</style>", 1)
    header = re.sub(r'<p class="sub">[\s\S]*?</p>', '<p class="sub">Phone work queue. Tap the green button, then hit Send yourself.</p>', header, count=1)
    header = re.sub(r'<div class="banner">[\s\S]*?</div>',
                    '<div class="banner"><b>DRAFTS / MAILTO ONLY — never auto-send.</b> Nothing on this page sends mail.'
                    '<span class="ver">v2.9.26 · Oct 4, 2026 11:55 PM ET · Sent caught up · ?v=2926</span></div>', header, count=1)
    footer = footer.replace("?v=2925", HARD)
    footer = re.sub(r'<p class="note">[\s\S]*?</p>',
                    '<p class="note">v2.9.26 · Sent checked Oct 4, 2026 11:55 PM ET · mailto only · no auto-send · ?v=2926</p>', footer, count=1)

    body = (strip + '\n<div class="grp">Waiting to send · priority order</div>\n' + "\n".join(q_html) +
            '\n<div class="grp">Reference · tap to open</div>\n' + "".join(folds))
    html_out = header + "\n" + body + "\n" + footer

    # ---- sanity ----
    low = html_out.lower()
    assert "gmail.googleapis" not in low and "scripts/send" not in low
    assert "?v=2925" not in html_out and "v2.9.25" not in html_out, "stale version"
    assert "never auto-send" in low
    for b in BANNED_TEXT:
        assert b not in low, f"banned text present: {b}"
    assert not re.search(r"\blina\b", low), "Lina present"
    mt = re.findall(r'href="mailto:([^?"]+)', html_out)
    mt = [m.lower() for m in mt]
    for m in mt:
        assert m not in SENT, f"mailto to sent address {m}"
    dup = [e for e, n in Counter(mt).items() if n > 1]
    assert not dup, f"dup mailto {dup}"
    all_emails = [c["email"] for grp in (fresh, touched, sent, booked, catholic, closed, skipped) for c in grp if c["email"]]
    d2 = [e for e, n in Counter(all_emails).items() if n > 1]
    assert not d2, f"dup cards {d2}"
    assert "Corporate HQ · <b>Corporate HQ" not in html_out and "Field District · <b>Field District" not in html_out
    assert html_out.count("<details") == html_out.count("</details>") and " open>" not in html_out

    for p in (ROOT / "dunk-list.html", CRIT / "dunk-list.html"):
        p.write_text(html_out)

    # ---- board json ----
    board["as_of"] = AS_OF
    board["board_version"] = BOARD_VER
    touched_by_email = {c["email"]: c["touch"] for c in touched}
    n_sent_rows = n_touch_rows = 0
    for s in board["sections"]:
        keep = []
        for r in s.get("rows") or []:
            em = (r.get("email") or "").strip().lower()
            blob = ((r.get("contact") or "") + " " + (r.get("account") or "") + " " + em).lower()
            if any(b in blob for b in BANNED_TEXT) or re.search(r"\blina\b", (r.get("contact") or "").lower()):
                r["draft_status"] = "DO_NOT_CONTACT"
                r["chip_tags"] = ["DO NOT CONTACT", "No mailto"]
            if em in SENT_NEW:
                d, sub = SENT_NEW[em]
                r["draft_status"] = "SENT"
                r["chip_tags"] = [t for t in (r.get("chip_tags") or []) if "WAITING" not in t] + [f"ALREADY SENT {d}"]
                r["sent_note"] = f"ALREADY SENT {d} — {sub}"
                n_sent_rows += 1
            elif em in touched_by_email:
                a, d = touched_by_email[em]
                r["org_touched"] = f"ORG ALREADY TOUCHED · {a} · {d}"
                tags = [t for t in (r.get("chip_tags") or []) if "ORG ALREADY TOUCHED" not in t]
                r["chip_tags"] = tags + ["ORG ALREADY TOUCHED"]
                n_touch_rows += 1
            keep.append(r)
        s["rows"] = keep
    board["v2926"] = {
        "as_of": AS_OF, "hard_refresh": HARD, "no_outbound_send": True, "compose_only": True,
        "flipped_already_sent": flipped, "org_touched_count": len(touched),
        "fresh_waiting_count": waiting_n, "sent_today_gmail": SENT_TODAY,
        "change": "Sent catch-up (exact + alias), org-touched within 30 days de-emphasized, phone work-queue layout, collapsed reference sections.",
    }
    BOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n")
    shutil.copy2(BOARD, CRIT / "data" / "principal_dunk_board.json")

    for p in (ROOT / "principal-dunk.html", CRIT / "principal-dunk.html"):
        if p.exists():
            t = p.read_text()
            p.write_text(t.replace("?v=2925", HARD).replace("?v=2924", HARD))

    summary = {
        "board_version": BOARD_VER, "as_of": AS_OF, "hard_refresh": HARD, "no_outbound_send": True, "compose_only": True,
        "banner": "DRAFTS / MAILTO ONLY — never auto-send",
        "counters": {"waiting": waiting_n, "sent_today_gmail_messages": SENT_TODAY, "sent_total_cards": len(sent), "booked": len(booked)},
        "flipped_already_sent_this_pass": flipped,
        "org_touched": [{"name": c["who"], "org": c["org"], "email": c["email"], "touched_via": c["touch"][0], "touched_et": c["touch"][1]} for c in touched],
        "fresh_waiting": [{"rank": i + 1, "name": c["who"], "org": c["org"], "email": c["email"], "seg": c["seg"]} for i, c in enumerate(fresh)],
        "section_counts": {"fresh": len(fresh), "org_touched": len(touched), "already_sent": len(sent), "booked": len(booked),
                           "catholic": len(catholic), "no_thank_yous": len(closed), "skipped_no_email": len(skipped)},
        "removed_banned_cards": removed_dnc,
        "board_rows_flipped_sent": n_sent_rows, "board_rows_org_touched": n_touch_rows,
        "off_list_sent_tonight_not_on_board": [
            "katherineadesja@gmail.com", "gpeptapresident@gmail.com", "secretary.jcepto@gmail.com", "kwelch.hodgespres@gmail.com",
            "atlanticcoasthsptsa@gmail.com", "alimacanipta@gmail.com", "president@landrumpto.com", "info@fivepointsassociation.org",
            "e000822111@brookdale.com", "adultdaycare@agingtrue.org", "ekendall@wjxt.com", "radams@wjxt.com"],
        "live_urls": [
            "https://code4crittersoncallapps.github.io/sheehan-exec-suite/dunk-list.html?v=2926",
            "https://code4crittersoncallapps.github.io/critters-on-call/exec/dunk-list.html?v=2926",
        ],
    }
    out = ROOT / "data" / "_dunk_v2926_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    shutil.copy2(out, CRIT / "data" / "_dunk_v2926_summary.json")
    print(json.dumps({"counters": summary["counters"], "sections": summary["section_counts"], "flipped": flipped,
                      "removed": removed_dnc, "board_sent": n_sent_rows, "board_touch": n_touch_rows}, indent=1))


if __name__ == "__main__":
    main()
