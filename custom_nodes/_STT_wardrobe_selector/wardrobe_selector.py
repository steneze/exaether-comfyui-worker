"""
Wardrobe Selector Node for ComfyUI
Custom node to select clothing items from organized text files and concatenate descriptions.

Structure:
wardrobe/
├── Elise_byday/
│   ├── 01_hairstyle.txt
│   ├── 02_makeup.txt
│   └── ...
└── Elise_bynight/
    └── ...

File format (name;description):
1. Blouse soie blanche;elegant white silk blouse with small mother-of-pearl buttons
2. T-shirt noir;fitted black cotton t-shirt with subtle boat neckline
"""

import os
import random

# Path to wardrobe folder - adjust this to your setup
WARDROBE_BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wardrobe")

# Maximum categories to support
MAX_CATEGORIES = 30


def scan_wardrobe():
    """
    Scan the wardrobe folder and return structured data.
    Returns:
        personas: list of persona folder names
        categories: list of all category names across all personas (sorted)
        data: dict of {persona: {category: {display_name: description}}}
    """
    personas = []
    categories = set()
    data = {}
    
    if not os.path.exists(WARDROBE_BASE_PATH):
        os.makedirs(WARDROBE_BASE_PATH)
        return personas, [], data
    
    # Scan persona folders
    for persona_name in sorted(os.listdir(WARDROBE_BASE_PATH)):
        persona_path = os.path.join(WARDROBE_BASE_PATH, persona_name)
        if not os.path.isdir(persona_path):
            continue
        
        personas.append(persona_name)
        data[persona_name] = {}
        
        # Scan category files in this persona
        for filename in sorted(os.listdir(persona_path)):
            if not filename.endswith('.txt'):
                continue
            
            category_name = filename[:-4]  # Remove .txt
            categories.add(category_name)
            data[persona_name][category_name] = {}
            
            # Parse the file
            filepath = os.path.join(persona_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or ';' not in line:
                            continue
                        parts = line.split(';', 1)
                        display_name = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""
                        data[persona_name][category_name][display_name] = description
            except Exception as e:
                print(f"[WardrobeSelector] Error reading {filepath}: {e}")
    
    return personas, sorted(categories), data


# Scan at module load
PERSONAS, CATEGORY_NAMES, DATA = scan_wardrobe()
CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]


def get_options_for_category(cat_name, personas, data):
    """Build dropdown options for a category."""
    options = ["(none)"]
    for persona_name in personas:
        if persona_name in data and cat_name in data[persona_name]:
            for display_name in sorted(data[persona_name][cat_name].keys()):
                options.append(f"[{persona_name}] {display_name}")
    return options


def get_options_for_category_filtered(cat_name, persona_filter, personas, data):
    """Build dropdown options for a category, filtered by persona."""
    options = []
    if persona_filter and persona_filter != "(none)":
        # Only items from selected persona
        if persona_filter in data and cat_name in data[persona_filter]:
            for display_name in sorted(data[persona_filter][cat_name].keys()):
                options.append(f"[{persona_filter}] {display_name}")
    else:
        # All items from all personas
        for persona_name in personas:
            if persona_name in data and cat_name in data[persona_name]:
                for display_name in sorted(data[persona_name][cat_name].keys()):
                    options.append(f"[{persona_name}] {display_name}")
    return options


class WardrobeSelector:
    """
    A node that allows selecting clothing/styling items from organized text files
    and outputs a concatenated description string.
    
    Items are prefixed with [PersonaName] in dropdowns.
    You can mix items from different personas freely.
    
    Randomize feature: When seed changes and randomize=True, all categories 
    that are not set to (none) will be randomized within the same persona.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # Rescan to get fresh data
        global PERSONAS, CATEGORY_NAMES, DATA
        PERSONAS, CATEGORY_NAMES, DATA = scan_wardrobe()
        CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
        
        persona_options = ["(none)"] + PERSONAS
        
        inputs = {
            "required": {
                "randomize": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "persona_filter": (persona_options, {"default": "(none)"}),
            },
            "optional": {}
        }
        
        # Add a dropdown for each category found
        for cat_name in CATEGORY_NAMES:
            options = get_options_for_category(cat_name, PERSONAS, DATA)
            inputs["optional"][cat_name] = (options, {"default": "(none)"})
        
        return inputs
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_segment",)
    FUNCTION = "build_prompt"
    CATEGORY = "prompt/wardrobe"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # Always refresh when randomize is on or seed changes
        if kwargs.get("randomize", False):
            return kwargs.get("seed", 0)
        return float("NaN")
    
    def build_prompt(self, randomize=False, seed=0, persona_filter="(none)", **kwargs):
        """
        Build the concatenated prompt from selected items.
        
        If randomize=True, categories not set to (none) will be randomized
        to a random item from the same persona (or filtered persona).
        """
        descriptions = []
        
        # Set random seed for reproducibility
        if randomize:
            random.seed(seed)
        
        for cat_name, selection in kwargs.items():
            if selection == "(none)" or not selection:
                continue
            
            # Parse selection: "[PersonaName] DisplayName"
            if not selection.startswith("["):
                continue
                
            try:
                bracket_end = selection.index("]")
                item_persona = selection[1:bracket_end]
                display_name = selection[bracket_end+2:]  # Skip "] "
            except (ValueError, IndexError):
                continue
            
            # If randomize is enabled, pick a random item from the same category
            if randomize:
                # Determine which persona to use for randomization
                if persona_filter != "(none)":
                    random_persona = persona_filter
                else:
                    random_persona = item_persona
                
                # Get available options for this category and persona
                if random_persona in DATA and cat_name in DATA[random_persona]:
                    available_items = list(DATA[random_persona][cat_name].keys())
                    if available_items:
                        display_name = random.choice(available_items)
                        item_persona = random_persona
            
            # Get the description
            if item_persona in DATA and cat_name in DATA[item_persona]:
                if display_name in DATA[item_persona][cat_name]:
                    desc = DATA[item_persona][cat_name][display_name]
                    if desc:
                        descriptions.append(desc)
        
        result = ", ".join(descriptions)
        return (result,)


class WardrobeRandomizer:
    """
    A node that outputs random selections for all categories of a given persona.
    Useful for generating completely random outfits.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        global PERSONAS, CATEGORY_NAMES, DATA
        PERSONAS, CATEGORY_NAMES, DATA = scan_wardrobe()
        CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
        
        persona_options = PERSONAS if PERSONAS else ["(none)"]
        
        return {
            "required": {
                "persona": (persona_options, {"default": persona_options[0]}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "exclude_categories": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_segment",)
    FUNCTION = "randomize_all"
    CATEGORY = "prompt/wardrobe"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return kwargs.get("seed", 0)
    
    def randomize_all(self, persona, seed=0, exclude_categories=""):
        """
        Generate a random selection from all categories for the given persona.
        """
        random.seed(seed)
        descriptions = []
        
        # Parse excluded categories
        excluded = set()
        if exclude_categories:
            excluded = set(x.strip() for x in exclude_categories.split(","))
        
        if persona not in DATA:
            return ("",)
        
        persona_data = DATA[persona]
        
        for cat_name in sorted(persona_data.keys()):
            # Skip excluded categories
            if cat_name in excluded:
                continue
            
            items = persona_data[cat_name]
            if items:
                display_name = random.choice(list(items.keys()))
                desc = items[display_name]
                if desc:
                    descriptions.append(desc)
        
        result = ", ".join(descriptions)
        return (result,)


class WardrobeReloader:
    """
    Utility node to force reload wardrobe data without restarting ComfyUI.
    Connect to workflow and run once to refresh.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "reload": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "reload"
    CATEGORY = "prompt/wardrobe"
    
    @classmethod
    def IS_CHANGED(cls, reload):
        return float("NaN")
    
    def reload(self, reload):
        if reload:
            global PERSONAS, CATEGORY_NAMES, DATA
            PERSONAS, CATEGORY_NAMES, DATA = scan_wardrobe()
            CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
            
            total_items = sum(
                len(items) 
                for persona_data in DATA.values() 
                for items in persona_data.values()
            )
            
            status = f"Reloaded:\n"
            status += f"  Personas: {', '.join(PERSONAS)}\n"
            status += f"  Categories: {len(CATEGORY_NAMES)}\n"
            status += f"  Total items: {total_items}"
            return (status,)
        return ("No reload",)


# Node registration
NODE_CLASS_MAPPINGS = {
    "WardrobeSelector": WardrobeSelector,
    "WardrobeRandomizer": WardrobeRandomizer,
    "WardrobeReloader": WardrobeReloader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WardrobeSelector": "👗 Wardrobe Selector",
    "WardrobeRandomizer": "🎲 Wardrobe Randomizer",
    "WardrobeReloader": "🔄 Wardrobe Reloader",
}