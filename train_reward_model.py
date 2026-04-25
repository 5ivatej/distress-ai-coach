"""Train a future-oriented reward model with LoRA/QLoRA for Colab T4."""
from __future__ import annotations

import argparse
import inspect
import json
import math
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Sequence

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt
import torch
from accelerate import Accelerator
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments,
)

from src.training_utils import RewardSample, collect_reward_dataset

TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

_unwrap_signature = inspect.signature(Accelerator.unwrap_model)
if "keep_torch_compile" not in _unwrap_signature.parameters:
    _orig_unwrap_model = Accelerator.unwrap_model

    def _compat_unwrap_model(self, model, *args, keep_torch_compile=None, **kwargs):
        del keep_torch_compile
        return _orig_unwrap_model(self, model, *args, **kwargs)

    Accelerator.unwrap_model = _compat_unwrap_model


def str2bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return value.lower() in {"1", "true", "yes", "y", "on"}


def _preferred_dtype():
    if not torch.cuda.is_available():
        return torch.float32
    major, _minor = torch.cuda.get_device_capability()
    return torch.bfloat16 if major >= 8 else torch.float16


def build_quantization_config(use_4bit: bool):
    if not use_4bit or not torch.cuda.is_available():
        return None
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=_preferred_dtype(),
    )


def split_samples(samples: Sequence[Any], eval_ratio: float = 0.2) -> tuple[List[Any], List[Any]]:
    if not samples:
        return [], []
    split_idx = max(1, math.floor(len(samples) * (1.0 - eval_ratio)))
    return list(samples[:split_idx]), list(samples[split_idx:])


def dataset_from_samples(samples: Sequence[RewardSample]) -> Dataset:
    return Dataset.from_list([
        {"text": sample.text, "labels": float(sample.future_oriented)}
        for sample in samples
    ])


def tokenize_dataset(dataset: Dataset, tokenizer, max_length: int) -> Dataset:
    def _tokenize(batch: Dict[str, List[Any]]) -> Dict[str, Any]:
        encoded = tokenizer(
            batch["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
        encoded["labels"] = [float(label) for label in batch["labels"]]
        return encoded

    tokenized = dataset.map(_tokenize, batched=True, remove_columns=["text"])
    tokenized.set_format(type="torch")
    return tokenized


def build_model_and_tokenizer(
    model_name: str,
    use_4bit: bool,
    lora_r: int,
    lora_alpha: int,
    lora_dropout: float,
):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = build_quantization_config(use_4bit)
    model_kwargs = {
        "num_labels": 1,
        "problem_type": "regression",
        "low_cpu_mem_usage": True,
    }
    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["device_map"] = "auto"
    elif torch.cuda.is_available():
        model_kwargs["torch_dtype"] = _preferred_dtype()

    model = AutoModelForSequenceClassification.from_pretrained(model_name, **model_kwargs)
    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.use_cache = False

    if quantization_config is not None:
        model = prepare_model_for_kbit_training(model)
    model.gradient_checkpointing_enable()

    peft_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        bias="none",
        target_modules=TARGET_MODULES,
        modules_to_save=["score"],
    )
    model = get_peft_model(model, peft_config)
    if hasattr(model, "print_trainable_parameters"):
        model.print_trainable_parameters()
    return model, tokenizer, ("qlora" if quantization_config is not None else "lora")


def save_loss_plot(log_history: Sequence[Dict[str, Any]], output_path: Path) -> None:
    losses = [(entry.get("step"), entry.get("loss")) for entry in log_history if "loss" in entry and "step" in entry]
    if not losses:
        return
    xs = [step for step, _ in losses]
    ys = [loss for _, loss in losses]
    plt.figure(figsize=(7, 4))
    plt.plot(xs, ys, marker="o")
    plt.xlabel("training step")
    plt.ylabel("loss")
    plt.title("Reward Model Training Loss")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def save_prediction_plot(labels: Sequence[float], predictions: Sequence[float], output_path: Path) -> None:
    if not labels or not predictions:
        return
    xs = list(range(len(labels)))
    plt.figure(figsize=(8, 4))
    plt.plot(xs, labels, marker="o", label="env future_oriented")
    plt.plot(xs, predictions, marker="x", label="reward model")
    plt.xlabel("sample index")
    plt.ylabel("score")
    plt.title("Reward Model vs Environment Labels")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def train_model(
    model_name: str,
    output_dir: str,
    train_dataset: Dataset,
    eval_dataset: Dataset,
    max_length: int,
    epochs: float,
    batch_size: int,
    gradient_accumulation_steps: int,
    use_4bit: bool,
    lora_r: int,
    lora_alpha: int,
    lora_dropout: float,
):
    model, tokenizer, backend = build_model_and_tokenizer(
        model_name=model_name,
        use_4bit=use_4bit,
        lora_r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
    )
    tokenized_train = tokenize_dataset(train_dataset, tokenizer, max_length=max_length)
    tokenized_eval = tokenize_dataset(eval_dataset, tokenizer, max_length=max_length)

    args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        num_train_epochs=epochs,
        logging_steps=1,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        report_to=[],
        learning_rate=2e-4,
        remove_unused_columns=False,
        fp16=torch.cuda.is_available(),
        bf16=False,
        gradient_checkpointing=True,
        optim="paged_adamw_8bit" if use_4bit and torch.cuda.is_available() else "adamw_torch",
        label_names=["labels"],
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
    )
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    return trainer, tokenized_eval, list(trainer.state.log_history), backend


def prediction_metrics(trainer: Trainer, eval_dataset: Dataset) -> tuple[List[float], Dict[str, float]]:
    prediction_output = trainer.predict(eval_dataset)
    raw_predictions = prediction_output.predictions
    if isinstance(raw_predictions, tuple):
        raw_predictions = raw_predictions[0]
    preds = [float(row[0] if isinstance(row, (list, tuple)) else row) for row in raw_predictions]
    labels = [float(value) for value in prediction_output.label_ids]
    mae = sum(abs(pred - label) for pred, label in zip(preds, labels)) / max(1, len(labels))
    mse = sum((pred - label) ** 2 for pred, label in zip(preds, labels)) / max(1, len(labels))
    return preds, {"mae_vs_env": mae, "mse_vs_env": mse}


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a future-oriented reward model with QLoRA.")
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-3B-Instruct", help="Base reward model name or local path.")
    parser.add_argument("--episodes-per-task", type=int, default=4, help="Environment rollout episodes per task.")
    parser.add_argument("--epochs", type=float, default=1.0, help="Training epochs.")
    parser.add_argument("--batch-size", type=int, default=1, help="Per-device batch size.")
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8, help="Gradient accumulation steps.")
    parser.add_argument("--max-length", type=int, default=1024, help="Training sequence length.")
    parser.add_argument("--use-4bit", type=str2bool, default=True, help="Enable 4-bit quantized base model loading when CUDA is available.")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank.")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha.")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout.")
    parser.add_argument("--output-dir", default="artifacts/reward_model", help="Reward model output directory.")
    parser.add_argument("--results-dir", default="results", help="Metrics output directory.")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    samples = collect_reward_dataset(episodes_per_task=args.episodes_per_task)
    train_samples, eval_samples = split_samples(samples)
    eval_samples = eval_samples or train_samples[:1]
    train_dataset = dataset_from_samples(train_samples)
    eval_dataset = dataset_from_samples(eval_samples)

    trainer, tokenized_eval, log_history, backend = train_model(
        model_name=args.model_name,
        output_dir=args.output_dir,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        max_length=args.max_length,
        epochs=args.epochs,
        batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        use_4bit=args.use_4bit,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
    )
    predictions, metric_values = prediction_metrics(trainer, tokenized_eval)
    labels = [float(sample.future_oriented) for sample in eval_samples]

    config = {
        "backend": "regression",
        "reward_model_name": args.model_name,
        "training_backend": backend,
        "uses_4bit": bool(args.use_4bit and torch.cuda.is_available()),
    }
    (output_dir / "reward_backend_config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    preview_payload = []
    for sample, pred in zip(eval_samples[:10], predictions[:10]):
        payload = asdict(sample)
        payload["predicted_score"] = pred
        preview_payload.append(payload)

    metrics = {
        "reward_backend": "regression",
        "reward_model_name": args.model_name,
        "training_backend": backend,
        "episodes_per_task": args.episodes_per_task,
        "sample_count": len(samples),
        "train_samples": len(train_samples),
        "eval_samples": len(eval_samples),
        "uses_4bit": bool(args.use_4bit and torch.cuda.is_available()),
        **metric_values,
        "log_history": log_history,
    }
    (results_dir / "reward_model_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (results_dir / "reward_dataset_preview.json").write_text(json.dumps(preview_payload, indent=2), encoding="utf-8")
    save_loss_plot(log_history, results_dir / "reward_model_loss.png")
    save_prediction_plot(labels, predictions, results_dir / "reward_model_predictions.png")

    print(f"Wrote reward backend config to {output_dir / 'reward_backend_config.json'}")
    print(f"Wrote reward metrics to {results_dir / 'reward_model_metrics.json'}")
    print(f"Wrote reward preview to {results_dir / 'reward_dataset_preview.json'}")


if __name__ == "__main__":
    main()
