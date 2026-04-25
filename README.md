---
title: Distress AI Coach (OpenEnv)
emoji: "🧭"
sdk: docker
pinned: false
tags:
  - openenv
---

# Distress AI Coach

An OpenEnv environment for training and evaluating AI coaches that help users prepare for difficult real-world conversations.

This repo keeps the paper-inspired training structure from RLFF-ESC:

- deterministic environment
- partially observable hidden state
- hybrid immediate + future-oriented reward
- separate reward model and policy model

The domain is different. Instead of therapy-style support, this repo focuses on difficult-conversation coaching.

## Tasks

| Task ID | Difficulty | Core challenge |
| --- | --- | --- |
| `manager_boundary_reset` | easy | Coach the user through a respectful boundary conversation with their manager. |
| `relationship_repair_talk` | medium | Coach the user through a repair conversation where they need to own harm without defensiveness. |
| `volatile_boundary_planning` | hard | Coach the user through a boundary conversation where escalation risk is real, so de-escalation planning matters. |

## Why this is long-horizon

The agent has to:

- surface the real blocker behind the conversation
- avoid jumping into a final script too early
- carry memory across sessions
- remember unresolved threads
- plan one usable next step
- incorporate safer logistics and backup support in higher-risk cases

The value of a reply is often only visible later, so the environment rewards both current-turn quality and future conversation quality.

## Two-model setup

The current intended setup is:

- reward model: `Qwen/Qwen2.5-3B-Instruct` trained with QLoRA as a future-oriented regressor
- policy model: `Qwen/Qwen2.5-0.5B-Instruct` trained with LoRA/QLoRA on reward-guided trajectories

Scripts:

- [train_reward_model.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/train_reward_model.py)
- [train_trl.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/train_trl.py)
- [src/reward_backend.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/reward_backend.py)

## Key files

- [src/env.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/env.py)
- [src/seeker.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/seeker.py)
- [src/tasks.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/tasks.py)
- [src/grader.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/grader.py)
- [src/agentic.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/agentic.py)
- [src/training_utils.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/training_utils.py)
- [COLAB_README.md](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/COLAB_README.md)

## Colab-first flow

The recommended runtime is Google Colab with a `T4` GPU.

Core commands:

```bash
python train_reward_model.py           --model-name Qwen/Qwen2.5-3B-Instruct           --episodes-per-task 4           --epochs 1           --batch-size 1           --gradient-accumulation-steps 8           --max-length 1024           --use-4bit true           --output-dir artifacts/reward_model           --results-dir results

python train_trl.py           --model-name Qwen/Qwen2.5-0.5B-Instruct           --reward-backend regression           --reward-model-path artifacts/reward_model           --episodes-per-task 4           --epochs 1           --batch-size 1           --gradient-accumulation-steps 8           --max-length 768           --use-4bit true           --output-dir artifacts/policy_model           --results-dir results
```

`.env.example` matches those defaults. The detailed Colab runbook is in [COLAB_README.md](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/COLAB_README.md).

## Important scope note

This repo now supports:

- a truly trained reward model path
- 4-bit QLoRA-style loading for Colab CUDA runtimes
- reward-guided policy training with a separate reward model

It is still not a full PPO/GRPO RL implementation. The current policy stage is reward-guided supervised fine-tuning.
