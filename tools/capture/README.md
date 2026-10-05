# tools/capture

Reproduces every generated image under `assets/` from a clean clone: the project
screenshots in the featured-work rows, the terminal renders, the Open Graph image,
and the before/after page screenshots used in pull requests.

Pinned: Playwright 1.56.1 (headless Chromium, the build Playwright ships), sharp 0.34.3.
Needs Node 22+, Python 3.10+, git, and network access to GitHub, PyPI and npm.

```bash
cd tools/capture
npm ci                         # playwright + sharp, exact versions from package-lock.json
npx playwright install chromium   # skip if PLAYWRIGHT_BROWSERS_PATH already has it
bash run-clis.sh               # clones each project under work/, runs its quick-start,
                               # writes terminal/*.txt and builds the Chat Buddy app
node capture.mjs               # writes assets/*.png + *.webp (+ og-hero.png, the two SVGs)
```

`node capture.mjs <job> …` runs a subset. Jobs, in the order of the featured rows:

| job | output | source |
|---|---|---|
| `ief4d` | `governed-data-ief-4d` | `/governed-data/ief-4d/ief-telecom-disclosure-4d-demo.html` in this repo, "Play both phases", paused after 42 s |
| `gd4d` | `governed-data-4d` | `/governed-data/governed-data-4d.html`, Act 1 stepped to beat 6 of 9 |
| `aiev` | `ai-evidence-record` | transcript of `aiev run-demo / verify / ask / tamper / verify` (`terminal/ai-evidence-record.txt`) |
| `modelev` | `model-evidence` | transcript of `node dist/run-evidence.mjs` on the v2 example (`terminal/model-evidence.txt`) |
| `edshield` | `edshield-demo` | `edshield/demo/index.html`, "Rules only" detector, after Redact |
| `corpuscle` | `corpuscle` | transcript of `corpuscle keygen / scan / verify` on the fixture corpus (`terminal/corpuscle.txt`) |
| `rxguard` | `rxguard-pharmacy-evidence`, `rxguard-mfp` | `/pharmacy-evidence/` and `/rxguard-mfp/` in this repo |
| `svgs` | `retro-flow.svg`, `edshield-evidence-agent-loop.svg` | copied from `retro/docs/` and `edshield-evidence/docs/` |
| `grocery` | `grocery-verdict-{light,dark}.webp` | WebP siblings of the PNGs already in `assets/` (from `grocery_optimizer/docs/screenshots/`) |
| `sanbuddy` | `sanbuddy-wizard`, `sanbuddy-chat` | the Chat Buddy production build on a local port, placeholder family (child "Alex", buddy "Rocky"), 820×1180 |
| `og` | `og-hero.png` | `templates/og.html`, 1200×630 |
| `site` | `screenshots/<label>-{desktop,mobile}[-dark].webp` | `--label before|after --page <html>`; full-page at 1440 and 390 wide, light and dark |

Desktop captures are 1280×800 at 2× device pixels; tablet captures are 820×1180 at 2×.
PNGs are palette-quantised and each gets a WebP sibling; the page serves WebP with PNG fallback.

The transcripts under `terminal/` are committed so the terminal renders need no CLI installed;
`run-clis.sh` regenerates them. `learned-behavior` is installed from PyPI (0.2.0) and its
transcript is the six-line ledger shown on the page, not an image.

Branches: every repo is cloned at its default branch. `model-evidence`, `corpuscle`, `edshield`,
`edshield-evidence` and `retro` are pinned to `main`; `ai-evidence-record` and `sanbuddy` have a
single branch, which is their default.

No real data appears in any capture: Chat Buddy uses placeholder names, RxGuard pages carry
their synthetic dataset, edshield's sample essay is synthetic, and the evidence-record demo is
seeded synthetic data.
