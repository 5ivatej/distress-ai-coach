# Colab Runbook

This is the direct Google Colab path for the real two-model setup:

- reward model: `Qwen/Qwen2.5-3B-Instruct` trained with QLoRA
- policy model: `Qwen/Qwen2.5-0.5B-Instruct` trained with LoRA/QLoRA
- GPU target: Colab `T4`

Do not use Docker in Colab unless you have a specific reason. The simplest path is to clone the repo and run the Python scripts directly.

## 1. Start Colab

Set runtime to `GPU`, then confirm you actually got a T4:

```bash
!nvidia-smi
```

## 2. Clone the repo

```bash
!git clone https://github.com/5ivatej/distress-ai-coach.git
%cd distress-ai-coach
```

## 3. Install dependencies

```bash
!pip install -U pip
!pip install -r requirements.txt
```

## 4. Optional: mount Drive for saving artifacts

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 5. Create `.env` if you want compose parity

```bash
%%writefile .env
POLICY_MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct
REWARD_MODEL_NAME=Qwen/Qwen2.5-3B-Instruct
REWARD_BACKEND=regression
REWARD_MODEL_OUTPUT_DIR=artifacts/reward_model
POLICY_MODEL_OUTPUT_DIR=artifacts/policy_model
TRAIN_RESULTS_DIR=results
```

## 6. Train the reward model

```bash
!python train_reward_model.py           --model-name Qwen/Qwen2.5-3B-Instruct           --episodes-per-task 4           --epochs 1           --batch-size 1           --gradient-accumulation-steps 8           --max-length 1024           --use-4bit true           --output-dir artifacts/reward_model           --results-dir results
```

This writes:

- `artifacts/reward_model/`
- `results/reward_model_metrics.json`
- `results/reward_model_loss.png`
- `results/reward_model_predictions.png`
- `results/reward_dataset_preview.json`

## 7. Train the policy model

```bash
!python train_trl.py           --model-name Qwen/Qwen2.5-0.5B-Instruct           --reward-backend regression           --reward-model-path artifacts/reward_model           --episodes-per-task 4           --epochs 1           --batch-size 1           --gradient-accumulation-steps 8           --max-length 768           --use-4bit true           --output-dir artifacts/policy_model           --results-dir results
```

This writes:

- `artifacts/policy_model/`
- `results/training_metrics.json`
- `results/loss_curve.png`
- `results/reward_curve.png`
- `results/before_after.md`
- `results/policy_dataset_preview.json`

## 8. Save outputs to Drive

```bash
!mkdir -p /content/drive/MyDrive/distress-ai-coach-run
!cp -r artifacts results /content/drive/MyDrive/distress-ai-coach-run/
```

## 9. What changed technically

The current scripts now assume:

- a truly trained reward model, not just a fixed judge
- QLoRA / 4-bit base-model loading on CUDA
- a trained reward-model path at `artifacts/reward_model`
- reward-guided policy dataset construction using that trained reward model

## 10. Common issues

- If you do not get a `T4`, memory behavior may differ.
- If Hugging Face downloads fail, rerun the cell.
- The first model load can take a while because Colab has to download both Qwen models.
- This is still reward-guided policy training, not full PPO/GRPO RL.
