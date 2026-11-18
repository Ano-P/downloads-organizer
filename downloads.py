import argparse
import shutil
from pathlib import Path
import sys
import logging

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
    ".cpp": "Code",
}#all types of extensions


def main():
    parser = argparse.ArgumentParser(description="Finds the directory")
    parser.add_argument("directory", help="Directory to organize")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    target_dir = validate_directory(args.directory)
    if target_dir is None:
        sys.exit("Cannot find directory.")

    eligible_files = scan_directory(target_dir)
    org_plan = create_organization_plan(target_dir, eligible_files)
    display_plan(org_plan)

    if not org_plan:
        return

    if args.apply:
        confirmed = confirm_org()
        if confirmed:
            setup_logging(target_dir)
            info = apply_plan(org_plan)
            display_summary(info)
        else:
            print("Organisation cancelled. No files were moved.")


def validate_directory(path): #validates whether the path exists and relevant
    path = Path(path)
    if path.exists() and path.is_dir():
        return path
    return None


def scan_directory(target_dir): #scans if the files are plausible
    files = []
    for entry in target_dir.iterdir():
        if entry.is_symlink():
            continue
        elif entry.name == ".downloads-organizer.log":
            continue
        elif not entry.is_file():
            continue
        files.append(entry)
    return files


def classify_file(file):#classifies files into extensions
    extension = file.suffix
    lower_extension = extension.lower()
    category = EXTENSION_CATEGORIES.get(lower_extension, "Others")
    return category


def create_organization_plan(target_dir, eligible_files):#plans out organization of files
    org_plan = []
    reserved_destinations = set()

    for file in eligible_files:
        file_category = classify_file(file)
        category_folder = target_dir / file_category
        destination = category_folder / file.name

        # exists() misses dangling symlinks, so check both conditions.
        if destination.exists() or destination.is_symlink() or destination in reserved_destinations:
            counter = 1
            new_name = f"{file.stem}_{counter}{file.suffix}"
            destination = category_folder / new_name

            while (
                destination.exists()
                or destination.is_symlink()
                or destination in reserved_destinations
            ):
                counter += 1
                new_name = f"{file.stem}_{counter}{file.suffix}"
                destination = category_folder / new_name

        reserved_destinations.add(destination)
        dest_dict = {
            "source": file,
            "category": file_category,
            "destination": destination,
        }
        org_plan.append(dest_dict)

    return org_plan


def display_plan(org_plan): #displays plan for user input
    if not org_plan:
        print("No eligible files found")
        return

    print(f"{'SOURCE':<20} {'CATEGORY':<12} DESTINATION")
    for item in org_plan:
        print(
            f"{item['source'].name:<20} "
            f"{item['category']:<12} "
            f"{item['destination'].parent.name}/{item['destination'].name}"
        )
    print(f"\n{len(org_plan)} files planned.")


def confirm_org():#user input
    while True:
        answer = input("Are you sure you want to proceed? [y/N]: ").strip().lower()
        if answer == "y":
            return True
        elif answer == "n" or answer == "":
            return False
        else:
            print("Invalid input. Please enter y or n.")


def apply_plan(org_plan):#applies the plan when user input is yes
    moved = 0
    skipped = 0
    failed = 0

    for plan in org_plan:
        source = plan["source"]
        destination = plan["destination"]
        destination_folder = destination.parent

        try:
            # Reject directory symlinks and Windows junctions.
            is_junction = getattr(
                destination_folder, "is_junction", lambda: False
            )()

            if destination_folder.is_symlink() or is_junction:
                print(
                    f"Skipping {source.name}: destination folder "
                    "is a symbolic link or junction."
                )
                logging.warning(
                    "Skipped %s: destination folder is a link or junction",
                    source.name
                )
                skipped += 1
                continue

            # Reject a regular file occupying the category-folder path.
            if destination_folder.exists() and not destination_folder.is_dir():
                print(
                    f"Skipping {source.name}: destination folder "
                    "path is occupied by a file."
                )
                logging.warning(
                    "Skipped %s: destination folder path is occupied by a file",
                    source.name
                )
                skipped += 1
                continue

            # Ensure the destination folder stays inside the selected directory.
            target_root = source.parent.resolve()
            resolved_destination_folder = destination_folder.resolve()

            try:
                resolved_destination_folder.relative_to(target_root)
            except ValueError:
                print(
                    f"Skipping {source.name}: destination resolves "
                    "outside the selected directory."
                )
                logging.warning(
                    "Skipped %s: destination resolves outside selected directory",
                    source.name
                )
                skipped += 1
                continue

            # Create the category folder after confirmation.
            if not destination_folder.exists():
                destination_folder.mkdir()

            # Reject an existing destination, including dangling symlinks.
            if destination.exists() or destination.is_symlink():
                print(
                    f"Skipping {source.name}: destination already exists "
                    "or is a symbolic link."
                )
                logging.warning(
                    "Skipped %s: destination already occupied",
                    source.name
                )
                skipped += 1
                continue

            # Move the file.
            shutil.move(str(source), str(destination))

            moved += 1

            logging.info(
                "Moved %s to %s",
                source.name,
                destination
            )

            print(
                f"Moved {source.name} to "
                f"{destination.parent.name}/{destination.name}"
            )

        except (OSError, shutil.Error) as error:
            failed += 1

            logging.error(
                "Failed to move %s: %s",
                source.name,
                error
            )

            print(f"Failed to move {source.name}: {error}")

    return {
        "moved": moved,
        "skipped": skipped,
        "failed": failed
    }



def setup_logging(target_dir): #sets up logging
    n = target_dir / ".downloads-organizer.log"
    logging.basicConfig(

    filename=str(n),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def display_summary(info):#displays the final summary
    print("\nOrganisation complete.")
    print("---------------------")
    print(f"Files moved:   {info['moved']}")
    print(f"Files skipped: {info['skipped']}")
    print(f"Files failed:  {info['failed']}")
    print("---------------------")




if __name__ == "__main__":
    main()
