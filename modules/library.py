import os
import json
import datetime
from tabulate import tabulate
from modules.utils import create_folder, count_files_in_dirs

ARCHIVE_PATH = None
INPUT_FOLDER_NAME = None
IMAGES_EXTENSIONS = None
INPUT_PATH = None

def create_library(library_name:str) -> None:
    create_folder(os.path.join(ARCHIVE_PATH, library_name))
    with open(os.path.join(ARCHIVE_PATH, library_name, "config.json"), "w") as file:
        json.dump({"name": library_name, "file_extensions":[]}, file, indent=4)

def load_libraries() -> list[dict]:
    libraries = []
    for library in os.listdir(ARCHIVE_PATH):
        if os.path.isdir(os.path.join(ARCHIVE_PATH, library)):
            if library == INPUT_FOLDER_NAME:
                continue
            if not(os.path.exists(os.path.join(ARCHIVE_PATH, library, "config.json"))):
                print(f"Config file not found for library {library}. Recreating it...")
                create_library(library)
            with open(os.path.join(ARCHIVE_PATH, library, "config.json"), "r") as file:
                json_data = json.load(file)
                json_data["photos"] = count_files_in_dirs(
                    os.path.join(ARCHIVE_PATH, library),
                    IMAGES_EXTENSIONS
                    )
                json_data["archives"] = count_files_in_dirs(
                    os.path.join(ARCHIVE_PATH, library),
                    [".zip"]
                    )
                libraries.append(json_data)
    return libraries

def display_libraries() -> None:
    libraries = load_libraries()
    for l in libraries:
        l["file_extensions"] = " ".join(l["file_extensions"])
    print(tabulate(libraries, headers="keys", tablefmt="fancy_grid"))

def get_photo_destinations(mode:str) -> list[dict]:
    if mode == "AUTO":
        LIBRARIES = load_libraries()
        l = []
        for f in os.listdir(INPUT_PATH):
            if os.path.isfile(os.path.join(INPUT_PATH, f)) and f.lower().endswith(tuple(ext.lower() for ext in IMAGES_EXTENSIONS)):
                file_extension = f.split(".")[-1].lower()
                found = False
                for library in LIBRARIES:
                    file_exts = library["file_extensions"] if isinstance(library["file_extensions"], list) else library["file_extensions"].split()
                    file_exts = [ext.lower() for ext in file_exts]
                    if file_extension in file_exts:
                        l.append({
                            "name":f,
                            "destination":library["name"],
                            "creation_date": datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(INPUT_PATH, f))).strftime("%Y-%m-%d"),
                            "size": f"{os.path.getsize(os.path.join(INPUT_PATH, f))} bytes"
                        })
                        found = True
                        break
                if not found:
                    l.append({
                            "name":f,
                            "destination":"?",
                            "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(INPUT_PATH, f))).strftime("%Y-%m-%d"),
                            "size": f"{os.path.getsize(os.path.join(INPUT_PATH, f))} bytes"
                    })
        return l
    else:
        if not(os.path.exists(os.path.join(ARCHIVE_PATH, mode))):
            print(f"Library {mode} not found.")
            return [
                {
                    "name":f,
                    "destination":"?",
                    "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(INPUT_PATH, f))).strftime("%Y-%m-%d"),
                    "size": f"{os.path.getsize(os.path.join(INPUT_PATH, f))} bytes"
                }
                for f in os.listdir(INPUT_PATH) if os.path.isfile(os.path.join(INPUT_PATH, f))
            ]
        else:
            return [
                {
                    "name":f,
                    "destination":mode,
                    "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(INPUT_PATH, f))).strftime("%Y-%m-%d"),
                    "size": f"{os.path.getsize(os.path.join(INPUT_PATH, f))} bytes"
                }
                for f in os.listdir(INPUT_PATH) if os.path.isfile(os.path.join(INPUT_PATH, f))
            ]
