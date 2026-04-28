import csv
import sys
from collections import defaultdict

def load_data(filepath):
    """
    Load model outputs from a CSV file.
    Expected columns: confidence, correct
    - confidence: float between 0 and 1 (e.g. 0.85 means 85% confident)
    - correct: 1 if the model output was correct, 0 if not
    """
    rows = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            confidence = float(row["confidence"])
            correct = int(row["correct"])
            rows.append((confidence, correct))
    return rows


def assign_bucket(confidence, num_buckets=10):
    """Assign a confidence score to a bucket (e.g. 0.0-0.1, 0.1-0.2, etc.)"""
    bucket = int(confidence * num_buckets)
    if bucket == num_buckets:
        bucket = num_buckets - 1
    return bucket


def analyze_calibration(rows, num_buckets=10):
    """
    For each confidence bucket, calculate:
    - how many predictions fell in this bucket
    - what the average confidence was
    - what the actual accuracy was
    - the calibration gap (confidence minus accuracy)
    """
    buckets = defaultdict(list)
    for confidence, correct in rows:
        bucket = assign_bucket(confidence, num_buckets)
        buckets[bucket].append((confidence, correct))

    results = []
    for bucket in sorted(buckets.keys()):
        entries = buckets[bucket]
        avg_confidence = sum(c for c, _ in entries) / len(entries)
        actual_accuracy = sum(correct for _, correct in entries) / len(entries)
        gap = avg_confidence - actual_accuracy
        results.append({
            "bucket": bucket,
            "count": len(entries),
            "avg_confidence": avg_confidence,
            "actual_accuracy": actual_accuracy,
            "gap": gap
        })
    return results


def interpret_gap(gap):
    """Label the calibration gap in plain language."""
    if gap > 0.1:
        return "OVERCONFIDENT"
    elif gap < -0.1:
        return "UNDERCONFIDENT"
    else:
        return "WELL CALIBRATED"


def print_report(results):
    """Print a readable calibration report."""
    print("\n" + "=" * 65)
    print("CALIBRATION AUDIT REPORT")
    print("=" * 65)
    print(f"{'Confidence Range':<20} {'Count':<8} {'Avg Conf':<12} {'Accuracy':<12} {'Gap':<10} {'Status'}")
    print("-" * 65)

    for r in results:
        low = r["bucket"] * 0.1
        high = low + 0.1
        conf_range = f"{low:.1f} - {high:.1f}"
        status = interpret_gap(r["gap"])
        print(
            f"{conf_range:<20} {r['count']:<8} "
            f"{r['avg_confidence']:<12.3f} {r['actual_accuracy']:<12.3f} "
            f"{r['gap']:<10.3f} {status}"
        )

    print("=" * 65)

    all_gaps = [r["gap"] for r in results]
    avg_gap = sum(all_gaps) / len(all_gaps)
    overall_status = interpret_gap(avg_gap)
    print(f"\nOverall calibration gap: {avg_gap:.3f} ({overall_status})")
    print("\nInterpretation:")
    print("  Positive gap = model is more confident than it is accurate (overconfident)")
    print("  Negative gap = model is less confident than it is accurate (underconfident)")
    print("  Gap near 0   = model confidence tracks actual accuracy (well calibrated)")
    print("=" * 65 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python calibration_audit.py your_data.csv")
        sys.exit(1)

    filepath = sys.argv[1]
    print(f"Loading data from {filepath}...")
    rows = load_data(filepath)
    print(f"Loaded {len(rows)} model outputs.")
    results = analyze_calibration(rows)
    print_report(results)


if __name__ == "__main__":
    main()
