# Reddit — r/ClaudeAI first (best fit), r/artificial a few days later. Text post, link inside.
# Reddit punishes self-promotion tone; this is written as "here is what I found", not "here is my project".

**Title:** I ran Claude Opus 5 as both builder and adversary on four real decisions and let a fixed rule pick ACT/WAIT/ABANDON. The adversary never once rated an objection non-blocking.

I built a small open-source tool (Decision Gate) where two model calls argue about a decision and a deterministic rule decides the action. Builder states the claims the decision rests on. Adversary attacks each claim and rates it FATAL / BLOCKING / MATERIAL / NON_BLOCKING with a `resolves_if`. Then: any unresolved FATAL → ABANDON, else any BLOCKING → WAIT, else ACT. The models never touch the gate.

I ran it on four decisions with Claude Opus 5 in both roles, three-round limit, no context beyond the question:

- Hospital replaces pagers with a messaging app in 12 months → **ABANDON**. One FATAL: pagers are the out-of-band channel, the app can't be its own fallback. Counterfactual: resolve it and the gate still says WAIT.
- Migrate nightly Spark (2 TB/day) to DuckDB on one big machine → **WAIT**, 9 BLOCKING (single-writer model, un-optimised Spark baseline, shared-tenant cost that doesn't disappear).
- Mid-size city pilots congestion pricing for 18 months → **WAIT**, 13 BLOCKING (federal-aid tolling rules, anti-diversion clauses, parking price already dominates the toll).
- Two-location bakery opens a third before hiring a GM → **WAIT**, 12 BLOCKING.

What I found interesting, and what I'd like opinions on:

1. **The stop rule never fired.** The review is supposed to end when a round adds nothing consequential. All four ran to the round limit. Opus never ran out of objections.
2. **Zero NON_BLOCKING across 92 challenges.** 1 FATAL, 44 BLOCKING, 47 MATERIAL. It used the top three rungs of a four-rung scale. Since the gate reads only those ratings, WAIT is nearly guaranteed from unedited output. Is this a prompt problem, a model habit, or is a critic just always going to inflate severity?
3. **Quality was very high.** Statute citations, concrete failure mechanisms, tensions between pairs of claims ("a rerun fits in the window" and "I/O fits in the window" can't both be comfortably true), and later rounds extended earlier challenges rather than repeating them.

The ledgers are unedited JSON in the repo and `decision-gate gate file.json` recomputes the action without a model call, so anyone can check them. Write-up with screenshots: https://hemangnagar.dev/decision-gate/ Code: https://github.com/hemangnagar/decision_gate

Would a second model that *only* re-rates severity fix (2), or just move the problem?
