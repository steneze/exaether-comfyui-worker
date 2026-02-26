# ComfyUI Scene Selector

Custom node for managing scene parameters (camera, lighting, pose, mood, environment) with organized text files.

## Installation

1. Copy the `comfyui-scene-selector` folder to `ComfyUI/custom_nodes/`
2. Restart ComfyUI
3. Find nodes under `prompt/scene`:
   - 🎬 Scene Selector
   - 🎲 Scene Randomizer
   - 🔄 Scene Reloader

## Structure

```
comfyui-scene-selector/
├── __init__.py
├── scene_selector.py
├── README.md
└── scenes/
    └── default/
        ├── 01_shot_type.txt
        ├── 02_camera_angle.txt
        ├── 03_camera_position.txt
        ├── 04_framing.txt
        ├── 05_photo_style.txt
        ├── 06_lens_effect.txt
        ├── 07_light_source.txt
        ├── 08_light_direction.txt
        ├── 09_light_quality.txt
        ├── 10_mood.txt
        ├── 11_color_grade.txt
        ├── 12_pose_body.txt
        ├── 13_pose_torso.txt
        ├── 14_pose_head.txt
        ├── 15_gaze_direction.txt
        ├── 16_pose_arms.txt
        ├── 17_pose_hands.txt
        ├── 18_expression_mouth.txt
        ├── 19_expression_eyes.txt
        ├── 20_location_type.txt
        ├── 21_background_style.txt
        └── 22_action_implied.txt
```

## Categories

### Camera & Framing
- **01_shot_type** — full body, waist-up, close-up, detail shots
- **02_camera_angle** — eye level, high, low, dutch angle
- **03_camera_position** — frontal, 3/4, profile, from behind
- **04_framing** — centered, rule of thirds, negative space

### Image Style
- **05_photo_style** — selfie, DSLR pro, candid, editorial, polaroid
- **06_lens_effect** — 85mm, 50mm, wide angle, bokeh, macro

### Lighting
- **07_light_source** — window, golden hour, studio, neon, candle
- **08_light_direction** — front, side, back, Rembrandt, butterfly
- **09_light_quality** — soft, hard, mixed, high key, low key

### Mood & Color
- **10_mood** — intimate, confident, mysterious, playful, intense
- **11_color_grade** — neutral, warm, cool, B&W, cinematic

### Pose
- **12_pose_body** — standing, sitting, lying, kneeling, walking
- **13_pose_torso** — facing camera, turned, twisted, leaning
- **14_pose_head** — straight, tilted, turned, over shoulder
- **15_gaze_direction** — direct, looking away, eyes closed
- **16_pose_arms** — at sides, crossed, on hip, in hair
- **17_pose_hands** — relaxed, holding object, touching face

### Expression
- **18_expression_mouth** — neutral, smile, pout, parted lips
- **19_expression_eyes** — soft, intense, dreamy, seductive

### Environment
- **20_location_type** — apartment, studio, street, beach, café
- **21_background_style** — plain, bokeh, architectural, dark
- **22_action_implied** — static, just arrived, getting ready, candid

## File Format

```
1. Plan américain;american shot, visible from mid-thigh up, cowboy framing
2. Gros plan;close-up shot, head and neck visible, emotional focus
```

- Number and name in French (or any language) for easy selection
- Description in English after semicolon
- One item per line

## Usage

### 🎬 Scene Selector
- Select specific settings for each category
- Enable **randomize** + change **seed** to randomize non-(none) categories
- Output concatenates all selected descriptions

### 🎲 Scene Randomizer
- Select a preset
- All categories randomized based on seed
- Use **exclude_categories** to skip specific categories (comma-separated)

## Combining with Wardrobe Selector

Use both nodes together for complete prompt generation:

```
[Wardrobe Selector] → clothing descriptions
[Scene Selector] → camera, lighting, pose descriptions
[String Concat] → combine both
[Your main prompt] → character description + combined string
```
