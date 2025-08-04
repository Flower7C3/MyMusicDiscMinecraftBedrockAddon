# 🎵 Personal Music Compilation – Minecraft Bedrock Addon

Personal music collection for Minecraft Bedrock Edition.

---

## 📋 Description

This addon enables adding custom music discs with playback in your own jukebox.

The `music_disc_generator.py` script automatically:

1. **Verifies ffmpeg** — checks if it's installed
2. **Scans MP3 files** from the `src/` directory
3. **Uses templates** — copies `.dist.*` files as configuration base
4. **Converts names** to `snake_case` for all keys
5. **Converts MP3 → OGG** using ffmpeg to `RP/sounds/items/`. If the OGG file already exists and has the same checksum as the MP3, conversion is skipped (data is stored in `.ogg_checksums.json` file).
6. **Extracts artwork** from MP3 files to `RP/textures/items/`
7. **Creates items** in `BP/items/` with `personal_music_compilation` namespace
8. **Updates `jukebox.json`** — generates dynamic `custom_disc_X` and `vanilla_disc_X` sections
9. **Updates `sound_definitions.json`** — adds sound definitions
10. **Updates `item_texture.json`** — adds textures
11. **Updates `musicDiscs.js`** — adds disc metadata (vanilla + custom)
12. **Generates `jukeboxManager.js`** — dynamically from template
13. **Cleans old files** — removes definitions for non-existent discs

### ✨ Features

- ✅ **Custom jukebox** with full functionality
- ✅ **Music disc generator** — automatic MP3 processing
- ✅ **Sound playback** with loop and particles
- ✅ **Automatic addon building**
- ✅ **Real-time debugging**
- ✅ **Minecraft Bedrock compatibility**
- ✅ **Dynamic vanilla sections** — handles all vanilla discs from Minecraft
- ✅ **Dynamic custom sections** — handles any number of custom discs
- ✅ **JavaScript templates** — dynamic generation of `jukeboxManager.js`

### 📦 Content

This addon supports:

**Vanilla discs (21 discs):**

- All vanilla discs from Minecraft are automatically supported
- `vanilla_disc_1` and `vanilla_disc_2` sections are generated dynamically
- Discs from `minecraft:music_disc_13` to `minecraft:music_disc_lava_chicken`

**Custom discs:**

- Any number of custom discs from MP3 files
- `custom_disc_1`, `custom_disc_2`, etc. sections are generated automatically
- Maximum 15 discs per section

---

## 🛠️ Installation and Building

### Requirements

- **Minecraft Bedrock** — with experimental features
- **Python** 3.7+ – for building packages
- **ffmpeg** – for audio conversion

### Installing ffmpeg

| **macOS (Homebrew)**      | **Ubuntu/Debian**                                | **Windows**                                                                    |
|---------------------------|--------------------------------------------------|--------------------------------------------------------------------------------|
| ```brew install ffmpeg``` | ```sudo apt update && sudo apt install ffmpeg``` | Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) |

### Virtual Environment (venv) - macOS

Before running scripts on macOS, it's recommended to create a virtual environment:

- Automatic setup (recommended)

```bash
./setup_venv.sh
```

- Activate environment

```bash
source venv/bin/activate
```

### 💻 Local Building

1. Download the repository and enter the directory:
    ```bash
   git clone https://github.com/Flower7C3/personal-music-compilation-minecraft-bedrock-addon.git
   cd personal-music-compilation-minecraft-bedrock-addon
   ```
2. Place MP3 files in the `src/` directory
3. Run the disc generator:
   ```bash
   python3 music_disc_generator.py
   ```
4. Run the build script without version bump:
   ```bash
   python3 build.py --mcaddon --test-on-local --no-bump
   ```

### 📱 Installation

After building the project, you'll find `.mcaddon` and `.mcpack` files in the [dist/](dist/) directory.

#### 💻 Locally (Minecraft Bedrock) from built packages

1. Open the `.mcaddon` file in Minecraft Bedrock
2. Enable packs:
    - Settings → Global Resources
    - Find "Personal Music Compilation RP" and enable it (move to right side)
3. Enable experiments:
    - Go to Settings → Experiments
    - Enable "Holiday Creator Features" (required for custom blocks)
4. Create or edit world:
    - Create a new world or edit existing one
    - In world settings, make sure "Holiday Creator Features" is enabled
    - Behavior pack should be automatically enabled after enabling resource pack

#### 🌐 On server (Aternos)

1. Upload `.mcpack` files to Aternos server
2. Start server and join the game

### 🎮 Usage

1. Go to creative mode
2. Place a jukebox in the world
3. Take any disc (vanilla or custom) in hand
4. Right-click on the jukebox
5. Enjoy the music! 🎵

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
