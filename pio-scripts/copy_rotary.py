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
    fw_dir = os.path.abspath(project_dir + "/firmware/rotary")

    # create folder
    os.makedirs(fw_dir, exist_ok=True)
    
    source_file = os.path.join(release_dir, f"WLED_{version}_{release_name}.bin")
    ota_file = f"{current_date}_WLED_{version}_{release_name}_ota.bin"
    output_file = os.path.join(fw_dir, ota_file)
    shutil.copy(source_file, output_file)

    source_file = os.path.join(merge_dir, f"WLED_{version}_{release_name}_full.bin")
    full_file = f"{current_date}_WLED_{version}_{release_name}_full.bin"
    output_file = os.path.join(fw_dir, full_file)
    shutil.copy(source_file, output_file)

# Registrierung des Scripts nach dem Build
env.AddPostAction("$BUILD_DIR/${PROGNAME}.bin", copy_bin)