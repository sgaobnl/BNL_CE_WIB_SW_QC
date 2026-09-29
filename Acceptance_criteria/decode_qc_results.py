#!/usr/bin/env python3
"""
Decode qc_results_J_blank_F_PASS.csv or qc_results_J_blank_F_FAIL.csv.

Source Column B example:
S:\\RTS_DAT_LArASIC_QC\\B002T0001\\results\\002_03132_20250815092610_Tray88_SKT6_RT.csv

Output columns:
A: Tray ID
B: Chip SN
C: Tray_loc
D: SKT_loc
E: source Column H
F: source Column F
G: source Column G
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


# Example:
# S:\RTS_DAT_LArASIC_QC\B002T0001\results\
# 002_03132_20250815092610_Tray88_SKT6_RT.csv
PATH_PATTERN = re.compile(
    r"""
    (?P<tray_id>B\d{3}T\d{4})
    .*?
    [\\/]
    (?P<chip_sn>\d{3}_\d{5})
    _
    \d{14}
    _
    Tray(?P<tray_loc>\d+)
    _
    SKT(?P<skt_loc>\d+)
    _RT\.csv
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)


def decode_path(value: str) -> tuple[str, str, str, str]:
    """
    Decode Column B path into:
        Tray ID, Chip SN, Tray_loc, SKT_loc

    Raises ValueError when the expected filename/path format
    cannot be decoded.
    """
    text = str(value).strip()

    match = PATH_PATTERN.search(text)
    if match is None:
        raise ValueError(
            f"Could not decode source Column B path: {text}"
        )

    return (
        match.group("tray_id"),
        match.group("chip_sn"),
        match.group("tray_loc"),
        match.group("skt_loc"),
    )


def decode_csv(input_csv: Path, output_csv: Path) -> None:
    with input_csv.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as source:
        reader = csv.reader(source)

        header = next(reader, None)
        if header is None:
            raise ValueError("Source CSV is empty.")

        if len(header) < 8:
            raise ValueError(
                "Source CSV must have at least 8 columns "
                "because Column H is required."
            )

        output_header = [
            "Tray ID",
            "Chip SN",
            "Tray_loc",
            "SKT_loc",
            header[7],  # source H
            header[5],  # source F
            header[6],  # source G
        ]

        output_csv.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_csv.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as target:
            writer = csv.writer(target)
            writer.writerow(output_header)

            for row_number, row in enumerate(reader, start=2):
                if len(row) < 8:
                    raise ValueError(
                        f"Row {row_number} has only {len(row)} "
                        "columns; at least 8 are required."
                    )

                tray_id, chip_sn, tray_loc, skt_loc = (
                    decode_path(row[1])  # source Column B
                )

                writer.writerow(
                    [
                        tray_id,
                        chip_sn,
                        tray_loc,
                        skt_loc,
                        row[7],  # source H -> output E
                        row[5],  # source F -> output F
                        row[6],  # source G -> output G
                    ]
                )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Decode QC result CSV paths."
    )

    parser.add_argument(
        "input_csv",
        type=Path,
        help=(
            "Input CSV, e.g. "
            "qc_results_J_blank_F_PASS.csv or "
            "qc_results_J_blank_F_FAIL.csv"
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV path. Defaults to <input>_decoded.csv.",
    )

    args = parser.parse_args()

    if not args.input_csv.exists():
        raise FileNotFoundError(
            f"Input file not found: {args.input_csv}"
        )

    output_csv = args.output
    if output_csv is None:
        output_csv = (
            args.input_csv.with_suffix("")
            .with_name(
                args.input_csv.stem + "_decoded"
            )
            .with_suffix(".csv")
        )

    decode_csv(
        args.input_csv,
        output_csv,
    )

    print(f"Decoded CSV written to: {output_csv}")


if __name__ == "__main__":
    main()
