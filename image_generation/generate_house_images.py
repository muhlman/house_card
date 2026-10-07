#!/usr/bin/env python3
"""
Generate isometric house images for Fork U-House Card using Gemini 3 Pro Image API.
"""

import argparse
import os
import sys
import io
import shutil
import time
from pathlib import Path

# Force line buffering for stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR / "reference"
MASTER_DIR = SCRIPT_DIR / "master"
OUT_DIR = SCRIPT_DIR / "output"

# Base prompt rules (attached to every request)
BASE_RULES = """
RULES (CAMERA – MANDATORY):
- VIEW: STRICT ISOMETRIC ONLY (SimCity / The Sims style).
- Isometric = equal angles, parallel lines stay parallel.
- The house and plot must be shown in this fixed isometric projection. NEVER render from a different angle.
- MARGINS: STRICT 15% Left, 15% Right, 5% Top, 15% Bottom. The house asset must be perfectly centered within these margins, with the entire glassmorphism base visible. WEATHER EFFECTS (snow, leaves, rain, fog) CAN EXTEND BEYOND THESE MARGINS.
- ASPECT RATIO: 3:2.

RULES (VISUAL STYLE: EPIC 2030 HIGH-FIDELITY ASSET):
- Style: Ultra-high-fidelity 3D asset, "SimCity 2030" / "The Sims 5" aesthetic.
- Lighting: DRAMATIC, CINEMATIC, HIGH CONTRAST. Intense golden hour sun shafts (day) or deep navy/cyan nocturnal tones (night). SUN SHAFTS MUST ONLY BE VISIBLE ON THE ASSET, NEVER ON THE DARK BACKGROUND.
- Effects: Volumetric God rays (ONLY ON THE ASSET, NO RAYS ON THE BLACK BACKGROUND), soft bloom, rich ray-traced reflections on car paint, glass base, and wet surfaces.
- Materiality: Hyper-realistic textures. A thick, multi-layered Glassmorphism base plate at the very bottom, with soil/grass on top.
- Background: Solid #121212 for perfect cutout.
- Quality: 4K RAW, maximum sharpness, zero blur.

RULES (STRICT FIDELITY TO ARCHITECTURE):
- CONSISTENCY: Keep geometry, camera angle, and scale 100% IDENTICAL to the master reference.
- Use the provided reference images ONLY for geometry, angle, and architectural details.
"""

WEATHER_RULES = {
    "sunny": "Cloudless sky: Plot highly illuminated by golden sun rays.",
    "partly_cloudy": "Partly cloudy.",
    "overcast": "Overcast and gloomy.",
    "rainy": "Heavy rain: Draw a downpour in front of the house on the plot - light reflections reflecting on the plot.",
    "snowy": "Snowing: Draw intense snowfall in front of the house on the plot - light reflections reflecting on the plot.",
    "hail": "Hailstorm: Large chunks of ice on the ground instead of snow. Random puddles/patches of water under the ice.",
    "lightning": "Thunderstorms: Draw strong lightning bolts in the sky. House strongly overexposed by lightning flashes. Shadows cast from a DIFFERENT side than master.",
    "fog": "Fog: Draw fog, a delicate cloud or slight smoke in front of house and car.",
}

XMAS_VARIANTS = {
    "aurora": "Aurora Borealis (Northern Lights) in the sky. Snowman with colorful lights in garden.",
    "penguins": "Penguins sliding on the snowy plot. Igloo built in the garden.",
    "santa": "Santa Claus sliding down the snowy roof. Christmas lights on eaves.",
    "stuck_santa": "Santa stuck in the chimney (legs sticking out). Reindeer parked on the roof.",
    "griswold": "Giant Christmas tree in garden. House decorated with excessive amounts of lights (Griswold style).",
}

GAMING_MODES = {
    "synthwave": "Synthwave style: Neon purples/pinks, grid lines, retro-future vibe. Flying DeLorean parked in front.",
    "cyberpunk": "Cyberpunk style: High-tech low-life, neon signs, rain, dark gritty atmosphere. Flying DeLorean parked in front.",
    "matrix": "Matrix style: Green code rain, digital artifacts. Half the asset in green wireframe vector style. 1990 Lamborghini Countach parked in front.",
    "mario": "Mario Bros World style: Green pipe, gold coins/stars on roof, beanstalk to sky. Mario & Luigi grilling meat in front of the house.",
    "xbox_kid": "Small astronaut kid (big head) playing Xbox on a red semi-transparent sofa in front of the house. Projector screen.",
}

SEASONS = ["winter", "spring", "summer", "autumn"]
TIMES = ["day", "night"]

def get_base_prompt_for_master() -> str:
    return f"""Task: Create a "SimCity 2030" style 3D asset of the house.
STRICT ISOMETRIC VIEW. 4K RAW.
{BASE_RULES}
VISUALS: Golden hour, strong sun shafts, high contrast HDR. Manicured lawn on thick glass base.
Specific for THIS image: Summer, Day, Sunny, bright.
"""

def get_prompt_for_variant(season: str, time_of_day: str, weather: str = "sunny", extras: str = "") -> str:
    season_ground = {
        "winter": "snow only, no grass",
        "spring": "spring grass with flowers",
        "summer": "manicured lawn",
        "autumn": "yellow-orange-brown leaves on grass",
    }
    night_rule = "Apply night colors to plot. Lights on inside house. Illuminate driveway." if time_of_day == "night" else ""
    
    weather_desc = WEATHER_RULES.get(weather, "")
    ground_desc = season_ground.get(season, "lawn")
    
    return f"""Reference: Master. Same isometric angle, position, scale.
{BASE_RULES}
Specific for THIS request:
- Season: {season.capitalize()}
- Time: {time_of_day.capitalize()}
- Weather: {weather_desc}
- Ground: {ground_desc}
{night_rule}
{extras}
IDENTICAL camera angle and position. 4K RAW. No watermark.
"""

def generate_with_gemini(prompt: str, reference_images: list[Path], output_path: Path, model_name: str = "models/gemini-3-pro-image") -> bool:
    try:
        import google.generativeai as genai
    except ImportError:
        print("Error: Install google-generativeai")
        return False

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        return False
        
    genai.configure(api_key=api_key)
    
    try:
        model = genai.GenerativeModel(model_name)
        contents = [prompt]
        for img_path in reference_images:
            if img_path.exists():
                from PIL import Image
                contents.append(Image.open(img_path))

        response = model.generate_content(contents)
        if not response.candidates: return False
            
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                from PIL import Image
                img = Image.open(io.BytesIO(part.inline_data.data))
                output_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(output_path, "PNG")
                return True
        return False
    except Exception as e:
        print(f"API error: {e}")
        return False

def run_gaming_modes(output_dir: Path, master_img: Path, model: str):
    print(f"Generating GAMING modes in {output_dir}...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for mode, desc in GAMING_MODES.items():
        fname = f"gaming_{mode}.png"
        print(f"Generating {fname}")
        generate_with_gemini(desc + "\n" + BASE_RULES, [master_img], output_dir / fname, model)

def run_set(output_dir: Path, master_img: Path, model: str):
    print(f"Generating set in {output_dir}...")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Standard Variants
    for season in SEASONS:
        for time_of_day in TIMES:
            # Sunny base
            fname = f"{season}_{time_of_day}.png"
            print(f"Generating {fname}")
            generate_with_gemini(get_prompt_for_variant(season, time_of_day), [master_img], output_dir / fname, model)
            
            # Weather
            weather_list = ["rainy", "fog", "lightning", "overcast"]
            if season != "summer": weather_list.append("snowy")
            if season != "winter": weather_list.append("hail")
            
            for w in weather_list:
                fname_w = f"{season}_{w}_{time_of_day}.png"
                print(f"Generating {fname_w}")
                generate_with_gemini(get_prompt_for_variant(season, time_of_day, w), [master_img], output_dir / fname_w, model)

    # 2. Xmas Variants
    for name, desc in XMAS_VARIANTS.items():
        for time_of_day in TIMES:
            fname = f"winter_xmas_{name}_{time_of_day}.png"
            print(f"Generating {fname}")
            generate_with_gemini(get_prompt_for_variant("winter", time_of_day, "sunny", desc), [master_img], output_dir / fname, model)

    # 3. Gaming Variants
    run_gaming_modes(output_dir, master_img, model)

def run_phase_master():
    """Generates ONLY the master reference image."""
    output_path = MASTER_DIR / "_master_reference.png"
    prompt = get_base_prompt_for_master()
    
    # Use all images in reference folder
    refs = [p for p in REFERENCE_DIR.glob("*") if p.suffix.lower() in [".jpg", ".png", ".jpeg"]]
    
    if not refs:
        print("Warning: No reference images found in reference/ folder.")
    
    models_to_try = [
        "models/gemini-3-pro-image",
        "models/gemini-2.5-flash-image"
    ]
    
    success = False
    for model_name in models_to_try:
        print(f"Generating MASTER reference to {output_path} using {model_name}...")
        if generate_with_gemini(prompt, refs, output_path, model_name=model_name):
            print(f"Master generation successful with {model_name}.")
            success = True
            break
        else:
            print(f"Failed with {model_name}. Trying next...")
            
    if not success:
        print("All master generation attempts failed.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["master", "base", "weather", "xmas", "gaming", "all", "hires"], required=True)
    args = parser.parse_args()

    # Special handling for master phase
    if args.phase == "master":
        MASTER_DIR.mkdir(parents=True, exist_ok=True)
        run_phase_master()
        return

    master = MASTER_DIR / "_master_reference.png"
    if not master.exists():
        print("Master image not found! Run --phase master first.")
        return

    preview_model = "models/gemini-3-pro-image"
    hires_model = "models/gemini-3-pro-image" # Placeholder, update if a specific hires model is available

    if args.phase == "all":
        run_set(OUT_DIR, master, preview_model)
    elif args.phase == "base":
        # Just base variants logic if needed, for now run_set does all
        run_set(OUT_DIR, master, preview_model)
    elif args.phase == "gaming":
        run_gaming_modes(OUT_DIR, master, preview_model)
    elif args.phase == "hires":
        print("Running Hires generation...")
        run_set(OUT_DIR, master, hires_model)

if __name__ == "__main__":
    main()
