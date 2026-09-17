/* ==========================================================================
   /api/lead — receives the "Book a demo" form and forwards it.

   Same shape as /api/chat: Vercel Node runtime, no dependencies. The form
   posts JSON here; this validates it and POSTs it on to LEAD_WEBHOOK_URL —
   a Google Apps Script, Zapier/Make hook, Slack incoming webhook, or
   anything else that accepts JSON. Nothing is stored on Vercel itself.

   Until LEAD_WEBHOOK_URL is set the endpoint answers 503 and the page shows
   the visitor a clear "not available right now" note rather than a false
   success. The old WhatsApp handoff still exists client-side as a switch
   (LEAD_CHANNEL in script.js) for when a production number is connected.
   ========================================================================== */

const AUTOMATE_OPTIONS = [
  "Customer support",
  "Lead qualification",
  "Sales",
  "Follow-ups",
  "Orders",
  "Everything"
];

const BIZ_OPTIONS = ["Retail", "Clinic", "Real estate", "Other"];

const MAX_FIELD = 120;

/* One lead every ~10s per IP; the same lightweight in-memory limiter the
   chat endpoint uses — Fluid Compute keeps instances warm, so this holds
   across a burst without pretending to be a database. */
const recent = new Map();
const WINDOW_MS = 10 * 1000;

function clientIp(req) {
  const fwd = req.headers["x-forwarded-for"];
  return (typeof fwd === "string" ? fwd.split(",")[0] : "").trim() || req.socket?.remoteAddress || "?";
}

function rateLimited(ip) {
  const now = Date.now();
  const last = recent.get(ip) || 0;
  if (now - last < WINDOW_MS) return true;
  recent.set(ip, now);
  if (recent.size > 5000) recent.clear();
  return false;
}

function clean(value) {
  return typeof value === "string" ? value.trim().slice(0, MAX_FIELD) : "";
}

/* Digits only, country code included: 10–15 digits (91 + a 10-digit
   Indian number is 12; 65 + 8 for Singapore is 10). Anything that isn't a
   digit is rejected outright rather than stripped, so what lands in the
   sheet is exactly what was validated. */
function cleanPhone(value) {
  const str = String(value || "").trim();
  if (!/^\d{10,15}$/.test(str)) return "";
  return str;
}

function parseLead(body) {
  if (!body || typeof body !== "object") return { error: "That didn't come through — try again." };

  /* Honeypot: real visitors never see or fill this field. */
  if (clean(body.website)) return { spam: true };

  const biz = clean(body.biz);
  const otherBiz = clean(body.otherBiz);
  const name = clean(body.name);
  const phone = cleanPhone(body.phone);
  const city = clean(body.city);
  const state = clean(body.state);
  const country = clean(body.country);
  const automate = clean(body.automate);

  if (!BIZ_OPTIONS.includes(biz)) return { error: "Pick your business type." };
  if (biz === "Other" && !otherBiz) return { error: "Tell us your business type." };
  if (!name) return { error: "Add your name." };
  if (!phone) return { error: "Enter the WhatsApp number as digits only, with the country code." };
  if (!city || !state || !country) return { error: "Add your city, state and country." };
  if (!AUTOMATE_OPTIONS.includes(automate)) return { error: "Pick what you'd like to automate." };

  return {
    lead: {
      business: biz === "Other" ? otherBiz : biz,
      businessOption: biz,
      name,
      phone,
      city,
      state,
      country,
      automate,
      /* Attribution the page collects from the URL; all optional. */
      source: clean(body.source),
      utm_source: clean(body.utm_source),
      utm_medium: clean(body.utm_medium),
      utm_campaign: clean(body.utm_campaign),
      utm_content: clean(body.utm_content),
      referrer: clean(body.referrer)
    }
  };
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed." });
  }

  let body = req.body;
  if (typeof body === "string") {
    try {
      body = JSON.parse(body);
    } catch (err) {
      body = null;
    }
  }

  const parsed = parseLead(body);
  if (parsed.spam) return res.status(200).json({ ok: true });
  if (parsed.error) return res.status(400).json({ error: parsed.error });

  const webhook = process.env.LEAD_WEBHOOK_URL;
  if (!webhook) {
    console.error("lead: LEAD_WEBHOOK_URL is not set — the demo form has nowhere to send leads.");
    return res.status(503).json({ error: "Booking isn't available right now. Please try again in a little while." });
  }

  if (rateLimited(clientIp(req))) {
    return res.status(429).json({ error: "Please wait a moment before sending again." });
  }

  const payload = Object.assign({}, parsed.lead, {
    receivedAt: new Date().toISOString(),
    page: req.headers.referer || "",
    userAgent: req.headers["user-agent"] || ""
  });

  /* Google Apps Script cold-starts slowly — 10–20s is normal for the first
     hit in a while — so this waits well past that. The visitor sees
     "Sending…" on the button meanwhile. */
  const controller = new AbortController();
  const timer = setTimeout(function () {
    controller.abort();
  }, 40000);

  try {
    const upstream = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    if (!upstream.ok) {
      console.error("lead: webhook responded " + upstream.status);
      return res.status(502).json({ error: "Couldn't save your request. Please try again." });
    }
  } catch (err) {
    console.error("lead: webhook request failed — " + (err && err.message));
    return res.status(502).json({ error: "Couldn't save your request. Please try again." });
  } finally {
    clearTimeout(timer);
  }

  return res.status(200).json({ ok: true });
};

module.exports.parseLead = parseLead;
module.exports.AUTOMATE_OPTIONS = AUTOMATE_OPTIONS;
