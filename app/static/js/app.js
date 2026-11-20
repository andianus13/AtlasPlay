/* AtlasPlay (publik): spotlight hero, pencarian real-time, simpan game, filter katalog. */
(function () {
  "use strict";
  const NP = window.NP || {};
  const reduceMotion = NP.reduceMotion;
  const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* ============================================================ SHOWCASE == */
  /* Slider hero: satu slide terlihat, ganti otomatis tiap 5 detik. Klik titik/panah langsung pindah dan mengulang timer. */
  const showcase = document.querySelector("[data-showcase]");
  if (showcase) {
    const slides = Array.from(showcase.querySelectorAll("[data-slide]"));
        const DURATION = 5000;
    let index = 0;
    let timer = null;

    showcase.style.setProperty("--dur", DURATION + "ms");

    const show = (next) => {
      index = (next + slides.length) % slides.length;
      slides.forEach((s, i) => {
        const on = i === index;
        s.classList.toggle("is-active", on);
        s.setAttribute("aria-hidden", on ? "false" : "true");
        s.inert = !on;
        // Inline juga diatur supaya hanya satu slide terlihat walau stylesheet lama masih di cache.
        s.style.opacity = on ? "1" : "0";
        s.style.visibility = on ? "visible" : "hidden";
        s.style.pointerEvents = on ? "auto" : "none";
        s.style.zIndex = on ? "1" : "0";
      });
      NP.backdrop.setBase(slides[index].dataset.banner);   // latar blur mengikuti slide aktif
      // Glow latar mengikuti warna dominan banner yang sedang aktif.
      const current = index;
      NP.dominant(slides[current].dataset.banner).then((c) => {
        NP.baseGlow = c;
        if (current === index && !NP.hoverGlow) NP.setGlow(c);
      });
      restart();
    };
    const restart = () => {
      clearTimeout(timer);
      if (slides.length < 2) { showcase.dataset.playing = "false"; return; }
      showcase.dataset.playing = "true";
      timer = setTimeout(() => show(index + 1), DURATION);
    };

    // Tab disembunyikan: timer dihentikan agar tidak melompat-lompat; saat kembali, hitungan mulai ulang.
    document.addEventListener("visibilitychange", () => { if (document.hidden) clearTimeout(timer); else restart(); });
    show(0);
  }

  /* Banner halaman detail bergeser pelan saat scroll (parallax ringan, vanilla) */
  const parallax = document.querySelector("[data-parallax] img");
  if (parallax && !reduceMotion) {
    const wrap = parallax.parentElement;
    parallax.style.transform = "scale(1.1)";
    parallax.style.willChange = "transform";
    let ticking = false;
    const update = () => {
      ticking = false;
      const r = wrap.getBoundingClientRect();
      const progress = Math.max(-1, Math.min(1, (r.top + r.height / 2 - innerHeight / 2) / innerHeight));
      parallax.style.transform = "translate3d(0," + (progress * -26).toFixed(1) + "px,0) scale(1.1)";
    };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  /* ===================== HALAMAN DETAIL: glow ambient dari warna poster ===== */
  const ambientSrc = document.querySelector("[data-ambient-src]");
  if (ambientSrc) {
    NP.backdrop.setBase(ambientSrc.dataset.ambientSrc || ambientSrc.dataset.ambientAlt);
    NP.dominant(ambientSrc.dataset.ambientSrc).then((c) => {
      NP.dominant(ambientSrc.dataset.ambientAlt).then((c2) => {
        NP.baseGlow = c;
        NP.setGlow(c);
        document.documentElement.style.setProperty("--glow-2", c2 || c);
      });
    });
  }

  /* ===== DETAIL: switch spesifikasi (Bandingkan / Minimum / Rekomendasi) ===== */
  document.querySelectorAll("[data-spec-switch]").forEach((sw) => {
    const target = document.querySelector(sw.dataset.specSwitch);
    if (!target) return;
    sw.querySelectorAll("[data-view]").forEach((btn) => btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      target.dataset.view = view;
      sw.querySelectorAll("[data-view]").forEach((b) => b.setAttribute("aria-selected", b === btn ? "true" : "false"));
    }));
  });

  /* ===================================================== PENCARIAN CEPAT == */
  const searchRoot = document.querySelector("[data-suggest-root]");
  if (searchRoot) {
    const input = searchRoot.querySelector("input");
    const list = searchRoot.querySelector("[data-suggest-list]");
    let items = [];
    let active = -1;
    let controller = null;

    const setOpen = (open) => { list.dataset.open = open ? "true" : "false"; input.setAttribute("aria-expanded", open ? "true" : "false"); };
    const highlight = (i) => {
      active = i;
      items.forEach((el, n) => el.setAttribute("aria-selected", n === i ? "true" : "false"));
      if (i >= 0) input.setAttribute("aria-activedescendant", items[i].id); else input.removeAttribute("aria-activedescendant");
    };
    const render = (results, q) => {
      if (!results.length) {
        list.innerHTML = '<li class="suggest__empty" role="presentation">Tidak ada game bernama “' + esc(q) + '”. <a class="text-link" href="/request-game">Ajukan game ini</a></li>';
        items = []; setOpen(true); return;
      }
      list.innerHTML = results.map((g, i) =>
        '<li role="presentation"><a role="option" id="sg-' + i + '" href="' + esc(g.url) + '" aria-selected="false">' +
        '<img class="aspect-[3/4] object-cover object-center" src="' + esc(g.cover) + '" alt="" width="36">' +
        '<span><span class="suggest__title">' + esc(g.title) + '</span><br><span class="suggest__sub">' + esc(g.developer || "Developer belum diisi") + " · " + esc(g.platforms.join(", ")) + "</span></span>" +
        (g.rating ? '<span class="suggest__rating">★ ' + g.rating.toFixed(1) + "</span>" : "") + "</a></li>").join("");
      items = Array.from(list.querySelectorAll("a[role=option]"));
      highlight(-1); setOpen(true);
    };
    const search = debounce(async () => {
      const q = input.value.trim();
      if (q.length < 2) { setOpen(false); return; }
      if (controller) controller.abort();
      controller = new AbortController();
      try {
        const res = await fetch("/api/search?q=" + encodeURIComponent(q), { signal: controller.signal, headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error("bad status");
        render((await res.json()).results, q);
      } catch (err) { if (err.name !== "AbortError") setOpen(false); }
    }, 180);

    input.addEventListener("input", search);
    input.addEventListener("focus", () => { if (input.value.trim().length >= 2 && list.children.length) setOpen(true); });
    input.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown" && items.length) { e.preventDefault(); highlight((active + 1) % items.length); }
      else if (e.key === "ArrowUp" && items.length) { e.preventDefault(); highlight((active - 1 + items.length) % items.length); }
      else if (e.key === "Enter" && active >= 0) { e.preventDefault(); items[active].click(); }
      else if (e.key === "Escape") { setOpen(false); }
    });
    document.addEventListener("click", (e) => { if (!searchRoot.contains(e.target)) setOpen(false); });
  }

  /* ========================================================= SIMPAN GAME == */
  const syncSaved = (slug, saved, count) => {
    document.querySelectorAll('[data-save-slug="' + slug + '"]').forEach((btn) => {
      btn.setAttribute("aria-pressed", saved ? "true" : "false");
      btn.setAttribute("aria-label", (saved ? "Hapus dari koleksi: " : "Simpan ke koleksi: ") + (btn.dataset.title || ""));
      const label = btn.querySelector("[data-save-label]");
      if (label) label.textContent = saved ? "Tersimpan di Koleksi" : "Simpan ke Koleksi";
      btn.classList.remove("pop"); void btn.offsetWidth; if (saved) btn.classList.add("pop");
    });
    document.querySelectorAll("[data-saved-count]").forEach((el) => { el.textContent = count; });
  };

  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.hasAttribute("data-save-form")) return;
    event.preventDefault();
    const btn = form.querySelector("[data-save-slug]");
    if (btn.disabled) return;
    btn.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: "POST", headers: { Accept: "application/json", "X-CSRF-Token": NP.csrf() }, body: new FormData(form), credentials: "same-origin",
      });
      if (res.status === 401) { const body = await res.json().catch(() => ({})); window.location.href = body.login || "/login"; return; }
      if (!res.ok) throw new Error("status " + res.status);
      const data = await res.json();
      syncSaved(btn.dataset.saveSlug, data.saved, data.count);
      NP.toast(data.message, data.saved ? "success" : "info");

      const card = form.closest("[data-remove-on-unsave]");
      if (card && !data.saved) {
        card.style.transition = "opacity .4s ease, transform .5s cubic-bezier(.22,1,.36,1)";
        card.style.opacity = "0"; card.style.transform = "scale(.92) translateY(10px)";
        setTimeout(() => {
          const grid = card.parentElement; card.remove();
          if (grid && !grid.children.length) window.location.reload();
        }, 450);
      }
    } catch (err) {
      NP.toast("Gagal menyimpan. Periksa koneksi lalu coba lagi.", "error");
    } finally { btn.disabled = false; }
  });

  /* =================================================== KATALOG DINAMIS ===== */
  const catalog = document.querySelector("[data-catalog]");
  if (catalog) {
    const form = catalog.querySelector("[data-catalog-form]");
    const results = catalog.querySelector("[data-results]");
    const qInput = form.querySelector('input[name="q"]');
    const sortSelect = form.querySelector('select[name="sort"]');
    const platformInput = form.querySelector('input[name="platform"]');
    const developerInput = form.querySelector('input[name="developer"]');
    const pills = catalog.querySelectorAll("[data-platform-pill]");
    let controller = null;

    const paramsFromForm = () => {
      const p = new URLSearchParams();
      if (qInput.value.trim()) p.set("q", qInput.value.trim());
      if (platformInput.value) p.set("platform", platformInput.value);
      if (developerInput && developerInput.value) p.set("developer", developerInput.value);
      if (sortSelect.value && sortSelect.value !== "terbaru") p.set("sort", sortSelect.value);
      return p;
    };

    const load = async (params, push) => {
      if (controller) controller.abort();
      controller = new AbortController();
      results.dataset.loading = "true";
      const query = params.toString();
      try {
        const res = await fetch("/games" + (query ? "?" + query : ""), { headers: { "X-Partial": "1" }, signal: controller.signal, credentials: "same-origin" });
        if (!res.ok) throw new Error("status " + res.status);
        results.innerHTML = await res.text();
        const url = "/games" + (query ? "?" + query : "");
        if (push) history.replaceState(null, "", url);
        if (NP.reveal) NP.reveal(results);
        const live = catalog.querySelector("[data-live]");
        const count = results.querySelector("[data-count]");
        if (live && count) live.textContent = count.textContent.trim();
      } catch (err) {
        if (err.name !== "AbortError") NP.toast("Gagal memuat daftar game. Coba lagi.", "error");
      } finally { delete results.dataset.loading; }
    };

    const run = () => load(paramsFromForm(), true);
    const runDebounced = debounce(run, 240);

    form.addEventListener("submit", (e) => { e.preventDefault(); run(); });
    qInput.addEventListener("input", runDebounced);
    sortSelect.addEventListener("change", run);

    pills.forEach((pill) => pill.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      platformInput.value = pill.dataset.platformPill;
      pills.forEach((p) => { const on = p === pill; p.classList.toggle("is-active", on); p.setAttribute("aria-pressed", on ? "true" : "false"); });
      run();
    }));

    // Pagination di dalam hasil: ambil sebagai partial agar tidak reload penuh
    results.addEventListener("click", (e) => {
      const link = e.target.closest("a[data-page-link]");
      if (!link || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault();
      load(new URL(link.href).searchParams, true).then(() => window.scrollTo({ top: catalog.offsetTop - 90, behavior: NP.reduceMotion ? "auto" : "smooth" }));
    });
  }

  /* ============================================== FORM ULASAN: PENGHITUNG == */
  document.querySelectorAll("[data-counter]").forEach((area) => {
    const out = document.querySelector(area.dataset.counter);
    if (!out) return;
    const update = () => { out.textContent = area.value.length + " / " + (area.maxLength > 0 ? area.maxLength : 2000); };
    area.addEventListener("input", update); update();
  });
})();
