---
title: Kitsune IoT Attack Trainer
emoji: ":shield:"
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# Kitsune IoT Attack Trainer

This Hugging Face Space trains classical ML intrusion-detection models from Kitsune CSV feature files.

Upload either:

- A single `.csv` file.
- A `.zip` containing Kitsune CSV feature files.

The trainer recursively loads CSVs, detects the target column, builds preprocessing for numeric and categorical columns, trains a selected sklearn model, and exports:

- `model.joblib`
- `metrics.json`
- `classification_report.csv`
- `confusion_matrix.csv`
- `metadata.json`

Use the Kitsune dataset from Kaggle, then upload the preprocessed CSV feature files here. Raw PCAP files should be converted to CSV before training.
