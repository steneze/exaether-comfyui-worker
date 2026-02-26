"""
Scene Selector Node for ComfyUI
Custom node to select scene parameters (camera, lighting, pose, mood) and concatenate descriptions.

Structure:
scenes/
├── default/
│   ├── 01_shot_type.txt
│   ├── 02_camera_angle.txt
│   └── ...
└── [other_presets]/
    └── ...

File format (name;description):
1. Plan américain;american shot, visible from mid-thigh up, cowboy framing
2. Gros plan;close-up shot, head and neck visible, emotional focus
"""

import os
import random

# Path to scenes folder - adjust this to your setup
SCENES_BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "scenes")

# Maximum categories to support
MAX_CATEGORIES = 30


def scan_scenes():
    """
    Scan the scenes folder and return structured data.
    Returns:
        presets: list of preset folder names
        categories: list of all category names across all presets (sorted)
        data: dict of {preset: {category: {display_name: description}}}
    """
    presets = []
    categories = set()
    data = {}
    
    if not os.path.exists(SCENES_BASE_PATH):
        os.makedirs(SCENES_BASE_PATH)
        return presets, [], data
    
    # Scan preset folders
    for preset_name in sorted(os.listdir(SCENES_BASE_PATH)):
        preset_path = os.path.join(SCENES_BASE_PATH, preset_name)
        if not os.path.isdir(preset_path):
            continue
        
        presets.append(preset_name)
        data[preset_name] = {}
        
        # Scan category files in this preset
        for filename in sorted(os.listdir(preset_path)):
            if not filename.endswith('.txt'):
                continue
            
            category_name = filename[:-4]  # Remove .txt
            categories.add(category_name)
            data[preset_name][category_name] = {}
            
            # Parse the file
            filepath = os.path.join(preset_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or ';' not in line:
                            continue
                        parts = line.split(';', 1)
                        display_name = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""
                        data[preset_name][category_name][display_name] = description
            except Exception as e:
                print(f"[SceneSelector] Error reading {filepath}: {e}")
    
    return presets, sorted(categories), data


# Scan at module load
PRESETS, CATEGORY_NAMES, DATA = scan_scenes()
CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]


def get_options_for_category(cat_name, presets, data):
    """Build dropdown options for a category."""
    options = ["(none)"]
    for preset_name in presets:
        if preset_name in data and cat_name in data[preset_name]:
            for display_name in sorted(data[preset_name][cat_name].keys()):
                options.append(f"[{preset_name}] {display_name}")
    return options


class SceneSelector:
    """
    A node that allows selecting scene parameters from organized text files
    and outputs a concatenated description string.
    
    Categories include: shot type, camera angle, lighting, pose, mood, etc.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        # Rescan to get fresh data
        global PRESETS, CATEGORY_NAMES, DATA
        PRESETS, CATEGORY_NAMES, DATA = scan_scenes()
        CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
        
        inputs = {
            "required": {
                "randomize": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {}
        }
        
        # Add a dropdown for each category found
        for cat_name in CATEGORY_NAMES:
            options = get_options_for_category(cat_name, PRESETS, DATA)
            inputs["optional"][cat_name] = (options, {"default": "(none)"})
        
        return inputs
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_segment",)
    FUNCTION = "build_prompt"
    CATEGORY = "prompt/scene"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs.get("randomize", False):
            return kwargs.get("seed", 0)
        return float("NaN")
    
    def build_prompt(self, randomize=False, seed=0, **kwargs):
        """
        Build the concatenated prompt from selected items.
        If randomize=True, categories not set to (none) will be randomized.
        """
        descriptions = []
        
        if randomize:
            random.seed(seed)
        
        for cat_name, selection in kwargs.items():
            if selection == "(none)" or not selection:
                continue
            
            if not selection.startswith("["):
                continue
                
            try:
                bracket_end = selection.index("]")
                item_preset = selection[1:bracket_end]
                display_name = selection[bracket_end+2:]
            except (ValueError, IndexError):
                continue
            
            # If randomize, pick random item from same preset and category
            if randomize:
                if item_preset in DATA and cat_name in DATA[item_preset]:
                    available_items = list(DATA[item_preset][cat_name].keys())
                    if available_items:
                        display_name = random.choice(available_items)
            
            # Get the description
            if item_preset in DATA and cat_name in DATA[item_preset]:
                if display_name in DATA[item_preset][cat_name]:
                    desc = DATA[item_preset][cat_name][display_name]
                    if desc:
                        descriptions.append(desc)
        
        result = ", ".join(descriptions)
        return (result,)


class SceneRandomizer:
    """
    A node that outputs random selections for all categories of a given preset.
    Useful for generating completely random scene settings.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        global PRESETS, CATEGORY_NAMES, DATA
        PRESETS, CATEGORY_NAMES, DATA = scan_scenes()
        CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
        
        preset_options = PRESETS if PRESETS else ["default"]
        
        return {
            "required": {
                "preset": (preset_options, {"default": preset_options[0]}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
            "optional": {
                "exclude_categories": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt_segment",)
    FUNCTION = "randomize_all"
    CATEGORY = "prompt/scene"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return kwargs.get("seed", 0)
    
    def randomize_all(self, preset, seed=0, exclude_categories=""):
        """
        Generate a random selection from all categories for the given preset.
        """
        random.seed(seed)
        descriptions = []
        
        excluded = set()
        if exclude_categories:
            excluded = set(x.strip() for x in exclude_categories.split(","))
        
        if preset not in DATA:
            return ("",)
        
        preset_data = DATA[preset]
        
        for cat_name in sorted(preset_data.keys()):
            if cat_name in excluded:
                continue
            
            items = preset_data[cat_name]
            if items:
                display_name = random.choice(list(items.keys()))
                desc = items[display_name]
                if desc:
                    descriptions.append(desc)
        
        result = ", ".join(descriptions)
        return (result,)


class SceneReloader:
    """
    Utility node to force reload scene data without restarting ComfyUI.
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
    CATEGORY = "prompt/scene"
    
    @classmethod
    def IS_CHANGED(cls, reload):
        return float("NaN")
    
    def reload(self, reload):
        if reload:
            global PRESETS, CATEGORY_NAMES, DATA
            PRESETS, CATEGORY_NAMES, DATA = scan_scenes()
            CATEGORY_NAMES = CATEGORY_NAMES[:MAX_CATEGORIES]
            
            total_items = sum(
                len(items) 
                for preset_data in DATA.values() 
                for items in preset_data.values()
            )
            
            status = f"Reloaded:\n"
            status += f"  Presets: {', '.join(PRESETS)}\n"
            status += f"  Categories: {len(CATEGORY_NAMES)}\n"
            status += f"  Total items: {total_items}"
            return (status,)
        return ("No reload",)


# Node registration
NODE_CLASS_MAPPINGS = {
    "SceneSelector": SceneSelector,
    "SceneRandomizer": SceneRandomizer,
    "SceneReloader": SceneReloader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SceneSelector": "🎬 Scene Selector",
    "SceneRandomizer": "🎲 Scene Randomizer",
    "SceneReloader": "🔄 Scene Reloader",
}
