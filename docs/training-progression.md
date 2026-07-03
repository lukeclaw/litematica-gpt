# Training progression

This page shows how the fine-tunes progressed. Per-step loss was streamed to the training console
on the remote ThunderCompute GPU instances; those raw logs were **not** archived back into this
repo, so the record here is built from **on-disk checkpoint milestones** and the training configs —
all verifiable in the tree. No loss numbers are invented.

## Runs and how far they trained

Adapters are checkpointed every 100 steps (`save_every: 100`), so the highest saved checkpoint is a
faithful marker of how long each run went.

| Model | Role | Steps reached | Checkpoints saved | Evidence |
|-------|------|---------------|-------------------|----------|
| `dsl_compiler_llama8b` | Compiler (Llama 3.1 8B) | **6000** | 60 | `0000100…0006000_adapters.safetensors` |
| `spatial_distill_llama8b` | Planner (Llama 3.1 8B) | **1000** | 10 | `0000100…0001000_adapters.safetensors` |
| `gemma4_think_compiler_lora` | Compiler (Gemma 4) | 100 | 1 | `0000100_adapters.safetensors` |
| `gemma4_compiler_lora` v1→v3 | Compiler (Gemma 4) | final only | — | three iterated final adapters |
| `gemma4_planner_lora` | Planner (Gemma 4) | final only | — | final adapter |

> Checkpoint weights are large binaries and are **not** committed (see [MODELS.md](../MODELS.md));
> only the final adapters are published as Releases. The step counts above are what the checkpoint
> filenames record.

## Training configuration

From [`ml_workspace/setup_and_configs/lora_config.yaml`](../ml_workspace/setup_and_configs/lora_config.yaml):

| Param | Value |
|-------|-------|
| rank / alpha | 128 / 256 (Gemma 4) · 256 / 512 (Llama compiler) |
| dropout | 0.05 |
| scale | 10.0 |
| lora_layers | 16 |
| learning_rate | 2e-5 |
| batch_size | 1 (grad accumulation 8) |
| max_seq_length | 3000 |
| iters | 1000 (compiler run extended to 6000) |
| save_every | 100 |

## The loss design

The interesting part of this project isn't a vanilla loss curve — it's the **custom weighted
structural loss** built to stop the model collapsing into "safe" flat foundations. See
[`ml_workspace/logs_and_runs/investigations/architectural_loss_strategy.md`](../ml_workspace/logs_and_runs/investigations/architectural_loss_strategy.md):
coordinate digits penalized 5×, `palette → layer_y` transitions 10×, and a repetition spike penalty
to punish infinite `layer_y` loops.

## Regenerating the loss curve

If a raw training log is retrieved from a GPU instance, the committed monitor can parse it into a
loss/step series:

```bash
python ml_workspace/logs_and_runs/training-monitor/scripts/parse_logs.py <training_compiler.log>
```

It matches HuggingFace-trainer lines (`{'loss': '...', 'learning_rate': '...', 'epoch': '...'}`) and
prints the latest step, loss, and ETA.
