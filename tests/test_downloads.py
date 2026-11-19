from pathlib import Path
import logging

import pytest
import downloads


# --------------------------------------------------
# validate_directory()
# --------------------------------------------------

def test_validate_directory_existing_directory(tmp_path):
    result = downloads.validate_directory(tmp_path)

    assert result == tmp_path


def test_validate_directory_nonexistent_path(tmp_path):
    missing_path = tmp_path / "does_not_exist"

    result = downloads.validate_directory(missing_path)

    assert result is None


def test_validate_directory_file_instead_of_directory(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text("Test file")

    result = downloads.validate_directory(file_path)

    assert result is None


# --------------------------------------------------
# classify_file()
# --------------------------------------------------

@pytest.mark.parametrize(
    ("filename", "expected_category"),
    [
        ("report.pdf", "Documents"),
        ("notes.TXT", "Documents"),
        ("photo.jpg", "Images"),
        ("picture.WEBP", "Images"),
        ("video.mp4", "Videos"),
        ("film.MKV", "Videos"),
        ("song.mp3", "Audio"),
        ("music.FLAC", "Audio"),
        ("backup.zip", "Archives"),
        ("archive.7z", "Archives"),
        ("script.py", "Code"),
        ("website.HTML", "Code"),
        ("unknown.xyz", "Others"),
        ("no_extension", "Others"),
    ],
)
def test_classify_file(filename, expected_category):
    file = Path(filename)

    result = downloads.classify_file(file)

    assert result == expected_category


# --------------------------------------------------
# scan_directory()
# --------------------------------------------------

def test_scan_directory_only_returns_direct_files(tmp_path):
    direct_file = tmp_path / "report.pdf"
    direct_file.write_text("Test")

    subfolder = tmp_path / "Existing Folder"
    subfolder.mkdir()

    nested_file = subfolder / "nested.pdf"
    nested_file.write_text("Nested test")

    result = downloads.scan_directory(tmp_path)

    result_names = {file.name for file in result}

    assert result_names == {"report.pdf"}


def test_scan_directory_ignores_log_file(tmp_path):
    regular_file = tmp_path / "report.pdf"
    regular_file.write_text("Test")

    log_file = tmp_path / ".downloads-organizer.log"
    log_file.write_text("Previous log")

    result = downloads.scan_directory(tmp_path)

    result_names = {file.name for file in result}

    assert result_names == {"report.pdf"}


def test_scan_directory_ignores_symlinks(tmp_path):
    original_file = tmp_path / "original.pdf"
    original_file.write_text("Original")

    linked_file = tmp_path / "linked.pdf"

    try:
        linked_file.symlink_to(original_file)
    except (OSError, NotImplementedError):
        pytest.skip("This system does not permit creating file symlinks.")

    result = downloads.scan_directory(tmp_path)

    result_names = {file.name for file in result}

    assert result_names == {"original.pdf"}


# --------------------------------------------------
# create_organization_plan()
# --------------------------------------------------

def test_create_organization_plan_assigns_correct_destinations(tmp_path):
    document = tmp_path / "notes.txt"
    document.write_text("Document")

    image = tmp_path / "photo.png"
    image.write_text("Image")

    unknown = tmp_path / "unknown.xyz"
    unknown.write_text("Unknown")

    files = [document, image, unknown]

    result = downloads.create_organization_plan(tmp_path, files)

    assert len(result) == 3

    assert result[0]["source"] == document
    assert result[0]["category"] == "Documents"
    assert result[0]["destination"] == tmp_path / "Documents" / "notes.txt"

    assert result[1]["source"] == image
    assert result[1]["category"] == "Images"
    assert result[1]["destination"] == tmp_path / "Images" / "photo.png"

    assert result[2]["source"] == unknown
    assert result[2]["category"] == "Others"
    assert result[2]["destination"] == tmp_path / "Others" / "unknown.xyz"


def test_create_organization_plan_handles_existing_filename_collision(tmp_path):
    source = tmp_path / "photo.png"
    source.write_text("New image")

    images_folder = tmp_path / "Images"
    images_folder.mkdir()

    existing_file = images_folder / "photo.png"
    existing_file.write_text("Existing image")

    result = downloads.create_organization_plan(tmp_path, [source])

    planned_destination = result[0]["destination"]

    assert planned_destination == images_folder / "photo_1.png"
    assert source.exists()
    assert existing_file.read_text() == "Existing image"


def test_create_organization_plan_does_not_create_category_folders(tmp_path):
    source = tmp_path / "photo.png"
    source.write_text("Image")

    downloads.create_organization_plan(tmp_path, [source])

    assert not (tmp_path / "Images").exists()


# --------------------------------------------------
# display_plan()
# --------------------------------------------------

def test_display_plan_shows_file_and_destination(tmp_path, capsys):
    source = tmp_path / "report.pdf"
    source.write_text("Document")

    plan = downloads.create_organization_plan(tmp_path, [source])

    downloads.display_plan(plan)

    output = capsys.readouterr().out

    assert "report.pdf" in output
    assert "Documents" in output
    assert "1 files planned." in output


def test_display_plan_handles_empty_plan(capsys):
    downloads.display_plan([])

    output = capsys.readouterr().out

    assert "No eligible files found" in output


# --------------------------------------------------
# confirm_org()
# --------------------------------------------------

@pytest.mark.parametrize("answer", ["y", "Y", " y "])
def test_confirm_org_accepts_yes(answer, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: answer)

    result = downloads.confirm_org()

    assert result is True


@pytest.mark.parametrize("answer", ["n", "N", ""])
def test_confirm_org_rejects_no_or_enter(answer, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: answer)

    result = downloads.confirm_org()

    assert result is False


def test_confirm_org_repeats_after_invalid_input(monkeypatch, capsys):
    answers = iter(["maybe", "y"])

    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    result = downloads.confirm_org()

    output = capsys.readouterr().out

    assert result is True
    assert "Invalid input" in output


# --------------------------------------------------
# apply_plan()
# --------------------------------------------------

def test_apply_plan_moves_file_successfully(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("Document")

    plan = downloads.create_organization_plan(tmp_path, [source])

    result = downloads.apply_plan(plan)

    destination = tmp_path / "Documents" / "report.pdf"

    assert destination.exists()
    assert not source.exists()

    assert result == {
        "moved": 1,
        "skipped": 0,
        "failed": 0,
    }


def test_apply_plan_skips_destination_folder_occupied_by_file(tmp_path):
    source = tmp_path / "photo.png"
    source.write_text("Image")

    # A regular file occupies the path where the Images folder should be.
    images_path = tmp_path / "Images"
    images_path.write_text("Not a folder")

    plan = downloads.create_organization_plan(tmp_path, [source])

    result = downloads.apply_plan(plan)

    assert source.exists()
    assert images_path.is_file()

    assert result == {
        "moved": 0,
        "skipped": 1,
        "failed": 0,
    }


def test_apply_plan_skips_existing_destination(tmp_path):
    source = tmp_path / "photo.png"
    source.write_text("New image")

    # Create the plan before the destination exists.
    plan = downloads.create_organization_plan(tmp_path, [source])

    # Simulate another file appearing at the planned destination.
    images_folder = tmp_path / "Images"
    images_folder.mkdir()

    existing_destination = images_folder / "photo.png"
    existing_destination.write_text("Existing image")

    result = downloads.apply_plan(plan)

    assert source.exists()
    assert existing_destination.read_text() == "Existing image"

    assert result == {
        "moved": 0,
        "skipped": 1,
        "failed": 0,
    }


def test_apply_plan_counts_move_failure(tmp_path, monkeypatch):
    source = tmp_path / "report.pdf"
    source.write_text("Document")

    plan = downloads.create_organization_plan(tmp_path, [source])

    def fake_move(source_path, destination_path):
        raise OSError("Simulated move failure")

    monkeypatch.setattr(downloads.shutil, "move", fake_move)

    result = downloads.apply_plan(plan)

    assert source.exists()

    assert result == {
        "moved": 0,
        "skipped": 0,
        "failed": 1,
    }


def test_apply_plan_rejects_destination_outside_selected_directory(tmp_path):
    source = tmp_path / "report.pdf"
    source.write_text("Document")

    outside_folder = tmp_path.parent / f"{tmp_path.name}_outside"
    destination = outside_folder / "report.pdf"

    plan = [
        {
            "source": source,
            "category": "Documents",
            "destination": destination,
        }
    ]

    result = downloads.apply_plan(plan)

    assert source.exists()
    assert not outside_folder.exists()

    assert result == {
        "moved": 0,
        "skipped": 1,
        "failed": 0,
    }


def test_apply_plan_rejects_symlink_destination_folder(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    outside_folder = tmp_path / "outside"
    outside_folder.mkdir()

    source = root / "photo.png"
    source.write_text("Image")

    images_link = root / "Images"

    try:
        images_link.symlink_to(outside_folder, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("This system does not permit creating directory symlinks.")

    plan = downloads.create_organization_plan(root, [source])

    result = downloads.apply_plan(plan)

    assert source.exists()
    assert result == {
        "moved": 0,
        "skipped": 1,
        "failed": 0,
    }


# --------------------------------------------------
# display_summary()
# --------------------------------------------------

def test_display_summary_shows_all_counters(capsys):
    info = {
        "moved": 2,
        "skipped": 3,
        "failed": 1,
    }

    downloads.display_summary(info)

    output = capsys.readouterr().out.lower()

    assert "moved" in output
    assert "skipped" in output
    assert "failed" in output

    assert "2" in output
    assert "3" in output
    assert "1" in output


# --------------------------------------------------
# setup_logging()
# --------------------------------------------------

def test_setup_logging_uses_correct_log_file(tmp_path, monkeypatch):
    captured_arguments = {}

    def fake_basic_config(**kwargs):
        captured_arguments.update(kwargs)

    monkeypatch.setattr(
        downloads.logging,
        "basicConfig",
        fake_basic_config
    )

    downloads.setup_logging(tmp_path)

    expected_log_path = tmp_path / ".downloads-organizer.log"

    assert captured_arguments["filename"] == str(expected_log_path)
    assert captured_arguments["level"] == logging.INFO
    assert "asctime" in captured_arguments["format"]


# --------------------------------------------------
# main()
# --------------------------------------------------

def test_main_default_mode_does_not_modify_files(tmp_path, monkeypatch):
    source = tmp_path / "photo.png"
    source.write_text("Image")

    monkeypatch.setattr(
        "sys.argv",
        ["downloads.py", str(tmp_path)]
    )

    def unexpected_input(_):
        raise AssertionError("Dry-run mode should not ask for confirmation.")

    monkeypatch.setattr("builtins.input", unexpected_input)

    downloads.main()

    assert source.exists()
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / ".downloads-organizer.log").exists()


def test_main_cancelled_apply_does_not_modify_files(tmp_path, monkeypatch):
    source = tmp_path / "photo.png"
    source.write_text("Image")

    monkeypatch.setattr(
        "sys.argv",
        ["downloads.py", str(tmp_path), "--apply"]
    )

    monkeypatch.setattr("builtins.input", lambda _: "n")

    downloads.main()

    assert source.exists()
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / ".downloads-organizer.log").exists()


def test_main_confirmed_apply_moves_files(tmp_path, monkeypatch):
    source = tmp_path / "photo.png"
    source.write_text("Image")

    monkeypatch.setattr(
        "sys.argv",
        ["downloads.py", str(tmp_path), "--apply"]
    )

    monkeypatch.setattr("builtins.input", lambda _: "y")

    # Keep this test focused on the CLI workflow, not logging configuration.
    monkeypatch.setattr(downloads, "setup_logging", lambda _: None)

    downloads.main()

    destination = tmp_path / "Images" / "photo.png"

    assert destination.exists()
    assert not source.exists()


def test_main_exits_for_invalid_directory(tmp_path, monkeypatch):
    missing_path = tmp_path / "missing_directory"

    monkeypatch.setattr(
        "sys.argv",
        ["downloads.py", str(missing_path)]
    )

    with pytest.raises(SystemExit) as error:
        downloads.main()

    assert error.value.code == "Cannot find directory."