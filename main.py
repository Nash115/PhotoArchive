import os
import json
import datetime

from tabulate import tabulate

print("👋 Welcome to the Photo archiver program! Type 'help' to see the list of available commands.")

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
    create_folder("Archive/" + library_name)
    # Create the config file into the library folder
    with open(f"Archive/{library_name}/config.json", "w") as file:
        json.dump({"name": library_name, "file_extensions":[]}, file, indent=4)


def load_librries() -> list[dict]:
    """Return the list of libraries.

    Returns
    -------
    list[dict]
        The list of libraries.
    """
    libraries = []
    for library in os.listdir("Archive"):
        if os.path.isdir(f"Archive/{library}"):
            if not(os.path.exists(f"Archive/{library}/config.json")):
                print(f"Config file not found for library {library}. Recreating it...")
                create_library(library)
            with open(f"Archive/{library}/config.json", "r") as file:
                libraries.append(json.load(file))
    return libraries


def display_libraries() -> None:
    """Display the list of libraries."""
    libraries = load_librries()
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
        LIBRARIES = load_librries()
        l = []
        for f in os.listdir("Input"):
            if os.path.isfile("Input/"+f):
                file_extension = f.split(".")[-1]
                found = False
                for library in LIBRARIES:
                    if file_extension in library["file_extensions"] or library["file_extensions"] == []:
                        l.append({
                            "name":f,
                            "destination":library["name"],
                            "creation_date": datetime.datetime.fromtimestamp(os.path.getctime("Input/"+f)).strftime("%Y-%m-%d"),
                            "size": f"{os.path.getsize("Input/"+f)} bytes"
                        })
                        found = True
                        break
                if not found:
                    l.append({
                            "name":f,
                            "destination":"?",
                            "creation_date": datetime.datetime.fromtimestamp(os.path.getctime("Input/"+f)).strftime("%Y-%m-%d"),
                            "size": f"{os.path.getsize("Input/"+f)} bytes"
                    })
        return l
    else:
        if not(os.path.exists(f"Archive/{mode}")):
            print(f"Library {mode} not found.")
            return [
                {
                    "name":f,
                    "destination":"?",
                    "creation_date": datetime.datetime.fromtimestamp(os.path.getctime("Input/"+f)).strftime("%Y-%m-%d"),
                    "size": f"{os.path.getsize("Input/"+f)} bytes"
                }
                for f in os.listdir("Input") if os.path.isfile(f)
            ]
        else:
            return [
                {
                    "name":f,
                    "destination":mode,
                    "creation_date": datetime.datetime.fromtimestamp(os.path.getctime("Input/"+f)).strftime("%Y-%m-%d"),
                    "size": f"{os.path.getsize("Input/"+f)} bytes"
                }
                for f in os.listdir("Input") if os.path.isfile(f)
            ]
create_folder("Archive")
create_folder("Input")

cmd = ""
STOP_COMMANDS = ["exit", "quit", "q", "stop", "end", "bye"]
HELP_COMMANDS = ["help", "h", "?"]
while not(cmd in STOP_COMMANDS):
    if os.listdir("Archive") == []: # Check if no library has been created yet
        print("Welcome !")
        print("You don't have any library yet. Let's start by creating one.")
        print("Please enter the name of the library you want to create.")
        library_name = input("Library name: ")
        create_folder("Archive/" + library_name)
    

    cmd = input("Enter a command: ").lower() # Prompt the user to enter a command


    if cmd in STOP_COMMANDS:
        print("Goodbye! 👋")
        break
    elif cmd in HELP_COMMANDS:
        print("  - help: Display the list of available commands")
        print("  - exit: Exit the program")
        print("  - list-libraries: Display the list of libraries")
        print("  - create-library: Create a new library")
        print("  - load: Load all the photos from the 'Input' folder into a library")
    elif cmd == "list-libraries":
        display_libraries()
    elif cmd == "create-library":
        library_name = input("Library name: ")
        create_library(library_name)
    elif cmd == "load":
        print("Please enter the name of the library where you want to load the photos.")
        print("You can type 'AUTO' to automatically load the photos into the library with the correspondig file extension.")
        if len(os.listdir("Input")) == 0:
            print("No photos found in the 'Input' folder.")
        else:
            photos_destination = input("Library name (or 'AUTO') : ")
            destinations = get_photo_destinations(photos_destination)
            print(tabulate(destinations, headers="keys", tablefmt="fancy_grid"))
            if input("Do you want to proceed? (y/n) : ").lower() == "y":
                for photo in destinations:
                    if not(photo["destination"] == "?"):
                        if os.path.exists(f"Archive/{photo['destination']}/{photo['creation_date']}") == False:
                            os.mkdir(f"Archive/{photo['destination']}/{photo['creation_date']}")
                        os.rename(f"Input/{photo['name']}", f"Archive/{photo['destination']}/{photo['creation_date']}/{photo['name']}")
                print("Photos loaded successfully.")
            else:
                print("Canceled.")
                print("Photos not loaded.")
    else:
        print(f"Command \"{cmd}\" not recognized. Please try again.")