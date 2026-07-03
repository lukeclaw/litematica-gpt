# Litematica-GPT

This repository contains two main components:
1. **Litematica Mod**: A Java/Fabric mod for Minecraft (located at the root and `src/`).
2. **ML Workspace**: A comprehensive Python ML training and evaluation pipeline for DSL generation (located in `ml_workspace/`).

## Project Structure
- `src/`: Java source code for the Litematica mod.
- `ml_workspace/`: Consolidated ML workspace for model training and data processing.
    - [ml_workspace/AGENTS.md](ml_workspace/AGENTS.md)

## Development Workflow
- **Java**: Standard Gradle project. Use `./gradlew build`.
- **ML**: Uses a dedicated `venv/` at the root. All ML operations should be run from within the `ml_workspace/` context or with proper relative paths.

## ML Training & Deployment
- **Training Infrastructure**: Uses ThunderCompute RTX A6000 instances for training Gemma 4 models
- **Training Bundles**: Pre-configured zip archives for compiler and planner agent training
- **Deployment Guide**: See [THUNDERCOMPUTE_BUNDLING.md](THUNDERCOMPUTE_BUNDLING.md) for detailed bundling and deployment instructions
- **Key Components**:
  - Training scripts in `ml_workspace/scripts/train/`
  - Setup scripts in `ml_workspace/setup_and_configs/`
  - Pre-built bundles in `ml_workspace/data/archives/`
  - Training logs in `ml_workspace/logs_and_runs/`
