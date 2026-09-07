from pathlib import Path
import csv
from typing import Dict, List, Callable, Tuple, Any

from check_row_count import check_row_count
from check_sn_row5 import check_serial_number
from check_row20 import check_row20
from check_row21 import check_row21


CheckFunction = Callable[[List[List[str]]], Tuple[bool, Dict[str, Any]]]


class CSVAnalyzer:
    """
    Common analyzer for RT and LN CSV files.

    The analyzer itself is only responsible for:
        1. Reading the CSV file
        2. Running the configured checks
        3. Collecting results

    New checks can be added to CHECKS without changing the
    main analysis flow.
    """

    CHECKS = [
        ("Check_1", check_row_count),
        ("Check_2", check_serial_number),
        ("Check_3", check_row20),
        ("Check_4", check_row21),

        # --------------------------------------------------
        # Add future checks here:
        #
        # ("Check_5", check_row22),
        # ("Check_6", check_row23),
        # --------------------------------------------------
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
        Read the file and run checks in order.

        The first failed check stops the analysis.
        """

        if not self._read_file():
            return self.result

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
                self.result["Overall_Result"] = "FAIL"
                self.result["Fail_Code"] = (
                    check_result.get("fail_code", "")
                )
                return self.result

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
        Run one check.

        check_name is kept as an argument so debugging/logging
        can be added later without changing the check functions.
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
    # Store check results
    # ==================================================

    def _store_check_result(
        self,
        check_name: str,
        passed: bool,
        check_result: Dict[str, Any],
    ) -> None:
        """
        Store each check result in the output dictionary.

        Example:
            Check_1_Result = PASS
            Check_2_Result = FAIL
            Check_2_Fail_Code = ...

        Any extra fields returned by a check are also stored.
        """

        self.result[f"{check_name}_Result"] = (
            "PASS" if passed else "FAIL"
        )

        fail_code = check_result.get("fail_code", "")

        if fail_code:
            self.result[f"{check_name}_Fail_Code"] = fail_code

        for key, value in check_result.items():

            if key == "fail_code":
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

    def export(self, results: List[Dict[str, Any]]) -> None:
        """
        Export results using the union of all result keys.
        This means new checks can add new fields without
        requiring changes to FIELDNAMES.
        """

        if not results:
            return

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Preserve a sensible order for the first columns,
        # then append any additional check-specific columns.
        preferred_columns = [
            "File",
            "File_Path",
            "File_Type",
            "Overall_Result",
            "Fail_Code",
        ]

        all_columns = []

        for column in preferred_columns:
            if any(column in result for result in results):
                all_columns.append(column)

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
    Analyze a list of RT/LN CSV files.
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
    # Get serial number
    #
    # Check 2 returns:
    #     Check_2_sn = 006_01042
    # ==================================================

    serial_number = None

    for result in results:

        sn = result.get("Check_2_sn")

        if sn:
            serial_number = sn
            break

    if not serial_number:
        print("Cannot determine serial number.")
        return

    # ==================================================
    # Generate output filename
    #
    # Example:
    #     006_01042_ana_result.csv
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
