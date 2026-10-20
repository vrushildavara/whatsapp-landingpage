/* ==========================================================================
   wo-track.js — first-party analytics for web.wogent.in (and Google Tag Manager)

   Loaded on every page with one tag:  <script src="/wo-track.js" defer></script>
   Configure it in DEFAULTS just below (one place for every page); window.WA_TRACKING,
   if a page sets it before this script, overrides per page:
     collectorUrl  where events go
     gtmId         "GTM-XXXXXXX" — empty means Google Tag Manager is not loaded. When it is
                   set, script.js stops loading GA4 directly: add GA4 as a tag inside GTM.

   What it records, posted to the Wogent backend and read in admin.wogent.in → Marketing:
     page_view    every page
     page_exit    leaving a page, with time it was visible and furthest scroll
     cta_click    a click through to wogent.in (log in / sign up)
     demo_open, demo_request, chat_open — sent by script.js through window.woTrack()

   Identity lives in first-party cookies on .wogent.in, so the sign-up page on wogent.in
   reads the same visitor and credits the account to the campaign that brought it:
     wo_vid    random visitor id (1 year)            wo_visits  visit counter (1 year)
     wo_sess   session id + the touch that started it (expires after 30 idle minutes)
     wo_team   set by visiting any page with ?wo_team=1 — marks our own browsers so they
               are left out of the numbers (?wo_team=0 clears it)

   Nothing here can break the page: every entry point swallows its own errors.
   ========================================================================== */
(function () {
  "use strict";

  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var DEFAULTS = {
    // A local copy of the site posts to a local backend (uv run uvicorn … on :8000).
    collectorUrl: LOCAL ? "http://localhost:8000/marketing/events" : "https://api.wogent.in/marketing/events",
    gtmId: "GTM-TJDPC2KJ"
  };

  var CFG = window.WA_TRACKING || {};
  var COLLECTOR = typeof CFG.collectorUrl === "string" ? CFG.collectorUrl : DEFAULTS.collectorUrl;
  var GTM_ID = typeof CFG.gtmId === "string" && CFG.gtmId ? CFG.gtmId : DEFAULTS.gtmId;
  GTM_ID = /^GTM-[A-Z0-9]{4,10}$/.test(GTM_ID) ? GTM_ID : "";
  window.WO_GTM_ENABLED = !!GTM_ID; // read by script.js to stop loading GA4 directly
  var SESSION_IDLE_S = 30 * 60;
  var YEAR_S = 365 * 24 * 60 * 60;
  // Shared across web.wogent.in and wogent.in; host-only on previews and localhost.
  var DOMAIN = /(^|\.)wogent\.in$/.test(location.hostname) ? "; Domain=.wogent.in" : "";
  var GPC = navigator.globalPrivacyControl === true;

  // ------------------------------------------------------------------ cookies

  function readCookie(name) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : null;
  }

  function writeCookie(name, value, maxAge) {
    var secure = location.protocol === "https:" ? "; Secure" : "";
    document.cookie = name + "=" + encodeURIComponent(value) + "; Max-Age=" + maxAge + "; Path=/; SameSite=Lax" + DOMAIN + secure;
  }

  var UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") return window.crypto.randomUUID();
    var b = window.crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40;
    b[8] = (b[8] & 0x3f) | 0x80;
    var h = Array.prototype.map.call(b, function (x) { return ("0" + x.toString(16)).slice(-2); }).join("");
    return h.slice(0, 8) + "-" + h.slice(8, 12) + "-" + h.slice(12, 16) + "-" + h.slice(16, 20) + "-" + h.slice(20);
  }

  // ------------------------------------------------------------------ identity

  function visitorId() {
    var id = readCookie("wo_vid");
    if (!id || !UUID_RE.test(id)) id = uuid();
    writeCookie("wo_vid", id, YEAR_S); // re-written so the year rolls forward
    return id;
  }

  function landingTouch() {
    var q = new URLSearchParams(location.search);
    var get = function (k) { var v = q.get(k); return v ? v.trim().slice(0, 120) : null; };
    var fbclid = get("fbclid");
    // Meta's click cookie; written once per click id so its timestamp stays the click's.
    var fbc = readCookie("_fbc") || "";
    if (fbclid && fbc.slice(-fbclid.length) !== fbclid) {
      writeCookie("_fbc", "fb.1." + Date.now() + "." + fbclid, 90 * 24 * 60 * 60);
    }
    var ref = null;
    try {
      var r = document.referrer ? new URL(document.referrer) : null;
      ref = r && !/(^|\.)wogent\.in$/.test(r.hostname) && r.host !== location.host ? r.href.slice(0, 512) : null;
    } catch (e) { ref = null; }
    return {
      source: get("utm_source"), medium: get("utm_medium"), campaign: get("utm_campaign"),
      content: get("utm_content"), term: get("utm_term"), ref: ref,
      click: fbclid ? "meta" : get("gclid") ? "google" : null
    };
  }

  function sameCampaign(a, b) {
    return a.source === b.source && a.medium === b.medium && a.campaign === b.campaign && a.content === b.content;
  }

  /* The current session, starting a new one after 30 idle minutes or when the visitor
     arrives through a different campaign link (the rule Google Analytics uses too). */
  function session() {
    var current = null;
    try { current = JSON.parse(readCookie("wo_sess") || "null"); } catch (e) { current = null; }
    var landing = landingTouch();
    var arrivedViaCampaign = !!(landing.source || landing.campaign || landing.click);
    if (!current || !UUID_RE.test(current.id || "") || (arrivedViaCampaign && !sameCampaign(current.touch || {}, landing))) {
      var visits = (parseInt(readCookie("wo_visits") || "0", 10) || 0) + 1;
      writeCookie("wo_visits", String(visits), YEAR_S);
      current = { id: uuid(), visit: visits, touch: landing };
    }
    writeCookie("wo_sess", JSON.stringify(current), SESSION_IDLE_S); // idle expiry = cookie expiry
    return current;
  }

  (function teamFlag() {
    var flag = new URLSearchParams(location.search).get("wo_team");
    if (flag === "1") writeCookie("wo_team", "1", YEAR_S);
    if (flag === "0") writeCookie("wo_team", "", 0);
  })();

  // ------------------------------------------------------------------ Google Tag Manager

  if (GTM_ID) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    /* Consent Mode v2 defaults, set before the container so its tags respect them.
       Advertising signals are denied for browsers sending Global Privacy Control. */
    var ads = GPC ? "denied" : "granted";
    window.gtag("consent", "default", {
      analytics_storage: "granted", ad_storage: ads, ad_user_data: ads, ad_personalization: ads
    });
    window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    var gtm = document.createElement("script");
    gtm.async = true;
    gtm.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM_ID;
    var appendGtm = function () { document.head.appendChild(gtm); };
    if (document.readyState === "complete") appendGtm();
    else window.addEventListener("load", appendGtm);
  }

  // ------------------------------------------------------------------ sending

  function send(body, beacon) {
    if (!COLLECTOR) return;
    var json = JSON.stringify(body);
    // text/plain keeps this a CORS "simple request": no preflight round trip.
    if (beacon && navigator.sendBeacon && navigator.sendBeacon(COLLECTOR, new Blob([json], { type: "text/plain" }))) return;
    try {
      fetch(COLLECTOR, { method: "POST", body: json, keepalive: true, credentials: "omit", headers: { "Content-Type": "text/plain" } })
        .catch(function () {});
    } catch (e) { /* ignore */ }
  }

  /**
   * Record one event; returns its id (the same id goes to Meta as eventID so the browser
   * and server copies of a conversion dedupe), or null when nothing could be recorded.
   */
  function woTrack(name, props, extra) {
    try {
      var s = session();
      var t = s.touch || {};
      var id = uuid();
      var body = {
        id: id, name: name, site: "web", vid: visitorId(), sid: s.id, visit: s.visit,
        path: (location.pathname + location.search).slice(0, 512), ref: t.ref,
        utm: { source: t.source, medium: t.medium, campaign: t.campaign, content: t.content, term: t.term },
        click: t.click, props: props || {}, internal: readCookie("wo_team") === "1"
      };
      if (extra && typeof extra.dwell === "number") body.dwell = Math.round(extra.dwell);
      if (extra && typeof extra.scroll === "number") body.scroll = Math.round(extra.scroll);
      if (name === "demo_request") {
        body.fbc = readCookie("_fbc");
        body.fbp = readCookie("_fbp");
      }
      send(body, !!(extra && extra.beacon));
      return id;
    } catch (e) {
      return null;
    }
  }

  window.woTrack = woTrack;

  // ------------------------------------------------------------------ page view & exit

  var visibleMs = 0;
  var visibleSince = document.visibilityState === "visible" ? performance.now() : null;
  var maxScroll = 0;
  var exited = false;

  function scrollPct() {
    var doc = document.documentElement;
    var scrollable = doc.scrollHeight - window.innerHeight;
    return scrollable <= 0 ? 100 : Math.min(100, Math.round((window.scrollY / scrollable) * 100));
  }

  function exit() {
    if (exited) return;
    exited = true;
    if (visibleSince !== null) visibleMs += performance.now() - visibleSince;
    woTrack("page_exit", {}, { beacon: true, dwell: visibleMs, scroll: maxScroll });
  }

  maxScroll = scrollPct();
  woTrack("page_view");
  window.addEventListener("scroll", function () { maxScroll = Math.max(maxScroll, scrollPct()); }, { passive: true });
  // One exit per page view: the first of tab hidden or page hide wins.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") exit();
  });
  window.addEventListener("pagehide", exit);

  // ------------------------------------------------------------------ clicks to the app

  document.addEventListener(
    "click",
    function (event) {
      var link = event.target && event.target.closest ? event.target.closest("a[href]") : null;
      if (!link) return;
      var url;
      try { url = new URL(link.href); } catch (e) { return; }
      if (!/(^|\.)wogent\.in$/.test(url.hostname) || url.hostname === location.hostname) return;
      var cta = link.getAttribute("data-cta") || (/\/(register|signup)/.test(url.pathname) ? "sign_up" : /\/login/.test(url.pathname) ? "log_in" : "app");
      woTrack("cta_click", { cta: cta.slice(0, 60) });
      if (GTM_ID) window.dataLayer.push({ event: "cta_click", cta: cta });
    },
    { capture: true }
  );
})();
