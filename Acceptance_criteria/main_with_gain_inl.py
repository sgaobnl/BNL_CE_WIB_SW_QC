from pathlib import Path
import csv
from typing import Dict, List, Callable, Tuple, Any

from check_row_count import check_row_count
from check_sn_row5 import check_serial_number
from check_row20 import check_row20
from check_row21 import check_row21
from check_row22 import check_row22
from check_row26 import check_row26

from check_row28 import check_row28
from check_row29 import check_row29
from check_row30 import check_row30
from check_row31 import check_row31
from check_row32 import check_row32
from check_row33 import check_row33

from gain_linearity_with_acceptance import (
    GainLinearityAnalyzer,
)


CheckFunction = Callable[
    [List[List[str]], str],
    Tuple[bool, Dict[str, Any]]
]


class CSVAnalyzer:
    """
    Analyzer for RT and LN CSV files.

    Normal acceptance checks:
        Check_row_cnt
        Check_row5
        Check_row20
        Check_row21
        Check_row22

    In addition, GainLinearityAnalyzer is run on Row 20 ~ Row 22.

    Every check runs even if an earlier check fails.

    The result CSV contains two cells for each acceptance check:
        <Check>_Result
        <Check>_Fail_Code

    Parsed values are retained in self.parsed_data.
    """

    CHECKS = [
        ("Check_row_cnt", check_row_count),
        ("Check_row5", check_serial_number),
        ("Check_row20", check_row20),
        ("Check_row21", check_row21),
        ("Check_row22", check_row22),
        ("Check_row26", check_row26),

        ("check_row28",  check_row28),
        ("check_row29",  check_row29),
        ("check_row30",  check_row30),
        ("check_row31",  check_row31),
        ("check_row32",  check_row32),
        ("check_row33",  check_row33),

        # Future checks:
        # ("Check_row23", check_row23),
    ]

    # --------------------------------------------------
    # Gain / INL input values corresponding to:
    # Row 20, Row 21, Row 22
    # --------------------------------------------------

    GAIN_INL_X_VALUES = [
        4.7 * 32 * 0.185,
        4.7 * 16 * 0.185,
        4.7 * 24 * 0.185,
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

            "check_row20_21_22_gain_INL_result": "FAIL",
            "check_row20_21_22_gain_INL_Fail_Code": "",
        }

        # Parsed values are retained here and are NOT exported
        # unless explicitly added to CSV fields.
        self.parsed_data: Dict[str, Any] = {}

    # ==================================================
    # Main analysis
    # ==================================================

    def analyze(self) -> Dict[str, Any]:
        """
        Read file and run all acceptance checks.

        A failed check never stops later checks.
        """

        if not self._read_file():
            return self.result

        failed_checks = []

        # --------------------------------------------------
        # Normal acceptance checks
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Gain / INL acceptance check
        #
        # This is independent from the normal checks and
        # therefore still runs when Row 20/21/22 checks fail.
        # --------------------------------------------------

        gain_inl_passed, gain_inl_result = (
            self._check_gain_linearity()
        )

        self.result[
            "check_row20_21_22_gain_INL_result"
        ] = "PASS" if gain_inl_passed else "FAIL"

        self.result[
            "check_row20_21_22_gain_INL_Fail_Code"
        ] = gain_inl_result.get(
            "fail_code",
            "",
        )

        if not gain_inl_passed:
            fail_code = gain_inl_result.get(
                "fail_code",
                "FAIL: gain/INL check failed",
            )

            if fail_code:
                failed_checks.append(fail_code)

        # --------------------------------------------------
        # Overall result
        # --------------------------------------------------

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

            self.result[
                "check_row20_21_22_gain_INL_result"
            ] = "FAIL"

            self.result[
                "check_row20_21_22_gain_INL_Fail_Code"
            ] = (
                "FAIL: cannot read file; "
                "gain/INL analysis was not performed"
            )

            return False

    # ==================================================
    # Run one normal check
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
    # Store normal check result
    # ==================================================

    def _store_check_result(
        self,
        check_name: str,
        passed: bool,
        check_result: Dict[str, Any],
    ) -> None:
        """
        Store exactly two CSV fields for the check.

        Any other returned values are retained in parsed_data.
        """

        self.result[
            f"{check_name}_Result"
        ] = "PASS" if passed else "FAIL"

        self.result[
            f"{check_name}_Fail_Code"
        ] = check_result.get(
            "fail_code",
            "",
        )

        for key, value in check_result.items():

            if key == "fail_code":
                continue

            self.parsed_data[
                f"{check_name}_{key}"
            ] = value

    # ==================================================
    # Gain / INL analysis
    # ==================================================

    def _check_gain_linearity(
        self,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Run GainLinearityAnalyzer for this CSV file.

        Overall PASS requires all 16 channels to pass:
            1. Gain acceptance
            2. Nonlinearity acceptance

        If any channel fails, the fail code lists every
        failed channel and its failure reason.
        """

        try:
            analyzer = GainLinearityAnalyzer(
                self.csv_file,
                self.GAIN_INL_X_VALUES,
            )

            channel_results = analyzer.analyze()

        except Exception as exc:

            return False, {
                "fail_code": (
                    "FAIL: gain/INL analyzer exception - "
                    f"{exc}"
                )
            }

        # Save detailed channel results internally.
        self.parsed_data[
            "Gain_INL_Channel_Results"
        ] = channel_results

        # --------------------------------------------------
        # Require all 16 channels.
        # --------------------------------------------------

        if len(channel_results) != 16:

            return False, {
                "fail_code": (
                    "FAIL: gain/INL analysis did not "
                    "produce all 16 channels"
                )
            }

        failed_channels = []

        for channel_result in channel_results:

            channel = channel_result.get(
                "Channel",
                "UNKNOWN",
            )

            if channel_result.get(
                "Overall_Result"
            ) != "PASS":

                channel_failures = []

                gain_result = channel_result.get(
                    "Gain_Result"
                )

                if gain_result != "PASS":
                    channel_failures.append(
                        self._clean_gain_failure_code(
                            channel_result.get(
                                "Fail_Code",
                                "",
                            )
                        )
                    )

                nonlinearity_result = (
                    channel_result.get(
                        "Nonlinearity_Result"
                    )
                )

                # The original Fail_Code may already include
                # both gain and nonlinearity failures.
                # Keep all information for a failed channel.
                if nonlinearity_result != "PASS":
                    nonlinearity_value = (
                        channel_result.get(
                            "Nonlinearity_Percent"
                        )
                    )

                    if (
                        isinstance(
                            nonlinearity_value,
                            (int, float),
                        )
                    ):
                        channel_failures.append(
                            (
                                "Nonlinearity_Percent="
                                f"{nonlinearity_value:.6g}"
                                " >= 0.5%"
                            )
                        )
                    else:
                        channel_failures.append(
                            "Nonlinearity_Percent unavailable"
                        )

                # Avoid empty/duplicate text.
                channel_failures = [
                    text
                    for text in channel_failures
                    if text
                ]

                if channel_failures:
                    failed_channels.append(
                        f"{channel}: "
                        + "; ".join(
                            self._unique_strings(
                                channel_failures
                            )
                        )
                    )
                else:
                    failed_channels.append(
                        f"{channel}: channel acceptance failed"
                    )

        if failed_channels:

            return False, {
                "fail_code": (
                    "FAIL: gain/INL failed - "
                    + " | ".join(failed_channels)
                )
            }

        return True, {
            "fail_code": "",
        }

    # ==================================================
    # Utility for gain failure text
    # ==================================================

    @staticmethod
    def _clean_gain_failure_code(
        fail_code: str,
    ) -> str:
        """
        Extract the useful gain-related part from the
        GainLinearityAnalyzer fail code.
        """

        if not fail_code:
            return ""

        parts = [
            part.strip()
            for part in fail_code.split("|")
            if part.strip()
        ]

        gain_parts = [
            part
            for part in parts
            if (
                "Gain out of 3STD range" in part
                or "gain statistics unavailable" in part.lower()
            )
        ]

        if gain_parts:
            return gain_parts[0]

        return ""

    @staticmethod
    def _unique_strings(
        values: List[str],
    ) -> List[str]:

        result = []

        for value in values:
            if value and value not in result:
                result.append(value)

        return result

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
    Export the acceptance results.

    Each check occupies exactly two cells:
        <Check>_Result
        <Check>_Fail_Code
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

        "check_row20_21_22_gain_INL_result",
        "check_row20_21_22_gain_INL_Fail_Code",
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
    Analyze all supplied files.
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

                "check_row20_21_22_gain_INL_result": "FAIL",
                "check_row20_21_22_gain_INL_Fail_Code": (
                    "FAIL: file does not exist"
                ),
            })

            continue

        analyzer = CSVAnalyzer(
            csv_file
        )

        results.append(
            analyzer.analyze()
        )

        analyzers.append(
            analyzer
        )

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
    # Get serial number from Check 2 parsed data
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
    # Output filename
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

    exporter.export(
        results
    )

    print(
        f"Analysis results saved to: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()
