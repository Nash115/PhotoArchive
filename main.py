import os
from dotenv import load_dotenv
from tabulate import tabulate
import modules.utils as utils
import modules.archive as archive
import modules.library as library

load_dotenv()

ARCHIVE_PATH = os.getenv("ARCHIVE_PATH", None)
INPUT_FOLDER_NAME = os.getenv("INPUT_FOLDER_NAME", "-Input-")
IMAGES_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".nef", ".tiff", ".cr2", ".cr3", ".heic", ".webp")

if ARCHIVE_PATH is None:
    print("No archive path specified. Please set the ARCHIVE_PATH environment variable.")
    exit(1)

if not os.path.exists(ARCHIVE_PATH):
    print(f"⚠️ WARNING: The archive path '{ARCHIVE_PATH}' does not exist.")
    exit(1)

INPUT_PATH = os.path.join(ARCHIVE_PATH, INPUT_FOLDER_NAME)
utils.create_folder(INPUT_PATH)

# Initialize module constants
library.ARCHIVE_PATH = ARCHIVE_PATH
library.INPUT_FOLDER_NAME = INPUT_FOLDER_NAME
library.IMAGES_EXTENSIONS = IMAGES_EXTENSIONS
library.INPUT_PATH = INPUT_PATH
archive.ARCHIVE_PATH = ARCHIVE_PATH

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
        library.create_library(library_name)

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
        library.display_libraries()
    elif cmd == "create":
        library_name = input("Library name: ")
        library.create_library(library_name)
    elif cmd == "load":
        print("Please enter the name of the library where you want to load the photos.")
        print("You can type 'AUTO' to automatically load the photos into the library with the corresponding file extension.")
        if len(os.listdir(INPUT_PATH)) == 0:
            print(f"No photos found in the '{INPUT_FOLDER_NAME}' folder.")
        else:
            photos_destination = input("Library name (or 'AUTO') : ")
            destinations = library.get_photo_destinations(photos_destination)
            print(f"Photos to load : ({len(destinations)})")
            print(tabulate(destinations, headers="keys", tablefmt="fancy_grid"))
            if input("Do you want to proceed? (y/n) : ").lower() == "y":
                for photo in destinations:
                    if not(photo["destination"] == "?"):
                        utils.create_folder(os.path.join(ARCHIVE_PATH, photo["destination"], photo["creation_date"]))
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
                callback = archive.compress_library_date
            else:
                print("You chose to decompress some content")
                mode = "decompress"
                callback = archive.decompress_library_date
            n = archive.archiveAction(mode, callback)
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
