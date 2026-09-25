from pathlib import Path
import re
import json
from typing import Dict, List, Any, Optional


# BxxxTxxxx means:
#   B + 3 digits + T + 4 digits
# Example: B123T4567
FOLDER_PATTERN = re.compile(r"^B\d{3}T\d{4}$", re.IGNORECASE)


def empty_index() -> Dict[str, Dict[str, List[Any]]]:
    return {
        "RT": {},
        "LN": {},
    }


def load_existing_index(json_file: Path) -> Dict[str, Dict[str, List[Any]]]:
    """
    Load the existing JSON index if it exists.
    If it does not exist, return an empty index.
    """
    if not json_file.exists():
        print(f"No existing index found: {json_file}")
        print("Creating a new index.")
        return empty_index()

    try:
        with json_file.open("r", encoding="utf-8") as f:
            index = json.load(f)

        index.setdefault("RT", {})
        index.setdefault("LN", {})

        print(f"Loaded existing index: {json_file}")
        return index

    except (json.JSONDecodeError, OSError) as e:
        print(f"Warning: Could not read existing index: {e}")
        print("Starting with an empty index.")
        return empty_index()


def normalize_index_schema(index: Dict[str, Dict[str, List[Any]]]) -> None:
    """
    Upgrade older RT schema from list[str] to list[dict].
    LN stays as list[str].
    """
    normalized_rt = {}

    for folder_name, rt_entries in index.get("RT", {}).items():
        upgraded = []

        for entry in rt_entries:
            if isinstance(entry, dict):
                path = str(entry.get("path", ""))
                if not path:
                    continue

                upgraded.append(
                    {
                        "path": path,
                        "has_ln": bool(entry.get("has_ln", False)),
                        "ln_path": entry.get("ln_path"),
                    }
                )
            else:
                path = str(entry)
                if not path:
                    continue

                upgraded.append(
                    {
                        "path": path,
                        "has_ln": False,
                        "ln_path": None,
                    }
                )

        if upgraded:
            normalized_rt[folder_name] = upgraded

    index["RT"] = normalized_rt
    index.setdefault("LN", {})


def build_existing_file_set(index: Dict[str, Dict[str, List[Any]]]) -> set:
    """
    Build a set containing all CSV files already listed in the JSON index.
    """
    existing_files = set()

    for folder_files in index.get("LN", {}).values():
        for file_path in folder_files:
            existing_files.add(str(Path(file_path)).lower())

    for folder_files in index.get("RT", {}).values():
        for entry in folder_files:
            if isinstance(entry, dict):
                file_path = entry.get("path", "")
            else:
                file_path = str(entry)

            if file_path:
                existing_files.add(str(Path(file_path)).lower())

    return existing_files


def matching_ln_path(rt_path: Path) -> Optional[Path]:
    """
    For xxx_RT.csv, return xxx_LN.csv in the same folder.
    If the RT file name does not match the expected pattern, return None.
    """
    if not rt_path.name.lower().endswith("_rt.csv"):
        return None

    prefix = rt_path.name[:-7]  # remove "_RT.csv"
    return rt_path.parent / f"{prefix}_LN.csv"


def refresh_rt_markers(index: Dict[str, Dict[str, List[Any]]]) -> int:
    """
    Update every RT entry with has_ln / ln_path based on the filesystem.
    Returns the number of RT files that currently have a matching LN file.
    """
    matched_count = 0

    for folder_name, rt_entries in index.get("RT", {}).items():
        for entry in rt_entries:
            rt_path = Path(entry["path"])
            ln_path = matching_ln_path(rt_path)

            has_ln = ln_path is not None and ln_path.is_file()

            entry["has_ln"] = has_ln
            entry["ln_path"] = str(ln_path) if has_ln else None

            if has_ln:
                matched_count += 1

    return matched_count


def remove_missing_files(index: Dict[str, Dict[str, List[Any]]]) -> int:
    """
    Remove files from the JSON index if they no longer exist on the filesystem.
    Also remove empty folder entries.

    Returns:
        Number of removed file entries.
    """
    removed_count = 0

    # Remove missing LN files
    for folder_name in list(index.get("LN", {}).keys()):
        old_files = index["LN"][folder_name]
        kept_files = []

        for file_path in old_files:
            if Path(file_path).is_file():
                kept_files.append(file_path)
            else:
                print(f"  REMOVED LN: {file_path}")
                removed_count += 1

        if kept_files:
            index["LN"][folder_name] = kept_files
        else:
            del index["LN"][folder_name]

    # Remove missing RT files
    for folder_name in list(index.get("RT", {}).keys()):
        old_entries = index["RT"][folder_name]
        kept_entries = []

        for entry in old_entries:
            rt_path = entry["path"] if isinstance(entry, dict) else str(entry)

            if Path(rt_path).is_file():
                if isinstance(entry, dict):
                    kept_entries.append(entry)
                else:
                    kept_entries.append(
                        {
                            "path": rt_path,
                            "has_ln": False,
                            "ln_path": None,
                        }
                    )
            else:
                print(f"  REMOVED RT: {rt_path}")
                removed_count += 1

        if kept_entries:
            index["RT"][folder_name] = kept_entries
        else:
            del index["RT"][folder_name]

    return removed_count


def scan_qc_files(root_path: Path, index: Dict[str, Dict[str, List[Any]]]) -> int:
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
        raise FileNotFoundError(f"Root path does not exist: {root_path}")

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

            if name_lower.endswith("_rt.csv"):
                file_type = "RT"
            elif name_lower.endswith("_ln.csv"):
                file_type = "LN"
            else:
                continue

            file_path = str(csv_file)
            normalized_path = file_path.lower()

            if normalized_path in existing_files:
                continue

            if subfolder.name not in index[file_type]:
                index[file_type][subfolder.name] = []

            if file_type == "RT":
                ln_path = matching_ln_path(csv_file)
                has_ln = ln_path is not None and ln_path.is_file()

                index["RT"][subfolder.name].append(
                    {
                        "path": file_path,
                        "has_ln": has_ln,
                        "ln_path": str(ln_path) if has_ln else None,
                    }
                )

            else:
                index["LN"][subfolder.name].append(file_path)

            existing_files.add(normalized_path)
            new_file_count += 1

            print(f"  NEW {file_type}: {csv_file.name}")

    return new_file_count


def print_index(index: Dict[str, Dict[str, List[Any]]]) -> None:
    print("\nRT index:")

    for folder, entries in sorted(index.get("RT", {}).items()):
        print(f"  {folder}")
        for entry in entries:
            print(f"    {entry['path']}  | has_ln={entry['has_ln']}")

    print("\nLN index:")

    for folder, files in sorted(index.get("LN", {}).items()):
        print(f"  {folder}")
        for f in files:
            print(f"    {f}")


if __name__ == "__main__":

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------
    ROOT_PATH = Path(r"S:\RTS_DAT_LArASIC_QC")
    JSON_FILE = ROOT_PATH / "Acceptance" / "qc_csv_index.json"

    # --------------------------------------------------
    # 1. Load existing JSON index
    # --------------------------------------------------
    result = load_existing_index(JSON_FILE)

    # Normalize older JSON schema if needed
    normalize_index_schema(result)

    # --------------------------------------------------
    # 2. Remove files that no longer exist
    # --------------------------------------------------
    removed_file_count = remove_missing_files(result)

    # --------------------------------------------------
    # 3. Scan and add newly discovered files
    # --------------------------------------------------
    new_file_count = scan_qc_files(ROOT_PATH, result)

    # --------------------------------------------------
    # 4. Refresh RT markers after the scan
    # --------------------------------------------------
    matched_rt_count = refresh_rt_markers(result)

    # --------------------------------------------------
    # 5. Print updated index
    # --------------------------------------------------
    print_index(result)

    # --------------------------------------------------
    # 6. Save synchronized JSON
    # --------------------------------------------------
    JSON_FILE.parent.mkdir(parents=True, exist_ok=True)

    with JSON_FILE.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------
    print("\n--------------------------------")
    print(f"New files added    : {new_file_count}")
    print(f"Files removed      : {removed_file_count}")
    print(f"RT with matching LN: {matched_rt_count}")
    print(f"Index saved to     : {JSON_FILE}")
    print("--------------------------------")
