# calibration-audit

A command-line tool that checks whether an AI model's stated confidence matches how often it's right.

I built it as a companion to [A Practical AI Evaluation Framework for Consumer Products](https://byshannoncoleman.substack.com/p/a-practical-ai-evaluation-framework), from my Substack, Ground Truth.

## Why it exists

A model that says it's 90% confident should be right about 90% of the time. Plenty of teams never check this, though. That matters because people decide how much to trust an answer based on how sure it sounds, so a model that sounds confident and isn't accurate pushes them toward the wrong call.

This tool sorts a model's outputs into ranges by confidence and compares the average confidence in each range with the share of outputs that actually were correct.

## Usage

Requires Python 3. No other packages needed.

```
python calibration_audit.py your_data.csv
```

The CSV needs two columns:

- `confidence`: the model's stated confidence, from 0 to 1
- `correct`: 1 if the output was right, 0 if it wasn't

`sample_data.csv` is included if you want to try it first.

## What you get

For each confidence range (0.0 to 0.1, 0.1 to 0.2, and so on), the report shows:

- how many outputs fell in that range
- their average confidence
- how many of them were correct
- the gap between the two
- a label: OVERCONFIDENT, UNDERCONFIDENT, or WELL CALIBRATED (a gap within 0.1)

Below the table, it gives two summary numbers:

- **Expected calibration error.** The average size of the gap, weighted by how many outputs are in each range. Gaps in either direction count, so an overconfident range can't hide behind an underconfident one.
- **Weighted average gap.** Which direction the model leans. Positive means overconfident, and negative means underconfident.

It also flags ranges with fewer than five outputs, since one or two answers can swing their accuracy a lot.

## Example output

```
Confidence Range     Count    Avg Conf     Accuracy     Gap        Status
-----------------------------------------------------------------
0.0 - 0.1            1        0.050        0.000        0.050      WELL CALIBRATED
0.1 - 0.2            2        0.125        0.500        -0.375     UNDERCONFIDENT
0.2 - 0.3            2        0.225        0.500        -0.275     UNDERCONFIDENT
0.3 - 0.4            3        0.343        0.667        -0.323     UNDERCONFIDENT
0.4 - 0.5            2        0.425        0.500        -0.075     WELL CALIBRATED
0.5 - 0.6            2        0.525        0.500        0.025      WELL CALIBRATED
0.6 - 0.7            3        0.643        0.333        0.310      OVERCONFIDENT
0.7 - 0.8            4        0.738        0.500        0.238      OVERCONFIDENT
0.8 - 0.9            10       0.857        0.600        0.257      OVERCONFIDENT
0.9 - 1.0            11       0.923        0.545        0.377      OVERCONFIDENT

Expected calibration error: 0.278 (MISCALIBRATED, MOSTLY OVERCONFIDENT)
Weighted average gap: +0.157
Note: 8 range(s) have fewer than 5 outputs, so treat their status as rough.
```

On the sample data, the model is right only 55% of the time when it claims 90% to 100% confidence. The expected calibration error is 0.278, mostly overconfident.

## Real-data example: base vs. instruction-tuned model

I ran the audit on Qwen2.5-7B and Qwen2.5-7B-Instruct, using each model's per-question MMLU-Pro results from the [Open LLM Leaderboard](https://huggingface.co/open-llm-leaderboard) (12,032 questions per model). `mmlu_pro_to_csv.py` converts those results into the two columns this tool reads. The model gives each answer option a probability, and its level of confidence is the probability of the answer it chose.

| | Base | Instruct |
|---|---|---|
| Accuracy | 43.7% | 42.9% |
| Expected calibration error | 0.061 | 0.454 |
| Answers at 90%+ confidence | 1,442 (93% correct) | 7,921 (53% correct) |

The two models are about equally accurate, yet instruction tuning made the model far more confident without making it right more often. When the base model claims 90% or higher, it's right 93% of the time. When the instruct model does, it's right about half the time.

A few limits: this covers one model family and one benchmark, and confidence here is the model's probability over the answer options, not a confidence it states in words. Post-training has been reported to hurt calibration before, so this is an independent check of a known effect.

To reproduce:

```
python mmlu_pro_to_csv.py samples_leaderboard_mmlu_pro_<timestamp>.jsonl qwen_base.csv
python calibration_audit.py qwen_base.csv
```

## Background

Calibration is Layer 1 of a four-layer evaluation framework for consumer AI products. The full framework covers output quality, decision quality, trust infrastructure, and failure mode monitoring, and it's on [Ground Truth](https://byshannoncoleman.substack.com).

Built by [Shannon L. Coleman, PhD](https://shannonlcoleman.com), Principal Mixed Methods Researcher and Strategist

## License

MIT. See LICENSE.
