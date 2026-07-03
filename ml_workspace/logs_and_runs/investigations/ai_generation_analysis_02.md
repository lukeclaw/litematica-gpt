# Investigation 02: Tail Assembly Blockiness and DSL Verbosity

## Date: 2026-04-16

### Input: Sub-agent Response for 'Tail Assembly'
```
palette
S = minecraft:light_gray_concrete
E = minecraft:gray_concrete
end_palette
fill 38 5 26 40 7 30 minecraft:light_gray_concrete
fill 39 6 31 41 7 33 minecraft:light_gray_concrete
fill 39 8 27 39 8 29 minecraft:gray_concrete
fill 40 8 26 40 8 30 minecraft:gray_concrete
fill 41 8 27 41 8 29 minecraft:gray_concrete
fill 42 8 28 42 8 28 minecraft:gray_concrete
fill 41 9 28 41 9 28 minecraft:gray_concrete
fill 40 9 28 40 10 28 minecraft:gray_concrete
fill 39 9 28 39 9 28 minecraft:gray_concrete
fill 38 8 27 38 8 29 minecraft:gray_concrete
fill 38 9 28 38 9 28 minecraft:gray_concrete
fill 41 5 26 42 6 30 minecraft:light_gray_concrete
fill 42 6 27 42 7 29 minecraft:light_gray_concrete
fill 42 5 28 42 5 28 minecraft:gray_concrete
fill 38 5 27 38 5 29 minecraft:gray_concrete
fill 39 5 26 40 5 26 minecraft:gray_concrete
fill 39 5 30 40 5 30 minecraft:gray_concrete
```

---

### Analysis

#### 1. Persistent Spatial Compression (Low Res)
The vertical resolution remains extremely low (y=5 to y=10).
- **The Result**: A tail assembly—which should have stabilizers, a rudder, and a tapered cone—is forced into a 5-block height.
- **The Problem**: At this scale, the AI cannot represent "aerodynamic" or "curved" shapes; it can only place small blocks of concrete.

#### 2. DSL Command Inefficiency
The sub-agent is using `fill` commands for single-block placements.
- **Example**: `fill 42 8 28 42 8 28 minecraft:gray_concrete`
- **The Problem**: It should be using the `set` command. Using `fill` for single blocks makes the script 2x-3x longer than necessary, contributing to context exhaustion.

#### 3. Total Ignorance of Palette
Once again, the AI defined `S` and `E` but completely ignored them, typing out the full `minecraft_id` every time.
- **The Problem**: This is a direct waste of output tokens and suggests the AI is "lazy" or overwhelmed by the prompt complexity, defaulting to the most literal Minecraft syntax it knows rather than our optimized DSL.

#### 4. Geometry Hallucination
The "Tail" is essentially a small 4x5x7 blob. It has no structural relationship to a fuselage or wings.

---

### Refined Brainstormed Solutions
1. **Implicit Coordinate Normalization**: In the prompt, we should emphasize that coordinates are **Absolute**, and provide a "Goal Resolution" (e.g., "Think at a scale of 1 block = 0.5 meters").
2. **Palette Enforcement**: Update the sub-agent prompt to say: *"MANDATORY: You MUST use your palette characters in all commands. DO NOT use raw minecraft_ids in the script body."*
3. **Command Specificity**: Tell the AI: *"Use 'set' for single blocks, 'fill' only for volumes larger than 2x2x2."*
4. **Structural Proportioning**: The planner needs a prompt update to check "Is this part too small for the level of detail requested?" If yes, it should expand the `global_bounds`.
