/* AtlasPlay: perilaku bersama (publik + admin): toast, dialog konfirmasi, menu, drawer, reveal saat scroll. */
(function () {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const csrf = () => (document.querySelector('meta[name="csrf-token"]') || {}).content || "";
  const NP = (window.NP = window.NP || {});
  NP.csrf = csrf;
  NP.reduceMotion = reduceMotion;

  const ICONS = {
    success: '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8L16 9.5"/></svg>',
    error: '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.4v.1"/></svg>',
    info: '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.1"/></svg>',
    close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>',
  };


  /* ------------------------------------- warna dominan gambar (canvas) ------ */
  const ACCENT = "#34D399";
  const dominantCache = new Map();
  NP.dominant = function (src) {
    if (!src) return Promise.resolve(ACCENT);
    if (dominantCache.has(src)) return dominantCache.get(src);
    const job = new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.decoding = "async";
      img.onload = () => {
        try {
          const size = 36;
          const canvas = document.createElement("canvas");
          canvas.width = canvas.height = size;
          const ctx = canvas.getContext("2d", { willReadFrequently: true });
          ctx.drawImage(img, 0, 0, size, size);
          const data = ctx.getImageData(0, 0, size, size).data;
          const buckets = Array.from({ length: 12 }, () => ({ w: 0, r: 0, g: 0, b: 0 }));
          let total = 0;
          for (let i = 0; i < data.length; i += 4) {
            if (data[i + 3] < 200) continue;
            const r = data[i] / 255, g = data[i + 1] / 255, b = data[i + 2] / 255;
            const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
            if (max < 0.16 || d < 0.08) continue;
            const s = d / max;
            let h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
            h = (h * 60 + 360) % 360;
            const weight = s * s * max;
            const k = buckets[Math.floor(h / 30) % 12];
            k.w += weight; k.r += r * weight; k.g += g * weight; k.b += b * weight; total += weight;
          }
          if (total < 0.5) return resolve(ACCENT);
          const best = buckets.reduce((a, c) => (c.w > a.w ? c : a));
          resolve(normalizeColor(best.r / best.w, best.g / best.w, best.b / best.w));
        } catch (err) { resolve(ACCENT); }   // canvas tercemar (gambar dari domain lain)
      };
      img.onerror = () => resolve(ACCENT);
      img.src = src;
    });
    dominantCache.set(src, job);
    return job;
  };
  /* Naikkan kecerahan dan kejenuhan seperlunya supaya warna tetap terbaca di latar gelap. */
  function normalizeColor(r, g, b) {
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0; const l = (max + min) / 2, d = max - min;
    if (d) {
      s = d / (1 - Math.abs(2 * l - 1));
      h = max === r ? ((g - b) / d) % 6 : max === g ? (b - r) / d + 2 : (r - g) / d + 4;
      h = (h * 60 + 360) % 360;
    }
    s = Math.min(0.85, Math.max(s, 0.5));
    const L = Math.min(0.62, Math.max(l, 0.5));
    const c = (1 - Math.abs(2 * L - 1)) * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = L - c / 2;
    const [rr, gg, bb] = h < 60 ? [c, x, 0] : h < 120 ? [x, c, 0] : h < 180 ? [0, c, x] : h < 240 ? [0, x, c] : h < 300 ? [x, 0, c] : [c, 0, x];
    const hex = (v) => Math.round((v + m) * 255).toString(16).padStart(2, "0");
    return "#" + hex(rr) + hex(gg) + hex(bb);
  }
  /* Backdrop poster blur dinamis: dua lapis gambar bergantian untuk crossfade 0.7 detik.
     base = gambar halaman (slide aktif / game detail); hover poster menimpanya sementara. */
  NP.backdrop = (() => {
    const root = document.querySelector("[data-backdrop]");
    const layers = root ? Array.from(root.querySelectorAll(".backdrop__img")) : [];
    let cur = -1, shown = "", base = "", token = 0, restoreTimer = 0, hovering = false;
    const fallback = () => {
      const img = document.querySelector("[data-poster] .poster__img");
      return img ? img.currentSrc || img.src : "";
    };
    const show = (src) => {
      if (!layers.length || src === shown) return;
      shown = src;
      const mine = ++token;
      if (!src) { layers.forEach((l) => l.classList.remove("is-on")); cur = -1; return; }
      const next = layers[cur === 0 ? 1 : 0];
      const probe = new Image();
      const swap = () => {
        if (mine !== token) return;     // sudah ada permintaan yang lebih baru
        next.src = src;
        next.getBoundingClientRect();
        next.classList.add("is-on");
        layers.forEach((l) => { if (l !== next) l.classList.remove("is-on"); });
        cur = layers.indexOf(next);
      };
      probe.onload = probe.onerror = swap;
      probe.src = src;
    };
    return {
      setBase(src) { base = src || ""; if (!hovering) show(base || fallback()); },
      hover(src) { clearTimeout(restoreTimer); hovering = true; if (src) show(src); },
      restore() {
        clearTimeout(restoreTimer);
        restoreTimer = setTimeout(() => { hovering = false; show(base || fallback()); }, 140);
      },
      init() { if (!hovering && !shown) show(base || fallback()); },
    };
  })();
  document.addEventListener("DOMContentLoaded", () => NP.backdrop.init());

  NP.setGlow = (color) => { document.documentElement.style.setProperty("--glow", color || ACCENT); };

  /* Kartu poster: warna dominan cover untuk border/glow kartu dan cahaya latar saat hover */
  let hoverCard = null;
  const paintPoster = (card) => {
    if (!card) return Promise.resolve(ACCENT);
    if (card._glow) return card._glow;
    const img = card.querySelector(".poster__img");
    card._glow = NP.dominant(img ? img.currentSrc || img.src : "").then((c) => { card.style.setProperty("--gc", c); return c; });
    return card._glow;
  };
  const enterCard = (card) => {
    if (!card || card === hoverCard) return;
    hoverCard = card;
    const pimg = card.querySelector(".poster__img");
    NP.backdrop.hover(pimg ? pimg.currentSrc || pimg.src : "");
    paintPoster(card).then((c) => { if (hoverCard === card) { NP.hoverGlow = true; NP.setGlow(c); } });
  };
  const leaveCard = () => {
    if (!hoverCard) return;
    hoverCard = null; NP.hoverGlow = false;
    NP.backdrop.restore();
    NP.setGlow(NP.baseGlow || ACCENT);
  };
  document.addEventListener("pointerover", (e) => {
    const card = e.target.closest && e.target.closest("[data-poster]");
    if (card) enterCard(card); else leaveCard();
  });
  document.addEventListener("focusin", (e) => enterCard(e.target.closest && e.target.closest("[data-poster]")));
  document.addEventListener("focusout", leaveCard);

  /* Kartu poster: tilt 3D (maks 6 derajat) dan kilau yang mengikuti kursor */
  if (!reduceMotion && window.matchMedia("(hover: hover)").matches) {
    let active = null, frame = 0;
    const reset = (card) => {
      if (!card) return;
      const f = card.querySelector(".poster__frame");
      card.classList.remove("is-tilting");
      f.style.setProperty("--rx", "0deg"); f.style.setProperty("--ry", "0deg");
    };
    document.addEventListener("pointermove", (e) => {
      if (e.pointerType && e.pointerType !== "mouse") return;
      const card = e.target.closest && e.target.closest("[data-poster]");
      let hit = null;
      if (card) {   // geometri frame, bukan elemen target, supaya tetap akurat saat kartu sedang miring
        const fr = card.querySelector(".poster__frame").getBoundingClientRect();
        if (e.clientX >= fr.left - 6 && e.clientX <= fr.right + 6 && e.clientY >= fr.top - 6 && e.clientY <= fr.bottom + 6) hit = card;
      }
      if (active && active !== hit) { reset(active); active = null; }
      if (!hit) return;
      active = hit;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const f = hit.querySelector(".poster__frame");
        const r = f.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        hit.classList.add("is-tilting");
        f.style.setProperty("--ry", ((px - 0.5) * 16).toFixed(2) + "deg");
        f.style.setProperty("--rx", ((0.5 - py) * 16).toFixed(2) + "deg");
        f.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
        f.style.setProperty("--my", (py * 100).toFixed(1) + "%");
      });
    }, { passive: true });
    document.addEventListener("pointerleave", () => { reset(active); active = null; });
  }

  /* ---------------------------------------------------------------- toast -- */
  NP.toast = function (message, type) {
    const host = document.getElementById("toasts");
    if (!host || !message) return;
    type = ICONS[type] && type !== "close" ? type : "info";
    const life = type === "error" ? 6500 : 4500;

    const el = document.createElement("div");
    el.className = "toast toast--" + type;
    el.setAttribute("role", type === "error" ? "alert" : "status");
    el.style.setProperty("--life", life + "ms");
    el.innerHTML = ICONS[type] + "<p></p><button type=\"button\" aria-label=\"Tutup notifikasi\">" + ICONS.close + "</button><span class=\"toast__bar\"></span>";
    el.querySelector("p").textContent = message;
    host.appendChild(el);

    let timer;
    const dismiss = () => {
      clearTimeout(timer);
      el.classList.add("is-leaving");
      setTimeout(() => el.remove(), 380);
    };
    const start = () => { timer = setTimeout(dismiss, life); };
    el.querySelector("button").addEventListener("click", dismiss);
    el.addEventListener("mouseenter", () => clearTimeout(timer));
    el.addEventListener("mouseleave", () => { el.querySelector(".toast__bar").style.animation = "none"; void el.offsetWidth; el.querySelector(".toast__bar").style.animation = ""; start(); });
    start();
    while (host.children.length > 4) host.firstElementChild.remove();
  };

  document.querySelectorAll("#flash-list li").forEach((li, i) => {
    setTimeout(() => NP.toast(li.textContent.trim(), li.dataset.type), 250 + i * 220);
  });

  /* ------------------------------------------------------ dialog konfirmasi -- */
  const dialog = document.getElementById("confirm-dialog");
  if (dialog && typeof dialog.showModal === "function") {
    const title = dialog.querySelector("[data-confirm-title]");
    const text = dialog.querySelector("[data-confirm-text]");
    const ok = dialog.querySelector("[data-confirm-ok]");
    let pending = null;

    document.addEventListener("submit", (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement) || !form.hasAttribute("data-confirm") || form.dataset.confirmed === "1") return;
      event.preventDefault();
      pending = form;
      title.textContent = form.dataset.confirmTitle || "Yakin ingin melanjutkan?";
      text.textContent = form.dataset.confirm;
      ok.textContent = form.dataset.confirmOk || "Ya, hapus";
      dialog.showModal();
      ok.focus();
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog || event.target.closest("[data-confirm-cancel]")) dialog.close();
    });
    ok.addEventListener("click", () => {
      if (!pending) return;
      const form = pending;
      form.dataset.confirmed = "1";
      dialog.close();
      if (typeof form.requestSubmit === "function") form.requestSubmit(); else form.submit();
    });
    dialog.addEventListener("close", () => { pending = null; });
  }

  /* ----------------------------------------------------- menu pengguna ----- */
  document.querySelectorAll("[data-menu]").forEach((root) => {
    const button = root.querySelector("[data-menu-button]");
    const menu = root.querySelector("[data-menu-panel]");
    const set = (open) => { menu.dataset.open = open ? "true" : "false"; button.setAttribute("aria-expanded", open ? "true" : "false"); };
    button.addEventListener("click", (e) => { e.stopPropagation(); set(menu.dataset.open !== "true"); });
    document.addEventListener("click", (e) => { if (!root.contains(e.target)) set(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
  });

  /* --------------------------------------------- drawer (nav publik & admin) -- */
  [["drawer", "[data-drawer-open]", "[data-drawer-close]"], ["sidebar", "[data-sidebar-open]", "[data-sidebar-close]"]].forEach(([name, openSel, closeSel]) => {
    const set = (open) => {
      if (open) document.body.dataset[name] = "open"; else delete document.body.dataset[name];
      document.querySelectorAll(openSel).forEach((b) => b.setAttribute("aria-expanded", open ? "true" : "false"));
    };
    document.querySelectorAll(openSel).forEach((b) => b.addEventListener("click", () => set(true)));
    document.querySelectorAll(closeSel).forEach((b) => b.addEventListener("click", () => set(false)));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
    window.matchMedia("(min-width: 1024px)").addEventListener("change", () => set(false));
  });

  /* ------------------------------------------- reveal bertahap saat scroll -- */
  NP.reveal = function (root) {
    const scope = root || document;
    const items = scope.querySelectorAll("[data-reveal]:not(.is-in)");
    if (!items.length) return;
    if (!("IntersectionObserver" in window)) { items.forEach((el) => el.classList.add("is-in")); return; }

    // Anak dari kontainer [data-stagger] mendapat jeda berurutan (maksimal 8 langkah).
    // Jeda berurutan dari kiri ke kanan: indeks dihitung per baris grid (jumlah kolom aktual).
    scope.querySelectorAll("[data-stagger]").forEach((group) => {
      const cols = Math.max(1, getComputedStyle(group).gridTemplateColumns.split(" ").filter(Boolean).length);
      group.querySelectorAll(":scope > [data-reveal]").forEach((el, i) => el.style.setProperty("--i", i % cols));
    });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach((el) => io.observe(el));
  };
  NP.reveal();

  /* Bagian tanpa data-reveal pada .bars dipakai grafik admin */
  document.querySelectorAll(".bars").forEach((el) => {
    if (reduceMotion || !("IntersectionObserver" in window)) { el.classList.add("is-in"); return; }
    const io = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { el.classList.add("is-in"); io.disconnect(); } }), { threshold: 0.2 });
    io.observe(el);
  });
})();
