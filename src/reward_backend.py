"""Reward backend helpers for learned reward models and optional LLM judge mode."""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import torch
from peft import PeftConfig, PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
)

from .agentic import AgentMemory
from .training_utils import build_reward_text


def select_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _preferred_dtype(device: str):
    if device != "cuda":
        return torch.float32
    major, _minor = torch.cuda.get_device_capability()
    return torch.bfloat16 if major >= 8 else torch.float16


def _build_quantization_config(device: str, use_4bit: bool = True):
    if not use_4bit or device != "cuda":
        return None
    compute_dtype = _preferred_dtype(device)
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )


def load_sequence_reward_model(model_path: str, use_4bit: bool = True):
    model_ref = Path(model_path)
    device = select_device()
    quantization_config = _build_quantization_config(device, use_4bit=use_4bit)
    adapter_config_path = model_ref / "adapter_config.json"

    if adapter_config_path.exists():
        peft_config = PeftConfig.from_pretrained(str(model_ref))
        base_model_name = peft_config.base_model_name_or_path
        tokenizer_source = str(model_ref) if (model_ref / "tokenizer_config.json").exists() else base_model_name
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model_kwargs = {
            "num_labels": 1,
            "problem_type": "regression",
            "low_cpu_mem_usage": True,
        }
        if quantization_config is not None:
            model_kwargs["quantization_config"] = quantization_config
            model_kwargs["device_map"] = "auto"
        elif device == "cuda":
            model_kwargs["torch_dtype"] = _preferred_dtype(device)

        base_model = AutoModelForSequenceClassification.from_pretrained(base_model_name, **model_kwargs)
        model = PeftModel.from_pretrained(base_model, str(model_ref))
    else:
        tokenizer = AutoTokenizer.from_pretrained(str(model_ref))
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        model_kwargs = {
            "low_cpu_mem_usage": True,
        }
        if quantization_config is not None:
            model_kwargs["quantization_config"] = quantization_config
            model_kwargs["device_map"] = "auto"
        elif device == "cuda":
            model_kwargs["torch_dtype"] = _preferred_dtype(device)
        model = AutoModelForSequenceClassification.from_pretrained(str(model_ref), **model_kwargs)
        if device != "cuda":
            model.to(device)

    model.eval()
    return model, tokenizer


def load_llm_reward_judge(model_name: str, use_4bit: bool = True):
    device = select_device()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model_kwargs = {"low_cpu_mem_usage": True}
    quantization_config = _build_quantization_config(device, use_4bit=use_4bit)
    if quantization_config is not None:
        model_kwargs["quantization_config"] = quantization_config
        model_kwargs["device_map"] = "auto"
    elif device == "cuda":
        model_kwargs["torch_dtype"] = _preferred_dtype(device)
    model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
    if device != "cuda":
        model.to(device)
    model.eval()
    return model, tokenizer, device


def _llm_judge_prompt(text: str) -> str:
    return textwrap.dedent(
        f"""
        You are a reward judge for a difficult-conversation coaching benchmark.

        Score the candidate coach response for future-oriented quality.
        Use this scale:
        - 0 = actively harmful, derailing, or escalating
        - 25 = weak / unhelpful
        - 50 = neutral / mixed
        - 75 = good and likely to improve the trajectory
        - 100 = excellent and strongly improves the future trajectory

        Return ONLY valid JSON in this format:
        {{"score": <integer 0-100>, "reason": "<short reason>"}}

        Context:
        {text}
        """
    ).strip()


def parse_judge_score(text: str) -> float:
    text = (text or "").strip()
    if not text:
        return 0.5

    try:
        payload = json.loads(text)
        raw = payload.get("score", 50)
        value = float(raw)
        if value > 1.0:
            value /= 100.0
        return max(0.0, min(1.0, value))
    except Exception:
        pass

    match = re.search(r"(-?\d+(?:\.\d+)?)", text)
    if not match:
        return 0.5
    value = float(match.group(1))
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))


def judge_text_with_llm(model, tokenizer, device: str, text: str, max_new_tokens: int = 64) -> Tuple[float, str]:
    prompt = _llm_judge_prompt(text)
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    model_device = next(model.parameters()).device if hasattr(model, "parameters") else device
    inputs = {key: value.to(model_device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            top_p=None,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    prompt_len = inputs["input_ids"].shape[1]
    generated = outputs[0][prompt_len:]
    decoded = tokenizer.decode(generated, skip_special_tokens=True).strip()
    return parse_judge_score(decoded), decoded


def score_candidates_with_sequence_reward(
    reward_model,
    reward_tokenizer,
    candidates: Sequence[Tuple[str, str]],
    reward_texts: Sequence[str],
) -> List[Tuple[str, str, float]]:
    scored: List[Tuple[str, str, float]] = []
    model_device = next(reward_model.parameters()).device
    for (source, candidate), text in zip(candidates, reward_texts):
        inputs = reward_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=True,
        )
        inputs = {key: value.to(model_device) for key, value in inputs.items()}
        with torch.no_grad():
            logits = reward_model(**inputs).logits
        score = float(logits.squeeze().item())
        scored.append((source, candidate, score))
    scored.sort(key=lambda item: item[2], reverse=True)
    return scored


def score_candidates_with_llm_reward(
    reward_model,
    reward_tokenizer,
    device: str,
    candidates: Sequence[Tuple[str, str]],
    reward_texts: Sequence[str],
) -> List[Tuple[str, str, float]]:
    scored: List[Tuple[str, str, float]] = []
    for (source, candidate), text in zip(candidates, reward_texts):
        score, _raw = judge_text_with_llm(reward_model, reward_tokenizer, device, text)
        scored.append((source, candidate, score))
    scored.sort(key=lambda item: item[2], reverse=True)
    return scored


def load_reward_backend(
    backend: str,
    reward_model_name: str = "",
    reward_model_path: str = "",
    use_4bit: bool = True,
):
    if backend == "llm_judge":
        if not reward_model_name:
            raise ValueError("reward_model_name is required for llm_judge backend")
        model, tokenizer, device = load_llm_reward_judge(reward_model_name, use_4bit=use_4bit)
        return {
            "backend": "llm_judge",
            "model": model,
            "tokenizer": tokenizer,
            "device": device,
            "model_name": reward_model_name,
        }
    if backend == "regression":
        if not reward_model_path:
            raise ValueError("reward_model_path is required for regression backend")
        model, tokenizer = load_sequence_reward_model(reward_model_path, use_4bit=use_4bit)
        return {
            "backend": "regression",
            "model": model,
            "tokenizer": tokenizer,
            "device": next(model.parameters()).device,
            "model_name": reward_model_path,
        }
    raise ValueError(f"Unsupported reward backend: {backend}")


def resolve_reward_backend(
    requested_backend: str,
    reward_model_name: str = "",
    reward_model_path: str = "",
) -> Tuple[str, str]:
    if requested_backend != "auto":
        if requested_backend == "llm_judge":
            return "llm_judge", reward_model_name
        if requested_backend == "regression":
            return "regression", reward_model_path
        return requested_backend, ""

    config_path = Path(reward_model_path) / "reward_backend_config.json" if reward_model_path else None
    if config_path and config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        backend = str(config.get("backend", "auto"))
        model_name = str(config.get("reward_model_name", "")) or reward_model_name
        if backend in {"llm_judge", "regression"}:
            return backend, model_name if backend == "llm_judge" else reward_model_path

    if reward_model_path and Path(reward_model_path).exists():
        return "regression", reward_model_path
    if reward_model_name:
        return "llm_judge", reward_model_name
    return "none", ""


def reward_texts_for_candidates(observation, memory: AgentMemory, candidates: Sequence[Tuple[str, str]]) -> List[str]:
    return [build_reward_text(observation, memory, candidate) for _, candidate in candidates]
