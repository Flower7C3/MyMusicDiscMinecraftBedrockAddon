#!/usr/bin/env python3
"""
Skrypt do automatyzacji procesu dodawania nowych muzycznych dysków do pakietu Minecraft.
Konwertuje pliki MP3 z katalogu src/ na dyski muzyczne z odpowiednimi teksturami i dźwiękami.
"""

import os
import json
import re
import subprocess
import shutil
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from console_utils import ConsoleStyle, print_header

class MusicDiscGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.bp_dir = self.project_root / "BP"
        self.rp_dir = self.project_root / "RP"
        
        # Katalogi
        self.items_dir = self.bp_dir / "items" / "mymusic"
        self.sounds_dir = self.rp_dir / "sounds" / "music" / "game" / "records"
        self.textures_dir = self.rp_dir / "textures" / "mymusic" / "items"
        
        # Pliki konfiguracyjne
        self.jukebox_file = self.bp_dir / "blocks" / "jukebox.json"
        self.sound_definitions_file = self.rp_dir / "sounds" / "sound_definitions.json"
        self.item_texture_file = self.rp_dir / "textures" / "item_texture.json"
        
        # Plik z sumami kontrolnymi
        self.checksums_file = self.project_root / ".ogg_checksums.json"
        
        # Namespace
        self.namespace = "mymusic"
        
        # Utworzenie katalogów jeśli nie istnieją
        self._create_directories()
    
    def _create_directories(self):
        """Tworzy niezbędne katalogi jeśli nie istnieją."""
        directories = [
            self.items_dir,
            self.sounds_dir,
            self.textures_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _to_snake_case(self, text: str) -> str:
        """Konwertuje tekst do snake_case."""
        # Usuń rozszerzenie pliku
        text = re.sub(r'\.[^.]*$', '', text)
        
        # Zamień spacje i podkreślenia na pojedyncze podkreślenia
        text = re.sub(r'[_\s]+', '_', text)
        
        # Usuń znaki specjalne i zamień na podkreślenia
        text = re.sub(r'[^a-zA-Z0-9]', '_', text)
        
        # Usuń wielokrotne podkreślenia
        text = re.sub(r'_+', '_', text)
        
        # Usuń podkreślenia na początku i końcu
        text = text.strip('_')
        
        # Konwertuj na małe litery
        return text.lower()
    
    def _get_mp3_files(self, specific_file: Optional[str] = None) -> List[Path]:
        """Zwraca listę plików MP3 z katalogu src/ lub konkretny plik."""
        if specific_file:
            file_path = self.src_dir / specific_file
            if file_path.exists() and file_path.suffix.lower() == '.mp3':
                print(ConsoleStyle.info(f"Przetwarzam konkretny plik: {specific_file}"))
                return [file_path]
            else:
                print(ConsoleStyle.error(f"Plik {specific_file} nie istnieje lub nie jest plikiem MP3!"))
                return []
        
        if not self.src_dir.exists():
            print(ConsoleStyle.error(f"Katalog {self.src_dir} nie istnieje!"))
            return []
        
        mp3_files = list(self.src_dir.glob("*.mp3"))
        print(ConsoleStyle.info(f"Znaleziono {len(mp3_files)} plików MP3 w {self.src_dir}"))
        return mp3_files
    
    def _extract_artwork(self, mp3_file: Path, output_file: Path) -> bool:
        """Wyciąga artwork z pliku MP3 lub używa domyślnego obrazka."""
        try:
            # Próbuj wyciągnąć artwork z MP3
            cmd = [
                "ffmpeg", "-y", "-i", str(mp3_file),
                "-vf", "select=eq(n\\,0),scale=32:32", "-vframes", "1",
                str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and output_file.exists() and output_file.stat().st_size > 0:
                print(ConsoleStyle.success(f"Wyciągnięto artwork z {mp3_file.name} (32x32px)"))
                return True
            else:
                # Użyj domyślnego obrazka
                default_texture = self.rp_dir / "pack_icon.png"
                if default_texture.exists():
                    # Skopiuj i przeskaluj domyślny obrazek
                    cmd = [
                        "ffmpeg", "-y", "-i", str(default_texture),
                        "-vf", "scale=32:32",
                        str(output_file)
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(ConsoleStyle.success(f"Użyto domyślnego obrazka dla {mp3_file.name} (32x32px)"))
                        return True
                    else:
                        print(ConsoleStyle.warning(f"Nie można przeskalować domyślnego obrazka dla {mp3_file.name}"))
                        return False
                else:
                    print(ConsoleStyle.warning(f"Nie można znaleźć domyślnego obrazka dla {mp3_file.name}"))
                    return False
                    
        except Exception as e:
            print(ConsoleStyle.error(f"Błąd podczas wyciągania artwork z {mp3_file.name}: {e}"))
            return False
    
    def _get_file_checksum(self, file_path: Path) -> str:
        """Oblicza sumę kontrolną pliku."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _load_checksums(self) -> Dict[str, str]:
        """Ładuje sumy kontrolne z pliku."""
        if self.checksums_file.exists():
            try:
                with open(self.checksums_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Błąd podczas ładowania sum kontrolnych: {e}")
        return {}
    
    def _save_checksums(self, checksums: Dict[str, str]):
        """Zapisuje sumy kontrolne do pliku."""
        try:
            with open(self.checksums_file, 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Błąd podczas zapisywania sum kontrolnych: {e}")
    
    def _convert_mp3_to_ogg(self, mp3_file: Path, ogg_file: Path) -> bool:
        """Konwertuje plik MP3 do formatu OGG z sprawdzaniem sum kontrolnych."""
        # Sprawdź czy plik OGG już istnieje i ma tę samą sumę kontrolną
        checksums = self._load_checksums()
        mp3_checksum = self._get_file_checksum(mp3_file)
        
        if ogg_file.exists() and mp3_checksum in checksums:
            existing_checksum = self._get_file_checksum(ogg_file)
            if existing_checksum == checksums[mp3_checksum]:
                print(ConsoleStyle.info(f"Pominięto konwersję {mp3_file.name} (plik OGG już istnieje)"))
                return True
        
        try:
            cmd = [
                "ffmpeg", "-y", "-i", str(mp3_file),
                "-vn", "-acodec", "libvorbis",
                str(ogg_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and ogg_file.exists():
                # Zapisz sumę kontrolną
                ogg_checksum = self._get_file_checksum(ogg_file)
                checksums[mp3_checksum] = ogg_checksum
                self._save_checksums(checksums)
                
                print(ConsoleStyle.success(f"Skonwertowano {mp3_file.name} do {ogg_file.name}"))
                return True
            else:
                print(ConsoleStyle.error(f"Błąd podczas konwersji {mp3_file.name}: {result.stderr}"))
                return False
                
        except Exception as e:
            print(ConsoleStyle.error(f"Błąd podczas konwersji {mp3_file.name}: {e}"))
            return False
    
    def _create_item_json(self, disc_name: str, display_name: str) -> Dict:
        """Tworzy JSON dla itemu dysku muzycznego."""
        return {
            "format_version": "1.21.40",
            "minecraft:item": {
                "description": {
                    "identifier": f"{self.namespace}:music_disc_{disc_name}",
                    "menu_category": {
                        "category": "items",
                        "group": "itemGroup.name.record"
                    }
                },
                "components": {
                    "minecraft:icon": f"{self.namespace}:music_disc_{disc_name}",
                    "minecraft:display_name": {
                        "value": f"§bMusic Disc\n§7{display_name}"
                    },
                    "minecraft:max_stack_size": 1
                }
            }
        }
    
    def _update_jukebox_json(self, disc_names: List[str]):
        """Aktualizuje jukebox.json dodając nowe dyski do sekcji my_music_disc:custom_disc_1."""
        if not self.jukebox_file.exists():
            print(f"❌ Plik {self.jukebox_file} nie istnieje!")
            return False
        
        try:
            with open(self.jukebox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Znajdź sekcję my_music_disc:custom_disc_1
            states = data["minecraft:block"]["description"]["states"]
            custom_disc_1 = states.get("my_music_disc:custom_disc_1", [])
            
            # Usuń wszystkie istniejące dyski my_music_disc: i moremusicdiscs:
            custom_disc_1 = [item for item in custom_disc_1 if not item.startswith("my_music_disc:music_disc_") and not item.startswith("moremusicdiscs:music_disc_")]
            
            # Dodaj "none" na początku jeśli nie ma
            if "none" not in custom_disc_1:
                custom_disc_1.insert(0, "none")
            
            # Dodaj nowe dyski
            for disc_name in disc_names:
                disc_identifier = f"{self.namespace}:music_disc_{disc_name}"
                if disc_identifier not in custom_disc_1:
                    custom_disc_1.append(disc_identifier)
                    print(f"✅ Dodano dysk do jukebox: {disc_identifier}")
            
            states["my_music_disc:custom_disc_1"] = custom_disc_1
            
            with open(self.jukebox_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Zaktualizowano {self.jukebox_file}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd podczas aktualizacji {self.jukebox_file}: {e}")
            return False
    
    def _update_sound_definitions(self, disc_names: List[str]):
        """Aktualizuje sound_definitions.json dodając nowe definicje dźwięków."""
        if not self.sound_definitions_file.exists():
            print(f"❌ Plik {self.sound_definitions_file} nie istnieje!")
            return False
        
        try:
            with open(self.sound_definitions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sound_definitions = data["sound_definitions"]
            
            # Usuń wszystkie istniejące wpisy record. dla dysków my_music_disc:
            to_remove = []
            for key in sound_definitions.keys():
                if key.startswith("record."):
                    disc_name = key.replace("record.", "")
                    if disc_name not in disc_names:
                        to_remove.append(key)
            
            for key in to_remove:
                del sound_definitions[key]
                print(f"🗑️  Usunięto wpis dźwięku: {key}")
            
            # Dodaj nowe wpisy
            for disc_name in disc_names:
                sound_key = f"record.{disc_name}"
                if sound_key not in sound_definitions:
                    sound_definitions[sound_key] = {
                        "__use_legacy_max_distance": True,
                        "category": "record",
                        "max_distance": 64.0,
                        "min_distance": None,
                        "sounds": [
                            {
                                "load_on_low_memory": True,
                                "name": f"sounds/music/game/records/{disc_name}",
                                "stream": True,
                                "volume": 0.50
                            }
                        ]
                    }
                    print(f"✅ Dodano wpis dźwięku: {sound_key}")
            
            with open(self.sound_definitions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Zaktualizowano {self.sound_definitions_file}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd podczas aktualizacji {self.sound_definitions_file}: {e}")
            return False
    
    def _update_item_texture(self, disc_names: List[str]):
        """Aktualizuje item_texture.json dodając nowe tekstury."""
        if not self.item_texture_file.exists():
            print(f"❌ Plik {self.item_texture_file} nie istnieje!")
            return False
        
        try:
            with open(self.item_texture_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            texture_data = data["texture_data"]
            
            # Usuń wszystkie istniejące wpisy dla dysków my_music_disc: i moremusicdiscs:
            to_remove = []
            for key in texture_data.keys():
                if key.startswith("my_music_disc:music_disc_") or key.startswith("moremusicdiscs:music_disc_"):
                    disc_name = key.replace("my_music_disc:music_disc_", "").replace("moremusicdiscs:music_disc_", "")
                    if disc_name not in disc_names:
                        to_remove.append(key)
            
            for key in to_remove:
                del texture_data[key]
                print(f"🗑️  Usunięto wpis tekstury: {key}")
            
            # Dodaj nowe wpisy
            for disc_name in disc_names:
                texture_key = f"{self.namespace}:music_disc_{disc_name}"
                if texture_key not in texture_data:
                    texture_data[texture_key] = {
                        "textures": f"textures/{self.namespace}/items/music_disc_{disc_name}"
                    }
                    print(f"✅ Dodano wpis tekstury: {texture_key}")
            
            with open(self.item_texture_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Zaktualizowano {self.item_texture_file}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd podczas aktualizacji {self.item_texture_file}: {e}")
            return False
    
    def _cleanup_old_files(self, current_disc_names: List[str]):
        """Usuwa pliki dla dysków, które nie są przetworzone z src/."""
        
        # Sprawdź istniejące pliki dźwięków
        if self.sounds_dir.exists():
            for sound_file in self.sounds_dir.glob("*.ogg"):
                sound_name = sound_file.stem
                if sound_name not in current_disc_names:
                    sound_file.unlink()
                    print(f"🗑️  Usunięto stary plik dźwięku: {sound_file.name}")
        
        # Sprawdź istniejące tekstury
        if self.textures_dir.exists():
            for texture_file in self.textures_dir.glob("music_disc_*.png"):
                texture_name = texture_file.stem.replace("music_disc_", "")
                if texture_name not in current_disc_names:
                    texture_file.unlink()
                    print(f"🗑️  Usunięto starą teksturę: {texture_file.name}")
        
        # Usuń nadmiarowe pliki itemów
        if self.items_dir.exists():
            for item_file in self.items_dir.glob("music_disc_*.item.json"):
                item_name = item_file.stem.replace("music_disc_", "").replace(".item", "")
                if item_name not in current_disc_names:
                    item_file.unlink()
                    print(f"🗑️  Usunięto nadmiarowy plik itemu: {item_file.name}")
        
        # Usuń nadmiarowe wpisy w sound_definitions.json
        self._cleanup_sound_definitions(current_disc_names)
        
        # Aktualizuj musicDiscs.js
        self._update_music_discs_js(current_disc_names)
    
    def _update_music_discs_js(self, disc_names: List[str]):
        """Aktualizuje musicDiscs.js z nowymi dyskami."""
        music_discs_file = self.bp_dir / "scripts" / "musicDisc" / "musicDiscs.js"
        
        if not music_discs_file.exists():
            print(f"❌ Plik {music_discs_file} nie istnieje!")
            return
        
        try:
            # Zbierz wszystkich artystów z plików MP3
            artists_dict = self._get_artists_from_mp3_files()
            
            # Stwórz nowy plik od podstaw
            content = """export var artistNames;
(function (artistNames) {
    artistNames["C418"] = "C418";
    artistNames["Lena_Raine"] = "Lena Raine";
    artistNames["Samuel_Aberg"] = "Samuel Åberg";
    artistNames["Aaron_Cherof"] = "Aaron Cherof";
    artistNames["Laudividni"] = "Laudividni";
    artistNames["Firch"] = "Firch";
    artistNames["The_Bling_Bling_Cheese"] = "The Bling-Bling Cheese";
    artistNames["Someone_zy2sh"] = "@Someone-zy2sh";
    artistNames["The_Musical_Sparrow"] = "The Musical Sparrow";
    artistNames["T_en_M"] = "T_en_M";
    artistNames["Naps_the_Block_Music"] = "Naps the Block Music";
    artistNames["Thaetaa_Terraainn"] = "Thaetaa-Terrainn";
    artistNames["Doom_On_A_Spoon"] = "Doom_On_A_Spoon";
    artistNames["Gamingtunes"] = "Gamingtunes";
    artistNames["Gwyd"] = "Gwyd";
    artistNames["Antimo_And_Wells"] = "Antimo & Wells";"""
            
            # Dodaj nowych artystów
            for artist_key, artist_name in artists_dict.items():
                content += f'\n    artistNames["{artist_key}"] = "{artist_name}";'
            
            content += """
})(artistNames || (artistNames = {}));

export const musicDiscs = {
    "minecraft:music_disc_13": {
        musicName: "13",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.13",
            tickLength: 3580
        }
    },
    "minecraft:music_disc_cat": {
        musicName: "cat",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.cat",
            tickLength: 3700
        }
    },
    "minecraft:music_disc_blocks": {
        musicName: "blocks",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.blocks",
            tickLength: 6960
        }
    },
    "minecraft:music_disc_chirp": {
        musicName: "chirp",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.chirp",
            tickLength: 3740
        }
    },
    "minecraft:music_disc_far": {
        musicName: "far",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.far",
            tickLength: 3540
        }
    },
    "minecraft:music_disc_mall": {
        musicName: "mall",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.mall",
            tickLength: 3980
        }
    },
    "minecraft:music_disc_mellohi": {
        musicName: "mellohi",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.mellohi",
            tickLength: 1980
        }
    },
    "minecraft:music_disc_stal": {
        musicName: "stal",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.stal",
            tickLength: 3060
        }
    },
    "minecraft:music_disc_strad": {
        musicName: "strad",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.strad",
            tickLength: 3800
        }
    },
    "minecraft:music_disc_ward": {
        musicName: "ward",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.ward",
            tickLength: 5080
        }
    },
    "minecraft:music_disc_11": {
        musicName: "11",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.11",
            tickLength: 1460
        }
    },
    "minecraft:music_disc_wait": {
        musicName: "wait",
        artist: artistNames.C418,
        sound: {
            volume: 1,
            id: "record.wait",
            tickLength: 4800
        }
    },
    "minecraft:music_disc_otherside": {
        musicName: "otherside",
        artist: artistNames.Lena_Raine,
        sound: {
            volume: 1,
            id: "record.otherside",
            tickLength: 3960
        }
    },
    "minecraft:music_disc_5": {
        musicName: "5",
        artist: artistNames.Samuel_Aberg,
        sound: {
            volume: 1,
            id: "record.5",
            tickLength: 3600
        }
    },
    "minecraft:music_disc_pigstep": {
        musicName: "Pigstep",
        artist: artistNames.Lena_Raine,
        sound: {
            volume: 1,
            id: "record.pigstep",
            tickLength: 3000
        }
    },
    "minecraft:music_disc_relic": {
        musicName: "Relic",
        artist: artistNames.Aaron_Cherof,
        sound: {
            volume: 1,
            id: "record.relic",
            tickLength: 4400
        }
    },
    "minecraft:music_disc_creator": {
        musicName: "Creator",
        artist: artistNames.Lena_Raine,
        sound: {
            volume: 1,
            id: "record.creator",
            tickLength: 3560
        }
    },
    "minecraft:music_disc_creator_music_box": {
        musicName: "Creator (Music Box)",
        artist: artistNames.Lena_Raine,
        sound: {
            volume: 1,
            id: "record.creator_music_box",
            tickLength: 1500
        }
    },
    "minecraft:music_disc_precipice": {
        musicName: "Precipice",
        artist: artistNames.Aaron_Cherof,
        sound: {
            volume: 1,
            id: "record.precipice",
            tickLength: 6000
        }
    }"""
            
            # Dodaj nowe wpisy mymusic:
            for disc_name in disc_names:
                # Wyciągnij artystę i tytuł z nazwy pliku MP3
                artist, title = self._get_artist_and_title_from_mp3(disc_name)
                
                # Oblicz tickLength z pliku OGG
                ogg_file = self.sounds_dir / f"{disc_name}.ogg"
                tick_length = 3000  # domyślna wartość
                
                if ogg_file.exists():
                    try:
                        # Użyj ffprobe do pobrania długości
                        cmd = [
                            "ffprobe", "-v", "quiet", "-show_entries", 
                            "format=duration", "-of", "csv=p=0", str(ogg_file)
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            duration = float(result.stdout.strip())
                            # Konwertuj sekundy na ticki (20 ticków na sekundę)
                            tick_length = int(duration * 20)
                    except Exception as e:
                        print(f"⚠️  Nie można obliczyć długości dla {disc_name}: {e}")
                
                # Dodaj nowy wpis
                content += f',\n    "my_music_disc:music_disc_{disc_name}": {{\n'
                content += f'        musicName: "{title}",\n'
                content += f'        artist: artistNames.{artist},\n'
                content += f'        sound: {{\n'
                content += f'            volume: 0.75,\n'
                content += f'            id: "record.{disc_name}",\n'
                content += f'            tickLength: {tick_length}\n'
                content += f'        }}\n'
                content += f'    }}'
                
                print(f"✅ Dodano wpis do musicDiscs.js: my_music_disc:music_disc_{disc_name} ({artist} - {title})")
            
            # Dodaj końcowy nawias
            content += "\n};"
            
            with open(music_discs_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Zaktualizowano {music_discs_file}")
            
        except Exception as e:
            print(f"❌ Błąd podczas aktualizacji {music_discs_file}: {e}")
    
    def _cleanup_sound_definitions(self, current_disc_names: List[str]):
        """Usuwa nadmiarowe wpisy w sound_definitions.json."""
        if not self.sound_definitions_file.exists():
            return
        
        try:
            with open(self.sound_definitions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sound_definitions = data.get("sound_definitions", {})
            removed_count = 0
            
            # Znajdź wpisy do usunięcia
            to_remove = []
            for key in sound_definitions.keys():
                if key.startswith("record."):
                    disc_name = key.replace("record.", "")
                    if disc_name not in current_disc_names:
                        to_remove.append(key)
            
            # Usuń wpisy
            for key in to_remove:
                del sound_definitions[key]
                removed_count += 1
                print(f"🗑️  Usunięto wpis dźwięku: {key}")
            
            if removed_count > 0:
                # Zapisz zaktualizowany plik
                with open(self.sound_definitions_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print(f"✅ Zaktualizowano {self.sound_definitions_file}")
            
        except Exception as e:
            print(f"❌ Błąd podczas czyszczenia sound_definitions.json: {e}")
    
    def process_mp3_files(self, specific_file: Optional[str] = None):
        """Główna funkcja przetwarzająca pliki MP3."""
        print_header("Generator Dysków Muzycznych dla Minecraft")
        
        # Sprawdź czy ffmpeg jest dostępny
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(ConsoleStyle.error("ffmpeg nie jest zainstalowany lub nie jest dostępny!"))
            print(ConsoleStyle.info("Zainstaluj ffmpeg: https://ffmpeg.org/download.html"))
            return
        
        mp3_files = self._get_mp3_files(specific_file)
        if not mp3_files:
            print(ConsoleStyle.error("Nie znaleziono plików MP3 do przetworzenia!"))
            return
        
        processed_disc_names = []
        errors = []
        
        for i, mp3_file in enumerate(mp3_files, 1):
            print(ConsoleStyle.process(f"Przetwarzam: {mp3_file.name} ({i}/{len(mp3_files)})"))
            
            # Konwertuj nazwę pliku do snake_case
            disc_name = self._to_snake_case(mp3_file.name)
            display_name = mp3_file.stem  # Oryginalna nazwa bez rozszerzenia
            
            print(ConsoleStyle.info(f"Nazwa dysku: {disc_name}"))
            print(ConsoleStyle.info(f"Nazwa wyświetlana: {display_name}"))
            
            try:
                # Utwórz plik itemu
                item_file = self.items_dir / f"music_disc_{disc_name}.item.json"
                item_data = self._create_item_json(disc_name, display_name)
                
                with open(item_file, 'w', encoding='utf-8') as f:
                    json.dump(item_data, f, indent=4, ensure_ascii=False)
                print(ConsoleStyle.success(f"Utworzono item: {item_file.name}"))
                
                # Konwertuj MP3 do OGG
                ogg_file = self.sounds_dir / f"{disc_name}.ogg"
                if self._convert_mp3_to_ogg(mp3_file, ogg_file):
                    processed_disc_names.append(disc_name)
                
                # Wyciągnij artwork
                texture_file = self.textures_dir / f"music_disc_{disc_name}.png"
                self._extract_artwork(mp3_file, texture_file)
                
            except Exception as e:
                error_msg = f"Błąd podczas przetwarzania {mp3_file.name}: {e}"
                print(ConsoleStyle.error(error_msg))
                errors.append(error_msg)
        
        # Aktualizuj pliki konfiguracyjne
        if processed_disc_names:
            ConsoleStyle.print_section("Aktualizuję pliki konfiguracyjne")
            
            # Aktualizuj jukebox.json
            self._update_jukebox_json(processed_disc_names)
            
            # Aktualizuj sound_definitions.json
            self._update_sound_definitions(processed_disc_names)
            
            # Aktualizuj item_texture.json
            self._update_item_texture(processed_disc_names)
        
        # Czyszczenie starych plików
        ConsoleStyle.print_section("Czyszczę stare pliki")
        self._cleanup_old_files(processed_disc_names)
        
        # Podsumowanie
        ConsoleStyle.print_summary(len(processed_disc_names), len(mp3_files), errors)
        
        if processed_disc_names:
            print(ConsoleStyle.info(f"Nowe dyski: {', '.join(processed_disc_names)}"))

    def _get_artists_from_mp3_files(self) -> Dict[str, str]:
        """Zbiera wszystkich artystów z plików MP3 w src/."""
        mp3_files = list(self.src_dir.glob("*.mp3"))
        artists_dict = {}
        
        for mp3_file in mp3_files:
            file_name = mp3_file.stem
            if " - " in file_name:
                artist_part, title_part = file_name.split(" - ", 1)
                artist_name = artist_part.strip()
                artist_key = artist_name.replace(" ", "_").replace("&", "_").replace("-", "_")
                # Usuń podwójne podkreślniki
                while "__" in artist_key:
                    artist_key = artist_key.replace("__", "_")
                artists_dict[artist_key] = artist_name
        
        return artists_dict
    
    def _get_artist_and_title_from_mp3(self, disc_name: str) -> Tuple[str, str]:
        """Wyciąga artystę i tytuł z pliku MP3 na podstawie nazwy dysku."""
        mp3_files = list(self.src_dir.glob("*.mp3"))
        artist = "Unknown_Artist"
        title = disc_name.replace("_", " ").title()
        
        for mp3_file in mp3_files:
            if self._to_snake_case(mp3_file.name) == disc_name:
                # Wyciągnij artystę i tytuł z nazwy pliku
                file_name = mp3_file.stem
                if " - " in file_name:
                    artist_part, title_part = file_name.split(" - ", 1)
                    artist = artist_part.strip().replace(" ", "_").replace("&", "_").replace("-", "_")
                    # Usuń podwójne podkreślniki
                    while "__" in artist:
                        artist = artist.replace("__", "_")
                    title = title_part.strip()
                break
        
        return artist, title

def main():
    """Główna funkcja skryptu."""
    parser = argparse.ArgumentParser(description="Generator Dysków Muzycznych dla Minecraft")
    parser.add_argument("--file", "-f", help="Konwertuj konkretny plik MP3 z katalogu src/")
    args = parser.parse_args()
    
    # Sprawdź czy jesteśmy w katalogu projektu
    project_root = os.getcwd()
    
    if not os.path.exists(os.path.join(project_root, "BP")) or not os.path.exists(os.path.join(project_root, "RP")):
        print(ConsoleStyle.error("Nie znaleziono katalogów BP i RP! Upewnij się, że jesteś w katalogu projektu."))
        return
    
    generator = MusicDiscGenerator(project_root)
    generator.process_mp3_files(args.file)

if __name__ == "__main__":
    main() 