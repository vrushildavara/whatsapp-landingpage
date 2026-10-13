"""Builds the static SEO pages (industry pages, language pages, comparison posts).

    python tools/build_pages.py

Each page lives in PAGES below as plain data; the HTML shell (head, nav, footer,
JSON-LD) is shared so every page stays consistent. Output is plain static HTML
next to the existing site, exactly like the hand-written blog posts. Re-run
after editing any page's data. Claim rules: see README "Claims and wording"
(no prices, no reply-time numbers, only Hindi / Gujarati / English).
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://web.wogent.in"
TODAY = "2026-10-13"


def esc(s):
    return html.escape(s, quote=True)


def fonts_block():
    """The self-hosted @font-face <style> block, copied from index.html."""
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    m = re.search(r"<style>\s*/\* Inter and Space Grotesk are variable fonts[\s\S]*?</style>", src)
    return m.group(0)


ICONS = """<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
<meta name="theme-color" content="#2f8f5b" />"""

NAV = """<nav class="nav">
  <div class="container">
    <a href="/" class="nav-brand">
      <span class="nav-mark">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M4 18V7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H9l-5 4Z" fill="#fff"/>
          <g fill="#267a4c"><circle cx="9.5" cy="10.5" r="1.3"/><circle cx="14.5" cy="10.5" r="1.3"/></g>
        </svg>
      </span>
      <span>Wo<span class="brand-ai">gent</span></span>
    </a>
    <ul class="nav-links">
      <li><a href="/#how-it-works">How it works</a></li>
      <li><a href="/#capabilities">What it does</a></li>
      <li><a href="/#demos">See it in action</a></li>
      <li><a href="/blog/">Blog</a></li>
    </ul>
    <div class="nav-actions">
      <a href="/#overview" class="btn btn-primary btn-sm">Book a demo</a>
    </div>
  </div>
</nav>"""

# Shared with index.html and the blog via tools/patch note in README.
SOLUTIONS = [
    ("/whatsapp-ai-agent-for-retail-shops/", "Retail shops"),
    ("/whatsapp-ai-agent-for-clinics/", "Clinics"),
    ("/whatsapp-ai-agent-for-real-estate/", "Real estate"),
    ("/whatsapp-ai-agent-for-restaurants/", "Restaurants"),
    ("/whatsapp-ai-agent-for-coaching-institutes/", "Coaching institutes"),
    ("/whatsapp-ai-agent-gujarati/", "In Gujarati"),
    ("/whatsapp-ai-agent-hindi/", "In Hindi"),
]


def solutions_nav():
    items = "\n".join(f'        <li><a href="{u}">{esc(t)}</a></li>' for u, t in SOLUTIONS)
    return f"""    <nav class="footer-solutions" aria-label="WhatsApp AI agent by industry and language">
      <span class="footer-solutions-label">WhatsApp AI agent for</span>
      <ul>
{items}
      </ul>
    </nav>"""


def footer():
    return f"""<footer id="footer">
  <div class="container">
{solutions_nav()}
    <div class="footer-bottom">
      <span class="footer-brand">Wo<span class="brand-ai">gent</span></span>
      <ul class="footer-links">
        <li><a href="/#how-it-works">How it works</a></li>
        <li><a href="/#capabilities">What it does</a></li>
        <li><a href="/#faq">FAQ</a></li>
        <li><a href="/blog/">Blog</a></li>
        <li><a href="mailto:wogent7@gmail.com">Contact</a></li>
      </ul>
      <span class="footer-copyright">© 2026 Wogent. All rights reserved.</span>
    </div>
  </div>
</footer>"""


ORG = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "Wogent", "url": f"{SITE}/",
       "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo-512.png", "width": 512, "height": 512}}


def chat_html(chat):
    """chat = {"title": ..., "caption": ..., "messages": [(side, text, time), ...]}"""
    rows = []
    for m in chat["messages"]:
        if m[0] == "chip":
            rows.append(f'<span class="chat-chip">{esc(m[1])}</span>')
            continue
        side, text, time = m
        ticks = ' <b aria-hidden="true">✓✓</b>' if side == "out" else ""
        who = "Customer" if side == "in" else "Wogent agent"
        rows.append(f'<div class="chat-msg chat-{side}"><span class="sr-only">{who}: </span>{esc(text)}'
                    f'<time>{esc(time)}{ticks}</time></div>')
    cap = f'<figcaption>{esc(chat["caption"])}</figcaption>' if chat.get("caption") else ""
    head = f'<div class="chat-head"><span class="chat-avatar" aria-hidden="true">{esc(chat["title"][:2].upper())}</span>{esc(chat["title"])}</div>'
    return f'<figure class="chat-sample">{head}<div class="chat-feed">{"".join(rows)}</div>{cap}</figure>'


def faq_html(faq):
    items = "\n".join(
        f'        <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
    return f"""      <h2 id="faq">Frequently asked questions</h2>
      <div class="faq-list">
{items}
      </div>"""


def render_block(b):
    kind = b[0]
    if kind == "p":
        return f"      <p>{b[1]}</p>"
    if kind == "h2":
        return f"      <h2>{esc(b[1])}</h2>"
    if kind == "h3":
        return f"      <h3>{esc(b[1])}</h3>"
    if kind == "ul":
        return "      <ul>\n" + "\n".join(f"        <li>{x}</li>" for x in b[1]) + "\n      </ul>"
    if kind == "ol":
        return "      <ol>\n" + "\n".join(f"        <li>{x}</li>" for x in b[1]) + "\n      </ol>"
    if kind == "chat":
        return "      " + chat_html(b[1])
    if kind == "callout":
        return f'      <p class="callout">{b[1]}</p>'
    if kind == "table":
        head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in b[1][0])
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in b[1][1:])
        return f'      <div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    raise ValueError(kind)


STEPS = [("h2", "How it works"),
         ("ol", ["<strong>Connect your WhatsApp number.</strong> Your existing number, connected through Meta's official WhatsApp Cloud API.",
                 "<strong>Send us what you already have.</strong> Catalog, price list, brochure, menu or fee sheet. A PDF is fine.",
                 "<strong>The agent takes the chats.</strong> We test it on real conversations first. Then it answers day and night, and your team steps in only when needed."])]


def page(p):
    url = f"{SITE}{p['path']}"
    is_post = p["path"].startswith("/blog/")
    crumbs = [("Home", f"{SITE}/")] + ([("Blog", f"{SITE}/blog/")] if is_post else []) + [(p["crumb"], url)]
    graph = [
        {"@type": "BlogPosting" if is_post else "WebPage", "@id": f"{url}#main",
         **({"headline": p["h1"]} if is_post else {"name": p["title"]}),
         "description": p["description"], "url": url, "inLanguage": "en-IN",
         "datePublished": p.get("published", TODAY), "dateModified": TODAY,
         "image": f"{SITE}/assets/og-image.jpg",
         "author": {"@type": "Organization", "name": "Wogent Team", "url": f"{SITE}/"},
         "publisher": {"@id": f"{SITE}/#organization"},
         "mainEntityOfPage": url,
         **({"isPartOf": {"@id": f"{SITE}/blog/#blog"}} if is_post else
            {"isPartOf": {"@id": f"{SITE}/#website"},
             "about": {"@type": "Service", "name": p["service"], "serviceType": "WhatsApp AI agent",
                       "provider": {"@id": f"{SITE}/#organization"}, "areaServed": "IN",
                       **({"audience": {"@type": "BusinessAudience", "audienceType": p["audience"]}} if p.get("audience") else {}),
                       "availableLanguage": ["hi", "gu", "en"]}})},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]},
        ORG,
    ]
    if p.get("faq"):
        graph.append({"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    depth = p["path"].strip("/").count("/") + 1
    up = "../" * depth
    crumb_html = "\n".join(
        (f'        <li><a href="{u.replace(SITE, "") or "/"}">{esc(n)}</a></li>' if i < len(crumbs) - 1
         else f'        <li aria-current="page">{esc(n)}</li>') for i, (n, u) in enumerate(crumbs))
    body = "\n\n".join(render_block(b) for b in p["body"])
    if p.get("steps", True) and not is_post:
        body += "\n\n" + "\n\n".join(render_block(b) for b in STEPS)
    if p.get("faq"):
        body += "\n\n" + faq_html(p["faq"])
    related = "\n".join(f'          <li><a href="{u}">{esc(t)}</a></li>' for u, t in p["related"])
    meta = (f'<time datetime="{p.get("published", TODAY)}">{p.get("published_label", "13 October 2026")}</time>'
            f'\n        <span>{p["read"]} min read</span>') if is_post else f'<span>Updated <time datetime="{TODAY}">13 October 2026</time></span>'

    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["description"])}" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<link rel="canonical" href="{url}" />
<link rel="alternate" hreflang="en-IN" href="{url}" />
<link rel="alternate" hreflang="x-default" href="{url}" />

<meta property="og:url" content="{url}" />
<meta property="og:type" content="{"article" if is_post else "website"}" />
<meta property="og:site_name" content="Wogent" />
<meta property="og:locale" content="en_IN" />
<meta property="og:title" content="{esc(p["og_title"])}" />
<meta property="og:description" content="{esc(p["description"])}" />
<meta property="og:image" content="{SITE}/assets/og-image.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Wogent: Not a chatbot. An AI agent for WhatsApp Business." />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(p["og_title"])}" />
<meta name="twitter:description" content="{esc(p["description"])}" />
<meta name="twitter:image" content="{SITE}/assets/og-image.jpg" />

<script type="application/ld+json">
{ld}
</script>

{ICONS}
{fonts_block()}
<link rel="stylesheet" href="{up}styles.css" />
<link rel="stylesheet" href="{up}blog/blog.css" />
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>

{NAV}

<main id="main">
  <div class="container article-container">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
{crumb_html}
      </ol>
    </nav>

    <header class="article-header">
      <span class="blog-tag">{esc(p["tag"])}</span>
      <h1>{esc(p["h1"])}</h1>
      <div class="article-meta">
        {meta}
      </div>
    </header>

    <div class="article-body">

      <p class="answer-first">{p["answer"]}</p>

{body}

      <div class="article-cta">
        <h3>{esc(p.get("cta_title", "See it answer your customers"))}</h3>
        <p>{esc(p.get("cta_text", "We'll demo the agent on a real conversation from your business, in Hindi, Gujarati or English. The demo is free."))}</p>
        <a href="/#overview" class="btn btn-primary">Book a free demo</a>
      </div>

      <section class="related-articles">
        <h2>Related</h2>
        <ul class="related-list">
{related}
        </ul>
      </section>

    </div>
  </div>
</main>

{footer()}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Page data
# --------------------------------------------------------------------------

REL_COMMON = [("/blog/whatsapp-ai-agent-vs-chatbot/", "WhatsApp AI agent vs chatbot: what is the difference?"),
              ("/blog/best-whatsapp-automation-for-indian-businesses/", "How to choose WhatsApp automation for an Indian business")]

FAQ_SAFE = ("Is my WhatsApp number safe?",
            "Yes. Wogent uses Meta's official WhatsApp Cloud API with your own business account, not unofficial automation tools. Your account still follows WhatsApp's Business and messaging policies.")
FAQ_COST = ("How much does it cost?",
            "A flat monthly plan based on your message volume and number of WhatsApp numbers. Book a free demo and we'll quote it.")
FAQ_TEAM = ("Can my staff still reply?",
            "Yes. Every chat is in a shared inbox. Anyone on your team can take over a conversation with one tap; the agent steps back until you hand it back.")

PAGES = [
    # ---------------------------------------------------------------- retail
    {
        "path": "/whatsapp-ai-agent-for-retail-shops/",
        "title": "WhatsApp AI Agent for Retail Shops in India | Wogent",
        "og_title": "WhatsApp AI agent for retail shops",
        "description": "A WhatsApp AI agent for Indian retail and wholesale shops: answers price and stock questions from your catalog, takes orders in the chat and follows up, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for retail shops",
        "crumb": "Retail shops", "tag": "Retail", "service": "WhatsApp AI agent for retail shops",
        "audience": "Retail and wholesale shops",
        "answer": "Wogent is a WhatsApp AI agent for Indian retail and wholesale shops. It answers price and stock questions from your own catalog, takes the order inside the chat and follows up when a customer goes quiet, 24/7, in Hindi, Gujarati or English, and it's set up for you on the official WhatsApp Cloud API.",
        "body": [
            ("h2", "The messages a shop gets all day"),
            ("ul", ["\"LED bulb stock ma che?\"", "\"Geyser 15L ni price su che?\"", "\"Where is my order?\"",
                    "A photo of a broken part with \"ye milega?\"", "\"Same as last time\" from a regular who ordered six weeks ago"]),
            ("p", "Most of these arrive while you're serving someone at the counter, after closing time, or on a Sunday. Each one you answer late is a sale that can go to the next shop."),
            ("chat", {"title": "Gada Electronics (demo)", "caption": "A sample chat in Gujarati-English. Demo data, not a real customer.",
                      "messages": [("in", "Geyser 15L ni price su che? Stock ma che?", "10:40 PM"),
                                   ("out", "Haan, 15L geyser stock ma che. Ketla joiye?", "10:40 PM"),
                                   ("in", "2 joiye. Kal delivery thase?", "10:41 PM"),
                                   ("out", "Done. 2 x Geyser 15L, order #GE1042 confirmed. Delivery kal thase.", "10:41 PM"),
                                   ("chip", "Order taken at 10:41 PM, nobody on duty")]}),
            ("h2", "What the agent does for a shop"),
            ("ul", ["<strong>Price and stock:</strong> answers from the catalog or price list you already have, fine print included.",
                    "<strong>Orders in the chat:</strong> quantity, price, confirmed. No forms, no app.",
                    "<strong>Photos:</strong> a customer sends a photo of a part; it identifies it, quotes the price and takes the order. It also reads payment screenshots and handwritten lists.",
                    "<strong>Order status:</strong> \"Where is my order?\" gets the live status from your system, not \"we'll get back to you\".",
                    "<strong>Follow-ups:</strong> if a customer asks a price and goes quiet, it sends a nudge after a delay you set and stops the moment they reply.",
                    "<strong>Festival offers:</strong> send a Diwali offer to your whole list with an approved template, and the agent answers every reply.",
                    "<strong>Your team stays in charge:</strong> an unusual request or an upset customer goes to your staff with the full chat already open."]),
        ],
        "faq": [("Can it answer from my price list PDF?", "Yes. Send us the catalog or price list you already use, even a PDF. The agent answers price, stock and product questions from it, including the fine print such as warranty."),
                ("Can customers order on WhatsApp without an app?", "Yes. The agent takes the order inside the WhatsApp chat: quantity, price and confirmation. There is no form or app for the customer to install."),
                ("Does it reply in Gujarati?", "Yes. It replies in Hindi, Gujarati or English, whichever the customer uses, even when they mix all three in one message."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-gujarati/", "WhatsApp AI agent that replies in Gujarati")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- clinics
    {
        "path": "/whatsapp-ai-agent-for-clinics/",
        "title": "WhatsApp AI Agent for Clinics: Book Appointments | Wogent",
        "og_title": "WhatsApp AI agent for clinics",
        "description": "A WhatsApp AI agent for Indian clinics and dental practices: books appointment slots, answers timing, fee and location questions, and hands patients to your staff, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for clinics",
        "crumb": "Clinics", "tag": "Clinics", "service": "WhatsApp AI agent for clinics",
        "audience": "Clinics, dental and physiotherapy practices",
        "answer": "Wogent is a WhatsApp AI agent for Indian clinics, dental and physiotherapy practices. It books appointment slots, answers questions about timings, consultation fees and location from your own information, and hands anything medical or unusual to your staff, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "Why clinics lose patients on WhatsApp"),
            ("p", "Patients message when they think of it: late at night, on Sundays, between their own work. The reception desk is busy with the patients in front of it. A slot question that waits until the next morning often becomes a booking somewhere else."),
            ("chat", {"title": "Smile Dental (demo)", "caption": "A sample booking chat. Demo data, not a real patient.",
                      "messages": [("in", "Tuesday 4 PM slot male?", "11:02 PM"),
                                   ("out", "Haan, Tuesday 4 PM available che. Tamaru naam ane kai treatment mate?", "11:02 PM"),
                                   ("in", "Priya Shah, cleaning", "11:03 PM"),
                                   ("out", "Booked: Priya Shah, Tuesday 4 PM, cleaning. Clinic location and parking info niche mokli che.", "11:03 PM"),
                                   ("chip", "Slot booked on a Sunday night")]}),
            ("h2", "What the agent does for a clinic"),
            ("ul", ["<strong>Appointments:</strong> offers open slots and books them in the chat.",
                    "<strong>Everyday questions:</strong> timings, consultation fees, doctors' days, location and parking, from the details you give us.",
                    "<strong>Your staff for anything clinical:</strong> symptoms, reports or an unhappy patient go straight to your team, with the full chat open in the shared inbox.",
                    "<strong>Follow-ups:</strong> a patient who asked and went quiet gets one polite nudge after a delay you set, and it stops the moment they reply.",
                    "<strong>Voice notes:</strong> many patients prefer to speak. The agent listens to voice notes and can reply with one in a natural Hindi or Hinglish voice.",
                    "<strong>Your number, your chats:</strong> conversations stay in your own WhatsApp Business account."]),
            ("callout", "<strong>The agent doesn't give medical advice.</strong> It handles bookings and practical questions, and passes anything about symptoms or treatment to your doctors and staff."),
        ],
        "faq": [("Can patients book appointments on WhatsApp?", "Yes. The agent offers available slots and confirms the booking inside the WhatsApp chat, day or night."),
                ("Will it answer medical questions?", "No. It answers practical questions such as timings, fees and location, and hands anything about symptoms, reports or treatment to your clinic staff with the chat already open."),
                ("Does it understand voice notes from patients?", "Yes. It listens to voice notes and can reply with a voice note of its own in a natural Hindi or Hinglish voice. Times and links follow as text."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-hindi/", "WhatsApp AI agent that replies in Hindi")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- real estate
    {
        "path": "/whatsapp-ai-agent-for-real-estate/",
        "title": "WhatsApp AI Agent for Real Estate Leads & Site Visits | Wogent",
        "og_title": "WhatsApp AI agent for real estate",
        "description": "A WhatsApp AI agent for Indian builders and brokers: answers property enquiries from your brochure, qualifies leads and books site visits 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for real estate",
        "crumb": "Real estate", "tag": "Real estate", "service": "WhatsApp AI agent for real estate",
        "audience": "Real estate builders, developers and brokers",
        "answer": "Wogent is a WhatsApp AI agent for Indian real estate builders and brokers. It answers property enquiries from your brochure, asks the questions your sales team would ask to qualify the lead, and books site visits, 24/7 in Hindi, Gujarati or English, with every chat visible to your team.",
        "body": [
            ("h2", "Property leads go cold fast"),
            ("p", "Ads and listing portals send enquiries at all hours. A buyer who asks \"2BHK still available?\" at 6 AM is usually asking three other projects the same thing. The first useful reply tends to get the site visit."),
            ("chat", {"title": "Skyline Residency (demo)", "caption": "A sample enquiry. Demo data, not a real buyer.",
                      "messages": [("in", "2BHK still available?", "6:15 AM"),
                                   ("out", "Yes, 2BHK units are available in Tower B. Are you looking to buy for yourself or as an investment?", "6:15 AM"),
                                   ("in", "Self use. Can I visit Saturday?", "6:16 AM"),
                                   ("out", "Saturday 11 AM site visit booked for you. Our sales team will meet you at the site office. Location pin below.", "6:16 AM"),
                                   ("chip", "Site visit booked at 6:16 AM")]}),
            ("h2", "What the agent does for builders and brokers"),
            ("ul", ["<strong>Answers from your brochure:</strong> configurations, amenities, location, possession timeline, whatever is in the material you share.",
                    "<strong>Qualifies the lead:</strong> budget, configuration, timeline and purpose, asked naturally in the chat.",
                    "<strong>Books site visits:</strong> offers a time and confirms it.",
                    "<strong>Hands hot leads to sales:</strong> your team takes over any chat with one tap and sees the whole conversation.",
                    "<strong>Follows up:</strong> a buyer who goes quiet gets a nudge after a delay you set, and it stops the moment they reply.",
                    "<strong>Launch broadcasts:</strong> send a new-project announcement with an approved template; the agent answers every reply."]),
        ],
        "faq": [("Can it qualify real estate leads on WhatsApp?", "Yes. It asks about budget, configuration, timeline and purpose in a natural conversation and passes qualified buyers to your sales team with the full chat."),
                ("Can it book site visits?", "Yes. It offers visit times and confirms the booking inside the WhatsApp chat."),
                ("What does it answer from?", "From the brochure, price sheet or project documents you share with us. If something isn't in your material, it brings in your team instead of guessing."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-gujarati/", "WhatsApp AI agent that replies in Gujarati")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- restaurants
    {
        "path": "/whatsapp-ai-agent-for-restaurants/",
        "title": "WhatsApp AI Agent for Restaurants & Cafes | Wogent",
        "og_title": "WhatsApp AI agent for restaurants",
        "description": "A WhatsApp AI agent for Indian restaurants, cafes and cloud kitchens: shares the menu, answers questions, books tables and takes orders in the chat, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for restaurants",
        "crumb": "Restaurants", "tag": "Restaurants", "service": "WhatsApp AI agent for restaurants",
        "audience": "Restaurants, cafes and cloud kitchens",
        "answer": "Wogent is a WhatsApp AI agent for Indian restaurants, cafes and cloud kitchens. It shares your menu, answers questions about dishes, timings and location, books tables and takes orders inside the WhatsApp chat, in Hindi, Gujarati or English, even during the dinner rush.",
        "body": [
            ("h2", "Your phone rings hardest when you're busiest"),
            ("p", "Table and order enquiries peak exactly when the kitchen and floor are full. Messages pile up, and a customer who doesn't hear back orders from someone else."),
            ("chat", {"title": "Spice Route Kitchen (demo)", "caption": "A sample booking chat. Demo data, not a real customer.",
                      "messages": [("in", "Aaj table milega 8 baje? 4 log", "6:48 PM"),
                                   ("out", "Haan, aaj 8 baje 4 logon ke liye table available hai. Naam bata dijiye?", "6:48 PM"),
                                   ("in", "Rahul K. Menu bhi bhejo", "6:49 PM"),
                                   ("out", "Table booked: Rahul K, 4 guests, 8 PM. Menu PDF neeche bhej diya hai.", "6:49 PM"),
                                   ("chip", "Table booked during the rush")]}),
            ("h2", "What the agent does for a restaurant"),
            ("ul", ["<strong>Menu and questions:</strong> answers from your menu: veg or Jain options, spice level, timings, location, parking.",
                    "<strong>Table bookings:</strong> offers a time and confirms it in the chat.",
                    "<strong>Orders:</strong> takes takeaway or delivery orders with items, quantity and confirmation. No form, no app.",
                    "<strong>Regulars:</strong> remembers returning customers, so \"same as last time\" works.",
                    "<strong>Offers:</strong> send a festival or weekend offer to your list with an approved template; the agent answers every reply.",
                    "<strong>Complaints go to you:</strong> an unhappy customer is handed to your team with the full chat open."]),
        ],
        "faq": [("Can customers book a table on WhatsApp?", "Yes. The agent offers a time, takes the name and number of guests, and confirms the booking in the chat."),
                ("Can it take food orders?", "Yes. It takes the order inside the WhatsApp chat with items, quantity and confirmation, from your own menu."),
                ("Does it remember regular customers?", "Yes. A returning customer is greeted by name, and \"same as last time\" just works."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-hindi/", "WhatsApp AI agent that replies in Hindi")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- coaching
    {
        "path": "/whatsapp-ai-agent-for-coaching-institutes/",
        "title": "WhatsApp AI Agent for Coaching Institutes & Schools | Wogent",
        "og_title": "WhatsApp AI agent for coaching institutes",
        "description": "A WhatsApp AI agent for Indian coaching institutes and training centres: answers fee, batch and syllabus questions, books demo classes and follows up with enquiries, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for coaching institutes",
        "crumb": "Coaching institutes", "tag": "Education", "service": "WhatsApp AI agent for coaching institutes",
        "audience": "Coaching institutes, tuition classes and training centres",
        "answer": "Wogent is a WhatsApp AI agent for Indian coaching institutes, tuition classes and training centres. It answers fee, batch timing and syllabus questions from your own brochure, books demo classes and follows up with students and parents who go quiet, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "Admission season means hundreds of the same questions"),
            ("p", "\"Fees kitni hai?\", \"Batch kab start?\", \"Weekend batch hai?\" Parents and students ask the same things again and again, often late in the evening. Each slow reply is an admission that may go to another institute."),
            ("chat", {"title": "Bright Future Classes (demo)", "caption": "A sample enquiry. Demo data, not a real student.",
                      "messages": [("in", "Class 10 maths ki fees kitni hai? Batch kab start?", "9:20 PM"),
                                   ("out", "Class 10 Maths ki fees aur batch details hamare brochure mein hain, neeche bhej rahe hain. Naya batch Monday se start ho raha hai. Kya aap free demo class attend karna chahenge?", "9:20 PM"),
                                   ("in", "Haan, Saturday?", "9:21 PM"),
                                   ("out", "Saturday 10 AM demo class booked. Address aur timing neeche hai.", "9:21 PM"),
                                   ("chip", "Demo class booked at 9:21 PM")]}),
            ("h2", "What the agent does for an institute"),
            ("ul", ["<strong>Fees, batches, syllabus:</strong> answered from your brochure or fee sheet.",
                    "<strong>Demo classes:</strong> offers a slot and books it in the chat.",
                    "<strong>Lead follow-ups:</strong> an enquiry that goes quiet gets a nudge after a delay you set, and it stops when they reply.",
                    "<strong>Parents and students:</strong> replies in Hindi, Gujarati or English, whichever they write in.",
                    "<strong>Announcements:</strong> send a new-batch or result announcement with an approved template; the agent answers every reply.",
                    "<strong>Your counsellors stay in charge:</strong> any chat can be taken over with one tap."]),
        ],
        "faq": [("Can it answer fee and batch questions on WhatsApp?", "Yes. It answers from the brochure, fee sheet or timetable you share with us, and brings in your team for anything it doesn't cover."),
                ("Can it book demo classes?", "Yes. It offers a time and confirms the demo class booking inside the chat."),
                ("Does it follow up with students who don't reply?", "Yes. After a delay you set it sends one nudge, within WhatsApp's template rules, and stops the moment they reply."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-hindi/", "WhatsApp AI agent that replies in Hindi")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- gujarati
    {
        "path": "/whatsapp-ai-agent-gujarati/",
        "title": "WhatsApp AI Agent in Gujarati for Businesses | Wogent",
        "og_title": "A WhatsApp AI agent that replies in Gujarati",
        "description": "Wogent is a WhatsApp AI agent that understands and replies in Gujarati, including Gujarati typed in English letters and Gujarati-Hindi-English mixed messages. Built for businesses in Gujarat and beyond.",
        "h1": "A WhatsApp AI agent that replies in Gujarati",
        "crumb": "In Gujarati", "tag": "Gujarati", "service": "Gujarati WhatsApp AI agent",
        "audience": "Gujarati-speaking businesses and their customers",
        "answer": "Wogent is a WhatsApp AI agent that understands and replies in Gujarati: in Gujarati script, in Gujarati typed with English letters (\"stock ma che?\"), and in messages that mix Gujarati, Hindi and English. It answers in whichever language the customer uses, takes orders and books appointments, and is set up for you on the official WhatsApp Cloud API.",
        "body": [
            ("h2", "Your customers don't write in textbook Gujarati"),
            ("p", "Real customer messages look like \"bhai LED bulb 9W wala che? 10 joiye che, price su che aapna\". Script-based chatbots break on messages like this. An AI agent reads what the customer means and answers it."),
            ("chat", {"title": "Patel Hardware (demo)", "caption": "Gujarati typed in English letters, the way most customers write. Demo data.",
                      "messages": [("in", "bhai LED bulb 9W wala che? 10 joiye che, price su che aapna", "8:05 PM"),
                                   ("out", "Haa, 9W LED bulb stock ma che. 10 bulb no total price niche mokli che. Order confirm karu?", "8:05 PM"),
                                   ("in", "haa karo", "8:06 PM"),
                                   ("out", "Order confirmed. Kale dukan par ready rahese.", "8:06 PM")]}),
            ("chat", {"title": "Patel Hardware (demo)", "caption": "The same kind of question in Gujarati script. Demo data.",
                      "messages": [("in", "આ પંખા માં રિમોટ આવે છે? વોરંટી કેટલી?", "9:12 PM"),
                                   ("out", "હા, આ પંખા સાથે રિમોટ આવે છે. વોરંટીની વિગત કેટલોગ મુજબ નીચે મોકલી છે.", "9:12 PM")]}),
            ("h2", "What \"replies in Gujarati\" means"),
            ("ul", ["<strong>Gujarati script</strong> (ગુજરાતી) and <strong>Gujarati in English letters</strong> are both understood.",
                    "<strong>Mixed messages</strong>, e.g. Gujarati with Hindi and English words, are normal and handled.",
                    "<strong>It follows the customer:</strong> it replies in the language they wrote in, and switches if they switch.",
                    "<strong>Your catalog can stay in English.</strong> The agent answers in Gujarati from an English price list or brochure.",
                    "<strong>Voice notes too:</strong> it listens to voice messages, and can reply with a voice note in Hindi or Hinglish."]),
            ("p", "Wogent supports three languages: Gujarati, Hindi and English. It's built for businesses in Ahmedabad, Surat, Rajkot, Vadodara and anywhere else customers write in Gujarati."),
        ],
        "faq": [("Does Wogent reply in Gujarati?", "Yes. It understands Gujarati in Gujarati script and in English letters, and replies in Gujarati when the customer writes in Gujarati."),
                ("Can it handle Gujarati, Hindi and English in one message?", "Yes. Mixed-language messages are normal for Indian customers. The agent understands them and replies in the customer's language."),
                ("Do I need my catalog in Gujarati?", "No. The agent can answer in Gujarati from a catalog or price list written in English."),
                ("Which languages does Wogent support?", "Gujarati, Hindi and English, including any mix of the three."),
                FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-hindi/", "WhatsApp AI agent that replies in Hindi"),
                    ("/whatsapp-ai-agent-for-retail-shops/", "WhatsApp AI agent for retail shops")] + REL_COMMON[:1],
    },
    # ---------------------------------------------------------------- hindi
    {
        "path": "/whatsapp-ai-agent-hindi/",
        "title": "WhatsApp AI Agent in Hindi: Replies in Hindi & Hinglish | Wogent",
        "og_title": "A WhatsApp AI agent that replies in Hindi",
        "description": "Wogent is a WhatsApp AI agent that understands and replies in Hindi and Hinglish, including Hindi typed in English letters, and can reply with a Hindi voice note. For Indian businesses selling on WhatsApp.",
        "h1": "A WhatsApp AI agent that replies in Hindi",
        "crumb": "In Hindi", "tag": "Hindi", "service": "Hindi WhatsApp AI agent",
        "audience": "Hindi-speaking businesses and their customers",
        "answer": "Wogent is a WhatsApp AI agent that understands and replies in Hindi: in Devanagari, in Hinglish typed with English letters (\"price kya hai?\"), and in messages that mix Hindi with English or Gujarati. It can also listen to voice notes and reply with a voice note in a natural Hindi or Hinglish voice.",
        "body": [
            ("h2", "Hindi on WhatsApp is mostly Hinglish"),
            ("p", "Most customers type Hindi in English letters, mix in English words and skip punctuation: \"bhaiya ye wala kitne ka hai, aaj deliver ho jayega?\". The agent reads messages the way a person at your counter would."),
            ("chat", {"title": "Sharma Mobiles (demo)", "caption": "Hinglish, the way most customers type. Demo data.",
                      "messages": [("in", "bhaiya ye cover kitne ka hai? aaj deliver ho jayega?", "7:32 PM"),
                                   ("out", "Is cover ka price aur photo neeche bhej diya hai. Haan, aaj shaam tak delivery ho jayegi. Order kar doon?", "7:32 PM"),
                                   ("in", "haan kar do, 2 piece", "7:33 PM"),
                                   ("out", "Done. 2 cover ka order confirm ho gaya.", "7:33 PM")]}),
            ("chat", {"title": "Sharma Mobiles (demo)", "caption": "Devanagari works the same way. Demo data.",
                      "messages": [("in", "दुकान रविवार को खुली है?", "10:15 AM"),
                                   ("out", "हाँ, रविवार को सुबह 10 से शाम 6 बजे तक दुकान खुली है।", "10:15 AM")]}),
            ("h2", "What \"replies in Hindi\" means"),
            ("ul", ["<strong>Devanagari and Hinglish</strong> are both understood.",
                    "<strong>Voice notes both ways:</strong> it listens to voice messages and can answer with a voice note in a natural Hindi or Hinglish voice, when the customer asks, when they sent one, or always. Prices, links and order numbers follow as text.",
                    "<strong>It follows the customer:</strong> Hindi in, Hindi out; English in, English out; mixed in, mixed out.",
                    "<strong>Your catalog can stay in English.</strong> The agent answers in Hindi from an English price list or brochure."]),
            ("p", "Wogent supports three languages: Hindi, Gujarati and English, including any mix of them."),
        ],
        "faq": [("Does Wogent reply in Hindi?", "Yes. It understands Hindi in Devanagari and in Hinglish, and replies in Hindi when the customer writes in Hindi."),
                ("Can it send voice notes in Hindi?", "Yes. It can reply with a WhatsApp voice note in a natural Hindi or Hinglish voice, when the customer asks, when they sent a voice note, or always, as you prefer."),
                ("Do I need my catalog in Hindi?", "No. The agent answers in Hindi from a catalog or price list written in English."),
                ("Which languages does Wogent support?", "Hindi, Gujarati and English, including any mix of the three."),
                FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-gujarati/", "WhatsApp AI agent that replies in Gujarati"),
                    ("/whatsapp-ai-agent-for-clinics/", "WhatsApp AI agent for clinics")] + REL_COMMON[:1],
    },
    # ---------------------------------------------------------------- buyer's guide
    {
        "path": "/blog/best-whatsapp-automation-for-indian-businesses/",
        "title": "How to Choose WhatsApp Automation in India (2026) | Wogent",
        "og_title": "How to choose WhatsApp automation for an Indian business",
        "description": "A practical 2026 checklist for Indian small businesses choosing WhatsApp automation: official API, managed vs DIY, Hindi and Gujarati support, human handoff, follow-ups and the questions to ask in a demo.",
        "h1": "How to choose WhatsApp automation for an Indian business: a 2026 checklist",
        "crumb": "Choosing WhatsApp automation", "tag": "Guide", "read": 8,
        "answer": "The best WhatsApp automation for an Indian small business runs on Meta's official WhatsApp Business API, understands the languages your customers actually write in (often Hindi, Gujarati and English mixed together), hands chats to your team cleanly, and is something you will realistically keep running. For most owners without a tech team, that last point decides between a self-serve platform and a managed service.",
        "body": [
            ("h2", "1. Is it on the official WhatsApp Business API?"),
            ("p", "Use a product built on Meta's official WhatsApp Business Platform (the Cloud API, or a Meta Business Solution Provider). Tools that automate the normal WhatsApp app with unofficial methods put your number at risk. Even on the official API, your account still has to follow WhatsApp's Business and messaging policies, so be wary of anyone promising \"no ban risk\" or \"unlimited free messages\"."),
            ("h2", "2. Does it understand how your customers really write?"),
            ("p", "Indian customers write \"stock ma che?\", \"price kya hai bhaiya\" and full Gujarati or Devanagari, often in the same chat. Ask the vendor to show a live reply to a messy, mixed-language message from your own business, not a scripted demo."),
            ("h2", "3. Chatbot flows or an AI agent?"),
            ("p", "A flow-based chatbot follows menus you design; it's predictable but breaks on anything off-script. An AI agent reads the message, works out what the customer needs and can act: check stock, take an order, book a slot. Many platforms now offer both. Read <a href=\"/blog/whatsapp-ai-agent-vs-chatbot/\">AI agent vs chatbot</a> for the difference in a real conversation."),
            ("h2", "4. Self-serve platform or managed service?"),
            ("p", "This is the decision that matters most for a small business."),
            ("ul", ["<strong>Self-serve platforms</strong> give you a dashboard, a no-code builder and usually a free trial. They're flexible and suit teams with someone who has time to set up flows, connect data and keep them updated.",
                    "<strong>Managed services</strong> set the agent up for you: connect the number, load your catalog, test on real conversations and maintain it. They suit owners who want the result without learning a tool."]),
            ("p", "Neither is better in general. Be honest about who in your business will own the setup three months from now."),
            ("h2", "5. Can your team take over instantly?"),
            ("p", "Look for a shared inbox where any staff member can take over a chat with one tap and see the full history, with roles so you control who can reply, who can only read and who manages settings."),
            ("h2", "6. Does it follow up, within the rules?"),
            ("p", "Customers who ask a price and go quiet are your easiest sales. Good automation sends a follow-up after a delay you choose, uses approved templates outside WhatsApp's 24-hour window, and stops the moment the customer replies."),
            ("h2", "7. Can it act, not just answer?"),
            ("ul", ["Take an order in the chat (quantity, price, confirmation)", "Book an appointment, table, demo class or site visit",
                    "Check live order status from your system", "Read photos, payment screenshots and voice notes"]),
            ("h2", "8. How is it priced?"),
            ("p", "Pricing models differ: per seat, per message, flat monthly, plus Meta's own per-conversation charges for template messages. Ask for the total monthly cost at your real message volume, including Meta's charges."),
            ("h2", "Questions to ask in any demo"),
            ("ol", ["Show me a reply to this exact message from one of my customers.", "What happens when it doesn't know the answer?",
                    "How does my staff take over a chat?", "Who sets it up, and who updates it when my prices change?",
                    "What will I pay per month at my message volume, including Meta's charges?"]),
            ("callout", "<strong>Where Wogent fits:</strong> Wogent is a managed WhatsApp AI agent for Indian SMBs on the official WhatsApp Cloud API. We set it up and test it for you, and it replies in Hindi, Gujarati and English. If you'd rather build and run flows yourself, a self-serve platform may suit you better."),
        ],
        "faq": [("What is the best WhatsApp automation for a small business in India?", "One that runs on Meta's official WhatsApp Business API, understands Hindi, Gujarati and English as your customers write them, lets your team take over chats, follows up within WhatsApp's rules, and that someone in your business will actually keep running. Owners without a tech team often do better with a managed service."),
                ("Is it safe to automate my WhatsApp number?", "It's safest on Meta's official WhatsApp Business Platform. Unofficial tools that automate the normal WhatsApp app put your number at risk. On the official API your account must still follow WhatsApp's policies."),
                ("Do I need a developer to set up WhatsApp automation?", "Not necessarily. Self-serve platforms offer no-code builders you set up yourself, and managed services such as Wogent set everything up for you.")],
        "related": [("/blog/whatsapp-ai-agent-vs-chatbot-builders/", "Managed WhatsApp AI agent vs DIY chatbot platforms"),
                    ("/blog/whatsapp-business-api-india/", "WhatsApp Business API in India: what it is and how to get it"),
                    ("/blog/whatsapp-ai-agent-vs-chatbot/", "WhatsApp AI agent vs chatbot: what is the difference?")],
    },
    # ---------------------------------------------------------------- comparison
    {
        "path": "/blog/whatsapp-ai-agent-vs-chatbot-builders/",
        "title": "Managed WhatsApp AI Agent vs WATI, Interakt, AiSensy | Wogent",
        "og_title": "Managed WhatsApp AI agent vs DIY chatbot platforms",
        "description": "WATI, Interakt and AiSensy are self-serve WhatsApp platforms; Wogent is a managed WhatsApp AI agent set up for you. A fair comparison of the two approaches for Indian businesses.",
        "h1": "Managed WhatsApp AI agent vs DIY platforms like WATI, Interakt and AiSensy",
        "crumb": "Managed vs DIY platforms", "tag": "Comparison", "read": 6,
        "answer": "WATI, Interakt and AiSensy are self-serve WhatsApp Business API platforms: you sign up, start a free trial and build chatbots and AI agents yourself in their tools. Wogent is a managed WhatsApp AI agent: the Wogent team connects your number, loads your catalog, tests the agent on real conversations and keeps it running, with a focus on Hindi, Gujarati and English. Which is better depends on whether you want to build it yourself or have it built for you.",
        "body": [
            ("h2", "What each one says it is"),
            ("p", "Based on each company's own website, checked on 13 October 2026:"),
            ("ul", ["<strong>WATI</strong> describes itself as an AI-powered customer engagement platform, offers a free trial, lists no-code chatbots, and promotes \"Astra\" AI agents. It shows an \"Official Meta Business Partner\" badge.",
                    "<strong>Interakt</strong> describes itself as \"a full-stack growth engine for marketing, sales, and support\" on the WhatsApp Business Platform, offers a free trial and a drag-and-drop no-code chatbot builder, and says you can deploy AI agents.",
                    "<strong>AiSensy</strong> describes itself as an AI-powered WhatsApp marketing platform and an official WhatsApp Business Solution Partner, offers a free trial and a free plan, and promotes no-code chatbots and AI agents.",
                    "<strong>Wogent</strong> is a managed WhatsApp AI agent for Indian SMBs, built on the official WhatsApp Cloud API and set up for you rather than DIY."]),
            ("p", "Features change often; check each vendor's site for the latest."),
            ("h2", "The real difference: who builds and runs it"),
            ("table", [["", "Self-serve platforms (WATI, Interakt, AiSensy)", "Managed agent (Wogent)"],
                       ["Getting started", "Sign up, free trial, set it up yourself", "Book a free demo; the Wogent team sets it up"],
                       ["Building the bot / agent", "You, with no-code builders and AI tools", "Done for you from your catalog, price list or brochure"],
                       ["Testing", "You test it", "Tested on real conversations before going live"],
                       ["When prices or stock change", "You update flows or data", "You send the new list; it's updated for you"],
                       ["Breadth", "Wide: campaigns, CRM-style tools, many integrations and channels", "Focused: customer chats, orders, bookings, follow-ups, broadcasts"],
                       ["Languages", "Varies by vendor", "Hindi, Gujarati and English, including mixed messages"],
                       ["Best for", "Teams with time and someone to own the setup", "Owners who want it working without learning a tool"]]),
            ("h2", "When a self-serve platform is the better choice"),
            ("ul", ["You have a marketing or ops person who enjoys building flows", "You need many channels or deep marketing automation",
                    "You want to start for free and experiment"]),
            ("h2", "When a managed AI agent is the better choice"),
            ("ul", ["Nobody on your team has time to build and maintain a bot",
                    "Your customers write in Hindi, Gujarati or a mix, and you want that handled well from day one",
                    "You want orders, bookings and follow-ups working, tested on your real chats, before you rely on it"]),
            ("callout", "<strong>Fair note:</strong> this page is written by Wogent. We've described other platforms only from their own public websites. If you find something out of date, write to wogent7@gmail.com and we'll correct it."),
        ],
        "faq": [("Is Wogent a WATI or AiSensy alternative?", "It's a different approach. WATI, Interakt and AiSensy are self-serve platforms you set up yourself. Wogent is a managed WhatsApp AI agent that the Wogent team sets up and maintains for you, focused on Hindi, Gujarati and English."),
                ("Do WATI, Interakt and AiSensy have AI agents?", "According to their own websites (checked 13 October 2026), all three promote AI agents or AI chatbots alongside no-code builders."),
                ("Which is better for a small shop with no tech team?", "Usually a managed service, because someone else does the setup, testing and updates. If you have time to build and maintain flows yourself, a self-serve platform can work well.")],
        "related": [("/blog/best-whatsapp-automation-for-indian-businesses/", "How to choose WhatsApp automation for an Indian business"),
                    ("/blog/whatsapp-ai-agent-vs-chatbot/", "WhatsApp AI agent vs chatbot: what is the difference?"),
                    ("/whatsapp-ai-agent-for-retail-shops/", "WhatsApp AI agent for retail shops")],
    },
]


def main():
    for p in PAGES:
        out = os.path.join(ROOT, p["path"].strip("/").replace("/", os.sep), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(page(p))
        print("wrote", p["path"])


if __name__ == "__main__":
    main()
