#!/usr/bin/env python3
"""dunk v2.9.22 — stage Jax media shout-out mailtos (Michael voice, no sig). Dedup Action News Sent."""
from __future__ import annotations

import json
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
import html as html_lib
import re

ROOT = Path("/workspace/sheehan-exec-suite")
CRIT = Path("/workspace/critters-on-call/exec")
BOARD = ROOT / "data" / "principal_dunk_board.json"
AS_OF = "2026-09-30T12:10:00-04:00"
AS_OF_LABEL = "Sep 30, 2026 ~12:10 PM ET"
BOARD_VER = "Board v2.9.22 · Sep 30, 2026 ~12:10 PM ET · Jax media shout-out WAITING Send (Action News Sent dedup)"
HARD = "?v=2922"

# Shared media links block (his DNN reel) — no signature
DNN_LINKS = """Here are our media appearances so far. They are all on the Daily News Network — they've been extremely kind to lend us a platform and we usually bring a fluffy or feathery critter :)

Voice of the Jags
https://dailynewsnetwork.com/2026/shows/finding-your-frequency/finding-your-frequency-with-michael-sheehan-of-sheehan-homestead-3/

Ann-Marie first solo
https://dailynewsnetwork.com/2026/shows/buzzworthy-businesses/buzzworthy-businesses-with-ann-marie-sheehan-of-sheehan-homestead-llc-dba-critters-on-call/

Our very first time a few years ago
https://dailynewsnetwork.com/2024/shows/jacksonville-buzz/the-jacksonville-buzz-with-michael-ann-marie-sheehan-of-sheehan-homestead-llc/

All appearances so far
https://dailynewsnetwork.com/?s=sheehan+homestead

Thank you in advance for your consideration — even a simple shout-out would help us reach more families and community organizations.
"""

CORE_ASK = """Would any of the following be possible?

- A social / on-air shout-out for a local educational agritourism business near the Callahan/Jax border
  * Trunk-or-Treat and Fall Festival season is way better with a petting zoo or goat yoga
  * Homeschool families work with us for STEM and farm-school enrichment
- A short feel-good segment with Ann-Marie, Michael, and maybe an animal (live, Zoom, or in-studio — whatever you do)
- Some other way you support emerging local businesses (we've been asked for articles / white papers elsewhere)

"""


def pitch(greeting: str, outlet_hook: str) -> str:
    return (
        f"{greeting}\n\n"
        f"{outlet_hook}\n\n"
        "We are an educationally focused homestead on the Callahan/Jax border — primarily known for "
        "mobile STEM on Call and Critters on Call, plus intimate farm tours and small field trips. "
        "A rising tide lifts all ships, and we're hoping for the same kind of local love you already "
        "give Northeast Florida businesses and agritourism.\n\n"
        f"{CORE_ASK}"
        f"{DNN_LINKS}"
    ).rstrip() + "\n"


# Bodies adapted from his Action News Sent voice — NO signature (dunk strip + rule)
PITCHES = {
    "quick-river-city-live": {
        "email": "newstips@wjxt.com",
        "alt_emails": ["newstips@news4jax.com", "producer@wjxt.com"],
        "subject": "Social shout-out / live animal demo — local edu-tainment homestead (Callahan)?",
        "contact": "River City Live / News Tips",
        "account": "News4JAX River City Live (WJXT)",
        "body": pitch(
            "Hi River City Live / News4JAX team,",
            "We follow News4JAX and love when you highlight local businesses and family destinations. "
            "River City Live's demo style is a perfect fit for what we do — goats on set, not a talking head.",
        ),
        "why": "WAITING homestead Send · same Action News shout-out pitch adapted for RCL demo lane. Primary also Help Desk ticket (River City Live). Also newstips@wjxt.com · producer@wjxt.com. Dedup: never Sent.",
        "website": "https://help.news4jax.com/kb/article/255-river-city-live-how-do-i-get-on-the-show/",
        "form_url": "https://help.news4jax.com/new/",
    },
    "quick-first-coast-news-tip": {
        "email": "news@firstcoastnews.com",
        "subject": "Social shout-out for local edu-tainment / agritourism biz (Callahan)?",
        "contact": "Newsroom",
        "account": "First Coast News (WTLV/WJXX)",
        "body": pitch(
            "Hi First Coast News team,",
            "We follow you on socials and notice you shout out a lot of local businesses — including some agritourism. "
            "It's awesome. We benefit second-hand as an educational homestead near the Callahan/Jax border.",
        ),
        "why": "WAITING homestead Send · Action News pitch adapted for FCN newsroom tip. Text tip also 904-633-8808. Do NOT treat First Coast Living Grow Your Business as free until confirmed unpaid. Never Sent.",
        "website": "https://www.firstcoastnews.com/contact-us",
    },
    "quick-action-news-events-calendar": {
        "email": "events@actionnewsjax.com",
        "subject": "Community calendar — Callahan farm / family animal events?",
        "contact": "Family Focus / Community Calendar",
        "account": "Action News Jax — Community Calendar",
        "body": (
            "Hi Family Focus / Community Calendar team,\n\n"
            "We just emailed news@ about a social shout-out. Separately — if you take public dated events for the "
            "community calendar, we'd love to list our next open farm morning / trunk-or-treat style family hit "
            "(Callahan / metro Jax · mobile petting zoo + STEM).\n\n"
            "Happy to send a short blurb + photo/flyer with date/time as soon as the next public date is locked.\n\n"
            "Website: https://www.sheehanhomestead.com/\n"
        ),
        "why": "WAITING homestead Send · calendar lane separate from news@ (already Sent Sep 30). Public dated events only + photo/flyer.",
        "website": "https://www.actionnewsjax.com/family-focus/community-calendar/",
    },
    "quick-wjct-first-coast-connect": {
        "email": "firstcoastconnect@wjct.org",
        "alt_emails": ["sbennett@wjct.org"],
        "subject": "First Coast Connect idea — Callahan farm animals + family STEM?",
        "contact": "Stacey Bennett / First Coast Connect",
        "account": "WJCT First Coast Connect",
        "body": pitch(
            "Hi Stacey,",
            "Pitching First Coast Connect with a civic/education frame (not a party-rental ad): "
            "Callahan homestead bringing farm animals + family STEM / ag literacy to metro Jax and Nassau.",
        ),
        "why": "WAITING homestead Send · named producer Stacey Bennett also sbennett@wjct.org. Civic frame. Show 9–10a · call-in 904-549-2937 during hour only. Never Sent.",
        "website": "https://news.wjct.org/shows/first-coast-connect",
    },
    "quick-folio-weekly": {
        "email": "team@folioweekly.com",
        "subject": "Farm / family scene — Callahan edu-tainment homestead shout?",
        "contact": "Events / Editorial",
        "account": "Folio Weekly",
        "body": pitch(
            "Hi Folio team,",
            "Soft ask for a Folio listing or short scene piece on a Callahan educational homestead that brings "
            "animals to Jax family events — not a coupon, just a local rising-tide shout.",
        ),
        "why": "WAITING homestead Send · also submit-event form. Allow 48 business hours. Never Sent.",
        "website": "https://folioweekly.com/all-events/submit-event/",
        "form_url": "https://folioweekly.com/all-events/submit-event/",
    },
    "quick-shop-the-904": {
        "email": "Shopthe904@cmg.com",
        "subject": "Shop the 904 open mic — Callahan farm / animals?",
        "contact": "Shop the 904 / CMG Jax",
        "account": "Shop the 904 (CMG Jax radio · WOKV cluster)",
        "body": (
            "Hi Shop the 904 team,\n\n"
            "We're a Callahan educational homestead (Critters on Call / STEM on Call) that brings animals to "
            "metro Jax festivals and family events. Soft ask for an open-mic / shout if there's a fit — "
            "happy to send a 10-second owner voice note (Michael founder and/or Ann-Marie mommy-and-me).\n\n"
            f"{DNN_LINKS}"
        ),
        "why": "WAITING homestead Send · WOKV/CMG open mic. 10-sec voice note via email or CMG Jax app. Never Sent.",
        "website": "https://www.wokv.com/events/shop-904/IERCM3DNMZFUJOPWHK6PW5UZQQ/",
    },
    "quick-jacksonville-today": {
        "email": "news@jaxtoday.org",
        "alt_emails": ["jessica@jaxtoday.org"],
        "subject": "Community tip — Callahan farm animals / family STEM?",
        "contact": "News / Tips",
        "account": "Jacksonville Today",
        "body": pitch(
            "Hi Jacksonville Today team,",
            "Soft community tip (not a business directory ad): Callahan educational homestead serving metro Jax "
            "families with animals + STEM — hoping for a newsletter shout if it fits.",
        ),
        "why": "WAITING homestead Send · tips news@jaxtoday.org; Perspectives jessica@jaxtoday.org. Never Sent.",
        "website": "https://jaxtoday.org/",
    },
    "quick-i-know-jax": {
        "email": "info@iknowjax.com",
        "alt_emails": ["joe@iknowjax.com"],
        "subject": "I Know Jax shout — Callahan farm morning / animals?",
        "contact": "Joe Talentino / I Know Jax",
        "account": "I Know Jax (CW17)",
        "body": pitch(
            "Hi Joe,",
            "Soft ask for an I Know Jax shout on a Callahan farm morning — we bring the animals for Jax families. "
            "Press-release / photos path (free). Happy to keep it short.",
        ),
        "why": "WAITING homestead Send · named Joe joe@iknowjax.com · 904-345-0755. Free press path only — skip paid story. Never Sent.",
        "website": "https://iknowjax.com/tvshow/",
    },
    "quick-jacksonville-mom": {
        "email": "info@jacksonvillemom.com",
        "subject": "Mommy-and-me farm morning — guest note / calendar?",
        "contact": "Editors",
        "account": "Jacksonville Mom",
        "body": (
            "Hi Jacksonville Mom editors,\n\n"
            "Ann-Marie and Michael Sheehan — educational homestead on the Callahan/Jax border. Soft ask for a "
            "guest note on what a Nassau mommy-and-me farm morning actually looks like (community story, not a sales post) "
            "and/or a calendar listing for our next public farm morning.\n\n"
            "Happy to draft a short blurb; farm URL belongs in the bio per your guest guidelines.\n\n"
            f"{DNN_LINKS}"
        ),
        "why": "WAITING homestead Send · best mommy-group collateral. Guest = story not sales. Calendar form linked. Never Sent.",
        "website": "https://jacksonvillemom.com/guest-blog-guidelines/",
        "form_url": "https://jacksonvillemom.com/calendar-events/community/add/",
    },
    "quick-the-coastal": {
        "email": "editor@thecoastal.com",
        "subject": "First Coast farm essay — Callahan edu-tainment homestead?",
        "contact": "Nathan Woods",
        "account": "The Coastal",
        "body": pitch(
            "Hi Nathan,",
            "Soft ask for a short original First Coast farm / family essay if there's a fit — "
            "we bring the animals for local events. Happy to draft 300+ words unpublished.",
        ),
        "why": "WAITING homestead Send · named editor Nathan Woods. Submit form also live. Never Sent.",
        "website": "https://thecoastal.com/contact-us/",
        "form_url": "https://thecoastal.com/submit-your-story/",
    },
    "quick-fernandina-observer": {
        "email": "hello@fernandinaobserver.org",
        "subject": "Nassau feature — Callahan educational homestead / animals?",
        "contact": "Publisher / Reader submissions",
        "account": "Fernandina Observer",
        "body": pitch(
            "Hi Fernandina Observer team,",
            "Hometown Nassau ask: short feature or shout for a Callahan educational homestead that brings "
            "animals to Nassau and metro Jax families.",
        ),
        "why": "WAITING homestead Send · Nassau hometown ink. Reader submissions form + publisher email. Never Sent.",
        "website": "https://www.fernandinaobserver.org/reader-submissions/",
        "form_url": "https://www.fernandinaobserver.org/reader-submissions/",
    },
    "quick-news-leader-fernandina": {
        "email": "tdishman@fbnewsleader.com",
        "subject": "Callahan farm feature — local edu-tainment / animals?",
        "contact": "Tracy Dishman",
        "account": "Fernandina Beach News-Leader",
        "body": pitch(
            "Hi Tracy,",
            "Soft ask for a local feature / shout — we bring the animals for Nassau and metro Jax families "
            "from an educational homestead on the Callahan border.",
        ),
        "why": "WAITING homestead Send · named editor Tracy Dishman · 904-261-3696. Never Sent.",
        "website": "https://www.fbnewsleader.com/local-regional-columns/letters-editor-policy",
    },
    "quick-jacksonville-magazine": {
        "email": "joe@jacksonvillemag.com",
        "subject": "Callahan farm feature — couple / small-biz homestead?",
        "contact": "Joe",
        "account": "Jacksonville Magazine",
        "body": pitch(
            "Hi Joe,",
            "Soft ask for a Magazine feature / shout on a Callahan farm family that brings animals to Jax events — "
            "momtrepreneur / small-biz couple frame. Happy to draft or sit for photos.",
        ),
        "why": "WAITING homestead Send · published pitch email joe@. Slow lead time. Never Sent.",
        "website": "https://www.jacksonvillemag.com/contact-us/careers/",
    },
}

# New Times-Union card (public exec editor email published on jacksonville.com about-us)
TIMES_UNION = {
    "id": "quick-times-union-tips",
    "account": "Florida Times-Union / jacksonville.com",
    "contact": "Paul Runnestrand (Executive Editor)",
    "title": "Executive Editor · public tip path",
    "email": "prunnestrand@jacksonville.com",
    "phone": "904-359-4598",
    "city": "Jacksonville",
    "segment": "Media / Community",
    "persona": "other",
    "kind": "mailto",
    "lane": "quick_emails",
    "quick_email": True,
    "bucket": "media_collab",
    "tier": "A",
    "legacy_tier": 1,
    "area": "Metro Jax · Jacksonville",
    "website": "https://www.jacksonville.com/contact/staff/",
    "subject": "Local tip — Callahan edu-tainment / agritourism homestead?",
    "quick_body": pitch(
        "Hi Paul,",
        "Reaching the Times-Union with a local community tip (Callahan / Nassau border educational homestead). "
        "No general tips@ is published; using your public executive-editor address from the about-us page. "
        "Happy to be routed to the right metro / features desk.",
    ),
    "why": "WAITING homestead Send · published prunnestrand@jacksonville.com (about-us). News tips phone 904-359-4598. letters@jacksonville.com is opinion-only — not used here. Never Sent. No invented tips@.",
    "owe_reason": "WAITING homestead Send · Times-Union media pitch staged Sep 30 · do not auto-send",
    "tags": ["media", "Times-Union", "WAITING Send", "Michael dunk"],
    "chip_tags": [
        "WAITING · Michael Send",
        "Media shout-out pitch",
        "Named EE public email",
        "Never Sent",
    ],
    "draft_status": "WAITING_ON_MICHAEL_SEND",
    "draft_surface": "mailto / homestead compose",
    "lead_source": "jacksonville.com about-us · public EE email",
    "lead_source_type": "public_directory",
    "lead_source_date": "2026-09-30",
}


def update_row(r: dict, spec: dict) -> dict:
    out = deepcopy(r)
    out["email"] = spec["email"]
    out["subject"] = spec["subject"]
    out["quick_body"] = spec["body"]
    out["why"] = spec["why"]
    out["owe_reason"] = "WAITING homestead Send · Jax media shout-out pitch staged Sep 30 · same Action News voice · no auto-send · dunk mailto no signature"
    out["draft_status"] = "WAITING_ON_MICHAEL_SEND"
    out["draft_surface"] = "mailto / homestead compose"
    out["kind"] = "mailto"
    out["quick_email"] = True
    if spec.get("contact"):
        out["contact"] = spec["contact"]
        out["title"] = spec["contact"]
    if spec.get("account"):
        out["account"] = spec["account"]
    if spec.get("website"):
        out["website"] = spec["website"]
    if spec.get("form_url"):
        out["form_url"] = spec["form_url"]
    tags = list(out.get("tags") or [])
    for t in ["media", "WAITING Send", "Michael dunk", "shout-out pitch"]:
        if t not in tags:
            tags.append(t)
    out["tags"] = tags
    out["chip_tags"] = [
        "WAITING · Michael Send",
        "Media shout-out pitch",
        "Action News voice adapted",
        "Never Sent",
        "No signature",
    ]
    if spec.get("alt_emails"):
        out["board_note"] = "Also: " + " · ".join(spec["alt_emails"])
    return out


def mark_action_news_sent(r: dict) -> dict:
    out = deepcopy(r)
    out["subject"] = "Social Shout Out for Local Eduatainment/Agritourism Biz?"
    # Keep his Sent body as archive reference (no sig needed for Sent card — no re-send)
    out["quick_body"] = (
        "Hi there,\n"
        "We follow you on socials, especially with our Facebook\n"
        "https://www.facebook.com/sheehan.homestead and have noticed you shout out\n"
        "a lot of local businesses and even some local agritourism businesses.\n"
        "It's awesome that you do that. We definitely benefit second hand because\n"
        "we are an educationally focused homestead that is located near the\n"
        "Callahan/Jax border. Some of the other businesses we've seen you shout out\n"
        "share key words and are close to us geographically, so we know that \"a\n"
        "rising tide lifts all ships.\" We are primarily known for our mobile STEM\n"
        "on Call and Critters on Call offerings, however we also accommodate\n"
        "intimate farm tours and small field trips.\n\n"
        "Would it be possible to do any of the following?\n\n"
        "- Receive the same kind of shout out on your socials to support a local\n"
        "educational business\n"
        "* Trunk or Treat and Fall Festival Season events are way better with a\n"
        "petting zoo or goat yoga\n"
        "* Homeschool families work with us for STEM and farm school enrichment\n"
        "* Happy to offer other details\n\n"
        "- We would be happy to do a feel good segment with Ann-Marie, Michael, and\n"
        "maybe an animal by either zoom or in studio if you do that kind of feel\n"
        "good segment?\n\n"
        "- Some other way we haven't thought of that you support local businesses\n"
        "that are still emerging. We've been asked to contribute articles and white\n"
        "papers as an example, but I'm not sure if that's something you guys do.\n\n"
        "Here are our media appearances so far. They are all on the Daily News\n"
        "Network. They've been extremely kind to lend us a platform and I think\n"
        "they appreciate that we usually bring a fluffy or feathery critter :)\n\n"
        "Voice of the Jags\n"
        "https://dailynewsnetwork.com/2026/shows/finding-your-frequency/finding-your-frequency-with-michael-sheehan-of-sheehan-homestead-3/\n"
        "AM first time solo\n"
        "https://dailynewsnetwork.com/2026/shows/buzzworthy-businesses/buzzworthy-businesses-with-ann-marie-sheehan-of-sheehan-homestead-llc-dba-critters-on-call/\n"
        "Our very first time a few years ago\n"
        "https://dailynewsnetwork.com/2024/shows/jacksonville-buzz/the-jacksonville-buzz-with-michael-ann-marie-sheehan-of-sheehan-homestead-llc/\n"
        "All 8 appearances so far https://dailynewsnetwork.com/?s=sheehan+homestead\n\n"
        "Thank you in advance for your consideration as we believe even a simple\n"
        "shout out would enhance our reach and ability to serve families and\n"
        "community organizations.\n"
    )
    out["why"] = (
        "SENT Sep 30, 2026 9:50 AM ET · Gmail to news@actionnewsjax.com · subject "
        "\"Social Shout Out for Local Eduatainment/Agritourism Biz?\" · no re-send. "
        "Calendar lane events@ still WAITING."
    )
    out["owe_reason"] = "ALREADY SENT Sep 30 9:50 AM ET · do not re-send news@"
    out["chip_tags"] = [
        "SENT Sep 30 9:50 AM ET",
        "news@actionnewsjax.com",
        "No re-send",
        "Calendar events@ still open",
    ]
    out["draft_status"] = "SENT"
    out["draft_surface"] = "Gmail Sent"
    out["lead_source"] = "Gmail Sent Sep 30"
    out["lead_source_type"] = "sent"
    out["lead_source_date"] = "2026-09-30"
    out["tags"] = ["media", "SENT", "Action News", "dedup"]
    return out


def mailto_href(email: str, subject: str, body: str) -> str:
    return (
        "mailto:"
        + email
        + "?subject="
        + quote(subject, safe="")
        + "&body="
        + quote(body, safe="")
    )


def dunk_list_media_section(board: dict) -> str:
    sec = next(s for s in board["sections"] if s.get("id") == "media" or s.get("title", "").startswith("Media"))
    cards = []
    # WAITING first, then SENT Action News as reference
    order = [
        "quick-river-city-live",
        "quick-first-coast-news-tip",
        "quick-action-news-events-calendar",
        "quick-wjct-first-coast-connect",
        "quick-folio-weekly",
        "quick-shop-the-904",
        "quick-jacksonville-today",
        "quick-i-know-jax",
        "quick-jacksonville-mom",
        "quick-the-coastal",
        "quick-times-union-tips",
        "quick-fernandina-observer",
        "quick-news-leader-fernandina",
        "quick-jacksonville-magazine",
        "quick-action-news-jax-shoutout",
        "quick-buzz-dnn-interview",
    ]
    by_id = {r["id"]: r for r in sec["rows"]}
    for rid in order:
        r = by_id.get(rid)
        if not r:
            continue
        email = r.get("email") or ""
        subj = r.get("subject") or ""
        body = r.get("quick_body") or ""
        sent = (r.get("draft_status") == "SENT") or any("SENT" in t for t in (r.get("chip_tags") or []))
        kind = r.get("kind")
        if kind == "form" or not email:
            chip = '<span class="chip form">FORM</span>'
            links = f'<a class="btn" href="{html_lib.escape(r.get("form_url") or r.get("website") or "#")}" target="_blank" rel="noopener">Open form</a>'
        elif sent:
            chip = '<span class="chip sent">ALREADY SENT</span>'
            links = f'<a class="btn" href="{mailto_href(email, subj, body)}">Open mailto (archive)</a>'
        else:
            chip = '<span class="chip wait">WAITING Send</span>'
            links = f'<a class="btn" href="{mailto_href(email, subj, body)}">Open mailto</a>'
        name = html_lib.escape(r.get("account") or rid)
        meta_bits = []
        if email:
            meta_bits.append(f"<b>{html_lib.escape(email)}</b>")
        if r.get("contact"):
            meta_bits.append(html_lib.escape(r["contact"]))
        if r.get("phone"):
            meta_bits.append(html_lib.escape(r["phone"]))
        meta = " · ".join(meta_bits)
        why = html_lib.escape((r.get("why") or "")[:280])
        cards.append(
            f'''<article class="card top">
  <h3>{chip} {name}</h3>
  <div class="meta">{meta}</div>
  <div class="why">{why}</div>
  <div class="links">{links}</div>
</article>'''
        )
    head = (
        '<div class="sec">Jax media shout-out · WAITING homestead Send (Action News news@ SENT)</div>\n'
        '<div class="why"><b>Same pitch voice as Action News Sent</b> · adapted per outlet · '
        "<b>dunk mailto no signature</b> · compose only · never auto-send · Mayo/corporate NOT in this lane. "
        "Dedup: news@actionnewsjax.com Sent Sep 30 9:50 AM ET.</div>\n"
    )
    return head + "\n\n".join(cards) + "\n\n"


def patch_dunk_list(path: Path, section_html: str) -> None:
    s = path.read_text()
    # bump version refs
    s = s.replace("?v=2921", "?v=2922")
    s = s.replace("v=2921", "v=2922")
    # remove prior media section if we inserted one before
    s = re.sub(
        r'<div class="sec">Jax media shout-out · WAITING homestead Send[\s\S]*?(?=<div class="sec">)',
        "",
        s,
        count=1,
    )
    marker = '<div class="sec">Top dunks · shamebusters (WAITING Send unless noted)</div>'
    if marker not in s:
        raise SystemExit(f"marker missing in {path}")
    s = s.replace(marker, section_html + marker, 1)
    path.write_text(s)


def main() -> None:
    board = json.loads(BOARD.read_text())
    updated_ids = []
    added_ids = []

    # Update media section + owe Action News
    for si, sec in enumerate(board["sections"]):
        rows = sec.get("rows") or []
        new_rows = []
        for r in rows:
            rid = r.get("id")
            if rid in ("owe-action-news-jax-shoutout", "quick-action-news-jax-shoutout"):
                new_rows.append(mark_action_news_sent(r))
                updated_ids.append(rid)
            elif rid in PITCHES:
                new_rows.append(update_row(r, PITCHES[rid]))
                updated_ids.append(rid)
            else:
                new_rows.append(r)
        # Insert Times-Union into Media section after Folio if missing
        if sec.get("title", "").startswith("Media") or sec.get("id") == "media":
            ids = {r.get("id") for r in new_rows}
            if "quick-times-union-tips" not in ids:
                # place after folio
                placed = False
                out = []
                for r in new_rows:
                    out.append(r)
                    if r.get("id") == "quick-folio-weekly":
                        out.append(TIMES_UNION)
                        placed = True
                if not placed:
                    out.insert(0, TIMES_UNION)
                new_rows = out
                added_ids.append("quick-times-union-tips")
            # refresh Buzz form why (house account — form not mailto)
            for i, r in enumerate(new_rows):
                if r.get("id") == "quick-buzz-dnn-interview":
                    rr = deepcopy(r)
                    rr["why"] = (
                        "House network — already booked often. Use interview FORM (not mailto). "
                        "Book more: Buzz, Around Town, Buzzworthy; Ann-Marie Ask the Educator. "
                        "Paste short animal/STEM ask into form notes. Not a cold first pitch."
                    )
                    rr["chip_tags"] = ["FORM", "House account", "Book more segments"]
                    rr["draft_status"] = "FORM_PATH"
                    new_rows[i] = rr
                    updated_ids.append(rr["id"])
        board["sections"][si]["rows"] = new_rows

    board["board_version"] = BOARD_VER
    board["as_of"] = AS_OF
    board["v2922"] = {
        "as_of": AS_OF,
        "hard_refresh": HARD,
        "change": (
            "Jax media shout-out WAITING Send staged (Action News voice adapted, no signature). "
            "Dedup: news@actionnewsjax.com SENT Sep 30 9:50 AM ET. "
            "Added Times-Union prunnestrand@. Mayo/corporate NOT added."
        ),
        "added": added_ids,
        "updated": sorted(set(updated_ids)),
        "no_outbound_send": True,
        "staged_waiting_mailto": [
            PITCHES[k]["email"] for k in PITCHES if k != "quick-action-news-jax-shoutout"
        ]
        + [TIMES_UNION["email"]],
        "sent_dedup": ["news@actionnewsjax.com"],
    }

    # write board both mirrors
    BOARD.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n")
    crit_board = CRIT / "data" / "principal_dunk_board.json"
    shutil.copy2(BOARD, crit_board)

    # dunk-list both mirrors
    section = dunk_list_media_section(board)
    for p in (ROOT / "dunk-list.html", CRIT / "dunk-list.html"):
        patch_dunk_list(p, section)

    # principal-dunk hard-refresh stamp both mirrors
    for p in (ROOT / "principal-dunk.html", CRIT / "principal-dunk.html"):
        t = p.read_text()
        t = t.replace("?v=2921", "?v=2922")
        t = t.replace("Hard-refresh (?v=2921)", "Hard-refresh (?v=2922)")
        t = t.replace("Hard-refresh (?v=2920)", "Hard-refresh (?v=2922)")
        p.write_text(t)

    summary = {
        "board_version": BOARD_VER,
        "as_of": AS_OF_LABEL,
        "hard_refresh": HARD,
        "added_count": len(added_ids),
        "updated": sorted(set(updated_ids)),
        "added": added_ids,
        "sent_dedup": ["news@actionnewsjax.com · Sep 30 9:50 AM ET"],
        "no_outbound_send": True,
        "live_urls": [
            f"https://onchainoffgrid-hub.github.io/sheehan-exec-suite/dunk-list.html{HARD}",
            f"https://onchainoffgrid-hub.github.io/critters-on-call/exec/dunk-list.html{HARD}",
            f"https://onchainoffgrid-hub.github.io/sheehan-exec-suite/principal-dunk.html{HARD}",
            f"https://onchainoffgrid-hub.github.io/critters-on-call/exec/principal-dunk.html{HARD}",
        ],
        "delta": (
            "Media WAITING mailtos use Action News Sent voice adapted per outlet; "
            "dunk mailto no signature; Action News news@ marked SENT; Times-Union added; "
            "Mayo/corporate excluded from dunk."
        ),
    }
    (ROOT / "data" / "_dunk_v2922_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    shutil.copy2(ROOT / "data" / "_dunk_v2922_summary.json", CRIT / "data" / "_dunk_v2922_summary.json")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
