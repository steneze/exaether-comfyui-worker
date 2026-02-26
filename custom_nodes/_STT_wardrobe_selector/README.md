# ComfyUI Wardrobe Selector

Custom node for managing character wardrobes with organized text files.

## Installation

1. Copy the `comfyui-wardrobe-selector` folder to `ComfyUI/custom_nodes/`
2. Restart ComfyUI
3. Find the node under `prompt/wardrobe` → "👗 Wardrobe Selector"

## Structure

```
comfyui-wardrobe-selector/
├── __init__.py
├── wardrobe_selector.py
├── README.md
└── wardrobe/
    ├── Elise_byday/
    │   ├── tops.txt
    │   ├── bottoms.txt
    │   ├── shoes.txt
    │   └── hairstyles.txt
    ├── Elise_bynight/
    │   └── ...
    └── [OtherPersona]/
        └── ...
```

## File Format

Each `.txt` file contains items in format `name;description`:

```
Blouse soie blanche;elegant white silk blouse with small mother-of-pearl buttons, relaxed fit
T-shirt noir;fitted black cotton t-shirt with subtle boat neckline, simple and clean
Pull cachemire;cream cashmere crewneck sweater, fine knit, relaxed fit
```

- **name**: Display name shown in dropdown (French or any language)
- **description**: Full prompt description (English recommended for Flux/SDXL)
- Separated by semicolon `;`
- One item per line

## Usage

1. **persona_filter**: Select a persona folder to filter items (or "(none)" to see all)
2. **Category dropdowns**: Each `.txt` file becomes a dropdown
3. **Selection format**: `[PersonaName] ItemName`
4. **Output**: Concatenated descriptions separated by `, `

### Example

Selections:
- persona_filter: `Elise_byday`
- tops: `[Elise_byday] Blouse soie blanche`
- bottoms: `[Elise_byday] Jean slim indigo`
- shoes: `(none)`

Output:
```
elegant white silk blouse with small mother-of-pearl buttons, relaxed fit, high-waisted slim dark indigo jeans, clean lines, no distressing
```

## Adding New Items

1. Edit the `.txt` files in the wardrobe folder
2. Add node "🔄 Wardrobe Reloader" to your workflow and run it
3. Or restart ComfyUI
4. Refresh the page (F5)

## Adding New Personas

1. Create a new folder in `wardrobe/` (e.g., `Rosa_byday/`)
2. Add `.txt` files with items
3. Restart ComfyUI

## Tips

- Use consistent category names across personas (e.g., all have `tops.txt`, `bottoms.txt`)
- Keep descriptions detailed for generation consistency
- Use `(none)` to skip categories you don't need
- The persona_filter helps you focus on one character at a time
