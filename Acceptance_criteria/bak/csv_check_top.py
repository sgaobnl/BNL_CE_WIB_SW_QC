from pathlib import Path
import csv
from typing import Dict, List, Callable, Tuple, Any

from check_row_count import check_row_count
from check_sn_row5 import check_serial_number
from check_row20 import check_row20
from check_row21 import check_row21


CheckFunction = Callable[
    [List[List[str]]],
    Tuple[bool, Dict[str, Any]]
]


class CSVAnalyzer:
    """
    Common analyzer for RT and LN CSV files.

    All configured checks are executed even when one check fails.
    Every check result is recorded in the final CSV.
    """

    CHECKS = [
        ("Check_1", check_row_count),
        ("Check_2", check_serial_number),
        ("Check_3", check_row20),
        ("Check_4", check_row21),

        # Add future checks here:
        # ("Check_5", check_row22),
        # ("Check_6", check_row23),
    ]

    def __init__(self, csv_file: Path):
        self.csv_file = Path(csv_file)
        self.rows: List[List[str]] = []

        self.result: Dict[str, Any] = {
            "File": self.csv_file.name,
            "File_Path": str(self.csv_file),
            "File_Type": self._get_file_type(),
            "Overall_Result": "FAIL",
            "Fail_Code": "",
        }

    # ==================================================
    # Main analysis
    # ==================================================

    def analyze(self) -> Dict[str, Any]:
        """
        Read the file and run ALL checks.

        A failed check does not stop subsequent checks.
        """

        if not self._read_file():
            return self.result

        failed_checks = []

        for check_name, check_function in self.CHECKS:

            passed, check_result = self._run_check(
                check_name,
                check_function,
            )

            self._store_check_result(
                check_name,
                passed,
                check_result,
            )

            if not passed:
                failed_checks.append(
                    check_result.get(
                        "fail_code",
                        f"{check_name} failed"
                    )
                )

        # ----------------------------------------------
        # Overall result is determined only AFTER all
        # checks have completed.
        # ----------------------------------------------

        if failed_checks:
            self.result["Overall_Result"] = "FAIL"

            # Keep all failure codes in one CSV field
            self.result["Fail_Code"] = " | ".join(
                code for code in failed_checks if code
            )
        else:
            self.result["Overall_Result"] = "PASS"
            self.result["Fail_Code"] = ""

        return self.result

    # ==================================================
    # Read CSV
    # ==================================================

    def _read_file(self) -> bool:
        try:
            with self.csv_file.open(
                "r",
                newline="",
                encoding="utf-8-sig",
            ) as f:
                self.rows = list(csv.reader(f))

            return True

        except Exception as exc:
            self.result["Overall_Result"] = "FAIL"
            self.result["Fail_Code"] = (
                f"FAIL: cannot read file - {exc}"
            )
            return False

    # ==================================================
    # Run one check
    # ==================================================

    def _run_check(
        self,
        check_name: str,
        check_function: CheckFunction,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Run one check independently.

        An exception in one check is converted into a FAIL
        for that check, without stopping other checks.
        """

        try:
            return check_function(self.rows)

        except Exception as exc:
            return False, {
                "fail_code": (
                    f"FAIL: {check_name} exception - {exc}"
                )
            }

    # ==================================================
    # Store check result
    # ==================================================

    def _store_check_result(
        self,
        check_name: str,
        passed: bool,
        check_result: Dict[str, Any],
    ) -> None:
        """
        Store each check independently.

        Example:
            Check_1_Result = PASS
            Check_2_Result = FAIL
            Check_2_Fail_Code = FAIL: SN is incorrect

        Any additional values returned by the check are
        stored automatically.
        """

        self.result[f"{check_name}_Result"] = (
            "PASS" if passed else "FAIL"
        )

        for key, value in check_result.items():

            if key == "fail_code":
                if value:
                    self.result[
                        f"{check_name}_Fail_Code"
                    ] = value
                continue

            self.result[f"{check_name}_{key}"] = value

    # ==================================================
    # Determine RT / LN
    # ==================================================

    def _get_file_type(self) -> str:

        name = self.csv_file.name.upper()

        if name.endswith("_RT.CSV"):
            return "RT"

        if name.endswith("_LN.CSV"):
            return "LN"

        return "UNKNOWN"


class CSVResultExporter:
    """
    Export analysis results to CSV.
    """

    def __init__(self, output_file: Path):
        self.output_file = Path(output_file)

    def export(
        self,
        results: List[Dict[str, Any]]
    ) -> None:
        """
        Export results using the union of all result keys.
        """

        if not results:
            return

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Keep the main columns first.
        preferred_columns = [
            "File",
            "File_Path",
            "File_Type",
            "Overall_Result",
            "Fail_Code",
        ]

        all_columns = []

        for column in preferred_columns:
            if any(
                column in result
                for result in results
            ):
                all_columns.append(column)

        # Then add all check-specific columns.
        for result in results:
            for column in result.keys():
                if column not in all_columns:
                    all_columns.append(column)

        with self.output_file.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=all_columns,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(results)


def analyze_files(
    input_files: List[Path],
) -> List[Dict[str, Any]]:
    """
    Analyze all supplied RT/LN files.

    Each file is analyzed independently.
    """

    results = []

    for csv_file in input_files:

        csv_file = Path(csv_file)

        if not csv_file.is_file():
            results.append({
                "File": csv_file.name,
                "File_Path": str(csv_file),
                "File_Type": "UNKNOWN",
                "Overall_Result": "FAIL",
                "Fail_Code": (
                    f"FAIL: file does not exist: {csv_file}"
                ),
            })
            continue

        analyzer = CSVAnalyzer(csv_file)
        results.append(
            analyzer.analyze()
        )

    return results


def main() -> None:

    # ==================================================
    # Configuration
    # ==================================================

    input_files = [
        Path(
            r"S:\RTS_DAT_LArASIC_QC\B006T0001\results\006_01186_20251006165356_Tray59_SKT3_RT.csv"
        ),
        Path(
            r"S:\RTS_DAT_LArASIC_QC\B006T0001\results\006_01186_20251006165356_Tray59_SKT3_LN.csv"
        ),
    ]

    output_dir = Path(
        r"S:\RTS_DAT_LArASIC_QC\Acceptance"
    )

    # ==================================================
    # Analyze
    # ==================================================

    results = analyze_files(input_files)

    if not results:
        return

    # ==================================================
    # Get serial number
    # ==================================================

    serial_number = None

    for result in results:

        sn = result.get("Check_2_sn")

        if sn:
            serial_number = sn
            break

    if not serial_number:
        print(
            "Warning: serial number could not be determined."
        )

        # Still export the results instead of stopping.
        serial_number = "UNKNOWN"

    # ==================================================
    # Generate output filename
    # ==================================================

    output_file = (
        output_dir /
        f"{serial_number}_ana_result.csv"
    )

    # ==================================================
    # Export
    # ==================================================

    exporter = CSVResultExporter(output_file)

    exporter.export(results)

    print(
        f"Analysis results saved to: {output_file}"
    )


if __name__ == "__main__":
    main()
