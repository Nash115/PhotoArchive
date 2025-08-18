import os
from dotenv import load_dotenv
import modules.utils as utils

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