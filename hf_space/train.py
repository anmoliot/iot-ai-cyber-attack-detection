from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


DEFAULT_TARGET_CANDIDATES = (
    "Label",
    "label",
    "Class",
    "class",
    "Attack",
    "attack",
    "Category",
    "category",
    "target",
)


@dataclass
class TrainConfig:
    data_dir: str
    output_dir: str = "outputs"
    target_column: str | None = None
    model: str = "random_forest"
    test_size: float = 0.2
    random_state: int = 42
    max_rows_per_file: int | None = 100_000
    max_total_rows: int | None = 500_000


def find_csv_files(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.rglob("*.csv") if path.is_file())


def read_csv_sample(path: Path, max_rows: int | None) -> pd.DataFrame:
    try:
        return pd.read_csv(path, nrows=max_rows, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, nrows=max_rows, low_memory=False, encoding="latin1")


def load_dataset(data_dir: Path, max_rows_per_file: int | None, max_total_rows: int | None) -> pd.DataFrame:
    csv_files = find_csv_files(data_dir)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found under {data_dir}")

    frames: list[pd.DataFrame] = []
    remaining = max_total_rows

    for csv_file in csv_files:
        per_file_limit = max_rows_per_file
        if remaining is not None:
            if remaining <= 0:
                break
            per_file_limit = min(per_file_limit or remaining, remaining)

        frame = read_csv_sample(csv_file, per_file_limit)
        if frame.empty:
            continue

        frame["__source_file"] = str(csv_file.relative_to(data_dir))
        frames.append(frame)

        if remaining is not None:
            remaining -= len(frame)

    if not frames:
        raise ValueError("CSV files were found, but all loaded frames were empty.")

    return pd.concat(frames, ignore_index=True, sort=False)


def detect_target_column(df: pd.DataFrame, configured: str | None) -> str:
    if configured:
        if configured not in df.columns:
            raise ValueError(f"Target column '{configured}' was not found. Available columns: {list(df.columns)}")
        return configured

    for candidate in DEFAULT_TARGET_CANDIDATES:
        if candidate in df.columns:
            return candidate

    raise ValueError(
        "Could not infer target column. Pass --target-column. "
        f"Tried: {', '.join(DEFAULT_TARGET_CANDIDATES)}"
    )


def make_model(name: str, random_state: int):
    models = {
        "random_forest": RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=300,
            class_weight="balanced",
            n_jobs=-1,
            random_state=random_state,
        ),
        "decision_tree": DecisionTreeClassifier(class_weight="balanced", random_state=random_state),
        "svm": SVC(class_weight="balanced", probability=True, random_state=random_state),
        "mlp": MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=300, random_state=random_state),
        "knn": KNeighborsClassifier(n_neighbors=5),
        "logistic_regression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            n_jobs=-1,
            random_state=random_state,
        ),
    }
    if name not in models:
        raise ValueError(f"Unknown model '{name}'. Choose one of: {', '.join(models)}")
    return models[name]


def build_pipeline(df: pd.DataFrame, target_column: str, model_name: str, random_state: int) -> Pipeline:
    feature_df = df.drop(columns=[target_column])
    numeric_features = feature_df.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = [col for col in feature_df.columns if col not in numeric_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", make_model(model_name, random_state)),
        ]
    )


def normalize_target(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "None": np.nan})


def train(config: TrainConfig) -> dict:
    data_dir = Path(config.data_dir)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_dataset(data_dir, config.max_rows_per_file, config.max_total_rows)
    target_column = detect_target_column(df, config.target_column)

    df[target_column] = normalize_target(df[target_column])
    df = df.dropna(subset=[target_column])
    df = df.dropna(axis=1, how="all")

    if df[target_column].nunique() < 2:
        raise ValueError(f"Target column '{target_column}' must contain at least two classes.")

    y = df[target_column]
    X = df.drop(columns=[target_column])

    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=stratify,
    )

    train_df = X_train.copy()
    train_df[target_column] = y_train
    pipeline = build_pipeline(train_df, target_column, config.model, config.random_state)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    labels = sorted(y.unique().tolist())
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    metrics = {
        "model": config.model,
        "target_column": target_column,
        "rows_loaded": int(len(df)),
        "features": int(X.shape[1]),
        "classes": labels,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "macro_f1": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
    }

    joblib.dump(pipeline, output_dir / "model.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (output_dir / "metadata.json").write_text(
        json.dumps(
            {
                "config": asdict(config),
                "csv_files": [str(path.relative_to(data_dir)) for path in find_csv_files(data_dir)],
                "feature_columns": X.columns.tolist(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    pd.DataFrame(report).transpose().to_csv(output_dir / "classification_report.csv")
    pd.DataFrame(cm, index=labels, columns=labels).to_csv(output_dir / "confusion_matrix.csv")

    return metrics


def extract_zip(zip_path: Path, destination: Path) -> Path:
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(destination)
    return destination


def prepare_upload(upload_path: Path) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp_dir = tempfile.TemporaryDirectory()
    root = Path(temp_dir.name)
    if upload_path.suffix.lower() == ".zip":
        data_dir = extract_zip(upload_path, root / "data")
    else:
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(upload_path, data_dir / upload_path.name)
    return temp_dir, data_dir


def parse_args(argv: Iterable[str] | None = None) -> TrainConfig:
    parser = argparse.ArgumentParser(description="Train IoT cyber attack classifier from CSV feature files.")
    parser.add_argument("--data-dir", required=True, help="Folder containing CSV files.")
    parser.add_argument("--output-dir", default="outputs", help="Folder for model and metrics.")
    parser.add_argument("--target-column", default=None, help="Target label column. Auto-detected if omitted.")
    parser.add_argument(
        "--model",
        default="random_forest",
        choices=[
            "random_forest",
            "extra_trees",
            "decision_tree",
            "svm",
            "mlp",
            "knn",
            "logistic_regression",
        ],
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-rows-per-file", type=int, default=100_000)
    parser.add_argument("--max-total-rows", type=int, default=500_000)
    args = parser.parse_args(argv)
    return TrainConfig(**vars(args))


if __name__ == "__main__":
    result = train(parse_args())
    print(json.dumps(result, indent=2))
