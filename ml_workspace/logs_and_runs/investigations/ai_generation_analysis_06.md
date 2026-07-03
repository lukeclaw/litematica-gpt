# Investigation 06: Fuselage Hollowing and Structural Overlap

## Date: 2026-04-16

### Input: Sub-agent Response for 'Fuselage'
```
palette
# = minecraft:light_gray_concrete
= = minecraft:gray_concrete
w = minecraft:light_blue_stained_glass
c = minecraft:cyan_stained_glass
end_palette

fill 8 4 20 40 10 36 minecraft:light_gray_concrete
carve 9 5 21 39 9 35
fill 8 4 20 40 4 36 minecraft:light_gray_concrete
...
fill 8 5 20 11 9 22 minecraft:cyan_stained_glass
...
```

---

### Analysis

#### 1. The "Box" Architecture
- **The Observation**: The fuselage is created by filling a massive 32x6x16 solid block of concrete and then carving out the center.
- **The Problem**: While "fill and carve" is a valid way to make a room, it creates perfectly sharp 90-degree corners. Minecraft AI defaults to this because it's the "safest" way to ensure the structure is hollow, but it results in a plane that looks like a shipping container.

#### 2. Resolution Death Spiral
- **The Observation**: Again, the height is capped at **6 blocks** (`y=4` to `y=10`).
- **The Result**: A 6-block high fuselage is too short to have a curved bottom, a curved top, and a row of windows in the middle. The AI is forced to choose between "shape" and "windows," and it's choosing windows, resulting in a flat-roofed box.

#### 3. Redundant Work (Context Waste)
- **The Observation**: The AI is manually drawing 4 individual window panes using `fill` commands.
- **The Problem**: If it used the `layer_y` ASCII map, it could "draw" the side profile of the plane much more intuitively. The fact that it's using raw `fill` for every detail suggests it doesn't "trust" the DSL or finds it too complex for the current scale.

#### 4. Part Overlap Conflict
- **The Observation**: The Fuselage ends at `x=8`. The Nose (from Investigation 04) starts at `x=4`.
- **The Result**: They overlap by 4 blocks. This is actually good for merging, but because both parts are just "Boxes," you end up with a double-thick wall at the junction point rather than a smooth transition.

---

### Final Synthesis of All Issues

After 6 investigations, we have a clear technical debt list:

1.  **[CRITICAL] Parser Bug**: The parser doesn't resolve palette characters (`S`, `#`, etc.) in `fill`/`set`/`box` commands. The AI is forced to use long `minecraft:id` strings, which eats context and leads to generic "Stone" builds when it hallucinates IDs.
2.  **[CRITICAL] Scale Primer**: Our prompt example [0,0,0, 10,20,10] is essentially telling the AI: "Build me a toy." We need to prime it with a [0,0,0, 150,50,100] example.
3.  **[ENHANCEMENT] Geometric Resolution**: We should instruct the AI that "High Effort" implies using at least 15-20 blocks of height for any object meant to be "rounded" or "cylindrical."
4.  **[ENHANCEMENT] DSL Enforcement**: We must strictly forbid the use of raw `minecraft:` IDs in the command body to force the AI to use the palette, which improves its "spatial reasoning" and script efficiency.

---

### Next Steps
1.  Refactor `OpenAISchematicDSLParser.java` to support palette lookup in all commands.
2.  Update `HighEffortAIWorkflow.java` with the "Macro-Scale" prompt and "No Raw IDs" constraint.
3.  Implement a "Detail Multiplier" to scale up the planner's assigned volumes.
