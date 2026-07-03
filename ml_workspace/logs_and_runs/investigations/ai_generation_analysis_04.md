# Investigation 04: Nose/Cockpit Detail and DSL-Parser Mismatch

## Date: 2026-04-16

### Input: Sub-agent Response for 'Nose and Cockpit Detail'
```
palette
S = minecraft:light_gray_concrete
T = minecraft:gray_concrete
G = minecraft:cyan_stained_glass
A = minecraft:yellow_concrete
end_palette
fill 4 4 22 14 10 34 S
carve 5 5 23 13 9 33
fill 5 5 24 13 9 32 S
...
fill 8 7 27 10 8 29 G
...
fill 4 6 25 14 6 31 A
```

---

### Analysis

#### 1. Vertical Resolution Trap
- **The Observation**: The nose of a plane is being built between `y=4` and `y=10`. 
- **The Problem**: This confirms a total vertical span of only 6 blocks. You cannot create a realistic "nose cone" curve with 6 blocks of height. The AI is still thinking in "Miniature" mode.

#### 2. DSL Logic Bug (The "S/T/G" Issue)
- **The Observation**: The AI is correctly attempting to use palette characters (`S`, `T`, `G`, `A`) as the material argument for the `fill` command.
- **The Problem**: Our current `OpenAISchematicDSLParser.java` is bugged. It only looks up the `palette` map during `layer_y` processing. For `fill`, `set`, and `box`, it passes the string (e.g., "S") to `parseState()`, which doesn't have access to the palette.
- **The Result**: The parser fails to find a block named "S", defaults to the fallback (Stone), and the user sees a build made entirely of stone instead of the intended colors.

#### 3. Sophisticated Geometric Intent
- **The Success**: The AI is using `carve` to hollow out the nose before refilling it, which shows it *wants* to build complex internal structures. 
- **The Failure**: The tool (the parser) is failing to interpret the AI's shorthand, and the scale is too small for the geometry to resolve into anything but a box.

---

### Refined Brainstormed Solutions
1. **Global Palette Resolution**: Fix `OpenAISchematicDSLParser` so that `set`, `fill`, and `box` check the `palette` map before attempting to resolve a raw Minecraft ID.
2. **Resolution Multiplier**: We should consider adding a "Resolution Multiplier" to the UI. If the user selects "High Detail," we tell the AI to multiply all its planned dimensions by 2x or 3x.
3. **Minimum Volume Prompting**: Explicitly tell the AI: *"Avoid small volumes. If an object is important (like a Cockpit), ensure it is at least 15 blocks wide to allow for glass and interior detail."*
4. **Coordinate Mapping Confirmation**: Reinforce that `0,0,0` is the corner of the schematic, but encourage it to build at a higher offset for clarity.
