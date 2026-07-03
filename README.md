Litematica-GPT
==============

Litematica-GPT is a fork of [Litematica](https://github.com/maruohon/litematica) (by *masa*)
that adds an **AI schematic generator**: describe a structure in plain English and the mod
generates a placeable Litematica schematic for you, in-game.

> **Base mod:** Litematica is a client-side schematic mod for Minecraft. This fork targets
> **Minecraft 1.21.1 / Fabric** and layers an AI generation pipeline on top of it. All of the
> original Litematica functionality (placement, material lists, schematic editing, etc.) is
> unchanged — see the [upstream project](https://github.com/maruohon/litematica) for that.

---

## What this fork adds

- **"Generate AI Schematic" screen** — opened from the Litematica main menu. Enter a prompt
  (e.g. *"a small stone-brick guard tower"*) and a name, click **Generate**, and the result is
  loaded as a schematic ready to place.
- **Two AI providers**, selectable in the config (`aiProvider`):
  - **OpenAI** — hosted GPT models.
  - **Google Gemini (Vertex AI)** — including custom **tuned models** in the Vertex Model Registry.
- **Agentic generation flow** (`HighEffortAIWorkflow`): a *planner* model turns the prompt into a
  spatial construction plan, and a *worker/compiler* model emits the structure in a compact custom
  **DSL**, which is parsed back into blocks. This split reduces coordinate drift and hallucinated syntax.
- **Custom text DSL** — a lightweight, human-readable alternative to binary `.litematic` files that
  LLMs can generate reliably. A round-trip debug utility lives in [`tools/DSLReverserTool.java`](tools/DSLReverserTool.java).

The self-hosted fine-tuned models used by the local Gemini/MLX path are documented in
**[MODELS.md](MODELS.md)**, and their weights are published as GitHub Releases.

---

## Configuration

AI settings live in Litematica's **Generic** config (`config/litematica.json`, or the in-game
config menu). Nothing is hardcoded — all keys are supplied by you.

| Option | Default | Purpose |
|--------|---------|---------|
| `aiProvider` | `OPENAI` | Which provider to use (`OPENAI` / `GEMINI`). |
| `openAiApiKey` | *(empty)* | Your OpenAI API key. |
| `openAiWorkerModelId` | `gpt-4o-mini` | Model that compiles the DSL. |
| `openAiPlannerModelId` | `gpt-5.4-mini` | Model that plans the structure. |
| `geminiApiKey` | *(empty)* | Vertex AI bearer token. |
| `geminiProjectId` | *(empty)* | GCP project ID (omit only for fully-qualified `projects/...` model paths). |
| `geminiLocation` | `us-central1` | Vertex AI region. |
| `geminiWorkerModelId` | `gemini-1.5-flash-001` | Worker/compiler model. Accepts base models, `tunedModels/…`, `models/…`, numeric registry IDs, or full `projects/…` paths. |
| `geminiPlannerModelId` | `gemini-2.5-flash` | Planner model. |
| `aiFallbackBlock` | `minecraft:stone` | Block substituted when a generated block can't be resolved. |

> **Never commit your API keys.** Keep them in your local config only.

---

## Building

Standard Gradle / Fabric build (Minecraft 1.21.1):

```
git clone https://github.com/lukeclaw/litematica-gpt.git
cd litematica-gpt
./gradlew build
```

The built jar lands in `build/libs/`. Requires [malilib](https://github.com/maruohon/malilib)
(version pinned in `gradle.properties`).

---

## Repository layout

This is a **research monorepo** — it holds both the shippable mod *and* the process that produced
the AI models (scripts, configs, datasets, training notes), so the full experimentation history is
visible.

```
src/                  Java source for the mod (Litematica + AI feature under
                      src/.../schematic/ai/ and gui/GuiOpenAISchematic.java)
tools/                Standalone developer utilities (not part of the mod build)
docs/                 ML architecture + ThunderCompute training/deployment guides
ml_workspace/         The ML research project:
    scripts/            data prep, training, evaluation, utilities
    setup_and_configs/  LoRA configs + environment setup
    data/processed/     final fine-tuning datasets (JSONL) — committed
    data/sample/        small raw-DSL sample (full 10 GB corpus is local-only)
    models_and_adapters/ adapter_config.json for every fine-tune (weights via Releases)
    logs_and_runs/      training logs / loss progression
MODELS.md             Fine-tuning history + how to get the trained LoRA adapters
build.gradle          Fabric/Gradle build config
```

**What is *not* in git** (too large; see [MODELS.md](MODELS.md) for where it lives): trained model
weights (`*.safetensors` → GitHub Releases), the full ~10 GB raw scraped corpus, multi-GB dataset
archives, virtualenvs, and the Minecraft dev-runtime world. Everything needed to understand and
reproduce the work — code, configs, processed data, and docs — **is** committed.

---

## Credits & license

- Original **Litematica** and its base code © *masa* — https://github.com/maruohon/litematica
- AI generation feature and fork by **lukeclaw**.
- Licensed under the terms in [LICENSE.txt](LICENSE.txt) (inherited from upstream Litematica).
