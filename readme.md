# 🏠 Fork U-House Card

> This is a fork of [silasmariusz/fork_u-house_card](https://github.com/silasmariusz/fork_u-house_card).
> It adds unit awareness (°F / mph installs), aspect-ratio sizing so the house is never cropped,
> and entity-driven image overlays (e.g. a vehicle on the driveway while someone is home).
> All credit for the card itself goes upstream.

![msedge_bNu5APEUJq](https://github.com/user-attachments/assets/8405dc20-4e71-4588-a56a-044292b8ab87)

An isometric, glassmorphism-styled Home Assistant Lovelace card: your house rendered per season,
time of day and weather, with animated rain, snow, fog, stars and clouds on top, room temperature
badges, and a one-line "storyteller" advisory built from your weather and air sensors.

"Fork U" means I DON'T FCKING CARE, you have to mod this card as you need. (Weather effects based on Prism).

## ✅ What you need

**Required**

| Thing | Why |
|---|---|
| `weather.*` entity (Met.no, OpenWeatherMap, Google Weather, ...) | Picks the weather variant of the house image, drives the animations and the advisory |
| `sensor.season` from the **Season** integration | Picks the season variant. English and Polish state names are understood |
| `sun.sun` | Day / night switch for the image and the night dimming |
| At least one temperature sensor | The `rooms` list must exist, even with a single entry |
| The house images (see [Images](#images)) | Without them the card is an empty box |

**Optional, but each one unlocks something**

| Entity | Unlocks |
|---|---|
| Cloud coverage sensor (0-100 %) | Cloud density. Without it the sky is cloud-free unless the weather state says otherwise |
| Wind speed + wind bearing sensors | Direction and speed of clouds, rain and snow, and the wind-chill advisory. Falls back to the weather entity's `wind_speed` / `wind_bearing` attributes, then to a fixed westerly breeze |
| UV index sensor | "UV high" advisory above 6 |
| PM2.5 / AQI sensor | Air-quality advisories above 50 and 100 |
| Pollen sensor (text `high` / `very_high` / `extreme` / `red`, or a number above 50) | Pollen advisory |
| An `input_boolean` for party / gaming mode | The ambient light overlay |
| `person.*` or any other entity | Image overlays (vehicles on the driveway, lights, decorations) |

## ✨ Features

* **🧠 Smart advisor:** one sentence built from storms, air quality, pollen, rain or snow in the next three forecast slots, current rain or snow, UV, wind chill, cold or heat, in that priority order. Falls back to a "comfortable conditions" line.
* **🌦️ Prism weather engine:** rain and snow particles, stars on clear nights, fog on foggy weather and on rainy or cloudy nights, clouds scaled by coverage, lightning flashes, all steered by real wind data.
* **🌗 Day / night:** the house image switches to its night variant and dims slightly after sunset.
* **🎮 Gaming ambient mode:** a toggleable magenta / cyan / purple light overlay.
* **🌡️ Room badges:** positionable temperature badges, coloured cold / optimal / warm / hot.
* **🚗 Overlays:** extra images shown while an entity is in a given state, with weather and day / night variants.
* **🌍 English and Polish** text.

## 📥 Installation

### HACS (recommended)

1. HACS → **Frontend** → three-dot menu → **Custom repositories**.
2. Add `https://github.com/muhlman/house_card`, category **Lovelace**, then **Download**.
3. HACS registers the resource and installs to `config/www/community/house_card/`. Hard-refresh your browser.

### Manual

1. Copy `fork_u-house_card.js` to `config/www/house_card/fork_u-house_card.js`.
2. Dashboard → Resources → add `/local/house_card/fork_u-house_card.js` as a **JavaScript module**.
3. Set `image_path: /local/house_card/images/` in the card config (see below).

## ⚙️ Configuration

Every key the card reads is listed here. Anything else in the YAML is ignored.

```yaml
type: custom:fork-u-house-card
language: en                      # en (default) or pl

# --- Images ---
image_path: /local/community/house_card/images/   # default; folder holding the PNGs below

# Weather variants are used automatically whenever the file exists, so just add images.
# To stop one from showing, turn it off (key order can be img_{season}_{time}_{weather}
# or img_{season}_{weather}_{time}):
# img_winter_night_hail: false     # never show winter_hail_night.png
# auto_weather_images: false       # upstream behaviour: only images with an explicit true are used

# --- Entities ---
weather_entity: weather.forecast_home          # required
season_entity: sensor.season                   # required
sun_entity: sun.sun                            # default sun.sun
cloud_coverage_entity: sensor.openweathermap_cloud_coverage
wind_speed_entity: sensor.wind_speed
wind_direction_entity: sensor.wind_bearing
uv_entity: sensor.uv_index
aqi_entity: sensor.waqi_pm2_5
pollen_entity: sensor.pollen_level
party_mode_entity: input_boolean.gaming_mode

# --- Units (normally auto-detected from Home Assistant) ---
# temperature_unit: "°F"          # or "°C"; include the degree sign
# wind_speed_unit: mph            # km/h (default), mph, m/s, kn

# --- Sizing ---
# aspect_ratio: "4:3"             # default; the card sets its height from its width
# height: 350                     # fixed height in px instead (the original, cropping behaviour)
# image_fit: contain              # letterbox instead of cover

# --- Testing ---
# test_weather_state: snowy       # forces the ANIMATIONS and advisory only; the house image
                                  # still follows weather_entity. Remove when done.

# --- Room badges (required, at least one) ---
# x / y are percentages of the card, 0,0 top-left; the badge is centred on the point.
rooms:
  - name: Living Room
    entity: sensor.living_room_temperature
    x: 50
    y: 70
    weight: 1                     # 0 excludes the room from the home median (see note)
  - name: Outside
    entity: sensor.outdoor_temperature
    x: 50
    y: 8
    weight: 0

# --- Overlays (optional) ---
overlays:
  - entity: person.one
    image: vehicle_1_{weather}_{time}.png
  - entity: person.two
    image: vehicle_2_{weather}_{time}.png
    states: [home]                # default "home"; a list is accepted
```

Notes:

* `title` is accepted but not displayed.
* The home-median pill that `weight` feeds is hidden by the card's CSS, so `weight` has no
  visible effect unless you re-enable `.median-pill`.
* Thresholds are defined in °C and km/h. The card reads Home Assistant's unit system and
  converts automatically, so °F / mph installs classify correctly and the advisory prints the
  native unit. Use the `*_unit` keys only if a sensor reports in a different unit than Home
  Assistant's setting.

### How the house image is chosen

1. **Christmas** - from 14 December to 14 January the image is always `winter_xmas_{day|night}.png`.
2. **Season** from `season_entity`, **time** from `sun_entity` (`below_horizon` = night).
3. **Weather** from `weather_entity`, mapped to a filename suffix:

   | Home Assistant state | Suffix |
   |---|---|
   | `lightning`, `lightning-rainy` | `lightning` |
   | `rainy`, `pouring` | `rainy` |
   | `snowy`, `snowy-rainy` | `snowy` |
   | `hail` | `hail` |
   | `fog` | `fog` |
   | `sunny`, `clear-night`, `cloudy`, `partlycloudy`, `windy`, `exceptional` | *(none - base image)* |

4. If the suffix is set, the card tries `{season}_{suffix}_{time}.png` and shows it when the file
   exists, otherwise `{season}_{time}.png`. Setting `img_{season}_{time}_{suffix}: false` skips
   the weather image for that combination; `auto_weather_images: false` switches to the
   upstream opt-in behaviour where only flags set to `true` are used. Existence is checked by
   loading the image, and misses are remembered per page load, so reload after adding files.

### Overlays

Overlays are full-frame PNGs with transparency, the **same pixel size and camera as the house
images**, drawn between the house and the weather effects while their entity is in one of the
configured states. The example above puts a vehicle on the driveway while a person is home, but
any entity works: a lit porch while a light is on, a bike while its tracker is home, decorations
while an `input_boolean` is set.

Filename tokens: `{time}` → `day` / `night`; `{weather}` → the suffix from the table above
(empty for clear or cloudy); `{season}` → `spring` / `summer` / `autumn` / `winter`. Missing
variants fall back: the weather token is dropped first, then the season. So on a snowy winter
night `vehicle_1_{season}_{weather}_{time}.png` tries `vehicle_1_winter_snowy_night.png`,
`vehicle_1_snowy_night.png`, `vehicle_1_winter_night.png`, `vehicle_1_night.png`. Only the plain
day and night files are required. Bare filenames resolve against `image_path`; paths starting
with `/` or `http` are used as-is. Misses are remembered per page load, so reload after adding files.

## Images

All images share one frame: same camera, position and scale as the master reference, 4:3
(the originals are 1448 × 1086), solid dark background for the houses, transparent background
for overlays. The full set the card can request is **50 files**:

| Category | Count | Files |
|---|---|---|
| Base | 8 | `{season}_{day\|night}.png` - also used for cloudy and partly cloudy |
| Weather | 40 | `{season}_{rainy\|snowy\|fog\|lightning\|hail}_{day\|night}.png` |
| Christmas | 2 | `winter_xmas_day.png`, `winter_xmas_night.png` |

Every weather image is optional: if a file is missing the base image is used, and any one can be
switched off with its `img_*: false` flag.

Overlay sets are per overlay, with only the plain day and night files required:
`vehicle_1_day.png`, `vehicle_1_night.png`, plus any of `vehicle_1_{rainy|snowy|fog|lightning|hail}_{day|night}.png`.

> The bundled generator (`image_generation/`, Colab notebook) predates the hail variants and also
> produces `*_overcast_*` and `gaming_*` files that the card never requests. Add hail prompts if you
> want them, and ignore the overcast and gaming output.

## 🖼️ Image Generation Workflow

### 🚀 Easy Generation with Google Colab (Recommended)

Generate all required house assets for free using Google's cloud infrastructure and the Gemini API. No installation required on your computer.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/muhlman/house_card/blob/main/colab_generator/generate_house_assets.ipynb)

**Steps:**
1. Click the **Open in Colab** button above.
2. Get a free API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Upload photos of your house when prompted.
4. Run the notebook (select `gemini-2.5-flash-image` for **Free Tier** generation).

---

### Local Generation (Advanced)

For automated or semi-automated generation using **Gemini 3 Pro** locally, use the `image_generation/` folder and the `generate_house_images.py` script.

### Output files

See [Images](#images) above for the full list of 50 files the card can use. The generator
covers 42 of them (no hail) and additionally emits overcast and gaming variants the card ignores.

### Workflow

1. **Reference Images** – Place photos of your house in `image_generation/reference/` (Street View, Satellite).
2. **Master** – Generate the master reference image (Summer, Day, Sunny) and save as `image_generation/master/_master_reference.png`.
3. **Variants** – Run the script (`python generate_house_images.py`) or use `--export-prompts` to export prompts for manual use in [Gemini](https://gemini.google.com).
4. **Results** – Copy `image_generation/output/*.png` to the folder your `image_path` points at (default `config/www/community/house_card/images/`).

Details: [image_generation/README.md](image_generation/README.md)


## Note for me (reddit questions) answer:

To be honest this is only the one thing fine I was looking for years and finally it was even coded by AI. I did my changes ofcourse and fixes

First I used google street view to take screenshot of my house The Google Maps satellite view to capture roof of my house

I used only free version of Gemini and asked to generate me Sims4 and Sim City like but modern 3d isometric asset of my home in weather and season condition: xxxxx

Where xxx is winter/autumn/spring/summer (add season integration in ha first) Where xxx also contains day and night to generate lights on from the window rooms (you need night shade sensor or use sun sensor from integration) Basically at this step you don’t need to do EXTRAS!!!! I recommend to do this after a week after fine tuning ;). Go to CONTINUE part

EXTRAS generate above with fog using clouds around house for each season and day/night, also rainy useful for spring time and autumn with orange/brown 🍂🍁 around the house

EXTRA2: ask for Xmas season fun things like add Santa snowing from the roof, penguins and iglo on front of your house

EXTRA3: immersive mode, kids birthdays: asked to do synthwave colors, reflection, kid playing on sofa with a gamepad controller, flying Delorin from Back to the Future with lights on and big screen for my kiddo

CONTINUE You are almost done. Download your graphics and move now to free ChatGPT, create a prompt: Asked Gemini with PROMPT written bellow to generate images of my house, but the resolution is too low. (Prompt you used) and that’s all (attach images from Gemini)

You have graphics now. Nice.

Fork my repo on GitHub! Necessary because would be nice if you could edit text strings to much your requirements. If you are newbie use GitHub by web to fork and later to edit files and commit changes - seriously super easy.

https://github.com/silasmariusz/fork_u-house_card

Enjoy


# **🚀 AI ASSET GENERATOR**
> [!TIP]
> 
> You don't need to manually create 40+ images! 
> We have created a **Free AI Tool** that generates all weather, season, and day/night variants for you in minutes.
> 
> [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/muhlman/house_card/blob/main/colab_generator/generate_house_assets.ipynb) <br> *(Click above to start generating for free!)*
>
> Howto:
> ![ezgif-84e148d15543d035](https://github.com/user-attachments/assets/97116b93-1bc0-44ff-9ddd-b01cb8389c41)
>
> Result:
> <img width="1344" height="768" alt="winter_lightning_day" src="https://github.com/user-attachments/assets/26b3a9fa-f3ad-48c3-9ec6-ea43631a1614" />
>
> Source data (google maps, and streatview)
> <img width="646" height="349" alt="roof" src="https://github.com/user-attachments/assets/5029ba36-28d9-4630-8d0a-cd20161ad65e" />
![optional](https://github.com/user-attachments/assets/c6e87b26-6a0a-4e23-b5ea-b67d547e5c3e)
![ang3](https://github.com/user-attachments/assets/ccdf5ff7-f45f-4761-a081-9e5d279f9381)
![ang2](https://github.com/user-attachments/assets/02c2b669-5126-41c8-9b81-3aa998973e4f)
![ang1](https://github.com/user-attachments/assets/30630e89-f732-4a04-8e5a-631dcc8be960)


