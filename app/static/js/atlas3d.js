/* AtlasPlay: gamepad 3D orisinal (wireless pro controller berbodi obsidian, aksen emerald dan cyan).
   Three.js dimuat dari CDN; bila gagal, memakai salinan lokal di /static/vendor. Bila WebGL tidak ada,
   kanvas disembunyikan dan halaman tetap berfungsi normal. */
const CDN = "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js";
const LOCAL = "/static/vendor/three.module.min.js";

async function loadThree() {
  try { return await import(CDN); } catch (e) { return await import(LOCAL); }
}

const EMERALD = 0x10b981, CYAN = 0x38bdf8, INK = 0x0b1117;
const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 4);   // easeOutQuart

async function start(canvas) {
  const mode = canvas.dataset.atlas3d || "bg";
  const reduce = false;   // animasi 3D sengaja tidak dimatikan oleh prefers-reduced-motion (permintaan produk)
  let THREE;
  try { THREE = await loadThree(); } catch (e) { canvas.style.display = "none"; return; }

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "low-power" });
  } catch (e) { canvas.style.display = "none"; return; }
  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, mode === "bg" ? 1 : 1.75));

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 1.4, 11);

  /* ---- cahaya: rim emerald dan cyan di atas latar gelap ---- */
  scene.add(new THREE.AmbientLight(0x8aa0ba, 0.9));
  const lEm = new THREE.PointLight(EMERALD, 70, 0, 2); lEm.position.set(5, 3.5, 4); scene.add(lEm);
  const lCy = new THREE.PointLight(CYAN, 60, 0, 2); lCy.position.set(-5, -2.5, 4.5); scene.add(lCy);
  const lFill = new THREE.PointLight(0xcfe0f5, 140, 0, 2); lFill.position.set(0, 5, 9); scene.add(lFill);
  const lBack = new THREE.PointLight(0x9be9ff, 120, 0, 2); lBack.position.set(0, 4, -5); scene.add(lBack);

  const root = new THREE.Group(); scene.add(root);
  const parts = [];       // bagian yang "dirakit"
    let seed = 7;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };

  const add = (obj, delay, spread = 1) => {
    const dir = new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize();
    // arah pecah radial dari pusat controller (dengan sedikit acak), jarak dan putaran unik per kepingan
    const ctr = new THREE.Box3().setFromObject(obj).getCenter(new THREE.Vector3());
    const rad = ctr.length() > 0.35 ? ctr.clone().normalize().multiplyScalar(0.85).add(dir.clone().multiplyScalar(0.45)).normalize() : dir.clone();
    rad.z += 0.35 + rnd() * 0.3; rad.normalize();
    parts.push({
      obj, delay, dir, spread, rad, blast: 2.6 + rnd() * 3.2, spinAxis: dir.clone(), spinAng: 4 + rnd() * 8,
      pos: obj.position.clone(), scale: obj.scale.clone(), quat: obj.quaternion.clone(),
      offQuat: new THREE.Quaternion().setFromEuler(new THREE.Euler(rnd() * 3, rnd() * 3, rnd() * 3)),
    });
    root.add(obj);
    return obj;
  };

  const glass = new THREE.MeshPhysicalMaterial({
    color: INK, metalness: 0.75, roughness: 0.22, clearcoat: 1, clearcoatRoughness: 0.15, flatShading: true,
    emissive: 0x0a5a44, emissiveIntensity: 1.1,
  });
  const edgeMat = (c, o = 0.9) => new THREE.LineBasicMaterial({ color: c, transparent: true, opacity: o });
  const metal = (c, e = 0.35) => new THREE.MeshStandardMaterial({ color: c, metalness: 0.85, roughness: 0.25, emissive: c, emissiveIntensity: e });

  /* ================= GAMEPAD ORISINAL ================= */
  const SLATE = 0x1e293b, OBSIDIAN = 0x0f172a;
  const satin = (c, r = 0.42, m = 0.55) => new THREE.MeshPhysicalMaterial({ color: c, metalness: m, roughness: r, clearcoat: 0.35, clearcoatRoughness: 0.4 });
  const glows = [];   // material cincin/garis bercahaya, didenyutkan saat klik
  const glow = (c, i = 1.6) => { const m = new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: i, metalness: 0.2, roughness: 0.35 }); glows.push([m, i]); return m; };
  const trigMat = new THREE.MeshStandardMaterial({ color: 0x1b3447, metalness: 0.8, roughness: 0.28, emissive: CYAN, emissiveIntensity: 0.28 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x0b1220, metalness: 0.4, roughness: 0.6 });
  const bevel = (d, b = 0.05) => ({ depth: d, bevelEnabled: true, bevelThickness: b, bevelSize: b, bevelSegments: 4, curveSegments: 24 });

  // siluet bodi: kurva halus (Catmull-Rom) dengan bagian tengah ramping dan grip yang melebar
  const half = [[0, 1.05], [0.9, 1.2], [1.8, 1.27], [2.4, 1.1], [2.75, 0.6], [3.05, -0.2], [3.38, -1.0], [3.45, -1.6],
                [3.1, -1.98], [2.55, -1.98], [2.1, -1.5], [1.6, -0.95], [1.0, -0.72], [0, -0.66]];
  const outline = half.concat(half.slice(1, -1).reverse().map(([x, y]) => [-x, y]));
  const curve = new THREE.CatmullRomCurve3(outline.map(([x, y]) => new THREE.Vector3(x, y, 0)), true, "centripetal");
  const pts2 = curve.getPoints(260).map((p) => new THREE.Vector2(p.x, p.y));
  const bodyShape = new THREE.Shape(pts2);

  // cangkang dibagi tiga kepingan (grip kiri, tengah, grip kanan) supaya bisa pecah dan menyatu dengan presisi
  const clipX = (poly, xc, keepGreater) => {
    const out = [], n = poly.length;
    const inside = (v) => (keepGreater ? v.x >= xc : v.x <= xc);
    const cut = (p, c) => new THREE.Vector2(xc, p.y + ((xc - p.x) / (c.x - p.x)) * (c.y - p.y));
    for (let i = 0; i < n; i++) {
      const c = poly[i], p = poly[(i + n - 1) % n];
      if (inside(c)) { if (!inside(p)) out.push(cut(p, c)); out.push(c); } else if (inside(p)) out.push(cut(p, c));
    }
    return out;
  };
  const centered = (mesh) => {   // pusatkan geometri agar kepingan berputar pada porosnya sendiri
    mesh.geometry.computeBoundingBox();
    const c = mesh.geometry.boundingBox.getCenter(new THREE.Vector3());
    mesh.geometry.translate(-c.x, -c.y, 0); mesh.position.add(new THREE.Vector3(c.x, c.y, 0)); return mesh;
  };
  const XC = 1.25;
  const panels = [clipX(pts2, -XC, false), clipX(clipX(pts2, -XC, true), XC, false), clipX(pts2, XC, true)];
  panels.forEach((poly, i) => {
    const g = new THREE.ExtrudeGeometry(new THREE.Shape(poly), { ...bevel(0.34, 0.12), bevelOffset: -0.12 });
    g.translate(0, 0, -0.17); g.computeVertexNormals();
    add(centered(new THREE.Mesh(g, satin(SLATE))), 0.0 + i * 0.05, 1.0);
  });

  const plateGeo = new THREE.ExtrudeGeometry(bodyShape, bevel(0.03, 0.03));
  plateGeo.scale(0.93, 0.9, 1); plateGeo.translate(0, 0.02, 0);
  const plate = new THREE.Mesh(plateGeo, satin(OBSIDIAN, 0.5, 0.35)); plate.position.z = 0.3;
  add(centered(plate), 0.1, 1.1);
  const ZT = 0.37;   // tinggi permukaan atas pelat

  // jalur cahaya tipis di tepi atas pelat
  const strip = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.035, 0.03), glow(EMERALD, 1.8));
  strip.position.set(0, 0.98, ZT + 0.02); add(strip, 0.5, 1.2);

  // analog stick: cincin emerald + tutup cekung
  const capProfile = [[0, 0], [0.27, 0], [0.29, 0.05], [0.28, 0.13], [0.25, 0.17], [0.18, 0.155], [0.09, 0.125], [0, 0.115]].map(([r, h]) => new THREE.Vector2(r, h));
  const makeStick = (x, y, delay) => {
    const g = new THREE.Group();
    const well = new THREE.Mesh(new THREE.TorusGeometry(0.4, 0.03, 12, 64), glow(EMERALD, 1.5)); g.add(well);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.37, 0.37, 0.05, 48), darkMat); rim.rotation.x = Math.PI / 2; rim.position.z = -0.01; g.add(rim);
    const cap = new THREE.Mesh(new THREE.LatheGeometry(capProfile, 40), satin(0x131c2e, 0.55, 0.5)); cap.rotation.x = Math.PI / 2; cap.position.z = 0.02; g.add(cap);
    g.position.set(x, y, ZT + 0.03); add(g, delay, 1.3); return g;
  };
  makeStick(-1.55, 0.3, 0.2); makeStick(0.85, -0.45, 0.3);

  // D-pad presisi
  const a = 0.115, L = 0.33;
  const cross = new THREE.Shape([[-a, L], [a, L], [a, a], [L, a], [L, -a], [a, -a], [a, -L], [-a, -L], [-a, -a], [-L, -a], [-L, a], [-a, a]].map(([x, y]) => new THREE.Vector2(x, y)));
  const dpad = new THREE.Group();
  dpad.add(new THREE.Mesh(new THREE.ExtrudeGeometry(cross, bevel(0.06, 0.03)), satin(0x131c2e, 0.5, 0.5)));
  const dring = new THREE.Mesh(new THREE.TorusGeometry(0.46, 0.016, 8, 64), glow(EMERALD, 1.3)); dring.position.z = -0.03; dpad.add(dring);
  dpad.position.set(-0.85, -0.45, ZT + 0.02); add(dpad, 0.35, 1.3);

  // empat tombol aksi
  [[0, 0.36], [0.36, 0], [0, -0.36], [-0.36, 0]].forEach(([dx, dy], i) => {
    const g = new THREE.Group();
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.18, 0.09, 40), satin(0x131c2e, 0.4, 0.55)); cap.rotation.x = Math.PI / 2; g.add(cap);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.175, 0.014, 8, 40), glow(i === 1 ? CYAN : EMERALD, 1.5)); ring.position.z = 0.045; g.add(ring);
    g.position.set(1.55 + dx, 0.3 + dy, ZT + 0.04); add(g, 0.4 + i * 0.07, 1.4);
  });

  // tombol tengah: dua pil kecil + tombol home bercahaya
  [-0.3, 0.3].forEach((x, i) => {
    const m = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.05, 24), satin(0x131c2e, 0.5, 0.5));
    m.rotation.x = Math.PI / 2; m.position.set(x, 0.52, ZT + 0.03); add(m, 0.6 + i * 0.05, 1.2);
  });
  const home = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.025, 10, 40), glow(EMERALD, 2));
  home.position.set(0, 0.08, ZT + 0.03); add(home, 0.65, 1.2);

  // bumper L1/R1 dan trigger L2/R2
  const slab = (w, h) => { const r = Math.min(h / 2, 0.14), sh = new THREE.Shape();
    sh.moveTo(-w / 2 + r, -h / 2); sh.lineTo(w / 2 - r, -h / 2); sh.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r);
    sh.lineTo(w / 2, h / 2 - r); sh.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2); sh.lineTo(-w / 2 + r, h / 2);
    sh.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r); sh.lineTo(-w / 2, -h / 2 + r); sh.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2); return sh; };
  [-1, 1].forEach((sd, i) => {
    const bump = new THREE.Mesh(new THREE.ExtrudeGeometry(slab(1.3, 0.3), bevel(0.14, 0.05)), trigMat);
    bump.position.set(sd * 1.85, 1.3, 0.0); bump.rotation.set(-0.15, 0, -sd * 0.16); add(bump, 0.75 + i * 0.05, 1.5);
    const trig = new THREE.Mesh(new THREE.ExtrudeGeometry(slab(1.0, 0.7), bevel(0.22, 0.09)), trigMat);
    trig.position.set(sd * 1.95, 1.05, -0.5); trig.rotation.set(-0.5, 0, -sd * 0.12); add(trig, 0.85 + i * 0.05, 1.7);
  });

  /* ---- khusus Welcome: inti chip bercahaya, serpihan, dan partikel cahaya untuk animasi shatter ---- */
  const debris = [], sparkSets = [];
  let chipMat = null, lFlash = null, shock = null;
  if (mode === "hero") {
    chipMat = new THREE.MeshStandardMaterial({ color: EMERALD, emissive: EMERALD, emissiveIntensity: 1.6, metalness: 0.3, roughness: 0.3, flatShading: true });
    const chip = new THREE.Mesh(new THREE.OctahedronGeometry(0.34, 0), chipMat); chip.position.set(0, 0.1, 0.0);
    const chipWire = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.OctahedronGeometry(0.5, 0)), new THREE.LineBasicMaterial({ color: CYAN, transparent: true, opacity: 0.9 }));
    chip.add(chipWire); add(chip, 0.3, 0.6);
    const shardMats = [satin(SLATE, 0.4, 0.6), satin(OBSIDIAN, 0.45, 0.5), glow(EMERALD, 1.2), glow(CYAN, 1.0)];
    for (let i = 0; i < 46; i++) {
      const geo = i % 3 ? new THREE.TetrahedronGeometry(0.1 + rnd() * 0.18, 0) : new THREE.OctahedronGeometry(0.08 + rnd() * 0.12, 0);
      const m = new THREE.Mesh(geo, shardMats[i % shardMats.length]);
      const p0 = new THREE.Vector3((rnd() - 0.5) * 4.5, (rnd() - 0.5) * 1.8, (rnd() - 0.5) * 0.3);
      const rad = p0.clone().normalize().add(new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() * 0.8)).normalize();
      m.scale.setScalar(0); m.position.copy(p0); root.add(m);
      debris.push({ m, p0, rad, blast: 2.2 + rnd() * 4.5, axis: new THREE.Vector3(rnd() - 0.5, rnd() - 0.5, rnd() - 0.5).normalize(), ang: 3 + rnd() * 9, s: 0.7 + rnd() * 0.9 });
    }
    [[EMERALD, 90], [CYAN, 70]].forEach(([c, n]) => {
      const arr = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { const r = 1.5 + rnd() * 4.5, a1 = rnd() * 6.283, b1 = Math.acos(2 * rnd() - 1); arr.set([r * Math.sin(b1) * Math.cos(a1) * 1.3, r * Math.cos(b1) * 0.8, r * Math.sin(b1) * Math.sin(a1)], i * 3); }
      const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(arr, 3));
      const pts = new THREE.Points(g, new THREE.PointsMaterial({ color: c, size: 0.1, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
      root.add(pts); sparkSets.push(pts);
    });
    lFlash = new THREE.PointLight(EMERALD, 0, 0, 2); root.add(lFlash);
    shock = new THREE.Mesh(new THREE.TorusGeometry(1, 0.018, 8, 120), new THREE.MeshBasicMaterial({ color: EMERALD, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
    scene.add(shock);
  }

  /* ---- debu bintang ---- */
  const N = mode === "bg" ? 260 : 360;
  const pos = new Float32Array(N * 3);
  for (let i = 0; i < N; i++) {
    const r = 5 + rnd() * 9, a = rnd() * 6.283, b = Math.acos(2 * rnd() - 1);
    pos.set([r * Math.sin(b) * Math.cos(a), r * Math.cos(b) * 0.7, r * Math.sin(b) * Math.sin(a)], i * 3);
  }
  const starGeo = new THREE.BufferGeometry(); starGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({ color: 0x7dd3fc, size: 0.04, transparent: true, opacity: 0.6, depthWrite: false }));
  scene.add(stars);

  /* ---- ukuran & penempatan menurut mode ---- */
  const base = new THREE.Vector3(0, 0.2, 0);   // posisi dasar (tengah layar) untuk gerak melayang
  const place = () => {
    const w = canvas.clientWidth || innerWidth, h = canvas.clientHeight || innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
    const wide = w / h > 1.15;
    base.set(0, 0.2, 0);
    if (mode === "hero") {
      // controller di area atas; blok teks (±400px) tetap lega di bawah
      const unit = h / 7.58, avail = Math.max(240, h - 410);
      const padPx = Math.min(avail * 0.82, 430);
      root.scale.setScalar(Math.min(1.1, Math.max(0.3, padPx / (4.5 * unit))));
      base.set(0, 0.2 + (h / 2 - (avail / 2 + 14)) / unit, 0);
    }
    else if (mode === "auth") { root.scale.setScalar(wide ? 0.78 : 0.55); }
    else { root.scale.setScalar(wide ? 1.05 : 0.7); }
    root.position.copy(base);
  };
  place();
  new ResizeObserver(place).observe(canvas);

  /* ---- interaksi ---- */
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener("pointermove", (e) => { mouse.tx = (e.clientX / innerWidth - 0.5) * 2; mouse.ty = (e.clientY / innerHeight - 0.5) * 2; }, { passive: true });
  let scrollK = 0, scrollT = 0;
  const onScroll = () => { scrollT = Math.min(1, scrollY / Math.max(1, innerHeight * 1.2)); };
  addEventListener("scroll", onScroll, { passive: true }); onScroll();
  let kick = 0;                                   // klik: putaran 360 derajat cepat + denyut cahaya
  let origin = 0;                                 // awal siklus shatter (detik jam kanvas)
  const CYCLE = 10.5;
  addEventListener("pointerdown", () => {
    if (mode === "hero") { const c = (t - origin) % CYCLE; if (t > 1.5 && (c < 2.4 || c > 6.7)) origin = t - 2.5; }
    else if (mode === "auth" && kick < 0.15) kick = 1;
  });

  const clock = new THREE.Clock();
  let t = 0, running = true, last = 0;
  const frame = () => {
    if (!running) return;
    requestAnimationFrame(frame);
    const dt = Math.min(clock.getDelta(), 0.05);
    if (mode === "bg" && performance.now() - last < 33) return;   // latar halus: ~30 fps
    last = performance.now();
    t += dt;
    render(dt);
  };

  const smooth = (x) => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  let wt = 0, quatTmp = new THREE.Quaternion(), tmpV = new THREE.Vector3();

  // tingkat "terurai" e (0 utuh, 1 tersebar penuh) dan skala waktu menurut fase siklus Welcome
  function shatterState(c) {
    let e = 0, ts = 1;
    if (c >= 2.5 && c < 3.0) e = 0.8 * (1 - Math.pow(1 - (c - 2.5) / 0.5, 3));          // pecah cepat
    else if (c >= 3.0 && c < 5.2) e = 0.8 + 0.2 * smooth((c - 3.0) / 2.2);                // slow-motion
    else if (c >= 5.2 && c < 6.5) { const u = (c - 5.2) / 1.3; e = 1 - (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2); }   // tersedot kembali
    if (c >= 3.0 && c < 5.2) ts = 1 - 0.93 * Math.min(smooth((c - 3.0) / 0.15), 1 - smooth((c - 5.0) / 0.2));
    return { e, ts };
  }

  function render(dt) {
    mouse.x += (mouse.tx - mouse.x) * 0.05; mouse.y += (mouse.ty - mouse.y) * 0.05;
    scrollK += (scrollT - scrollK) * 0.06;
    kick = Math.max(0, kick - dt / 1.1);
    const intro = mode === "bg" ? 2.2 : 3.6;     // durasi perakitan awal (detik)
    const ki = ease(t / intro);

    // siklus shatter (hanya Welcome): dimulai setelah perakitan awal
    let e = 0, ts = 1, cyc = -1, flash = 0, cpulse = 0;
    if (mode === "hero") {
      if (origin === 0) origin = intro - 0.2;
      const c = t - origin;
      if (c >= 0) { cyc = c % CYCLE; const st = shatterState(cyc); e = st.e; ts = st.ts; }
      if (cyc >= 2.5 && cyc < 3.4) flash = cyc < 2.62 ? (cyc - 2.5) / 0.12 : Math.pow(Math.max(0, 1 - (cyc - 2.62) / 0.78), 2);
      if (cyc >= 6.2 && cyc < 7.4) cpulse = Math.sin(Math.PI * (cyc - 6.2) / 1.2);
    }
    wt += dt * ts;                                // waktu dunia: melambat (~0.07x) saat bullet-time

    // perakitan awal + kepingan terpental radial saat shatter
    const dip = scrollK * (mode === "bg" ? 0.5 : 1.4);
    for (const p of parts) {
      const k = ease((t - p.delay) / (intro - 0.9));
      const out = (1 - k) * 6.5 * p.spread + dip * p.spread;
      p.obj.position.copy(p.pos).addScaledVector(p.dir, out).addScaledVector(p.rad, p.blast * e);
      p.obj.scale.copy(p.scale).multiplyScalar(0.001 + 0.999 * k);
      p.obj.quaternion.copy(p.offQuat).slerp(p.quat, k);
      if (e > 0) { quatTmp.setFromAxisAngle(p.spinAxis, p.spinAng * e); p.obj.quaternion.premultiply(quatTmp); }
    }
    for (const d of debris) {
      d.m.position.copy(d.p0).addScaledVector(d.rad, d.blast * e);
      d.m.scale.setScalar(d.s * Math.min(1, e * 6));
      d.m.quaternion.setFromAxisAngle(d.axis, d.ang * e);
    }
    sparkSets.forEach((sp, i) => { sp.material.opacity = Math.min(1, e * 3) * 0.95; sp.rotation.y = wt * (i ? -0.12 : 0.09); sp.rotation.x = wt * 0.05; });
    if (lFlash) lFlash.intensity = flash * 700 + e * 25;
    if (chipMat) chipMat.emissiveIntensity = 1.6 + flash * 6 + e * 1.5;
    if (shock) {
      const s2 = cyc >= 2.5 ? (cyc - 2.5) / 0.9 : 2;
      shock.material.opacity = s2 < 1 ? (1 - s2) * 0.85 : 0;
      shock.scale.setScalar(0.4 + Math.min(1, s2) * 8 * root.scale.x);
      shock.position.copy(root.position); shock.quaternion.copy(camera.quaternion);
    }

    const pulse = Math.max(Math.sin(Math.PI * (1 - kick)) * (kick > 0 ? 1 : 0), cpulse, flash);
    for (const [m, i0] of glows) m.emissiveIntensity = i0 * (1 + pulse * 2.6 + 0.12 * Math.sin(t * 2 + i0));

    // melayang naik-turun, berayun, sesekali putar 360 derajat, miring mengikuti kursor
    const w2 = wt % 15, u = Math.min(1, Math.max(0, (w2 - 11) / 3.2));
    const turn = Math.PI * 2 * smooth(u);
    const kickTurn = Math.PI * 2 * (1 - kick * kick) * (kick > 0 ? 1 : 0);
    root.position.set(base.x, base.y + Math.sin(wt * 1.0) * 0.16, base.z);
    root.rotation.x = -0.4 + Math.sin(wt * 0.7) * 0.12 + mouse.y * 0.35;
    root.rotation.y = (1 - ki) * Math.PI * 1.6 + Math.sin(wt * 0.45) * 0.65 + turn + kickTurn + mouse.x * 0.5;
    root.rotation.z = Math.sin(wt * 0.52) * 0.1 - mouse.x * 0.12;
    camera.position.x = mouse.x * 0.5;
    camera.position.y = 1.4 - mouse.y * 0.4;
    camera.position.z = 11 + (mode === "bg" ? 0 : (1 - ki) * 6);   // zoom-in saat intro
    camera.lookAt(0, 0.2, 0);
    stars.rotation.y += dt * 0.02 * ts;
    lEm.position.x = 5 + Math.sin(t * 0.6) * 1.2;
    lCy.position.y = -2.5 + Math.cos(t * 0.5) * 1.0;
    renderer.render(scene, camera);
  }

  document.addEventListener("visibilitychange", () => {
    running = !document.hidden && !reduce;
    if (running) { clock.getDelta(); frame(); }
  });
  canvas.dataset.ready = "true";
  if (reduce) { t = 99; render(0); running = false; } else frame();
}

document.querySelectorAll("canvas[data-atlas3d]").forEach((c) => start(c).catch(() => { c.style.display = "none"; }));
