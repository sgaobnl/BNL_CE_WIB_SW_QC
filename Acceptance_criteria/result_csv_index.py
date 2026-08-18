from pathlib import Path
import re
import json
from typing import Dict, List


# BxxxTxxxx means:
#   B + 3 digits + T + 4 digits
# Example: B123T4567
FOLDER_PATTERN = re.compile(r"^B\d{3}T\d{4}$", re.IGNORECASE)


def load_existing_index(json_file: Path) -> Dict[str, Dict[str, List[str]]]:
    """
    Load the existing JSON index if it exists.

    If it does not exist, return an empty index.
    """
    if not json_file.exists():
        print(f"No existing index found: {json_file}")
        print("Creating a new index.")

        return {
            "RT": {},
            "LN": {},
        }

    try:
        with json_file.open("r", encoding="utf-8") as f:
            index = json.load(f)

        # Make sure expected keys exist
        index.setdefault("RT", {})
        index.setdefault("LN", {})

        print(f"Loaded existing index: {json_file}")

        return index

    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not read existing index: {e}")
        print("Starting with an empty index.")

        return {
            "RT": {},
            "LN": {},
        }


def build_existing_file_set(
    index: Dict[str, Dict[str, List[str]]]
) -> set:
    """
    Build a set containing all CSV files already listed
    in the JSON index.

    Using a set makes duplicate checking fast.
    """
    existing_files = set()

    for file_type in ("RT", "LN"):
        for folder_files in index.get(file_type, {}).values():
            for file_path in folder_files:
                # Normalize path/case for Windows
                existing_files.add(str(Path(file_path)).lower())

    return existing_files


def scan_qc_files(
    root_path: Path,
    index: Dict[str, Dict[str, List[str]]]
) -> int:
    """
    Scan ROOT_PATH for folders matching BxxxTxxxx.

    Under each matching folder:
        - Look for a direct child folder named 'results'
        - Find *_RT.csv files
        - Find *_LN.csv files

    Files already listed in the JSON index are ignored.

    Returns:
        Number of newly added files.
    """

    if not root_path.exists():
        raise FileNotFoundError(
            f"Root path does not exist: {root_path}"
        )

    # Build fast lookup table for files already indexed
    existing_files = build_existing_file_set(index)

    new_file_count = 0

    for subfolder in root_path.iterdir():

        if not subfolder.is_dir():
            continue

        if not FOLDER_PATTERN.match(subfolder.name):
            continue

        results_dir = subfolder / "results"

        if not results_dir.is_dir():
            continue

        print(f"Scanning: {results_dir}")

        for csv_file in results_dir.iterdir():

            if not csv_file.is_file():
                continue

            name_lower = csv_file.name.lower()

            # Determine file type
            if name_lower.endswith("_rt.csv"):
                file_type = "RT"

            elif name_lower.endswith("_ln.csv"):
                file_type = "LN"

            else:
                continue

            file_path = str(csv_file)

            # Windows paths are case-insensitive
            normalized_path = file_path.lower()

            # Skip files already in JSON
            if normalized_path in existing_files:
                continue

            # Create folder entry if necessary
            if subfolder.name not in index[file_type]:
                index[file_type][subfolder.name] = []

            # Add new file
            index[file_type][subfolder.name].append(file_path)

            # Add to existing set immediately so duplicates
            # cannot be added during the same scan
            existing_files.add(normalized_path)

            new_file_count += 1

            print(
                f"  NEW {file_type}: {csv_file.name}"
            )

    return new_file_count


def print_index(
    index: Dict[str, Dict[str, List[str]]]
) -> None:

    print("\nRT index:")

    for folder, files in sorted(index["RT"].items()):
        print(f"  {folder}")

        for f in files:
            print(f"    {f}")

    print("\nLN index:")

    for folder, files in sorted(index["LN"].items()):
        print(f"  {folder}")

        for f in files:
            print(f"    {f}")


def remove_missing_files(
    index: Dict[str, Dict[str, List[str]]]
) -> int:
    """
    Remove files from the JSON index if they no longer
    exist on the filesystem.

    Also remove empty BxxxTxxxx entries.

    Returns:
        Number of removed file entries.
    """

    removed_count = 0

    for file_type in ("RT", "LN"):

        # list(...) is required because we may delete dictionary entries
        for folder_name in list(index[file_type].keys()):

            old_files = index[file_type][folder_name]
            existing_files = []

            for file_path in old_files:

                if Path(file_path).is_file():
                    existing_files.append(file_path)
                else:
                    print(
                        f"  REMOVED {file_type}: {file_path}"
                    )
                    removed_count += 1

            # Update list
            if existing_files:
                index[file_type][folder_name] = existing_files
            else:
                # No files left under this folder
                del index[file_type][folder_name]

    return removed_count


if __name__ == "__main__":

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------
    ROOT_PATH = Path(r"S:\RTS_DAT_LArASIC_QC")

    # JSON file stored beside this Python script
    JSON_FILE = ROOT_PATH / "Acceptance" / "qc_csv_index.json"

    # --------------------------------------------------
    # 1. Load existing JSON index
    # --------------------------------------------------

    result = load_existing_index(JSON_FILE)

    # --------------------------------------------------
    # 2. Remove files that no longer exist
    # --------------------------------------------------

    removed_file_count = remove_missing_files(result)

    # --------------------------------------------------
    # 3. Scan and add newly discovered files
    # --------------------------------------------------

    new_file_count = scan_qc_files(
        ROOT_PATH,
        result,
    )

    # --------------------------------------------------
    # 4. Print updated index
    # --------------------------------------------------

    print_index(result)

    # --------------------------------------------------
    # 5. Save synchronized JSON
    # --------------------------------------------------

    with JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            indent=2,
        )

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n--------------------------------")
    print(f"New files added   : {new_file_count}")
    print(f"Files removed     : {removed_file_count}")
    print(f"Index saved to    : {JSON_FILE}")
    print("--------------------------------")


