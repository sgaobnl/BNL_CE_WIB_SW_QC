from pathlib import Path
import csv
from typing import Dict, List, Callable, Tuple, Any

from check_row_count import check_row_count
from check_sn_row5 import check_serial_number
from check_row20 import check_row20
from check_row21 import check_row21
from check_row22 import check_row22


CheckFunction = Callable[
    [List[List[str]], str],
    Tuple[bool, Dict[str, Any]]
]


class CSVAnalyzer:
    """
    Analyzer for RT and LN CSV files.

    Each check:
        - returns PASS/FAIL
        - returns a failure cause
        - may return parsed values for internal use

    All checks run even if an earlier check fails.

    The CSV output contains only two cells per check:
        Check_N_Result
        Check_N_Fail_Code

    Parsed values are kept separately in self.parsed_data.
    """

    CHECKS = [
        ("Check_row_cnt", check_row_count),
        ("Check_row5", check_serial_number),
        ("Check_row20", check_row20),
        ("Check_row21", check_row21),
        ("Check_row22", check_row22),

        # Future checks:
        # from check_row22 import check_row22
        # ("Check_5", check_row22),
    ]

    def __init__(self, csv_file: Path):
        self.csv_file = Path(csv_file)
        self.rows: List[List[str]] = []

        # Data exported to the result CSV
        self.result: Dict[str, Any] = {
            "File": self.csv_file.name,
            "File_Path": str(self.csv_file),
            "File_Type": self._get_file_type(),
            "Overall_Result": "FAIL",
            "Fail_Code": "",
        }

        # Parsed values kept internally and NOT exported
        self.parsed_data: Dict[str, Any] = {}

    # ==================================================
    # Main analysis
    # ==================================================

    def analyze(self) -> Dict[str, Any]:
        """
        Read file and run ALL checks.

        A failed check never stops later checks.
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
                fail_code = check_result.get(
                    "fail_code",
                    f"{check_name} failed",
                )

                if fail_code:
                    failed_checks.append(fail_code)

        # ----------------------------------------------
        # Overall result is decided after ALL checks
        # ----------------------------------------------

        if failed_checks:
            self.result["Overall_Result"] = "FAIL"
            self.result["Fail_Code"] = " | ".join(
                failed_checks
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

                self.rows = list(
                    csv.reader(f)
                )

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
    # Store result from one check
    # ==================================================

    def _store_check_result(
        self,
        check_name: str,
        passed: bool,
        check_result: Dict[str, Any],
    ) -> None:
        """
        Store exactly two report fields for each check:

            Check_N_Result
            Check_N_Fail_Code

        Any other fields returned by the check are stored
        in self.parsed_data for internal use.
        """

        # ----------------------------------------------
        # Report fields
        # ----------------------------------------------

        self.result[
            f"{check_name}_Result"
        ] = "PASS" if passed else "FAIL"

        self.result[
            f"{check_name}_Fail_Code"
        ] = check_result.get(
            "fail_code",
            "",
        )

        # ----------------------------------------------
        # Internal parsed data
        # ----------------------------------------------

        for key, value in check_result.items():

            if key == "fail_code":
                continue

            self.parsed_data[
                f"{check_name}_{key}"
            ] = value

    # ==================================================
    # File type
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
    Export only the acceptance result fields.
    """

    FIELDNAMES = [
        "File",
        "File_Path",
        "File_Type",
        "Overall_Result",
        "Fail_Code",

        "Check_row_cnt_Result",
        "Check_row_cnt_Fail_Code",

        "Check_row5_Result",
        "Check_row5_Fail_Code",

        "Check_row20_Result",
        "Check_row20_Fail_Code",

        "Check_row21_Result",
        "Check_row21_Fail_Code",

        "Check_row22_Result",
        "Check_row22_Fail_Code",

    ]

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

        with self.output_file.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as f:

            writer = csv.DictWriter(
                f,
                fieldnames=self.FIELDNAMES,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(results)


def analyze_files(
    input_files: List[Path],
) -> Tuple[
    List[Dict[str, Any]],
    List[CSVAnalyzer],
]:
    """
    Analyze all files and return both:
        1. exportable result dictionaries
        2. analyzer objects containing parsed_data
    """

    results = []
    analyzers = []

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

        results.append(
            analyzer.analyze()
        )

        analyzers.append(analyzer)

    return results, analyzers


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

    results, analyzers = analyze_files(
        input_files
    )

    if not results:
        print("No analysis results.")
        return

    # ==================================================
    # Get parsed serial number
    # ==================================================

    serial_number = None

    for analyzer in analyzers:

        sn = analyzer.parsed_data.get(
            "Check_row5_sn"
        )

        if sn:
            serial_number = sn
            break

    if not serial_number:
        serial_number = "UNKNOWN"

    # ==================================================
    # Output file
    # ==================================================

    output_file = (
        output_dir /
        f"{serial_number}_ana_result.csv"
    )

    # ==================================================
    # Export
    # ==================================================

    exporter = CSVResultExporter(
        output_file
    )

    exporter.export(results)

    print(
        f"Analysis results saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()
