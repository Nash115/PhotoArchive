import os

def create_folder(folder_name:str) -> None:
    os.makedirs(folder_name, exist_ok=True)

def count_files_in_dirs(path: str, files_extensions: list[str]) -> int:
    count = 0
    lower_exts = tuple(ext.lower() for ext in files_extensions)
    for root, dirs, files in os.walk(path):
        files = [f for f in files if f.lower().endswith(lower_exts)]
        count += len(files)
    return count
