# 🎵 Personal Music Compilation – Minecraft Bedrock Addon

Osobista kolekcja muzyki dla Minecraft Bedrock Edition.

---

## 📋 Opis

Ten dodatek umożliwia dodawanie własnych płyt muzycznych z odtwarzaniem we własnej szafie
grającej (jukebox).

Skrypt `music_disc_generator.py` automatycznie:

1. **Weryfikuje ffmpeg** — sprawdza, czy jest zainstalowane
2. **Skanuje pliki MP3** z katalogu `src/`
3. **Używa szablonów** — kopiuje pliki `.dist.*` jako podstawę konfiguracji
4. **Konwertuje nazwy** do `snake_case` dla wszystkich kluczy
5. **Konwertuje MP3 → OGG** używając ffmpeg do `RP/sounds/items/`. Jeśli plik OGG już istnieje i ma tę samą sumę
   kontrolną co MP3, konwersja jest pomijana (dane są przechowywane w pliku `.ogg_checksums.json`).
6. **Wyciąga obrazki** z plików MP3 do `RP/textures/items/`
7. **Tworzy itemy** w `BP/items/` z namespace `personal_music_compilation`
8. **Aktualizuje `jukebox.json`** — generuje dynamiczne sekcje `custom_disc_X` i `vanilla_disc_X`
9. **Aktualizuje `sound_definitions.json`** — dodaje definicje dźwięków
10. **Aktualizuje `item_texture.json`** – dodaje tekstury
11. **Aktualizuje `musicDiscs.js`** — dodaje metadane dysków (vanilla + custom)
12. **Generuje `jukeboxManager.js`** — dynamicznie z szablonu
13. **Czyści stare pliki** — usuwa definicje dla nieistniejących dysków

### ✨ Funkcjonalności

- ✅ **Custom jukebox** z pełną funkcjonalnością
- ✅ **Generator dysków muzycznych** — automatyczne przetwarzanie MP3
- ✅ **Odtwarzanie dźwięku** z pętlą i cząsteczkami
- ✅ **Automatyczne budowanie** dodatku
- ✅ **Debugowanie** w czasie rzeczywistym
- ✅ **Kompatybilność** z Minecraft Bedrock
- ✅ **Dynamiczne sekcje vanilla** — obsługa wszystkich dysków vanilla z Minecraft
- ✅ **Dynamiczne sekcje custom** — obsługa dowolnej liczby dysków custom
- ✅ **Szablony JavaScript** — dynamiczne generowanie `jukeboxManager.js`

### 📦 Zawartość

Ten addon obsługuje:

**Dyski vanilla (21 dysków):**

- Wszystkie dyski vanilla z Minecraft są automatycznie obsługiwane
- Sekcje `vanilla_disc_1` i `vanilla_disc_2` są generowane dynamicznie
- Dysk `minecraft:music_disc_13` do `minecraft:music_disc_lava_chicken`

**Dyski custom:**

- Dowolna liczba dysków custom z plików MP3
- Sekcje `custom_disc_1`, `custom_disc_2`, itd. są generowane automatycznie
- Maksymalnie 15 dysków na sekcję

---

## 🛠️ Instalacja i budowanie

### Wymagania

- **Minecraft Bedrock** — z eksperymentalnymi funkcjami
- **Python** 3.7+ – do budowania paczek
- **ffmpeg** – do konwersji audio

### Instalacja ffmpeg

| **macOS (Homebrew)**      | **Ubuntu/Debian**                                | **Windows**                                                                    |
|---------------------------|--------------------------------------------------|--------------------------------------------------------------------------------|
| ```brew install ffmpeg``` | ```sudo apt update && sudo apt install ffmpeg``` | Pobierz z [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html) |

### Środowisko wirtualne (venv) - macOS

Przed uruchomieniem skryptów na macOS, zalecane jest utworzenie środowiska wirtualnego:

- Automatyczna konfiguracja (zalecane)

```bash
./setup_venv.sh
```

- Aktywuj środowisko

```bash
source venv/bin/activate
```

### 💻 Budowanie lokalne

1. Pobierz repozytorium i wejdź do katalogu:
    ```bash
   git clone https://github.com/Flower7C3/personal-music-compilation-minecraft-bedrock-addon.git
   cd personal-music-compilation-minecraft-bedrock-addon
   ```
2. Umieść pliki MP3 w katalogu `src/`
3. Uruchom generator dysków:
   ```bash
   python3 music_disc_generator.py
   ```
4. Uruchom skrypt budowania bez podnoszenia wersji:
   ```bash
   python3 build.py --mcaddon --test-on-local --no-bump
   ```

### 📱 Instalacja

Po zbudowaniu projektu w katalogu [dist/](dist/) znajdziesz pliki `.mcaddon` i  `.mcpack`.

#### 💻 Lokalnie (Minecraft Bedrock) ze zbudowanych paczek

1. Otwórz plik `.mcaddon` w Minecraft Bedrock
2. Włącz paczki:
    - Ustawienia → Zasoby globalne
    - Znajdź "Personal Music Compilation RP" i włącz ją (przesuń na prawą stronę)
3. Włącz eksperymenty:
    - Przejdź do Ustawienia → Eksperymenty
    - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)
4. Utwórz lub edytuj świat:
    - Utwórz nowy świat lub edytuj istniejący
    - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
    - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

#### 🌐 Na serwerze (Aternos)

1. Wgraj pliki `.mcpack` na serwer Aternos
2. Uruchom serwer i dołącz do gry

### 🎮 Użycie

1. Przejdź do trybu kreatywnego
2. Umieść szafę grającą w świecie
3. Weź dowolny dysk (vanilla lub custom) do ręki
4. Kliknij prawym przyciskiem na jukebox
5. Ciesz się muzyką! 🎵

---

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów. 