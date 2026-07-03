Fine-Tuned Models
=================

Litematica-GPT's local generation path uses **custom fine-tuned models** to turn a prompt into the
mod's schematic DSL. This document is the record of what was trained, the ideas behind it, and where
to get the weights. The full training pipeline (scripts, configs, processed datasets) lives under
[`ml_workspace/`](ml_workspace/); its architecture is described in
[`docs/ml-architecture.md`](docs/ml-architecture.md).

## The core idea: split planning from compiling

Base LLMs plan well but are unreliable at emitting a strict custom DSL with exact block coordinates.
So the pipeline uses **two specialized models**:

1. **Planner (spatial distiller)** — turns a short prompt (*"admin shoppe"*) into a step-by-step
   spatial construction rationale.
2. **Compiler (DSL specialist)** — rewrites that rationale into valid Litematica DSL.

Fine-tuning the compiler with a high-rank LoRA forces the model to *overwrite* its pretrained coding
habits and learn the DSL exactly, which sharply reduces syntax errors and coordinate drift.

## Experiment history

This was iterative. The evolution is visible in the committed processed datasets
(`ml_workspace/data/processed/mlx_*`) and the adapter configs:

| Base model family | Role | Adapter | LoRA (r / α) | Notes |
|---|---|---|---|---|
| **Llama 3.1 8B** (MLX 4-bit) | Planner | `spatial_distill_llama8b` | 8 / — | Lightweight spatial distiller (first planner). |
| **Llama 3.1 8B** (Unsloth 4-bit) | Compiler | `dsl_compiler_llama8b` | 256 / 512 | Heavy-capacity compiler; full checkpoint history (steps 3.7k→6k). |
| **Gemma 4 (e4b-it)** | Planner | `gemma4_planner_lora` | 128 / 256 | Planner ported to Gemma 4. |
| **Gemma 4 (e4b-it)** | Compiler | `gemma4_compiler_lora` (v1/v2/v3) | 128 / 256 | Main compiler, three iterations. |
| **Gemma 4 (e4b-it)** | Compiler | `gemma4_think_compiler_lora` | 128 / 256 | "Thinking" compiler variant. |

Additional base models were trialed during data prep and never promoted to a shipped adapter —
evidence remains in `ml_workspace/data/processed/`:
- **Phi-4** (`mlx_data_phi4*`) — several prompt/format variants.
- **~9B model** (`mlx_data_9b`).
- **Qwen** (`prepare_qwen_compiler_data.py`) — compiler data prep.
- Compiler dataset iterations **v1 → v7** (`mlx_compiler_data_v*`) trace the format/quality progression.

## Training setup (representative)

- **Method:** LoRA (PEFT), targeting all attention + MLP projections (`q/k/v/o`, `gate/up/down`).
- **Gemma 4 compiler:** rank 128, alpha 256, 32 layers.
- **Llama 3.1 compiler:** rank 256, alpha 512 (higher capacity).
- **Data:** ~3,165 DSL blueprints paired with synthetic spatial rationales, 8,192-token context.
- **Hardware:** trained on ThunderCompute RTX A6000 (48 GB) via Unsloth; run locally on Apple
  Silicon via MLX. See [`docs/thundercompute-bundling.md`](docs/thundercompute-bundling.md) and
  [`docs/thundercompute-redeploy.md`](docs/thundercompute-redeploy.md).

## Getting the weights

Adapter weights (0.6–2.5 GB each) are **too large for git** and are published as
**GitHub Release assets** — one release per fine-tune, so the history is visible on the
[Releases page](https://github.com/lukeclaw/litematica-gpt/releases). Only **final adapters** are
uploaded (not every intermediate checkpoint); the loss/step progression is preserved in the
committed training logs under `ml_workspace/logs_and_runs/`.

Download an `adapters.safetensors` and place it next to its committed `adapter_config.json`, e.g.:

```
ml_workspace/models_and_adapters/specialized_skills/gemma4_compiler_lora/
    adapter_config.json     # committed (reproducible hyperparameters)
    adapters.safetensors    # downloaded from the matching GitHub Release
```

Then point the local MLX runner at that adapter directory.
