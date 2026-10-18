# WoAi — landing page

Static, no build step. `index.html` + `styles.css` + `script.js`, plus one
serverless function in `api/`. Open `index.html` directly in a browser, or
serve it with any static server (`npx serve .`) — everything except the chat
widget works that way. The chat needs the function, so use `vercel dev`.

## What's on the page

Eight sections, cut down from a much longer first version after client
feedback ("too much content, no visuals, add animations"), then grown by
two when broadcasts v2 and journeys shipped:

1. **Hero** — a "New: Journeys" pill linking to that section, headline,
   one line, CTAs, the animated retail phone with floating chips around it.
2. **Ticker** — a scrolling strip of real-world moments; this replaced the
   old "problem" section.
3. **How it works** — three steps on a line that draws itself on scroll
   (a vertical connector on phones).
4. **Capabilities showcase** — one phone, seven capabilities (thinks first,
   language, live lookup, orders, photos, memory, handoff). On wide screens
   the block is pinned and scrolling walks through them. Under 900px it
   becomes title → scrolling chip row → phone → caption: the phone
   auto-advances every ~4s while on screen until the user taps a chip or
   swipes the phone, and each change pops the bubbles in. Reduced motion
   gets the tab row with no auto-advance. Replaced eight alternating rows.
5. **Broadcasts** (`#broadcasts`, `.bcx-*`) — four step buttons (who,
   message, when, results) beside one campaign window. While on screen it
   advances every ~5s with a hairline filling under the active step, until
   the visitor taps a step; each panel plays its own entrance (counters,
   the `{{name}}` slot cycling through customers, the quiet-hours toggle,
   the results bars). Phones show the window above the steps. Four safety
   points sit underneath. Reduced motion: no auto-advance.
6. **Journeys** (`#journeys`, `.jx-*`) — a dark band so the newest feature
   stands apart. Four starter chips switch the board between journeys
   defined in `JOURNEY_FLOWS` (`script.js`); each run plays one customer
   through it (connectors light, an avatar rides from step to step, sends
   pop what the customer saw, waits fill a bar) with a plain-words
   caption underneath, alternating branches. It only plays on screen, and
   the board keeps the tallest journey's height. Reduced motion or no
   GSAP: the board is drawn still with a one-line summary.
7. **Front desk** — three cards (contacts address book, shared inbox,
   document answers), each with a small animation that plays once as it
   scrolls in. The contacts card shows a new tag starting a journey.
8. **Demos** — one phone with five tabs (retail / clinic / real estate /
   broadcast / journey), then the FAQ and the CTA band.

A short "Built for businesses that get customers on WhatsApp" strip with
business-type chips sits between the ticker and How it works.

Motion is GSAP 3.13 + ScrollTrigger from cdnjs (`index.html`, just before
`script.js`). The whole motion layer sits in one block in `script.js`, guarded
by `prefers-reduced-motion` and by the CDN having loaded — without either,
the page renders in its finished static state. Beyond the section pieces
above: the hero phone shows a seconds counter while the agent types
(`data-wa-stopwatch`), the ticker pauses on hover and lights each outcome as
it crosses the centre, the inbox card keeps receiving new enquiries while
on screen, the demo phone tilts toward the cursor and wipes between tabs,
FAQ answers slide open, the nav compacts on scroll and underlines the
section in view, primary buttons lean toward the cursor, and the CTA band
has drifting bubbles behind it. A later pass added a page-load curtain, a
cursor-following glow, word-by-word headline reveals, press/ripple feedback
on buttons, a blinking nav mark and an idle nudge on the chat launcher,
WhatsApp-style bubble squash + tick colouring + reaction bursts in the chat
mockups, and Lenis smooth scrolling (jsdelivr, desktop pointers only —
touch devices keep native scrolling). Section copy is headlines plus one
line each; all of it is grounded in the real product (Hindi/Gujarati/English
WhatsApp agent for Indian SMBs, demoed with Gada Electronics as the primary
retail example).

Copy rules that apply everywhere: no prices or invented numbers, no vendor or
model names, and no internal mechanics (intervals, queue states, storage
layers) — describe what the customer gets.

## WhatsApp chat mockups

All chat visuals — the animated hero phone, the seven showcase screens, the
document-lookup snippet in the front-desk grid, and the use-case demo phone —
are rendered by one reusable component in `script.js`
(`CHAT_DATA` + `renderStatic`/`renderAnimated`). To change a conversation, edit
its message array in `CHAT_DATA`; every `[data-wa-chat="<key>"]` element using
that key re-renders automatically. Add `data-wa-animate` to have a thread play
message-by-message (the hero phone; add `data-wa-once` to play a single pass,
as the docs snippet does). The demo phone is driven by the tab buttons'
`data-demo` keys instead; `renderAnimated` returns a handle with `stop()` so
switching tabs cancels the previous thread. A message can carry
`image: { kind: "photo" | "screenshot", label, src }` to show an attachment
above its text. With `src` it renders that file (the photos row uses
`assets/img-switch.svg`, an illustration of the switch in that conversation —
swap the path for a real product photo when you have one); without `src` the
tile is drawn in CSS, which is how the payment screenshot is done.
The contacts and inbox visuals in the grid are plain HTML/CSS (`.ct-*`,
`.bc-*`), not chat mockups.

If real product screenshots become available later, they can replace these
mockups by swapping the `.wa-window` / `.wa-snippet` container's contents for
an `<img>` — the surrounding layout (phone bezel, caption) doesn't need to
change.

## Book-a-demo form and leads

The modal form posts to `/api/lead` (`api/lead.js`), which validates the
fields — business type, name, WhatsApp number, city/state/country, and
"What would you like to automate?" — and forwards the lead as JSON to
`LEAD_WEBHOOK_URL` (a Google Apps Script web app, Zapier/Make hook, Slack
incoming webhook, anything that accepts a JSON POST). UTM parameters from
the landing URL and the referrer ride along. Nothing is stored on Vercel.
Without `LEAD_WEBHOOK_URL` the endpoint answers 503 and the form shows
"Booking isn't available right now" — set it on the Vercel project before
sending paid traffic. A honeypot field and a per-IP rate limit keep bots out.

`LEAD_CHANNEL` at the top of the modal code in `script.js` switches the
submit action: `"webhook"` (current, for the Meta Ads test phase where no
production WhatsApp number is connected) or `"whatsapp"`, which opens a
wa.me chat to `WHATSAPP_NUMBER` with the details prefilled — the original
flow, kept for when a number is live.

The site chat shows an invitation bubble above its launcher six seconds
after arrival, once per browser session (`sessionStorage` key `wa-teaser`);
tapping it opens the panel. In the demo form, picking +91 swaps the State
box for a list of Indian states and union territories (`INDIAN_STATES` in
`script.js`); other countries get a text box. City, state and country are
letters-only on both sides (`PLACE_RE` in `script.js` and `api/lead.js`).

Copy rules from the reviews: no em or en dashes anywhere a visitor reads
(the chatbot's brief says the same and `cleanReply` in `api/chat.js` turns
any that slip through into commas); headlines and lines lead with the
customer's situation, then what the agent does.

## Tracking

`window.WA_TRACKING` in `index.html` holds two IDs; `script.js` loads a
tracker only for the IDs that are set, so an empty string means that
tracker is not on the page at all.

- `ga4MeasurementId` — Google Analytics 4 (`G-16RD8E52BK`, property "WoAi").
  gtag.js boots and sends `page_view` from the config call.
- `metaPixelId` — Meta Pixel. Empty until Meta provides one; set it and the
  Pixel boots and fires `PageView`.

Everything else goes through one `track(event, params)` helper:
`ViewContent` (use-case demos scrolled into view; demo form opened),
`Contact` (site chat opened), `Lead` and `Schedule` (demo form submitted
successfully). Meta receives those names unchanged (they are its standard
events); GA4 receives `view_content`, `contact`, `generate_lead` and
`schedule` — mark `generate_lead` as a key event in GA4 Admin to count demo
requests as conversions. Each call also dispatches a DOM `wa:track` event,
so a tag manager can listen without touching the page code.

## Claims and wording

Meta Ads compliance rules baked into the copy: the site is "built on the
official WhatsApp Cloud API" — never "official", "partner" or "powered by"
in a way that implies WhatsApp/Meta endorsement — and it makes no
guarantees about accounts never being restricted or banned (the FAQ says
the account stays subject to WhatsApp's Business and messaging policies).
The chat assistant's brief in `api/chat.js` carries the same rules.

## Chat assistant

The floating widget in the bottom-right corner answers visitor questions about
the product. It posts to `api/chat.js`, a Vercel serverless function — the
OpenRouter key and the assistant's system prompt live there and never reach
the browser.

**Setup.** The function needs at least one provider key. Set as many as you
like — every key you add joins the fallback chain, so the free tiers stack:

| Provider | Env var | Free allowance |
| --- | --- | --- |
| Gemini (Google AI Studio) | `GEMINI_API_KEY` | Largest of the three, no card needed. Google publishes current limits in the [AI Studio dashboard](https://aistudio.google.com/rate-limit) |
| Groq | `GROQ_API_KEY` | 30/min, 1,000 req/day, but **200,000 tokens/day** — with our ~1,500-token prompt that is ~130 messages/day |
| OpenRouter | `OPENROUTER_API_KEY` | 50 req/day; **1,000/day** after a one-off $10 credit |

```
vercel env add GEMINI_API_KEY     # for deployments; repeat per provider
cp .env.local.example .env.local  # or just edit .env.local for local dev
```

`.env.local` is gitignored. With no key at all the function returns 500 and
the widget shows a friendly note instead of answering.

**The chain is ordered by accuracy, not by quota — and that matters.**
OpenRouter answers first even though Gemini has the far bigger free tier,
because Gemini does not answer from the brief. See "Why Gemini is last"
below before you reorder it.

**Do this before real traffic:** add a one-off $10 credit to the OpenRouter
account. It lifts free models from 50 to 1,000 requests/day, which is what
makes this configuration comfortable — the accurate model then handles
essentially all traffic. Without it, 50 requests/day is the real ceiling and
the widget starts erroring once it is spent. Alternatively set
`OPENROUTER_MODEL` to a cheap paid id such as `inclusionai/ling-3.0-flash`
(~$0.0001 per message, roughly $10 per 100,000 messages).

**Local run:** `vercel dev` (a plain static server won't serve `/api/chat`).

**How the chain works.** `PROVIDERS` in `api/chat.js` lists each provider with
its key variable, endpoint and its own ordered model list. `buildChain()`
flattens that into the attempts for one request, skipping any provider whose
key is missing, and the handler walks the chain until something answers
acceptably. A 429, 502, timeout, or a reply that fails `checkReply` all move
on to the next attempt identically.

Adding a provider is therefore a key, not a code change. This stays small
because Gemini, Groq and OpenRouter all speak the **OpenAI chat-completions
format** — the only provider-specific bits are the URL, the two OpenRouter
attribution headers, and OpenRouter's `reasoning` extension (never sent
elsewhere, since other providers reject unknown fields). Any other
OpenAI-compatible provider (DeepSeek, Together, Fireworks, a local Ollama)
can be added as one more entry in `PROVIDERS`.

The OpenRouter model order came from a bake-off — four questions ("how are you
different?" in English, Hindi and Gujarati, plus a "just give me a rough
price" bait), each reply scored by `checkReply`. The comment above that
provider's `models` records what each scored and why four others were
excluded. Re-run it before reordering, because free-tier behaviour drifts.

**Why Gemini is last, despite the biggest free tier.** It was tried first,
and it does not answer from the brief. Across repeated runs Gemini flash
models claimed a CRM and database integration, an analytics dashboard, a
"visual flow builder" needing no technical knowledge, payment handling,
invoice generation and inventory tracking; quoted an invented ₹1,500/month
plan and a ₹500–2,000 range; told visitors to "check the official pricing
page" (there isn't one); said setup is instant and self-serve, which is the
exact opposite of the done-for-you positioning; and once introduced itself as
"a large language model, trained by Google". This was not a lite-tier
problem — 3.5-flash, 3.6-flash and 3.8-flash all scored 1–2 out of 5 on
grounding too, while being 4–6× slower.

Six rounds of prompt tightening and filter-writing did not fix it: each round
it invented something new, most often in Hindi or Gujarati where the patterns
are hardest to write. `FALSE_CLAIM_PATTERNS` now blocks every specific
fabrication observed, but treat that as damage control, not a guarantee —
do not promote Gemini up the chain expecting the filter to hold.

It stays in the chain because its free allowance is genuinely large and it is
useful exactly where it sits: as overflow once OpenRouter's daily cap is
spent. When it is filling in and the gate rejects it, the visitor gets the
"couldn't reach my brain" note. That is deliberate — an error is better than
a confident lie about the product.

**Free tiers do run out**, and when one does, every model behind that key
fails together — which is why the chain spans providers rather than just
models. A single day of building and testing exhausted OpenRouter's 50/day.

**Don't trust the model, check the reply.** `checkReply` in `api/chat.js` is
not decoration. During testing free models invented a monthly price in rupees,
invented retention statistics, pasted their own scratchpad into the answer,
answered a Hindi question in English, and looped one token for 250 words. A
reply that trips the gate is discarded and the next model is tried, exactly
like a failed request. It rejects:

- invented prices (there is no public price list, so any figure is made up)
- leaked reasoning ("The user asked…", "so I'll answer in English")
- repetition loops and low word variety
- replies over 130 words
- mangled output (`?` runs, replacement characters)
- **wrong script** — if the visitor writes in Devanagari or Gujarati, the
  reply must come back in that script. Roman-script questions are
  unconstrained, so Hinglish still gets Hinglish.

Truncation is caught separately: a `finish_reason` of `length` means the model
was cut off mid-sentence, so that reply is dropped too. `MAX_TOKENS` is
generous headroom rather than a length limit, because Devanagari and Gujarati
cost several tokens per word — at 500 a Gujarati reply was being cut mid-word.
Brevity is enforced in words by the gate, not by starving the token budget.

If you loosen any of this, re-run the bake-off first. Two traps worth knowing:
the price rules must require a real digit (an earlier `[\d,]+` matched the bare
comma in "customers," and silently rejected good replies), and if you test
non-Latin input from a Windows shell, send it from a UTF-8 client — Git Bash
curl mangles Devanagari to `?????` before it ever reaches the endpoint, which
looks exactly like a model failure.

**What it's allowed to say.** `SYSTEM_PROMPT` in `api/chat.js` is grounded in
the claims on this page — capabilities, use cases, the "why us" points, and
the FAQ answers. It is told never to invent pricing (there is no public price
list), features, or timelines, and to route anything it doesn't know to a
demo. Keep it in sync when the page's copy changes, or the assistant will
start contradicting the page it sits on.

**And `FALSE_CLAIM_PATTERNS` cuts both ways.** It was first written to block
Gemini's fabrications, and some of those later became real features (a
dashboard, a system connection). When the page gains a capability, audit the
patterns too — a stale one silently rejects *accurate* replies and burns a
model attempt. Each relaxation is documented inline in the array. Also avoid
phrasing the prompt as "it has no X" for a blocked word: models echo the
disclaimer ("it is not a CRM") and the gate then rejects a true answer.

## Images

- `assets/og-image.jpg` — the Open Graph / Twitter card image (1200×630), exported
  from the brand kit (`E:/Games/prompts/wogent/brand-kit/covers/wogent-cover-website-og-share-1200x630.png`).
  Every page, the sitemap and the JSON-LD point at this exact path; it was missing
  until 2026-10-13, so keep the filename.
- `assets/logo-512.png` — square logo used as the Organization `logo` in JSON-LD.
- `favicon.ico`, `assets/icon.svg`, `apple-touch-icon.png`, `assets/icon-192.png`,
  `site.webmanifest` — icons from the brand kit (`brand-kit/logo/…`), linked from
  every page's `<head>`.

## SEO pages and AI-assistant files

- Industry pages (`/whatsapp-ai-agent-for-<industry>/`), language pages
  (`/whatsapp-ai-agent-gujarati/`, `/whatsapp-ai-agent-hindi/`) and the two guide
  posts in `/blog/` are generated by `python tools/build_pages.py`. Edit the page
  data in that file and re-run it; don't hand-edit the generated HTML. `tools/` is
  in `.vercelignore`, so the script never ships.
- Each page opens with an "answer-first" paragraph: a self-contained summary that
  search snippets and AI assistants can quote. Keep it accurate to "Claims and
  wording" above.
- The "WhatsApp AI agent for" footer row (`.footer-solutions`) is on every page;
  add new pages to `SOLUTIONS` in the script and to the static pages' footers.
- `llms.txt` (summary) and `llms-full.txt` (all facts, FAQs and page answers in
  one file) are for AI crawlers. Regenerate `llms-full.txt` when the FAQ or pages
  change. `robots.txt` explicitly allows the main AI search crawlers.
- When adding a page: add it to `sitemap.xml` with today's `lastmod`, and link it
  from at least one existing page.

## Editing

- Colors, type, spacing tokens: top of `styles.css` (`:root`). Note
  `--accent` is reserved for large text/decorative fills; small text and
  icons use the darker `--accent-hover` for WCAG AA contrast — keep that
  split when adding new elements.
- Contact links point at `mailto:wogent7@gmail.com` — update if that
  should be a different address.

## Deploying

This repo is **not** the same deployment as the live product app
(`whatsagent-live.vercel.app`, which is the authenticated dashboard — it has
no public marketing page). This static site is meant to be deployed as its
own, separate Vercel project with its own URL; its CTAs link out to the
product app / a contact email rather than assuming they share a domain.

Live at **https://woai-ai.vercel.app** (Vercel project
`whatsagent-ai-landing`, which keeps its original name; `woai.vercel.app`
is owned by another Vercel team, hence the `-ai`). The older
`watsagent-ai-landing`, `whatsagent-ai-landing`, `whatsagent-landing` and
`landing-page-ivory-six-32` hosts all 308-redirect there via `vercel.json`.
Note this is a different project from the product dashboard at
`whatsagent-ai.vercel.app` — don't deploy one over the other.

```bash
vercel --prod --yes
```

`woai-ai.vercel.app` is a **project domain** (Settings → Domains), not a
`vercel alias set` alias, so it follows every production deploy on its own —
no alias step. The old hosts are still per-deployment aliases; they keep
serving the redirect because `vercel.json` ships with every build, but if one
ever stops redirecting, re-point it:

```bash
vercel alias set <the-new-deployment-url> watsagent-ai-landing.vercel.app
```

**SEO files:** `robots.txt`, `sitemap.xml` and the JSON-LD block in
`index.html` (Organization, WebSite, SoftwareApplication, FAQPage) all
hard-code the live URL — update them if the host changes again. After a host
change, add the new property in Google Search Console and submit
`https://woai-ai.vercel.app/sitemap.xml`.

Two files matter to the deploy beyond the site itself:

- `.vercelignore` — this project deploys **without a git repo**, so Vercel
  uploads whatever sits in the folder and serves it statically. Keeping
  `.env*` out is a security control: without it, `/.env.local` is publicly
  fetchable with the API keys in it. Verify after any deploy that
  `curl -o /dev/null -w '%{http_code}' <url>/.env.local` returns 404.
- Environment variables live on the project (`vercel env ls`), not in the
  upload. They must be set for Production before the chat works.

No build command. The static pages work on any host (Netlify, GitHub Pages),
but the chat widget needs a host that runs the `api/` function with the
provider keys in its environment.
