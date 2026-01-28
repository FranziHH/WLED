import os
import re
import sys
import subprocess
Import("env")
import json

python_path = sys.executable

try:
    import esptool
    major_version = int(esptool.__version__.split('.')[0])
    
    if major_version < 5:
        print(f"--- VERSION {esptool.__version__} ZU ALT. UPDATE AUF 5.1 ---")
        subprocess.check_call([python_path, "-m", "pip", "install", "esptool==5.1"])
        import importlib
        importlib.reload(esptool)
except (ImportError, ValueError):
    print("--- INSTALLIERE ESPTOOL 5.1 ---")
    subprocess.check_call([python_path, "-m", "pip", "install", "esptool==5.1"])
    import esptool

def merge_bin_action(source, target, env):
    # 1. Den Release-Namen aus den Build-Flags extrahieren
    build_flags = env.get("BUILD_FLAGS", [])
    merge_name = "WLED_merged" 
    
    for flag in build_flags:
        if "WLED_RELEASE_NAME" in flag:
            match = re.search(r'\\"(.*?)\\"', flag)
            if match:
                release_name = match.group(1)
            break

    # 2. Pfade definieren
    project_dir = env.subst("$PROJECT_DIR")
    build_dir = env.subst("$BUILD_DIR")

    with open("package.json", "r") as package:
        version = json.load(package)["version"]   

    # Zielordner: build_output/merge
    output_dir = os.path.join(project_dir, "build_output", "merge")
    output_file = os.path.join(output_dir, f"WLED_{version}_{release_name}_full.bin")
    
    # Falls der Ordner nicht existiert, erstellen wir ihn
    if not os.path.exists(output_dir):
        print(f"--- [MERGE] Erstelle Verzeichnis: {output_dir} ---")
        os.makedirs(output_dir)
    
    # Quelldateien definieren
    bootloader = os.path.join(build_dir, "bootloader.bin")
    partitions = os.path.join(build_dir, "partitions.bin")
    firmware = os.path.join(build_dir, "firmware.bin")
    # NEU: Das Filesystem-Image
    filesystem = os.path.join(build_dir, "littlefs.bin")

    if not all(os.path.isfile(f) for f in [bootloader, partitions, firmware]):
        print(f"--- [MERGE] Fehler: Binärdateien in {build_dir} nicht gefunden! ---")
        return

    # 3. Das esptool Kommando zusammenbauen
    cmd = [
        f'"{python_path}"', "-m", "esptool", "--chip", "esp32s3", "merge_bin",
        "-o", f"\"{output_file}\"",
        "0x0000", f"\"{bootloader}\"",
        "0x8000", f"\"{partitions}\"",
        "0x10000", f"\"{firmware}\""
    ]

    # NEU: Wenn das Filesystem existiert, hänge es an die Adresse 00x300000 an
    if os.path.isfile(filesystem):
        print(f"--- [MERGE] Füge Filesystem (Presets/Config) hinzu ---")
        cmd.extend(["0x310000", f"\"{filesystem}\""])
    else:
        print(f"--- [MERGE] HINWEIS: Keine littlefs.bin gefunden. Erzeuge Image ohne Presets. ---")

    print(f"--- [MERGE] Schutz-Modus: Übernehme Bootloader-Header für build_output/merge/WLED_{version}_{release_name}_full.bin ---")
    env.Execute(" ".join(cmd))

# Registrierung des Scripts nach dem Build
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", merge_bin_action)