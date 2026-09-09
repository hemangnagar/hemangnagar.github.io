# r/ClaudeAI (also fits r/ClaudeCode) — text post. Link goes at the BOTTOM, not the top.
# Flair: Coding / Productivity. Post in the morning US time; reply to every comment in the first 2 hours.

## Title

My global CLAUDE.md hit ~300 lines and Claude quietly stopped following it. So I built a retrospective ritual that caps it at 25 lines — and makes lessons compete for the slots.

## Body

Every AI-coding setup I've seen has the same problem: memory files with no writer. CLAUDE.md, skills, STATE.md — they're storage. Nothing ever asks *"what did this project teach us that the next one should inherit?"*, and nothing ever removes the rules that stopped earning their place. So the global file grows, and at some point the model treats it as background noise.

I built a `/retro` skill for Claude Code that runs at milestones (tag, merge to main, archive) instead of every session. It's small — stdlib Python, two markdown files — but three rules do all the work:

**1. A fixed interview, drafted from evidence.** Four questions, same every time: what was the goal and did it change; what took longer than expected; what did we get wrong first; which recurring failures had a real cause. Claude drafts the answers from git history, session transcripts, and learned-behavior's observations. I reply `agree` / `edit` / `skip`. Takes a couple of minutes.

**2. Every lesson is scoped from a closed menu:** `project | stack | global | discard`. Project lessons stay with the repo. Only `stack` and `global` cross projects. That one rule is what stops the global file from filling up with project trivia.

**3. The cross-project playbook is capped at 25 lines** and loaded into every session. A new lesson has to displace a weaker one (confidence + how often it proved useful) or it's rejected. Rejection is a designed outcome — it's the damper that keeps "self-improvement" from compounding noise.

Dogfooding so far: two retros. The tool found three real bugs in itself (shallow-clone `HEAD~N`, hosted git refusing tag pushes, Claude Code's transcript path encoding), and produced six lessons I would genuinely have written down — things like "verify a sandbox's egress policy before polling a URL; a blocked domain 403s forever and looks exactly like 'still deploying'."

The contrast I keep thinking about: continuous memory systems (mem0, Weaviate's Engram) capture every task and sort at *read* time via search. This sorts at *write* time via a budget. I don't know yet which bet is right — that's what the next month of running it on real repos is for.

Honest question for people here: how do you carry lessons between repos today? Hand-edit the global CLAUDE.md? Not at all?

Repo (MIT): https://github.com/hemangnagar/retro

## Reply drafts for likely comments

- **"Why not just use memory / mem0 / Engram?"** → Those are great at capture. My problem was the opposite: too much captured, nothing curated. The cap forces the curation. If you already have a small, well-pruned CLAUDE.md, you don't need this.
- **"25 is arbitrary."** → It is. It's the number where I still read every line. Change `MAX_LESSONS` in playbook.py; the point is that there *is* a number.
- **"This is just a checklist."** → The interview is. The scope menu and the eviction rule are the part a checklist doesn't do — nothing in a checklist removes last quarter's rule.
