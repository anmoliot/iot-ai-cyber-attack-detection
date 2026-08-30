from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import gradio as gr

from train import TrainConfig, prepare_upload, train


MODELS = [
    "random_forest",
    "extra_trees",
    "decision_tree",
    "svm",
    "mlp",
    "knn",
    "logistic_regression",
]


def zip_outputs(output_dir: Path) -> Path:
    archive_path = output_dir.parent / "training_outputs.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in output_dir.rglob("*"):
            if path.is_file():
                archive.write(path, path.relative_to(output_dir))
    return archive_path


def run_training(
    upload_file,
    target_column: str,
    model: str,
    max_rows_per_file: int,
    max_total_rows: int,
    test_size: float,
):
    if upload_file is None:
        raise gr.Error("Upload a CSV file or a ZIP containing CSV files.")

    target_column = target_column.strip() or None
    upload_path = Path(upload_file.name)

    prepared = None
    job_temp = tempfile.TemporaryDirectory()
    try:
        prepared, data_dir = prepare_upload(upload_path)
        output_dir = Path(job_temp.name) / "outputs"
        metrics = train(
            TrainConfig(
                data_dir=str(data_dir),
                output_dir=str(output_dir),
                target_column=target_column,
                model=model,
                max_rows_per_file=max_rows_per_file,
                max_total_rows=max_total_rows,
                test_size=test_size,
            )
        )
        archive = zip_outputs(output_dir)
        metrics_text = json.dumps(metrics, indent=2)
        copied_archive = Path(job_temp.name) / "download_training_outputs.zip"
        shutil.copy2(archive, copied_archive)
        return metrics_text, str(copied_archive)
    finally:
        if prepared is not None:
            prepared.cleanup()


with gr.Blocks(title="Kitsune IoT Attack Trainer") as demo:
    gr.Markdown("# Kitsune IoT Attack Trainer")
    gr.Markdown(
        "Upload Kitsune CSV feature files, or a ZIP containing those CSVs. "
        "Use the Kitsune Kaggle dataset and convert raw PCAP captures to CSV before training."
    )

    with gr.Row():
        upload = gr.File(label="Kitsune CSV or ZIP of CSV files", file_types=[".csv", ".zip"])
        with gr.Column():
            target = gr.Textbox(label="Target column", placeholder="Leave blank to auto-detect Label/class/target")
            model = gr.Dropdown(MODELS, value="random_forest", label="Model")
            max_rows_per_file = gr.Number(value=100000, precision=0, label="Max rows per file")
            max_total_rows = gr.Number(value=500000, precision=0, label="Max total rows")
            test_size = gr.Slider(0.05, 0.4, value=0.2, step=0.05, label="Test split")
            train_button = gr.Button("Train")

    metrics = gr.Code(label="Metrics", language="json")
    download = gr.File(label="Model and reports")

    train_button.click(
        run_training,
        inputs=[upload, target, model, max_rows_per_file, max_total_rows, test_size],
        outputs=[metrics, download],
    )


if __name__ == "__main__":
    demo.launch()
