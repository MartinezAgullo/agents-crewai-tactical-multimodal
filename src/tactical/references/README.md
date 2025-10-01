
# Reference Images

This directory contains visual reference materials for entity classification.

## Purpose

Provides example images of uniforms, insignia, and equipment patterns to support the Classification Reference Tool in identifying Friend, Foe, Civilian, and Unknown entities.

## Structure

```
references/
└── insignia/
├── friends/      # Allied force insignia (NATO patches, UN helmets, friendly national flags)
└── foes/         # Hostile force insignia (enemy patches, militant group symbols)
```

## Usage

Reference image paths are configured in `src/tactical/config/classifications.yaml`. The Classification Reference Tool uses these images to provide visual context when classifying detected entities from field intelligence.

## Adding References

1. Place images in the appropriate subdirectory (`friends/` or `foes/`)
2. Update `classifications.yaml` with the new image path
3. Use descriptive filenames (e.g., `nato_flag_patch.jpg`, `hostile_group_a_symbol.jpg`)

## Note

These references are supplementary visual aids. The primary classification logic is based on observable characteristics documented in `classifications.yaml`.

