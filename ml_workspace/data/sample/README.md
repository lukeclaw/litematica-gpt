# Raw data sample

This folder holds a **small representative sample** of the raw training corpus so the DSL format is
visible in the repo. The full corpus (~10 GB of scraped Minecraft schematics converted to DSL,
43k+ files) is kept local and is **not** committed — see [MODELS.md](../../../MODELS.md).

## Contents

`dsl/` — six DSL files from the `<10 KB` filtered set (`dsl_10kb`), spanning a range of build types:

| File | Kind |
|------|------|
| `10 - admin shoppe.txt` | small shop building |
| `10002 - Iron Piston Doors.txt` | redstone contraption |
| `2831 - Modern House #5.txt` | residential |
| `10934 - Birch House With Windows.txt` | residential |
| `4271 - AUTO Potion brewer.txt` | functional / redstone |
| `11577 - medieval tavern.txt` | themed building |

## Pipeline (full set, local)

```
data/raw/dataset/dsl/          raw scraped schematics -> DSL (43k files)
data/raw/dataset/dsl_10kb/     filtered to <10 KB (fits LLM context)
data/processed/mlx_*/          final train/valid JSONL pairs (committed)
```

The `data/processed/` JSONL pairs (the actual fine-tuning datasets) **are** committed to this repo.
