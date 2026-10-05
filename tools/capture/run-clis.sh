#!/usr/bin/env bash
# Re-runs each project's documented quick-start and writes the terminal output that
# capture.mjs renders into the ai-evidence-record, model-evidence, corpuscle and
# learned-behavior captures. Clones go under tools/capture/work/ (git-ignored); only
# the .txt transcripts in tools/capture/terminal/ are committed.
#
# Needs: git, python3 (3.10+), node (22+), network to GitHub and PyPI.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$HERE/work"
OUT="$HERE/terminal"
mkdir -p "$WORK" "$OUT"

clone() { # clone <repo> [<branch>]
  local repo="$1" branch="${2:-}"
  if [ ! -d "$WORK/$repo" ]; then
    if [ -n "$branch" ]; then git clone -q --depth 1 --branch "$branch" "https://github.com/hemangnagar/$repo.git" "$WORK/$repo"
    else git clone -q --depth 1 "https://github.com/hemangnagar/$repo.git" "$WORK/$repo"; fi
  fi
}

# One virtualenv for the Python projects.
if [ ! -x "$WORK/venv/bin/python" ]; then python3 -m venv "$WORK/venv"; fi
# shellcheck disable=SC1091
. "$WORK/venv/bin/activate"
pip install -q --upgrade pip >/dev/null

# ---------------------------------------------------------------- ai-evidence-record
# The repository's only branch is its default branch (not main/master).
clone ai-evidence-record
pip install -q -e "$WORK/ai-evidence-record" >/dev/null
( cd "$WORK/ai-evidence-record"
  {
    echo '$ aiev run-demo'; aiev run-demo
    echo '$ aiev verify';   aiev verify
    echo '$ aiev ask --record AE:AIEV-001-1042:3'; aiev ask --record AE:AIEV-001-1042:3
    echo '$ aiev tamper --seq 16 --field payload.value --set "Migraine"'; aiev tamper --seq 16 --field payload.value --set "Migraine" | grep -v -E "^\s+(before|after):"
    echo '$ aiev verify';   aiev verify || true
  } > "$OUT/ai-evidence-record.txt"
  aiev run-demo >/dev/null   # reset the ledger after the tamper
)

# ---------------------------------------------------------------- model-evidence
clone model-evidence main
( cd "$WORK/model-evidence"
  {
    echo '$ node dist/run-evidence.mjs dist/examples/bundle-v2.json dist/examples/policy-v2.json'
    node dist/run-evidence.mjs dist/examples/bundle-v2.json dist/examples/policy-v2.json
    echo "# exit $?  (0 pass · 1 fail · 2 insufficient evidence · 3 input error)"
  } > "$OUT/model-evidence.txt"
)

# ---------------------------------------------------------------- corpuscle
clone corpuscle main
pip install -q -e "$WORK/corpuscle" >/dev/null
( cd "$WORK/corpuscle"
  rm -rf keys tests/fixtures/sample_corpus/.corpuscle
  {
    echo '$ corpuscle keygen --out keys'; corpuscle keygen --out keys
    echo '$ corpuscle scan tests/fixtures/sample_corpus --corpus-id sample --version-id v1 --key keys/dev.key.pem'
    corpuscle scan tests/fixtures/sample_corpus --corpus-id sample --version-id v1 --key keys/dev.key.pem
    echo '$ corpuscle verify tests/fixtures/sample_corpus --pub keys/dev.pub.pem'
    corpuscle verify tests/fixtures/sample_corpus --pub keys/dev.pub.pem
  } > "$OUT/corpuscle.txt"
)

# ---------------------------------------------------------------- learned-behavior (from PyPI)
export LEARNED_BEHAVIOR_HOME="$WORK/learned-behavior-home"
rm -rf "$LEARNED_BEHAVIOR_HOME"; mkdir -p "$LEARNED_BEHAVIOR_HOME"
{
  echo '$ pip install learned-behavior'
  pip install --force-reinstall --no-deps learned-behavior==0.2.0 2>/dev/null | grep "Successfully installed"
  echo '$ learned-behavior init-db'
  learned-behavior init-db | sed "s|$LEARNED_BEHAVIOR_HOME|~/.local/share/learned-behavior|"
  echo '$ learned-behavior learn --workspace "$PWD" --title "Use sh, not bash, on vapor images" --rule "laravelphp/vapor has no bash; use sh -c"'
  learned-behavior learn --workspace /home/user/demo --title "Use sh, not bash, on vapor images" --rule "laravelphp/vapor has no bash; use sh -c" | sed "s|/home/user|~|"
  echo '$ learned-behavior advice --workspace "$PWD" --output claude-json   # the UserPromptSubmit hook'
  learned-behavior advice --workspace /home/user/demo --output claude-json
  echo
} > "$OUT/learned-behavior.txt"

# ---------------------------------------------------------------- clones that capture.mjs screenshots or copies from
clone edshield main            # demo/index.html (rules-only mode needs no model download)
clone edshield-evidence main   # docs/edshield-agent-loop.svg
clone retro main               # docs/retro-flow.svg
clone sanbuddy                 # Next.js app; capture.mjs starts it on a local port
( cd "$WORK/sanbuddy" && npm ci --no-audit --no-fund >/dev/null && NEXT_TELEMETRY_DISABLED=1 npx next build >/dev/null )

echo "wrote:"; ls -1 "$OUT"
