# Image Generation for Fork U-House Card (local script)

> The Colab notebook in `../colab_generator/` is the maintained generator and covers the full image
> set plus vehicle overlays. This script is the older local path and has not been updated for hail,
> the overcast weather mapping or overlays.

Workflow for generating isometric house graphics using Gemini 3 Pro API.

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `reference/` | Street View photos, satellite images, and best existing variants (e.g. summer_day_sunny, autumn_day_fog) to use as input |
| `master/` | The canonical master reference image (`_master_reference.png`) – use as strict template for all other variants |
| `output/` | Generated images ready for `images/` folder; copy to `../images/` when complete |
| `prompts/` | Exported prompts (run with `--export-prompts`) for manual use in Gemini web UI |

## Setup

Create a Google API key at <https://aistudio.google.com/apikey>, then:

```bash
pip install -r requirements.txt
export GOOGLE_API_KEY=your_key
```

## Usage

### Option A: API (automated)

1. Place reference photos in `reference/` (house at Zyndrama 52, 33-300 Nowy Sącz).
2. Phase 1: `python generate_house_images.py --phase master` – generates master. Place result in `master/_master_reference.png` if generated elsewhere.
3. Phases 2–4: `python generate_house_images.py --phase base`, `--phase weather`, `--phase xmas` (or `--phase all`).
4. Copy `output/*.png` to `../images/` for the card to use.

**Note:** Standard Gemini API models (gemini-1.5, gemini-2.0) are text-only. For image generation use Vertex AI with `gemini-3-pro-image` or Imagen, or run prompts manually (Option B).

### Option B: Manual (prompts export)

1. Run `python generate_house_images.py --export-prompts` to export all 43 prompts to `prompts/`.
2. Open each `.md` file, copy the prompt, attach the indicated images in [Gemini](https://gemini.google.com) or Vertex AI.
3. Save generated images to `output/` with the filename from the prompt header.

## Required Output Files (42 total)

- **Base**: winter_day, winter_night, spring_day, spring_night, summer_day, summer_night, autumn_day, autumn_night
- **Weather**: `{season}_{rainy|snowy|fog|lightning}_{day|night}` for each season
- **Xmas**: winter_xmas_day, winter_xmas_night
