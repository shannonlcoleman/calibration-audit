"""
Convert an Open LLM Leaderboard MMLU-Pro samples file (.jsonl) into the
two-column CSV that calibration_audit.py expects (confidence, correct).

Usage:
    python mmlu_pro_to_csv.py samples_leaderboard_mmlu_pro_XXXX.jsonl output.csv

Confidence is the probability the model gave its top answer, computed by
applying softmax to its log-likelihood for each answer option.
Correct is 1 if that top answer matches the right answer, 0 if not.
"""
import csv
import json
import math
import sys


def unwrap(x):
    # Responses can be nested like [["-1.23", "False"]] or ["-1.23", "False"]
    while isinstance(x, list) and len(x) > 0 and isinstance(x[0], list):
        x = x[0]
    if isinstance(x, list):
        x = x[0]
    return float(x)


def main():
    if len(sys.argv) < 3:
        print("Usage: python mmlu_pro_to_csv.py input.jsonl output.csv")
        sys.exit(1)

    rows, skipped = [], 0
    first_error = None
    with open(sys.argv[1], encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            resps = rec.get("filtered_resps") or rec.get("resps")
            try:
                logliks = [unwrap(r) for r in resps]
            except (TypeError, ValueError, IndexError) as e:
                skipped += 1
                if first_error is None:
                    first_error = f"responses: {e} | {str(resps)[:200]}"
                continue
            top = max(logliks)
            exps = [math.exp(l - top) for l in logliks]
            total = sum(exps)
            probs = [e / total for e in exps]
            pred = probs.index(max(probs))

            # Prefer the harness's own scoring; fall back to comparing with the target
            if "acc" in rec:
                correct = int(float(rec["acc"]) >= 0.5)
            else:
                target = rec.get("target")
                try:
                    target = int(target)
                except (TypeError, ValueError):
                    t = str(target).strip().upper()
                    if len(t) == 1 and "A" <= t <= "Z":
                        target = ord(t) - ord("A")
                    else:
                        skipped += 1
                        if first_error is None:
                            first_error = f"target: {str(target)[:100]}"
                        continue
                correct = int(pred == target)
            rows.append((round(max(probs), 6), correct))

    with open(sys.argv[2], "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["confidence", "correct"])
        w.writerows(rows)

    acc = sum(c for _, c in rows) / len(rows) if rows else 0
    if first_error:
        print(f"First skipped row: {first_error}")
        if not rows:
            with open(sys.argv[1], encoding="utf-8") as f:
                rec = json.loads(f.readline())
            print("Fields in first row:", list(rec.keys()))
            for k in ("target", "filtered_resps", "resps", "acc"):
                print(f"  {k}: {str(rec.get(k))[:200]}")
    print(f"Wrote {len(rows)} rows to {sys.argv[2]} (skipped {skipped}). Accuracy: {acc:.3f}")


if __name__ == "__main__":
    main()
