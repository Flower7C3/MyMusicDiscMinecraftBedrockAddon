# 🎵 Personal Music Compilation – Minecraft Bedrock Addon

Projekt dodatku Minecraft Bedrock umożliwiający dodawanie własnych płyt muzycznych z odtwarzaniem we własnej szafie
grającej (jukebox).

## 📋 Funkcjonalności

- ✅ **Custom jukebox** z pełną funkcjonalnością
- ✅ **Generator dysków muzycznych** — automatyczne przetwarzanie MP3
- ✅ **Odtwarzanie dźwięku** z pętlą i cząsteczkami
- ✅ **Automatyczne budowanie** dodatku
- ✅ **Debugowanie** w czasie rzeczywistym
- ✅ **Kompatybilność** z Minecraft Bedrock
- ✅ **Dynamiczne sekcje vanilla** — obsługa wszystkich dysków vanilla z Minecraft
- ✅ **Dynamiczne sekcje custom** — obsługa dowolnej liczby dysków custom
- ✅ **Szablony JavaScript** — dynamiczne generowanie `jukeboxManager.js`

### Obsługiwane dyski

**Dyski vanilla (21 dysków):**

- Wszystkie dyski vanilla z Minecraft są automatycznie obsługiwane
- Sekcje `vanilla_disc_1` i `vanilla_disc_2` są generowane dynamicznie
- Dysk `minecraft:music_disc_13` do `minecraft:music_disc_lava_chicken`

**Dyski custom:**

- Dowolna liczba dysków custom z plików MP3
- Sekcje `custom_disc_1`, `custom_disc_2`, itd. są generowane automatycznie
- Maksymalnie 15 dysków na sekcję

## 🏗️ Budowanie

Paczka nie jest automatycznie budowana. Należy lokalnie dodać wybrane przez siebie pliki MP3 i zbudować paczkę.

## 🛠️ Instalacja

### Wymagania

- **Minecraft Bedrock** — z eksperymentalnymi funkcjami
- **Python** 3.7+ – do budowania paczek
- **ffmpeg** – do konwersji audio

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

### Instalacja ffmpeg

**macOS (Homebrew):**

```bash
brew install ffmpeg
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Pobierz z [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Generator dysków (`music_disc_generator.py`)

1. Umieść pliki MP3 w katalogu `src/`
2. Uruchom generator:
   ```bash
   python3 music_disc_generator.py
   ```

Skrypt automatycznie:

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

### Lokalne budowanie

- Buduj tylko `.mcaddon`

```bash
python3 build.py --mcaddon
```

- Buduj tylko `.mcpack`

```bash
python3 build.py --mcpack
```

- Buduj wszystkie typy pakietów

```bash
python3 build.py --all
```

- Buduj bez zwiększania wersji

```bash
python3 build.py --mcaddon --no-bump
```

- Buduj i zainstaluj lokalnie

```bash
python3 build.py --mcaddon --test-on-local
```

### Na serwerze (Aternos)

1. Wgraj wygenerowane pliki `.mcaddon` na serwer Aternos
2. Uruchom serwer

### Aktywacja w grze

Po zainstalowaniu paczek musisz je aktywować w Minecraft:

1. **Zamknij Minecraft** (jeśli jest uruchomiony)

2. **Otwórz Minecraft** i przejdź do:
    - Ustawienia → Zasoby globalne
    - Znajdź "Personal Music Compilation RP" i włącz ją

3. **Włącz eksperymenty**:
    - Przejdź do Ustawienia → Eksperymenty
    - Włącz "Holiday Creator Features" (wymagane dla niestandardowych bloków)

4. **Utwórz lub edytuj świat**:
    - Utwórz nowy świat lub edytuj istniejący
    - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone
    - Paczka zachowań powinna być automatycznie włączona po włączeniu paczki zasobów

5. **Przetestuj jukebox**:
    - Umieść customowy jukebox (`personal_music_compilation:jukebox`) w świecie
    - Weź dowolny dysk (vanilla lub custom) do ręki
    - Kliknij prawym przyciskiem na jukebox
    - Ciesz się muzyką! 🎵

## 🔧 Rozwiązywanie problemów

### Jukebox nie działa

- Sprawdź, czy używasz **customowego jukebox** (`personal_music_compilation:jukebox`), nie vanilla
- Upewnij się, że **eksperymentalne funkcje** są włączone
- Sprawdź konsolę gry (F3 + D) dla komunikatów debugowania
- Upewnij się, że addon jest poprawnie zainstalowany

### Dyski vanilla nie działają

- Sprawdź, czy plik `src/minecraft.music_disc.json` istnieje
- Uruchom generator ponownie: `python3 music_disc_generator.py`
- Sprawdź, czy sekcje `vanilla_disc_X` zostały wygenerowane w `jukebox.json`

### Generator nie działa

- Sprawdź, czy **ffmpeg** jest zainstalowane
- Upewnij się, że pliki MP3 nie są uszkodzone
- Sprawdź uprawnienia do zapisu w katalogach

### Błędy budowania

- Sprawdź, czy wszystkie pliki są poprawnie utworzone
- Upewnij się, że struktura katalogów jest prawidłowa
- Sprawdź logi budowania

### Namespace

Wszystkie elementy używają namespace `personal_music_compilation:`:

- `personal_music_compilation:music_disc_*` - custom dyski muzyczne
- `personal_music_compilation:jukebox` - custom jukebox
- `personal_music_compilation:custom_disc_X` - dynamiczne sekcje dysków custom
- `personal_music_compilation:vanilla_disc_X` - dynamiczne sekcje dysków vanilla
- `personal_music_compilation:playing_disc` - stan odtwarzania

### Konwersja nazw

Skrypt automatycznie konwertuje nazwy plików do `snake_case`:

- `Twoja Muzyka.mp3` → `twoja_muzyka`
- `Super Hit - 2024.mp3` → `super_hit_2024`
- `Rock & Roll Classic.mp3` → `rock_roll_classic`

### Pliki szablonów (`.dist.*`)

Skrypt używa plików szablonów jako podstawy konfiguracji:

- `BP/blocks/jukebox.dist.json` - szablon szafy grającej
- `RP/sounds/sound_definitions.dist.json` - szablon definicji dźwięków
- `RP/textures/item_texture.dist.json` - szablon definicji tekstur
- `template/BP/scripts/jukebox/jukeboxManager.dist.js` - szablon JavaScript szafy grającej

Przed każdą aktualizacją skrypt kopiuje plik szablonu do głównego pliku konfiguracyjnego.

### Dynamiczne generowanie JavaScript

- `jukeboxManager.js` jest generowany dynamicznie z szablonu
- Obsługuje dowolną liczbę sekcji `custom_disc_X` i `vanilla_disc_X`
- Automatycznie dostosowuje się do liczby dysków

### System Git i ignorowanie plików

Wygenerowane pliki są ignorowane przez Git:

- `BP/items/music_disc_*.item.json` - pliki itemów dysków
- `RP/sounds/items/*.ogg` - pliki dźwięków OGG
- `RP/textures/items/music_disc_*.png` - pliki tekstur dysków
- `BP/blocks/jukebox.json` - wygenerowany plik konfiguracyjny
- `RP/sounds/sound_definitions.json` - wygenerowany plik konfiguracyjny
- `RP/textures/item_texture.json` - wygenerowany plik konfiguracyjny
- `BP/scripts/musicDisc/musicDiscs.js` - wygenerowany plik konfiguracyjny
- `BP/scripts/jukebox/jukeboxManager.js` - wygenerowany plik JavaScript
- `.ogg_checksums.json` - plik z sumami kontrolnymi

Pliki szablonów (`.dist.*`) są śledzone przez Git.

### Raportowanie błędów

Jeśli znajdziesz błąd:

1. Sprawdź konsolę gry (F3 + D)
2. Zbierz komunikaty debugowania
3. Opisz kroki reprodukcji
4. Dołącz informacje o wersji Minecraft

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.
