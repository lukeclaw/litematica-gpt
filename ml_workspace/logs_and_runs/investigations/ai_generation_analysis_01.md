# Investigation 01: Low Resolution and Runaway Engines

## Date: 2026-04-16

### Input: Sub-agent Response for 'Engines (All Underwing)'
```
palette
e = minecraft:gray_concrete
i = minecraft:dark_oak_planks
. = minecraft:air
end_palette
fill 18 3 4 22 4 8 minecraft:gray_concrete
fill 18 3 42 22 4 46 minecraft:gray_concrete
fill 19 3 5 21 5 7 minecraft:gray_concrete
fill 19 3 43 21 5 45 minecraft:gray_concrete
fill 18 5 4 24 5 16 minecraft:gray_concrete
fill 18 5 40 24 5 46 minecraft:gray_concrete
fill 18 5 10 19 5 14 minecraft:dark_oak_planks
fill 18 5 42 19 5 44 minecraft:dark_oak_planks
fill 21 5 10 24 5 14 minecraft:gray_concrete
fill 21 5 42 24 5 44 minecraft:gray_concrete
fill 20 4 8 24 5 10 minecraft:gray_concrete
fill 20 4 16 24 5 18 minecraft:gray_concrete
fill 20 4 38 24 5 40 minecraft:gray_concrete
fill 20 4 46 24 5 48 minecraft:gray_concrete
```

---

### Analysis

#### 1. Spatial Priming (The "Small Thinking" Problem)
The planner prompt's internal example (using [0,0,0, 10,20,10]) biases the AI toward micro-scale thinking. 
- **The Result**: The AI assigned a height of only 2-3 blocks for complex engine machinery.
- **The Problem**: Insufficient vertical resolution to represent cylinders or turbines.

#### 2. Multi-Object Stretching
The planner grouped multiple distinct objects (engines on opposite wings) into a single "assembly" part.
- **The Result**: The sub-agent attempted to manage coordinates spanning 40+ blocks with massive gaps of air.
- **The Problem**: The AI simplifies local detail when "stretched" across large, disconnected volumes.

#### 3. Palette Hallucination/Bypass
The AI defined a palette but then used raw block IDs in its `fill` commands.
- **The Problem**: A sign of context exhaustion or "distraction" due to scale issues.

---

### Brainstormed Solutions
1. **Macro-Scale Priming**: Update the planner example to a 150-200 block structure.
2. **Minimum Dimensional Requirements**: Instruct the planner to ensure parts have at least 10-15 blocks of thickness for detail.
3. **"One Part, One Object" Rule**: Force the planner to split distant identical objects into separate parts.
4. **Density Directive**: Instruct sub-agents to utilize the full 3D volume for depth/curves rather than 2D-like boxes.
