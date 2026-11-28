"""Builds the static SEO pages (industry pages, language pages, comparison posts).

    python tools/build_pages.py

Each page lives in PAGES below as plain data; the HTML shell (head, nav, footer,
JSON-LD) is shared so every page stays consistent. Output is plain static HTML
next to the existing site, exactly like the hand-written blog posts. Re-run
after editing any page's data. Claim rules: see README "Claims and wording"
(prices only as published in PRICING below, no reply-time numbers, only
Hindi / Gujarati / English).
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://web.wogent.in"
TODAY = "2026-10-13"  # default dates; a page sets "published"/"modified" when it is newer
MONTHS = "January February March April May June July August September October November December".split()


def date_label(d):
    return f"{int(d[8:])} {MONTHS[int(d[5:7]) - 1]} {d[:4]}"


def esc(s):
    return html.escape(s, quote=True)


def fonts_block():
    """The self-hosted @font-face <style> block, copied from index.html."""
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    m = re.search(r"<style>\s*/\* Inter and Space Grotesk are variable fonts[\s\S]*?</style>", src)
    return m.group(0)


ICONS = """<link rel="icon" href="/favicon.ico" sizes="any" />
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml" />
<link rel="icon" href="/assets/icon-192.png" type="image/png" sizes="192x192" />
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
      <li><a href="/pricing/">Pricing</a></li>
      <li><a href="/blog/">Blog</a></li>
    </ul>
    <div class="nav-actions">
      <a href="https://wogent.in/login" class="btn btn-ghost btn-sm nav-login">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="m10 17 5-5-5-5"/><path d="M15 12H3"/></svg>
        <span>Log in</span>
      </a>
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
    ("/whatsapp-ai-agent-for-salons/", "Salons"),
    ("/whatsapp-ai-agent-for-gyms/", "Gyms"),
    ("/whatsapp-ai-agent-for-travel-agents/", "Travel agents"),
    ("/whatsapp-ai-agent-for-online-stores/", "Online stores"),
    ("/whatsapp-ai-agent-gujarati/", "In Gujarati"),
    ("/whatsapp-ai-agent-hindi/", "In Hindi"),
    ("/whatsapp-ai-agent-surat/", "In Surat"),
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
        <li><a href="/pricing/">Pricing</a></li>
        <li><a href="/blog/">Blog</a></li>
        <li><a href="/privacy/">Privacy</a></li>
        <li><a href="/terms/">Terms</a></li>
        <li><a href="/refund-policy/">Refunds</a></li>
        <li><a href="/delivery-policy/">Delivery</a></li>
        <li><a href="https://wogent.in/login">Log in</a></li>
        <li><a href="/contact/">Contact</a></li>
      </ul>
      <span class="footer-copyright">© 2026 Wogent. All rights reserved.</span>
    </div>
  </div>
</footer>"""


ORG = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "Wogent", "url": f"{SITE}/",
       "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo-512.png", "width": 512, "height": 512},
       "address": {"@type": "PostalAddress", "addressLocality": "Surat", "addressRegion": "Gujarat", "postalCode": "395009", "addressCountry": "IN"}}


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
    published = p.get("published", TODAY)
    modified = p.get("modified", published)
    is_post = p["path"].startswith("/blog/")
    crumbs = [("Home", f"{SITE}/")] + ([("Blog", f"{SITE}/blog/")] if is_post else []) + [(p["crumb"], url)]
    graph = [
        {"@type": "BlogPosting" if is_post else "WebPage", "@id": f"{url}#main",
         **({"headline": p["h1"]} if is_post else {"name": p["title"]}),
         "description": p["description"], "url": url, "inLanguage": "en-IN",
         "datePublished": published, "dateModified": modified,
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
    meta = (f'<time datetime="{published}">{date_label(published)}</time>'
            f'\n        <span>{p["read"]} min read</span>') if is_post else f'<span>Updated <time datetime="{modified}">{date_label(modified)}</time></span>'

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
<!-- First-party analytics + Google Tag Manager (configure in /wo-track.js). -->
<script src="/wo-track.js" defer></script>
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
            "Pay as you go has no monthly fee (optional plans start at ₹999 a month with AI replies included). You recharge a prepaid wallet and pay per use: ₹0.80 per AI reply, 5 paise per utility template, "
            "10 paise on top of Meta's charge per marketing template, and human replies are free. New accounts get 2,000 free credits. "
            "Full rate card at web.wogent.in/pricing.")
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
            ("p", "Pricing models differ: per seat, per message, flat monthly, plus Meta's own per-message charges for template messages (and, from 1 October 2026, for service replies above 1,000 a month per number). Ask for the total monthly cost at your real message volume, including Meta's charges."),
            ("p", "Wogent's pay as you go has no monthly fee (optional plans start at ₹999 a month with AI replies included): you recharge a prepaid wallet and pay per use, ₹0.80 per AI reply and a few paise per template on top of Meta's charge. See the <a href=\"/pricing/\">rate card</a>."),
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
                       ["Getting started", "Sign up, free trial, set it up yourself", "Sign up with 2,000 free credits, or book a free demo and have the Wogent team set it up"],
                       ["Pricing", "Monthly plan plus per-message charges", "No monthly fee: prepaid wallet, pay per use (<a href=\"/pricing/\">rate card</a>)"],
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


# --------------------------------------------------------------------------
# Pricing page. These figures mirror the backend's src/app/common/pricing.py
# (whatsapp-agents) and api/chat.js ALLOWED_PRICE_FIGURES: change all three
# together. Meta's rates are its India list rates from 1 October 2026.
# --------------------------------------------------------------------------

SIGNUP_URL = "https://wogent.in/register"
PRICING_UPDATED = ("2026-11-20", "20 November 2026")

# (what, credits, rupees, Meta's own charge, note)
RATE_CARD = [
    ("AI reply", "16", "₹0.80", "Service message",
     "Every answer the agent writes, including AI-written follow-ups. Memory, documents, tools and stage tracking are included."),
    ("AI voice-note reply", "80", "₹4.00", "Service message",
     "A natural Hindi or Hinglish voice note, up to about 40 seconds (600 characters); longer answers go as text. Replaces the ₹0.80 text charge for that reply."),
    ("Reading a photo, voice note or document", "5", "₹0.25", "None",
     "When a customer sends a photo, payment screenshot, voice note or PDF and the agent reads it."),
    ("Emoji reaction by the agent", "1", "₹0.05", "Service message", ""),
    ("Automatic text follow-up", "1", "₹0.05", "Service message", "A fixed-text nudge you wrote, sent inside WhatsApp's 24-hour window."),
    ("Marketing template, text", "2", "₹0.10", "₹0.8631", "Broadcasts, offers, journeys. Charged per message sent."),
    ("Marketing template with image, video or document", "3", "₹0.15", "₹0.8631", ""),
    ("Utility template", "1", "₹0.05", "₹0.115", "Order updates, reminders, follow-ups outside 24 hours."),
    ("Authentication template (OTP)", "1", "₹0.05", "₹0.115", ""),
    ("Reply from your team in the inbox", "0", "Free", "Service message", "Your staff never cost credits."),
]

FREE_ITEMS = ["Replies from your team, and their reactions", "Incoming customer messages",
              "STOP and START confirmations", "Test conversations in sandbox mode",
              "Messages that fail to send", "Unlimited contacts"]

RECHARGE_PACKS = [("₹500", "10,000", "", "10,000"), ("₹2,000", "40,000", "+3%", "41,200"),
                  ("₹5,000", "1,00,000", "+5%", "1,05,000"), ("₹10,000", "2,00,000", "+7%", "2,14,000")]

CASHBACK = [("Bronze", "20,000", "₹1,000", "2%"), ("Silver", "1,00,000", "₹5,000", "4%"),
            ("Gold", "4,00,000", "₹20,000", "6%"), ("Platinum", "10,00,000", "₹50,000", "8%")]

ACHIEVEMENTS = [("Send your first broadcast", "200"), ("Put your first journey live", "200"),
                ("30 days with a green WhatsApp quality rating", "500"),
                ("₹10,000 of sales tracked from WhatsApp", "1,000"),
                ("₹1 lakh of sales tracked from WhatsApp", "5,000"),
                ("₹10 lakh of sales tracked from WhatsApp", "25,000")]

# (title, lines, Wogent total, Meta total, all-in)
EXAMPLES = [
    ("A small clinic",
     ["1,200 AI replies", "200 appointment reminders (utility)", "50 reports or photos read"],
     "₹982.50", "₹46.00", "₹1,028.50"),
    ("A busy retail shop",
     ["4,000 AI replies", "200 voice-note replies", "2,000 festival offers (marketing)"],
     "₹4,200.00", "₹2,094.20", "₹6,294.20"),
]

# Monthly and yearly plans (backend: pricing.PLANS). Prices before GST; yearly = 10 months.
# (code, name, for whom, monthly Rs, yearly Rs, yearly per month Rs, AI replies a month,
#  credits a month, highlights, popular)
PLANS = [
    ("payg", "Pay as you go", "Few chats, or just trying Wogent", "0", None, None, None, None,
     ["₹0.80 per AI reply from your wallet", "2 team logins, 1 WhatsApp number", "AI agent, shared inbox, knowledge base, broadcasts"], False),
    ("starter", "Starter", "Clinics, salons, coaches, small shops", "999", "9,990", "833", "1,500", "24,000",
     ["2 team logins, 1 WhatsApp number", "AI agent with knowledge search and human handover", "+5% bonus credits on every top-up"], False),
    ("growth", "Growth", "Online stores, D2C, real estate, education", "2,499", "24,990", "2,083", "4,000", "64,000",
     ["5 team logins, 2 WhatsApp numbers", "Journeys and button flows", "Shopify and Razorpay, with AI tools",
      "AI voice-note replies", "+10% bonus credits on every top-up"], True),
    ("pro", "Pro", "Busy brands and bigger teams", "5,999", "59,990", "4,999", "10,000", "1,60,000",
     ["10 team logins, 3 WhatsApp numbers", "Everything in Growth, unlimited live journeys", "Priority support",
      "+20% bonus credits on every top-up"], False),
]

PRICING_FAQ = [
    ("Do I need a monthly plan?",
     "No. Pay as you go has no monthly fee and no contract: you recharge the wallet when you want and pay only for what the agent does. If you use the agent every day, a plan is cheaper: Starter ₹999, Growth ₹2,499 or Pro ₹5,999 a month (2 months free if you pay yearly), each with AI replies included every month, more team logins and numbers, and bonus credits on top-ups. Growth adds journeys, Shopify and Razorpay, and AI voice-note replies."),
    ("What happens to unused plan credits?",
     "A plan's credits are for that month and don't carry over. Anything beyond them comes from your wallet, and credits you buy never expire."),
    ("Can I change or cancel a plan?",
     "Yes, from Plans & billing in the dashboard. An upgrade starts right away and the unused days of your old plan come back as credits. A downgrade or cancellation takes effect at the end of the period you paid for. Plans renew automatically by UPI Autopay or card."),
    ("What is a credit?",
     "1 credit is ₹0.05, so ₹100 buys 2,000 credits. Every action uses a whole number of credits, shown in the rate card."),
    ("Is GST included?",
     "No. 18% GST is added when you recharge. Credits and the rates on this page are before GST."),
    ("Who pays WhatsApp's charges?",
     "Meta bills its own message charges to the card on your WhatsApp Business Account. They never pass through your Wogent wallet. From 1 October 2026 Meta also charges ₹0.115 for each service reply (AI or human) above the first 1,000 a month per number."),
    ("What happens when my balance runs out?",
     "The AI agent stops replying and hands each new chat to your team, so no customer is left with a wrong or half answer. Broadcasts, journeys and follow-ups pause. Everything resumes the moment you recharge. You get a low-balance warning in the dashboard first."),
    ("Do credits expire?",
     "Credits you pay for never expire. Free trial credits last 14 days, and bonus and reward credits last 60 days. Credits that expire soonest are used first."),
    ("Do failed messages cost credits?",
     "No. A message that fails to send is not charged, and a template that WhatsApp reports as failed is credited back."),
    ("How do rewards work?",
     "Use more in a month and you get up to 8% of it back as credits on the 1st of the next month. You also earn one-time credits for milestones such as your first broadcast and for sales tracked from WhatsApp through Shopify or Razorpay."),
    ("Can you set it up for me?",
     "Yes. Done-for-you setup is optional: we connect your number, write the agent's instructions, load your catalog and test it on real chats. It is quoted after a free demo, usually ₹5,000 to ₹15,000 once, and is billed outside the wallet."),
    ("Can I pay by UPI?",
     "Yes. Recharges go through Razorpay: UPI, cards, net banking and wallets."),
]


def plans_html():
    """The plan cards with a Monthly / Yearly switch (a tiny inline script flips data-period)."""
    cards = []
    for code, name, who, monthly, yearly, yearly_pm, replies, credits, points, popular in PLANS:
        if code == "payg":
            price = '<span class="pr-plan-amt">₹0</span><span class="pr-plan-per">/month</span>'
            billed = '<span class="pr-plan-billed">No monthly fee. Recharge from ₹500.</span>'
            included = '<p class="pr-plan-inc"><b>Pay per use</b><span>From your wallet, no plan needed</span></p>'
        else:
            price = (f'<span class="pr-plan-amt" data-month="₹{monthly}" data-year="₹{yearly_pm}">₹{monthly}</span>'
                     '<span class="pr-plan-per">/month</span>')
            billed = (f'<span class="pr-plan-billed" data-month="Billed monthly" '
                      f'data-year="₹{yearly} billed yearly">Billed monthly</span>')
            included = (f'<p class="pr-plan-inc"><b>~{replies} AI replies</b>'
                        f'<span>a month included ({credits} credits)</span></p>')
        items = "".join(f"<li>{esc(x)}</li>" for x in points)
        badge = '<span class="pr-plan-badge">Most popular</span>' if popular else ""
        cards.append(f"""        <article class="pr-plan{' is-popular' if popular else ''}">
          {badge}<h3>{esc(name)}</h3>
          <p class="pr-plan-for">{esc(who)}</p>
          <p class="pr-plan-price">{price}</p>
          {billed}
          {included}
          <ul>{items}</ul>
          <a href="{SIGNUP_URL}" class="btn {'btn-primary' if popular else 'btn-ghost'}">{'Start free' if code == 'payg' else 'Choose ' + esc(name)}</a>
        </article>""")
    return "\n".join(cards)


def pricing_page():
    path = "/pricing/"
    url = f"{SITE}{path}"
    title = "Wogent Pricing: Pay per use or plans from ₹999 | WhatsApp AI agent"
    description = ("Wogent pricing: pay as you go with no monthly fee (₹0.80 per AI reply) or a plan from ₹999 a month with AI replies included. "
                   "a few paise per WhatsApp template on top of Meta's charge, and free replies from your team. 2,000 free credits to start.")
    graph = [
        {"@type": "WebPage", "@id": f"{url}#main", "name": title, "description": description, "url": url,
         "inLanguage": "en-IN", "dateModified": PRICING_UPDATED[0],
         "publisher": {"@id": f"{SITE}/#organization"}, "isPartOf": {"@id": f"{SITE}/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Pricing", "item": url}]},
        {"@type": "Product", "@id": f"{url}#ai-reply", "name": "Wogent AI reply on WhatsApp",
         "brand": {"@id": f"{SITE}/#organization"},
         "offers": {"@type": "Offer", "price": "0.80", "priceCurrency": "INR", "url": url,
                    "availability": "https://schema.org/InStock",
                    "description": "Per AI reply, from a prepaid wallet on pay as you go. Excludes 18% GST and Meta's own message charges."}},
        ORG,
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in PRICING_FAQ]},
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    def credits_cell(c):
        return '<span class="pr-free">Free</span>' if c == "0" else f'{c} <span class="pr-unit">cr</span>'

    rows = "\n".join(
        f'            <tr><th scope="row">{esc(what)}'
        + (f'<span class="pr-note">{esc(note)}</span>' if note else "")
        + f'</th><td class="pr-num">{credits_cell(cr)}</td><td class="pr-num pr-inr">{esc(inr)}</td>'
        f'<td class="pr-meta">{esc(meta)}</td></tr>'
        for what, cr, inr, meta, note in RATE_CARD)
    free = "\n".join(f"          <li>{esc(x)}</li>" for x in FREE_ITEMS)
    packs = "\n".join(
        f'          <li class="pr-pack{" is-best" if i == 2 else ""}"><span class="pr-pack-amt">{esc(a)}</span>'
        f'<span class="pr-pack-cr">{esc(total)} credits</span>'
        f'<span class="pr-pack-bonus">{esc(b + " bonus") if b else "No bonus"}</span></li>'
        for i, (a, _cr, b, total) in enumerate(RECHARGE_PACKS))
    tiers = "\n".join(
        f'            <tr><th scope="row">{esc(n)}</th><td class="pr-num">{esc(c)}</td><td class="pr-num">{esc(r)}</td>'
        f'<td class="pr-num pr-inr">{esc(p)}</td></tr>' for n, c, r, p in CASHBACK)
    ach = "\n".join(f'          <li><span>{esc(t)}</span><b>+{esc(c)} cr</b></li>' for t, c in ACHIEVEMENTS)
    examples = "\n".join(
        f"""        <article class="pr-example">
          <h3>{esc(t)}</h3>
          <ul>{"".join(f"<li>{esc(x)}</li>" for x in lines)}</ul>
          <dl>
            <div><dt>Wogent credits</dt><dd>{esc(w)}</dd></div>
            <div><dt>Meta's charges</dt><dd>{esc(m)}</dd></div>
            <div class="pr-total"><dt>Total for the month</dt><dd>{esc(total)}</dd></div>
          </dl>
        </article>""" for t, lines, w, m, total in EXAMPLES)
    faq = "\n".join(f'        <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in PRICING_FAQ)
    plans = plans_html()

    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<link rel="canonical" href="{url}" />
<link rel="alternate" hreflang="en-IN" href="{url}" />
<link rel="alternate" hreflang="x-default" href="{url}" />

<meta property="og:url" content="{url}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Wogent" />
<meta property="og:locale" content="en_IN" />
<meta property="og:title" content="Wogent pricing: pay per use or plans from ₹999" />
<meta property="og:description" content="{esc(description)}" />
<meta property="og:image" content="{SITE}/assets/og-image.jpg" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Wogent pricing: pay per use or plans from ₹999" />
<meta name="twitter:description" content="{esc(description)}" />
<meta name="twitter:image" content="{SITE}/assets/og-image.jpg" />

<script type="application/ld+json">
{ld}
</script>

{ICONS}
{fonts_block()}
<link rel="stylesheet" href="../styles.css" />
<link rel="stylesheet" href="../blog/blog.css" />
<link rel="stylesheet" href="pricing.css" />
<!-- First-party analytics + Google Tag Manager (configure in /wo-track.js). -->
<script src="/wo-track.js" defer></script>
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>

{NAV}

<main id="main" class="pr">
  <div class="container pr-container">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="/">Home</a></li>
        <li aria-current="page">Pricing</li>
      </ol>
    </nav>

    <header class="pr-hero">
      <span class="blog-tag">Pricing</span>
      <h1>Pay for what the agent does. Or pick a plan.</h1>
      <p class="pr-lede">Pay as you go with no monthly fee, or choose a plan with AI replies included every month. Each reply or message uses a few credits, and your team's replies are always free.</p>
      <div class="pr-hero-facts">
        <span><b>1 credit</b> = ₹0.05</span>
        <span><b>₹0.80</b> per AI reply</span>
        <span>Plans from <b>₹999</b>/month</span>
        <span><b>2,000</b> free credits to start</span>
      </div>
      <div class="pr-cta-row">
        <a href="{SIGNUP_URL}" class="btn btn-primary">Start free with 2,000 credits</a>
        <a href="/#overview" class="btn btn-ghost">Book a demo</a>
      </div>
      <p class="pr-small">Rates exclude 18% GST. Updated <time datetime="{PRICING_UPDATED[0]}">{PRICING_UPDATED[1]}</time>.</p>
    </header>

    <section class="pr-section" aria-labelledby="plans">
      <div class="pr-plans-head">
        <div>
          <h2 id="plans">Plans</h2>
          <p class="pr-section-lede">Pay as you go, or pick a plan with AI replies included every month. Cancel any time; a plan runs to the end of the period you paid for.</p>
        </div>
        <div class="pr-period" role="radiogroup" aria-label="Billing period">
          <button type="button" role="radio" aria-checked="true" data-period="month">Monthly</button>
          <button type="button" role="radio" aria-checked="false" data-period="year">Yearly <em>2 months free</em></button>
        </div>
      </div>
      <div class="pr-plans" data-period="month">
{plans}
      </div>
      <p class="pr-small"><strong>Enterprise:</strong> 50,000+ AI replies a month, unlimited team and numbers, custom AI tools and an account manager. <a href="mailto:wogent7@gmail.com?subject=Enterprise%20plan">Talk to us</a>. Plan credits renew every month and don't carry over; credits you buy never expire. Prices exclude 18% GST. UPI Autopay covers charges up to ₹15,000; yearly Growth and Pro are paid by card.</p>
      <script>
        (() => {{
          const grid = document.querySelector(".pr-plans");
          document.querySelectorAll(".pr-period [data-period]").forEach((button) => {{
            button.addEventListener("click", () => {{
              const period = button.dataset.period;
              grid.dataset.period = period;
              document.querySelectorAll(".pr-period [data-period]").forEach((b) => b.setAttribute("aria-checked", String(b === button)));
              grid.querySelectorAll("[data-month]").forEach((el) => {{ el.textContent = el.dataset[period]; }});
            }});
          }});
        }})();
      </script>
    </section>

    <section class="pr-section" aria-labelledby="rate-card">
      <h2 id="rate-card">Rate card</h2>
      <p class="pr-section-lede">What each action uses from your wallet. Meta's own charge for the same message is shown beside it; Meta bills that to your WhatsApp Business Account, not to Wogent.</p>
      <div class="table-wrap pr-table-wrap">
        <table class="pr-table">
          <thead><tr><th scope="col">Action</th><th scope="col">Credits</th><th scope="col">In ₹</th><th scope="col">Meta's charge (paid to Meta)</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
      <p class="pr-small"><strong>Service message:</strong> Meta's first 1,000 service messages per number each month are free, then ₹0.115 each (from 1 October 2026). Template rates are Meta's India rates; other countries differ.</p>
      <div class="pr-free-box">
        <h3>Never charged</h3>
        <ul>
{free}
        </ul>
      </div>
    </section>

    <section class="pr-section" aria-labelledby="examples">
      <h2 id="examples">What a month looks like</h2>
      <p class="pr-section-lede">Worked out from the rate card, before GST. Typical WhatsApp platforms charge ₹1,500 to ₹4,999 a month before a single message is sent.</p>
      <div class="pr-examples">
{examples}
      </div>
    </section>

    <section class="pr-section" aria-labelledby="recharge">
      <h2 id="recharge">Recharge</h2>
      <p class="pr-section-lede">Recharge from ₹500 by UPI, card or net banking. Bigger recharges add bonus credits.</p>
      <ul class="pr-packs">
{packs}
      </ul>
      <p class="pr-small">Paid credits never expire. Bonus credits last 60 days. GST is added at checkout.</p>
    </section>

    <section class="pr-section" aria-labelledby="rewards">
      <h2 id="rewards">Rewards</h2>
      <p class="pr-section-lede">The more your business sells on WhatsApp, the more comes back to you.</p>
      <div class="pr-rewards">
        <div>
          <h3>Monthly cashback</h3>
          <div class="table-wrap">
            <table class="pr-table pr-table-compact">
              <thead><tr><th scope="col">Level</th><th scope="col">Credits used / month</th><th scope="col">About</th><th scope="col">Cashback</th></tr></thead>
              <tbody>
{tiers}
              </tbody>
            </table>
          </div>
          <p class="pr-small">Paid on the 1st of the next month. Reward credits last 60 days.</p>
        </div>
        <div>
          <h3>Milestones</h3>
          <ul class="pr-milestones">
{ach}
          </ul>
          <p class="pr-small">Sales are tracked from Shopify and Razorpay orders that came through WhatsApp.</p>
        </div>
      </div>
    </section>

    <section class="pr-section pr-split" aria-labelledby="start">
      <div>
        <h2 id="start">Start free</h2>
        <p>Every new account gets <strong>1,000 credits</strong> on sign-up and <strong>1,000 more</strong> when you connect your WhatsApp number: about 125 AI replies to try it on real customers. Trial credits last 14 days, one trial per business.</p>
        <a href="{SIGNUP_URL}" class="btn btn-primary">Create your account</a>
      </div>
      <div>
        <h2>Or have it set up for you</h2>
        <p>Optional done-for-you setup: we connect your number, write the agent's instructions, load your catalog and test it on real chats. Usually <strong>₹5,000 to ₹15,000 once</strong>, quoted after a free demo and billed outside the wallet.</p>
        <a href="/#overview" class="btn btn-ghost">Book a free demo</a>
      </div>
    </section>

    <section class="pr-section" aria-labelledby="faq">
      <h2 id="faq">Pricing questions</h2>
      <div class="faq-list">
{faq}
      </div>
    </section>
  </div>
</main>

{footer()}
</body>
</html>
"""


# --------------------------------------------------------------------------
# Legal pages (privacy policy, terms). Same shell, no CTA or related links.
# Fill in the LEGAL details before publishing; the build warns while any is
# still a placeholder.
# --------------------------------------------------------------------------

LEGAL_UPDATED = ("2026-11-23", "23 November 2026")
LEGAL = {
    "entity": "Vrushilkumar Amitkumar Davra",
    "address": "Shop/Office No. 412, 4th Floor, Aadinath Arcade, Near LP Savani Circle, Beside Honey Park, Honey Park Road, Pankaj Nagar, Adajan, Surat, Gujarat 395009, India",
    "city": "Surat, Gujarat",
    "grievance_officer": "Vrushilkumar Amitkumar Davra",
    "email": "wogent7@gmail.com",
    "phone": "+91 79849 15842",
}


def _legal(key):
    v = LEGAL[key]
    return f"<mark>{esc(v)}</mark>" if v.startswith("[") else esc(v)


def legal_page(p):
    url = f"{SITE}{p['path']}"
    graph = [
        {"@type": "WebPage", "@id": f"{url}#main", "name": p["title"], "description": p["description"],
         "url": url, "inLanguage": "en-IN", "dateModified": LEGAL_UPDATED[0],
         "publisher": {"@id": f"{SITE}/#organization"}, "isPartOf": {"@id": f"{SITE}/#website"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": url}]},
        ORG,
    ]
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    body = "\n\n".join(render_block(b) for b in p["body"])
    # Linkable sections, e.g. /privacy/#stopping-whatsapp-messages-opt-out
    toc = []

    def anchor(m):
        slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(m.group(1)).lower()).strip("-")
        toc.append(f'          <li><a href="#{slug}">{m.group(1)}</a></li>')
        return f'<h2 id="{slug}">{m.group(1)}</h2>'
    body = re.sub(r"<h2>(.*?)</h2>", anchor, body)
    toc = "\n".join(toc)
    other = next(o for o in LEGAL_PAGES if o is not p)
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["description"])}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{url}" />

<meta property="og:url" content="{url}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Wogent" />
<meta property="og:locale" content="en_IN" />
<meta property="og:title" content="{esc(p["h1"])}" />
<meta property="og:description" content="{esc(p["description"])}" />
<meta property="og:image" content="{SITE}/assets/og-image.jpg" />

<script type="application/ld+json">
{ld}
</script>

{ICONS}
{fonts_block()}
<link rel="stylesheet" href="../styles.css" />
<link rel="stylesheet" href="../blog/blog.css" />
<!-- First-party analytics + Google Tag Manager (configure in /wo-track.js). -->
<script src="/wo-track.js" defer></script>
</head>
<body>
<a href="#main" class="skip-link">Skip to content</a>

{NAV}

<main id="main">
  <div class="container article-container">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <ol>
        <li><a href="/">Home</a></li>
        <li aria-current="page">{esc(p["crumb"])}</li>
      </ol>
    </nav>

    <header class="article-header">
      <span class="blog-tag">Legal</span>
      <h1>{esc(p["h1"])}</h1>
      <div class="article-meta">
        <span>Last updated <time datetime="{LEGAL_UPDATED[0]}">{LEGAL_UPDATED[1]}</time></span>
      </div>
    </header>

    <div class="article-body">

      <p class="answer-first">{p["answer"]}</p>

      <details class="legal-toc">
        <summary>On this page</summary>
        <ol>
{toc}
        </ol>
      </details>

{body}

      <aside class="legal-related">
        <span>Also read our <a href="{other["path"]}">{esc(other["crumb"])}</a></span>
        <span>Questions? Write to <a href="mailto:{LEGAL['email']}">{esc(LEGAL['email'])}</a></span>
      </aside>

    </div>
  </div>
</main>

{footer()}
</body>
</html>
"""


def _contact_block():
    trading = "" if LEGAL["entity"] == "Wogent" else ", trading as Wogent"
    return ("ul", [f"<strong>Operator:</strong> {_legal('entity')}{trading}",
                   f"<strong>Address:</strong> {_legal('address')}",
                   f"<strong>Phone / WhatsApp:</strong> <a href=\"tel:{LEGAL['phone'].replace(' ', '')}\">{esc(LEGAL['phone'])}</a>",
                   f"<strong>Email:</strong> <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a>"])


OPT_OUT_BLOCKS = [
    ("h2", "Stopping WhatsApp messages (opt-out)"),
    ("p", "If a business messages you on WhatsApp through Wogent and you no longer want its offers or updates, you can stop them at any time:"),
    ("ul", ["<strong>Reply STOP</strong> in the chat (or tap the <strong>Stop</strong> button where a message has one). The business is told and must stop sending you promotional messages.",
            "<strong>Use WhatsApp's own controls:</strong> you can stop marketing messages from a business, block it, or report it from the chat or the business's profile.",
            f"<strong>Write to us</strong> at <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a> with your WhatsApp number and the business's name, and we will pass the request on and record it."]),
    ("p", "To receive offers again later, reply <strong>START</strong> or message the business. Opting out of promotions does not stop replies to questions you send the business yourself, or messages it must send you about an order or booking you made."),
]

LEGAL_PAGES = [
    {
        "path": "/privacy/",
        "crumb": "Privacy Policy",
        "title": "Privacy Policy | Wogent",
        "description": "How Wogent collects, uses, shares and protects personal data on its website, its dashboard and the WhatsApp conversations it handles for businesses, and how to opt out of WhatsApp messages.",
        "h1": "Privacy Policy",
        "answer": "This policy explains what personal data Wogent handles, why, who it is shared with, and the choices you have, including how to stop WhatsApp messages from a business that uses Wogent. It applies to our website web.wogent.in, the Wogent dashboard, and the WhatsApp conversations we process for businesses.",
        "body": [
            ("h2", "Who we are"),
            ("p", "Wogent is a WhatsApp AI agent service for Indian businesses. It runs on Meta's official WhatsApp Business Platform (Cloud API). Wogent is operated by:"),
            _contact_block(),
            ("p", "Wogent is an independent service. It is not owned, operated or endorsed by Meta or WhatsApp."),

            ("h2", "Two roles we play"),
            ("ul", ["<strong>For our website visitors and our business customers' team members</strong>, we decide how your data is used, and we are responsible for it (a Data Fiduciary under India's Digital Personal Data Protection Act, 2023).",
                    "<strong>For people who chat with a business on WhatsApp</strong>, the business that uses Wogent decides how your data is used. We process it on that business's behalf and on its instructions. For questions about how a business uses your data, contact that business first; we will help it respond."]),

            ("h2", "What we collect"),
            ("h3", "When you visit our website"),
            ("ul", ["<strong>Demo request form:</strong> your name, WhatsApp number, business type, city and what you want to automate. We send it to our sales team's tools so we can contact you; it is not stored on the website server.",
                    "<strong>Website chat assistant:</strong> the questions you type, so an AI model can answer them. Please don't share sensitive personal information in this chat.",
                    "<strong>Usage data:</strong> pages viewed, device and browser type, approximate location and referral source, collected with Google Analytics using cookies. Your browser also keeps a small note so a pop-up isn't shown twice in one visit."]),
            ("h3", "When a business uses the Wogent dashboard"),
            ("ul", ["Account details for the business's team members: name, email address, password (stored only in hashed form), role and activity in the dashboard, such as who replied to which chat.",
                    "Business details: business name, WhatsApp Business Account and phone number identifiers, and the access permissions the business grants through Meta.",
                    "Content the business provides: agent instructions, documents such as catalogs, price lists or brochures, templates, contact lists and campaign settings.",
                    "Wallet and billing records: recharges, credits used per action, rewards, and the payment reference from our payment processor, Razorpay. Card, UPI and bank details are entered on Razorpay's checkout and never reach our servers."]),
            ("h3", "When you chat with a business that uses Wogent"),
            ("ul", ["Your WhatsApp phone number and profile name.",
                    "Messages you send and receive, including photos, documents, voice notes and their transcripts or descriptions.",
                    "Information that helps the business serve you: conversation summaries, the stage of your enquiry, notes the agent keeps to remember earlier conversations, orders or bookings, and labels or details the business adds.",
                    "Delivery information from WhatsApp, such as whether a message was delivered or read, and whether you have opted out."]),
            ("h3", "Connected stores and payments"),
            ("p", "If a business connects Shopify, we keep a copy of its product catalogue and, for checkouts, only the shopper's phone number and cart contents (to send cart reminders). Order details are fetched live and not stored. If a business connects Razorpay, we create payment links for the amount agreed in the chat. Store access tokens and payment keys are encrypted. Integration activity logs are deleted after 30 days, and we delete Shopify customer data when Shopify sends a deletion request or the store uninstalls the app."),

            ("h2", "How we use it"),
            ("ul", ["To run the service: receive and answer WhatsApp messages, hand chats to the business's staff, send broadcasts and follow-ups the business sets up, and show conversations in the dashboard.",
                    "To answer demo requests and support questions, and to send you service and account messages.",
                    "To keep the service secure and reliable: detect abuse, investigate problems and keep logs.",
                    "To meet legal obligations and Meta's WhatsApp policies.",
                    "To understand and improve our website, using aggregated analytics."]),
            ("p", "We do not sell personal data. We do not use one business's conversations to train AI models for other businesses."),

            ("h2", "AI processing"),
            ("p", "Wogent uses AI models to read incoming messages, understand photos and voice notes, search the business's documents, and write replies. These models are provided by third-party AI providers who process the data only to return a result to us. A business can take over any conversation, and the agent is set up to hand chats to a person when it can't help or when you ask for one. AI replies can be wrong; for anything important, confirm with the business."),

            ("h2", "Who we share it with"),
            ("ul", ["<strong>Meta (WhatsApp):</strong> to send and receive WhatsApp messages. Meta's own policies apply to WhatsApp.",
                    "<strong>Service providers</strong> who help us run Wogent, under contracts that limit their use of the data: cloud hosting, databases and file storage; AI model providers; email and team-notification tools; and website analytics.",
                    "<strong>The business you are chatting with,</strong> who can see your conversation in its dashboard, along with its authorised team members.",
                    "<strong>Authorities,</strong> when required by law or to protect rights, safety and security.",
                    "<strong>A buyer or successor,</strong> if Wogent's business is sold or merged, under the same protections."]),
            ("p", "Some of our providers store or process data outside India. When they do, we use providers with appropriate security commitments and follow any transfer restrictions under Indian law."),

            ("h2", "How long we keep it"),
            ("p", "We keep business account data and conversations while the business has a Wogent account, so the business can see its chat history. When a business closes its account or asks us to, we delete or anonymise its data within a reasonable period, except what we must keep for legal, tax, security or dispute reasons. Demo requests are kept as long as needed to follow up with you, and then deleted."),

            ("h2", "Security"),
            ("p", "We use encryption in transit (HTTPS), encrypt stored WhatsApp access credentials, verify that incoming WhatsApp events really come from Meta, keep each business's data separate, and limit dashboard access by role. No system is perfectly secure; if a breach affects your data, we will notify you and the authorities as the law requires."),
        ] + OPT_OUT_BLOCKS + [
            ("h2", "Your rights"),
            ("p", "Subject to applicable law, you can ask to access, correct, update or erase your personal data, withdraw consent you gave earlier, nominate someone to act for you, and raise a grievance. If you chatted with a business that uses Wogent, you can make these requests to that business or to us; we will work with the business to respond. We may need to verify your identity first."),

            ("h2", "Children"),
            ("p", "Wogent is a service for businesses and is not directed at children. We do not knowingly collect children's data for our own purposes. Businesses using Wogent are responsible for getting any consent the law requires for the people they message."),

            ("h2", "Grievance Officer"),
            ("p", f"For any privacy question, request or complaint, contact our Grievance Officer, {_legal('grievance_officer')}, at <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a>. We aim to acknowledge complaints promptly and resolve them within the time the law requires. If you are not satisfied, you may complain to the Data Protection Board of India."),

            ("h2", "Changes to this policy"),
            ("p", "We may update this policy as the service or the law changes. We will change the date at the top, and tell business customers about significant changes before they apply."),
        ],
    },
    {
        "path": "/terms/",
        "crumb": "Terms of Service",
        "title": "Terms of Service | Wogent",
        "description": "The terms for businesses using Wogent, the WhatsApp AI agent service: accounts, WhatsApp policies and consent, opt-outs, fees, AI limitations, data, availability and liability.",
        "h1": "Terms of Service",
        "answer": "These terms apply when a business signs up for or uses Wogent, the WhatsApp AI agent service. By using Wogent you agree to them on behalf of your business. If you are only chatting with a business on WhatsApp, see our <a href=\"/privacy/\">Privacy Policy</a> instead.",
        "body": [
            ("h2", "1. About these terms"),
            ("p", "\"Wogent\", \"we\" and \"us\" mean the operator named below. \"You\" means the business that uses Wogent and the people it authorises to use its account. If you have a signed order form or agreement with us, it takes priority over these terms where they differ."),
            _contact_block(),

            ("h2", "2. The service"),
            ("p", "Wogent connects your WhatsApp Business number, through Meta's official WhatsApp Business Platform, to an AI agent and a dashboard. It can answer customer messages, use your documents and connected tools, hand chats to your team, send template messages, broadcasts and follow-ups, and show your conversations in a shared inbox. Features may change as we improve the service."),
            ("p", "Wogent is an independent service and is not owned, operated or endorsed by Meta or WhatsApp. We will describe our relationship with Meta accurately, and only use partner titles Meta has actually given us."),

            ("h2", "3. Your account"),
            ("ul", ["You must be a business or professional, and the person accepting these terms must be authorised to bind it.",
                    "Give us accurate information and keep it up to date.",
                    "Keep your login details safe and use team roles to limit access. You are responsible for what happens under your account.",
                    "You own, or have permission to use, the WhatsApp Business Account and phone number you connect. You can disconnect it at any time."]),

            ("h2", "4. WhatsApp policies and consent"),
            ("p", "Your use of WhatsApp through Wogent is also governed by Meta's terms and policies, including the WhatsApp Business Terms of Service, the WhatsApp Business Messaging Policy and the WhatsApp Commerce Policy. You agree to follow them. In particular, you will:"),
            ("ul", ["Message people only when you have their phone number and their permission (opt-in) to receive messages from your business on WhatsApp, and keep a record of it. An uploaded contact list is not proof of permission.",
                    "Use approved message templates when the 24-hour customer service window has closed, and use the right template category (marketing, utility or authentication).",
                    "Not send spam or content that is illegal, misleading, harassing or harmful, and not use Wogent for products or services WhatsApp does not allow.",
                    "Give customers a clear way to reach a person, and not present the AI agent as a human when asked."]),
            ("p", "Meta reviews templates and monitors message quality. It may reject or pause templates, limit how many people you can message, or restrict your account. These decisions are Meta's, and we cannot guarantee any template will be approved."),

            ("h2", "5. Opt-outs (STOP)"),
            ("p", "When a customer replies STOP, asks you to stop messaging them, or uses WhatsApp's controls to stop your marketing messages, you must stop sending them promotional messages until they opt in again. Mark them as opted out in Wogent's contacts so they are left out of your campaigns, and do not send them promotions again without fresh permission. Our <a href=\"/privacy/#stopping-whatsapp-messages-opt-out\">Privacy Policy</a> explains to your customers how they can opt out."),

            ("h2", "6. Fees and WhatsApp charges"),
            ("ul", ["Wogent is prepaid. You recharge a wallet in Indian rupees and receive credits (1 credit = ₹0.05). GST is added at checkout. Each action uses the credits shown on our <a href=\"/pricing/\">pricing page</a> at the time it happens; we will give notice before raising a rate.",
                    "Paid credits do not expire. Free, bonus and reward credits expire on the date shown in your wallet (14 days for trial credits, 60 days for bonus and reward credits) and have no cash value.",
                    "Failed sends are not charged, and a template that WhatsApp reports as failed is credited back. Otherwise credits are not refundable or transferable, except where the law says so.",
                    "Plans (Starter, Growth, Pro) are optional monthly or yearly subscriptions, charged in advance by Razorpay autopay with GST added. Each plan includes credits every month, which expire at the end of that month. You can cancel any time; the plan then ends at the end of the period you paid for. See our <a href=\"/refund-policy/\">Refund and Cancellation Policy</a>.",
                    "When your balance runs out, the AI agent stops replying and hands chats to your team, and broadcasts, journeys and follow-ups pause until you recharge. Replies from your team are never charged.",
                    "Optional done-for-you setup is quoted and invoiced separately.",
                    "Meta charges separately for WhatsApp messages, by message category and country, under its own pricing, which can change. Meta bills these to the payment method on your own WhatsApp Business Account; they are not part of Wogent's credits."]),

            ("h2", "7. The AI agent"),
            ("p", "The agent writes replies with AI, based on your instructions, your documents and the conversation. AI can make mistakes, misunderstand a message or give incomplete answers. You are responsible for:"),
            ("ul", ["The instructions, documents, prices and information you give the agent, and keeping them accurate.",
                    "Reviewing how the agent behaves for your business, and taking over chats when needed.",
                    "Not letting the agent give medical, legal or financial advice, or make binding commitments, beyond what you have set up and checked."]),
            ("p", "You may not use Wogent to run a general-purpose AI assistant or chatbot service for the public. Wogent is for conversations about your own business."),

            ("h2", "8. Your data"),
            ("p", "You own your data, including your customers' conversations and contact lists. You give us permission to process it only to provide, secure and support the service, and as described in our <a href=\"/privacy/\">Privacy Policy</a>. For your customers' personal data we act on your behalf; you are responsible for having a lawful basis and giving any notices the law requires. When you leave, you can ask us to export your data, and we will then delete it as described in the Privacy Policy."),

            ("h2", "9. Acceptable use"),
            ("p", "You will not misuse the service: no attempts to break its security, access other businesses' data, overload it, reverse engineer it, resell it without our written permission, or use it to break any law or anyone's rights."),

            ("h2", "10. Availability and changes"),
            ("p", "We work to keep Wogent available and reliable, and to retry and recover messages when something fails. But the service depends on Meta, WhatsApp, internet and cloud providers outside our control, so we cannot promise it will be uninterrupted or error-free, or that every message will be delivered. We will tell you in advance about planned maintenance or major changes where we reasonably can."),

            ("h2", "11. Suspension and ending the service"),
            ("ul", ["You can stop using Wogent at any time. There is no contract or monthly fee to cancel.",
                    "We may suspend or end your access if you seriously or repeatedly break these terms or Meta's policies, if a payment is reversed, or if your use puts other businesses, Meta's platform or the law at risk. Where possible we will warn you first and give you a chance to fix the problem.",
                    "When the service ends, your WhatsApp number stays yours; you can disconnect it from Wogent and connect it elsewhere."]),

            ("h2", "12. Liability"),
            ("p", "To the extent the law allows: the service is provided on an \"as is\" and \"as available\" basis; neither party is liable for indirect or consequential losses, such as lost profits, business or data; and our total liability for any claim is limited to the amount you recharged with us in the three months before the claim arose. Nothing in these terms limits liability that cannot be limited by law."),
            ("p", "You will compensate us for claims made against us by third parties, including Meta or your customers, that arise from your content, your messages, or your breach of these terms or Meta's policies."),

            ("h2", "13. Changes to these terms"),
            ("p", "We may update these terms. We will change the date at the top and tell you about significant changes before they apply. If you keep using Wogent after that, the new terms apply."),

            ("h2", "14. Law and disputes"),
            ("p", f"These terms are governed by the laws of India. Courts in {_legal('city')} have exclusive jurisdiction. Before going to court, please write to us so we can try to resolve the issue."),

            ("h2", "15. Contact"),
            ("p", f"Questions about these terms: <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a>."),
        ],
    },
    {
        "path": "/refund-policy/",
        "crumb": "Refund and Cancellation Policy",
        "title": "Refund and Cancellation Policy | Wogent",
        "description": "How cancelling a Wogent plan works, when wallet credits and plan payments are refunded, and how long a refund takes.",
        "h1": "Refund and Cancellation Policy",
        "answer": "You can cancel a Wogent plan at any time, and it ends at the end of the period you already paid for. Payments for a period that has started and wallet credits are not refundable, except for failed sends, duplicate or wrong charges, and where the law requires. Approved refunds go back to your original payment method within 5 to 7 working days.",
        "body": [
            ("h2", "1. Cancelling a plan"),
            ("ul", ["You can cancel a monthly or yearly plan at any time from <strong>Plans and billing</strong> in your dashboard, or by writing to us.",
                    "Cancelling stops future renewals. Your plan and its features stay active until the end of the period you paid for; after that your workspace moves to pay as you go, and you can keep using any paid wallet credits.",
                    "We do not refund the rest of a period that has already started, whether monthly or yearly."]),
            ("h2", "2. Changing plans"),
            ("ul", ["<strong>Upgrading</strong> starts the higher plan at once. The unused part of your current paid period is added to your wallet as paid credits, which do not expire. It is not refunded in cash.",
                    "<strong>Downgrading</strong> or switching between monthly and yearly takes effect at the end of your current period; nothing is charged until then."]),
            ("h2", "3. Failed renewals"),
            ("p", "If a renewal payment fails, Razorpay retries it and your plan stays active for 3 more days. If it still has not been paid, your workspace moves to pay as you go. Nothing is charged for the time without a plan."),
            ("h2", "4. Wallet credits"),
            ("ul", ["Paid credits do not expire and can be used at any time while your account is open.",
                    "Credits for messages that fail to send are not charged, and a template that WhatsApp reports as failed is credited back automatically.",
                    "Otherwise, wallet recharges and the credits included with plans are not refundable or transferable, and bonus, trial and reward credits have no cash value."]),
            ("h2", "5. When we refund"),
            ("ul", ["You were charged twice for the same recharge or renewal, or charged an amount different from the one shown at checkout.",
                    "Money left your account but the payment failed, or the credits or plan you paid for were not added to your workspace and we could not fix it.",
                    "We end the service for a reason that is not your fault; we then refund any paid credits you have not used.",
                    "Any other case where the law requires a refund."]),
            ("h2", "6. How to ask for a refund"),
            ("p", f"Write to <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a> within 30 days of the payment, with your registered email, the payment date and amount, and the Razorpay payment ID or invoice number. We reply within 2 working days."),
            ("p", "Approved refunds are made to the original payment method through Razorpay within 5 to 7 working days. Your bank may take a few more days to show it."),
            ("h2", "7. Contact"),
            _contact_block(),
        ],
    },
    {
        "path": "/delivery-policy/",
        "crumb": "Shipping and Delivery Policy",
        "title": "Shipping and Delivery Policy | Wogent",
        "description": "Wogent is an online software service: nothing is shipped. How and when you get access, credits and plans after paying.",
        "h1": "Shipping and Delivery Policy",
        "answer": "Wogent is an online software service, so nothing is shipped. Your account is ready as soon as you sign up, and credits or a plan you pay for are added to your workspace as soon as Razorpay confirms the payment, usually within a minute.",
        "body": [
            ("h2", "1. What we deliver"),
            ("p", "Wogent is a WhatsApp AI agent and dashboard used in your web browser. We do not sell or ship physical goods, and there are no shipping charges."),
            ("h2", "2. When you get it"),
            ("ul", ["<strong>Your account:</strong> available straight after you sign up and verify your email.",
                    "<strong>Wallet credits:</strong> added to your workspace as soon as the payment is confirmed, usually within a minute.",
                    "<strong>Plans:</strong> active, with that month's included credits, as soon as the first payment is confirmed. Renewals are applied automatically on the renewal date.",
                    "<strong>Optional setup work</strong>, if you order it, is delivered online within the time agreed in your quote."]),
            ("h2", "3. If something has not arrived"),
            ("p", f"If credits or a plan you paid for are not in your workspace 24 hours after the payment, write to <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a> with the Razorpay payment ID. We will add them or refund the payment as described in our <a href=\"/refund-policy/\">Refund and Cancellation Policy</a>."),
            ("h2", "4. Contact"),
            _contact_block(),
        ],
    },
    {
        "path": "/contact/",
        "crumb": "Contact Us",
        "title": "Contact Us | Wogent",
        "description": "Contact Wogent: business address in Surat, phone and WhatsApp, and email for sales, support, billing and refunds.",
        "h1": "Contact Us",
        "answer": f"Write to <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a> or message us on WhatsApp at {esc(LEGAL['phone'])}. We reply within one working day, Monday to Saturday, 10 am to 7 pm IST.",
        "body": [
            ("h2", "Business details"),
            _contact_block(),
            ("h2", "Support and billing"),
            ("ul", [f"<strong>Product help, billing and refunds:</strong> <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a>. For a payment, include the Razorpay payment ID or invoice number.",
                    f"<strong>Sales and demos:</strong> <a href=\"https://wa.me/{LEGAL['phone'].replace(' ', '').lstrip('+')}\">WhatsApp {esc(LEGAL['phone'])}</a>.",
                    f"<strong>Privacy and grievances:</strong> our Grievance Officer, {_legal('grievance_officer')}, at <a href=\"mailto:{LEGAL['email']}\">{esc(LEGAL['email'])}</a>."]),
            ("h2", "Hours"),
            ("p", "Monday to Saturday, 10 am to 7 pm IST, except public holidays."),
        ],
    },
]


# --------------------------------------------------------------------------
# Pages added 16 November 2026: four more industries, the Surat page and three
# guides. Same copy rules as above: only features and prices the product has.
# --------------------------------------------------------------------------
NEW = "2026-11-16"

PAGES += [
    # ---------------------------------------------------------------- salons
    {
        "path": "/whatsapp-ai-agent-for-salons/", "published": NEW,
        "title": "WhatsApp AI Agent for Salons & Beauty Parlours | Wogent",
        "og_title": "WhatsApp AI agent for salons and beauty parlours",
        "description": "A WhatsApp AI agent for Indian salons, beauty parlours and spas: books appointments, answers price and package questions from your rate card and sends reminders, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for salons and beauty parlours",
        "crumb": "Salons", "tag": "Salons", "service": "WhatsApp AI agent for salons and beauty parlours",
        "audience": "Salons, beauty parlours and spas",
        "answer": "Wogent is a WhatsApp AI agent for Indian salons, beauty parlours and spas. It books appointments in the chat, answers price and package questions from your own rate card, sends reminders and brings back clients who have not visited for a while, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "Your hands are busy when the phone buzzes"),
            ("p", "A stylist in the middle of a haircut can't type a reply. Clients ask \"Sunday 5 baje slot hai?\" or \"bridal package ketla nu che?\" and wait. If the answer takes two hours, many of them have already booked the parlour down the road."),
            ("chat", {"title": "Glow Beauty Studio (demo)", "caption": "A sample booking chat. Demo data, not a real client.",
                      "messages": [("in", "Sunday 5 baje haircut aur facial ka slot hai?", "9:48 PM"),
                                   ("out", "Haan, Sunday 5 PM available hai. Haircut aur facial dono ke liye lagbhag 90 minute lagenge. Aapka naam?", "9:48 PM"),
                                   ("in", "Neha. Price kitna hoga?", "9:49 PM"),
                                   ("out", "Neha ji, dono services ka rate card neeche bhej rahi hoon. Sunday 5 PM aapke naam se book kar diya hai.", "9:49 PM"),
                                   ("chip", "Appointment booked after closing time")]}),
            ("h2", "What the agent does for a salon"),
            ("ul", ["<strong>Appointments:</strong> offers open slots and books them inside the chat.",
                    "<strong>Prices and packages:</strong> answers from the rate card you already have, including bridal and party packages.",
                    "<strong>Reminders:</strong> sends an appointment reminder with an approved template, so fewer clients forget.",
                    "<strong>Photos:</strong> a client sends a photo of the hairstyle or mehndi design she wants; the agent reads it and passes it to your stylist with the chat.",
                    "<strong>Clients who stopped coming:</strong> a win-back journey sends an offer to people who have gone quiet, and stops the moment they reply.",
                    "<strong>Festival and wedding-season offers:</strong> send one broadcast to your whole client list; the agent answers every reply.",
                    "<strong>Your staff stay in charge:</strong> anyone on the team can take over a chat with one tap."]),
        ],
        "faq": [("Can clients book a salon appointment on WhatsApp?", "Yes. The agent offers available slots and confirms the booking inside the WhatsApp chat, including late at night and on holidays."),
                ("Can it answer price questions from my rate card?", "Yes. Send us the rate card or package list you already use, even as a PDF or photo. The agent answers from it and brings in your staff for anything it doesn't cover."),
                ("Can it send appointment reminders?", "Yes. Reminders go out as approved WhatsApp utility templates, which cost 5 paise each on Wogent plus Meta's own charge."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-for-clinics/", "WhatsApp AI agent for clinics"),
                    ("/blog/whatsapp-broadcast-without-getting-banned/", "How to send WhatsApp broadcasts without risking your number")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- gyms
    {
        "path": "/whatsapp-ai-agent-for-gyms/", "published": NEW,
        "title": "WhatsApp AI Agent for Gyms & Fitness Studios | Wogent",
        "og_title": "WhatsApp AI agent for gyms and fitness studios",
        "description": "A WhatsApp AI agent for Indian gyms, yoga and fitness studios: answers membership fee and batch questions, books trial sessions and follows up on enquiries and renewals, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for gyms and fitness studios",
        "crumb": "Gyms", "tag": "Fitness", "service": "WhatsApp AI agent for gyms and fitness studios",
        "audience": "Gyms, yoga studios and fitness centres",
        "answer": "Wogent is a WhatsApp AI agent for Indian gyms, yoga studios and fitness centres. It answers membership fee, batch timing and trainer questions from your own fee sheet, books trial sessions, and follows up with enquiries and members whose plans are about to end, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "Most gym enquiries arrive when the desk is empty"),
            ("p", "People decide to join a gym late in the evening or early on a Monday morning. They message three gyms with \"monthly fees kitni hai?\" and usually visit whichever one answers first. A reply the next afternoon is often too late."),
            ("chat", {"title": "Iron Fit Gym (demo)", "caption": "A sample enquiry. Demo data, not a real member.",
                      "messages": [("in", "Monthly fees kitni hai? Morning batch hai?", "10:55 PM"),
                                   ("out", "Haan, morning batch 6 se 10 baje tak hai. Monthly, quarterly aur yearly plan ki fees neeche bhej raha hoon. Kya aap ek free trial session lena chahenge?", "10:55 PM"),
                                   ("in", "Haan kal subah 7 baje", "10:56 PM"),
                                   ("out", "Done. Kal subah 7 baje aapka trial session book ho gaya hai. Location neeche hai.", "10:56 PM"),
                                   ("chip", "Trial booked at 10:56 PM")]}),
            ("h2", "What the agent does for a gym"),
            ("ul", ["<strong>Fees and plans:</strong> monthly, quarterly and yearly prices answered from your fee sheet.",
                    "<strong>Batches and trainers:</strong> timings, personal training, yoga or zumba classes, whatever is in the details you give us.",
                    "<strong>Trial sessions:</strong> offers a time and books it in the chat.",
                    "<strong>Enquiry follow-ups:</strong> someone who asked the fees and went quiet gets a nudge after a delay you set, and it stops the moment they reply.",
                    "<strong>Renewals:</strong> send a reminder with an approved template before a plan ends, and the agent answers the replies.",
                    "<strong>Offers:</strong> send a New Year or summer offer to your whole list in one broadcast.",
                    "<strong>Your team stays in charge:</strong> any chat can be taken over with one tap."]),
        ],
        "faq": [("Can it answer membership fee questions on WhatsApp?", "Yes. It answers from the fee sheet and plan details you share with us, and brings in your team for anything it doesn't cover."),
                ("Can it book trial sessions?", "Yes. It offers a time and confirms the trial session inside the WhatsApp chat."),
                ("Can it remind members to renew?", "Yes. Renewal reminders go out as approved WhatsApp templates to the members you choose, and the agent handles the replies."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-for-coaching-institutes/", "WhatsApp AI agent for coaching institutes"),
                    ("/whatsapp-ai-agent-hindi/", "WhatsApp AI agent that replies in Hindi")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- travel
    {
        "path": "/whatsapp-ai-agent-for-travel-agents/", "published": NEW,
        "title": "WhatsApp AI Agent for Travel Agents & Tour Operators | Wogent",
        "og_title": "WhatsApp AI agent for travel agents",
        "description": "A WhatsApp AI agent for Indian travel agents and tour operators: answers package enquiries from your itineraries, collects dates, travellers and budget, and hands ready leads to your team, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for travel agents and tour operators",
        "crumb": "Travel agents", "tag": "Travel", "service": "WhatsApp AI agent for travel agents and tour operators",
        "audience": "Travel agents and tour operators",
        "answer": "Wogent is a WhatsApp AI agent for Indian travel agents and tour operators. It answers package enquiries from your own itineraries and price sheets, collects travel dates, number of travellers and budget, and hands the ready lead to your team to quote and book, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "One enquiry, ten questions"),
            ("p", "\"Dubai package ketla nu che?\" is never one message. It is dates, how many people, which hotel, is visa included, is Jain food available. Your team answers the same ten questions for every enquiry, and most of those people are comparing three agents at once."),
            ("chat", {"title": "Safar Holidays (demo)", "caption": "A sample enquiry. Demo data, not a real traveller.",
                      "messages": [("in", "Dubai 5 night package ketla nu che? December ma javu che", "8:30 PM"),
                                   ("out", "Dubai 5 night package ni itinerary ane price niche mokli che. Ketla loko javana cho, ane kai tarikh?", "8:30 PM"),
                                   ("in", "4 adults, 20 December. Jain food malse?", "8:32 PM"),
                                   ("out", "Haan, Jain food ni vyavastha package ma che. 4 adults, 20 December ni detail amari team ne mokli didhi che. Te tamne final quote sathe message karse.", "8:32 PM"),
                                   ("chip", "Lead ready for the team, details already collected")]}),
            ("h2", "What the agent does for a travel business"),
            ("ul", ["<strong>Package questions:</strong> inclusions, hotels, meals, visa and what is not included, answered from the itineraries and price sheets you share.",
                    "<strong>Collects the details:</strong> destination, dates, number of travellers, budget and special needs, asked naturally in the chat.",
                    "<strong>Hands over a ready lead:</strong> your team opens the chat with everything already collected and sends the final quote.",
                    "<strong>Reads documents and photos:</strong> a customer sends a passport photo or a payment screenshot; the agent reads it and keeps it with the chat.",
                    "<strong>Follow-ups:</strong> a traveller who got a quote and went quiet gets a nudge after a delay you set, and it stops the moment they reply.",
                    "<strong>Season offers:</strong> send a Diwali or summer-holiday package to your list in one broadcast; the agent answers every reply."]),
            ("callout", "<strong>The agent doesn't issue tickets or confirm fares.</strong> Fares and availability change by the hour, so the final quote and the booking stay with your team. The agent does the answering, the collecting and the chasing."),
        ],
        "faq": [("Can it answer tour package questions on WhatsApp?", "Yes. It answers from the itineraries, price sheets and brochures you share with us. If something isn't in your material, it brings in your team instead of guessing."),
                ("Does it book flights or hotels?", "No. It collects the traveller's details and hands the lead to your team, who send the final quote and make the booking."),
                ("Does it follow up with people who asked for a quote?", "Yes. After a delay you set it sends a nudge, within WhatsApp's template rules, and stops the moment the customer replies."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-for-real-estate/", "WhatsApp AI agent for real estate"),
                    ("/whatsapp-ai-agent-gujarati/", "WhatsApp AI agent that replies in Gujarati")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- online stores
    {
        "path": "/whatsapp-ai-agent-for-online-stores/", "published": NEW,
        "title": "WhatsApp AI Agent for Online Stores & D2C Brands | Wogent",
        "og_title": "WhatsApp AI agent for online stores and D2C brands",
        "description": "A WhatsApp AI agent for Indian online stores and D2C brands: answers product questions from your catalog, gives order status, takes orders in the chat and sends offers and follow-ups, 24/7 in Hindi, Gujarati and English.",
        "h1": "WhatsApp AI agent for online stores and D2C brands",
        "crumb": "Online stores", "tag": "E-commerce", "service": "WhatsApp AI agent for online stores and D2C brands",
        "audience": "Online stores, D2C brands and Instagram sellers",
        "answer": "Wogent is a WhatsApp AI agent for Indian online stores, D2C brands and Instagram sellers. It answers product, size and delivery questions from your catalog, tells customers where their order is, takes orders inside the chat and sends offers and follow-ups, 24/7 in Hindi, Gujarati or English.",
        "body": [
            ("h2", "Half your support inbox is one question"),
            ("p", "\"Where is my order?\" The rest is \"size chart?\", \"COD available?\", \"kab tak deliver hoga?\" and \"return kaise karu?\". None of these need a person, but every one of them needs a fast answer, or the customer cancels or complains in public."),
            ("chat", {"title": "Rang Kurtis (demo)", "caption": "A sample chat. Demo data, not a real customer.",
                      "messages": [("in", "Mera order kahan hai? 3 din ho gaye", "11:20 AM"),
                                   ("out", "Aapka order #RK2087 kal dispatch ho gaya hai aur kal tak deliver ho jayega. Tracking link neeche hai.", "11:20 AM"),
                                   ("in", "Ok. Same kurti blue me M size hai?", "11:21 AM"),
                                   ("out", "Haan, blue M size stock mein hai. Order kar du? Same address par bhejna hai?", "11:21 AM"),
                                   ("chip", "Status answered, second order started")]}),
            ("h2", "What the agent does for an online store"),
            ("ul", ["<strong>Order status:</strong> answers \"where is my order?\" with the live status from your connected system.",
                    "<strong>Product questions:</strong> sizes, colours, material, delivery time and return policy, from your catalog and policy documents.",
                    "<strong>Orders in the chat:</strong> product, quantity, address, confirmed, for customers who would rather message than use a website.",
                    "<strong>Remembers regulars:</strong> name, last order and address, so \"same as last time\" works.",
                    "<strong>Photos:</strong> a customer sends a screenshot from your Instagram page; the agent finds the product and quotes it.",
                    "<strong>Offers and journeys:</strong> a welcome series for new customers, a sale broadcast to a tagged group, a win-back offer for people who have not bought in a while.",
                    "<strong>Complaints go to a person:</strong> an upset customer or a damaged-parcel photo goes to your team with the full chat open."]),
        ],
        "faq": [("Can it answer \"where is my order?\" on WhatsApp?", "Yes. It checks the live order status from your connected system and replies with a real answer instead of \"we'll get back to you\"."),
                ("Can customers order on WhatsApp instead of the website?", "Yes. The agent takes the order inside the chat: product, quantity, address and confirmation. There is no form or app for the customer to install."),
                ("Can I send sale offers to my customers?", "Yes. You send an approved WhatsApp template to an uploaded list, a saved group or everyone with a tag, and the agent answers every reply. Anyone who replies STOP is taken off at once."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-for-retail-shops/", "WhatsApp AI agent for retail shops"),
                    ("/blog/take-orders-on-whatsapp-automatically/", "How to take orders on WhatsApp automatically")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- surat
    {
        "path": "/whatsapp-ai-agent-surat/", "published": NEW,
        "title": "WhatsApp AI Agent in Surat for Shops & Businesses | Wogent",
        "og_title": "WhatsApp AI agent for businesses in Surat",
        "description": "Wogent is a WhatsApp AI agent built in Surat for Surat businesses: textile and saree traders, retail shops, clinics and classes. It answers customers in Gujarati, Hindi and English 24/7 on the official WhatsApp Cloud API.",
        "h1": "WhatsApp AI agent for businesses in Surat",
        "crumb": "Surat", "tag": "Surat", "service": "WhatsApp AI agent for businesses in Surat",
        "audience": "Businesses in Surat, Gujarat",
        "answer": "Wogent is a WhatsApp AI agent from Surat, Gujarat, for businesses such as textile and saree traders, retail shops, clinics and coaching classes. It answers customers, takes orders and books appointments 24/7 in Gujarati, Hindi and English, and is set up for you on the official WhatsApp Cloud API. The team works remotely, so setup and support happen online, for Surat and the rest of India.",
        "body": [
            ("h2", "Surat does business on WhatsApp"),
            ("p", "A saree wholesaler sends catalog photos to buyers in other states. A shop in Adajan gets \"stock ma che?\" forty times a day. A dental clinic on Ghod Dod Road gets slot requests at midnight. Almost all of it comes in on WhatsApp, in Gujarati typed with English letters, and most of it waits until someone is free to reply."),
            ("chat", {"title": "Shree Sarees (demo)", "caption": "A sample wholesale enquiry. Demo data, not a real buyer.",
                      "messages": [("in", "Aa design ma biji colour che? 50 piece joiye", "7:10 AM"),
                                   ("out", "Haan, aa design 6 colour ma che. Catalog niche mokli che. 50 piece no rate pan sathe che.", "7:10 AM"),
                                   ("in", "Red ane green 25-25 mokli do", "7:12 AM"),
                                   ("out", "Order confirmed: 25 red, 25 green, total 50 piece. Dispatch ni detail amari team tamne mokalse.", "7:12 AM"),
                                   ("chip", "Order taken before the shop opened")]}),
            ("h2", "What it does for a Surat business"),
            ("ul", ["<strong>Replies in Gujarati the way Surat types it:</strong> \"ketla nu che?\", \"stock ma che?\", Gujarati script, Hindi and English, even mixed in one message.",
                    "<strong>Answers from your catalog:</strong> rates, designs, colours and stock from the price list or catalog you already send to buyers.",
                    "<strong>Takes the order in the chat:</strong> quantity, rate, confirmed, at any hour.",
                    "<strong>Reads photos:</strong> a buyer forwards a design photo; the agent finds it and quotes it.",
                    "<strong>Books appointments:</strong> for clinics, salons and classes.",
                    "<strong>Sends festival offers:</strong> one Diwali or Uttarayan broadcast to your whole list, with every reply answered.",
                    "<strong>Your staff take over when needed:</strong> every chat sits in a shared inbox."]),
            ("h2", "A Gujarati-speaking team, online"),
            ("p", "Wogent started in Surat and works remotely. We set the agent up for you over a call and WhatsApp, test it on your real chats and speak to you in Gujarati or Hindi, with no office visit needed. You can also sign up and try it yourself with free credits."),
        ],
        "faq": [("Is Wogent based in Surat?", "Yes. Wogent is from Surat, Gujarat. The team works remotely, so setup and support happen online for businesses anywhere in India."),
                ("Does it reply in Gujarati?", "Yes. It understands Gujarati script and Gujarati typed in English letters, such as \"ketla nu che?\", and replies in the language the customer uses."),
                ("Which Surat businesses is it for?", "Any business that gets customers on WhatsApp: textile and saree traders, retail and wholesale shops, clinics, salons, restaurants, coaching classes and real estate."),
                FAQ_TEAM, FAQ_SAFE, FAQ_COST],
        "related": [("/whatsapp-ai-agent-gujarati/", "WhatsApp AI agent that replies in Gujarati"),
                    ("/whatsapp-ai-agent-for-retail-shops/", "WhatsApp AI agent for retail shops")] + REL_COMMON,
    },
    # ---------------------------------------------------------------- API pricing guide
    {
        "path": "/blog/whatsapp-business-api-pricing-india/", "published": NEW,
        "title": "WhatsApp Business API Pricing in India (2026) | Wogent",
        "og_title": "WhatsApp Business API pricing in India: what you actually pay",
        "description": "What the WhatsApp Business API costs in India in 2026: Meta's per-message rates for marketing, utility, authentication and service messages, what platforms add on top, and two worked monthly examples.",
        "h1": "WhatsApp Business API pricing in India (2026): what you actually pay",
        "crumb": "WhatsApp API pricing in India", "tag": "Pricing", "read": 7,
        "answer": "The WhatsApp Business API has no licence fee from Meta, but you pay per message. Meta's India rates from 1 October 2026 are ₹0.8631 for each marketing template and ₹0.115 for each utility or authentication template. Service replies to a customer who messaged you are free for the first 1,000 a month per number, then ₹0.115 each. On top of Meta's charge you pay the platform you use to send messages, either as a monthly plan or per message.",
        "body": [
            ("h2", "The two bills every business gets"),
            ("ol", ["<strong>Meta's charge.</strong> A price for each message, set by Meta and the same whichever platform you use.",
                    "<strong>Your platform's charge.</strong> The software that connects you to the API: a monthly plan, a markup on each message, a per-use fee, or a mix."]),
            ("p", "Most confusion about WhatsApp API cost comes from quotes that show only one of the two. Always ask for both."),
            ("h2", "Meta's rates for India"),
            ("table", [["Message type", "What it is", "Meta's charge per message"],
                       ["Marketing template", "Offers, festival greetings, new arrivals, win-back messages", "₹0.8631"],
                       ["Utility template", "Order updates, appointment reminders, payment receipts", "₹0.115"],
                       ["Authentication template", "One-time passwords (OTP)", "₹0.115"],
                       ["Service reply", "Any reply inside 24 hours of the customer's last message", "Free for the first 1,000 a month per number, then ₹0.115"]]),
            ("p", "These are Meta's India list rates from 1 October 2026. Meta revises them from time to time, so check Meta's own rate card before you budget for a large campaign."),
            ("h2", "Template or service message: which one are you sending?"),
            ("p", "When a customer messages you, a 24-hour window opens. Inside it you can reply with normal free-form messages; these are service replies. To message someone first, or after the window has closed, you must use a template that Meta has approved, and Meta charges for it by category. That is why a festival offer to 2,000 people costs far more than answering 2,000 questions."),
            ("h2", "What platforms add on top"),
            ("ul", ["<strong>Monthly plans:</strong> a fixed fee, often per seat or per number, whether you send ten messages or ten thousand.",
                    "<strong>Message markup:</strong> a few paise added to Meta's charge on every template.",
                    "<strong>Pay per use:</strong> no fixed fee; you pay for what the software actually does.",
                    "<strong>Setup fees:</strong> one-time charges for onboarding or for building the bot."]),
            ("p", "Wogent's pay as you go has no monthly fee (optional plans start at ₹999 a month with AI replies included): ₹0.80 per AI reply, 5 paise per utility or authentication template and 10 paise per text marketing template, each on top of Meta's charge. Replies typed by your own team are free. The full list is on the <a href=\"/pricing/\">pricing page</a>."),
            ("h2", "Two worked examples"),
            ("table", [["", "A small clinic", "A busy retail shop"],
                       ["Monthly activity", "1,200 AI replies, 200 appointment reminders, 50 reports or photos read", "4,000 AI replies, 200 voice-note replies, 2,000 festival offers"],
                       ["Meta's charge", "₹46.00", "₹2,094.20"],
                       ["Wogent's charge", "₹982.50", "₹4,200.00"],
                       ["Total for the month", "₹1,028.50", "₹6,294.20"]]),
            ("p", "Figures exclude 18% GST. Notice where the retail shop's Meta bill comes from: 2,000 marketing templates cost ₹1,726.20 of the ₹2,094.20. Marketing messages are the expensive part of WhatsApp, so send them to people who are likely to care."),
            ("h2", "How to keep the bill down"),
            ("ul", ["Send offers to a tagged group instead of the whole list.",
                    "Use utility templates only for real transactions; Meta reclassifies promotional wording as marketing.",
                    "Reply inside the 24-hour window where you can, because service replies are free up to 1,000 a month per number.",
                    "Stop messaging people who never read; resend only to those who did not open the first time, once.",
                    "Honour STOP at once. Blocks and reports lower your quality rating, which limits how many people you can reach."]),
            ("callout", "<strong>Who bills what:</strong> Meta bills its message charges to the card on your own WhatsApp Business Account. With Wogent they never pass through your Wogent wallet, so you can see both bills separately."),
        ],
        "faq": [("Is the WhatsApp Business API free in India?", "There is no licence fee from Meta, and service replies are free for the first 1,000 a month per number. Template messages are charged per message: ₹0.8631 for marketing and ₹0.115 for utility or authentication, at Meta's India rates from 1 October 2026. Your platform's fee is extra."),
                ("How much does one WhatsApp marketing message cost in India?", "Meta charges ₹0.8631 for each marketing template delivered in India (rate from 1 October 2026). Your platform may add its own fee; Wogent adds 10 paise for a text template and 15 paise for one with an image, video or document."),
                ("Do I pay for replying to customers?", "Replies inside 24 hours of the customer's last message are service replies. They are free for the first 1,000 a month per number; after that Meta charges ₹0.115 each."),
                ("Is GST charged on WhatsApp API fees?", "Yes, 18% GST applies. The rates quoted here are before GST.")],
        "related": [("/pricing/", "Wogent pricing: pay per use or plans from ₹999"),
                    ("/blog/whatsapp-business-api-india/", "WhatsApp Business API in India: what it is and how to get it"),
                    ("/blog/whatsapp-broadcast-without-getting-banned/", "How to send WhatsApp broadcasts without risking your number")],
    },
    # ---------------------------------------------------------------- orders guide
    {
        "path": "/blog/take-orders-on-whatsapp-automatically/", "published": NEW,
        "title": "How to Take Orders on WhatsApp Automatically (2026) | Wogent",
        "og_title": "How to take orders on WhatsApp automatically",
        "description": "Three ways an Indian shop can take orders on WhatsApp without someone typing every reply: the WhatsApp Business app catalog, a menu chatbot, and an AI agent. What each one can and cannot do.",
        "h1": "How to take orders on WhatsApp automatically",
        "crumb": "Taking orders on WhatsApp", "tag": "Guide", "read": 6,
        "answer": "There are three ways to take orders on WhatsApp without typing every reply yourself. The free WhatsApp Business app gives you a catalog and a cart, but a person still has to confirm each order. A menu chatbot on the WhatsApp Business API takes orders through fixed buttons. An AI agent on the API reads normal messages such as \"2 geyser bhej do\", checks your price list, confirms the order and follows up, at any hour.",
        "body": [
            ("h2", "Option 1: the WhatsApp Business app catalog"),
            ("p", "The free WhatsApp Business app lets you add products with photos and prices. Customers can browse the catalog, add items to a cart and send the cart to you as a message. It costs nothing and takes an afternoon to set up."),
            ("p", "The limit is that the cart is only a message. Someone on your side still has to read it, check stock, confirm the total and reply. At 11 PM or during a rush, that reply waits."),
            ("h2", "Option 2: a menu chatbot"),
            ("p", "On the WhatsApp Business API you can build a flow: the customer taps \"Order\", picks a category, picks a product, picks a quantity. It works at any hour and the answers are predictable."),
            ("p", "The limit is that customers don't write in menus. They write \"bhaiya kal wala hi bhej do\" or send a photo of a handwritten list. A menu bot either ignores that or sends the menu again."),
            ("h2", "Option 3: an AI agent"),
            ("p", "An AI agent reads the message the way your staff would. It works out what the customer wants, looks up the product and price in your catalog, asks for anything missing, and confirms the order in the chat."),
            ("chat", {"title": "Gada Electronics (demo)", "caption": "A sample order. Demo data, not a real customer.",
                      "messages": [("in", "bhai 2 geyser 15L bhej do, same address", "10:40 PM"),
                                   ("out", "2 x Geyser 15L, pichhle order wale address par. Order #GE1042 confirm kar diya hai. Kal delivery ho jayegi.", "10:40 PM"),
                                   ("chip", "Order taken at 10:40 PM, nobody on duty")]}),
            ("h2", "Side by side"),
            ("table", [["", "Business app catalog", "Menu chatbot", "AI agent"],
                       ["Works when nobody is on duty", "No", "Yes", "Yes"],
                       ["Understands free-typed and mixed-language messages", "A person reads them", "No", "Yes"],
                       ["Reads a photo or a handwritten list", "A person reads it", "No", "Yes"],
                       ["Remembers \"same as last time\"", "If your staff remember", "No", "Yes"],
                       ["Needs the WhatsApp Business API", "No", "Yes", "Yes"],
                       ["Cost", "Free", "Platform fee plus Meta's charges", "Platform fee plus Meta's charges"]]),
            ("h2", "What you need before you automate orders"),
            ("ol", ["<strong>A clean price list.</strong> A PDF or sheet with product names, variants and prices. If two prices disagree, fix that first.",
                    "<strong>A rule for stock.</strong> Either the agent checks your system, or you tell it what is always available and what needs confirming.",
                    "<strong>A rule for payment and delivery.</strong> Advance or COD, delivery area and charges, written down.",
                    "<strong>Someone to take over.</strong> Bulk orders, complaints and special requests should reach a person with the chat already open.",
                    "<strong>A number on the WhatsApp Business API.</strong> Your existing business number can usually be moved."]),
            ("h2", "Which option should you pick?"),
            ("ul", ["<strong>A few orders a day, during shop hours:</strong> the free Business app is enough.",
                    "<strong>A short, fixed menu:</strong> a menu chatbot works and is predictable.",
                    "<strong>Many orders, messy messages, late-night enquiries:</strong> an AI agent pays for itself in the orders you currently miss."]),
            ("callout", "<strong>Where Wogent fits:</strong> Wogent is an AI agent for the third case. It takes orders in the chat in Hindi, Gujarati and English, reads photos and voice notes, and hands unusual requests to your team. Pay as you go has no monthly fee and an AI reply costs ₹0.80; optional plans start at ₹999 a month with AI replies included. See the <a href=\"/pricing/\">rate card</a>."),
        ],
        "faq": [("Can I take orders on WhatsApp for free?", "Yes, with the free WhatsApp Business app's catalog and cart. A person still has to read and confirm each order, so it only works while someone is available to reply."),
                ("Can customers order on WhatsApp without filling a form?", "Yes. An AI agent takes the order from normal chat messages, asks for anything missing such as quantity or address, and confirms it in the same chat."),
                ("Do I need the WhatsApp Business API to automate orders?", "Yes for any real automation. The free Business app only offers quick replies, away messages and a catalog; chatbots and AI agents run on the WhatsApp Business API."),
                ("Can an AI agent read a photo of a handwritten order list?", "Yes. Wogent's agent reads photos customers send, including product photos, payment screenshots and handwritten lists.")],
        "related": [("/whatsapp-ai-agent-for-retail-shops/", "WhatsApp AI agent for retail shops"),
                    ("/whatsapp-ai-agent-for-online-stores/", "WhatsApp AI agent for online stores"),
                    ("/blog/whatsapp-ai-agent-vs-chatbot/", "WhatsApp AI agent vs chatbot: what is the difference?")],
    },
    # ---------------------------------------------------------------- broadcast guide
    {
        "path": "/blog/whatsapp-broadcast-without-getting-banned/", "published": NEW,
        "title": "How to Send WhatsApp Broadcasts Without Risking Your Number | Wogent",
        "og_title": "How to send WhatsApp broadcasts without risking your number",
        "description": "Why business WhatsApp numbers get restricted after bulk messages, and the rules that keep a broadcast safe: the official API, opt-in, approved templates, a working STOP, quiet hours and watching your quality rating.",
        "h1": "How to send WhatsApp broadcasts without risking your number",
        "crumb": "Safe WhatsApp broadcasts", "tag": "Broadcasts", "read": 6,
        "answer": "Business numbers get restricted when they send bulk messages through unofficial tools, or when many recipients block and report them. To broadcast with far less risk, send through Meta's official WhatsApp Business API, message only people who agreed to hear from you, use templates Meta has approved, give everyone a working way to stop, and watch your quality rating. No tool can promise a number will never be restricted; these rules are what keep the risk low.",
        "body": [
            ("h2", "Why numbers get restricted"),
            ("ul", ["<strong>Unofficial bulk senders.</strong> Software that drives the normal WhatsApp app to message thousands of contacts breaks WhatsApp's terms. This is the most common reason a shop loses its number.",
                    "<strong>Messaging strangers.</strong> Bought lists and scraped numbers produce blocks and reports within minutes.",
                    "<strong>Too much, too often.</strong> Even real customers block a business that messages every day."]),
            ("h2", "1. Use the official WhatsApp Business API"),
            ("p", "The free WhatsApp Business app has a broadcast list, but it is small and only reaches people who have saved your number. For anything larger, use a product built on Meta's official WhatsApp Business API. It is the only approved way to message customers at scale."),
            ("h2", "2. Message only people who opted in"),
            ("p", "WhatsApp requires that a person has agreed to receive messages from your business. In practice: customers who messaged you first, people who ticked a box at checkout, people who gave their number at the counter and were told they would get offers on WhatsApp. Never upload a list you bought."),
            ("h2", "3. Use approved templates, in the right category"),
            ("p", "A message you start must be a template that Meta has approved. Offers and greetings are marketing templates; order updates and reminders are utility templates. Putting an offer inside a utility template gets it rejected or reclassified. Keep the wording clear, name your business, and personalise it with the customer's name."),
            ("h2", "4. Make STOP work"),
            ("p", "Tell people how to stop, and remove them the moment they ask. A customer who can't unsubscribe will block and report you instead, and that is what damages a number."),
            ("h2", "5. Respect the clock and the calendar"),
            ("ul", ["Don't send at night. Hold messages until morning.",
                    "Don't send to the same person every day. Once or twice a week is plenty for most shops.",
                    "Don't send the same offer to everyone. A tagged group that actually buys that product will read it."]),
            ("h2", "6. Watch your quality rating"),
            ("p", "Meta gives every business number a quality rating based on how recipients react, and it limits how many new people you can message in a day. Good quality raises that limit over time; a run of blocks lowers it. If your rating drops, stop broadcasting, tighten your list and wait for it to recover."),
            ("h2", "7. Answer the replies"),
            ("p", "A broadcast that gets replies is a conversation, and conversations are what WhatsApp is for. A broadcast that gets silence and blocks looks like spam. Make sure someone, or something, answers every reply quickly."),
            ("h2", "A pre-send checklist"),
            ("ol", ["Is this list made only of people who agreed to hear from us?", "Is the template approved, in the right category?",
                    "Does the message say who we are and how to stop?", "Is it going out in daytime?",
                    "Is someone ready to answer the replies?", "Do we know what this broadcast will cost at Meta's rate?"]),
            ("p", "For the cost question, see <a href=\"/blog/whatsapp-business-api-pricing-india/\">WhatsApp Business API pricing in India</a>."),
            ("callout", "<strong>How Wogent handles this:</strong> broadcasts go out as approved templates on the official WhatsApp Cloud API. Quiet hours hold messages overnight, anyone who replies STOP is removed at once, and the agent answers every reply. Your account still has to follow WhatsApp's Business and messaging policies."),
        ],
        "faq": [("Why did my WhatsApp Business number get banned after sending bulk messages?", "Most often because the messages were sent with an unofficial bulk tool, which breaks WhatsApp's terms, or because many recipients blocked or reported the number. Sending to bought or scraped lists causes both."),
                ("Is it allowed to send bulk WhatsApp messages to customers?", "Sending through Meta's official WhatsApp Business API to people who have opted in is allowed by WhatsApp's policies. Messaging people who never agreed to hear from you breaks those policies."),
                ("How many people can I broadcast to on WhatsApp?", "On the official API, Meta sets a daily limit on how many new people each business can message. The limit rises as you keep a good quality rating and falls if many people block you."),
                ("Can any tool guarantee my number won't be banned?", "No. Be wary of anyone who promises that. The official API, opted-in contacts, approved templates and a working STOP keep the risk low, but your account always has to follow WhatsApp's policies.")],
        "related": [("/blog/whatsapp-business-api-pricing-india/", "WhatsApp Business API pricing in India (2026)"),
                    ("/blog/whatsapp-business-api-india/", "WhatsApp Business API in India: what it is and how to get it"),
                    ("/blog/what-is-whatsapp-automation/", "What is WhatsApp automation?")],
    },
]


def main():
    for p in PAGES:
        out = os.path.join(ROOT, p["path"].strip("/").replace("/", os.sep), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(page(p))
        print("wrote", p["path"])
    for p in LEGAL_PAGES:
        out = os.path.join(ROOT, p["path"].strip("/"), "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(legal_page(p))
        print("wrote", p["path"])
    out = os.path.join(ROOT, "pricing", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(pricing_page())
    print("wrote /pricing/")
    missing = [k for k, v in LEGAL.items() if v.startswith("[")]
    if missing:
        print("WARNING: legal details still placeholders:", ", ".join(missing))


if __name__ == "__main__":
    main()
