/* AtlasPlay admin: pratinjau gambar langsung, tooltip grafik, submit otomatis filter, cetak. */
(function () {
  "use strict";

  const SIZES = { cover: { w: 600, h: 800, label: "600 x 800 px (3:4)" }, banner: { w: 1400, h: 550, label: "1400 x 550 px (21:9)" } };
  const MIN = { cover: [300, 400], banner: [700, 275] };
  const PLACEHOLDER = { cover: "/static/img/placeholder-cover.svg", banner: "/static/img/placeholder-banner.svg" };

  /* ---------------------------------------- pratinjau gambar sebelum simpan -- */
  document.querySelectorAll("[data-image-field]").forEach((root) => {
    const kind = root.dataset.imageField; // "cover" | "banner"
    const file = root.querySelector('input[type="file"]');
    const url = root.querySelector('input[data-url]');
    const frame = root.querySelector(".preview-frame");
    const img = frame.querySelector("img");
    const meta = root.querySelector(".preview-meta");
    const clear = root.querySelector('input[name^="clear_"]');
    const original = img.getAttribute("src");
    let objectUrl = null;

    const setMeta = (text, warn) => { meta.textContent = text; meta.classList.toggle("warn", !!warn); };
    const reset = () => {
      if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
      img.src = original || PLACEHOLDER[kind];
      frame.dataset.state = original && original.indexOf("placeholder") === -1 ? "filled" : "empty";
      setMeta(original && original.indexOf("placeholder") === -1 ? "Gambar saat ini" : "Belum ada gambar", false);
    };

    const preview = (src, naturalW, naturalH, origin) => {
      img.src = src;
      frame.dataset.state = "filled";
      const tooSmall = naturalW < MIN[kind][0] || naturalH < MIN[kind][1];
      const target = SIZES[kind].w / SIZES[kind].h;
      const ratio = naturalW / naturalH;
      const cropped = Math.abs(ratio - target) > 0.02;
      let text = origin + ": " + naturalW + " x " + naturalH + " px";
      if (cropped) text += ". Akan dipotong dari tengah ke " + SIZES[kind].label;
      else text += ". Sudah sesuai rasio";
      if (tooSmall) text = "Terlalu kecil (" + naturalW + " x " + naturalH + " px). Minimal " + MIN[kind][0] + " x " + MIN[kind][1] + " px.";
      setMeta(text, tooSmall || cropped);
    };

    file.addEventListener("change", () => {
      const f = file.files && file.files[0];
      if (!f) { reset(); return; }
      if (!/^image\//.test(f.type)) { setMeta("File bukan gambar.", true); file.value = ""; return; }
      if (f.size > 5 * 1024 * 1024) { setMeta("Ukuran file " + (f.size / 1048576).toFixed(1) + " MB, maksimal 5 MB.", true); file.value = ""; return; }
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(f);
      const probe = new Image();
      probe.onload = () => preview(objectUrl, probe.naturalWidth, probe.naturalHeight, "File baru");
      probe.onerror = () => { setMeta("Gambar tidak bisa dibaca.", true); file.value = ""; };
      probe.src = objectUrl;
      if (url) url.value = "";
      if (clear) clear.checked = false;
    });

    if (url) {
      const onUrl = () => {
        const value = url.value.trim();
        if (!value) { if (!(file.files && file.files[0])) reset(); return; }
        if (!/^https?:\/\//i.test(value)) { setMeta("URL harus diawali http:// atau https://", true); return; }
        const probe = new Image();
        probe.onload = () => preview(value, probe.naturalWidth, probe.naturalHeight, "Dari URL");
        probe.onerror = () => setMeta("URL gambar tidak bisa dimuat.", true);
        probe.src = value;
        file.value = "";
      };
      let t; url.addEventListener("input", () => { clearTimeout(t); t = setTimeout(onUrl, 350); });
      if (url.value.trim()) setMeta("Gambar dari URL", false);
    }

    if (clear) clear.addEventListener("change", () => {
      if (clear.checked) { file.value = ""; if (url) url.value = ""; img.src = PLACEHOLDER[kind]; frame.dataset.state = "empty"; setMeta("Gambar akan dihapus saat disimpan", true); }
      else reset();
    });
    setMeta(frame.dataset.state === "filled" ? "Gambar saat ini" : "Belum ada gambar", false);
  });

  /* ------------------------------------------------------ warna platform ----- */
  document.querySelectorAll("[data-color-sync]").forEach((wrap) => {
    const picker = wrap.querySelector('input[type="color"]');
    const text = wrap.querySelector('input[type="text"]');
    const sample = document.querySelector("[data-color-sample]");
    const paint = (v) => { if (sample) sample.style.setProperty("--c", v); };
    picker.addEventListener("input", () => { text.value = picker.value.toUpperCase(); paint(text.value); });
    text.addEventListener("input", () => { if (/^#[0-9a-fA-F]{6}$/.test(text.value)) { picker.value = text.value; paint(text.value); } });
    paint(text.value);
  });
  const sampleText = document.querySelector("[data-color-sample-text]");
  if (sampleText) {
    const nameInput = document.getElementById("f-name");
    const shortInput = document.getElementById("f-short_name");
    const update = () => {
      const short = shortInput && shortInput.value.trim();
      sampleText.textContent = short || (nameInput && nameInput.value.trim().slice(0, 12)) || "PC";
    };
    [nameInput, shortInput].forEach((el) => el && el.addEventListener("input", update));
    update();
  }

  /* ------------------------------------------------- tooltip grafik batang ---- */
  const tip = document.getElementById("chart-tip");
  if (tip) {
    const show = (row, x, y) => {
      tip.innerHTML = "<b>" + row.dataset.value + "</b> game di " + row.dataset.label;
      tip.classList.add("is-on");
      const w = tip.offsetWidth;
      tip.style.left = Math.min(window.innerWidth - w - 12, x + 14) + "px";
      tip.style.top = y + 16 + "px";
    };
    document.querySelectorAll("[data-bar]").forEach((row) => {
      row.addEventListener("pointermove", (e) => show(row, e.clientX, e.clientY));
      row.addEventListener("pointerleave", () => tip.classList.remove("is-on"));
      row.addEventListener("focus", () => { const r = row.getBoundingClientRect(); show(row, r.left + 40, r.top); });
      row.addEventListener("blur", () => tip.classList.remove("is-on"));
    });
  }

  /* ------------------------------------------------ filter otomatis submit ---- */
  document.querySelectorAll("[data-autosubmit]").forEach((form) => {
    form.querySelectorAll("select").forEach((s) => s.addEventListener("change", () => form.requestSubmit()));
  });
  let typing;
  document.querySelectorAll("[data-search-submit]").forEach((input) => {
    input.addEventListener("input", () => { clearTimeout(typing); typing = setTimeout(() => input.form.requestSubmit(), 420); });
  });

  document.querySelectorAll("[data-print]").forEach((b) => b.addEventListener("click", () => window.print()));
})();
