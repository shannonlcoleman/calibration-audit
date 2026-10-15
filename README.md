# calibration-audit

A command-line tool that checks whether an AI model's stated confidence matches how often it's right.

I built it as a companion to [A Practical AI Evaluation Framework for Consumer Products](https://byshannoncoleman.substack.com/p/a-practical-ai-evaluation-framework), from my Substack, Ground Truth.

## Why it exists

A model that says it's 90% confident should be right about 90% of the time. Plenty of teams never check this, though. That matters because people decide how much to trust an answer based on how sure it sounds, so a model that sounds confident and isn't accurate pushes them toward the wrong call.

This tool sorts a model's outputs into ranges by confidence and compares the average confidence in each range with the share of outputs that actually were correct.

## Usage

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

On the sample data, the model is right only 55% of the time when it claims 90% to 100% confidence. The expected calibration error is 0.278, mostly overconfident.

## Background

Calibration is Layer 1 of a four-layer evaluation framework for consumer AI products. The full framework covers output quality, decision quality, trust infrastructure, and failure mode monitoring, and it's on [Ground Truth](https://byshannoncoleman.substack.com).

Built by [Shannon L. Coleman, PhD](https://shannonlcoleman.com), Principal Mixed Methods Researcher and Strategist
