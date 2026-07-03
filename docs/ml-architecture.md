# Litematica-GPT Repository Guide

## Project Mission
The goal of this project is to build a local-hosted AI system capable of dynamically generating Minecraft structures (in Litematica DSL format) on the fly based on simple user prompts (e.g., "Build an admin shoppe").

To achieve high-quality spatial reasoning and perfect DSL syntax, the project uses an **Agentic Flow** with two distinct specialized models:

1. **Master Planner (Spatial Distiller)**: Converts a simple user prompt into a detailed, step-by-step "Spatial Rationale" (a deep spatial concept map).
2. **DSL Specialist (Compiler)**: Converts the Master Planner's rationale into perfect, raw Litematica DSL code.

---

## The Dual-Path Training Strategy

### Path 1: The Master Planner (Spatial Distill)
- **Input**: User prompt (e.g., structure name).
- **Output**: A `<Thinking>` block containing Footprint Analysis, Material Strategy, and Construction Sequence.
- **Data Generation**: `generate_synthetic_rationale.py` uses Gemini 3.1 Pro to reverse-engineer scraped DSL files into step-by-step architectural plans.
- **Adapter Location**: `specialized_skills/spatial_distill_llama8b/`
- **Training Optimization**: High temperature (0.7) during generation for creative architectural design.

### Path 2: The DSL Specialist (Compiler)
- **Input**: The detailed "Spatial Rationale" (Concept Map).
- **Output**: Raw Litematica DSL code.
- **Data Generation**: `prepare_compiler_data.py` maps the synthetic rationales to the exact DSL output, creating training pairs for the compiler.
- **Adapter Location**: `specialized_skills/dsl_compiler_llama8b/`
- **Training Optimization**: High LoRA Rank (128/256) to force the model to "overwrite" pre-trained habits and strictly learn the custom DSL syntax. Evaluated at temperature 0.0 or 0.1 for strict mathematical precision.

---

## Key Directories & Files

### 📁 Datasets Pipeline & Transformations

The project relies on a pipeline of data transformations to create the final training sets for both models. Here is the flow:

1. **`dataset/dsl/`** -> **`dataset/dsl_10kb/`**
   - **Origin:** Raw Minecraft schematics scraped and converted into the custom text-based DSL.
   - **Transformation:** Filtered to only include files smaller than 10KB.
   - **Purpose:** Ensures the final training examples comfortably fit within standard LLM context windows (preventing truncation during training or inference).

2. **`dataset/dsl_10kb/`** -> **`dataset/synthetic_rationales.jsonl`**
   - **Transformation:** The script `generate_synthetic_rationale.py` sends the raw DSL code to Gemini 3.1 Pro acting as a "Master Teacher." Gemini reverse-engineers the code to write a step-by-step `<Thinking>` process (the rationale).
   - **Purpose:** This acts as the "ground truth" concept map, bridging the gap between a simple name ("admin shoppe") and raw 3D coordinates.

3. **`dataset/synthetic_rationales.jsonl`** -> **`mlx_compiler_data_v6/`**
   - **Transformation:** Merges all 3,165 Gemini-generated rationales with their corresponding raw DSL code. It uses an expanded **8,192 token context window** (optimized for A6000/H100 GPUs).
   - **Purpose:** This is the **"God Mode" Instruction-Tuning Dataset for Path 2 (The DSL Specialist)**. It maximizes the architectural depth and prevents truncation of complex designs.

4. **`dataset/synthetic_rationales.jsonl`** -> **`mlx_distill_full/`** (via `prepare_mlx_distill_data.py`)
   - **Transformation:** Extracts just the structure name (Prompt) and the Gemini-generated rationale (Target), formatted into chat templates.
   - **Purpose:** This is the **Instruction-Tuning Dataset for Path 1 (The Master Planner)**. It teaches the model to hallucinate complex architectural logic from a simple title.

### 📁 Scripts
- **Data Preparation**:
  - `schematic_to_dsl.py` & `litematic_to_dsl.py`: Convert raw Minecraft schematic formats into the custom text-based DSL.
  - `generate_synthetic_rationale.py`: Calls the Gemini API to generate the Master Planner training data.
  - `prepare_god_dataset.py`: (New) Assembles the final v6 dataset with 8k token support.
- **Execution & Testing**:
  - `local_orchestrator.py`: The main inference script that runs the full agentic flow, swapping between the Planner and Compiler adapters.
  - `test_llama_compiler_v*.py`: Iterative test scripts to evaluate the DSL Specialist's coordinate accuracy and syntax mapping.
- **Training**:
  - `train_litematica_gemma4.py` / `train_unsloth.py`: High-performance training scripts (utilizing Unsloth) designed to be run on remote GPUs (e.g., A6000 on Thunder Compute) for fast, memory-efficient fine-tuning.

### 📁 Specialized Skills (Adapters)
- Holds the output weights (LoRA adapters) for the local Apple Silicon (MLX) execution.
- Includes `lora_config.yaml` detailing the aggressive training parameters (Rank 128, Alpha 256).

---

## Optimizations & Technical Choices
1. **Separation of Concerns**: Splitting spatial reasoning from syntax generation drastically reduces "hallucinations" and coordinate drift.
2. **MLX Framework**: Optimized for Apple Silicon (M-Series), allowing fast local execution and quick adapter swapping in `local_orchestrator.py`.
3. **Unsloth & Remote GPU Training**: Utilizing Thunder Compute instances (A6000/A100) with Unsloth allows for 2x faster training with a massive **8,192+ sequence length**, preventing truncation of large, complex DSL blueprints like industrial pipe networks or 2D logo canvases.
4. **Custom DSL**: A lightweight, text-based alternative to binary `.litematic` files, making it easily understandable and generate-able by LLMs.
