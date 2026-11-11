# Downloads Organizer Specification

## 1. Project Overview

Downloads Organizer is a command-line application designed to organise files within a user-selected directory. The application identifies file extensions and categorises files based on their types, such as JPG files for images, MP4 files for videos and PDF files for documents. It creates separate category folders and moves the corresponding files into them, helping users keep their directories organised without manually creating folders and moving files.

## 2. Problem Statement

Many users struggle to keep their downloaded files organised due to the growing number of files stored in a single directory. Manually sorting each file into separate folders requires time and effort, making the process inconvenient for users who regularly download different types of files. As a result, important files often remain mixed with unrelated downloads, making them harder to locate and manage.

## 3. Project Goals

The goal of this project is to develop a command-line application that helps users manage and organise files within their selected directories. The application aims to simplify file organisation by automatically grouping files into appropriate folders based on their extensions. It should provide a reliable, safe and convenient way to manage files while reducing the time and effort required for manual organisation.

## 4. Project Scope

### Included in the project

- Accepting a user-selected directory.
- Identifying and scanning eligible files within the selected directory.
- Categorising files using their extensions.
- Creating category folders when required.
- Moving files into their appropriate category folders.
- Providing a dry-run mode to preview proposed changes.
- Requiring explicit confirmation before actual file movement.
- Handling filename collisions without overwriting existing files.
- Recording operations using a log file.
- Displaying a summary after organisation.

### Excluded from the project

- Organising files recursively inside existing subfolders.
- Deleting or restoring files.
- Modifying the contents of files.
- Overwriting existing files.
- Allowing users to create custom categories or manually assign individual files to different destination folders.
- Organising files outside the user-selected directory.

## 5. User Input and Output

Users will provide a directory path through the command line. The application will scan the selected directory and display an organisation preview showing where each eligible file will be moved.

The application will provide two modes of operation. By default, it will run in dry-run mode and display the proposed organisation without making changes. Users who supply the `--apply` command-line option will be asked to confirm before the application performs actual file movement.

### User Input

| Input | Description | Required? |
|---|---|---|
| Directory path | The location of the directory containing the files to organise. | Yes |
| `--apply` | Requests actual file organisation rather than preview mode. | No |
| Confirmation (`y` or `n`) | Confirms or cancels the proposed file movements. | Only in apply mode |

### Application Output

| Output | Description | Location |
|---|---|---|
| Organisation preview | Displays proposed file movements and destination folders. | Terminal |
| Error messages | Explains invalid paths, permission problems and other failures. | Terminal |
| Progress messages | Displays important stages of the organisation process. | Terminal |
| Final summary | Reports the number of files moved, skipped and failed. | Terminal |
| Operation logs | Records detailed information about actual operations and errors. | `.downloads-organizer.log` inside the selected directory |

## 6. Functional Requirements

FR-01: The application must accept a directory path provided by the user through the command line.

FR-02: The application must validate the selected directory before scanning or modifying it.

FR-03: The application must scan eligible files directly inside the selected directory.

FR-04: The application must identify file extensions without being affected by uppercase or lowercase differences.

FR-05: The application must categorise files using predefined extension categories.

FR-06: The application must place unknown and extensionless files into an Others folder.

FR-07: The application must create category folders when required during actual organisation.

FR-08: The application must generate and display an organisation plan before moving files.

FR-09: The application must use dry-run mode by default without making changes to the selected directory.

FR-10: The application must accept a `--apply` command-line argument to request actual file movement.

FR-11: The application must request confirmation before performing actual file movement.

FR-12: The application must handle filename collisions without overwriting existing files.

FR-13: The application must move files into their appropriate category folders while keeping all destination paths inside the selected directory.

FR-14: The application must record actual operations and errors in a separate log file.

FR-15: The application must display a final summary showing the results of the organisation process.

## 7. File Categories

The application will use predefined file categories based on common file extensions.

| Category | Supported extensions |
|---|---|
| Documents | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.md` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` |
| Videos | `.mp4`, `.mov`, `.mkv`, `.avi`, `.webm` |
| Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.m4a` |
| Archives | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| Code | `.py`, `.js`, `.ts`, `.html`, `.css`, `.json`, `.java`, `.cpp` |
| Others | Unrecognised and extensionless files |

The application must recognise extensions regardless of their capitalisation. Uncommon or unsupported extensions will be categorised under Others.

Existing subfolders will not be scanned or modified.

## 8. Application Workflow

1. The user starts the application and provides a directory path.
2. The application processes the command-line arguments.
3. The application validates the selected directory.
4. The application scans eligible files directly inside the directory.
5. The application identifies file extensions and categorises the files.
6. The application prepares an organisation plan, including destination paths and filename collision handling.
7. The application displays the organisation preview.

8. The application determines which mode has been requested:
   - Without `--apply`, the application displays the preview and exits without changing anything.
   - With `--apply`, the application asks the user to confirm the proposed organisation.

9. When the user declines or presses Enter, the application cancels the operation without moving files.
10. When the user confirms, the application creates the necessary category folders and moves the eligible files.
11. The application records actual operations and errors in the log file.
12. The application displays a final summary of the results.

## 9. Safety and Security Requirements

- The application must validate the selected directory before performing operations.
- Files must never be deleted.
- Existing files must never be overwritten.
- File organisation must not be recursive.
- Files must never be moved outside the selected directory.
- Symbolic links must be skipped.
- Existing subfolders must remain untouched.
- Dry-run mode must be the default.
- Dry-run mode must not create folders, move or rename files, or create a log file.
- Actual file movement must require the `--apply` option and explicit user confirmation.
- Filename collisions must be handled by generating a unique destination filename.
- The application's own log file must be excluded from file categorisation and movement.
- The log file must remain inside the selected directory.
- The application must avoid recording sensitive file contents or unnecessary personal information in logs.

## 10. Error Handling

The application must handle unexpected situations and display understandable error messages.

| Situation | Expected behaviour |
|---|---|
| Directory does not exist | Display an error and stop. |
| Supplied path points to a file instead of a directory | Explain that a directory is required and stop. |
| Directory is empty | Display a message explaining that there are no files to organise. |
| Directory cannot be accessed | Display an appropriate permission error. |
| Unknown file extension | Categorise the file under Others. |
| File has no extension | Categorise the file under Others. |
| Filename collision | Generate a unique filename without overwriting the existing file. |
| Individual file cannot be moved | Report and log the failure, then continue with other files when safe. |
| User cancels organisation | Cancel the operation without moving files. |
| Invalid confirmation input | Request a valid confirmation response. |

Unexpected failures that prevent safe operation must stop the application rather than risk modifying the wrong files.

## 11. Testing Requirements

The application will use pytest for automated testing. Tests will use pytest's `tmp_path` fixture to create isolated temporary directories and sample files without modifying the user's actual files.

The following behaviours must be tested:

- Correct categorisation of supported file extensions.
- Recognition of uppercase and lowercase extensions.
- Handling of unknown extensions.
- Handling of files without extensions.
- Correct organisation preview.
- Dry-run mode leaving the filesystem unchanged.
- Successful file movement during apply mode.
- Correct handling of filename collisions.
- Rejection of invalid directory paths.
- Skipping existing subfolders and symbolic links.
- Ensuring files are never moved outside the selected directory.
- Correct creation of operation logs during actual organisation.

The application will also undergo independent manual testing using a separate sample directory containing different file types, unknown extensions, extensionless files and filename collisions.

## 12. Acceptance Criteria

The project will be considered complete when all the following conditions are met:

- The application accepts a user-provided directory path through the command line.
- Invalid directory paths are rejected without modifying the filesystem.
- The application scans files directly inside the selected directory without recursively entering existing subfolders.
- Common file extensions are categorised correctly.
- Uppercase and lowercase extensions are recognised.
- Unknown and extensionless files are placed into Others.
- Dry-run mode displays an accurate organisation preview without modifying the filesystem.
- Apply mode requires explicit user confirmation before moving files.
- Declining confirmation cancels the operation without modifying files.
- Category folders are created only when necessary during actual organisation.
- Files are moved into their correct category folders.
- Existing files are never deleted or overwritten.
- Filename collisions are resolved by generating unique filenames.
- No files are moved or written outside the selected directory.
- Detailed operations and errors are recorded in the log file during actual organisation.
- The log file is excluded from subsequent file organisation.
- The final summary accurately reports successful movements, skipped files and failures.
- The automated tests pass.
- The application passes independent manual testing using the separate sample directory.
- The README.md and requirements.txt files are complete.
- The GitHub repository contains the finished project and its documented development history.