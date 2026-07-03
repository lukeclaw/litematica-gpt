# Investigation 03: Landing Gear Coherence and Vertical Alignment

## Date: 2026-04-16

### Input: Sub-agent Response for 'Landing Gear (All)'
```
palette
l = minecraft:black_concrete
w = minecraft:black_wool
h = minecraft:stone_button
end_palette
layer_y 4 0 0
.....lllllll.
....lwwhhwwwl
....lllllllll.
.....l....l..
.....l....l..
.....l....l..
.....l....l..
.....l....l..
.....l....l..
end_layer
... (layers 3, 2, 1, 0)
```

---

### Analysis

#### 1. Vertical "Crushing"
The landing gear is generated at the absolute bottom of the coordinate space (`y=0` to `y=4`).
- **The Problem**: In the previous investigations, we saw engines at `y=3` and the tail at `y=5`. This means the AI is attempting to fit an entire airplane—wheels, engines, and fuselage—within a **10-block vertical slice**. 
- **The Result**: The plane is essentially "flat". It has no room for a rounded fuselage or realistic landing gear struts.

#### 2. Grouping Efficiency vs. Detail
The planner grouped all landing gear into one part.
- **The Result**: The ASCII map shows multiple vertical lines (`l.l`). It is trying to draw all wheels and struts in a single map.
- **The Problem**: By cramming multiple distinct mechanical objects into one sub-agent, we lose the ability to use intricate commands for each wheel or hydraulic strut.

#### 3. Successful DSL/Palette Usage
- **The Success**: This sub-agent **correctly** used the palette characters (`l`, `w`, `h`) instead of raw block IDs. This proves the system instructions are understood but inconsistently applied across different sub-agent instances.

#### 4. Absolute Coordinate Confusion
The AI is using `layer_y` starting at `0`. 
- **The Problem**: If this is a "High Effort" build, it should likely be elevated in the air or at least higher than `y=0`. The AI is defaulting to the origin, possibly due to the small examples provided in the prompts.

---

### Refined Brainstormed Solutions
1. **Vertical Scale Bias**: Add a prompt instruction: *"The Minecraft world is 320 blocks high. For high-detail builds like aircraft or ships, aim for a total height of at least 40-60 blocks. Do not flatten your build into the first 10 layers."*
2. **Explicit Unit Scale**: Tell the AI: *"Scale Reference: Assume 1 block = 0.5 meters. Use this to calculate realistic dimensions for the requested object."*
3. **Forced Object Separation**: Instruct the planner: *"If a part contains multiple mirrored or repeating objects (like wheels or engines), split them into 'Left', 'Right', and 'Center' parts to maximize resolution."*
4. **Origin Offset**: Encourage the planner to start builds at `y=64` (sea level) or higher to avoid "Origin Bias" where it crams everything at `0,0,0`.
