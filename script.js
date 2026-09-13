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
      { threshold: 0.12 }
    );
    revealEls.forEach(function (el) {
      io.observe(el);
    });
  }

  /* ---------------- WhatsApp chat mockup component ----------------
     Reusable renderer: pass a container with data-wa-chat="<key>" and
     it renders a WhatsApp-style header + bubble thread from CHAT_DATA.
     Add data-wa-animate to have the thread play in message-by-message
     (used for the hero); every other instance renders statically.
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
    catalog: {
      business: "Gada Electronics",
      messages: [
        { from: "customer", text: "What's the warranty on the Havells ceiling fan?", time: "2:05" },
        { from: "agent", text: "1-year manufacturer warranty, ₹1,850, in stock in white and brown.", time: "2:05" }
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
        { from: "customer", text: "Hey, it's me again", time: "10:20" },
        { from: "agent", text: "Welcome back! Last time you ordered 9W LED bulbs — need more, or something else today?", time: "10:20" }
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
        { threshold: 0.4 }
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
