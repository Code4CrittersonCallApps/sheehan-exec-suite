#!/usr/bin/env python3
"""dunk v2.9.25 — Sent-reconciled phone list. Mailto only. Never auto-send."""
from __future__ import annotations

import csv
import html as html_lib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

ROOT = Path("/workspace/sheehan-exec-suite")
CRIT = Path("/workspace/critters-on-call/exec")
BOARD = ROOT / "data" / "principal_dunk_board.json"
HTML_IN = ROOT / "dunk-list.html"
CANDS = Path("/tmp/new_cands.json")
GLEN = Path("/workspace/exports/glengarry-2026-10-04")
ET = ZoneInfo("America/New_York")
AS_OF = "2026-10-04 evening ET"
BOARD_VER = (
    "Board v2.9.25 · Oct 4, 2026 evening ET · Sent reconcile + net-new mailto "
    "(compose only, never auto-send)"
)
HARD = "?v=2925"

# email -> (date label ET, subject). Confirmed sheehanhomestead Sent (to or cc).
SENT = {
    "bseptapres@gmail.com": ("Oct 1, 2026 6:39 PM ET", "Re: Petting zoo for fall festival / trunk or treat?"),
    "rtrevett@sjcds.net": ("Oct 4, 2026 8:39 PM ET", "Petting zoo for fall festival / trunk or treat?"),
    "llicata@vestapropertyservices.com": ("Oct 2, 2026 11:46 AM ET", "Vesta Referred Petting Zoo/Goat Yoga/Mommy&Me/STEM?"),
    "llicatta@vestapropertyservices.com": ("Oct 2, 2026 11:46 AM ET", "Vesta Referred Petting Zoo/Goat Yoga/Mommy&Me/STEM?"),
    "news@actionnewsjax.com": ("Sep 30, 2026 9:50 AM ET", "Social Shout Out for Local Eduatainment/Agritourism Biz?"),
    "kate.trivelpiece@fsresidential.com": ("Oct 2, 2026 5:44 PM ET", "Re: Petting zoo for CDD / amenity fall festival?"),
    "abrassfield@rizzetta.com": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall or spring events?"),
    "athompson@elcduval.org": ("Mar 3, 2026 12:09 PM ET", "Re: Golden Ticket/VPK"),
    "comments@mcdjax.com": ("Oct 4, 2026 8:35 PM ET", "Petting zoo for community / employee family event?"),
    "carvalhov@pfm.com": ("Sep 25, 2026 3:20 PM ET", "Petting zoo for CDD / amenity fall festival?"),
    "cathy.hemphill@goddardschools.com": ("Sep 23, 2026 7:10 PM ET", "Trunk or treat"),
    "cburgessalf@yahoo.com": ("Oct 30, 2024 8:17 AM ET", "Re: Petting Zoo"),
    "danielle@daniellekeenerevents.com": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall or spring events?"),
    "communityfirst@c1cufl.org": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for employee family day?"),
    "david.decamp@crowley.com": ("Sep 28, 2026 1:51 AM ET", "Petting zoo for fall festival / trunk or treat?"),
    "contact@vestapropertyservices.com": ("Apr 16, 2025 9:27 AM ET", "homestead Sent"),
    "donny.hoessler@stjohns.k12.fl.us": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall festival / trunk or treat?"),
    "doug@dayspring.health": ("Nov 18, 2024 6:59 PM ET", "homestead Sent (cc)"),
    "donald.beardsley@invitedclubs.com": ("Nov 4, 2024 3:17 PM ET", "homestead Sent"),
    "fcpreschool.director@aol.com": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall or spring events?"),
    "flaglercenter@tlechildcare.com": ("Sep 25, 2026 11:13 AM ET", "Petting zoo for fall festival / trunk or treat?"),
    "g.david@unf.edu": ("Apr 25, 2025 10:13 AM ET", "homestead Sent"),
    "hiddenhills@cmcjaxfla.com": ("Sep 24, 2026 8:00 AM ET", "homestead Sent"),
    "info@duvallandscape.com": ("Sep 23, 2026 8:00 AM ET", "homestead Sent"),
    "info@fleetlanding.com": ("Nov 4, 2024 1:57 PM ET", "homestead Sent"),
    "info@jacksonvillemom.com": ("Aug 8, 2024 2:19 PM ET", "homestead Sent"),
    "jacksonvillecr@publix.com": ("Sep 30, 2026 9:22 PM ET", "homestead Sent"),
    "ivybrookptovr@gmail.com": ("Sep 23, 2026 7:12 PM ET", "homestead Sent"),
    "jennifer.ripkey@ivybrookacademy.com": ("Apr 20, 2026 5:25 PM ET", "homestead Sent"),
    "info@starlingatnocatee.com": ("Nov 5, 2024 7:25 AM ET", "homestead Sent"),
    "jacksonville2fl@goddardschools.com": ("Aug 28, 2024 6:35 PM ET", "homestead Sent"),
    "jenna@dayspringvillage.org": ("Nov 18, 2024 6:59 PM ET", "homestead Sent (cc)"),
    "jessa_collins@lcca.com": ("Nov 5, 2024 10:17 AM ET", "homestead Sent"),
    "jen.riesenberger@arborcompany.com": ("Sep 3, 2024 8:00 AM ET", "homestead Sent"),
    "joshua.gibson@publix.com": ("Sep 30, 2026 8:00 AM ET", "Petting zoo for kids night / local store event?"),
    "jsapere@maymgt.com": ("Sep 25, 2026 3:35 PM ET", "community festival animals?"),
    "jmeadows@vestapropertyservices.com": ("Jul 20, 2026 2:19 PM ET", "homestead Sent"),
    "jlucansky@vestapropertyservices.com": ("Jun 22, 2026 11:47 AM ET", "Fall Farm Events Are Filling Fast – Reserve Your Date Today!"),
    "lburnette@rivercityscience.org": ("Sep 18, 2026 5:28 PM ET", "homestead Sent"),
    "lisa.picard@gardensmemorycare.com": ("Oct 9, 2025 8:57 AM ET", "homestead Sent"),
    "ksperanza@canopyway.com": ("Sep 10, 2024 1:21 PM ET", "homestead Sent"),
    "mczmyr@vestapropertyservices.com": ("Oct 4, 2026 9:02 PM ET", "Fall or spring petting zoo/goat yoga dates?"),
    "mckena@dayspring.health": ("Nov 18, 2024 6:59 PM ET", "homestead Sent"),
    "lpaxton@ccmcnet.com": ("Oct 27, 2024 1:29 PM ET", "homestead Sent"),
    "mdawkins@nassaucountycoa.org": ("Nov 15, 2024 9:27 AM ET", "homestead Sent"),
    "niralnpatel1618@gmail.com": ("Jun 22, 2026 11:42 AM ET", "Fall Farm Events Are Filling Fast – Reserve Your Date Today!"),
    "rebecca.thompson@stjohns.k12.fl.us": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall or spring events?"),
    "ripollv@pfm.com": ("Sep 25, 2026 3:20 PM ET", "homestead Sent"),
    "pvalenzuela@discoveryvillages.com": ("Mar 2, 2026 11:55 AM ET", "homestead Sent"),
    "samantha.bacon@gardensmemorycare.com": ("Sep 4, 2025 5:30 PM ET", "homestead Sent"),
    "slewis@grandliving.com": ("Feb 26, 2025 9:27 AM ET", "homestead Sent"),
    "support@kidspartiesjax.com": ("Sep 29, 2026 10:32 PM ET", "Petting zoo for fall or spring events?"),
    "sustainability@crowley.com": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for employee family or community event?"),
    "tiffany.cantwell@stjohns.k12.fl.us": ("Sep 29, 2026 9:27 AM ET", "Petting zoo for fall festival / trunk or treat?"),
    "yuleedugoutclub@gmail.com": ("Oct 2, 2026 3:05 PM ET", "Our Current Giving Approach"),
}

DNC_EMAILS = {
    "llicata@vestapropertyservices.com",
    "llicatta@vestapropertyservices.com",
}
DNC_NAME_BITS = ("lisa licata", "lisa licatta", "georgia hamilton", "jessica morgan")
# "lina" alone is too wide (Angelina). Match whole tokens.
DNC_EXACT_NAMES = {"lina", "lina lihernandez", "lina hernandez"}

OUT_OF_AREA_COUNTIES = {
    "alachua", "orange", "escambia", "volusia", "putnam", "camden", "lee", "flagler",
}
SKIP_EMAIL_DOMAINS = ("stjohnsgolf.com",)  # already on calendar
SKIP_EMAILS = {
    "bthomas@vestapropertyservices.com",  # backup, do not second-pitch Lucansky
}

METRO = {"duval", "st. johns", "st johns", "clay", "nassau", "baker", ""}


def esc(s: str) -> str:
    return html_lib.escape(s or "", quote=True)


def emails_in(blob: str) -> list[str]:
    found = re.findall(r"mailto:([^?\"'\s>]+)", blob, flags=re.I)
    if not found:
        found = re.findall(r"<b>([^<]+@[^<]+)</b>", blob, flags=re.I)
    out = []
    for e in found:
        e = e.strip().lower()
        if "@" in e and " " not in e:
            out.append(e)
    # unique preserve order
    seen = set()
    uniq = []
    for e in out:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq


def title_of(article: str) -> str:
    m = re.search(r"<h3>([\s\S]*?)</h3>", article)
    if not m:
        return ""
    t = re.sub(r"<[^>]+>", "", m.group(1))
    return html_lib.unescape(re.sub(r"\s+", " ", t)).strip()


def bucket_for(section: str, title: str) -> str:
    s = section.lower()
    card = title.lower()
    if "catholic" in s or "deprior" in s:
        return "catholic"
    if "catch-all" in s:
        return "catchall"
    if s.startswith("scheduled") or "scheduled / booked" in s:
        return "scheduled"
    if "no-thank" in s or s.startswith("no-thank"):
        return "closed"
    if "media" in s or "shout-out" in s:
        return "media"
    if "hot chase" in s or "shamebuster" in s:
        return "open"
    if "owed" in s or "follow-up" in s:
        return "owed"
    if "already sent" in s:
        return "sent"
    if "private senior" in s:
        return "senior"
    if s.startswith("net-new corporate") or "field district" in s:
        return "corporate"
    # Card title only. Mixed TAM headings contain every segment word.
    if any(k in card for k in ("party with", "party company", "g.g. events", "lovelee", "carousel", "in good company", "event design", "kids parties")):
        return "planners"
    if any(k in card for k in ("senior", "memory", "council on aging", "pace place", "dayspring", "starling", "harborchase", "fleet landing", "osprey", "the blake", "discovery village", "grand living", "assisted", "day care", "adult day")):
        return "senior"
    if any(k in card for k in (" cdd", "hoa", "vesta", "firstservice", "associa", "rizzetta", "plantation", "country club", "golf", "amenity", "stewardship", "wildlight", "silverleaf", "greystar")):
        return "hoa"
    if any(k in card for k in ("school", "pta", "pto", "vpk", "preschool", "academy", "university", "college", " elc", "learning experience", "ivybrook")):
        return "schools"
    if any(k in card for k in ("festival", "chamber", "sports &", "sports and", "convention", "visitors bureau", "parish", "church")):
        return "festivals"
    if any(k in card for k in ("publix", "mcdonald", "mayo", "jea", "csx", "crowley", "ascension", "jaxport", "baptist", "credit union", "patriot", "dream finders", "mall", "ale works", "mwr")):
        return "corporate"
    return "corporate"

def strip_links(article: str) -> str:
    if "<div class=\"links\">" not in article:
        return article
    return re.sub(
        r"<div class=\"links\">[\s\S]*?</div>",
        "<div class=\"links\"><span class=\"meta\">No mailto. Already sent or do-not-contact. Do not stage a new chase.</span></div>",
        article,
        count=1,
    )


def set_chip(article: str, klass: str, label: str) -> str:
    return re.sub(
        r"<span class=\"chip[^\"]*\">[^<]*</span>",
        f"<span class=\"chip {klass}\">{esc(label)}</span>",
        article,
        count=1,
    )


def add_why(article: str, text: str) -> str:
    block = f"<div class=\"why\">{text}</div>\n  "
    if "<div class=\"links\">" in article:
        return article.replace("<div class=\"links\">", block + "<div class=\"links\">", 1)
    return article.rstrip() + "\n  " + block + "\n"


def is_dnc(email: str, title: str) -> bool:
    if email in DNC_EMAILS or email.startswith("llicata@") or email.startswith("llicatta@"):
        return True
    tl = title.lower()
    if any(b in tl for b in DNC_NAME_BITS):
        return True
    # whole-name Lina, not Angelina
    name = tl.split("·")[0]
    name = re.sub(r"^(waiting send|already sent|s ·|a ·|b ·|c ·|deprioritized)\s*", "", name).strip()
    if name in DNC_EXACT_NAMES or name.startswith("lina "):
        return True
    return False


def mailto_href(email: str, subject: str, body: str) -> str:
    return "mailto:" + email + "?subject=" + quote(subject, safe="") + "&body=" + quote(body, safe="")


def new_card(name: str, org: str, email: str, phone: str, title: str, subject: str, body: str, why: str) -> str:
    who = esc(name) if name else "Desk"
    org_e = esc(org)
    bits = [f"<b>{esc(email)}</b>"]
    if phone:
        bits.append(esc(phone))
    if title:
        bits.append(esc(title))
    meta = " · ".join(bits)
    link = mailto_href(email, subject, body)
    return (
        "<article class=\"card top\">\n"
        f"  <h3><span class=\"chip wait\">WAITING Send</span> {who} · {org_e}</h3>\n"
        f"  <div class=\"meta\">{meta}</div>\n"
        f"  <div class=\"why\">{why}</div>\n"
        f"  <div class=\"links\"><a class=\"btn\" href=\"{esc(link)}\">Open mailto</a></div>\n"
        "</article>"
    )


def pitch(first: str, hook: str) -> str:
    greet = f"Hi {first}," if first else "Hi there,"
    return (
        f"{greet}\n\n"
        "We bring mobile petting zoos to family events around metro Jacksonville. "
        f"{hook}\n\n"
        "Do you have one fall or spring date that should have animals? Happy to send open dates.\n"
    )


def first_name(name: str) -> str:
    name = (name or "").strip()
    if not name or name.startswith("(") or name.lower() in {"desk", "no name"}:
        return ""
    return name.split()[0]


def segment_of(row: dict) -> str:
    f = row["file"]
    blob = " ".join([row.get("title") or "", row.get("org") or "", row.get("community") or "", row.get("bucket") or ""]).lower()
    if f == "COLLEGES.csv":
        return "schools"
    if f == "ENTERPRISE.csv":
        return "corporate"
    if any(k in blob for k in ("party planner", "event planner", "event design", "event planning")):
        return "planners"
    if "festival" in blob:
        return "festivals"
    if any(k in blob for k in ("senior", "55+", "retirement", "assisted")):
        return "senior"
    return "hoa"


HOOKS = {
    "schools": ("Petting zoo for fall festival / trunk or treat?", "Schools and campuses book us for fall festivals, trunk-or-treat, and family STEM days."),
    "senior": ("Petting zoo for a resident or family day?", "Senior communities book a small visit for residents and family days."),
    "hoa": ("Petting zoo for CDD / amenity fall festival?", "CDD and HOA amenity desks book us for community festivals and family days."),
    "corporate": ("Petting zoo for employee family or community event?", "We also do employee family days and community events for local employers."),
    "festivals": ("Petting zoo for a fall festival date?", "Fall festivals are the main season for a petting zoo stop."),
    "planners": ("Petting zoo for fall or spring events?", "Planners use us when a family event needs animals, not another bounce house."),
}


def parse_sections(text: str):
    idx = text.find('<div class="sec">')
    header = text[:idx]
    rest = text[idx:]
    foot_at = rest.find('<div class="sec">Collateral')
    if foot_at < 0:
        raise SystemExit("collateral marker missing")
    footer = rest[foot_at:]
    body = rest[:foot_at]
    parts = re.split(r'<div class="sec">', body)
    sections = []
    for p in parts[1:]:
        title, _, content = p.partition("</div>")
        articles = re.findall(r"<article class=\"card[^\"]*\">[\s\S]*?</article>", content)
        sections.append({"title": title.strip(), "articles": articles})
    return header, footer, sections


def main() -> None:
    raw = HTML_IN.read_text()
    header, footer, sections = parse_sections(raw)

    flipped = []
    dnc_cards = []
    buckets = {k: [] for k in (
        "open", "catchall", "media", "schools", "senior", "hoa", "corporate",
        "festivals", "planners", "scheduled", "owed", "sent", "catholic", "closed",
    )}
    seen_email = {}
    dupes_removed = []

    for sec in sections:
        for art in sec["articles"]:
            title = title_of(art)
            ems = emails_in(art)
            email = ems[0] if ems else ""
            b = bucket_for(sec["title"], title)
            chip_m = re.search(r'class="chip[^"]*">([^<]+)', art)
            chip_label = chip_m.group(1) if chip_m else ""
            already_chip = ("SENT" in chip_label.upper()) and ("WAITING" not in chip_label.upper())
            if is_dnc(email, title):
                art2 = set_chip(art, "closed", "DO NOT CONTACT")
                art2 = strip_links(art2)
                note = "Do not pitch. Lisa Licata was a do-not-contact."
                if email in SENT:
                    d, sub = SENT[email]
                    note += f" ALREADY SENT {d} — {sub}."
                art2 = add_why(art2, f"<b>{esc(note)}</b>")
                art2 = art2.replace('class="card top"', 'class="card closed"', 1)
                dnc_cards.append(art2)
                flipped.append({"name": title, "email": email, "date": SENT.get(email, ("", ""))[0], "subject": SENT.get(email, ("", ""))[1], "dnc": True})
                if email:
                    seen_email[email] = "dnc"
                continue
            sent = SENT.get(email) if email else None
            if already_chip and not sent and b not in ("catholic", "scheduled", "closed"):
                art2 = strip_links(art)
                if email and email in seen_email:
                    dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": "sent", "title": title})
                else:
                    buckets["sent"].append(art2)
                    if email:
                        seen_email[email] = "sent"
                continue
            if b == "catholic":
                # stay deprioritized; never a mailto chase
                art2 = strip_links(art) if "mailto:" in art.lower() else art
                buckets["catholic"].append(art2)
                if email:
                    if email in seen_email:
                        dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": "catholic", "title": title})
                        buckets["catholic"].pop()
                    else:
                        seen_email[email] = "catholic"
                continue
            if b == "scheduled":
                art2 = art
                if sent:
                    art2 = strip_links(art2)
                    d, sub = sent
                    art2 = add_why(art2, f"<b>ALREADY SENT {esc(d)}</b> — {esc(sub)}. Booked card only. No mailto.")
                elif "mailto:" in art2.lower() and "waiting" in art2.lower():
                    # scheduled must not sit as a send chase
                    art2 = strip_links(art2)
                buckets["scheduled"].append(art2)
                if email:
                    if email in seen_email:
                        dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": "scheduled", "title": title})
                        buckets["scheduled"].pop()
                    else:
                        seen_email[email] = "scheduled"
                continue
            if b == "closed":
                buckets["closed"].append(strip_links(art) if "mailto:" in art.lower() else art)
                if email:
                    seen_email.setdefault(email, "closed")
                continue
            if sent and b != "owed":
                d, sub = sent
                art2 = set_chip(art, "sent", f"ALREADY SENT {d}")
                art2 = strip_links(art2)
                art2 = add_why(art2, f"<b>ALREADY SENT {esc(d)}</b> — {esc(sub)}. No mailto. Do not stage a fresh chase.")
                art2 = art2.replace('class="card top"', 'class="card"', 1)
                target = "sent"
                if email and email in seen_email:
                    dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": target, "title": title})
                else:
                    buckets[target].append(art2)
                    if email:
                        seen_email[email] = target
                    flipped.append({"name": title, "email": email, "date": d, "subject": sub, "dnc": False})
                continue
            if sent and b == "owed":
                d, sub = sent
                art2 = set_chip(art, "sent", f"ALREADY SENT {d}")
                art2 = strip_links(art2)
                art2 = add_why(art2, f"<b>ALREADY SENT {esc(d)}</b> — {esc(sub)}. No mailto.")
                if email and email in seen_email:
                    dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": "sent", "title": title})
                else:
                    buckets["sent"].append(art2)
                    if email:
                        seen_email[email] = "sent"
                    flipped.append({"name": title, "email": email, "date": d, "subject": sub, "dnc": False})
                continue
            # still waiting
            if email and email in seen_email:
                dupes_removed.append({"email": email, "kept": seen_email[email], "dropped": b, "title": title})
                continue
            if email:
                seen_email[email] = b
            buckets[b].append(art)

    # new contacts
    cands = json.loads(CANDS.read_text())
    skipped = []
    added = []
    grouped = {}
    for row in cands:
        email = row["email"].strip().lower()
        name = (row.get("name") or "").strip()
        nl = name.lower()
        if email in SKIP_EMAILS or any(email.endswith("@" + d) or email.endswith(d) for d in SKIP_EMAIL_DOMAINS) or "stjohnsgolf.com" in email:
            skipped.append({"name": name, "email": email, "reason": "already a customer or do-not-double-send backup"})
            continue
        if nl in DNC_EXACT_NAMES or any(b in nl for b in DNC_NAME_BITS) or email in DNC_EMAILS:
            skipped.append({"name": name, "email": email, "reason": "do-not-contact"})
            continue
        if email in SENT or email in seen_email:
            reason = "already in Gmail Sent" if email in SENT else "already on dunk list"
            skipped.append({"name": name, "email": email, "org": row.get("org"), "reason": reason})
            continue
        county = (row.get("county") or "").strip().lower()
        if row["file"] == "COLLEGES.csv" and county in OUT_OF_AREA_COUNTIES:
            skipped.append({"name": name, "email": email, "org": row.get("org"), "reason": f"out of area ({row.get('county')})"})
            continue
        if email not in grouped:
            grouped[email] = row
        else:
            prev = grouped[email]
            prev["org"] = prev.get("org") or ""
            extra = row.get("org") or ""
            if extra and extra not in prev["org"]:
                prev["org"] = prev["org"] + " / " + extra

    # doppelganger phone-only / already emailed skips (explicit)
    for item in json.loads(Path("/workspace/exports/dunk-doppelgangers-2026-10-03/dunk_additions.json").read_text())["additions"]:
        em = (item.get("email") or "").strip()
        if not em:
            skipped.append({"name": item.get("contact") or item.get("account"), "email": "", "reason": "no email", "account": item.get("account")})
        elif em.lower() in SENT or "emailed" in (item.get("gmail") or "").lower():
            skipped.append({"name": item.get("contact") or item.get("account"), "email": em, "reason": "already emailed", "account": item.get("account")})


    forced = [
        {"email":"vina.delcomyn@awakeningsami.com","name":"Vina Delcomyn","title":"LCAM / Community Manager","org":"Azalea Ridge HOA","community":"Azalea Ridge HOA","phone":"(904) 940-5850","file":"AMENITY.csv","bucket":"amenity","county":"Clay"},
        {"email":"marilyn@firstcoastcms.com","name":"Marilyn Newbauer","title":"Facility Attendant / Amenity","org":"Magnolia West CDD","community":"Magnolia West CDD","phone":"(904) 531-9382","file":"AMENITY.csv","bucket":"amenity","county":"Clay"},
        {"email":"mgiles@gmsnf.com","name":"Marilee Giles","title":"District / Amenity","org":"Oakleaf Plantation Master HOA","community":"Oakleaf Plantation Master HOA","phone":"(904) 940-5850","file":"AMENITY.csv","bucket":"amenity","county":"Clay"},
    ]
    for row in forced:
        email=row["email"]
        if email in SENT or email in seen_email or email in grouped:
            skipped.append({"name": row["name"], "email": email, "reason": "already on dunk list or Sent"})
            continue
        grouped[email]=row

    for email, row in grouped.items():
        seg = segment_of(row)
        subj, hook = HOOKS[seg]
        fn = first_name(row.get("name") or "")
        body = pitch(fn, hook)
        who = row.get("name") or "Desk"
        org = row.get("community") or row.get("org") or "Account"
        why = f"<b>Net-new {esc(seg)}</b> · not on the prior dunk board · not in Gmail Sent as of Oct 4, 2026 evening ET. Compose only. Tap mailto, then Send yourself."
        card = new_card(who, org, email, row.get("phone") or "", row.get("title") or "", subj, body, why)
        buckets[seg].append(card)
        seen_email[email] = seg
        added.append({
            "name": who,
            "email": email,
            "org": org,
            "segment": seg,
            "phone": row.get("phone") or "",
            "title": row.get("title") or "",
            "subject": subj,
            "body": body,
            "file": row["file"],
        })

    # header / footer stamps
    header = header.replace("?v=2924", HARD)
    header = re.sub(
        r'<div class="banner">[\s\S]*?</div>',
        '<div class="banner"><b>DRAFTS / MAILTO ONLY — never auto-send.</b> Tap Open mailto, then hit Send yourself. Nothing on this page sends mail.\n'
        '<span class="ver">v2.9.25 · Oct 4, 2026 evening ET · Sent reconciled · compose only · ?v=2925</span>\n'
        "</div>",
        header,
        count=1,
    )
    header = header.replace(
        "Compose only. Outward business drafts marked WAITING homestead Send. No auto-send. Personal / financial-stress / embarrassing items never listed.",
        "Compose only. Mailto drafts only. You tap the button and hit Send yourself. No auto-send. If Gmail Sent already has the address, there is no mailto.",
    )
    footer = footer.replace("?v=2924", HARD)
    footer = re.sub(
        r'<p class="note">[\s\S]*?</p>',
        "<p class=\"note\">Source refresh Oct 4, 2026 evening ET · v2.9.25 · Sent reconciled · mailto only · no auto-send · ?v=2925</p>",
        footer,
        count=1,
    )

    def sec(title: str, blurb: str, cards: list[str]) -> str:
        if not cards:
            return ""
        return (
            f'<div class="sec">{esc(title)}</div>\n'
            f'<div class="why">{blurb}</div>\n'
            + "\n\n".join(cards)
            + "\n\n"
        )

    parts = []
    parts.append(sec(
        "Open chases · not sent · mailto only · ?v=2925",
        "<b>Compose only. Nothing on this page sends.</b> Tabatha Onorato is not here: Gmail Sent has newer mail after Sep 25 (latest Oct 1, 2026 6:39 PM ET). No mailto on anyone already sent.",
        buckets["open"],
    ))
    parts.append(sec(
        "CATCH-ALL chains · Goddard not scheduled · Ivybrook twins · Vesta not-yet · ?v=2925",
        "<b>Compose only. Mailto only if Sent is empty.</b> One card per email. Dupes of Alexis Bailey, Joanna Lynch-Arias, and John Williams were removed from later sections. Lisa Licata is off this stack (do-not-contact). Catholic schools stay at the bottom.",
        buckets["catchall"],
    ))
    parts.append(sec(
        "Press / local media · mailto only",
        "<b>Same shout-out voice. No signature in the mailto.</b> Compose only. Never auto-send. Action News news@ is already sent and is not in this stack.",
        buckets["media"],
    ))
    parts.append(sec(
        "Net-new · schools / VPK / campus",
        "<b>WAITING Send only if Gmail Sent has no message to that address.</b> Mailto only.",
        buckets["schools"],
    ))
    parts.append(sec(
        "Net-new · private senior living",
        "<b>WAITING Send only if never sent.</b> Mailto only.",
        buckets["senior"],
    ))
    parts.append(sec(
        "Net-new · HOA / CDD amenity",
        "<b>WAITING Send only if never sent.</b> Mailto only. One card per inbox.",
        buckets["hoa"],
    ))
    parts.append(sec(
        "Net-new · corporate / employer",
        "<b>WAITING Send only if never sent.</b> Mailto only.",
        buckets["corporate"],
    ))
    parts.append(sec(
        "Net-new · festivals",
        "<b>WAITING Send only if never sent.</b> Mailto only.",
        buckets["festivals"],
    ))
    parts.append(sec(
        "Net-new · party planners",
        "<b>WAITING Send only if never sent.</b> Mailto only.",
        buckets["planners"],
    ))
    parts.append(sec(
        "SCHEDULED / BOOKED · calendar locked (not a chase)",
        "<b>Not mixed into WAITING Send.</b> No fresh chase mailto.",
        buckets["scheduled"],
    ))
    parts.append(sec(
        "Owed replies / follow-ups",
        "<b>Not a cold chase.</b> Mailto only if Sent does not already have the address.",
        buckets["owed"],
    ))
    parts.append(sec(
        "ALREADY SENT · no mailto · do not re-chase",
        "<b>Gmail Sent already has a message to this address.</b> Chip shows date and subject. The mailto button is removed.",
        buckets["sent"],
    ))
    parts.append(sec(
        "DEPRIORITIZED / LOW · Catholic schools (diocese insurance)",
        "<b>Not in the active stack.</b> Parish schools and parish ELCs stay here. No chase mailto.",
        buckets["catholic"],
    ))
    parts.append(sec(
        "Do not contact · off the waiting stack",
        "<b>Do not pitch.</b> Lisa Licata / Llicata@ (and Llicatta@). No mailto.",
        dnc_cards,
    ))
    parts.append(sec(
        "No-thank-yous / closed (no chase)",
        "<b>No chase.</b>",
        buckets["closed"],
    ))

    html_out = header + "\n" + "".join(parts) + footer
    # hard ban: no send API
    if "gmail.googleapis" in html_out or "scripts/send" in html_out:
        raise SystemExit("send API leaked into html")
    if html_out.count("?v=2924"):
        raise SystemExit("stale v=2924 left in html")

    # sanity
    articles = re.findall(r"<article class=\"card[^\"]*\">[\s\S]*?</article>", html_out)
    mailtos = []
    sent_with_mailto = []
    dnc_with_mailto = []
    emails_all = []
    for a in articles:
        ems = emails_in(a)
        if ems:
            emails_all.append(ems[0])
        has_mail = "mailto:" in a.lower()
        if has_mail and ems:
            mailtos.append(ems[0])
        chip = re.search(r'class="chip[^"]*">([^<]+)', a)
        label = chip.group(1) if chip else ""
        if "ALREADY SENT" in label and has_mail:
            sent_with_mailto.append(ems[0] if ems else title_of(a))
        if "DO NOT CONTACT" in label and has_mail:
            dnc_with_mailto.append(ems)
        if ems and ems[0] in SENT and has_mail and "SCHEDULED" not in label and "BOOKED" not in label:
            # waiting mailto to a sent address
            if "WAITING" in label or "NOT" in label:
                sent_with_mailto.append(ems[0])
    from collections import Counter
    dup_left = [e for e, n in Counter(emails_all).items() if n > 1 and "@" in e]
    if sent_with_mailto or dnc_with_mailto or dup_left:
        raise SystemExit(f"sanity fail sent_mailto={sent_with_mailto[:8]} dnc={dnc_with_mailto} dups={dup_left[:12]}")
    if "never auto-send" not in html_out.lower() and "NEVER AUTO-SEND" not in html_out:
        raise SystemExit("banner missing")
    if "bseptapres@gmail.com?subject" in html_out:
        raise SystemExit("Tabatha mailto still present")
    if "llicata@" in html_out.lower() and "mailto:llicata" in html_out.lower():
        raise SystemExit("Licata mailto still present")

    for p in (ROOT / "dunk-list.html", CRIT / "dunk-list.html"):
        p.write_text(html_out)

    # board json
    board = json.loads(BOARD.read_text())
    board["as_of"] = AS_OF
    board["board_version"] = BOARD_VER
    # dedupe rows by email, priority order
    pri = [
        "catch-all-chains", "owe", "quick_emails", "pto", "directors", "principals",
        "cdd", "not-emailed-amenity-oct-4", "university", "enterprise", "premium",
        "next40", "local_forms", "philanthropy_gm", "rcsa", "consumer", "other",
        "deprioritized-catholic-schools", "closed",
    ]
    order = {s.get("id"): i for i, s in enumerate(board["sections"])}
    def pri_key(sec):
        sid = sec.get("id") or ""
        return (pri.index(sid) if sid in pri else 50, order.get(sid, 99))
    board["sections"] = sorted(board["sections"], key=pri_key)
    seen_b = {}
    board_dupes = 0
    for sec in board["sections"]:
        kept = []
        for r in sec.get("rows") or []:
            em = (r.get("email") or "").strip().lower()
            if em and em in seen_b:
                board_dupes += 1
                continue
            if em:
                seen_b[em] = sec.get("id")
            if em in SENT:
                r["draft_status"] = "SENT"
                tags = [t for t in (r.get("chip_tags") or []) if "WAITING" not in t]
                d, sub = SENT[em]
                tags.append(f"ALREADY SENT {d}")
                r["chip_tags"] = tags
                r["sent_note"] = f"ALREADY SENT {d} — {sub}"
            if em in DNC_EMAILS or is_dnc(em, (r.get("contact") or "") + " " + (r.get("account") or "")):
                r["draft_status"] = "DO_NOT_CONTACT"
                r["chip_tags"] = ["DO NOT CONTACT", "No mailto"]
                r["why"] = (r.get("why") or "") + " DO NOT CONTACT. Off the active waiting stack."
            kept.append(r)
        sec["rows"] = kept

    # move licata rows to closed
    closed = next(s for s in board["sections"] if s.get("id") == "closed")
    for sec in board["sections"]:
        if sec.get("id") == "closed":
            continue
        stay = []
        for r in sec["rows"]:
            em = (r.get("email") or "").strip().lower()
            if em in DNC_EMAILS:
                r["lane"] = "closed"
                closed["rows"].append(r)
            else:
                stay.append(r)
        sec["rows"] = stay

    # add new rows into segment sections
    sec_by = {s.get("id"): s for s in board["sections"]}
    # ensure a v2925 net-new section group by appending rows onto existing sections
    target_id = {"schools": "directors", "senior": "directors", "hoa": "cdd", "corporate": "enterprise", "festivals": "directors", "planners": "enterprise"}
    for a in added:
        sid = target_id[a["segment"]]
        sec = sec_by[sid]
        sec["rows"].append({
            "id": "v2925-" + re.sub(r"[^a-z0-9]+", "-", a["email"].lower()).strip("-"),
            "account": a["org"],
            "contact": a["name"],
            "title": a["title"],
            "email": a["email"],
            "phone": a["phone"],
            "segment": a["segment"],
            "persona": "cdd" if a["segment"] == "hoa" else a["segment"],
            "kind": "mailto",
            "draft_status": "WAITING_SEND",
            "subject": a["subject"],
            "quick_body": a["body"],
            "why": "v2.9.25 net-new. Not on prior board. Not in Gmail Sent Oct 4 2026 evening ET. Mailto only.",
            "chip_tags": ["WAITING Send", "v2.9.25", "not in Sent"],
            "lead_source": a["file"],
        })

    # drop the temporary oct-4 section by merging remaining into cdd if not already moved
    new_sections = []
    for sec in board["sections"]:
        if sec.get("id") == "not-emailed-amenity-oct-4":
            # rows already deduped; append any left into cdd
            sec_by["cdd"]["rows"].extend(sec.get("rows") or [])
            continue
        new_sections.append(sec)
    board["sections"] = new_sections

    board["v2925"] = {
        "as_of": AS_OF,
        "hard_refresh": HARD,
        "no_outbound_send": True,
        "compose_only": True,
        "added_count": len(added),
        "dupes_removed_html": len(dupes_removed),
        "board_rows_deduped": board_dupes,
        "flipped_already_sent": [f for f in flipped if not f.get("dnc")],
        "dnc": [f for f in flipped if f.get("dnc")],
        "change": "Sent reconcile. Mailto removed where Sent has the address. Tabatha already sent after Sep 25. Lisa Licata off the stack. Dupes killed. Net-new mailto only.",
    }
    text = json.dumps(board, indent=2, ensure_ascii=False) + "\n"
    BOARD.write_text(text)
    shutil.copy2(BOARD, CRIT / "data" / "principal_dunk_board.json")

    waiting = 0
    for a in articles:
        if "mailto:" in a.lower() and "WAITING" in a:
            waiting += 1
    # recount from written html
    waiting = len(re.findall(r'class="chip wait"', html_out))

    summary = {
        "board_version": BOARD_VER,
        "as_of": AS_OF,
        "hard_refresh": HARD,
        "no_outbound_send": True,
        "compose_only": True,
        "banner": "DRAFTS / MAILTO ONLY — never auto-send",
        "added_count": len(added),
        "added": [{"name": a["name"], "email": a["email"], "org": a["org"], "segment": a["segment"]} for a in added],
        "dupes_removed": dupes_removed,
        "dupes_removed_count": len(dupes_removed),
        "flipped_already_sent": [f for f in flipped if not f.get("dnc")],
        "do_not_contact": [f for f in flipped if f.get("dnc")],
        "waiting_mailto_count": waiting,
        "skipped": skipped,
        "tabatha": {
            "email": "bseptapres@gmail.com",
            "stays_top": False,
            "reason": "Gmail Sent after Sep 25. Latest Oct 1, 2026 6:39 PM ET. Also Sep 30, 2026 4:20 PM ET. Mailto removed.",
        },
        "live_urls": [
            "https://code4crittersoncallapps.github.io/sheehan-exec-suite/dunk-list.html?v=2925",
            "https://code4crittersoncallapps.github.io/critters-on-call/exec/dunk-list.html?v=2925",
        ],
    }
    (ROOT / "data" / "_dunk_v2925_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    shutil.copy2(ROOT / "data" / "_dunk_v2925_summary.json", CRIT / "data" / "_dunk_v2925_summary.json")

    for p in (ROOT / "principal-dunk.html", CRIT / "principal-dunk.html"):
        if not p.exists():
            continue
        t = p.read_text()
        t = t.replace("?v=2924", HARD).replace("?v=2923", HARD).replace("?v=2922", HARD)
        p.write_text(t)

    print(json.dumps({
        "added": len(added),
        "dupes": len(dupes_removed),
        "flipped": len([f for f in flipped if not f.get("dnc")]),
        "dnc": len(dnc_cards),
        "waiting": waiting,
        "skipped": len(skipped),
        "board_dupes": board_dupes,
        "by_seg": {k: len(v) for k, v in buckets.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
