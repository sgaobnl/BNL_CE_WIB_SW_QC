#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

PATH_PATTERN = re.compile(
    r"""
    (?P<tray_id>B\d{3}T\d{4})
    .*?[\\/]
    (?P<chip_sn>\d{3}_\d{5})
    _
    (?P<timestamp>\d{14})
    _
    Tray(?P<tray_loc>\d+)
    _
    SKT(?P<skt_loc>\d+)
    _
    RT\.csv
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)


def decode_path(value: str):
    text = str(value).strip()
    m = PATH_PATTERN.search(text)
    if m is None:
        raise ValueError(f"Could not decode Column B: {text}")

    tray_loc = int(m.group("tray_loc"))
    return (
        m.group("tray_id"),
        m.group("chip_sn"),
        m.group("timestamp"),
        tray_loc,
        tray_loc // 15,
        tray_loc % 15,
        int(m.group("skt_loc")),
    )


def decode_csv(input_csv: Path, output_csv: Path):
    with input_csv.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            raise ValueError("Source CSV is empty.")
        if len(header) < 8:
            raise ValueError("Source CSV must have at least 8 columns.")

        out_header = [
            "Tray ID", "Chip SN", "Timestamp", "Tray_loc",
            "Tray_Row", "Tray_Col", "SKT_loc",
            header[7], header[5], header[6]
        ]

        with output_csv.open("w", newline="", encoding="utf-8-sig") as g:
            writer = csv.writer(g)
            writer.writerow(out_header)

            for row_number, row in enumerate(reader, start=2):
                if len(row) < 8:
                    raise ValueError(
                        f"Row {row_number} has only {len(row)} columns."
                    )

                decoded = decode_path(row[1])
                writer.writerow([
                    decoded[0],   # Tray ID
                    decoded[1],   # Chip SN
                    decoded[2],   # Timestamp
                    decoded[3],   # Tray_loc
                    decoded[4],   # Tray_Row = tray_loc // 15
                    decoded[5],   # Tray_Col = tray_loc % 15
                    decoded[6],   # SKT_loc
                    row[7],       # source H -> output H
                    row[5],       # source F -> output I
                    row[6],       # source G -> output J
                ])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input_csv", type=Path)
    p.add_argument("-o", "--output", type=Path)
    args = p.parse_args()

    if not args.input_csv.exists():
        raise FileNotFoundError(args.input_csv)

    output = args.output or args.input_csv.with_name(
        args.input_csv.stem + "_decoded.csv"
    )
    decode_csv(args.input_csv, output)
    print(output)


if __name__ == "__main__":
    main()
