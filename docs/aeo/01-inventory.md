# Problem pages & AEO layer — step 1: inventory

Status: waiting for Hemang's go-ahead before any page is written.
Date: 2026-10-07 · Author: Hemang Nagar (prepared with Claude Code)

## 1. Existing pages

Inbound = links from other pages in this repo. "No desc" means the page has no meta description today.

| URL | Title (chars) | Description | H1 | Canonical / JSON-LD | Inbound from |
|---|---|---|---|---|---|
| `/` | Hemang Nagar — data & AI engineering, Washington, DC (52) | 289 chars (over the 155 cap) | The LLM proposes. The pipeline disposes. | yes / Person | every demo page's "← Hemang Nagar" link |
| `/governed-data/` | Governed Data Platform — demos — Hemang Nagar (45) | 179 chars | Profile-driven governance for data in motion. | no / none | home (row 1) |
| `/governed-data/governed-data-4d.html` | Governed Data, in Four Dimensions (33) | 210 chars | Governed data, in four dimensions | no / none | governed-data index |
| `/governed-data/ief/*-demo.html` ×3 | "… \| IEF in action" (40–42) | no desc | empty `<h1>` (filled by script) | no / none | governed-data index |
| `/governed-data/ief-4d/*-4d-demo.html` ×3 | "… \| IEF in 4D" (36–38) | no desc | empty `<h1>` (filled by script) | no / none | governed-data index |
| `/governed-data/runbooks/sapient-demo-runbook.html` | SAPIENT Demo Runbook (20) | no desc | SAPIENT: reading the standard the sensors speak… | no / none | governed-data index |
| `/governed-data/runbooks/counter-uas-demo-runbook.html` | Counter-UAS Demo Runbook (24) | no desc | Counter-UAS: what the platform refuses… | no / none | governed-data index |
| `/pharmacy-evidence/` | Pharmacy Evidence Engine (24) | 182 chars | One engine, three possible markets. | no / none | home (row 6) |
| `/rxguard-mfp/` | RxGuard MFP Ledger (18) | no desc | none (app shell, no `<h1>`) | no / none | home (row 6), pharmacy-evidence |
| `/decision-gate/` | Decision Gate — Hemang Nagar (28) | 138 chars | AI can argue forever. Decisions cannot. | no / none | **none** (orphan by design since the redesign) |
| `/assets/hemang-nagar-resume.pdf` | — | — | — | in sitemap | home (nav, hiring band) |

Other facts about the current site:

- Deploy: GitHub Pages, "pages build and deployment" from `main`, default Jekyll build (`_config.yml` only excludes `promote` and `tools`). No GitHub Actions workflow of our own, so there is no CI today.
- `index.html` is a single hand-written file, inline CSS, three small vanilla-JS behaviours. The demo folders are copied verbatim from their source repos and the earlier brief says not to modify them.
- `sitemap.xml` and `robots.txt` are hand-written (added in the redesign). `robots.txt` allows everything except `/promote/`; it names no crawlers individually.
- The home page already carries a JSON-LD `Person` and a canonical. No other page has either.
- Trailing-slash state: folders with `index.html` are reached as `/x/`; the demo files are `.html` URLs. GitHub Pages 301-redirects `/x` → `/x/` on its own. No URLs were retired by the redesign (the old page used `#work` and `#engage` anchors only), so there is no legacy redirect map to build.
- Title suffix today is "— Hemang Nagar" on two pages and absent on the rest; the brief wants " | Hemang Nagar". The home page's own `<title>` does not follow the H1-first rule either.

## 2. Evidence per problem page

Legend: ✅ in the repo now · ⚠ exists but differs from the brief · ❌ not in any repo (would need a `<!-- TODO: evidence -->` marker or Hemang's input).

### 2.1 Governed Data Platform → `/problems/governance-on-data-in-motion`

Source material: this repo's `/governed-data/` demos only. The platform repo is private.

- ✅ The 4D scene and the three IEF walkthroughs (flat and 4D), with their counts (2,000 records per act; 456 minimised, 89 withheld; 1,800/200, 1,544/456, 49/1 promoted/quarantined).
- ✅ Two runbooks (SAPIENT / BSI Flex 335, Counter-UAS / ASTM F3411) describing runs against the deployed container, with the "obligations attach at enrichment, not at the sensor" finding.
- ✅ Screenshots already captured for the redesign (`assets/governed-data-ief-4d.*`, `assets/governed-data-4d.*`).
- ⚠ The demo index already calls the controls "OMG IEF" chains; the page will say "based on" / "aligned with" as the brief requires.
- ❌ "Ego-network and anomaly plots" and "GraphRAG on contact networks": nothing in this repo mentions GraphRAG, ego networks or anomaly plots. These secondary queries have no evidence here.
- ❌ "A profile file as a code sample": no profile file is public. Hemang would need to supply a redacted excerpt.
- ❌ "Medallion architecture with policy enforcement": the demos describe profiles, controls, quarantine and release sets, not bronze/silver/gold. The page can describe what the demos show; it should not claim a medallion layout.

### 2.2 AI Evidence Record + Model Evidence → `/problems/prove-a-model-meets-criteria`

Source: `hemangnagar/model-evidence` (public, tag `v2.0.0`), `hemangnagar/ai-evidence-record` (public), `hemangnagar/edshield-evidence` (public, uses model-evidence v2.0.0 as its judge).

- ✅ Sample evidence output: the `run-evidence.mjs` verdict table on `dist/examples/bundle-v2.json` + `policy-v2.json` (already rendered as `assets/model-evidence.*`). Exit codes 0/1/2/3.
- ✅ A criteria file: `dist/examples/policy-v2.json`; `dist/CONTRACT.md` documents contract 2.0 (views, null gates, cluster bootstrap, hashes).
- ✅ Multi-view output: span + document views in the example; stability on seed spread; reproducibility by hash comparison.
- ✅ Seed stability: factory experiment repeats training with three seeds and an exact same-seed rerun; 30 checks in `npm test`.
- ✅ A sealed acceptance set: `edshield-evidence` seals A1 with AES-256-GCM and records `used_for_decision`; its `evidence/ledger.md` has real rows (identifier recall 1.0000 [1.0000, 1.0000] on the PIILO holdout, rules+model; 0.7669 on k12_hard).
- ⚠ The project card pairs model-evidence with **ai-evidence-record** (the clinical-trial ledger). The brief's page is about model acceptance only. Suggest: the page treats model-evidence as the subject and mentions ai-evidence-record in one paragraph as the "sibling evidence record for AI outputs in a regulated process," or it gets its own page later. Hemang decides.
- ⚠ The hosted app (`model-evidence.hemnag.chatgpt.site`) is owner-private per the README; the page should link the repo, not the app.

### 2.3 edshield + edshield-evidence → `/problems/student-pii-detection-local-first`

Source: `hemangnagar/edshield` (public, Apache-2.0, PyPI `edshield` 0.2.0), `hemangnagar/edshield-evidence` (public).

- ✅ PyPI 0.2.0; Hugging Face weights `edshield/piilo-deberta-v3-small` and the ONNX INT8 export; FERPA/COPPA/research policies; verifier that refuses output with a leak; audit record with no student text.
- ✅ Benchmarks from the README: on 680 held-out PIILO documents, rules+model precision 0.642 / recall 1.000 / F5 0.979, 0 of 165 missed; browser INT8 file 0.639 / 1.000 / 0.979. Synthetic K-12 "hard" set: 319 of 1,433 identifiers get through (22%) with the model, 1,100 (77%) rules-only.
- ✅ edshield-evidence ledger rows (above) and the agent-loop diagram (`assets/edshield-evidence-agent-loop.svg`), which also states "76.7% → 88.5% → 99.4%" for the child-style practice set across release / new rules / retrained model.
- ✅ Browser demo screenshot (`assets/edshield-demo.*`), rules-only mode.
- ⚠ **The brief's figures "recall ~0.999 and F5 ~0.995 on validation" do not appear in either repo.** The README says recall 1.000 and F5 0.979. The page will use the README figures unless Hemang points at the run that produced 0.999/0.995.
- ⚠ Live demo at `hemangnagar.dev/edshield/`: the edshield repo's `pages.yml` deploys `demo/` as a project site, which GitHub serves under this domain. I cannot reach the domain from the sandbox; Hemang should confirm the URL resolves (it is already linked from the home page).

### 2.4 corpuscle → `/problems/auditable-corpus-datasheet`

Source: `hemangnagar/corpuscle` (public; `pyproject.toml` says license "Proprietary", so no license chip).

- ✅ Metric catalog: 97 metric IDs across ten families (`catalog/metric-catalog.yaml`).
- ✅ Signed-manifest round trip: keygen → scan → verify transcript on the 14-document fixture, two duplication findings, seven PASS checks (`assets/corpuscle.*`); DSSE over an in-toto Statement, Ed25519, Merkle root, records keyed by content hash.
- ✅ API spec: `api/openapi.yaml` (3.1, async scan jobs, proposals require an approver; MCP mirrors it).
- ✅ Agent layer: triage investigator, proposals, named approval, agent runs recorded in the manifest.
- ❌ "Dedup and language ID at scale with PySpark": the README lists the PySpark runner and the language family under Phase 1 (roadmap). Only the duplication family is built (exact + MinHash/LSH near-duplicates, in-process). The page will not claim Spark or language ID.
- ❌ "PII scan for training data" and "EU AI Act training data documentation": no PII detector and no EU AI Act mapping in the repo. The compliance and provenance families are roadmap. These can be framed as what a datasheet is *for* only if Hemang wants that context; they cannot be claimed as features.

### 2.5 Grocery Basket Optimizer → `/problems/llm-proposes-pipeline-disposes`

Source: `hemangnagar/grocery_optimizer` (public, MIT, CI on Windows + Linux).

- ✅ Verdict PWA screenshots (`assets/grocery-verdict-*.png/webp`, light/dark/exact).
- ✅ A gate rule: `src/grocery_optimizer/gold/contract.py` enforces `match_confidence >= 0.85` ("trustGate") on `gold_current_prices`; the ODCS v3 contract is `contracts/gold_current_prices.odcs.yaml`; below-threshold pairs go to `adjudicate` / a human review queue.
- ✅ The three gated judgment points (entity adjudicator with verdict cache, parser self-healing with byte-for-byte replay gate, narrator with audit gate) and the OpenLineage event per run.
- ❌ "A match-confidence distribution": no plot or table of the confidence distribution is in the repo. Either Hemang runs the pipeline and exports one, or the page shows the gate rule and the queue mechanics without a distribution.

### 2.6 RxGuard → `/problems/explainable-pharmacy-safety-checks` — **the brief's framing does not match the code**

Source: `hemangnagar/rxguard` (public, MIT, CycloneDX SBOM, CI).

- What RxGuard actually is: evidence-first **pharmacy margin and exception analysis**. It joins payer return, pharmacy cost and later adjustments, flags loss-making fills, unresolved reversals, rejected claims and incomplete audit packets, emits FHIR R4B `ExplanationOfBenefit` with the CARIN pharmacy profile URI, and gates every explanation so it cannot cite a dollar absent from the fact pack (`rxguard/explain.py: gate_explanation`). The MFP Refund Ledger module reconciles Medicare negotiated-price refunds (47-fill synthetic ledger, 14-day window, escalation letter behind the same gate).
- The README's "deliberately not implemented" list includes **clinical recommendations, substitution, dosing or interaction checking**. So "drug interaction checker with explanations" and "pharmacy safety check" describe something the repo explicitly does not do.
- Proposed H1 instead: **"How do you build a pharmacy exception check that explains every flag it raises?"** (slug `/problems/explainable-pharmacy-exception-checks`), secondary queries: pharmacy margin analysis with evidence; unresolved reversal detection; FHIR ExplanationOfBenefit for pharmacy claims; Medicare MFP refund reconciliation; gated LLM explanations that cannot invent a number.
- ✅ Evidence: the six reproducible scenarios with expected results; the explanation gate's four rules; a scenario JSON as the "rule definition"; the MFP ledger screenshot (`assets/rxguard-mfp.*`); the gate module path.
- ✅ Bonus: `rxguard/retro.json` is a real `/retro` output (dated 2026-09-03) — evidence for page 2.7.

### 2.7 retro + learned-behavior → `/problems/carry-lessons-across-ai-coding-projects`

Source: `hemangnagar/retro` (public, MIT), `hemangnagar/learned-behavior` (public, MIT, PyPI 0.2.0).

- ✅ Skill definition: `SKILL.md` (trigger wording, interview, scope menu, write-out steps).
- ✅ A retro output on a real repo: `rxguard/retro.json` (milestone, interview answers, lessons, scopes).
- ✅ The flow diagram (`assets/retro-flow.svg`), the three rules (ritual, scope, budget: 25-slot playbook), the playbook template (`playbook.md`).
- ✅ learned-behavior as the input: five Claude Code hooks, candidate → approved → dormant lifecycle, four miners, local SQLite, no network; the install-and-first-hook transcript already on the home page.
- ⚠ "Before/after example": no committed before/after of a playbook. The rxguard retro.json shows lessons and their scopes, which can stand in; a literal before/after would need Hemang to supply a playbook diff.
- ⚠ Both READMEs link `github.com/lisn0/learned-behavior`; the site links `hemangnagar/learned-behavior` (both exist). Hemang should say which is canonical.

### 2.8 Chat Buddy → `/problems/safe-chatbot-for-kids`

Source: `hemangnagar/sanbuddy` (public, MIT).

- ✅ Screenshots with a placeholder family (`assets/sanbuddy-wizard.*`, `assets/sanbuddy-chat.*`).
- ✅ Guardrail design: `docs/PROTECTED-CORE.md` (friend-not-therapist, recast-never-correct, one question per message, choice-first scaffolding, support-level slider 1–4, pointing the child toward real people) and `lib/systemPrompt.ts`; privacy charter (no accounts, no server storage, no telemetry, family's own API key via a stateless proxy, parent can read everything, PIN-gated dashboard).
- ⚠ "Without a cloud account": the app needs the family's own Anthropic API key, which is a cloud account with the model provider. The accurate claim is "no account with us, no server-side storage, the family's own key"; the H1 may need rewording to "…without handing a child's data to anyone."
- Note: the brief says "no COPPA language" here, which matches the README.

### 2.9 Mobius → `/work/mobius-cdr-fraud-detection`

Source: this brief and the earlier redesign brief only; no code, no customer or country names.

- ✅ Figures supplied by Hemang: hourly two-server batch → 30-minute CDR windows against 24 h of per-MSISDN history; latency 1 h+ → under 30 min; 28 nodes at 3B+ voice CDRs/day, later 50B+ SMS/day (1B+ per 30-minute window); 30M/day on 2 nodes (new in this brief); A2P/OTP SMS bypass reuse; HA namenode fix; live since 2015; at-risk accounts stayed. Stack: Hadoop, Spark, HBase + Phoenix, MongoDB, Node.js, AWS (S3, Lambda, EMR).
- ✅ Résumé corroborates the role (Head of Product Development / Chief Architect, Mobius Wireless Solution, Ashburn VA, 2015–2026) and the cross-source OTP/SMS correlation, RAG platform and Spark pipelines.
- ❌ Architecture sketch: none exists. I would draw a static SVG from the description (two-server batch → Spark windows → rules engine → Node.js UI), for Hemang to approve.
- Secondary query "sizing a Spark cluster for 3B+ CDRs a day": the only sizing facts are 28 nodes / 3B+ and 2 nodes / 30M. No node specs, so the page can report the ratio but not a sizing method.

### 2.10 `/about` and `/services` facts

From the brief: 20+ years; a decade-plus of Spark; domains (financial institutions, federal and law-enforcement data, telecom fraud); Northern Virginia; KYM Advisors employer and role; Collibra certified Architect; cleared without naming the level.

- ✅ Résumé confirms: 20+ years; Vienna, Virginia; KYM Advisors Inc., Engineer / Technical Lead, ODNI / IC programs, Feb 2022–present (full-time since May 2026); Spark from 2015 at Mobius onward; Rensselaer master's degrees (two) and a Mumbai bachelor's.
- ❌ **Collibra certified Architect is not on the résumé.** The page will carry it only if Hemang confirms the exact credential name.
- ⚠ **Clearance level conflict.** The brief says the site never names the level, but `assets/hemang-nagar-resume.pdf` (merged yesterday at Hemang's request) says "Active TS/SCI Clearance" on its first line, and the hero has an `INCLUDE_CLEARANCE` switch for a "TS/SCI cleared" chip (off). Options: (a) accept that the PDF names it and keep HTML pages to "cleared"; (b) publish a web version of the résumé without the level. Hemang decides.
- Services: the three existing engagements (governance readiness assessment, contracts and lineage implemented, LLM-in-the-pipeline design review) are the nouns; the brief allows a fourth. No pricing exists anywhere; the page will not invent one.

## 3. Build approach (decision needed)

The brief wants templates, front matter, build-time generation of `llms.txt` / `sitemap.xml` / RSS, and CI checks, while keeping the site static.

**Recommended: keep the default GitHub Pages Jekyll build, add CI alongside it.**

- Problem pages, `/about`, `/services`, `/work/mobius-…` and `/problems/` become Markdown files with front matter and one Jekyll layout (`_layouts/problem.html`) that reuses the home page's CSS variables and components. JSON-LD and breadcrumbs are Liquid includes driven by front matter.
- `llms.txt`, `sitemap.xml` and `feed.xml` become Liquid templates that iterate the same front matter, so they cannot drift. No plugins beyond what GitHub Pages already allows.
- `index.html` and the demo folders stay plain files (Jekyll copies them unchanged); the project cards only gain a "Why this matters →" link to their problem page.
- CI: a GitHub Actions workflow on pull requests runs `jekyll build` with the `github-pages` gem, then the hygiene checks (front-matter lint, one H1, link graph, lychee, JSON-LD validation, Lighthouse CI on four pages). It does not deploy; Pages keeps deploying `main` as it does now.
- Redirects: nothing to redirect today. If the trailing-slash policy is `/problems/slug/`, Pages already 301s the slash-less form, so no redirect map is needed yet; a `_redirects.yml` convention can be added when a URL first moves.

Alternative: switch Pages to deploy from an Actions workflow. More control (any generator, build-time image work) at the cost of changing the Pages source setting and adding a deploy step. Not needed for this brief.

## 4. Questions for Hemang before step 2

1. RxGuard page: approve the re-framed H1 "How do you build a pharmacy exception check that explains every flag it raises?" (and the slug change), since the code has no drug-interaction or clinical safety checks.
2. edshield figures: use the README's recall 1.000 / F5 0.979 on 680 held-out essays, or point me at the run behind "~0.999 / ~0.995".
3. Governed Data Platform: drop the GraphRAG / ego-network / medallion secondary queries (no evidence in this repo), or supply material. Supply a redacted profile excerpt if the "profile file as a code sample" should appear.
4. Model Evidence page: model-evidence as the subject with ai-evidence-record as one paragraph, or two pages?
5. Collibra certification: exact credential name, or leave it out.
6. Clearance level: keep the PDF as published, or replace it with a web version that says "cleared" only.
7. learned-behavior canonical repo: `hemangnagar/learned-behavior` or `lisn0/learned-behavior`.
8. Confirm `https://hemangnagar.dev/edshield/` serves the edshield demo.
9. Build approach: default Pages Jekyll build + CI on PRs (recommended), or Pages deployed from Actions.
10. `/decision-gate/` is an orphan today. Leave it unlisted (current state), link it from somewhere, or add it to the sitemap?

Nothing in sections 2–3 has been written to the site. Step 2 (template, index, JSON-LD partials, front-matter schema, one placeholder page) starts on the go-ahead.
