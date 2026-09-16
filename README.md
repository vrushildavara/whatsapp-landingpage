# WhatsAgent AI — landing page

Static, no build step. `index.html` + `styles.css` + `script.js`, plus one
serverless function in `api/`. Open `index.html` directly in a browser, or
serve it with any static server (`npx serve .`) — everything except the chat
widget works that way. The chat needs the function, so use `vercel dev`.

## What's on the page

Six sections, cut down from a much longer first version after client
feedback ("too much content, no visuals, add animations"):

1. **Hero** — headline, one line, CTAs, the animated retail phone with
   floating chips around it.
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
5. **Front desk** — three cards (broadcast campaign, shared inbox, document
   answers), each with a small animation that plays once as it scrolls in.
6. **Demos** — one phone with four tabs (retail / clinic / real estate /
   broadcast), then a 4-item FAQ and the CTA band.

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
The campaign and inbox visuals in the grid are plain HTML/CSS (`.bc-*`), not
chat mockups.

If real product screenshots become available later, they can replace these
mockups by swapping the `.wa-window` / `.wa-snippet` container's contents for
an `<img>` — the surrounding layout (phone bezel, caption) doesn't need to
change.

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

- `assets/og-image.jpg` — the Open Graph / Twitter card image, generated from
  `assets/og-image-source.html` (open that file and re-screenshot at 1200×630
  if the OG copy or colors need to change; no design tool required).
- `favicon.ico` — generated from `assets/favicon-source.html` the same way,
  at 64×64. The `<link rel="icon">` in `index.html` uses an inline SVG data URI
  for crisp rendering; `favicon.ico` exists solely so browsers that probe
  `/favicon.ico` by convention don't log a 404.

## Editing

- Colors, type, spacing tokens: top of `styles.css` (`:root`). Note
  `--accent` is reserved for large text/decorative fills; small text and
  icons use the darker `--accent-hover` for WCAG AA contrast — keep that
  split when adding new elements.
- Contact links point at `mailto:vrushildavra82@gmail.com` — update if that
  should be a different address.

## Deploying

This repo is **not** the same deployment as the live product app
(`whatsagent-live.vercel.app`, which is the authenticated dashboard — it has
no public marketing page). This static site is meant to be deployed as its
own, separate Vercel project with its own URL; its CTAs link out to the
product app / a contact email rather than assuming they share a domain.

Live at **https://whatsagent-ai-landing.vercel.app** (Vercel project
`whatsagent-ai-landing`). Note this is a different project from the product
dashboard at `whatsagent-ai.vercel.app` — don't deploy one over the other.

```bash
vercel --prod --yes
# then re-point the short URL — see the warning below
vercel alias set <the-new-deployment-url> whatsagent-ai-landing.vercel.app
```

**The alias step is not optional.** `whatsagent-ai-landing.vercel.app` was
created with `vercel alias set`, which pins it to one specific deployment; it
does NOT follow later production deploys. Skip the second command and the
short URL keeps serving the previous build while `vercel ls` reports the new
one as live — which looks exactly like a deploy that silently did nothing.
The auto-generated
`whatsagent-ai-landing-<team>.vercel.app` does follow production on its own,
so use that one if you want to skip the alias step.

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
