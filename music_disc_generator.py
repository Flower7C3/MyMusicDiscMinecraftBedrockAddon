#!/usr/bin/env python3
"""
Skrypt do automatyzacji procesu dodawania nowych muzycznych płyt do pakietu Minecraft.
Konwertuje pliki MP3 z katalogu src/ na płyty muzyczne z odpowiednimi teksturami i dźwiękami.
"""

import os
import sys
import json
import re
import subprocess
import shutil
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from console_utils import ConsoleStyle

class MusicDiscGenerator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.bp_dir = self.project_root / "BP"
        self.rp_dir = self.project_root / "RP"
        self.template_dir = self.project_root / "template"
        self.bp_template_dir = self.template_dir / "BP"
        self.rp_template_dir = self.template_dir / "RP"

        # Katalogi
        self.items_dir = self.bp_dir / "items"
        self.sounds_dir = self.rp_dir / "sounds" / "items"
        self.textures_dir = self.rp_dir / "textures" / "items"
        
        # Pliki konfiguracyjne
        self.jukebox_file = self.bp_dir / "blocks" / "jukebox.block.json"
        self.jukebox_dist_file = self.bp_template_dir / "blocks" / "jukebox.dist.block.json"
        self.sound_definitions_file = self.rp_dir / "sounds" / "sound_definitions.json"
        self.sound_definitions_dist_file = self.rp_template_dir / "sounds" / "sound_definitions.dist.json"
        self.item_texture_file = self.rp_dir / "textures" / "item_texture.json"
        self.item_texture_dist_file = self.rp_template_dir / "textures" / "item_texture.dist.json"
        self.music_discs_file = self.bp_dir / "scripts" / "musicDisc" / "musicDiscs.js"
        self.jukebox_manager_file = self.bp_dir / "scripts" / "jukebox" / "jukeboxManager.js"
        self.jukebox_manager_dist_file = self.bp_template_dir / "scripts" / "jukebox" / "jukeboxManager.dist.js"
        
        # Plik z sumami kontrolnymi
        self.checksums_file = self.project_root / ".ogg_checksums.json"
        
        # Namespace
        self.namespace = "personal_music_compilation"
        
        # Utworzenie katalogów, jeśli nie istnieją
        self._create_directories()
    
    def _create_directories(self):
        """Tworzy niezbędne katalogi, jeśli nie istnieją."""
        directories = [
            self.items_dir,
            self.sounds_dir,
            self.textures_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _to_snake_case(text: str) -> str:
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
                print(ConsoleStyle.info(f"Processing specific file [{specific_file}]"))
                return [file_path]
            else:
                print(ConsoleStyle.error(f"File [{specific_file}] does not exist or is not an MP3 file!"))
                return []
        
        if not self.src_dir.exists():
            print(ConsoleStyle.error(f"Katalog [{self.src_dir}] nie istnieje!"))
            return []
        
        mp3_files = list(self.src_dir.glob("*.mp3"))
        print(ConsoleStyle.info(f"Found [{len(mp3_files)}] MP3 files in [{self.src_dir}]"))
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
                print(ConsoleStyle.success(f"Extracted artwork from [{mp3_file.name}] (32x32px)"))
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
                        print(ConsoleStyle.success(f"Used default image for [{mp3_file.name}] (32x32px)"))
                        return True
                    else:
                        print(ConsoleStyle.warning(f"Cannot scale default image for [{mp3_file.name}]"))
                        return False
                else:
                    print(ConsoleStyle.warning(f"Cannot find default image for [{mp3_file.name}]"))
                    return False
                    
        except Exception as e:
            print(ConsoleStyle.error(f"Error extracting artwork from [{mp3_file.name}]: {e}"))
            return False

    @staticmethod
    def _get_file_checksum(file_path: Path) -> str:
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
                print(ConsoleStyle.warning(f"Error loading checksums: {e}"))
        return {}
    
    def _save_checksums(self, checksums: Dict[str, str]):
        """Zapisuje sumy kontrolne do pliku."""
        try:
            with open(self.checksums_file, 'w', encoding='utf-8') as f:
                json.dump(checksums, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(ConsoleStyle.warning(f"Error saving checksums: {e}"))
    
    def _convert_mp3_to_ogg(self, mp3_file: Path, ogg_file: Path) -> bool:
        """Konwertuje plik MP3 do formatu OGG ze sprawdzaniem sum kontrolnych."""
        # Sprawdź, czy plik OGG już istnieje i ma tę samą sumę kontrolną
        checksums = self._load_checksums()
        mp3_checksum = self._get_file_checksum(mp3_file)
        
        if ogg_file.exists() and mp3_checksum in checksums:
            existing_checksum = self._get_file_checksum(ogg_file)
            if existing_checksum == checksums[mp3_checksum]:
                print(ConsoleStyle.info(f"Skipped conversion [{mp3_file.name}] (OGG file already exists)"))
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
                
                print(ConsoleStyle.success(f"Converted [{mp3_file.name}] to [{ogg_file.name}]"))
                return True
            else:
                print(ConsoleStyle.error(f"Error converting [{mp3_file.name}]: {result.stderr}"))
                return False
                
        except Exception as e:
            print(ConsoleStyle.error(f"Error converting [{mp3_file.name}]: {e}"))
            return False
    
    def _create_item_json(self, disc_name: str, display_name: str) -> Dict:
        """Tworzy JSON dla itemu płyty muzycznej."""
        return {
            "format_version": "1.21.60",
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
                        "value": f"§bPersonal Music Compilation\n§7{display_name}"
                    },
                    "minecraft:max_stack_size": 1
                }
            }
        }
    
    def _update_jukebox_json(self, disc_names: List[str]):
        """Aktualizuje jukebox.json, dodając nowe płyty do dynamicznych sekcji custom_disc_X i vanilla_disc_X."""
        ConsoleStyle.print_section("Adding disc list to jukebox")
        if not self.jukebox_dist_file.exists():
            print(ConsoleStyle.error(f"File [{self.jukebox_dist_file}] does not exist!"))
            return False
        
        # Skopiuj plik dist do głównego pliku
        shutil.copy2(self.jukebox_dist_file, self.jukebox_file)
        
        try:
            with open(self.jukebox_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Usuń minecraft:cardinal_direction z traits i states
            if "traits" in data["minecraft:block"]["description"]:
                traits = data["minecraft:block"]["description"]["traits"]
                if "minecraft:placement_direction" in traits:
                    del traits["minecraft:placement_direction"]
                if not traits:  # Jeśli traits jest puste, usuń cały obiekt
                    del data["minecraft:block"]["description"]["traits"]

            # Usuń minecraft:cardinal_direction ze states
            states = data["minecraft:block"]["description"]["states"]
            if "minecraft:cardinal_direction" in states:
                del states["minecraft:cardinal_direction"]

            # Usuń permutacje związane z minecraft:cardinal_direction
            permutations = data["minecraft:block"]["permutations"]
            permutations_to_remove = []
            for i, permutation in enumerate(permutations):
                if "condition" in permutation and "minecraft:cardinal_direction" in permutation["condition"]:
                    permutations_to_remove.append(i)

            # Usuń permutacje od końca (żeby nie zmieniać indeksów)
            for i in reversed(permutations_to_remove):
                del permutations[i]
            
            states = data["minecraft:block"]["description"]["states"]
            
            # Aktualizuj sekcje vanilla_disc_X
            self._update_vanilla_disc_sections(states)
            
            # Oblicz ile sekcji potrzeba (maksymalnie 15 płyt na sekcję)
            discs_per_section = 15
            num_sections = max(1, (len(disc_names) + discs_per_section - 1) // discs_per_section)
            
            print(ConsoleStyle.info(f"Creating [{num_sections}] sections for [{len(disc_names)}] discs"))
            
            # Usuń wszystkie istniejące sekcje custom_disc_X
            keys_to_remove = []
            for key in states.keys():
                if key.startswith("personal_music_compilation:custom_disc_"):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del states[key]
            
            # Utwórz dynamiczne sekcje
            for section_num in range(1, num_sections + 1):
                section_key = f"personal_music_compilation:custom_disc_{section_num}"
                section_discs = ["none"]
                
                # Dodaj płyty do tej sekcji
                start_idx = (section_num - 1) * discs_per_section
                end_idx = min(start_idx + discs_per_section, len(disc_names))
                
                for i in range(start_idx, end_idx):
                    disc_identifier = f"{self.namespace}:music_disc_{disc_names[i]}"
                    section_discs.append(disc_identifier)
                    print(ConsoleStyle.success(f"Added disc [{disc_identifier}] to jukebox in section {section_num}."))
                
                states[section_key] = section_discs
            
            # Zaktualizuj warunki w permutations
            self._update_permutations_conditions(data, num_sections)
            
            with open(self.jukebox_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(ConsoleStyle.success(f"Updated [{self.jukebox_file}] with {num_sections} sections"))
            
            # Zaktualizuj jukeboxManager.js
            self._update_jukebox_manager_js(num_sections)
            
            return True
            
        except Exception as e:
            print(ConsoleStyle.error(f"Error updating [{self.jukebox_file}]: {e}"))
            return False
    
    def _update_vanilla_disc_sections(self, states: Dict):
        """Aktualizuje sekcje vanilla_disc_1 i vanilla_disc_2 na podstawie minecraft.music_disc.json."""
        minecraft_discs_file = self.src_dir / "minecraft.music_disc.json"
        
        if not minecraft_discs_file.exists():
            print(ConsoleStyle.warning(f"File [{minecraft_discs_file}] does not exist, skipping vanilla sections update"))
            return
        
        try:
            with open(minecraft_discs_file, 'r', encoding='utf-8') as f:
                minecraft_discs_data = json.load(f)
            
            # Usuń istniejące sekcje vanilla_disc_X
            keys_to_remove = []
            for key in states.keys():
                if key.startswith("personal_music_compilation:vanilla_disc_"):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del states[key]
            
            # Podziel płyty vanilla na sekcje (maksymalnie 15 na sekcję)
            discs_per_section = 15
            vanilla_discs = []
            
            for disc_data in minecraft_discs_data:
                disc_id = disc_data["id"]
                vanilla_discs.append(f"minecraft:music_disc_{disc_id}")
            
            # Oblicz ile sekcji potrzeba
            num_vanilla_sections = max(1, (len(vanilla_discs) + discs_per_section - 1) // discs_per_section)
            
            print(ConsoleStyle.info(f"Creating [{num_vanilla_sections}] vanilla sections for [{len(vanilla_discs)}] discs"))
            
            # Utwórz sekcje vanilla_disc_X
            for section_num in range(1, num_vanilla_sections + 1):
                section_key = f"personal_music_compilation:vanilla_disc_{section_num}"
                section_discs = ["none"]
                
                # Dodaj płyty do tej sekcji
                start_idx = (section_num - 1) * discs_per_section
                end_idx = min(start_idx + discs_per_section, len(vanilla_discs))
                
                for i in range(start_idx, end_idx):
                    disc_identifier = vanilla_discs[i]
                    section_discs.append(disc_identifier)
                    print(ConsoleStyle.success(f"Added vanilla disc [{disc_identifier}] to jukebox in section {section_num}."))
                
                states[section_key] = section_discs
            
        except Exception as e:
            print(ConsoleStyle.error(f"Error updating vanilla sections: {e}"))

    @staticmethod
    def _update_permutations_conditions(data: Dict, num_sections: int):
        """Aktualizuje warunki w permutations, aby uwzględnić wszystkie sekcje custom_disc_X."""
        permutations = data["minecraft:block"]["permutations"]

        # Warunek dla pustego jukebox (wszystkie sekcje == 'none')
        empty_condition_parts = [
            "q.block_state('personal_music_compilation:vanilla_disc_1') == 'none'",
            "q.block_state('personal_music_compilation:vanilla_disc_2') == 'none'"
        ]

        # Warunek dla grającego jukebox (przynajmniej jedna sekcja != 'none')
        playing_condition_parts = [
            "q.block_state('personal_music_compilation:vanilla_disc_1') != 'none'",
            "q.block_state('personal_music_compilation:vanilla_disc_2') != 'none'"
        ]

        # Dodaj warunki dla wszystkich sekcji custom_disc_X
        for section_num in range(1, num_sections + 1):
            section_key = f"personal_music_compilation:custom_disc_{section_num}"
            empty_condition_parts.append(f"q.block_state('{section_key}') == 'none'")
            playing_condition_parts.append(f"q.block_state('{section_key}') != 'none'")

        # Zaktualizuj pierwsze dwa permutations (pusty i grający jukebox)
        # if len(permutations) >= 2:
        permutations[0]["condition"] = " && ".join(empty_condition_parts)
        permutations[1]["condition"] = " || ".join(playing_condition_parts)

    def _update_sound_definitions(self, disc_names: List[str]):
        """Aktualizuje sound_definitions.json, dodając nowe definicje dźwięków."""
        ConsoleStyle.print_section("Updating sound definitions")
        if not self.sound_definitions_dist_file.exists():
            print(ConsoleStyle.error(f"File [{self.sound_definitions_dist_file}] does not exist!"))
            return False
        
        # Skopiuj plik dist do głównego pliku
        shutil.copy2(self.sound_definitions_dist_file, self.sound_definitions_file)
        
        try:
            with open(self.sound_definitions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sound_definitions = data["sound_definitions"]
            
            # Usuń wszystkie istniejące wpisy 'record.' dla płyt personal_music_compilation:
            to_remove = []
            for key in sound_definitions.keys():
                if key.startswith("record."):
                    disc_name = key.replace("record.", "")
                    if disc_name not in disc_names:
                        to_remove.append(key)
            
            for key in to_remove:
                del sound_definitions[key]
                print(ConsoleStyle.delete(f"Removed sound definition [{key}]"))
            
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
                                "name": f"sounds/items/{disc_name}",
                                "stream": True,
                                "volume": 0.50
                            }
                        ]
                    }
                    print(ConsoleStyle.success(f"Added sound definition [{sound_key}]"))
            
            with open(self.sound_definitions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(ConsoleStyle.success(f"Updated [{self.sound_definitions_file}]"))
            return True
            
        except Exception as e:
            print(ConsoleStyle.error(f"Error updating [{self.sound_definitions_file}]: {e}"))
            return False
    
    def _update_item_texture(self, disc_names: List[str]):
        ConsoleStyle.print_section("Updating textures")
        """Aktualizuje item_texture.json dodając nowe tekstury."""
        if not self.item_texture_dist_file.exists():
            print(ConsoleStyle.error(f"File [{self.item_texture_dist_file}] does not exist!"))
            return False
        
        # Skopiuj plik dist do głównego pliku
        shutil.copy2(self.item_texture_dist_file, self.item_texture_file)
        
        try:
            with open(self.item_texture_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            texture_data = data["texture_data"]
            
            # Usuń wszystkie istniejące wpisy dla płyt `personal_music_compilation:`
            to_remove = []
            for key in texture_data.keys():
                if key.startswith("personal_music_compilation:music_disc_"):
                    disc_name = key.replace("personal_music_compilation:music_disc_", "")
                    if disc_name not in disc_names:
                        to_remove.append(key)
            
            for key in to_remove:
                del texture_data[key]
                print(ConsoleStyle.delete(f"Removed texture entry [{key}]"))
            
            # Dodaj nowe wpisy
            for disc_name in disc_names:
                texture_key = f"{self.namespace}:music_disc_{disc_name}"
                if texture_key not in texture_data:
                    texture_data[texture_key] = {
                        "textures": f"textures/items/music_disc_{disc_name}"
                    }
                    print(ConsoleStyle.success(f"Added texture definition [{texture_key}]"))

            with open(self.item_texture_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(ConsoleStyle.success(f"Updated [{self.item_texture_file}]"))
            return True
            
        except Exception as e:
            print(ConsoleStyle.error(f"Error updating [{self.item_texture_file}]: {e}"))
            return False
    
    def _cleanup_old_files(self, current_disc_names: List[str]):
        """Usuwa pliki dla płyt, które nie są przetworzone z src/."""
        ConsoleStyle.print_section("Cleaning old files")

        # Sprawdź istniejące pliki dźwięków
        if self.sounds_dir.exists():
            for sound_file in self.sounds_dir.glob("*.ogg"):
                sound_name = sound_file.stem
                if sound_name not in current_disc_names:
                    sound_file.unlink()
                    print(ConsoleStyle.delete(f"Removed old sound file [{sound_file.name}]."))
        
        # Sprawdź istniejące tekstury
        if self.textures_dir.exists():
            for texture_file in self.textures_dir.glob("music_disc_*.png"):
                texture_name = texture_file.stem.replace("music_disc_", "")
                if texture_name not in current_disc_names:
                    texture_file.unlink()
                    print(ConsoleStyle.delete(f"Removed old texture [{texture_file.name}]."))
        
        # Usuń nadmiarowe pliki itemów
        if self.items_dir.exists():
            for item_file in self.items_dir.glob("music_disc_*.item.json"):
                item_name = item_file.stem.replace("music_disc_", "").replace(".item", "")
                if item_name not in current_disc_names:
                    item_file.unlink()
                    print(ConsoleStyle.delete(f"Removed redundant item file [{item_file.name}]."))

    def _update_jukebox_manager_js(self, num_sections: int):
        """Aktualizuje `jukeboxManager.js` z dynamicznymi sekcjami `custom_disc_X`."""
        if not self.jukebox_manager_dist_file.exists():
            print(ConsoleStyle.error(f"Template file [{self.jukebox_manager_dist_file}] does not exist!"))
            return
        
        # Wczytaj szablon
        with open(self.jukebox_manager_dist_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Generuj definicje `custom_disc_X`
        custom_disc_states = []
        custom_disc_states_array = []
        
        for i in range(1, num_sections + 1):
            custom_disc_states.append(f'    JukeboxStates["Custom_Disc_{i}"] = "{self.namespace}:custom_disc_{i}";')
            custom_disc_states_array.append(f'    JukeboxStates.Custom_Disc_{i}')
        
        # Zastąp placeholdery
        template_content = template_content.replace('{{CUSTOM_DISC_STATES}}', '\n'.join(custom_disc_states))

        # Zastąp placeholdery
        if num_sections == 0:
            template_content = template_content.replace('{{CUSTOM_DISC_STATES_ARRAY}}', '')
        else:
            template_content = template_content.replace('{{CUSTOM_DISC_STATES_ARRAY}}', ',\n' + ',\n'.join(custom_disc_states_array))
        
        # Zapisz wygenerowany plik
        with open(self.jukebox_manager_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(ConsoleStyle.success(f"Updated [{self.jukebox_manager_file}] with {num_sections} custom_disc_X sections"))

    def _update_music_discs_js(self, disc_names: List[str]):
        """Aktualizuje musicDiscs.js z nowymi płytami."""
        ConsoleStyle.print_section("Updating disc list")

        # Ścieżka do pliku minecraft.music_disc.json
        minecraft_discs_file = self.src_dir / "minecraft.music_disc.json"

        try:
            minecraft_discs_array = []
            custom_disc_array = []
            
            # Wczytaj dane z minecraft.music_disc.json
            if minecraft_discs_file.exists():
                try:
                    with open(minecraft_discs_file, 'r', encoding='utf-8') as f:
                        minecraft_discs_data = json.load(f)
                    
                    # Dodaj płytę vanilla z pliku JSON
                    for disc_data in minecraft_discs_data:
                        disc_id = disc_data["id"]
                        music_name = disc_data["musicName"]
                        artist = disc_data["artist"]
                        tick_length = disc_data["tickLength"]
                        
                        minecraft_discs_array.append(f'    "minecraft:music_disc_{disc_id}": {{\n'
                                                   f'        musicName: "{music_name}",\n'
                                                   f'        artist: "{artist}",\n'
                                                   f'        sound: {{\n'
                                                   f'            volume: 1,\n'
                                                   f'            id: "record.{disc_id}",\n'
                                                   f'            tickLength: {tick_length}\n'
                                                   f'        }}\n'
                                                   f'    }}')
                        
                        print(ConsoleStyle.success(f"Added disc [minecraft:music_disc_{disc_id}] ({artist} - {music_name}) to list."))
                        
                except Exception as e:
                    print(ConsoleStyle.error(f"Error loading [{minecraft_discs_file}]: {e}"))
            else:
                print(ConsoleStyle.warning(f"File [{minecraft_discs_file}] does not exist, skipping vanilla discs"))
            
            # Dodaj nowe wpisy personal_music_compilation:
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
                        print(ConsoleStyle.warning(f"Cannot calculate duration for [{disc_name}]: {e}"))
                
                # Dodaj nowy wpis
                custom_disc_array.append(f'    "personal_music_compilation:music_disc_{disc_name}": {{\n'
                                         f'        musicName: "{title}",\n'
                                         f'        artist: "{artist}",\n'
                                         f'        sound: {{\n'
                                         f'            volume: 1,\n'
                                         f'            id: "record.{disc_name}",\n'
                                         f'            tickLength: {tick_length}\n'
                                         f'        }}\n'
                                         f'    }}')

                print(ConsoleStyle.success(f"Added disc [personal_music_compilation:music_disc_{disc_name}] ({artist} - {title}) to list."))

            # Połącz wszystkie płyty (vanilla + custom)
            all_discs = minecraft_discs_array + custom_disc_array
            
            # Zapisz wygenerowany plik
            with open(self.music_discs_file, 'w', encoding='utf-8') as f:
                all_discs_string = '\n'.join(all_discs)
                newline = '\n'
                content = f"export const musicDiscs = {{{newline}{all_discs_string}{newline}}};"
                f.write(content)

            print(ConsoleStyle.success(f"Updated [{self.music_discs_file}]"))
            
        except Exception as e:
            print(ConsoleStyle.error(f"Error updating [{self.music_discs_file}]: {e}"))
    
    def clear_all(self, specific_file: Optional[str] = None):
        """Usuwa wszystkie wygenerowane pliki lub konkretny plik."""
        if specific_file:
            ConsoleStyle.print_section(f"Cleanup specific file: {specific_file}", icon="🗑️")
            return self._clear_specific_file(specific_file)
        else:
            ConsoleStyle.print_section("Cleanup all generated files", icon="🗑️")
            return self._clear_all_files()
    
    def _remove_config_files(self):
        """Remove all config files (sound_definitions.json, item_texture.json, jukebox.block.json, musicDiscs.js)."""
        config_files = [
            self.sound_definitions_file,
            self.item_texture_file,
            self.jukebox_file,
            self.music_discs_file
        ]
        for f in config_files:
            if f.exists():
                try:
                    f.unlink()
                    print(ConsoleStyle.delete(f"Removed config file [{f.name}]"))
                except Exception as e:
                    print(ConsoleStyle.error(f"Error removing config file [{f.name}]: {e}"))

    def _regenerate_config_files(self):
        """Regenerate config files based on current MP3s."""
        mp3_files = self._get_mp3_files()
        disc_names = [self._to_snake_case(mp3.name) for mp3 in mp3_files]
        self._update_sound_definitions(disc_names)
        self._update_item_texture(disc_names)
        self._update_jukebox_json(disc_names)
        self._update_music_discs_js(disc_names)

    def _clear_specific_file(self, file_name: str) -> int:
        """Usuwa pliki dla konkretnego dysku muzycznego."""
        files_removed = 0
        
        # Sprawdź czy to jest identyfikator (snake_case) czy nazwa pliku MP3
        if file_name.startswith("music_disc_"):
            # To jest identyfikator - usuń prefix "music_disc_"
            disc_name = file_name.replace("music_disc_", "")
        else:
            # To jest nazwa pliku MP3 - konwertuj do snake_case
            disc_name = self._to_snake_case(file_name)
        
        # Usuń plik dźwięku OGG
        ogg_file = self.sounds_dir / f"{disc_name}.ogg"
        if ogg_file.exists():
            try:
                ogg_file.unlink()
                print(ConsoleStyle.delete(f"Removed sound file [{ogg_file.name}]"))
                files_removed += 1
            except Exception as e:
                print(ConsoleStyle.error(f"Error removing [{ogg_file.name}]: {e}"))
        
        # Usuń teksturę
        texture_file = self.textures_dir / f"music_disc_{disc_name}.png"
        if texture_file.exists():
            try:
                texture_file.unlink()
                print(ConsoleStyle.delete(f"Removed texture [{texture_file.name}]"))
                files_removed += 1
            except Exception as e:
                print(ConsoleStyle.error(f"Error removing [{texture_file.name}]: {e}"))
        
        # Usuń plik itemu
        item_file = self.items_dir / f"music_disc_{disc_name}.item.json"
        if item_file.exists():
            try:
                item_file.unlink()
                print(ConsoleStyle.delete(f"Removed item file [{item_file.name}]"))
                files_removed += 1
            except Exception as e:
                print(ConsoleStyle.error(f"Error removing [{item_file.name}]: {e}"))
        
        if files_removed > 0:
            print(ConsoleStyle.success(f"Removed [{files_removed}] files for [{file_name}]"))
        else:
            print(ConsoleStyle.info(f"No files found for [{file_name}]"))
        # Regenerate config files after single removal
        self._regenerate_config_files()
        return files_removed
    
    def _clear_all_files(self) -> int:
        """Usuwa wszystkie wygenerowane pliki."""
        files_removed = 0
        
        # Usuń wszystkie pliki dźwięków OGG
        if self.sounds_dir.exists():
            for sound_file in self.sounds_dir.glob("*.ogg"):
                try:
                    sound_file.unlink()
                    print(ConsoleStyle.delete(f"Removed sound file [{sound_file.name}]"))
                    files_removed += 1
                except Exception as e:
                    print(ConsoleStyle.error(f"Error removing [{sound_file.name}]: {e}"))
        
        # Usuń wszystkie tekstury dysków muzycznych
        if self.textures_dir.exists():
            for texture_file in self.textures_dir.glob("music_disc_*.png"):
                try:
                    texture_file.unlink()
                    print(ConsoleStyle.delete(f"Removed texture [{texture_file.name}]"))
                    files_removed += 1
                except Exception as e:
                    print(ConsoleStyle.error(f"Error removing [{texture_file.name}]: {e}"))
        
        # Usuń wszystkie pliki itemów dysków muzycznych
        if self.items_dir.exists():
            for item_file in self.items_dir.glob("music_disc_*.item.json"):
                try:
                    item_file.unlink()
                    print(ConsoleStyle.delete(f"Removed item file [{item_file.name}]"))
                    files_removed += 1
                except Exception as e:
                    print(ConsoleStyle.error(f"Error removing [{item_file.name}]: {e}"))
        
        # Usuń plik sum kontrolnych
        checksums_file = self.project_root / ".ogg_checksums.json"
        if checksums_file.exists():
            try:
                checksums_file.unlink()
                print(ConsoleStyle.delete(f"Removed checksums file [{checksums_file.name}]"))
                files_removed += 1
            except Exception as e:
                print(ConsoleStyle.error(f"Error removing [{checksums_file.name}]: {e}"))
        
        if files_removed > 0:
            print(ConsoleStyle.success(f"Removed [{files_removed}] files"))
        else:
            print(ConsoleStyle.info("No files found to remove"))
        # Remove config files after full cleanup
        self._remove_config_files()
        return files_removed

    def process_mp3_files(self, specific_file: Optional[str] = None):
        """Główna funkcja przetwarzająca pliki MP3."""
        ConsoleStyle.print_section("Minecraft Music Disc Generator")
        
        # Sprawdź, czy ffmpeg jest dostępny
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(ConsoleStyle.error("ffmpeg is not installed or not available!"))
            print(ConsoleStyle.info("Install ffmpeg: https://ffmpeg.org/download.html"))
            sys.exit(1)
        
        mp3_files = self._get_mp3_files(specific_file)
        if not mp3_files:
            print(ConsoleStyle.error("No MP3 files found to process!"))
            return
        
        processed_disc_names = []
        errors = []
        
        for i, mp3_file in enumerate(mp3_files, 1):
            print(ConsoleStyle.divider('-'))
            print(ConsoleStyle.process(f"Processing [{mp3_file.name}] ({i}/{len(mp3_files)})"))
            
            # Konwertuj nazwę pliku do snake_case
            disc_name = self._to_snake_case(mp3_file.name)
            display_name = mp3_file.stem  # Oryginalna nazwa bez rozszerzenia
            
            print(ConsoleStyle.info(f"Disc name: {disc_name}"))
            print(ConsoleStyle.info(f"Display name: {display_name}"))
            
            try:
                # Utwórz plik itemu
                item_file = self.items_dir / f"music_disc_{disc_name}.item.json"
                item_data = self._create_item_json(disc_name, display_name)
                
                with open(item_file, 'w', encoding='utf-8') as f:
                    json.dump(item_data, f, indent=4, ensure_ascii=False)
                print(ConsoleStyle.success(f"Created item: {item_file.name}"))
                
                # Konwertuj MP3 do OGG
                ogg_file = self.sounds_dir / f"{disc_name}.ogg"
                if self._convert_mp3_to_ogg(mp3_file, ogg_file):
                    processed_disc_names.append(disc_name)
                
                # Wyciągnij artwork
                texture_file = self.textures_dir / f"music_disc_{disc_name}.png"
                self._extract_artwork(mp3_file, texture_file)
                
            except Exception as e:
                error_msg = f"Error processing {mp3_file.name}: {e}"
                print(ConsoleStyle.error(error_msg))
                errors.append(error_msg)
        
        # Aktualizuj pliki konfiguracyjne
        if processed_disc_names:

            # Aktualizuj sound_definitions.json
            self._update_sound_definitions(processed_disc_names)

            # Aktualizuj item_texture.json
            self._update_item_texture(processed_disc_names)

            # Aktualizuj jukebox.json
            self._update_jukebox_json(processed_disc_names)

        # Czyszczenie starych plików
        self._cleanup_old_files(processed_disc_names)

        # Aktualizuj musicDiscs.js
        self._update_music_discs_js(processed_disc_names)

        # Podsumowanie
        ConsoleStyle.print_summary(len(processed_disc_names), len(mp3_files), errors)
        
        if processed_disc_names:
            print(ConsoleStyle.info(f"New discs: {', '.join(processed_disc_names)}"))
    
    def _get_artist_and_title_from_mp3(self, disc_name: str) -> Tuple[str, str]:
        """Wyciąga artystę i tytuł z pliku MP3 na podstawie nazwy płyty."""
        mp3_files = list(self.src_dir.glob("*.mp3"))
        artist = "Unknown_Artist"
        title = disc_name.replace("_", " ").title()
        
        for mp3_file in mp3_files:
            if self._to_snake_case(mp3_file.name) == disc_name:
                # Wyciągnij artystę i tytuł z nazwy pliku
                file_name = mp3_file.stem
                if " - " in file_name:
                    artist_part, title_part = file_name.split(" - ", 1)
                    artist = artist_part.strip()
                    title = title_part.strip()
                break
        
        return artist, title

def main():
    """Główna funkcja skryptu."""
    parser = argparse.ArgumentParser(description="Generator Płyt Muzycznych dla Minecraft")
    parser.add_argument("--file", "-f", help="Konwertuj konkretny plik MP3 z katalogu src/")
    parser.add_argument("--clear", "-c", action="store_true", help="Clean all generated files")
    args = parser.parse_args()
    
    # Sprawdź, czy jesteśmy w katalogu projektu
    project_root = os.getcwd()
    
    if not os.path.exists(os.path.join(project_root, "BP")) or not os.path.exists(os.path.join(project_root, "RP")):
        print(ConsoleStyle.error("BP and RP directories not found! Make sure you are in the project directory."))
        return

    generator = MusicDiscGenerator(project_root)

    if args.clear:
        # Usuń wskazany plik lubwszystkie pliki
        generator.clear_all(args.file)
        return
    
    if args.file:
        # Tryb normalnego przetwarzania
        generator.process_mp3_files(args.file)
        return

    generator.process_mp3_files(args.file)

if __name__ == "__main__":
    main() 