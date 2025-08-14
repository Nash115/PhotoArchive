import os
import json
import datetime
from tabulate import tabulate
from dotenv import load_dotenv
import zipfile
import shutil
from progressbar import ProgressBar

load_dotenv()

ARCHIVE_PATH = os.getenv("ARCHIVE_PATH", None)
INPUT_FOLDER_NAME = os.getenv("INPUT_FOLDER_NAME", "-Input-")

if ARCHIVE_PATH is None:
    print("No archive path specified. Please set the ARCHIVE_PATH environment variable.")
    exit(1)

if not os.path.exists(ARCHIVE_PATH):
    print(f"⚠️ WARNING: The archive path '{ARCHIVE_PATH}' does not exist.")
    exit(1)

INPUT_PATH = os.path.join(ARCHIVE_PATH, INPUT_FOLDER_NAME)
if not os.path.exists(INPUT_PATH):
    os.mkdir(INPUT_PATH)



def create_folder(folder_name:str) -> None:
    os.makedirs(folder_name, exist_ok=True)


def create_library(library_name:str) -> None:
    create_folder(os.path.join(ARCHIVE_PATH, library_name))
    with open(os.path.join(ARCHIVE_PATH, library_name, "config.json"), "w") as file:
        json.dump({"name": library_name, "file_extensions":[]}, file, indent=4)


def count_files_in_dirs(path: str, files_extensions: list[str]) -> int:
    count = 0
    for root, dirs, files in os.walk(path):
        files = [f for f in files if f.lower().endswith(tuple(files_extensions))]
        count += len(files)
    return count


def load_libraries() -> list[dict]:
    libraries = []
    for library in os.listdir(ARCHIVE_PATH):
        if os.path.isdir(os.path.join(ARCHIVE_PATH, library)):
            if not(os.path.exists(os.path.join(ARCHIVE_PATH, library, "config.json"))):
                print(f"Config file not found for library {library}. Recreating it...")
                create_library(library)
            with open(os.path.join(ARCHIVE_PATH, library, "config.json"), "r") as file:
                json_data = json.load(file)
                json_data["photos"] = count_files_in_dirs(
                    os.path.join(ARCHIVE_PATH, library),
                    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".nef", ".tiff", ".cr2", ".cr3", ".heic", ".webp"]
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
            if os.path.isfile(os.path.join(INPUT_PATH, f)):
                file_extension = f.split(".")[-1]
                found = False
                for library in LIBRARIES:
                    if file_extension in library["file_extensions"] or library["file_extensions"] == []:
                        l.append({
                            "name":f,
                            "destination":library["name"],
                            "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(INPUT_PATH, f))).strftime("%Y-%m-%d"),
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

def compress_folder(src, zip_dest):
    with zipfile.ZipFile(zip_dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(src):
            for file in files:
                complete_path = os.path.join(root, file)
                rel_path = os.path.relpath(complete_path, src)
                zipf.write(complete_path, rel_path)
    if os.path.exists(zip_dest):
        return 1

def decompress_zip(zip_src, dest_folder):
    with zipfile.ZipFile(zip_src, 'r') as zipf:
        zipf.extractall(dest_folder)
    if os.path.exists(dest_folder):
        return 1
    else:
        return 0

def compress_library_date(library_name:str, date_folder:str) -> int:
    source_path = os.path.join(ARCHIVE_PATH, library_name, date_folder)
    if not os.path.exists(source_path):
        print(f"Source path '{source_path}' does not exist or is incorrect.")
        return 0
    
    destination_path = f"{source_path}.zip"
    if os.path.exists(destination_path):
        print(f"Destination path '{destination_path}' already exists. Skipping compression.")
        return 0
    
    n = compress_folder(source_path, destination_path)
    if n == 1:
        # print(f"Compressed successfully")
        # print(f"Removing source directory {source_path}...")
        shutil.rmtree(source_path)
    else:
        print(f"Failed to compress {source_path}")
    return n

def decompress_library_date(library_name:str, date_archive:str) -> int:
    source_path = os.path.join(ARCHIVE_PATH, library_name, date_archive)
    if not os.path.exists(source_path):
        print(f"Source path '{source_path}' does not exist.")
        return 0

    destination_path = os.path.join(ARCHIVE_PATH, library_name, date_archive.replace(".zip", ""))
    n = decompress_zip(source_path, destination_path)
    if n == 1:
        # print(f"Decompressed successfully")
        # print(f"Removing archive {source_path}...")
        os.remove(source_path)
    else:
        print(f"Failed to decompress {source_path}")
    return n

def archiveAction(mode:str, callback) -> int:
    print(f"Please enter the name of the library to {mode}:")
    print(f"\tyou can provide a specific date to {mode} only this date (ex: my_library/1970-01-01)")
    print(f"\tif you want to {mode} the whole library, just type the name of the library (ex: my_library)")
    print(f"\tif you want to {mode} all libraries, just type * (ex : * or */1970-01-01 for a specific date)")

    user_input = input("Library name (name / * / exit): ")

    if user_input == "exit":
        return -1

    n = 0

    library_name, date_folder = user_input.split("/") if "/" in user_input else (user_input, '*')

    libraries = os.listdir(ARCHIVE_PATH)

    count = 0

    for lib in libraries:
        if os.path.isdir(os.path.join(ARCHIVE_PATH, lib)) and (lib == library_name or library_name == "*"):
            dates = os.listdir(os.path.join(ARCHIVE_PATH, lib))
            for date in dates:
                if mode == "compress":
                    if os.path.isdir(os.path.join(ARCHIVE_PATH, lib, date)) and (date_folder == "*" or date_folder in date):
                        count += 1
                elif mode == "decompress":
                    if date.endswith(".zip") and (date_folder == "*" or date_folder in date):
                        count += 1
                else:
                    print(f"Unknown mode '{mode}'")

    progressbar = ProgressBar(count)

    progressbar.update(0)

    for lib in libraries:
        if os.path.isdir(os.path.join(ARCHIVE_PATH, lib)) and (lib == library_name or library_name == "*"):
            dates = os.listdir(os.path.join(ARCHIVE_PATH, lib))
            for date in dates:
                if mode == "compress":
                    if os.path.isdir(os.path.join(ARCHIVE_PATH, lib, date)) and (date_folder == "*" or date_folder in date):
                        # print(f"{mode.capitalize()}ing {date} from library '{lib}'...")
                        n += callback(lib, date)
                        progressbar.update(n)
                elif mode == "decompress":
                    if date.endswith(".zip") and (date_folder == "*" or date_folder in date):
                        # print(f"{mode.capitalize()}ing {date} from library '{lib}'...")
                        n += callback(lib, date)
                        progressbar.update(n)
                else:
                    print(f"Unknown mode '{mode}'")
    return n

print("👋 Welcome to the Photo archiver program! Type 'help' to see the list of available commands.")

cmd = ""
STOP_COMMANDS = ["exit", "quit", "q", "stop", "end", "bye"]
HELP_COMMANDS = ["help", "h", "?"]
while not(cmd in STOP_COMMANDS):
    if os.listdir(ARCHIVE_PATH) == []:
        print("Welcome !")
        print("You don't have any library yet. Let's start by creating one.")
        print("Please enter the name of the library you want to create.")
        library_name = input("Library name: ")
        create_library(library_name)

    cmd = input("Enter a command: ").lower()


    if cmd in STOP_COMMANDS:
        print("Goodbye! 👋")
        break
    elif cmd in HELP_COMMANDS:
        print("\t- help: Display the list of available commands")
        print("\t- exit: Exit the program")
        print("\t- list: Display the list of libraries")
        print("\t- create: Create a new library")
        print(f"\t- load: Load all the photos from the '{INPUT_FOLDER_NAME}' folder into a library")
        print("\t- archive: Compress or decompress a library / a date")
    elif cmd == "list":
        display_libraries()
    elif cmd == "create":
        library_name = input("Library name: ")
        create_library(library_name)
    elif cmd == "load":
        print("Please enter the name of the library where you want to load the photos.")
        print("You can type 'AUTO' to automatically load the photos into the library with the corresponding file extension.")
        if len(os.listdir(INPUT_PATH)) == 0:
            print(f"No photos found in the '{INPUT_FOLDER_NAME}' folder.")
        else:
            photos_destination = input("Library name (or 'AUTO') : ")
            destinations = get_photo_destinations(photos_destination)
            print(f"Photos to load : ({len(destinations)})")
            print(tabulate(destinations, headers="keys", tablefmt="fancy_grid"))
            if input("Do you want to proceed? (y/n) : ").lower() == "y":
                for photo in destinations:
                    if not(photo["destination"] == "?"):
                        create_folder(os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"]))
                        if os.path.exists(os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"], photo["name"])):
                            print(f"⚠️ WARNING: The file {photo['name']} already exists in the destination folder. ({photo['destination']}/{photo['creation_date']}) Skipping...")
                        else:
                            os.rename(os.path.join(INPUT_PATH, photo["name"]), os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"], photo["name"]))
                print("Photos loaded successfully.")
            else:
                print("Canceled.")
                print("Photos not loaded.")
    elif cmd == "archive":
        print("Please select the action type (compress / decompress)")
        action = ""
        while action not in ["c", "d", "exit"]:
            action = input("Action (c / d / exit): ").lower()
        if action == "c" or action == "d":
            if action == "c":
                print("You chose to compress some content")
                mode = "compress"
                callback = compress_library_date
            else:
                print("You chose to decompress some content")
                mode = "decompress"
                callback = decompress_library_date
            n = archiveAction(mode, callback)
            if n > 0:
                print(f"Successfully {mode}ed {n} items.")
            elif n == 0:
                print(f"No items were {mode}ed.")
            else:
                print("Archiving aborted.")
        elif action == "exit":
            print("Archiving aborted.")
    else:
        print(f"Command \"{cmd}\" not recognized. Please try again.")