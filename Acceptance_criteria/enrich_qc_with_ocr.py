#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PIC_ROOT_PATH = Path(r"S:\RTS_DAT_LArASIC_QC")

BMP_PATTERN = re.compile(
    r"^SN_(?P<ocr_sn>\d{3}_\d{5})_Tray_(?P<ocr_loc>\d+)_(?P<timestamp>\d{14})\.bmp$",
    re.IGNORECASE,
)


def decode_ocr_filename(filename: str):
    m = BMP_PATTERN.fullmatch(filename)
    if m is None:
        return None
    return {
        "OCR_SN": m.group("ocr_sn"),
        "OCR_LOC": int(m.group("ocr_loc")),
        "Timestamp": m.group("timestamp"),
    }


def find_ocr_file(row: dict, pic_root: Path):
    tray_id = str(row["Tray ID"]).strip()
    timestamp = str(row["Timestamp"]).strip()
    pic_path = pic_root / tray_id / "images" / "SN_OCR"

    if not pic_path.is_dir():
        return None, None

    # Exact timestamp match + required BMP filename pattern.
    for p in pic_path.glob("*.bmp"):
        decoded = decode_ocr_filename(p.name)
        if decoded and decoded["Timestamp"] == timestamp:
            return p.name, decoded

    return None, None


def enrich_csv(input_csv: Path, output_csv: Path, pic_root: Path):
    with input_csv.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        required = ["Tray ID", "Chip SN", "Timestamp", "Tray_loc"]
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))

        fieldnames = list(reader.fieldnames)
        for name in ["OCR_FS", "OCR_SN", "SN_match", "OCR_LOC", "LOC_Match"]:
            if name not in fieldnames:
                fieldnames.append(name)

        output_csv.parent.mkdir(parents=True, exist_ok=True)

        rows_processed = matched = sn_matches = loc_matches = 0

        with output_csv.open("w", newline="", encoding="utf-8-sig") as g:
            writer = csv.DictWriter(g, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                rows_processed += 1
                row.update({
                    "OCR_FS": "",
                    "OCR_SN": "",
                    "SN_match": "False",
                    "OCR_LOC": "",
                    "LOC_Match": "False",
                })

                filename, ocr = find_ocr_file(row, pic_root)

                if ocr is not None:
                    matched += 1
                    row["OCR_FS"] = filename
                    row["OCR_SN"] = ocr["OCR_SN"]
                    row["OCR_LOC"] = str(ocr["OCR_LOC"])

                    sn_ok = (
                        str(ocr["OCR_SN"]).strip()
                        == str(row["Chip SN"]).strip()
                    )
                    row["SN_match"] = str(sn_ok)
                    sn_matches += int(sn_ok)

                    try:
                        loc_ok = (
                            int(ocr["OCR_LOC"]) -1 == int(str(row["Tray_loc"]).strip())
                        )
                    except ValueError:
                        loc_ok = False

                    row["LOC_Match"] = str(loc_ok)
                    loc_matches += int(loc_ok)

                writer.writerow(row)

    return rows_processed, matched, sn_matches, loc_matches


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--pic-root", type=Path, default=PIC_ROOT_PATH)
    args = parser.parse_args()

    if not args.input_csv.exists():
        raise FileNotFoundError(args.input_csv)

    output = args.output or args.input_csv.with_name(
        args.input_csv.stem + "_ocr.csv"
    )

    summary = enrich_csv(args.input_csv, output, args.pic_root)

    print("Output:", output)
    print("Rows processed:", summary[0])
    print("OCR files matched:", summary[1])
    print("SN matches:", summary[2])
    print("Location matches:", summary[3])


if __name__ == "__main__":
    main()
