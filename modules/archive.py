import zipfile
import os
import shutil
from modules.progressbar import ProgressBar

ARCHIVE_PATH = None

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
