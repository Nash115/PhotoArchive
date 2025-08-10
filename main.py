import os
import json
import datetime
from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()

ARCHIVE_PATH = os.getenv("ARCHIVE_PATH", None)

if ARCHIVE_PATH is None:
    print("No archive path specified. Please set the ARCHIVE_PATH environment variable.")
    exit(1)

if not os.path.exists(ARCHIVE_PATH):
    print(f"⚠️ WARNING: The archive path '{ARCHIVE_PATH}' does not exist.")
    exit(1)

def create_folder(folder_name:str) -> None:
    """Create a folder with the given name if it does not exist.

    Parameters
    ----------
    folder_name : str
        The name of the folder to be created.
    """
    if os.path.exists(folder_name) == False:
        os.mkdir(folder_name)


def create_library(library_name:str) -> None:
    """Create a library with the given name if it does not exist.

    Parameters
    ----------
    library_name : str
        The name of the library to be created.
    """
    create_folder(os.path.join(ARCHIVE_PATH, library_name))
    # Create the config file into the library folder
    with open(os.path.join(ARCHIVE_PATH, library_name, "config.json"), "w") as file:
        json.dump({"name": library_name, "file_extensions":[]}, file, indent=4)


def count_files_in_dirs(path: str) -> int:
    """Count the number of files in the given directory and its subdirectories.

    Parameters
    ----------
    path : str
        The path to the directory to search.

    Returns
    -------
    int
        The number of files found.
    """
    IMAGES_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".nef", ".tiff", ".cr2", ".cr3", ".heic", ".webp"]
    count = 0
    for root, dirs, files in os.walk(path):
        # Exclude certain files
        files = [f for f in files if f.lower().endswith(tuple(IMAGES_EXTENSIONS))]
        count += len(files)
    return count

def load_libraries() -> list[dict]:
    """Return the list of libraries.

    Returns
    -------
    list[dict]
        The list of libraries.
    """
    libraries = []
    for library in os.listdir(ARCHIVE_PATH):
        if os.path.isdir(os.path.join(ARCHIVE_PATH, library)):
            if not(os.path.exists(os.path.join(ARCHIVE_PATH, library, "config.json"))):
                print(f"Config file not found for library {library}. Recreating it...")
                create_library(library)
            with open(os.path.join(ARCHIVE_PATH, library, "config.json"), "r") as file:
                json_data = json.load(file)
                json_data["photos"] = count_files_in_dirs(os.path.join(ARCHIVE_PATH, library))
                libraries.append(json_data)
    return libraries


def display_libraries() -> None:
    """Display the list of libraries."""
    libraries = load_libraries()
    print(tabulate(libraries, headers="keys", tablefmt="fancy_grid"))


def get_photo_destinations(mode:str) -> list[dict]:
    """Return the list of photo destinations.

    Parameters
    ----------
    mode : str
        The mode to use to get the photo destinations : 'AUTO' or a name of a library.
    
    Returns
    -------
    list[dict]
        The list of photo destinations.
    """
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
        
print("👋 Welcome to the Photo archiver program! Type 'help' to see the list of available commands.")

INPUT_PATH = os.path.join(ARCHIVE_PATH, "### Input ###")
create_folder(INPUT_PATH)

cmd = ""
STOP_COMMANDS = ["exit", "quit", "q", "stop", "end", "bye"]
HELP_COMMANDS = ["help", "h", "?"]
while not(cmd in STOP_COMMANDS):
    if os.listdir(ARCHIVE_PATH) == []: # Check if no library has been created yet
        print("Welcome !")
        print("You don't have any library yet. Let's start by creating one.")
        print("Please enter the name of the library you want to create.")
        library_name = input("Library name: ")
        create_library(library_name)

    cmd = input("Enter a command: ").lower() # Prompt the user to enter a command


    if cmd in STOP_COMMANDS:
        print("Goodbye! 👋")
        break
    elif cmd in HELP_COMMANDS:
        print("  - help: Display the list of available commands")
        print("  - exit: Exit the program")
        print("  - list-libraries: Display the list of libraries")
        print("  - create-library: Create a new library")
        print("  - load: Load all the photos from the '### Input ###' folder into a library")
    elif cmd == "list-libraries":
        display_libraries()
    elif cmd == "create-library":
        library_name = input("Library name: ")
        create_library(library_name)
    elif cmd == "load":
        print("Please enter the name of the library where you want to load the photos.")
        print("You can type 'AUTO' to automatically load the photos into the library with the correspondig file extension.")
        if len(os.listdir(INPUT_PATH)) == 0:
            print("No photos found in the '### Input ###' folder.")
        else:
            photos_destination = input("Library name (or 'AUTO') : ")
            destinations = get_photo_destinations(photos_destination)
            print(f"Photos to load : ({len(destinations)})")
            print(tabulate(destinations, headers="keys", tablefmt="fancy_grid"))
            if input("Do you want to proceed? (y/n) : ").lower() == "y":
                for photo in destinations:
                    if not(photo["destination"] == "?"):
                        create_folder(os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"]))
                        os.rename(os.path.join(INPUT_PATH, photo["name"]), os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"], photo["name"]))
                print("Photos loaded successfully.")
            else:
                print("Canceled.")
                print("Photos not loaded.")
    else:
        print(f"Command \"{cmd}\" not recognized. Please try again.")