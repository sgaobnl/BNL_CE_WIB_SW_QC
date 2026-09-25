from pathlib import Path
import csv
from typing import Dict, List, Callable, Tuple, Any

from check_row_count import check_row_count
from check_sn_row5 import check_serial_number
from check_row20 import check_row20
from check_row21 import check_row21


CheckFunction = Callable[
    [List[List[str]], str],
    Tuple[bool, Dict[str, Any]]
]


class CSVAnalyzer:
    """
    Analyzer for both RT and LN CSV files.

    Every check runs even if an earlier check fails.
    """

    CHECKS = [
        ("Check_1", check_row_count),
        ("Check_2", check_serial_number),
        ("Check_3", check_row20),
        ("Check_4", check_row21),

        # Add future checks here:
        #
        # from check_row22 import check_row22
        # ("Check_5", check_row22),
        #
        # from check_row23 import check_row23
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
        Run every configured check.
        A failure does not stop subsequent checks.
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
                        f"{check_name} failed",
                    )
                )

        if failed_checks:
            self.result["Overall_Result"] = "FAIL"
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
        try:
            return check_function(
                self.rows,
                self.result["File_Type"],
            )

        except Exception as exc:
            return False, {
                "fail_code": (
                    f"FAIL: {check_name} exception - {exc}"
                )
            }

    # ==================================================
    # Store one check result
    # ==================================================

    def _store_check_result(
        self,
        check_name: str,
        passed: bool,
        check_result: Dict[str, Any],
    ) -> None:
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

            self.result[
                f"{check_name}_{key}"
            ] = value

    # ==================================================
    # Determine file type
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
    Export results to CSV.
    """

    def __init__(self, output_file: Path):
        self.output_file = Path(output_file)

    def export(
        self,
        results: List[Dict[str, Any]],
    ) -> None:
        if not results:
            return

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        preferred_columns = [
            "File",
            "File_Path",
            "File_Type",
            "Overall_Result",
            "Fail_Code",
        ]

        columns = []

        for column in preferred_columns:
            if any(
                column in result
                for result in results
            ):
                columns.append(column)

        for result in results:
            for column in result.keys():
                if column not in columns:
                    columns.append(column)

        with self.output_file.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            writer = csv.DictWriter(
                f,
                fieldnames=columns,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(results)


def analyze_files(
    input_files: List[Path],
) -> List[Dict[str, Any]]:
    """
    Analyze each RT/LN file independently.
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
                    f"FAIL: file does not exist: "
                    f"{csv_file}"
                ),
            })
            continue

        analyzer = CSVAnalyzer(csv_file)
        results.append(analyzer.analyze())

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
        print("No analysis results.")
        return

    # ==================================================
    # Determine serial number
    # ==================================================

    serial_number = None

    for result in results:
        sn = result.get("Check_2_sn")

        if sn:
            serial_number = sn
            break

    if not serial_number:
        serial_number = "UNKNOWN"

    # ==================================================
    # Output filename
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
        f"Analysis results saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()
