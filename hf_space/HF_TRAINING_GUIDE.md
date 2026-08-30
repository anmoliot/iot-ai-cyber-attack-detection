# Kitsune Hugging Face Training Setup

## What was prepared

This folder contains a Hugging Face Space focused on training models from the Kitsune dataset.

The original notebooks are not directly portable because the trainable notebooks hard-code missing local paths such as:

- `INPUT/SM/*.csv`
- `INPUT/SW/*.csv`
- `INPUT/VAL/*.csv`
- `INPUT/TEST/*.csv`
- `csvs/*.csv`

The Space wrapper accepts Kitsune CSV feature files as an upload instead.

## Chosen Dataset

Use only Kitsune:

- Source: Kaggle `ymirsky/network-attack-dataset-kitsune`
- Expected upload: CSV feature files, or a ZIP containing CSV files
- Not expected upload: raw PCAP files

The notebook family closest to Kitsune training is under:

```text
ML_IOT_PART/000-kitsune/
ML_IOT_PART/0003-Performance-Evaluation/packet/
```

However, the clean Hugging Face entrypoint is `train.py`, because it can run headlessly without notebook-specific local paths.

## Local smoke test

From this folder:

```bash
pip install -r requirements.txt
python train.py --data-dir path/to/kitsune-csv-folder --target-column Label --model random_forest
```

If your label column is named `Label`, `label`, `Class`, `class`, `Attack`, `attack`, `Category`, `category`, or `target`, you can omit `--target-column`.

## Run as a Hugging Face Space

Create a new Space using:

- SDK: `Gradio`
- App file: `app.py`
- Python requirements: `requirements.txt`

Upload the files in this folder to the Space repository.

Then open the Space, upload the Kitsune CSV or ZIP, pick a model, and click **Train**.

## Run as a Hugging Face Job

After uploading this folder to a repo or making it available in a runtime:

```bash
python train.py \
  --data-dir ./kitsune_csv \
  --target-column Label \
  --model random_forest \
  --output-dir ./outputs
```

## Kitsune Dataset Handling

Download Kitsune from Kaggle:

```text
https://www.kaggle.com/datasets/ymirsky/network-attack-dataset-kitsune
```

Kaggle downloads usually require a Kaggle account and accepted dataset terms. After downloading:

1. If you already have CSV feature files, upload them directly or zip them.
2. If you only have raw PCAP captures, preprocess them locally first using the existing `ML_IOT_PART/000-kitsune/FE` notebooks.
3. Upload the resulting CSV or ZIP to the Hugging Face Space.

The raw PCAP notebooks in `ML_IOT_PART/000-kitsune/FE` are preprocessing steps, not the Hugging Face training entrypoint.
