(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- tracking ----------------
     One helper the rest of the page calls; it forwards to whatever is
     wired up. Google Analytics 4 loads only when WA_TRACKING.ga4MeasurementId
     is set in index.html, Meta Pixel only when WA_TRACKING.metaPixelId is —
     no ID, no script, no calls. Events used on this page:
       PageView     — on load (fired by the Pixel bootstrap)
       ViewContent  — the use-case demos scroll into view; the demo form opens
       Contact      — the site chat is opened
       Lead         — the demo form is submitted successfully
       Schedule     — same moment as Lead (a demo request is a booking ask)
     Meta gets these names as-is (they are its standard events); GA4 gets
     the snake_case equivalents in GA4_EVENTS below, with Lead mapped to its
     recommended generate_lead so it can be marked a key event. Every event
     also dispatches a DOM "wa:track" event, so another tag manager can
     listen without touching this file. */

  var TRACKING = window.WA_TRACKING || {};

  /* Set while the chat invitation bubble is on screen (see the chat widget
     block); the idle nudge on the launcher stays quiet meanwhile. */
  var teaserShowing = false;

  var GA4_EVENTS = {
    ViewContent: "view_content",
    Contact: "contact",
    Lead: "generate_lead",
    Schedule: "schedule"
  };

  function track(eventName, params) {
    params = params || {};
    try {
      if (typeof window.fbq === "function") {
        window.fbq("track", eventName, params);
      }
      if (typeof window.gtag === "function") {
        window.gtag("event", GA4_EVENTS[eventName] || eventName, params);
      }
      window.dispatchEvent(new CustomEvent("wa:track", { detail: { event: eventName, params: params } }));
    } catch (err) {
      /* Tracking must never break the page. */
    }
  }

  if (TRACKING.ga4MeasurementId) {
    /* Google's standard gtag.js bootstrap, gated on the ID. page_view fires
       from the config call, so PageView is not sent through track(). */
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", TRACKING.ga4MeasurementId);
    var gaScript = document.createElement("script");
    gaScript.async = true;
    gaScript.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(TRACKING.ga4MeasurementId);
    /* gtag.js is ~175KB of script; it waits for the page's load event so it
       never competes with the first paint. Calls made before then sit in
       dataLayer and are sent once it arrives. */
    var appendGa = function () {
      document.head.appendChild(gaScript);
    };
    if (document.readyState === "complete") appendGa();
    else window.addEventListener("load", appendGa);
  }

  if (TRACKING.metaPixelId) {
    /* Meta's standard bootstrap, unchanged apart from being gated on the ID. */
    (function (f, b, e, v, n, t, s) {
      if (f.fbq) return;
      n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n;
      n.push = n;
      n.loaded = true;
      n.version = "2.0";
      n.queue = [];
      t = b.createElement(e);
      t.async = true;
      t.src = v;
      s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    window.fbq("init", TRACKING.metaPixelId);
    window.fbq("track", "PageView");
  }

  /* Attribution read once from the landing URL; sent with every lead. */
  var PAGE_PARAMS = (function () {
    var out = {};
    try {
      var q = new URLSearchParams(window.location.search);
      ["utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach(function (k) {
        if (q.get(k)) out[k] = q.get(k);
      });
    } catch (err) {
      /* ignore */
    }
    out.source = window.location.href.split("#")[0].slice(0, 120);
    out.referrer = (document.referrer || "").slice(0, 120);
    return out;
  })();

  /* ---------------- WhatsApp chat mockup component ----------------
     Reusable renderer: pass a container with data-wa-chat="<key>" and
     it renders a WhatsApp-style header + bubble thread from CHAT_DATA.
     Add data-wa-animate to have the thread play in message-by-message
     (the hero and the use-case demo phones); every other instance renders
     statically. A message may carry `image: { kind, label, src }` to show
     a photo or payment-screenshot attachment above its text — with `src`
     it is a real image file, without one it is drawn in CSS.
  ------------------------------------------------------------------- */

  var CHAT_DATA = {
    retail: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Hii, LED bulb 9W ni price su che?", time: "9:41" },
        { from: "agent", text: "Namaste! Havells 9W LED bulb ₹129 ma available che, stock ma 40+ units che.", time: "9:41" },
        { from: "customer", text: "10 pieces joia. COD available?", time: "9:42", reaction: "👍" },
        { from: "agent", text: "Order confirm ✅ #GE1042: 10x Havells 9W LED bulb, ₹1,290 COD. Kal delivery thai jashe.", time: "9:43" }
      ]
    },
    "retail-full": {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Hii, LED bulb 9W ni price su che?", time: "9:41" },
        { from: "agent", text: "Namaste! Havells 9W LED bulb ₹129 ma available che, stock ma 40+ units che.", time: "9:41" },
        { from: "customer", text: "10 pieces joia. COD available?", time: "9:42" },
        { from: "agent", text: "Ha bilkul! 10 pieces = ₹1,290. COD available che, aajej order kari da'u?", time: "9:42" },
        { from: "customer", text: "Ha, order kari do. Delivery address same as before.", time: "9:43", reaction: "👍" },
        { from: "agent", text: "Order confirm ✅ #GE1042: 10x Havells 9W LED bulb, ₹1,290 COD. Kal delivery thai jashe.", time: "9:43" }
      ]
    },
    clinic: {
      business: "Shah Clinic",
      messages: [
        { from: "customer", text: "Hello, I need an appointment with Dr. Shah for a checkup", time: "11:02" },
        { from: "agent", text: "Hi! Dr. Shah has slots tomorrow at 11:00 AM, 3:30 PM, or 5:00 PM. Which works for you?", time: "11:02" },
        { from: "customer", text: "3:30 pm is fine", time: "11:03" },
        { from: "agent", text: "Great, booking tomorrow 3:30 PM with Dr. Shah. Can I get your full name?", time: "11:03" },
        { from: "customer", text: "Priya Mehta", time: "11:04", reaction: "👍" },
        { from: "agent", text: "Confirmed ✅ Priya Mehta, tomorrow 3:30 PM with Dr. Shah. We'll send a reminder 1 hour before.", time: "11:04" }
      ]
    },
    realestate: {
      business: "Bopal Realty",
      messages: [
        { from: "customer", text: "Hi, I saw your 2BHK listing in Bopal. Is it still available?", time: "6:15" },
        { from: "agent", text: "Yes, it's available! Can I ask your budget range and move-in timeline?", time: "6:15" },
        { from: "customer", text: "Budget around 45-50 lakh, want to move in within 2 months", time: "6:17" },
        { from: "agent", text: "Got it. This 2BHK in Bopal is ₹48L, ready to move. Want a site visit this weekend?", time: "6:17" },
        { from: "customer", text: "Yes, Saturday works", time: "6:18", reaction: "👍" },
        { from: "agent", text: "Booked ✅ Saturday 11 AM site visit. Our agent Rahul will call to confirm shortly.", time: "6:18" }
      ]
    },
    thinks: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "bhai kal mehman aave che, ghar ma AC nathi, kai jaldi setup thai jay evu?", time: "7:48" },
        { from: "system", text: "🧠 Understood: needs cooling by tomorrow, no AC installed, wants something quick", time: "7:48" },
        { from: "agent", text: "Samjhi gayo, kal sudhi cooling joiye che. Portable AC ₹24,990 aaje sanje deliver thai jashe, koi installation nathi, plug and start. Athva 1.5T split AC ₹32,500, kal savare install kari daiye. Kayu joiye?", time: "7:48" },
        { from: "customer", text: "portable j mokli do", time: "7:49", reaction: "👍" }
      ]
    },
    lang: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Bhai stock ma che ke nai, extension board?", time: "4:12" },
        { from: "agent", text: "Ha stock ma che! 4-socket ane 6-socket, be options available che.", time: "4:12" }
      ]
    },
    docs: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Stealth Air fan ma remote aave che? Warranty?", time: "2:05" },
        { from: "system", text: "📄 Havells-catalog-2026.pdf · page 40", time: "2:05" },
        { from: "agent", text: "Ha, remote included che. 2-year warranty, ₹3,950, stock ma che.", time: "2:05" }
      ]
    },
    orderstatus: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Mara order #GE1042 nu shu thayu? Kyare aavse?", time: "9:12" },
        { from: "system", text: "🔗 Checked order #GE1042 in your order system", time: "9:12" },
        { from: "agent", text: "Dispatched che ✅ Aaje sanje 6 vagya pehla delivery thashe. Delivery boy aavta pehla call karshe.", time: "9:12" }
      ]
    },
    photos: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", image: { kind: "photo", src: "assets/img-switch.svg", label: "Photo of a 16A modular switch" }, text: "Aa part malshe? Same joiye che", time: "4:05" },
        { from: "agent", text: "Ha malshe, aa 16A modular switch che. ₹95, stock ma che. Ketla joiye?", time: "4:05" },
        { from: "customer", image: { kind: "screenshot", label: "Payment successful · ₹190" }, text: "2 piece. Payment kari didhu", time: "4:09" },
        { from: "agent", text: "Screenshot mali gayo ✅ ₹190 for 2x 16A switch. Order #GE1077 aaje dispatch thashe.", time: "4:09" }
      ]
    },
    orders: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Book 2 tube lights please", time: "5:40" },
        { from: "agent", text: "Order confirmed ✅ #GE1058: 2x LED tube light, ₹398 total.", time: "5:41" }
      ]
    },
    memory: {
      business: "Gada Electronics",
      messages: [
        { from: "system", text: "Returning customer, last order 6 weeks ago", time: "10:20" },
        { from: "customer", text: "Hi, pela jeva j bulbs joiye che", time: "10:20" },
        { from: "agent", text: "Welcome back Mehul bhai! Last time tame 10x Havells 9W LED lidha hata, COD, Satellite address. Same order repeat karu?", time: "10:20" },
        { from: "customer", text: "Ha, same", time: "10:21", reaction: "👍" }
      ]
    },
    handoff: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "This is the second time my order is late, I'm not happy", time: "8:02" },
        { from: "agent", text: "I'm sorry about that. Connecting you to our store manager right now.", time: "8:02" },
        { from: "system", text: "🔔 Transferred to Ravi (Store Manager)", time: "8:02" }
      ]
    },
    broadcast: {
      business: "Gada Electronics",
      messages: [
        { from: "agent", text: "🪔 Diwali offer at Gada Electronics! Special prices on all Havells fans & lights till Sunday. Reply here to order or ask anything.", time: "10:00" },
        { from: "system", text: "📣 Sent to your customer list · approved template", time: "10:00" },
        { from: "customer", text: "Ceiling fan 1200mm brown ma che? Diwali price?", time: "10:14" },
        { from: "agent", text: "Ha che! Havells Ambrose 1200mm brown, Diwali price ₹2,150, stock ma che. Ahmedabad ma free delivery.", time: "10:14" },
        { from: "customer", text: "2 pieces, COD", time: "10:15", reaction: "👍" },
        { from: "agent", text: "Order confirm ✅ #GE1103: 2x Havells 1200mm fan (brown), ₹4,300 COD. Kal delivery thai jashe.", time: "10:15" }
      ]
    }
  };

  function tickIcon() {
    return (
      '<svg class="wa-ticks" viewBox="0 0 16 10" width="15" height="9" aria-hidden="true">' +
      '<path d="M1 5.5 4 8.5 9.5 2" fill="none" stroke="#53bdeb" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>' +
      '<path d="M5.2 5.5 8.2 8.5 14.5 1.5" fill="none" stroke="#53bdeb" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>"
    );
  }

  function initialsOf(name) {
    return name
      .split(" ")
      .map(function (w) {
        return w[0];
      })
      .join("")
      .slice(0, 2)
      .toUpperCase();
  }

  function buildHeader(business) {
    var header = document.createElement("div");
    header.className = "wa-header";
    header.innerHTML =
      '<span class="wa-avatar">' + initialsOf(business) + "</span>" +
      '<span class="wa-header-text"><strong>' + business + "</strong><span>online</span></span>";
    return header;
  }

  /* A photo or screenshot attached to a bubble. Give it `src` to show a
     real image file (a product photo, a screenshot); without one it is
     drawn in CSS — `kind` picks the look ("photo" is a camera tile,
     "screenshot" a payment-confirmation card) and `label` is the small
     caption under it. */
  function buildImage(image) {
    var el = document.createElement("span");
    el.className = "wa-image wa-image-" + (image.kind || "photo");
    if (image.src) {
      el.classList.add("wa-image-real");
      var img = document.createElement("img");
      img.src = image.src;
      img.alt = image.label || "";
      img.loading = "lazy";
      el.appendChild(img);
      return el;
    }
    var art = document.createElement("span");
    art.className = "wa-image-art";
    if (image.kind === "screenshot") {
      art.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="10" fill="#2f8f5b"/><path d="M7.5 12.5 10.5 15.5 16.5 9" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    } else {
      art.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>';
    }
    var label = document.createElement("span");
    label.className = "wa-image-label";
    label.textContent = image.label || "";
    el.appendChild(art);
    el.appendChild(label);
    return el;
  }

  /* Three copies of the emoji float up from the reaction and fade — the
     little flourish WhatsApp does when you react. GSAP-only; nothing is
     left in the DOM afterwards. */
  function burstReaction(bubble, emoji) {
    if (!window.gsap || reduceMotion) return;
    for (var i = 0; i < 3; i++) {
      var f = document.createElement("span");
      f.className = "wa-reaction-float";
      f.textContent = emoji;
      bubble.appendChild(f);
      gsap.fromTo(
        f,
        { x: 0, y: 0, scale: 0.6, autoAlpha: 1 },
        {
          x: (i - 1) * 18 + gsap.utils.random(-6, 6),
          y: -46 - i * 12,
          scale: 1.1,
          autoAlpha: 0,
          duration: 1.1,
          delay: i * 0.08,
          ease: "power1.out",
          onComplete: function (el) {
            el.remove();
          },
          onCompleteParams: [f]
        }
      );
    }
  }

  function buildReaction(emoji) {
    var r = document.createElement("span");
    r.className = "wa-reaction";
    r.textContent = emoji;
    return r;
  }

  function buildBubble(msg, includeReaction) {
    var wrap = document.createElement("div");
    if (msg.from === "system") {
      wrap.className = "wa-system";
      wrap.textContent = msg.text;
      return wrap;
    }
    wrap.className = "wa-bubble " + (msg.from === "agent" ? "wa-out" : "wa-in");
    if (msg.image) {
      wrap.classList.add("wa-has-image");
      wrap.appendChild(buildImage(msg.image));
    }
    var text = document.createElement("span");
    text.className = "wa-text";
    text.textContent = msg.text;
    var meta = document.createElement("span");
    meta.className = "wa-meta";
    meta.innerHTML = msg.time + (msg.from === "agent" ? tickIcon() : "");
    wrap.appendChild(text);
    wrap.appendChild(meta);
    if (msg.reaction && includeReaction !== false) {
      wrap.appendChild(buildReaction(msg.reaction));
    }
    return wrap;
  }

  function renderStatic(container, data) {
    container.innerHTML = "";
    container.appendChild(buildHeader(data.business));
    var body = document.createElement("div");
    body.className = "wa-body";
    data.messages.forEach(function (msg) {
      body.appendChild(buildBubble(msg));
    });
    container.appendChild(body);
  }

  /* Plays a thread message by message and loops. Returns a handle whose
     stop() cancels the pending timers — the use-case switcher needs that
     so the previous chat doesn't keep appending into the screen after a
     new one is rendered. opts.once plays a single pass and stops;
     opts.stopwatch shows a seconds counter while the agent is typing and
     flips it to a tick when the reply lands (the hero phone). */
  function renderAnimated(container, data, opts) {
    opts = opts || {};
    var once = !!opts.once;
    container.innerHTML = "";
    container.appendChild(buildHeader(data.business));
    var body = document.createElement("div");
    body.className = "wa-body wa-body-scroll";
    container.appendChild(body);

    var watch = null;
    var watchNum = null;
    if (opts.stopwatch) {
      watch = document.createElement("span");
      watch.className = "wa-stopwatch";
      watch.innerHTML = '<b>0</b>s';
      watchNum = watch.firstChild;
      container.appendChild(watch);
    }
    /* Typing takes longer on the stopwatch phone so the count has room to
       reach 7 — the number the page quotes. */
    var STOPWATCH_MAX = 7;
    var typingMs = opts.stopwatch ? 1500 : 850;

    var timers = [];
    var stopped = false;
    var later = function (fn, ms) {
      timers.push(window.setTimeout(function () {
        if (!stopped) fn();
      }, ms));
    };

    var trim = function () {
      while (body.children.length > 4) {
        body.removeChild(body.firstChild);
      }
    };

    var emit = function (type, info) {
      if (opts.onEvent) opts.onEvent(type, info || {});
    };

    var play = function () {
      body.innerHTML = "";
      var i = 0;
      emit("start");

      var step = function () {
        if (i >= data.messages.length) {
          if (!once) later(play, 2800);
          return;
        }

        var msg = data.messages[i];
        i += 1;

        if (msg.from === "agent") {
          var typing = document.createElement("div");
          typing.className = "wa-typing";
          typing.innerHTML = "<span></span><span></span><span></span>";
          body.appendChild(typing);
          emit("typing", { ms: typingMs });
          if (watch) {
            watch.className = "wa-stopwatch is-on";
            watchNum.textContent = "0";
            for (var n = 1; n <= STOPWATCH_MAX; n++) {
              (function (val) {
                later(function () {
                  watchNum.textContent = String(val);
                }, (typingMs / STOPWATCH_MAX) * val);
              })(n);
            }
          }
          later(function () {
            typing.remove();
            body.appendChild(buildBubble(msg));
            trim();
            emit("reply", msg);
            if (watch) {
              watch.className = "wa-stopwatch is-on is-done";
              later(function () {
                watch.className = "wa-stopwatch";
              }, 1100);
            }
            later(step, 1400);
          }, typingMs);
          return;
        }

        var bubble = buildBubble(msg, false);
        body.appendChild(bubble);
        trim();

        if (msg.reaction) {
          later(function () {
            bubble.appendChild(buildReaction(msg.reaction));
            burstReaction(bubble, msg.reaction);
          }, 750);
          later(step, 1900);
        } else {
          later(step, 1300);
        }
      };

      step();
    };

    play();

    return {
      stop: function () {
        stopped = true;
        timers.forEach(window.clearTimeout);
      }
    };
  }

  /* The hero phone reports its chat beats here so the floating chips can
     follow along; the motion section below fills this in. */
  var heroChatListener = null;
  var heroChatEvent = function (type, info) {
    if (heroChatListener) heroChatListener(type, info);
  };

  var animatedChats = [];
  document.querySelectorAll("[data-wa-chat]").forEach(function (el) {
    var data = CHAT_DATA[el.getAttribute("data-wa-chat")];
    if (!data) return;
    renderStatic(el, data);
    if (el.hasAttribute("data-wa-animate") && !reduceMotion) {
      animatedChats.push({ el: el, data: data });
    }
  });

  if (animatedChats.length) {
    if ("IntersectionObserver" in window) {
      var waIo = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            for (var i = 0; i < animatedChats.length; i++) {
              if (animatedChats[i].el === entry.target) {
                renderAnimated(animatedChats[i].el, animatedChats[i].data, {
                  once: animatedChats[i].el.hasAttribute("data-wa-once"),
                  stopwatch: animatedChats[i].el.hasAttribute("data-wa-stopwatch"),
                  onEvent: animatedChats[i].el.hasAttribute("data-wa-stopwatch") ? heroChatEvent : null
                });
                waIo.unobserve(entry.target);
                break;
              }
            }
          });
        },
        /* Start once a quarter of the screen is in view — high enough that
           the first message lands while the phone is still scrolling in,
           instead of the screen sitting empty until nearly half of it shows. */
        { threshold: 0.25 }
      );
      animatedChats.forEach(function (item) {
        waIo.observe(item.el);
      });
    } else {
      animatedChats.forEach(function (item) {
        renderAnimated(item.el, item.data, {
          once: item.el.hasAttribute("data-wa-once"),
          stopwatch: item.el.hasAttribute("data-wa-stopwatch"),
          onEvent: item.el.hasAttribute("data-wa-stopwatch") ? heroChatEvent : null
        });
      });
    }
  }

  /* Horizontal swipe on a touch screen: cb(+1) for a left swipe (next),
     cb(-1) for a right swipe. Vertical movement is left to the page. */
  function onSwipe(el, cb) {
    if (!el) return;
    var x0 = 0;
    var y0 = 0;
    el.addEventListener(
      "touchstart",
      function (e) {
        x0 = e.touches[0].clientX;
        y0 = e.touches[0].clientY;
      },
      { passive: true }
    );
    el.addEventListener(
      "touchend",
      function (e) {
        var dx = e.changedTouches[0].clientX - x0;
        var dy = e.changedTouches[0].clientY - y0;
        if (Math.abs(dx) > 48 && Math.abs(dy) < 40) cb(dx < 0 ? 1 : -1);
      },
      { passive: true }
    );
  }

  /* ---------------- segmented control ----------------
     .show-tabs and .demo-tabs get one sliding pill behind the active tab
     (decorative, created here so the markup stays as it is). The pill
     springs to the tab's position and width; its thin bar doubles as the
     auto-advance progress on the phone showcase. Arrow keys move between
     tabs, as a tablist should. */

  function segInit(list) {
    if (!list || list.querySelector(".seg-pill")) return;
    list.classList.add("seg");
    var pill = document.createElement("span");
    pill.className = "seg-pill";
    pill.setAttribute("aria-hidden", "true");
    pill.appendChild(document.createElement("i")).className = "seg-progress";
    list.insertBefore(pill, list.firstChild);
    var tabs = list.querySelectorAll('[role="tab"]');
    tabs.forEach(function (tab, i) {
      tab.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var next = tabs[(i + d + tabs.length) % tabs.length];
        next.focus();
        next.click();
      });
    });
    segMove(list, true);
    /* Fonts can change tab widths after first paint. */
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        segMove(list, true);
      });
    }
    window.addEventListener("resize", function () {
      segMove(list, true);
    });
  }

  function segMove(list, instant) {
    var pill = list && list.querySelector(".seg-pill");
    var tab = list && list.querySelector('[role="tab"].is-active');
    if (!pill || !tab) return;
    /* The spring lives in CSS (.seg-pill transition); placing it
       instantly just switches that transition off for one frame. */
    if (instant) pill.classList.add("seg-instant");
    pill.style.width = tab.offsetWidth + "px";
    pill.style.transform = "translateX(" + tab.offsetLeft + "px)";
    if (instant) {
      void pill.offsetWidth;
      pill.classList.remove("seg-instant");
    }
  }

  /* Fills the active pill's bar over the given seconds (0 hides it). */
  function segProgress(list, seconds) {
    var bar = list && list.querySelector(".seg-progress");
    if (!bar || !window.gsap || reduceMotion) return;
    if (!seconds) {
      gsap.to(bar, { opacity: 0, duration: 0.2, overwrite: true });
      return;
    }
    gsap.set(bar, { opacity: 1 });
    gsap.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: seconds, ease: "none", overwrite: true });
  }

  /* ---------------- use-case switcher ----------------
     One phone, four chips. Switching stops the running thread and replays
     the chosen one from the top. */

  var demoScreen = document.getElementById("demoScreen");
  var demoCaption = document.getElementById("demoCaption");
  var demoTabs = document.querySelectorAll(".demo-tab");
  var demoHandle = null;
  var demoStarted = false;

  function showDemo(key, animate) {
    var data = CHAT_DATA[key];
    if (!data || !demoScreen) return;
    if (demoHandle) demoHandle.stop();
    demoHandle = null;
    if (animate && !reduceMotion) {
      demoHandle = renderAnimated(demoScreen, data);
    } else {
      renderStatic(demoScreen, data);
    }
  }

  demoTabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      if (tab.classList.contains("is-active")) return;
      demoTabs.forEach(function (t) {
        var on = t === tab;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      segMove(tab.parentNode);
      var key = tab.getAttribute("data-demo");
      var caption = tab.getAttribute("data-caption");
      if (window.gsap && !reduceMotion) {
        /* Old chat fades down and out, the new one fades up and replays
           from its first message. */
        if (demoHandle) demoHandle.stop();
        gsap.to([demoScreen, demoCaption], {
          autoAlpha: 0,
          y: 8,
          duration: 0.2,
          ease: "power1.in",
          overwrite: true,
          onComplete: function () {
            demoCaption.textContent = caption;
            showDemo(key, true);
            gsap.fromTo(
              [demoScreen, demoCaption],
              { autoAlpha: 0, y: 8 },
              { autoAlpha: 1, y: 0, duration: 0.5, ease: "expo.out", stagger: 0.06 }
            );
          }
        });
        return;
      }
      demoCaption.textContent = caption;
      showDemo(key, true);
    });
  });

  onSwipe(document.querySelector(".demo-stage"), function (dir) {
    var tabs = Array.prototype.slice.call(demoTabs);
    var cur = tabs.findIndex(function (t) {
      return t.classList.contains("is-active");
    });
    var next = tabs[(cur + dir + tabs.length) % tabs.length];
    next.click();
    next.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
  });

  if (demoScreen) {
    showDemo("retail-full", false);
    if ("IntersectionObserver" in window) {
      var demoIo = new IntersectionObserver(
        function (entries) {
          if (entries[0].isIntersecting && !demoStarted) {
            demoStarted = true;
            track("ViewContent", { content_name: "use_case_demos" });
            if (!reduceMotion) {
              showDemo(document.querySelector(".demo-tab.is-active").getAttribute("data-demo"), true);
            }
            demoIo.disconnect();
          }
        },
        { threshold: 0.25 }
      );
      demoIo.observe(demoScreen);
    }
  }

  /* ---------------- capabilities showcase ----------------
     Six capabilities share one phone. On wide screens the block is pinned
     and scrolling walks through them (GSAP below); on narrow screens and
     under reduced motion the tabs do the same job by tap. */

  var showItems = Array.prototype.slice.call(document.querySelectorAll(".show-item"));
  var showScreens = Array.prototype.slice.call(document.querySelectorAll(".show-screen"));
  var showTabs = Array.prototype.slice.call(document.querySelectorAll(".show-tab"));

  var showTabsEl = document.querySelector(".show-tabs");
  var showIndex = 0;

  function setShow(index) {
    showIndex = index;
    showItems.forEach(function (el, i) {
      el.classList.toggle("is-active", i === index);
    });
    showScreens.forEach(function (el, i) {
      el.classList.toggle("is-active", i === index);
    });
    showTabs.forEach(function (el, i) {
      el.classList.toggle("is-active", i === index);
      el.setAttribute("aria-selected", i === index ? "true" : "false");
    });
    segMove(showTabsEl);
    /* The tab row scrolls sideways on phones: keep the active chip centred. */
    var tab = showTabs[index];
    if (tab && showTabsEl && showTabsEl.scrollWidth > showTabsEl.clientWidth) {
      showTabsEl.scrollTo({
        left: tab.offsetLeft - showTabsEl.clientWidth / 2 + tab.offsetWidth / 2,
        behavior: reduceMotion ? "auto" : "smooth"
      });
    }
  }

  /* Tab / swipe / auto-advance path (not the pinned desktop scrub): the
     chosen screen's bubbles pop in and its caption fades up. */
  function playShow(index) {
    setShow(index);
    if (!window.gsap || reduceMotion) return;
    gsap.from(showScreens[index].querySelectorAll(".wa-bubble, .wa-system"), {
      autoAlpha: 0,
      y: 12,
      scale: 0.96,
      transformOrigin: "bottom center",
      duration: 0.5,
      stagger: 0.16,
      ease: "expo.out",
      clearProps: "all"
    });
    gsap.from(showItems[index], { autoAlpha: 0, y: 8, duration: 0.35, ease: "power2.out", clearProps: "all" });
  }

  /* Set by any tap or swipe; the mobile auto-advance stops for good then. */
  var showTouched = false;

  showTabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () {
      showTouched = true;
      segProgress(showTabsEl, 0);
      playShow(i);
    });
  });
  onSwipe(document.querySelector(".show-stage"), function (dir) {
    showTouched = true;
    segProgress(showTabsEl, 0);
    playShow((showIndex + dir + showItems.length) % showItems.length);
  });
  segInit(showTabsEl);
  segInit(document.querySelector(".demo-tabs"));
  setShow(0);

  /* ---------------- springs ----------------
     No animation library for springs: they are CSS transitions on a
     linear() spring curve (styles.css, --spring-ui / --spring-pop). Button
     presses need no script at all (.btn:active). springTo() moves a small
     element to { opacity, scale, y } on one of those curves; springSet()
     puts it there with no transition. Reduced motion collapses every
     transition to ~0 in CSS, so these become instant on their own. */

  var canAnimate = !!window.gsap && !reduceMotion;

  function springProps(el, to) {
    el.style.opacity = to.opacity;
    el.style.transform = "translateY(" + (to.y || 0) + "px) scale(" + (to.scale == null ? 1 : to.scale) + ")";
  }

  function springTo(el, to, curve, delay) {
    if (!el) return;
    var d = delay ? " " + delay + "s" : "";
    var c = curve || "ui";
    el.style.transition =
      "opacity 0.25s var(--ease-ui)" + d + ", transform var(--spring-" + c + "-dur) var(--spring-" + c + ")" + d;
    springProps(el, to);
  }

  function springSet(el, to) {
    if (!el) return;
    el.style.transition = "none";
    springProps(el, to);
    void el.offsetWidth;
  }

  /* ---------------- motion (GSAP + ScrollTrigger) ----------------
     Everything in here is decoration on top of a page that already reads
     correctly without it: reduced-motion users and any load where the CDN
     script failed get the static page. */

  var hasGsap = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";

  if (hasGsap && !reduceMotion) {
    gsap.registerPlugin(ScrollTrigger);

    /* -- shared reveal: fade up 24px and clear a slight blur. Blur only on
          desktop; filters are expensive on low-end phones. -- */

    var BLUR_OK = window.matchMedia("(min-width: 901px)").matches;
    var revealFrom = function (extra) {
      var v = { y: 24, autoAlpha: 0 };
      if (BLUR_OK) v.filter = "blur(6px)";
      return Object.assign(v, extra || {});
    };
    var revealTo = function (extra) {
      var v = { y: 0, autoAlpha: 1, duration: 0.8, ease: "expo.out", clearProps: "transform,filter" };
      if (BLUR_OK) v.filter = "blur(0px)";
      return Object.assign(v, extra || {});
    };

    /* Wraps each word of el in <span class="w">; groupLines then sorts them
       into the lines the browser actually laid out, so a heading can rise
       line by line. The text is in the HTML, so it reads fine without JS. */
    var splitWords = function (el) {
      var words = el.textContent.trim().split(/\s+/);
      el.textContent = "";
      return words.map(function (w, i) {
        var s = document.createElement("span");
        s.className = "w";
        s.textContent = w;
        el.appendChild(s);
        if (i < words.length - 1) el.appendChild(document.createTextNode(" "));
        return s;
      });
    };
    var groupLines = function (spans) {
      var lines = [];
      var top = null;
      spans.forEach(function (s) {
        if (top === null || Math.abs(s.offsetTop - top) > 4) {
          lines.push([]);
          top = s.offsetTop;
        }
        lines[lines.length - 1].push(s);
      });
      return lines;
    };

    /* Heading reveal on scroll: words are hidden up front, but lines are
       measured only when the heading arrives, by which time the web fonts
       have settled the wrapping. */
    var revealHeading = function (h, words) {
      gsap.set(words, revealFrom());
      ScrollTrigger.create({
        trigger: h,
        start: "top 88%",
        once: true,
        onEnter: function () {
          groupLines(words).forEach(function (line, i) {
            gsap.fromTo(line, revealFrom(), revealTo({ delay: i * 0.1 }));
          });
        }
      });
    };

    /* -- smooth scrolling (Lenis) driving ScrollTrigger's clock -- */

    var nav = document.querySelector(".nav");
    var lenis = null;
    if (typeof window.Lenis !== "undefined" && !window.matchMedia("(pointer: coarse)").matches) {
      lenis = new Lenis({ lerp: 0.09, wheelMultiplier: 1, smoothWheel: true });
      window.__lenis = lenis;
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(function (time) {
        lenis.raf(time * 1000);
      });
      gsap.ticker.lagSmoothing(0);
      /* In-page anchors go through Lenis so they ease instead of jump.
         Lenis already honours the sections' scroll-margin-top (styles.css),
         which is what keeps them clear of the header — no extra offset. */
      document.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener("click", function (e) {
          var target = document.querySelector(a.getAttribute("href"));
          if (!target) return;
          e.preventDefault();
          lenis.scrollTo(target);
        });
      });
    }

    /* -- header: hides while you read down, returns the moment you scroll
          up; the hairline under it appears once the hero is behind you -- */

    if (nav) {
      ScrollTrigger.create({
        start: 0,
        end: "max",
        onUpdate: function (self) {
          var hide = self.scroll() > 160 && self.direction === 1 && !nav.contains(document.activeElement);
          nav.classList.toggle("is-hidden", hide);
        }
      });
      nav.addEventListener("focusin", function () {
        nav.classList.remove("is-hidden");
      });
      ScrollTrigger.create({
        trigger: ".hero",
        start: "bottom top+=80",
        end: 99999,
        toggleClass: { targets: nav, className: "is-scrolled" }
      });
    }

    /* -- hero load-in is CSS (styles.css, "Hero load-in") so the copy
          paints without waiting for this script. -- */

    /* The phone starts a touch small (CSS) and settles to full size as you
       begin to scroll, as if it is coming forward to meet you. Desktop
       only, matching the CSS. */
    gsap.matchMedia().add("(min-width: 901px)", function () {
      gsap.fromTo(
        ".hero-stage",
        { scale: 0.92 },
        {
          scale: 1,
          ease: "none",
          transformOrigin: "50% 30%",
          scrollTrigger: { trigger: ".hero", start: "top top", end: "+=40%", scrub: 0.8 }
        }
      );
    });

    /* -- hero chips follow the chat instead of floating on their own:
          the agent starts typing → "reading… thinking… typing…"; the reply
          lands → "answered in 7s" counts up; the confirmation lands → the
          order chip pops. Driven by events from renderAnimated on the
          data-wa-stopwatch phone. -- */

    var chipLang = document.querySelector(".chip-lang");
    var chipTyping = document.querySelector(".chip-typing");
    var chipOrder = document.querySelector(".chip-order");
    var chipClock = document.querySelector(".chip-clock");
    var chipState = document.querySelector(".chip-state");
    var chipClockText = chipClock ? chipClock.lastElementChild : null;
    var CHIP_HIDE = { opacity: 0, scale: 0.9, y: 6 };
    var CHIP_SHOW = { opacity: 1, scale: 1, y: 0 };
    /* Chips are small, so the "pop" curve's hint of overshoot is allowed. */
    var chipTo = springTo;
    var chipSet = springSet;

    [chipLang, chipTyping, chipOrder, chipClock].forEach(function (el) {
      chipSet(el, CHIP_HIDE);
    });
    /* After the opening panel has lifted (styles.css, --intro-out; 0s when
       the opening is skipped). */
    var introOut = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--intro-out")) || 0;
    chipTo(chipLang, CHIP_SHOW, "ui", introOut + 0.45);

    var chipStates = chipState ? chipState.getAttribute("data-states").split("|") : [];
    var chipTimers = [];
    var clearChipTimers = function () {
      chipTimers.forEach(window.clearTimeout);
      chipTimers = [];
    };
    var setChipState = function (text) {
      if (!chipState) return;
      chipState.textContent = text;
      gsap.fromTo(chipState, { opacity: 0, y: 3 }, { opacity: 1, y: 0, duration: 0.2, ease: "power1.out" });
    };
    var countClock = function () {
      if (!chipClockText) return;
      var final = chipClockText.textContent;
      var m = final.match(/^(.*?)(\d+)(\D*)$/);
      if (!m) return;
      var counter = { v: 0 };
      gsap.to(counter, {
        v: parseInt(m[2], 10),
        duration: 0.6,
        ease: "expo.out",
        onUpdate: function () {
          chipClockText.textContent = m[1] + Math.round(counter.v) + m[3];
        },
        onComplete: function () {
          chipClockText.textContent = final;
        }
      });
    };
    var heroReplies = 0;

    heroChatListener = function (type, info) {
      if (type === "start") {
        heroReplies = 0;
        clearChipTimers();
        chipTo(chipOrder, CHIP_HIDE);
        chipTo(chipClock, CHIP_HIDE);
      } else if (type === "typing") {
        clearChipTimers();
        chipTo(chipTyping, CHIP_SHOW);
        chipStates.forEach(function (text, i) {
          chipTimers.push(window.setTimeout(function () {
            setChipState(text);
          }, (info.ms / chipStates.length) * i));
        });
      } else if (type === "reply") {
        clearChipTimers();
        chipTo(chipTyping, CHIP_HIDE);
        heroReplies += 1;
        if (heroReplies === 1) {
          chipTo(chipClock, CHIP_SHOW);
          countClock();
        }
        if (/#GE\d+/.test(info.text || "")) {
          chipSet(chipOrder, { opacity: 0, scale: 0.8, y: 0 });
          chipTo(chipOrder, CHIP_SHOW, "pop");
        }
      }
    };

    /* -- section headlines rise line by line, like the hero. The showcase
          title is split here too but animated by the showcase below. -- */

    gsap.utils.toArray("[data-split]").forEach(function (h) {
      var words = splitWords(h);
      if (!h.classList.contains("show-title")) revealHeading(h, words);
    });

    /* -- mascot: the nav mark blinks on arrival and every so often; the
          chat launcher lifts gently when the page has sat idle -- */

    var eyes = document.querySelector(".nav-mark-eyes");
    if (eyes) {
      var blink = function () {
        gsap.to(eyes, { scaleY: 0.1, transformOrigin: "center", duration: 0.08, yoyo: true, repeat: 1 });
      };
      gsap.delayedCall(1.6, function () {
        blink();
        gsap.delayedCall(0.3, blink);
      });
      gsap.delayedCall(6, function tick() {
        blink();
        gsap.delayedCall(gsap.utils.random(4, 9), tick);
      });
    }

    var launcher = document.getElementById("chatLauncher");
    if (launcher) {
      var idleTimer = null;
      var nudge = function () {
        if (!document.getElementById("chatPanel").hidden || teaserShowing) return;
        gsap.timeline()
          .to(launcher, { y: -6, duration: 0.5, ease: "power2.out" })
          .to(launcher, { y: 0, duration: 0.7, ease: "power2.inOut" });
      };
      var resetIdle = function () {
        window.clearTimeout(idleTimer);
        idleTimer = window.setTimeout(nudge, 12000);
      };
      ["scroll", "mousemove", "keydown", "touchstart", "click"].forEach(function (evt) {
        window.addEventListener(evt, resetIdle, { passive: true });
      });
      resetIdle();
    }

    /* -- ticker: the track is duplicated once and slides by half its width.
          Scrolling speeds it up in proportion to scroll velocity, and the
          boost decays back to the resting pace; it pauses on hover and
          whenever it is off screen. -- */

    var tickerTrack = document.querySelector(".ticker-track");
    if (tickerTrack) {
      tickerTrack.innerHTML += tickerTrack.innerHTML;
      var verbs = gsap.utils.toArray(".ticker-item i");
      var tickerFrame = 0;
      var tickerTween = gsap.to(tickerTrack, {
        xPercent: -50,
        duration: 38,
        ease: "none",
        repeat: -1,
        onUpdate: function () {
          /* The outcome word lights up as it crosses the middle of the
             screen. Measuring every word is a layout read, so only every
             sixth frame. */
          if (tickerFrame++ % 6) return;
          var mid = window.innerWidth / 2;
          verbs.forEach(function (v) {
            var r = v.getBoundingClientRect();
            v.classList.toggle("is-hit", r.left < mid && r.right > mid);
          });
        }
      });

      var tickerBoost = 0;
      var tickerHover = false;
      var tickerOnScreen = true;
      var syncTicker = function () {
        if (tickerHover || !tickerOnScreen) tickerTween.pause();
        else tickerTween.resume();
      };
      ScrollTrigger.create({
        start: 0,
        end: "max",
        onUpdate: function (self) {
          tickerBoost = Math.max(tickerBoost, Math.min(Math.abs(self.getVelocity()) / 700, 3));
        }
      });
      gsap.ticker.add(function () {
        if (tickerBoost < 0.01 && tickerTween.timeScale() === 1) return;
        tickerBoost *= 0.93;
        if (tickerBoost < 0.01) tickerBoost = 0;
        tickerTween.timeScale(1 + tickerBoost);
      });

      var tickerEl = document.querySelector(".ticker");
      tickerEl.addEventListener("mouseenter", function () {
        tickerHover = true;
        syncTicker();
      });
      tickerEl.addEventListener("mouseleave", function () {
        tickerHover = false;
        syncTicker();
      });
      ScrollTrigger.create({
        trigger: tickerEl,
        start: "top bottom",
        end: "bottom top",
        onToggle: function (self) {
          tickerOnScreen = self.isActive;
          syncTicker();
        }
      });
    }

    /* -- how it works: the connector draws as the steps light up. On
          desktop the section pins and the scroll walks through the steps
          (the current one stays bright, the others dim); on phones there is
          no pin and the vertical connector draws as you pass. -- */

    var hiwSteps = gsap.utils.toArray(".hiw-step");
    if (hiwSteps.length) {
      var hiwFlow = document.querySelector(".hiw-flow");
      var buildHiw = function (st) {
        var tl = gsap.timeline({ scrollTrigger: st });
        tl.fromTo(
          ".hiw-line-draw",
          { strokeDasharray: "1000", strokeDashoffset: 1000 },
          { strokeDashoffset: 0, ease: "none", duration: 3 },
          0
        );
        /* Phones show a vertical connector instead; same scrub. */
        tl.fromTo(".hiw-vline i", { scaleY: 0 }, { scaleY: 1, ease: "none", duration: 3 }, 0);
        /* Steps light as the line reaches them, and unlight scrubbing back. */
        tl.eventCallback("onUpdate", function () {
          var p = tl.progress() * 3;
          var current = -1;
          hiwSteps.forEach(function (step, i) {
            var lit = p >= i * 1.05 - 0.01;
            step.classList.toggle("is-lit", lit);
            if (lit) current = i;
          });
          hiwSteps.forEach(function (step, i) {
            step.classList.toggle("is-current", i === current);
          });
        });
        return tl;
      };

      var hiwMm = gsap.matchMedia();
      hiwMm.add("(min-width: 901px)", function () {
        hiwFlow.classList.add("is-pinned");
        buildHiw({ trigger: ".hiw", start: "center center", end: "+=110%", pin: true, scrub: 0.8 });
        return function () {
          hiwFlow.classList.remove("is-pinned");
        };
      });
      hiwMm.add("(max-width: 900px)", function () {
        buildHiw({ trigger: ".hiw-flow", start: "top 72%", end: "bottom 45%", scrub: 0.6 });
      });

      hiwSteps.forEach(function (step, i) {
        gsap.fromTo(
          step,
          revealFrom(),
          revealTo({
            delay: window.innerWidth > 720 ? i * 0.08 : 0,
            scrollTrigger: { trigger: step, start: "top 88%" }
          })
        );
      });
    }

    /* -- capabilities showcase: pinned, scrubbed crossfade -- */

    var mm = gsap.matchMedia();

    mm.add("(min-width: 901px)", function () {
      var count = showItems.length;
      if (!count) return;
      setShow(0);
      showScreens.forEach(function (el, i) {
        gsap.set(el, { autoAlpha: i === 0 ? 1 : 0 });
      });

      /* The statement goes first: its words light from grey to full ink as
         you scroll (STATEMENT timeline units), then the capabilities take
         over. Opacity only, so the scrub stays on the compositor. */
      var STATEMENT = 1.2;
      var titleWords = gsap.utils.toArray(".show-title .w");
      var showTl = gsap.timeline({
        scrollTrigger: {
          trigger: ".show-pin",
          start: "top top",
          end: "+=" + (count * 70 + 60) + "%",
          pin: true,
          scrub: 0.6,
          onUpdate: function () {
            var t = (showTl.time() - STATEMENT) / (showTl.duration() - STATEMENT);
            var idx = Math.max(0, Math.min(count - 1, Math.round(t * (count - 1))));
            showItems.forEach(function (el, i) {
              el.classList.toggle("is-active", i === idx);
            });
          }
        }
      });
      if (titleWords.length) {
        showTl.fromTo(
          titleWords,
          { opacity: 0.16 },
          { opacity: 1, duration: 0.35, ease: "none", stagger: (STATEMENT - 0.35) / Math.max(1, titleWords.length - 1) },
          0
        );
      }

      /* Old screen leaves before the new one lands so two threads never
         overlap mid-scrub; then that step's bubbles pop in one by one, so
         each capability plays out as a short chat rather than appearing
         fully drawn. Scrolling back reverses it. */
      var bubblesOf = function (screen) {
        return screen.querySelectorAll(".wa-bubble, .wa-system");
      };
      for (var i = 1; i < count; i++) {
        showTl
          .to(showScreens[i - 1], { autoAlpha: 0, y: -10, duration: 0.3, ease: "power2.in" }, STATEMENT + (i - 1) + 0.45)
          .fromTo(showScreens[i], { autoAlpha: 0, y: 10 }, { autoAlpha: 1, y: 0, duration: 0.2, ease: "power2.out" }, STATEMENT + (i - 1) + 0.75)
          .from(
            bubblesOf(showScreens[i]),
            { autoAlpha: 0, y: 14, scale: 0.96, transformOrigin: "bottom center", duration: 0.18, stagger: 0.14, ease: "expo.out" },
            STATEMENT + (i - 1) + 0.85
          );
      }
      /* Padding so the last screen holds for a beat before unpinning. */
      showTl.to({}, { duration: 0.5 });

      /* The first screen isn't scrubbed — it plays as the section arrives. */
      gsap.from(bubblesOf(showScreens[0]), {
        autoAlpha: 0,
        y: 14,
        scale: 0.96,
        transformOrigin: "bottom center",
        duration: 0.6,
        stagger: 0.28,
        ease: "expo.out",
        scrollTrigger: { trigger: ".show-pin", start: "top 55%", toggleActions: "play none none reverse" }
      });

      return function () {
        showScreens.forEach(function (el) {
          gsap.set(el, { clearProps: "all" });
        });
        gsap.set(titleWords, { clearProps: "opacity" });
        setShow(0);
      };
    });

    /* On phones there is no pin: the phone walks through the capabilities
       by itself every few seconds while it is on screen, until the user
       taps a chip or swipes — then it is theirs. */
    mm.add("(max-width: 900px)", function () {
      /* No pin on phones: the statement just rises like the other headings. */
      var showTitle = document.querySelector(".show-title");
      if (showTitle) revealHeading(showTitle, gsap.utils.toArray(".show-title .w"));
      var timer = null;
      var ADVANCE_S = 4.2;
      var start = function () {
        if (timer || showTouched) return;
        segProgress(showTabsEl, ADVANCE_S);
        timer = window.setInterval(function () {
          if (showTouched) {
            window.clearInterval(timer);
            timer = null;
            return;
          }
          playShow((showIndex + 1) % showItems.length);
          segProgress(showTabsEl, ADVANCE_S);
        }, ADVANCE_S * 1000);
      };
      var stop = function () {
        window.clearInterval(timer);
        timer = null;
        segProgress(showTabsEl, 0);
      };
      var st = ScrollTrigger.create({
        trigger: ".show-stage",
        start: "top 85%",
        end: "bottom 15%",
        onToggle: function (self) {
          if (self.isActive) start();
          else stop();
        }
      });
      gsap.from(".show-stage", {
        y: 30,
        autoAlpha: 0,
        duration: 0.7,
        ease: "power3.out",
        scrollTrigger: { trigger: ".show-stage", start: "top 88%" }
      });
      return function () {
        stop();
        st.kill();
      };
    });

    /* -- front desk: cards settle in (scale 0.96 → 1 with the shared
          reveal), then each card's mini-UI plays once -- */

    gsap.utils.toArray(".desk-card").forEach(function (card, i) {
      gsap.fromTo(
        card,
        revealFrom({ scale: 0.96 }),
        revealTo({
          scale: 1,
          delay: window.innerWidth > 980 ? i * 0.08 : 0,
          scrollTrigger: { trigger: card, start: "top 88%" }
        })
      );
    });

    var campaignSteps = gsap.utils.toArray('[data-desk="campaign"] .bc-steps li');
    var campaignPill = document.querySelector('[data-desk="campaign"] .bc-pill');
    if (campaignSteps.length) {
      var campTl = gsap.timeline({
        scrollTrigger: { trigger: '[data-desk="campaign"]', start: "top 75%", once: true },
        delay: 0.3
      });
      campaignSteps.forEach(function (li, i) {
        var last = i === campaignSteps.length - 1;
        campTl.add(function () {
          li.classList.add(last ? "is-live" : "is-done");
          if (last && campaignPill) {
            /* "Sending" → "Sent": the pill settles in with a small spring. */
            campaignPill.textContent = "Sent";
            chipSet(campaignPill, { opacity: 0, scale: 0.85, y: 0 });
            chipTo(campaignPill, { opacity: 1, scale: 1, y: 0 }, "pop");
          }
        }, i * 0.55);
      });
    }

    var campBar = document.querySelector('[data-desk="campaign"] .bc-progress i');
    if (campBar && campTl) {
      campTl.fromTo(campBar, { scaleX: 0 }, { scaleX: 1, duration: 1.4, ease: "power1.inOut", transformOrigin: "left center" }, 0.9);
    }

    var inboxEl = document.querySelector('[data-desk="inbox"] .bc-inbox');
    var inboxRows = gsap.utils.toArray('[data-desk="inbox"] .bc-inbox-row');
    var hotRow = document.querySelector('[data-desk="inbox"] [data-hot]');
    var takeover = document.querySelector('[data-desk="inbox"] .bc-takeover');
    if (inboxRows.length) {
      takeover.style.transformOrigin = "right center";
      chipSet(takeover, { opacity: 0, scale: 0.6, y: 0 });

      /* Rows only ever move by transform: FLIP measures where each row is,
         lets the DOM change, then slides every row from its old place to
         its new one. */
      var flipRows = function (mutate) {
        var before = [];
        Array.prototype.forEach.call(inboxEl.children, function (r) {
          before.push([r, r.getBoundingClientRect().top]);
        });
        mutate();
        before.forEach(function (pair) {
          var r = pair[0];
          if (!r.isConnected) return;
          var dy = pair[1] - r.getBoundingClientRect().top;
          if (Math.abs(dy) > 0.5) {
            gsap.fromTo(r, { y: dy }, { y: 0, duration: 0.6, ease: "expo.out", clearProps: "transform" });
          }
        });
      };

      /* After the intro, a new enquiry drops in every few seconds and the
         oldest non-active row fades out, so the inbox looks like it is
         receiving live. Runs only while the card is on screen. */
      var INBOX_POOL = [
        { ini: "AJ", name: "Anita Joshi", text: "Fan ma 3 speed che ke 5?" },
        { ini: "DB", name: "Dhaval B", text: "Invoice moklo please" },
        { ini: "SK", name: "Sneha K", text: "Kal delivery thai shakse?" },
        { ini: "VP", name: "Vishal Parmar", text: "Geyser 25L stock ma che?" }
      ];
      var poolIdx = 0;
      var inboxTimer = null;
      var inboxOn = false;

      var pushEnquiry = function () {
        var item = INBOX_POOL[poolIdx % INBOX_POOL.length];
        poolIdx += 1;
        var row = document.createElement("div");
        row.className = "bc-inbox-row";
        row.innerHTML =
          '<span class="bc-avatar"></span>' +
          '<span class="bc-inbox-text"><strong></strong><span></span></span>' +
          '<span class="bc-stage bc-stage-new">New enquiry</span>';
        row.querySelector(".bc-avatar").textContent = item.ini;
        row.querySelector("strong").textContent = item.name;
        row.querySelector(".bc-inbox-text span").textContent = item.text;
        flipRows(function () {
          inboxEl.insertBefore(row, inboxEl.firstChild);
        });
        gsap.fromTo(row, { autoAlpha: 0, y: -10 }, { autoAlpha: 1, y: 0, duration: 0.6, ease: "expo.out", clearProps: "transform" });
        var stage = row.querySelector(".bc-stage");
        chipSet(stage, { opacity: 0, scale: 0.8, y: 0 });
        chipTo(stage, { opacity: 1, scale: 1, y: 0 }, "pop", 0.3);

        var rows = inboxEl.querySelectorAll(".bc-inbox-row");
        if (rows.length > 3) {
          var victim = null;
          for (var r = rows.length - 1; r >= 0; r--) {
            if (!rows[r].hasAttribute("data-hot")) {
              victim = rows[r];
              break;
            }
          }
          if (victim) {
            gsap.to(victim, {
              autoAlpha: 0,
              duration: 0.3,
              ease: "power1.in",
              onComplete: function () {
                flipRows(function () {
                  victim.remove();
                });
              }
            });
          }
        }
      };

      var startInbox = function () {
        if (inboxTimer || !inboxOn) return;
        inboxTimer = window.setInterval(pushEnquiry, 3600);
      };
      var stopInbox = function () {
        window.clearInterval(inboxTimer);
        inboxTimer = null;
      };

      var inboxTl = gsap.timeline({
        scrollTrigger: { trigger: '[data-desk="inbox"]', start: "top 75%", once: true },
        delay: 0.3
      });
      inboxTl
        .fromTo(inboxRows, { x: -16, autoAlpha: 0 }, { x: 0, autoAlpha: 1, duration: 0.7, stagger: 0.12, ease: "expo.out", clearProps: "transform" })
        .add(function () {
          hotRow.classList.add("is-active");
        }, "-=0.2")
        .add(function () {
          chipTo(takeover, { opacity: 1, scale: 1, y: 0 }, "pop");
        }, "+=0.3")
        .add(function () {
          inboxOn = true;
          startInbox();
        }, "+=1.2");

      ScrollTrigger.create({
        trigger: '[data-desk="inbox"]',
        start: "top bottom",
        end: "bottom top",
        onToggle: function (self) {
          if (self.isActive) startInbox();
          else stopInbox();
        }
      });
    }

    /* -- FAQ: answers open (expo.out) and close (power3.out) with GSAP,
          and a click mid-motion simply retargets from wherever the answer
          is (overwrite). The "+" turns into "×" in CSS, keyed off
          .is-closing so it turns back the moment a close starts. -- */

    gsap.utils.toArray(".faq-item").forEach(function (item) {
      var summary = item.querySelector("summary");
      var body = item.querySelector("p");
      var bodyMargin = parseFloat(getComputedStyle(body).marginBottom) || 0;
      var isOpen = item.open;
      summary.addEventListener("click", function (e) {
        e.preventDefault();
        var moving = gsap.isTweening(body);
        isOpen = !isOpen;
        item.classList.toggle("is-closing", !isOpen);
        if (isOpen && !moving) {
          item.open = true;
          gsap.set(body, { height: 0, marginBottom: 0, opacity: 0 });
        }
        body.style.overflow = "hidden";
        gsap.to(body, {
          height: isOpen ? body.scrollHeight : 0,
          marginBottom: isOpen ? bodyMargin : 0,
          opacity: isOpen ? 1 : 0,
          duration: isOpen ? 0.55 : 0.4,
          ease: isOpen ? "expo.out" : "power3.out",
          overwrite: true,
          onComplete: function () {
            if (!isOpen) {
              item.open = false;
              item.classList.remove("is-closing");
            }
            gsap.set(body, { clearProps: "height,marginBottom,opacity,overflow" });
          }
        });
      });
    });

    /* -- nav tracks the section in view -- */

    gsap.utils.toArray(".nav-links a[href^='#']").forEach(function (link) {
      var target = document.querySelector(link.getAttribute("href"));
      if (!target) return;
      ScrollTrigger.create({
        trigger: target,
        start: "top center",
        end: "bottom center",
        onToggle: function (self) {
          link.classList.toggle("is-current", self.isActive);
        }
      });
    });

    /* -- demo phone eases in once -- */

    gsap.utils.toArray(".demo-stage").forEach(function (el) {
      gsap.fromTo(el, revealFrom(), revealTo({ scrollTrigger: { trigger: el, start: "top 85%" } }));
    });

    /* -- final CTA: the band grows into place and brightens as it scrolls
          fully into view (brightness on desktop only), and the button's
          glow fades in once it arrives. It sits just above the page end, so
          both key off its bottom edge, which can always reach the bottom
          of the screen. The bubbles stay still. -- */

    var band = document.querySelector(".cta-band");
    if (band) {
      gsap.fromTo(
        band,
        BLUR_OK ? { scale: 0.94, filter: "brightness(0.88)" } : { scale: 0.94 },
        Object.assign(
          {
            scale: 1,
            ease: "none",
            scrollTrigger: { trigger: band, start: "top bottom", end: "bottom bottom", scrub: 0.8 }
          },
          BLUR_OK ? { filter: "brightness(1)" } : {}
        )
      );
      ScrollTrigger.create({
        trigger: band,
        start: "bottom bottom",
        once: true,
        onEnter: function () {
          band.classList.add("is-lit");
        }
      });
    }

    /* Chat threads render after first paint and change heights; the demo
       phone and showcase screens are fixed-height so this is a safety net
       for fonts and images arriving late. */
    /* This script is started after first paint (index.html), so the page
       may already have loaded by now. */
    if (document.readyState === "complete") {
      ScrollTrigger.refresh();
    } else {
      window.addEventListener("load", function () {
        ScrollTrigger.refresh();
      });
    }
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        ScrollTrigger.refresh();
      });
    }
  } else {
    /* Static fallback: show the finished state of every mini-animation.
       The CSS started the chips hidden and the stage small (.js); undo
       that here in case GSAP failed to load. */
    document.querySelectorAll(".hero-chip").forEach(function (chip) {
      chip.style.opacity = "1";
      chip.style.transform = "none";
    });
    var stage = document.querySelector(".hero-stage");
    if (stage) stage.style.transform = "none";
    document.querySelectorAll('[data-desk="campaign"] .bc-steps li').forEach(function (li, i, all) {
      li.classList.add(i === all.length - 1 ? "is-live" : "is-done");
    });
    var pill = document.querySelector('[data-desk="campaign"] .bc-pill');
    if (pill) pill.textContent = "Sent";
    var hot = document.querySelector('[data-desk="inbox"] [data-hot]');
    if (hot) hot.classList.add("is-active");
    var stepsAll = document.querySelectorAll(".hiw-step");
    stepsAll.forEach(function (s) {
      s.classList.add("is-lit");
    });
    var draw = document.querySelector(".hiw-line-draw");
    if (draw) draw.style.strokeDasharray = "none";
  }

  /* ---------------- book-a-demo modal ----------------
     LEAD_CHANNEL decides what "Book a demo" does with the form:
       "webhook"  — POST to /api/lead, which forwards it to LEAD_WEBHOOK_URL
                    (current Meta Ads testing flow; no WhatsApp number needed)
       "whatsapp" — open a wa.me chat to WHATSAPP_NUMBER with the details
                    prefilled (switch back once a production number is live)
  ------------------------------------------------------------------- */

  var LEAD_CHANNEL = "webhook";
  var WHATSAPP_NUMBER = "918200962919";

  var modal = document.getElementById("demoModal");
  var modalForm = document.getElementById("demoForm");
  var modalClose = document.getElementById("demoModalClose");
  var otherBizField = document.getElementById("otherBizField");
  var otherBizInput = document.getElementById("demoOtherBiz");
  var demoStatus = document.getElementById("demoStatus");
  var demoSubmit = document.getElementById("demoSubmit");
  var demoDone = document.getElementById("demoDone");
  var demoDoneClose = document.getElementById("demoDoneClose");
  var openTriggers = document.querySelectorAll("[data-open-demo-modal]");
  var lastFocused = null;
  var leadBusy = false;

  function focusableElements() {
    return Array.prototype.slice.call(
      modal.querySelectorAll('input, button, [href], [tabindex]:not([tabindex="-1"])')
    ).filter(function (el) {
      return !el.disabled && el.offsetParent !== null;
    });
  }

  /* Sheet motion (GSAP): the backdrop fades in with its blur, the sheet
     rises (expo.out) and the fields follow a beat behind. On phones the
     sheet comes up from the bottom edge and can be dragged down to
     dismiss. Under reduced motion, or without GSAP, it simply appears. */
  var modalSheet = modal.querySelector(".modal");
  var modalClosing = false;
  var modalIsSheet = function () {
    return window.matchMedia("(max-width: 720px)").matches;
  };

  function animateModalIn() {
    if (!canAnimate) return;
    var sheet = modalIsSheet();
    gsap.fromTo(modal, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: "power1.out", clearProps: "opacity" });
    gsap.fromTo(
      modalSheet,
      sheet ? { yPercent: 100, y: 0, opacity: 1 } : { yPercent: 0, y: 40, opacity: 0 },
      { yPercent: 0, y: 0, opacity: 1, duration: 0.6, ease: "expo.out", overwrite: true, clearProps: "transform,opacity" }
    );
    /* The confirmation animates its own parts in CSS; only the form's
       fields get this stagger. */
    var parts = demoDone.hidden ? modalSheet.querySelectorAll("h3, .modal-sub, #demoForm > *:not([hidden]):not(.field-hp)") : [];
    if (parts.length) gsap.fromTo(parts, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.5, ease: "expo.out", stagger: 0.04, delay: 0.08, clearProps: "transform,opacity" });
  }

  /* The phone sheet's grab strip: drag down past 120px, or flick, to
     close; anything less springs back. */
  if (modalSheet) {
    var grab = document.createElement("div");
    grab.className = "modal-grab";
    grab.setAttribute("aria-hidden", "true");
    modalSheet.insertBefore(grab, modalSheet.firstChild);
    var dragY0 = 0;
    var dragT0 = 0;
    var dragDy = 0;
    var dragging = false;
    grab.addEventListener("pointerdown", function (e) {
      if (!modalIsSheet() || !canAnimate) return;
      gsap.killTweensOf(modalSheet);
      dragging = true;
      dragY0 = e.clientY;
      dragT0 = performance.now();
      dragDy = 0;
      /* Throws NotFoundError (WebKit) if the pointer is already gone; the
         drag still works without capture. */
      try {
        grab.setPointerCapture(e.pointerId);
      } catch (err) {}
    });
    grab.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      var dy = e.clientY - dragY0;
      /* Up past the resting point resists, like a rubber band. */
      dragDy = dy > 0 ? dy : dy * 0.2;
      gsap.set(modalSheet, { y: dragDy });
    });
    var endDrag = function () {
      if (!dragging) return;
      dragging = false;
      var velocity = dragDy / Math.max(1, performance.now() - dragT0);
      if (dragDy > 120 || velocity > 0.6) {
        closeModal();
      } else {
        gsap.to(modalSheet, { y: 0, duration: 0.5, ease: "expo.out", clearProps: "transform" });
      }
    };
    grab.addEventListener("pointerup", endDrag);
    grab.addEventListener("pointercancel", endDrag);
  }

  function openModal(trigger) {
    lastFocused = trigger || document.activeElement;
    modalClosing = false;
    modal.hidden = false;
    animateModalIn();
    document.body.style.overflow = "hidden";
    if (window.__lenis) window.__lenis.stop();
    track("ViewContent", { content_name: "demo_form" });
    if (demoDone.hidden) {
      var firstRadio = modal.querySelector('input[name="biz"]:checked');
      (firstRadio || modal.querySelector("input, button")).focus();
    } else {
      demoDoneClose.focus();
    }
  }

  /* Restarts a one-shot CSS animation class (styles.css) on el. */
  function replayAnimation(el, cls) {
    el.classList.remove(cls);
    void el.offsetWidth;
    el.classList.add(cls);
    el.addEventListener("animationend", function done() {
      el.removeEventListener("animationend", done);
      el.classList.remove(cls);
    });
  }

  /* Every non-empty status here is an error: it slides in and the submit
     button shakes, so a failed tap reads as "no" even before reading. */
  function showStatus(text) {
    demoStatus.textContent = text;
    demoStatus.hidden = !text;
    if (text) {
      replayAnimation(demoStatus, "is-shown");
      replayAnimation(demoSubmit, "is-shaking");
    }
  }

  function setLeadBusy(busy) {
    leadBusy = busy;
    demoSubmit.disabled = busy;
    /* The label stays in the DOM (faded) so the button keeps its size and
       screen readers still have a name; aria-busy swaps it for the spinner. */
    demoSubmit.setAttribute("aria-busy", busy ? "true" : "false");
  }

  /* Success swaps the form for a confirmation inside the same modal; the
     form comes back cleared the next time the modal opens. */
  function showLeadDone(firstName) {
    /* The tick and copy animate in CSS (.modal-done); here the sheet
       eases from the form's height down to the confirmation's instead of
       snapping. */
    var fromHeight = modalSheet.offsetHeight;
    modalForm.hidden = true;
    demoDone.hidden = false;
    /* The confirmation stands on its own: the form's "Book a demo" title and
       intro go away, and the dialog is now named by "Demo requested". */
    setModalIntroHidden(true);
    document.getElementById("demoDoneText").textContent =
      "Thanks" + (firstName ? ", " + firstName : "") +
      ". We'll message you on WhatsApp within a working day to set up a time.";
    if (canAnimate) {
      gsap.fromTo(
        modalSheet,
        { height: fromHeight },
        { height: modalSheet.offsetHeight, duration: 0.5, ease: "expo.out", clearProps: "height" }
      );
    }
    demoDoneClose.focus();
  }

  function setModalIntroHidden(hide) {
    document.getElementById("demoModalTitle").hidden = hide;
    modalSheet.querySelector(".modal-sub").hidden = hide;
    modalSheet.setAttribute("aria-labelledby", hide ? "demoDoneTitle" : "demoModalTitle");
  }

  function resetLeadForm() {
    setModalIntroHidden(false);
    modalForm.reset();
    otherBizField.hidden = true;
    labelDialOptions(false);
    syncStateField();
    flagImg.src = "https://flagcdn.com/w40/" + selectedCountry().iso + ".png";
    lastAutoCountry = countryInput.value;
    showStatus("");
    setLeadBusy(false);
    modalForm.hidden = false;
    demoDone.hidden = true;
  }

  function closeModal(after) {
    if (modal.hidden || modalClosing) return;
    if (canAnimate) {
      modalClosing = true;
      var sheet = modalIsSheet();
      gsap.to(modal, { opacity: 0, duration: 0.22, delay: 0.05, ease: "power1.in" });
      gsap.to(modalSheet, {
        y: sheet ? modalSheet.offsetHeight : 24,
        opacity: sheet ? 1 : 0,
        duration: 0.28,
        ease: "power2.in",
        overwrite: true,
        onComplete: function () {
          if (!modalClosing) return;
          modalClosing = false;
          finishCloseModal();
          if (typeof after === "function") after();
        }
      });
      return;
    }
    finishCloseModal();
    if (typeof after === "function") after();
  }

  function finishCloseModal() {
    modal.hidden = true;
    if (window.gsap) {
      gsap.set(modal, { clearProps: "opacity" });
      gsap.set(modalSheet, { clearProps: "transform,opacity" });
    }
    document.body.style.overflow = "";
    if (window.__lenis) window.__lenis.start();
    if (lastFocused) {
      lastFocused.focus();
    }
  }

  openTriggers.forEach(function (btn) {
    btn.addEventListener("click", function () {
      openModal(btn);
    });
  });

  modalClose.addEventListener("click", closeModal);
  /* The form is reset only once the sheet has gone, so it doesn't swap
     back into view during the close animation. */
  demoDoneClose.addEventListener("click", function () {
    closeModal(resetLeadForm);
  });

  modal.addEventListener("click", function (event) {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (modal.hidden) return;
    if (event.key === "Escape") {
      closeModal();
      return;
    }
    if (event.key === "Tab") {
      var focusable = focusableElements();
      if (!focusable.length) return;
      var first = focusable[0];
      var last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
  });

  /* The "Other" field opens to its height and fades in (and closes the
     same way) instead of appearing and shoving the form down. */
  function toggleOtherBiz(show) {
    var f = otherBizField;
    if (show === !f.hidden && !(window.gsap && gsap.isTweening(f))) return;
    if (!canAnimate) {
      f.hidden = !show;
      return;
    }
    var margin = 18;
    if (show) {
      f.hidden = false;
      gsap.fromTo(
        f,
        { height: 0, opacity: 0, marginBottom: 0, overflow: "hidden" },
        { height: "auto", opacity: 1, marginBottom: margin, duration: 0.35, ease: "expo.out", overwrite: true, clearProps: "height,opacity,marginBottom,overflow" }
      );
    } else {
      gsap.to(f, {
        height: 0,
        opacity: 0,
        marginBottom: 0,
        overflow: "hidden",
        duration: 0.25,
        ease: "power3.out",
        overwrite: true,
        onComplete: function () {
          f.hidden = true;
          gsap.set(f, { clearProps: "height,opacity,marginBottom,overflow" });
        }
      });
    }
  }

  modalForm.querySelectorAll('input[name="biz"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
      var isOther = radio.value === "Other" && radio.checked;
      toggleOtherBiz(isOther);
      if (isOther) {
        otherBizInput.focus();
      }
    });
  });

  /* Country codes for the WhatsApp number. India first (the default), the
     rest alphabetical. [ISO code, name, dial code]; the flag comes from
     flagcdn.com by ISO code. Add a row to offer another country. */
  var COUNTRY_CODES = [
    ["in", "India", "91"],
    ["au", "Australia", "61"], ["bh", "Bahrain", "973"], ["bd", "Bangladesh", "880"],
    ["br", "Brazil", "55"], ["ca", "Canada", "1"], ["cn", "China", "86"],
    ["eg", "Egypt", "20"], ["fr", "France", "33"], ["de", "Germany", "49"],
    ["hk", "Hong Kong", "852"], ["id", "Indonesia", "62"], ["ie", "Ireland", "353"],
    ["it", "Italy", "39"], ["jp", "Japan", "81"], ["ke", "Kenya", "254"],
    ["kw", "Kuwait", "965"], ["my", "Malaysia", "60"], ["mu", "Mauritius", "230"],
    ["mx", "Mexico", "52"], ["np", "Nepal", "977"], ["nl", "Netherlands", "31"],
    ["nz", "New Zealand", "64"], ["ng", "Nigeria", "234"], ["om", "Oman", "968"],
    ["pk", "Pakistan", "92"], ["ph", "Philippines", "63"], ["pt", "Portugal", "351"],
    ["qa", "Qatar", "974"], ["sa", "Saudi Arabia", "966"], ["sg", "Singapore", "65"],
    ["za", "South Africa", "27"], ["kr", "South Korea", "82"], ["es", "Spain", "34"],
    ["lk", "Sri Lanka", "94"], ["se", "Sweden", "46"], ["ch", "Switzerland", "41"],
    ["tz", "Tanzania", "255"], ["th", "Thailand", "66"], ["tr", "Turkey", "90"],
    ["ae", "United Arab Emirates", "971"], ["gb", "United Kingdom", "44"],
    ["us", "United States", "1"], ["vn", "Vietnam", "84"]
  ];

  var INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh",
    "Lakshadweep", "Puducherry"
  ];

  var phoneInput = document.getElementById("demoPhone");
  var dialSelect = document.getElementById("demoDial");
  var flagImg = document.getElementById("demoFlag");
  var countryInput = document.getElementById("demoCountry");
  var stateInput = document.getElementById("demoState");
  var stateSelect = document.getElementById("demoStateSelect");

  (function () {
    var first = document.createElement("option");
    first.value = "";
    first.textContent = "Select state";
    stateSelect.appendChild(first);
    INDIAN_STATES.forEach(function (name) {
      var opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      stateSelect.appendChild(opt);
    });
  })();

  /* India gets the state list; everywhere else a free-text box. */
  function syncStateField() {
    var india = selectedCountry().iso === "in";
    stateSelect.hidden = !india;
    stateInput.hidden = india;
  }

  COUNTRY_CODES.forEach(function (row, i) {
    var opt = document.createElement("option");
    opt.value = row[0];
    opt.textContent = "+" + row[2] + "  " + row[1];
    opt.setAttribute("data-dial", row[2]);
    opt.setAttribute("data-name", row[1]);
    if (i === 0) opt.selected = true;
    dialSelect.appendChild(opt);
  });

  function selectedCountry() {
    var opt = dialSelect.options[dialSelect.selectedIndex];
    return { iso: opt.value, name: opt.getAttribute("data-name"), dial: opt.getAttribute("data-dial") };
  }

  /* A native select shows its chosen option's text, so the closed box would
     read "+91  India" and crowd the row. The list gets full labels while it
     is open; once closed, the chosen option's label shrinks to its code. */
  function labelDialOptions(open) {
    Array.prototype.forEach.call(dialSelect.options, function (opt) {
      var full = "+" + opt.getAttribute("data-dial") + "  " + opt.getAttribute("data-name");
      opt.textContent = open || !opt.selected ? full : "+" + opt.getAttribute("data-dial");
    });
  }
  labelDialOptions(false);
  syncStateField();
  dialSelect.addEventListener("focus", function () {
    labelDialOptions(true);
  });
  dialSelect.addEventListener("blur", function () {
    labelDialOptions(false);
  });

  /* Picking a code updates the flag, and fills the Country box unless the
     visitor has typed their own value there. */
  var lastAutoCountry = countryInput.value;
  dialSelect.addEventListener("change", function () {
    var c = selectedCountry();
    labelDialOptions(false);
    syncStateField();
    flagImg.src = "https://flagcdn.com/w40/" + c.iso + ".png";
    if (countryInput.value.trim() === lastAutoCountry) {
      countryInput.value = c.name;
      lastAutoCountry = c.name;
    }
  });

  /* The number field only ever holds digits: anything else typed or pasted
     is dropped on the spot. */
  phoneInput.addEventListener("input", function () {
    var digits = phoneInput.value.replace(/[^\d]/g, "");
    if (digits !== phoneInput.value) phoneInput.value = digits;
  });

  /* Dial code + national number -> one international number, digits only.
     A leading 0 on the national part (common in India: 098765...) is
     dropped. Returns "" when it can't be a WhatsApp number. */
  function normalisePhone(national, dial) {
    var digits = String(national || "").replace(/[^\d]/g, "").replace(/^0+/, "");
    if (digits.length < 6 || digits.length > 12) return "";
    var full = dial + digits;
    if (full.length < 10 || full.length > 15) return "";
    return full;
  }

  function readLead() {
    var biz = (modalForm.querySelector('input[name="biz"]:checked') || {}).value || "";
    var automate = (modalForm.querySelector('input[name="automate"]:checked') || {}).value || "";
    return {
      biz: biz,
      otherBiz: otherBizInput.value.trim(),
      name: modalForm.name.value.trim(),
      phone: modalForm.phone.value.trim(),
      dial: selectedCountry().dial,
      city: modalForm.city.value.trim(),
      state: (selectedCountry().iso === "in" ? stateSelect.value : stateInput.value).trim(),
      country: modalForm.country.value.trim(),
      automate: automate,
      website: modalForm.website.value
    };
  }

  /* Letters, spaces and the punctuation place names use; 2 to 60 chars.
     Mirrors api/lead.js. */
  var PLACE_RE = /^[A-Za-z][A-Za-z .'\-]{1,59}$/;
  var COUNTRY_NAMES = {};
  COUNTRY_CODES.forEach(function (row) {
    COUNTRY_NAMES[row[1].toLowerCase()] = row[1];
  });

  /* Mirrors api/lead.js so the visitor sees the problem before a round trip. */
  function validateLead(lead) {
    if (lead.biz === "Other" && !lead.otherBiz) return "Tell us your business type.";
    if (!lead.name) return "Add your name.";
    if (!lead.phone.trim()) return "Add your WhatsApp number.";
    if (/[^\d]/.test(lead.phone)) return "WhatsApp number should be numbers only.";
    var full = normalisePhone(lead.phone, lead.dial);
    if (!full) return "That doesn't look like a complete WhatsApp number. Check the digits and the country code.";
    lead.phone = full;
    if (!lead.city) return "Add your city.";
    if (!PLACE_RE.test(lead.city)) return "City should be letters only.";
    if (!lead.state) return selectedCountry().iso === "in" ? "Pick your state." : "Add your state.";
    if (!PLACE_RE.test(lead.state)) return "State should be letters only.";
    if (!lead.country) return "Add your country.";
    if (!COUNTRY_NAMES[lead.country.toLowerCase()]) return "Pick a country from the code list, or type its name in full.";
    lead.country = COUNTRY_NAMES[lead.country.toLowerCase()];
    if (!lead.automate) return "Pick what you'd like to automate.";
    return "";
  }

  function openWhatsAppLead(lead) {
    var bizLabel = lead.biz === "Other" && lead.otherBiz ? lead.otherBiz : lead.biz;
    var lines = [
      "Hi! I'd like to book a demo for Wogent.",
      "",
      "Business type: " + bizLabel,
      "Name: " + lead.name,
      "WhatsApp: " + lead.phone,
      "Location: " + lead.city + ", " + lead.state + ", " + lead.country,
      "Want to automate: " + lead.automate
    ];
    var url = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(lines.join("\n"));
    window.open(url, "_blank", "noopener");
  }

  modalForm.addEventListener("submit", function (event) {
    event.preventDefault();
    if (leadBusy) return;

    var lead = readLead();
    var problem = validateLead(lead);
    if (problem) {
      showStatus(problem);
      var invalid = modalForm.querySelector(":invalid");
      if (invalid) invalid.focus();
      return;
    }
    showStatus("");

    if (LEAD_CHANNEL === "whatsapp") {
      openWhatsAppLead(lead);
      track("Lead", { content_name: "demo_form", channel: "whatsapp" });
      track("Schedule", { content_name: "demo_form" });
      showLeadDone(lead.name.split(" ")[0]);
      return;
    }

    setLeadBusy(true);
    var payload = Object.assign({}, lead, PAGE_PARAMS);

    fetch("/api/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(function (res) {
        if (res.status === 404) {
          /* Static hosting without the api/ directory — a dev-setup issue,
             logged for the developer, never shown to the visitor as such. */
          console.warn("lead: /api/lead returned 404 — run with `vercel dev` or deploy with the api/ directory.");
          throw new Error("no-endpoint");
        }
        return res.json().then(function (data) {
          return { ok: res.ok, data: data || {} };
        });
      })
      .then(function (result) {
        setLeadBusy(false);
        if (!result.ok) {
          showStatus(result.data.error || "Couldn't send your request. Please try again.");
          return;
        }
        track("Lead", { content_name: "demo_form", channel: "webhook", automate: lead.automate });
        track("Schedule", { content_name: "demo_form" });
        showLeadDone(lead.name.split(" ")[0]);
      })
      .catch(function (err) {
        setLeadBusy(false);
        showStatus(
          err && err.message === "no-endpoint"
            ? "Booking isn't available right now. Please try again in a little while."
            : "Couldn't reach the server. Check your connection and try again."
        );
      });
  });

  /* ---------------- site chat widget ----------------
     Talks to /api/chat, which holds the OpenRouter key and the assistant's
     system prompt server-side. Deliberately non-modal: it's a floating
     helper, so focus is not trapped — Escape closes it and hands focus back
     to the launcher. History lives in memory only and resets on reload. */

  var CHAT_GREETING = "Hi! I'm the Wogent assistant. Ask me what it would do for your business, or start with one of these:";

  /* Openers offered as tappable replies under the greeting. Edit freely —
     they are sent verbatim as the visitor's first message. */
  var CHAT_QUICK_REPLIES = [
    "What would it do for my shop?",
    "Which languages does it support?",
    "How long does setup take?"
  ];

  /* How many turns of context to send. The endpoint caps this too. */
  var CHAT_HISTORY_TURNS = 10;

  var chatLauncher = document.getElementById("chatLauncher");
  var chatPanel = document.getElementById("chatPanel");
  var chatClose = document.getElementById("chatClose");
  var chatLog = document.getElementById("chatLog");
  var chatForm = document.getElementById("chatForm");
  var chatInput = document.getElementById("chatInput");
  var chatSend = document.getElementById("chatSend");

  var chatHistory = [];
  var chatBusy = false;
  var chatGreeted = false;
  var typingEl = null;

  function scrollChatDown() {
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  /* textContent, never innerHTML — the reply is model output. */
  function appendChatMessage(role, text) {
    var el = document.createElement("div");
    el.className = "chat-msg chat-msg-" + role;
    el.textContent = text;
    chatLog.appendChild(el);
    scrollChatDown();
    return el;
  }

  /* Failures show as a centred system line rather than a message bubble —
     they come from the page, not from the assistant, and a run of them
     should read as quiet status rather than three alarms. */
  function appendChatNote(text) {
    var el = document.createElement("p");
    el.className = "chat-note";
    el.textContent = text;
    chatLog.appendChild(el);
    scrollChatDown();
  }

  /* Openers live inside the log, the way quick replies do in a messaging
     app, so they scroll away with the conversation instead of holding a
     permanent bar above the input. */
  function appendQuickReplies() {
    var wrap = document.createElement("div");
    wrap.className = "chat-quick";

    CHAT_QUICK_REPLIES.forEach(function (question, i) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chat-quick-btn";
      btn.textContent = question;
      /* Rise in one after another, after the greeting bubble lands. */
      btn.style.animationDelay = 0.15 + i * 0.04 + "s";
      btn.addEventListener("click", function () {
        if (chatBusy) return;
        wrap.remove();
        sendChatMessage(question);
      });
      wrap.appendChild(btn);
    });

    chatLog.appendChild(wrap);
    scrollChatDown();
  }

  function clearQuickReplies() {
    var wrap = chatLog.querySelector(".chat-quick");
    if (wrap) wrap.remove();
  }

  function showTyping() {
    typingEl = document.createElement("div");
    typingEl.className = "chat-typing";
    typingEl.setAttribute("aria-label", "Typing");
    for (var i = 0; i < 3; i++) {
      typingEl.appendChild(document.createElement("span"));
    }
    chatLog.appendChild(typingEl);
    scrollChatDown();
  }

  function hideTyping() {
    if (typingEl && typingEl.parentNode) {
      typingEl.parentNode.removeChild(typingEl);
    }
    typingEl = null;
  }

  function setChatBusy(busy) {
    chatBusy = busy;
    chatSend.disabled = busy;
    chatInput.disabled = busy;
  }

  function openChat() {
    chatPanel.classList.remove("is-closing");
    chatPanel.hidden = false;
    chatLauncher.classList.add("is-open", "has-toggled");
    chatLauncher.setAttribute("aria-expanded", "true");

    if (!chatGreeted) {
      appendChatMessage("bot", CHAT_GREETING);
      appendQuickReplies();
      chatGreeted = true;
      track("Contact", { content_name: "site_chat" });
    }

    chatInput.focus();
  }

  function closeChat() {
    /* Shrinks back into the launcher (styles.css .is-closing), then hides.
       Reduced motion: hide straight away. */
    if (reduceMotion) {
      chatPanel.hidden = true;
    } else if (!chatPanel.classList.contains("is-closing")) {
      chatPanel.classList.add("is-closing");
      var finish = function () {
        chatPanel.removeEventListener("animationend", onEnd);
        window.clearTimeout(fallback);
        if (chatPanel.classList.contains("is-closing")) {
          chatPanel.classList.remove("is-closing");
          chatPanel.hidden = true;
        }
      };
      var onEnd = function (e) {
        if (e.target === chatPanel) finish();
      };
      /* Safety net in case animationend never fires. */
      var fallback = window.setTimeout(finish, 400);
      chatPanel.addEventListener("animationend", onEnd);
    }
    chatLauncher.classList.remove("is-open");
    chatLauncher.classList.add("has-toggled");
    chatLauncher.setAttribute("aria-expanded", "false");
    chatLauncher.focus();
  }

  function sendChatMessage(text) {
    var message = text.trim();
    if (!message || chatBusy) return;

    clearQuickReplies();
    appendChatMessage("user", message);
    chatHistory.push({ role: "user", content: message });
    chatInput.value = "";
    setChatBusy(true);
    showTyping();

    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: chatHistory.slice(-CHAT_HISTORY_TURNS) })
    })
      .then(function (res) {
        /* A plain static server has no /api/chat and answers 404 with HTML,
           which would blow up res.json() and look like a network failure.
           Name that case instead — it means "run vercel dev", not "check
           your wifi". */
        if (res.status === 404) {
          /* Diagnosis goes to the console, not to the visitor — they should
             never be told to run a dev command. */
          console.warn(
            "chat: /api/chat returned 404 — this page is being served without " +
              "its serverless function. Run the site with `vercel dev` locally, " +
              "and deploy to a host that runs the api/ directory."
          );
          throw new Error("no-endpoint");
        }
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (result) {
        hideTyping();
        if (!result.ok || !result.data.reply) {
          appendChatNote(
            result.data.error ||
              "Something went wrong. Try again, or book a demo and we'll answer personally."
          );
          /* Drop the unanswered turn so it doesn't poison later context. */
          chatHistory.pop();
          return;
        }
        appendChatMessage("bot", result.data.reply);
        chatHistory.push({ role: "assistant", content: result.data.reply });
      })
      .catch(function (err) {
        hideTyping();
        chatHistory.pop();
        appendChatNote(
          err && err.message === "no-endpoint"
            ? "Chat isn't available right now. Book a demo and we'll answer you personally."
            : "Couldn't reach the server. Check your connection and try again."
        );
      })
      .then(function () {
        setChatBusy(false);
        chatInput.focus();
      });
  }

  /* ---------------- chat invitation ----------------
     A small bubble above the launcher a few seconds after arrival, once per
     browser session: the "trailer before the movie". Tapping it opens the
     chat; the close button or 20 seconds dismisses it. Never shown once the
     panel has been opened. */

  var teaser = document.getElementById("chatTeaser");
  var teaserOpen = document.getElementById("chatTeaserOpen");
  var teaserClose = document.getElementById("chatTeaserClose");
  var teaserHideTimer = null;

  function teaserSeen() {
    try {
      return sessionStorage.getItem("wa-teaser") === "1";
    } catch (err) {
      return false;
    }
  }

  function markTeaserSeen() {
    try {
      sessionStorage.setItem("wa-teaser", "1");
    } catch (err) {
      /* private mode: show it again next load, no harm */
    }
  }

  function hideTeaser() {
    if (!teaser || teaser.hidden) return;
    window.clearTimeout(teaserHideTimer);
    teaserShowing = false;
    if (window.gsap && !reduceMotion) {
      gsap.to(teaser, {
        y: 10,
        autoAlpha: 0,
        duration: 0.25,
        ease: "power2.in",
        onComplete: function () {
          teaser.hidden = true;
        }
      });
    } else {
      teaser.hidden = true;
    }
  }

  function showTeaser() {
    if (!teaser || !chatPanel.hidden || teaserSeen()) return;
    markTeaserSeen();
    teaser.hidden = false;
    teaserShowing = true;
    if (window.gsap && !reduceMotion) {
      gsap.fromTo(
        teaser,
        { y: 16, scale: 0.96, autoAlpha: 0, transformOrigin: "bottom right" },
        { y: 0, scale: 1, autoAlpha: 1, duration: 0.6, ease: "expo.out" }
      );
    }
    teaserHideTimer = window.setTimeout(hideTeaser, 20000);
    /* Reading on is an answer too: once they scroll a screen past where
       the bubble appeared, it gets out of the way. */
    var shownAt = window.scrollY;
    var onScroll = function () {
      if (Math.abs(window.scrollY - shownAt) > window.innerHeight) {
        window.removeEventListener("scroll", onScroll);
        hideTeaser();
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (teaser && chatLauncher && chatPanel) {
    window.setTimeout(showTeaser, 6000);
    teaserOpen.addEventListener("click", function () {
      hideTeaser();
      openChat();
    });
    teaserClose.addEventListener("click", hideTeaser);
  }

  if (chatLauncher && chatPanel) {
    chatLauncher.addEventListener("click", function () {
      if (chatPanel.hidden) {
        hideTeaser();
        openChat();
      } else {
        closeChat();
      }
    });

    chatClose.addEventListener("click", closeChat);

    chatForm.addEventListener("submit", function (event) {
      event.preventDefault();
      sendChatMessage(chatInput.value);
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !chatPanel.hidden) {
        closeChat();
      }
    });
  }
})();
