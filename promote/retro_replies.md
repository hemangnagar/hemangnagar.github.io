# /retro — reply targets (sweep of 2026-09-09)

BLOCKER: github.com/hemangnagar/retro was PRIVATE at sweep time. Flip to public
(Settings → General → Danger Zone → Change visibility) before posting any link.

Order: do 1, 2, 6 first (filed in the last 24h, ~zero replies). Then one or two a day.
GitHub comments outrank tweets for reach here. Reply to responders within the hour.

## 1. anthropics/claude-code #92998 — cap silently drops the NEWEST entries (filed today)
https://github.com/anthropics/claude-code/issues/92998
Agree the failure mode at the cap is the defect, not the cap. What fixed it for me was changing *what* eviction is keyed on: not age or append order, but strength — each line carries a confidence and a hit counter (how often it actually fired), and a new lesson has to beat the weakest incumbent to get in. Corrections then displace the thing they corrected instead of losing to it. I run it as a milestone ritual rather than at write time so the judgment happens when there's evidence: github.com/hemangnagar/retro (playbook.py is the ~80 lines that do the displacement).

## 2. #90322 — opt-in global memory across projects (0 comments)
https://github.com/anthropics/claude-code/issues/90322
This is roughly what I settled on, minus the hand-maintenance: `~/.claude/CLAUDE.md` `@`-imports a `~/.retro/playbook.md`, so it loads in every project, and the file is capped at 25 lines so the cost of always-loading it stays trivial. The part that made it work was scoping: each lesson is tagged project / stack / global at a retrospective, and only stack + global ever reach the shared file. Tooling if useful: github.com/hemangnagar/retro.

## 3. #39195 — share memory across a SUBSET of projects (12 upvotes)
https://github.com/anthropics/claude-code/issues/39195
The subset case is the one a two-tier model can't express — I ended up with three scopes: `project` (stays in the repo), `stack:<name>` (shared by every repo on that tooling, e.g. `stack:git`, `stack:python`), and `global`. The stack tier is exactly the "some projects, not all" layer this issue describes, and it's cheap because the shared file is size-capped. Implementation as a /retro skill + file convention: github.com/hemangnagar/retro.

## 4. #83114 — 1,200+ memory files, curation mid-task, asks for hit-count eviction
https://github.com/anthropics/claude-code/issues/83114
Your ask #4 (usage telemetry driving eviction) and "curation off the critical path" are the two design decisions that fixed this for me: curation only runs at milestones (tag / merge / wrap-up), never mid-task, and every retained line carries a hit counter that protects it from displacement. It's deliberately a ritual, not a hook. github.com/hemangnagar/retro if you want to steal the eviction rule.

## 5. #83831 — cross-project memory; @import "pays token cost every session"
https://github.com/anthropics/claude-code/issues/83831
The token-cost objection is what the cap solves: a 25-line playbook is ~600 tokens, cheap enough to load everywhere, and it stays 25 lines because a new lesson must displace a weaker one. Rarely-needed knowledge fails that test and stays project-scoped. github.com/hemangnagar/retro

## 6. #92980 — user-level CLAUDE.md is 179k chars (filed today)
https://github.com/anthropics/claude-code/issues/92980
Beyond the limit itself: at 179k chars the file is past the point where the model weighs any single line. What worked for me was inverting it — the global file holds only a small scored playbook (capped at 25 lines, each with evidence and a hit count), and everything else moves to per-project CLAUDE.md or skills. The hard part isn't cutting once; it's having a rule for what gets in afterwards. github.com/hemangnagar/retro

## 7. X — @aarthir: "lessons sitting in the wrong place"
https://x.com/aarthir/status/2071248657991520474
The wrong-place problem is a scoping problem, and it needs a menu, not a purge: for each lesson — this repo, this stack, or how I work? Only the last two cross projects. I made it a milestone ritual with a 25-line cap so the purge never has to happen again: github.com/hemangnagar/retro

## 8. X — @mvanhorn article "Your AI's Memory Is Quietly Making It Dumber"
https://x.com/mvanhorn/article/2070966613994795489
"Enforced scarcity is the mechanism" is the whole thing. I turned your one-off audit into a repeatable ritual: retro at each milestone, every lesson scoped project/stack/global/discard, cross-project file capped at 25 lines with displacement by confidence + hits. Two repos in, it's found 3 bugs in itself. github.com/hemangnagar/retro

## 9. X — @weaviate_io: "memory systems accumulate, don't organise" (+ April post: Claude ignored Engram for MEMORY.md)
https://x.com/weaviate_io/status/2064703135902216618
https://x.com/weaviate_io/status/2039727522498093471
Your April finding is the interesting one: the always-loaded file wins on latency, so the real problem is keeping *that* file bounded and reconciled. That's a curation problem, not a retrieval one — I went the other way from Engram: sort at write time with a 25-line cap and a human gate, at milestones. github.com/hemangnagar/retro

## 10. Gist — ChristopherA "Self-Improving Claude Code" (active this week)
https://gist.github.com/ChristopherA/fd2985551e765a86f4fbb24080263a2f
The piece I was missing with a setup like this was promotion: which of the 30 learnings should follow me to the next repo? I added a scope step (project/stack/global/discard) and a separate 25-line cross-project playbook with displacement. Complements this nicely rather than replacing it: github.com/hemangnagar/retro

## Secondary (comment if time)
- #85075 stale memory silently loads — retro lines carry added: dates + hits. https://github.com/anthropics/claude-code/issues/85075
- #91188 compaction deletes load-bearing content to hit a number (50 comments). https://github.com/anthropics/claude-code/issues/91188
- #79217 make the cap configurable — contrarian: the cap is the feature; the missing piece is the eviction rule. https://github.com/anthropics/claude-code/issues/79217
- coleam00/claude-memory-compiler #26 per-project vs per-install (1.3k-star tool). https://github.com/coleam00/claude-memory-compiler/issues/26
- netresearch/retro-skill — adjacent project, active today; comparison/collab comment. https://github.com/netresearch/retro-skill
- @kunchenguid "disable auto memory" https://x.com/kunchenguid/status/2067728608584675465 — the alternative to off is small + curated.
- @PrajjwalYd "two versions of the same fact still arguing" https://x.com/PrajjwalYd/status/2072291317695324410 — displacement is the dedupe step.
- dev.to/amitaile post-mortem workflow (same idea minus scoping + cap) https://dev.to/amitaile/using-claude-code-to-post-mortem-its-own-mistakes-3ned
- lisn0/learned-behavior — open the --output json PR (docs/upstream in the retro repo).

Not reachable from the sandbox: Reddit (browse r/ClaudeAI for "CLAUDE.md" threads by hand), LinkedIn engagement counts.
