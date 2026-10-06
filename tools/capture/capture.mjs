// Reproducible captures for hemangnagar.dev.
//
//   npm ci && bash run-clis.sh        # once: clones, quick-starts, terminal transcripts
//   node capture.mjs                  # every asset in ../../assets/
//   node capture.mjs ief4d edshield   # a subset (job names below)
//   node capture.mjs site --label after --page ../../index.html   # PR screenshots
//
// Every UI capture is 1280×800 (desktop) or 820×1180 (tablet) at 2× device pixels and is
// written as PNG plus a WebP sibling. Terminal captures render a committed transcript from
// ./terminal/ into templates/terminal.html so they need no CLI to be installed.
import { chromium } from "playwright";
import sharp from "sharp";
import { spawn } from "node:child_process";
import { copyFile, mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import net from "node:net";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.resolve(HERE, "../..");
const ASSETS = path.join(SITE, "assets");
const WORK = path.join(HERE, "work");
const SHOTS = path.join(HERE, "screenshots");
const fileUrl = (p) => pathToFileURL(p).href;

const args = process.argv.slice(2);
const opt = (name, dflt) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : dflt; };
const jobsWanted = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--")));

const BROWSER_ARGS = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--font-render-hinting=none"];
const DESKTOP = { width: 1280, height: 800 };
const TABLET = { width: 820, height: 1180 };

let browser;
async function page(viewport, { scale = 2, dark = false } = {}) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: scale, colorScheme: dark ? "dark" : "light", reducedMotion: "reduce", ignoreHTTPSErrors: true });
  return ctx.newPage();
}

// PNG (palette-quantised, lossless-looking at UI content) plus a WebP sibling. Aims at ≤ 200 KB each.
async function save(buf, name, { pngQuality = 80, webpQuality = 82, palette = true } = {}) {
  await mkdir(ASSETS, { recursive: true });
  const png = path.join(ASSETS, `${name}.png`), webp = path.join(ASSETS, `${name}.webp`);
  let img = sharp(buf);
  await img.clone().png(palette ? { palette: true, quality: pngQuality, effort: 10, compressionLevel: 9 } : { compressionLevel: 9 }).toFile(png);
  await img.clone().webp({ quality: webpQuality, effort: 6 }).toFile(webp);
  const kb = async (p) => Math.round((await stat(p)).size / 1024);
  const meta = await img.metadata();
  console.log(`  ${name}: ${meta.width}×${meta.height}  png ${await kb(png)} KB  webp ${await kb(webp)} KB`);
}

async function terminal(name, title, { fontSize } = {}) {
  const text = await readFile(path.join(HERE, "terminal", `${name}.txt`), "utf8");
  const p = await page(DESKTOP);
  await p.goto(fileUrl(path.join(HERE, "templates", "terminal.html")));
  await p.evaluate(({ title, text, fontSize }) => window.renderTerminal({ title, text, fontSize }), { title, text: text.replace(/\s+$/, ""), fontSize });
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  // Clip to the terminal frame plus a margin, so the image is as tall as its transcript.
  const box = await p.locator(".frame").boundingBox();
  const m = 28, clip = { x: 0, y: Math.max(0, box.y - m), width: DESKTOP.width, height: Math.min(DESKTOP.height, box.height + 2 * m) };
  await save(await p.screenshot({ type: "png", clip }), name);
  await p.context().close();
}

async function waitForPort(port, ms = 90000) {
  const t0 = Date.now();
  while (Date.now() - t0 < ms) {
    const ok = await new Promise((res) => { const s = net.connect(port, "127.0.0.1"); s.once("connect", () => { s.end(); res(true); }); s.once("error", () => res(false)); });
    if (ok) return;
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`port ${port} never opened`);
}

const jobs = {
  // 1 · Governed Data Platform: the IEF chain in space and time (primary) …
  async ief4d() {
    const p = await page(DESKTOP);
    await p.goto(fileUrl(path.join(SITE, "governed-data/ief-4d/ief-telecom-disclosure-4d-demo.html")), { waitUntil: "load" });
    await p.waitForTimeout(1500);
    await p.getByRole("button", { name: /Play both phases/ }).click();
    await p.waitForTimeout(42000);           // let the chain build and the first files flow
    await p.keyboard.press("Space");         // pause
    await p.waitForTimeout(800);
    await save(await p.screenshot({ type: "png" }), "governed-data-ief-4d", { pngQuality: 70, webpQuality: 76 });
    await p.context().close();
  },
  // … and the one-source-released-three-ways replay (hover/tap swap).
  async gd4d() {
    const p = await page(DESKTOP);
    await p.goto(fileUrl(path.join(SITE, "governed-data/governed-data-4d.html")), { waitUntil: "load" });
    await p.waitForTimeout(1500);
    // The page notes software rendering when there is no GPU; that is a property of the capture box, not the demo.
    await p.evaluate(() => { for (const el of document.querySelectorAll("div,p,span")) if (el.childElementCount === 0 && /no GPU here/i.test(el.textContent)) (el.closest("div") || el).style.display = "none"; });
    const next = p.getByRole("button", { name: "→" }).first();
    for (let i = 0; i < 5; i++) { await next.click(); await p.waitForTimeout(1200); }
    await p.waitForTimeout(1500);
    await save(await p.screenshot({ type: "png" }), "governed-data-4d", { pngQuality: 60, webpQuality: 72 });
    await p.context().close();
  },
  // 2 · AI Evidence Record + Model Evidence
  async aiev() { await terminal("ai-evidence-record", "ai-evidence-record · aiev", { fontSize: 13.5 }); },
  async modelev() { await terminal("model-evidence", "model-evidence · run-evidence.mjs", { fontSize: 15 }); },
  // 3 · edshield browser demo (rules-only detector: no model download, nothing leaves the page)
  async edshield() {
    const p = await page(DESKTOP);
    await p.goto(fileUrl(path.join(WORK, "edshield/demo/index.html")), { waitUntil: "load" });
    await p.waitForTimeout(800);
    await p.selectOption("#engine", "rules");
    await p.click("#run");
    await p.waitForTimeout(1200);
    await save(await p.screenshot({ type: "png" }), "edshield-demo");
    await p.context().close();
  },
  // 4 · corpuscle sample scan
  async corpuscle() { await terminal("corpuscle", "corpuscle · scan → verify", { fontSize: 15 }); },
  // 6 · RxGuard: the two pages hosted in this repo
  async rxguard() {
    for (const [file, name] of [["pharmacy-evidence/index.html", "rxguard-pharmacy-evidence"], ["rxguard-mfp/index.html", "rxguard-mfp"]]) {
      const p = await page(DESKTOP);
      await p.goto(fileUrl(path.join(SITE, file)), { waitUntil: "load" });
      await p.waitForTimeout(1500);
      await save(await p.screenshot({ type: "png" }), name);
      await p.context().close();
    }
  },
  // 7 · diagrams reused as-is from their repos
  async svgs() {
    await copyFile(path.join(WORK, "retro/docs/retro-flow.svg"), path.join(ASSETS, "retro-flow.svg"));
    await copyFile(path.join(WORK, "edshield-evidence/docs/edshield-agent-loop.svg"), path.join(ASSETS, "edshield-evidence-agent-loop.svg"));
    console.log("  copied retro-flow.svg, edshield-evidence-agent-loop.svg");
  },
  // 5 · Grocery Basket Optimizer: WebP siblings for the screenshots already in assets/
  async grocery() {
    for (const n of ["grocery-verdict-light", "grocery-verdict-dark", "grocery-verdict-exact"]) {
      const src = path.join(ASSETS, `${n}.png`);
      await sharp(src).webp({ quality: 82, effort: 6 }).toFile(path.join(ASSETS, `${n}.webp`));
      console.log(`  ${n}.webp from ${n}.png`);
    }
  },
  // 8 · Chat Buddy: the real app on a local port, a placeholder family, an iPad-sized viewport
  async sanbuddy() {
    const dir = path.join(WORK, "sanbuddy");
    let url = process.env.SANBUDDY_URL, child;
    if (!url) {
      const port = 3017;
      child = spawn("npx", ["next", "start", "-p", String(port)], { cwd: dir, stdio: "ignore", env: { ...process.env, NEXT_TELEMETRY_DISABLED: "1" } });
      await waitForPort(port);
      url = `http://localhost:${port}/`;   // next dev treats 127.0.0.1 as a cross origin
    }
    try {
      // Parent setup wizard, driven through the UI with placeholder values.
      const hideBadge = (pg) => pg.addStyleTag({ content: "nextjs-portal, [data-nextjs-dev-tools-button], [data-next-badge-root] { display: none !important; }" });
      let p = await page(TABLET);
      await p.goto(url, { waitUntil: "networkidle" });
      await hideBadge(p);
      await p.getByPlaceholder("e.g. San").fill("Alex");
      await p.getByPlaceholder("e.g. 15").fill("10");
      await p.getByRole("button", { name: "Next", exact: true }).click();
      await p.getByRole("button", { name: /Developing/ }).click();
      await p.getByRole("button", { name: "Next", exact: true }).click();
      await p.getByPlaceholder(/Bollywood movies/).fill("dinosaurs, trains, Minecraft");
      await p.getByPlaceholder(/favorite wrestlers/).fill("Loves being asked which dinosaur is the fastest.");
      await p.waitForTimeout(500);
      await save(await p.screenshot({ type: "png" }), "sanbuddy-wizard");
      await p.context().close();

      // Chat view: seed the app's own storage with a finished profile and a short placeholder conversation.
      const data = {
        version: 1, savedAt: Date.now(),
        profile: { childName: "Alex", childAge: "10", communicationLevel: "developing", interests: "dinosaurs, trains, Minecraft", notes: "", skillTargets: ["wh_questions", "turn_taking"], supportLevel: 2, buddyName: "Rocky", buddyAvatar: "🦖", buddyColor: "#10b981", parentPin: "0000" },
        messages: [
          { id: "m1", role: "assistant", text: "Hi Alex! 🦖 I heard you like dinosaurs. Which one is your favorite?", chips: ["T. rex", "Velociraptor", "I'm not sure"], ts: Date.now() - 400000 },
          { id: "m2", role: "user", text: "T. rex", ts: Date.now() - 300000 },
          { id: "m3", role: "assistant", text: "T. rex is a great pick! Where do you think a T. rex would live?", chips: ["In a forest", "Near a river", "In a museum"], ts: Date.now() - 200000 },
          { id: "m4", role: "user", text: "near a river so it can drink", ts: Date.now() - 100000 },
          { id: "m5", role: "assistant", text: "Near a river so it can drink. Smart thinking! Who would you take to see a real T. rex?", chips: ["My mom", "My friend", "My teacher"], ts: Date.now() - 50000 },
        ],
        settings: { apiKey: "placeholder-for-capture", model: "claude-sonnet-4-6", autoRead: false },
      };
      p = await page(TABLET);
      await p.goto(url, { waitUntil: "networkidle" });
      await p.evaluate((d) => localStorage.setItem("chat-buddy-data-v1", JSON.stringify(d)), data);
      await p.goto(url, { waitUntil: "networkidle" });
      await hideBadge(p);
      await p.waitForTimeout(800);
      await save(await p.screenshot({ type: "png" }), "sanbuddy-chat");
      await p.context().close();
    } finally { child?.kill(); }
  },
  // Open Graph image, 1200×630, composed from the hero captures.
  async og() {
    const p = await page({ width: 1200, height: 630 }, { scale: 1 });
    await p.goto(fileUrl(path.join(HERE, "templates", "og.html")), { waitUntil: "networkidle" });
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(500);
    const buf = await p.screenshot({ type: "png" });
    await sharp(buf).png({ palette: true, quality: 90, effort: 10 }).toFile(path.join(ASSETS, "og-hero.png"));
    console.log(`  og-hero.png: ${Math.round((await stat(path.join(ASSETS, "og-hero.png"))).size / 1024)} KB`);
    await p.context().close();
  },
  // Full-page screenshots of the site (desktop + mobile, light + dark) for the PR description.
  // Stitched from viewport-height tiles after a scroll-through, so lazy images and scroll-in sections are settled.
  async site() {
    const label = opt("label", "after"), target = path.resolve(opt("page", path.join(SITE, "index.html")));
    await mkdir(SHOTS, { recursive: true });
    for (const [name, viewport] of [["desktop", { width: 1440, height: 900 }], ["mobile", { width: 390, height: 844 }]]) {
      for (const dark of [false, true]) {
        const p = await page(viewport, { scale: 1, dark });
        await p.goto(fileUrl(target), { waitUntil: "load" });
        await p.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});   // fonts and lazy assets; carry on if a third party stalls
        await p.addStyleTag({ content: ".sticky { display: none !important; }" });
        await p.evaluate(() => document.fonts.ready.then(() => true));
        const H = await p.evaluate(() => document.documentElement.scrollHeight);
        for (let y = 0; y < H; y += Math.round(viewport.height * 0.8)) { await p.evaluate((y) => scrollTo(0, y), y); await p.waitForTimeout(80); }
        const tiles = [];
        for (let y = 0; y < H; y += viewport.height) {
          const top = Math.min(y, H - viewport.height);
          await p.evaluate((y) => scrollTo(0, y), top);
          await p.waitForTimeout(250);
          const buf = await p.screenshot({ type: "png" });
          const cut = y - top;   // the last tile overlaps the one before it
          tiles.push({ top: y, input: cut ? await sharp(buf).extract({ left: 0, top: cut, width: viewport.width, height: viewport.height - cut }).toBuffer() : buf });
        }
        const out = path.join(SHOTS, `${label}-${name}${dark ? "-dark" : ""}.webp`);
        await sharp({ create: { width: viewport.width, height: H, channels: 3, background: "#ffffff" } })
          .composite(tiles.map((t) => ({ input: t.input, top: t.top, left: 0 })))
          .webp({ quality: 82, effort: 6 }).toFile(out);
        console.log(`  ${path.relative(HERE, out)} ${viewport.width}×${H} ${Math.round((await stat(out)).size / 1024)} KB`);
        await p.context().close();
      }
    }
  },
};

const order = ["ief4d", "gd4d", "aiev", "modelev", "edshield", "corpuscle", "rxguard", "svgs", "grocery", "sanbuddy", "og"];
const run = jobsWanted.length ? jobsWanted : order;
for (const j of run) if (!jobs[j]) { console.error(`unknown job ${j}; known: ${Object.keys(jobs).join(" ")}`); process.exit(2); }
browser = await chromium.launch({ args: BROWSER_ARGS });
try {
  for (const j of run) { console.log(`▶ ${j}`); await jobs[j](); }
} finally { await browser.close(); }
