# Strategy: Spatial Rationale & Weighted Structural Loss

## 1. The Problem: "The Foundation Trap"
During fine-tuning on Minecraft DSL, smaller models (8B-14B) often suffer from **Mode Collapse** or **Reward Hacking**. Because the model is rewarded for predicting the next token correctly, it learns that a 100x100 grid of "Air" or "Stone" is a statistically safe way to achieve a low error score. 

**Symptoms:**
*   Model generates `palette` then loops on `layer_y 0 0 0` with infinite `.` or `A` characters.
*   Model ignores the specific dimensions in the user prompt to output a generic "safe" foundation.

---

## 2. Solution Part A: Synthetic Rationale Distillation
We must break the direct link between **User Request** and **DSL Code**.
*   **The Teacher:** Use Gemini 3.1 Pro to look at raw DSL and write an "Active Voice" Thinking process.
*   **The Student:** Train the local model to output `<Thinking> [Rationale] </Thinking> <DSL> [Code] </DSL>`.
*   **The Result:** The model must "commit" to a plan (e.g., "I will build a 5x5 house") before it starts the code, making it logically harder to deviate into an infinite loop.

---

## 3. Solution Part B: Weighted Structural Loss (The "Hot-Patch")
To force the model to care about the *integrity* of the building, we modify the `default_loss` function in `mlx_lm/tuner/trainer.py`.

### Targeted Penalties:
1.  **Coordinate Precision (5x weight):** Penalize mistakes in numbers (0-9) more heavily than letters.
2.  **Command Sequence (10x weight):** High penalty for missing the transition from `palette` to `layer_y`.
3.  **Repetition Spike:** If `layer_y` or `fill` appears more than $N$ times in a single sequence without a change in the $Y$ coordinate, multiply the loss by 10.0.

### Implementation Logic (Draft):
```python
def architectural_loss(model, batch, lengths):
    logits = model(batch[:, :-1])
    targets = batch[:, 1:]
    
    # Standard Cross Entropy
    base_ce = nn.losses.cross_entropy(logits, targets)
    
    # 1. Identify Coordinate Tokens
    # (Mapping token IDs for 0-9 and space/coordinate markers)
    
    # 2. Identify Repeats
    # Check if the model is repeating the same grid line over and over
    
    # 3. Apply Multiplier
    # weighted_ce = base_ce * architectural_mask
    
    return weighted_ce.sum() / mask.sum()
```

---

## 4. How to Implement
1.  **Run Distillation:** Execute `generate_synthetic_rationale.py` to build the "Thinking" dataset.
2.  **Apply Patch:** Use a script to replace `default_loss` in the `venv/lib/python3.12/site-packages/mlx_lm/tuner/trainer.py` file with the weighted version.
3.  **Train at Rank 128:** High rank is necessary to ensure the model has the capacity to "unlearn" its generic habits.
4.  **Validate via `test_specialist.py`:** Use the "Palette Priming" technique (`full_prompt += "palette\n"`) to ensure the model enters the correct generation mode.
