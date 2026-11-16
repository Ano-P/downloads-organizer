import argparse
import shutil
from pathlib import Path 
import sys

EXTENSION_CATEGORIES = {
    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".md": "Documents",

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".webp": "Images",
    ".bmp": "Images",

    # Videos
    ".mp4": "Videos",
    ".mov": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".webm": "Videos",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".m4a": "Audio",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",

    # Code
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".json": "Code",
    ".java": "Code",
    ".cpp": "Code"
}



def main():
    parser = argparse.ArgumentParser(description='finds the directory')
    parser.add_argument('directory', help="Directory to organize")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    target_dir = validate_directory(args.directory)
    if target_dir == None:
        sys.exit('cannot find directory.')
    eligible_files = scan_directory(target_dir)
    org_plan = create_organization_plan(target_dir, eligible_files)
    display_plan(org_plan)
    









def validate_directory(path):#validates the existence of path and whether it is a directory.
    path = Path(path)
    if path.exists() and path.is_dir():
        return path
    else:
        return None



def scan_directory(target_dir):#scans the directory for valid files
    files = []
    for entry in target_dir.iterdir():
        if entry.is_symlink():
            continue
        elif entry.name == '.downloads-organizer.log':
            continue
        elif not entry.is_file():
            continue
        files.append(entry)

    return files


def classify_file(file):#classifies file extension
    extension = file.suffix
    lower_extension = extension.lower()
    category = EXTENSION_CATEGORIES.get(lower_extension, 'Others')
    return category



def create_organization_plan(target_dir, eligible_files): #plans where each file will go in each folder.
    org_plan = []
    reserved_destinations = set()
    for file in eligible_files:
        file_category = classify_file(file)
        category_folder = target_dir / file_category
        destination = category_folder / file.name
        if destination.exists() or destination in reserved_destinations:
            counter = 1 
            new = f"{file.stem}_{counter}{file.suffix}"
            destination = category_folder / new
            while destination.exists() or destination in reserved_destinations:
                    counter += 1
                    n = f"{file.stem}_{counter}{file.suffix}"
                    destination = category_folder / n
        reserved_destinations.add(destination)
        dest_dict = {"source" : file, "category" : file_category, "destination" : destination }
        org_plan.append(dest_dict)
    return org_plan


def display_plan(org_plan):#displays the changes its going to make
    if not org_plan:
        print("No eligible files found")
        return
    print(f"{'SOURCE':<20} {'CATEGORY':<12} DESTINATION")
    for item in org_plan:
        print(f"\n{len(org_plan)} files planned.")
        print(f"{item['source'].name:<20} {item['category']:<12} {item['destination'].parent.name}/{item['destination'].name}")







if __name__ == "__main__":
    main()