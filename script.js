(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- mobile nav ---------------- */
  var nav = document.querySelector(".nav");
  var toggle = document.querySelector(".nav-toggle");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
    nav.querySelectorAll(".nav-links a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------------- scroll reveal ---------------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) {
      el.classList.add("is-visible");
    });
  } else {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      /* Fire once the element's top edge is 10% of the viewport up from the
         bottom, whatever its height. A percentage threshold broke on tall
         blocks: the 4-phone demo grid is ~2,600px on a phone, so 12% of it
         meant scrolling ~320px into blank space before it faded in. */
      { threshold: 0, rootMargin: "0px 0px -10% 0px" }
    );
    revealEls.forEach(function (el) {
      io.observe(el);
    });
  }

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
        { from: "agent", text: "Order confirm ✅ #GE1042 — 10x Havells 9W LED bulb, ₹1,290 COD. Kal delivery thai jashe.", time: "9:43" }
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
        { from: "agent", text: "Order confirm ✅ #GE1042 — 10x Havells 9W LED bulb, ₹1,290 COD. Kal delivery thai jashe.", time: "9:43" }
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
        { from: "agent", text: "Confirmed ✅ Priya Mehta — tomorrow 3:30 PM with Dr. Shah. We'll send a reminder 1 hour before.", time: "11:04" }
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
        { from: "agent", text: "Dispatched che ✅ Aaje sanje 6 vagya pehla delivery thashe — delivery boy aavta pehla call karshe.", time: "9:12" }
      ]
    },
    photos: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", image: { kind: "photo", src: "assets/img-switch.svg", label: "Photo of a 16A modular switch" }, text: "Aa part malshe? Same joiye che", time: "4:05" },
        { from: "agent", text: "Ha malshe — aa 16A modular switch che. ₹95, stock ma che. Ketla joiye?", time: "4:05" },
        { from: "customer", image: { kind: "screenshot", label: "Payment successful · ₹190" }, text: "2 piece. Payment kari didhu", time: "4:09" },
        { from: "agent", text: "Screenshot mali gayo ✅ ₹190 for 2x 16A switch — order #GE1077 aaje dispatch thashe.", time: "4:09" }
      ]
    },
    orders: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Book 2 tube lights please", time: "5:40" },
        { from: "agent", text: "Order confirmed ✅ #GE1058 — 2x LED tube light, ₹398 total.", time: "5:41" }
      ]
    },
    memory: {
      business: "Gada Electronics",
      messages: [
        { from: "system", text: "Returning customer — last order 6 weeks ago", time: "10:20" },
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
    humanlike: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Order aavi gyo, thank you! 🙏", time: "6:32", reaction: "❤️" },
        { from: "agent", text: "Khushi thai amne! Kaik biju joi'e to kaho.", time: "6:33" }
      ]
    },
    followup: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "Geyser 15L ni price su che?", time: "1:10" },
        { from: "agent", text: "Bajaj 15L geyser ₹6,490, stock ma che. 5-year tank warranty.", time: "1:10" },
        { from: "system", text: "⏱ No reply for 2 hours — follow-up sent", time: "3:10" },
        { from: "agent", text: "Geyser vishe kai biju janvu che? Aaje order karo to kal install thai jashe.", time: "3:10" },
        { from: "customer", text: "Ha, order kari do 👍", time: "3:24" }
      ]
    },
    broadcast: {
      business: "Gada Electronics",
      messages: [
        { from: "agent", text: "🪔 Diwali offer at Gada Electronics! Special prices on all Havells fans & lights till Sunday. Reply here to order or ask anything.", time: "10:00" },
        { from: "system", text: "📣 Sent to your customer list · approved template", time: "10:00" },
        { from: "customer", text: "Ceiling fan 1200mm brown ma che? Diwali price?", time: "10:14" },
        { from: "agent", text: "Ha che! Havells Ambrose 1200mm brown — Diwali price ₹2,150, stock ma che. Ahmedabad ma free delivery.", time: "10:14" },
        { from: "customer", text: "2 pieces, COD", time: "10:15", reaction: "👍" },
        { from: "agent", text: "Order confirm ✅ #GE1103 — 2x Havells 1200mm fan (brown), ₹4,300 COD. Kal delivery thai jashe.", time: "10:15" }
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

  function renderAnimated(container, data) {
    container.innerHTML = "";
    container.appendChild(buildHeader(data.business));
    var body = document.createElement("div");
    body.className = "wa-body wa-body-scroll";
    container.appendChild(body);

    var trim = function () {
      while (body.children.length > 4) {
        body.removeChild(body.firstChild);
      }
    };

    var play = function () {
      body.innerHTML = "";
      var i = 0;

      var step = function () {
        if (i >= data.messages.length) {
          window.setTimeout(function () {
            play();
          }, 2800);
          return;
        }

        var msg = data.messages[i];
        i += 1;

        if (msg.from === "agent") {
          var typing = document.createElement("div");
          typing.className = "wa-typing";
          typing.innerHTML = "<span></span><span></span><span></span>";
          body.appendChild(typing);
          window.setTimeout(function () {
            typing.remove();
            body.appendChild(buildBubble(msg));
            trim();
            window.setTimeout(step, 1400);
          }, 850);
          return;
        }

        var bubble = buildBubble(msg, false);
        body.appendChild(bubble);
        trim();

        if (msg.reaction) {
          window.setTimeout(function () {
            bubble.appendChild(buildReaction(msg.reaction));
          }, 750);
          window.setTimeout(step, 1900);
        } else {
          window.setTimeout(step, 1300);
        }
      };

      step();
    };

    play();
  }

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
                renderAnimated(animatedChats[i].el, animatedChats[i].data);
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
        renderAnimated(item.el, item.data);
      });
    }
  }

  /* ---------------- book-a-demo modal ---------------- */

  var WHATSAPP_NUMBER = "918200962919";

  var modal = document.getElementById("demoModal");
  var modalForm = document.getElementById("demoForm");
  var modalClose = document.getElementById("demoModalClose");
  var otherBizField = document.getElementById("otherBizField");
  var otherBizInput = document.getElementById("demoOtherBiz");
  var openTriggers = document.querySelectorAll("[data-open-demo-modal]");
  var lastFocused = null;

  function focusableElements() {
    return Array.prototype.slice.call(
      modal.querySelectorAll('input, button, [href], [tabindex]:not([tabindex="-1"])')
    ).filter(function (el) {
      return !el.disabled && el.offsetParent !== null;
    });
  }

  function openModal(trigger) {
    lastFocused = trigger || document.activeElement;
    modal.hidden = false;
    document.body.style.overflow = "hidden";
    var firstRadio = modal.querySelector('input[name="biz"]:checked');
    (firstRadio || modal.querySelector("input, button")).focus();
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";
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

  modalForm.querySelectorAll('input[name="biz"]').forEach(function (radio) {
    radio.addEventListener("change", function () {
      var isOther = radio.value === "Other" && radio.checked;
      otherBizField.hidden = !isOther;
      if (isOther) {
        otherBizInput.focus();
      }
    });
  });

  modalForm.addEventListener("submit", function (event) {
    event.preventDefault();

    var biz = (modalForm.querySelector('input[name="biz"]:checked') || {}).value || "";
    var otherBiz = otherBizInput.value.trim();
    var bizLabel = biz === "Other" && otherBiz ? otherBiz : biz;
    var name = modalForm.name.value.trim();
    var city = modalForm.city.value.trim();
    var state = modalForm.state.value.trim();
    var country = modalForm.country.value.trim();

    if (!name || !city || !state || !country || (biz === "Other" && !otherBiz)) {
      modalForm.reportValidity();
      return;
    }

    var lines = [
      "Hi! I'd like to book a demo for WhatsAgent AI.",
      "",
      "Business type: " + bizLabel,
      "Name: " + name,
      "Location: " + city + ", " + state + ", " + country
    ];
    var message = lines.join("\n");
    var url = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(message);

    window.open(url, "_blank", "noopener");
    modalForm.reset();
    otherBizField.hidden = true;
    closeModal();
  });

  /* ---------------- site chat widget ----------------
     Talks to /api/chat, which holds the OpenRouter key and the assistant's
     system prompt server-side. Deliberately non-modal: it's a floating
     helper, so focus is not trapped — Escape closes it and hands focus back
     to the launcher. History lives in memory only and resets on reload. */

  var CHAT_GREETING = "Hi! Ask me anything about WhatsAgent AI.";

  /* Openers offered as tappable replies under the greeting. Edit freely —
     they are sent verbatim as the visitor's first message. */
  var CHAT_QUICK_REPLIES = [
    "How is this different from other WhatsApp bots?",
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

    CHAT_QUICK_REPLIES.forEach(function (question) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "chat-quick-btn";
      btn.textContent = question;
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
    chatPanel.hidden = false;
    chatLauncher.classList.add("is-open");
    chatLauncher.setAttribute("aria-expanded", "true");

    if (!chatGreeted) {
      appendChatMessage("bot", CHAT_GREETING);
      appendQuickReplies();
      chatGreeted = true;
    }

    chatInput.focus();
  }

  function closeChat() {
    chatPanel.hidden = true;
    chatLauncher.classList.remove("is-open");
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

  if (chatLauncher && chatPanel) {
    chatLauncher.addEventListener("click", function () {
      if (chatPanel.hidden) {
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
