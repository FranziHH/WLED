import os
import re
Import("env")
import json
import shutil
from datetime import datetime

def copy_bin(source, target, env):
    hwKey = "wled"
    current_date = datetime.now().strftime("%Y-%m-%d")

    build_flags = env.get("BUILD_FLAGS", [])
    
    for flag in build_flags:
        if "WLED_RELEASE_NAME" in flag:
            match = re.search(r'\\"(.*?)\\"', flag)
            if match:
                release_name = match.group(1)
            break

    with open("package.json", "r") as package:
        version = json.load(package)["version"] 

    project_dir = env.subst("$PROJECT_DIR")
    release_dir = os.path.join(project_dir, "build_output", "release")
    merge_dir = os.path.join(project_dir, "build_output", "merge")
    docs_dir = os.path.abspath(project_dir + "/../Lepro TB1 WLED/docs")
    fw_dir = os.path.abspath(docs_dir + "/firmware")
    fw_dir_local = os.path.abspath(project_dir + "/firmware/lepro_tb1")

    # create folder
    os.makedirs(fw_dir, exist_ok=True)
    os.makedirs(fw_dir_local, exist_ok=True)

    source_file = os.path.join(release_dir, f"WLED_{version}_{release_name}.bin")
    ota_file = f"{current_date}_WLED_{version}_{release_name}_ota.bin"
    output_file = os.path.join(fw_dir, ota_file)
    shutil.copy(source_file, output_file)
    output_file = os.path.join(fw_dir_local, ota_file)
    shutil.copy(source_file, output_file)

    source_file = os.path.join(merge_dir, f"WLED_{version}_{release_name}_full.bin")
    full_file = f"{current_date}_WLED_{version}_{release_name}_full.bin"
    output_file = os.path.join(fw_dir, full_file)
    shutil.copy(source_file, output_file)
    output_file = os.path.join(fw_dir_local, full_file)
    shutil.copy(source_file, output_file)

    json_path = os.path.join(docs_dir, "versions.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = False
        # Check für FULL
        if os.path.exists(os.path.join(fw_dir, full_file)):
            existing_item = next((item for item in data[hwKey]["full"] if item['id'] == full_file), None)
            if existing_item:
                # Eintrag aktualisieren
                existing_item["name"] = f"{current_date} {version}"
                updated = True
            else:
                data[hwKey]["full"].insert(0, {"id": full_file, "name": f"{current_date} {version}", "offset": "0x0"})
                updated = True

        # Check für UPDATE (App)
        if os.path.exists(os.path.join(fw_dir, ota_file)):
            existing_item = next((item for item in data[hwKey]["update"] if item['id'] == ota_file), None)
            if existing_item:
                # Eintrag aktualisieren
                existing_item["name"] = f"{current_date} {version}"
                updated = True
            else:
                data[hwKey]["update"].insert(0, {"id": ota_file, "name": f"{current_date} {version}", "offset": "0x10000"})
                updated = True

        if updated:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print("JSON erfolgreich aktualisiert.")

# Registrierung des Scripts nach dem Build
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", copy_bin)