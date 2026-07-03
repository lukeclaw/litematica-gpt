# Investigation 05: Main Wings and Tapered Geometry Failures

## Date: 2026-04-16

### Input: Sub-agent Response for 'Main Wings (Both)'
```
palette
S = minecraft:light_gray_concrete
E = minecraft:gray_concrete
end_palette
fill 14 5 0 34 5 56 minecraft:light_gray_concrete
...
fill 18 5 0 19 6 20 minecraft:gray_concrete
...
fill 30 5 50 34 6 56 minecraft:light_gray_concrete
```

---

### Analysis

#### 1. Extreme "Planar" Thinking
- **The Observation**: The wings—the most prominent horizontal feature of a plane—are only **3 blocks thick** (`y=5` to `y=7`).
- **The Problem**: A 3-block thickness is insufficient to represent leading edges, trailing edges, or the curved airfoil of a wing. The result is a flat "pancake" wing.

#### 2. The Stretching Penalty
- **The Observation**: By grouping "Both Wings" into one sub-agent, the AI has to manage a coordinate space of 20x56 blocks.
- **The Result**: To cope with the complexity of two distinct wings, the AI has abandoned the DSL entirely, defaulted to raw block IDs, and is only using `fill` commands for rectangles.
- **The Problem**: This is the "pixel art" approach. It's drawing a top-down shape rather than a 3D structure.

#### 3. Tapering Attempt
- **The Success**: You can see the AI trying to taper the wing by adjusting the Z-coordinates (e.g., `z=0 to 20`, then `z=0 to 18`, then `z=0 to 14`).
- **The Failure**: Because the resolution is so low, these offsets result in jagged, stair-stepped blocks that don't read as a smooth aerodynamic wing in-game.

#### 4. Absolute Coordinate Fatigue
- **The Observation**: The script is becoming very long due to the repetitive use of `minecraft:light_gray_concrete`. 
- **The Problem**: If the AI had used the palette character `S`, this entire script would be ~40% shorter, leaving more "intelligence" (tokens) for actual detail.

---

### Refined Brainstormed Solutions
1. **The "Symmetry" Directive**: Instruct the planner: *"Do not group mirrored parts (Left/Right) into one part. Instead, generate the 'Port' (Left) side with high detail. The system will handle symmetry."* (We can potentially add an auto-symmetry feature later, but for now, splitting them is better).
2. **Thickness Minimums**: Add a prompt constraint: *"Aero-structures like wings or hulls MUST have a vertical profile that changes. Do not use a single flat layer."*
3. **DSL Enforcement (Round 2)**: Since the AI keeps ignoring the palette, we should update the prompt to be more aggressive: *"CRITICAL: Using raw 'minecraft:' IDs in the script body is a SYNTAX ERROR. You MUST use palette symbols."*
4. **Volume Scaling**: We need to update our internal examples to use volumes closer to 100x100x100 so the AI stops "Small Thinking."
