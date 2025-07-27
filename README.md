# 🎵 My Music Disc - Minecraft Bedrock Addon

Projekt addonu Minecraft Bedrock umożliwiający dodawanie własnych dysków muzycznych z odtwarzaniem w customowym jukebox.

## 📋 Funkcjonalności

- ✅ **Custom jukebox** z pełną funkcjonalnością
- ✅ **Generator dysków muzycznych** - automatyczne przetwarzanie MP3
- ✅ **Odtwarzanie dźwięku** z pętlą i cząsteczkami
- ✅ **Automatyczne budowanie** addonów
- ✅ **Debugowanie** w czasie rzeczywistym
- ✅ **Kompatybilność** z Minecraft Bedrock



## 🛠️ Instalacja

### Wymagania

- **Python 3.6+**
- **ffmpeg** - do konwersji audio
- **Minecraft Bedrock** - z eksperymentalnymi funkcjami

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

### Dodawanie muzyki

1. Umieść pliki MP3 w katalogu `src/`
2. Uruchom generator:
   ```bash
   python3 music_disc_generator.py
   ```
3. Zbuduj addon:
   ```bash
   python3 build.py --mcaddon
   ```

### Aktywacja w grze

Po zainstalowaniu addon, musisz go aktywować w Minecraft:

1. **Zamknij Minecraft** (jeśli jest uruchomiony)

2. **Otwórz Minecraft** i przejdź do:
   - Ustawienia → Zasoby globalne
   - Znajdź "My Music Disc RP" i włącz ją

3. **Włącz eksperymenty**:
   - Przejdź do Ustawienia → Eksperymenty
   - Włącz "Holiday Creator Features" (wymagane dla custom bloków)

4. **Utwórz lub edytuj świat**:
   - Utwórz nowy świat lub edytuj istniejący
   - W ustawieniach świata upewnij się, że "Holiday Creator Features" jest włączone

5. **Przetestuj jukebox**:
   - Umieść customowy jukebox (`my_music_disc:jukebox`) w świecie
   - Weź customowy dysk (`my_music_disc:music_disc_*`) do ręki
   - Kliknij prawym przyciskiem na jukebox
   - Ciesz się muzyką! 🎵

## 📁 Struktura projektu

```
MyMusic/
├── src/                          # Pliki MP3 do przetworzenia
├── BP/                           # Behavior Pack
│   ├── items/my_music_disc/     # Custom dyski muzyczne
│   ├── blocks/                  # Custom jukebox
│   └── scripts/                 # Logika JavaScript
├── RP/                          # Resource Pack
│   ├── sounds/                  # Pliki dźwiękowe OGG
│   └── textures/                # Tekstury dysków
├── dist/                        # Zbudowane addony
├── music_disc_generator.py      # Generator dysków
├── build.py                     # Skrypt budowania
└── console_utils.py             # Narzędzia konsoli
```

## 🏗️ Budowanie

### Lokalne budowanie

```bash
# Buduj tylko .mcaddon
python3 build.py --mcaddon

# Buduj tylko .mcpack
python3 build.py --mcpack

# Buduj wszystkie typy pakietów
python3 build.py --all

# Buduj bez zwiększania wersji
python3 build.py --mcaddon --no-bump

# Buduj i zainstaluj lokalnie
python3 build.py --mcaddon --test-on-local
```

### Generator dysków (`music_disc_generator.py`)

Skrypt automatycznie:

1. **Skanuje pliki MP3** z katalogu `src/`
2. **Tworzy itemy** w `BP/items/my_music_disc/` z namespace `my_music_disc`
3. **Aktualizuje jukebox.json** - dodaje wpisy w sekcji `my_music_disc:custom_disc_1`
4. **Aktualizuje sound_definitions.json** - dodaje definicje dźwięków
5. **Konwertuje MP3 → OGG** używając ffmpeg do `RP/sounds/music/game/records/`
6. **Wyciąga obrazki** z plików MP3 do `RP/textures/my_music_disc/items/`
7. **Aktualizuje item_texture.json** - dodaje tekstury
8. **Konwertuje nazwy** do `snake_case` dla wszystkich kluczy
9. **Weryfikuje ffmpeg** - wymaga zainstalowania
10. **Czyści stare pliki** - usuwa definicje dla nieistniejących dysków

## 🔧 Konfiguracja

### Wymagania systemowe
- **Python 3.6+**
- **ffmpeg** - do konwersji audio
- **Minecraft Bedrock** - z eksperymentalnymi funkcjami

### Eksperymentalne funkcje
W świecie Minecraft włącz:
- ✅ Custom Blocks
- ✅ Scripting API
- ✅ Custom Items

## 🔧 Rozwiązywanie problemów

### Jukebox nie działa
- Sprawdź czy używasz **customowego jukebox** (`my_music_disc:jukebox`), nie vanilla
- Upewnij się, że **eksperymentalne funkcje** są włączone
- Sprawdź konsolę gry (F3 + D) dla komunikatów debugowania
- Upewnij się, że addon jest poprawnie zainstalowany

### Generator nie działa
- Sprawdź czy **ffmpeg** jest zainstalowane
- Upewnij się, że pliki MP3 nie są uszkodzone
- Sprawdź uprawnienia do zapisu w katalogach

### Błędy budowania
- Sprawdź czy wszystkie pliki są poprawnie utworzone
- Upewnij się, że struktura katalogów jest prawidłowa
- Sprawdź logi budowania

## 📦 Struktura projektu

```
MyMusic/
├── src/                          # Pliki MP3 do przetworzenia
├── BP/                           # Behavior Pack
│   ├── items/my_music_disc/     # Custom dyski muzyczne
│   ├── blocks/                  # Custom jukebox
│   └── scripts/                 # Logika JavaScript
├── RP/                          # Resource Pack
│   ├── sounds/                  # Pliki dźwiękowe OGG
│   └── textures/                # Tekstury dysków
├── dist/                        # Zbudowane addony
├── music_disc_generator.py      # Generator dysków
├── build.py                     # Skrypt budowania
└── console_utils.py             # Narzędzia konsoli
```

### Namespace
Wszystkie elementy używają namespace `my_music_disc:`:
- `my_music_disc:jukebox` - custom jukebox
- `my_music_disc:music_disc_*` - custom dyski muzyczne
- `my_music_disc:custom_disc_1` - stan dysku w jukebox
- `my_music_disc:playing_disc` - stan odtwarzania

### Konwersja nazw
Skrypt automatycznie konwertuje nazwy plików do `snake_case`:
- `Twoja Muzyka.mp3` → `twoja_muzyka`
- `Super Hit - 2024.mp3` → `super_hit_2024`
- `Rock & Roll Classic.mp3` → `rock_roll_classic`

### Synchronizacja
Skrypt automatycznie:
- Dodaje nowe dyski na podstawie plików w `src/`
- Usuwa wszystkie pliki, które nie są przetworzone z `src/`
- Aktualizuje wszystkie pliki konfiguracyjne:
  - `jukebox.json` - sekcja `my_music_disc:custom_disc_1`
  - `sound_definitions.json` - wpisy `record.`
  - `item_texture.json` - wpisy tekstur
  - `musicDiscs.js` - wpisy dysków
- Zachowuje tylko dyski z plików MP3 w `src/`

## 🔧 Narzędzia deweloperskie

### Dodawanie nowych dysków

1. Umieść plik MP3 w `src/`
2. Uruchom generator:
   ```bash
   python3 music_disc_generator.py
   ```
3. Zbuduj addon:
   ```bash
   python3 build.py --mcaddon
   ```
4. Przetestuj w grze

### Raportowanie błędów

Jeśli znajdziesz błąd:
1. Sprawdź konsolę gry (F3 + D)
2. Zbierz komunikaty debugowania
3. Opisz kroki reprodukcji
4. Dołącz informacje o wersji Minecraft

## 📄 Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE) dla szczegółów.
