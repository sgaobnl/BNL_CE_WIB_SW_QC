from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


HERE = Path(__file__).resolve().parent
MAIN_CANDIDATES = [
    HERE,
    HERE / "main_with_gain_inl_rows34_119",
]
for candidate in MAIN_CANDIDATES:
    if candidate.is_dir() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

try:
    from main_with_gain_inl_rows34_119 import CSVAnalyzer
except Exception as exc:
    raise SystemExit(
        "Cannot import main_with_gain_inl_rows34_119.py. "
        "Place this script in the same directory as the main QC script and its check modules. "
        f"Import error: {exc}"
    )


def iter_has_ln_entries(index: Dict[str, Any]) -> Iterable[Tuple[str, str, Dict[str, Any]]]:
    """Yield only RT entries whose has_ln field is exactly True."""
    rt_section = index.get("RT", {})
    if not isinstance(rt_section, dict):
        return

    for batch, items in rt_section.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("has_ln") is True:
                yield "RT", str(batch), item


def check_one(path: str) -> Dict[str, Any]:
    analyzer = CSVAnalyzer(Path(path))
    return analyzer.analyze()


def write_results(path: Path, rows: List[Dict[str, Any]]) -> None:
    fieldnames = [
        "batch",
        "rt_path",
        "ln_path",
        "rt_exists",
        "ln_exists",
        "rt_result",
        "ln_result",
        "pair_result",
        "rt_fail_code",
        "ln_fail_code",
    ]

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the complete QC main script for every RT JSON entry "
            "with has_ln=true, checking both RT and LN CSV files."
        )
    )
    parser.add_argument(
        "json_index",
        type=Path,
        help="Path to qc_csv_index.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("qc_results_has_ln_true.csv"),
        help="Output CSV file",
    )
    args = parser.parse_args()

    with args.json_index.open("r", encoding="utf-8") as f:
        index = json.load(f)

    selected = list(iter_has_ln_entries(index))

    results: List[Dict[str, Any]] = []
    total = len(selected)
    print(f"Selected RT entries with has_ln=true: {total}")

    for number, (_, batch, item) in enumerate(selected, start=1):
        rt_path = str(item.get("path", ""))
        ln_path = str(item.get("ln_path", ""))
#        if 'B006T0001' not in rt_path:
#            continue



        goodchips = [
                     'Tray00_SKT0',
                     'Tray02_SKT2',
                     'Tray04_SKT4',
                     'Tray05_SKT5',
                     'Tray06_SKT6',
                     'Tray07_SKT7',

                     'Tray08_SKT0',
                     'Tray09_SKT1',
                     'Tray12_SKT4',
                     'Tray13_SKT5',

                     'Tray17_SKT1',
                     'Tray18_SKT2',
                     'Tray19_SKT3',
                     'Tray20_SKT4',
                     'Tray21_SKT5',
                     'Tray22_SKT6',
                     'Tray23_SKT7',

                     'Tray25_SKT1',
                     'Tray26_SKT2',
                     'Tray28_SKT4',
                     'Tray29_SKT5',
                     'Tray31_SKT7',

                     'Tray32_SKT0',
                     'Tray33_SKT1',
                     'Tray34_SKT2',
                     'Tray35_SKT3',
                     'Tray36_SKT4',
                     'Tray37_SKT5',
                     'Tray39_SKT7',


                     'Tray41_SKT1',
                     'Tray42_SKT2',
                     'Tray43_SKT3',
                     'Tray44_SKT4',
                     'Tray45_SKT5',
                     'Tray46_SKT6',

                     'Tray48_SKT0',
                     'Tray49_SKT1',
                     'Tray50_SKT2',
                     'Tray51_SKT3',
                     'Tray52_SKT4',


                     'Tray56_SKT0',
                     'Tray57_SKT1',
                     'Tray58_SKT2',
                     'Tray59_SKT3',
                     'Tray60_SKT4',
                     'Tray61_SKT5',
                     'Tray62_SKT6',
                     'Tray63_SKT7',

                     'Tray64_SKT0',
                     'Tray65_SKT1',
                     'Tray67_SKT3',
                     'Tray68_SKT4',
                     'Tray69_SKT5',
                     'Tray70_SKT6',

                     'Tray72_SKT0',
                     'Tray73_SKT1',
                     'Tray74_SKT2',
                     'Tray75_SKT3',
                     'Tray78_SKT6',
                     'Tray79_SKT7',

                     'Tray80_SKT0',
                     'Tray81_SKT1',
                     'Tray82_SKT2',
                     'Tray83_SKT3',
                     'Tray84_SKT4',
                     'Tray85_SKT5',
                     'Tray86_SKT6',

                     'Tray88_SKT0',
                     'Tray89_SKT1']

#        pos = rt_path.find("_Tray")
#        sub_tray_skt = rt_path[pos+1:pos+12]
#        if sub_tray_skt not in goodchips:
#            continue


        rt_exists = Path(rt_path).is_file()
        ln_exists = Path(ln_path).is_file()

        row: Dict[str, Any] = {
            "batch": batch,
            "rt_path": rt_path,
            "ln_path": ln_path,
            "rt_exists": rt_exists,
            "ln_exists": ln_exists,
            "rt_result": "NOT_RUN",
            "ln_result": "NOT_RUN",
            "pair_result": "NOT_RUN",
            "rt_fail_code": "",
            "ln_fail_code": "",
        }

        if rt_exists:
            try:
                rt_result = check_one(rt_path)
                row["rt_result"] = rt_result.get("Overall_Result", "FAIL")
                row["rt_fail_code"] = rt_result.get("Fail_Code", "")
            except Exception as exc:
                row["rt_result"] = "FAIL"
                row["rt_fail_code"] = f"FAIL: batch runner exception - {exc}"
        else:
            row["rt_fail_code"] = "FILE NOT FOUND: RT path is not accessible"

        if ln_exists:
            try:
                ln_result = check_one(ln_path)
                row["ln_result"] = ln_result.get("Overall_Result", "FAIL")
                row["ln_fail_code"] = ln_result.get("Fail_Code", "")
            except Exception as exc:
                row["ln_result"] = "FAIL"
                row["ln_fail_code"] = f"FAIL: batch runner exception - {exc}"
        else:
            row["ln_fail_code"] = "FILE NOT FOUND: LN path is not accessible"

        if row["rt_result"] == "PASS" and row["ln_result"] == "PASS":
            row["pair_result"] = "PASS"
        elif row["rt_result"] == "NOT_RUN" or row["ln_result"] == "NOT_RUN":
            row["pair_result"] = "NOT_RUN"
        else:
            row["pair_result"] = "FAIL"

        results.append(row)

        if number % 100 == 0 or number == total:
            print(f"Processed {number}/{total}")

    write_results(args.output, results)

    pass_count = sum(r["pair_result"] == "PASS" for r in results)
    fail_count = sum(r["pair_result"] == "FAIL" for r in results)
    not_run_count = sum(r["pair_result"] == "NOT_RUN" for r in results)

    print(f"PASS: {pass_count}")
    print(f"FAIL: {fail_count}")
    print(f"NOT_RUN: {not_run_count}")
    print(f"Results: {args.output.resolve()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
