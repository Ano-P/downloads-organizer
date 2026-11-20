# Downloads Organizer

A Python command-line tool that organises files in a selected directory into categories based on their file extensions.

The programme previews the proposed changes before moving anything. It supports a dry-run mode by default, confirmation before applying changes, collision handling and activity logging.

## Features

- Organises files into categories based on their extensions.
- Supports case-insensitive extension detection.
- Places unknown and extensionless files into `Others`.
- Previews planned changes before modifying files.
- Requires confirmation before moving files.
- Prevents existing files from being overwritten.
- Handles filename collisions by adding numbered suffixes.
- Processes only files directly inside the selected directory.
- Skips symbolic links, subdirectories and its own log file.
- Checks destination paths to prevent movement outside the selected directory.
- Records successful moves, skipped files and failures.
- Provides a summary after an organisation operation.

## Categories

| Category | Supported extensions |
|---|---|
| Documents | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.md` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` |
| Videos | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm` |
| Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.m4a` |
| Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| Code | `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.java`, `.cpp` |
| Others | Unrecognised and extensionless files |

## Requirements

- Python 3
- Pytest for running the automated tests

The organiser uses Python's standard library. No third-party packages are required to run the application.

## Installation

Clone or download the repository, then open a terminal in the project directory.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install pytest:

```bash
python -m pip install pytest
```

## Usage

### Dry-run mode

Run the programme with a directory path:

```bash
python downloads.py "C:\Users\YourName\Downloads"
```

Dry-run mode is the default.

The programme displays the proposed file movements without changing the directory.

It does not create category folders, move files or create a log file.

### Apply changes

Add the `--apply` argument:

```bash
python downloads.py "C:\Users\YourName\Downloads" --apply
```

The programme displays the organisation plan and requests confirmation.

- Enter `y` to proceed.
- Enter `n` or press Enter to cancel.
- Invalid responses prompt you again.

After confirmation, the programme creates the required category folders and moves the files.

## File Organisation Behaviour

### Filename collisions

The programme preserves existing files.

When a destination filename already exists, it adds a numbered suffix.

For example:

```text
Images/
    photo.png
```

A new file with the same name is planned as:

```text
Images/
    photo.png
    photo_1.png
```

Further collisions receive higher numbers.

### Existing directories

The programme only scans files directly inside the selected directory.

It does not recursively scan or reorganise existing subdirectories.

Existing category folders are reused, but their existing contents are not reorganised.

### Logging

After the user confirms an organisation operation, the programme creates or updates:

```text
.downloads-organizer.log
```

The log records file movements and errors. The organiser excludes this file from future sorting operations.

### Safety

The programme includes safeguards to:

- Preserve existing destination files.
- Skip symbolic links during scanning.
- Reject symbolic link and junction destination folders.
- Reject category paths occupied by regular files.
- Verify destination folders remain inside the selected directory.
- Avoid creating category folders during dry-run mode.
- Avoid modifying files when the user cancels.

## Testing

The project uses pytest for automated testing.

Run the complete test suite from the project directory:

```bash
python -m pytest -v
```

Display reasons for skipped tests:

```bash
python -m pytest -v -rs
```

The tests cover directory validation, file classification, scanning, organisation planning, collision handling, confirmation, file movement, logging, summaries and command-line behaviour.

Some symbolic link tests require operating system permissions to create symbolic links.

## Project Structure

```text
downloads-organizer/
│
├── downloads.py
├── tests/
│   └── test_downloads.py
├── README.md
└── .gitignore
```

## Project Purpose

This project was developed to practise Python programming, command-line interfaces, file handling, error handling, logging, automated testing and Git version control.