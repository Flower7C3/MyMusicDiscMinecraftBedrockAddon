#!/usr/bin/env python3
"""
Comprehensive verification script for Minecraft Bedrock Addon
Verifies project structure, files, textures, and build readiness
"""
from minecraft_check import MinecraftUtils


def main():
    """Main verification function"""
    MinecraftUtils.verification_summary([
        MinecraftUtils.verify_config,
        MinecraftUtils.verify_manifests,
        MinecraftUtils.verify_project_structure,
        MinecraftUtils.count_project_files,
        MinecraftUtils.verify_translations,
        MinecraftUtils.verify_blocks,
        MinecraftUtils.verify_textures,
    ])

if __name__ == "__main__":
    main()
