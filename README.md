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

This repo keeps the paper-inspired RL structure from RLFF-ESC:

- deterministic environment
- partially observable hidden state
- hybrid immediate + future-oriented reward
- separate reward model and policy model

The change is the sub-domain. Instead of therapy-style support, this repo focuses on difficult conversation coaching.

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

The repo supports:

- a learned reward model
- a learned policy model

Reward model:

- recommended practical model: `distilroberta-base`
- script: [train_reward_model.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/train_reward_model.py)

Policy model:

- recommended practical model: `Qwen/Qwen2.5-0.5B-Instruct` or `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- script: [train_trl.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/train_trl.py)

## Key files

- [src/env.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/env.py)
- [src/seeker.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/seeker.py)
- [src/tasks.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/tasks.py)
- [src/grader.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/grader.py)
- [src/agentic.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/agentic.py)
- [src/training_utils.py](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/src/training_utils.py)
- [COLAB_README.md](/Users/5ivatej/Desktop/meta-hackathon/distress-ai-coach/COLAB_README.md)

## Docker / Colab

Model names are controlled from `.env`:

```env
POLICY_MODEL_NAME=distilgpt2
REWARD_MODEL_NAME=distilroberta-base
REWARD_MODEL_OUTPUT_DIR=artifacts/reward_model
POLICY_MODEL_OUTPUT_DIR=artifacts/policy_model
```

Recommended practical setup:

```env
POLICY_MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct
REWARD_MODEL_NAME=distilroberta-base
```

Run order:

```bash
docker compose up --build env-server
docker compose --profile reward up --build reward-trainer
docker compose --profile train up --build trainer
```

This pivot keeps the original paper-aligned training idea, but applies it to a safer benchmark: AI coaching for difficult conversations, not AI therapy.
