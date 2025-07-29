# Zasady developerskie w projekcie

## Namespace

Wszystkie elementy używają namespace `personal_music_compilation:`:

- `personal_music_compilation:music_disc_*` - custom dyski muzyczne
- `personal_music_compilation:jukebox` - custom jukebox
- `personal_music_compilation:custom_disc_X` - dynamiczne sekcje dysków custom
- `personal_music_compilation:vanilla_disc_X` - dynamiczne sekcje dysków vanilla
- `personal_music_compilation:playing_disc` - stan odtwarzania

## Konwersja nazw

Skrypt automatycznie konwertuje nazwy plików do `snake_case`:

- `Twoja Muzyka.mp3` → `twoja_muzyka`
- `Super Hit - 2024.mp3` → `super_hit_2024`
- `Rock & Roll Classic.mp3` → `rock_roll_classic`

## Pliki szablonów (`.dist.*`)

Skrypt używa plików szablonów jako podstawy konfiguracji:

- `BP/blocks/jukebox.dist.json` - szablon szafy grającej
- `RP/sounds/sound_definitions.dist.json` - szablon definicji dźwięków
- `RP/textures/item_texture.dist.json` - szablon definicji tekstur
- `template/BP/scripts/jukebox/jukeboxManager.dist.js` - szablon JavaScript szafy grającej

Przed każdą aktualizacją skrypt kopiuje plik szablonu do głównego pliku konfiguracyjnego.

## Dynamiczne generowanie JavaScript

- `jukeboxManager.js` jest generowany dynamicznie z szablonu
- Obsługuje dowolną liczbę sekcji `custom_disc_X` i `vanilla_disc_X`
- Automatycznie dostosowuje się do liczby dysków

## System Git i ignorowanie plików

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
