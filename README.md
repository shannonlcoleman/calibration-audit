# calibration-audit

A command-line tool for measuring confidence calibration in AI model outputs.

Built as a companion to [A Practical AI Evaluation Framework for Consumer Products](https://byshannoncoleman.substack.com/p/a-practical-ai-evaluation-framework), published in Ground Truth.

---

## The problem this solves

Most AI product teams never check whether their model's expressed confidence actually correlates with its accuracy. A model that presents itself as 90% confident should be right around 90% of the time. Most are not. This is calibration failure, and it is one of the most consequential gaps in consumer AI evaluation because users adjust their trust and behavior based on how confident the model appears.

This tool takes a CSV of model outputs with confidence scores and ground truth labels, buckets them by confidence range, and shows you exactly where the model is overconfident, underconfident, or well calibrated.

---

## Usage
python calibration_audit.py your_data.csv

Your CSV file needs two columns:

- `confidence`: a float between 0 and 1 representing the model's expressed confidence
- `correct`: 1 if the output was correct, 0 if not

A sample data file is included to test the tool.

---

## Output

The tool prints a calibration report showing for each confidence bucket:

- how many predictions fell in that range
- the average confidence score
- the actual accuracy rate
- the gap between confidence and accuracy
- a plain language status: OVERCONFIDENT, UNDERCONFIDENT, or WELL CALIBRATED

---

## Background

Calibration is Layer 1 of a four-layer evaluation framework for consumer AI products. The full framework covers output quality, decision quality, trust infrastructure, and failure mode monitoring.

Full framework: [byshannoncoleman.substack.com](https://byshannoncoleman.substack.com)

---

Built by [Shannon Coleman, PhD](https://shannonlcoleman.com) | Experience Research and Strategy Leader