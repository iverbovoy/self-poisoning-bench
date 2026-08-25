#!/usr/bin/env bash
# SPB free-tier reproduction: regenerate everything downstream of the
# stored model outputs and assert it is byte-identical to the tree.
# No API calls. Exit 1 on any difference.
set -euo pipefail
cd "$(dirname "$0")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
fail=0

echo "== corpora (generator is deterministic)"
cp -r corpus "$TMP/corpus"; cp -r corpus-b "$TMP/corpus-b"
cp -r corpus-en "$TMP/corpus-en"; cp -r corpus-b-en "$TMP/corpus-b-en"
python3 gen_corpus.py --storyline a >/dev/null
python3 gen_corpus.py --storyline b >/dev/null
python3 gen_corpus.py --storyline en >/dev/null
python3 gen_corpus.py --storyline ben >/dev/null
diff -r "$TMP/corpus" corpus   && echo "   corpus    identical" || fail=1
diff -r "$TMP/corpus-b" corpus-b && echo "   corpus-b  identical" || fail=1
diff -r "$TMP/corpus-en" corpus-en && echo "   corpus-en identical" || fail=1
diff -r "$TMP/corpus-b-en" corpus-b-en && echo "   corpus-b-en identical" || fail=1

echo "== verdicts from stored judgments (both rubrics)"
mkdir -p "$TMP/v"
for d in runs/*/; do
  c=$(basename "$d")
  for f in verdicts.csv verdicts-v11.csv; do
    [ -f "$d/$f" ] && cp "$d/$f" "$TMP/v/$c.$f"
  done
done
python3 judge.py --summarize --rubric v10 >/dev/null
python3 judge.py --summarize --rubric v11 >/dev/null
n=0
for f in "$TMP"/v/*; do
  b=$(basename "$f"); c=${b%%.*}; name=${b#*.}
  if ! diff -q "$f" "runs/$c/$name" >/dev/null; then echo "   DIFF runs/$c/$name"; fail=1; fi
  n=$((n+1))
done
echo "   $n verdict files checked"

echo "== summary tables"
cp runs/summary-v10.csv "$TMP/s10"; cp runs/summary-v11.csv "$TMP/s11"
python3 curve.py --rubric v10 >/dev/null; python3 curve.py --rubric v11 >/dev/null
diff -q "$TMP/s10" runs/summary-v10.csv >/dev/null && echo "   summary-v10 identical" || { echo "   DIFF summary-v10"; fail=1; }
diff -q "$TMP/s11" runs/summary-v11.csv >/dev/null && echo "   summary-v11 identical" || { echo "   DIFF summary-v11"; fail=1; }

echo "== adjudication score (re-derived from human.csv)"
cp adjudication/scored.csv "$TMP/scored"
python3 adjudicate.py --score | grep -E "^all|laundered by"
diff -q "$TMP/scored" adjudication/scored.csv >/dev/null && echo "   scored.csv identical" || { echo "   DIFF scored.csv"; fail=1; }

echo "== replicates"
python3 replicates.py | grep -E "^==|laundered"

echo "== EN adjudication, LLM seat (re-derived from human-fable5.csv)"
cp adjudication-en/scored-fable5.csv "$TMP/scored-en"
python3 adjudicate.py --corpus en --tag fable5 --score | grep -E "^all|laundered by"
diff -q "$TMP/scored-en" adjudication-en/scored-fable5.csv >/dev/null && echo "   scored-fable5.csv identical" || { echo "   DIFF scored-fable5.csv"; fail=1; }

echo "== SuperRed report (re-derived from per-run traces)"
cp superred/results/REPORT.md "$TMP/REPORT.md"
python3 superred/report.py >/dev/null
diff -q "$TMP/REPORT.md" superred/results/REPORT.md >/dev/null && echo "   REPORT.md identical" || { echo "   DIFF REPORT.md"; fail=1; }

echo "== Section 6 inference statistics (stats.py, seed 0)"
cp runs/stats-en-a.txt "$TMP/sa"; cp runs/stats-en-b.txt "$TMP/sb"
python3 stats.py > runs/stats-en-a.txt
python3 stats.py --prefix ben- --corpus corpus-b-en > runs/stats-en-b.txt
diff -q "$TMP/sa" runs/stats-en-a.txt >/dev/null && echo "   stats-en-a identical" || { echo "   DIFF stats-en-a"; fail=1; }
diff -q "$TMP/sb" runs/stats-en-b.txt >/dev/null && echo "   stats-en-b identical" || { echo "   DIFF stats-en-b"; fail=1; }

echo "== Proposition model check (formal_check.py)"
python3 formal_check.py | grep -q "unreachable under I1+I2+I2'+I4" && echo "   holds (counterexample per dropped invariant)" || { echo "   FAIL formal_check"; fail=1; }

echo "== utility grid summary (re-derived from stored answers+judgments)"
cp superred/results/utility/summary.csv "$TMP/us"
python3 superred/utility.py --summarize >/dev/null
diff -q "$TMP/us" superred/results/utility/summary.csv >/dev/null && echo "   utility summary identical" || { echo "   DIFF utility summary"; fail=1; }

echo "== directive-parser eval (re-scored from stored answers)"
cp runs/directive-eval/summary.csv "$TMP/ds"
python3 directive_eval.py >/dev/null
diff -q "$TMP/ds" runs/directive-eval/summary.csv >/dev/null && echo "   directive summary identical" || { echo "   DIFF directive summary"; fail=1; }

if [ $fail -eq 0 ]; then echo "OK: everything regenerates identically"; else echo "FAIL: see DIFF lines"; exit 1; fi
