from pathlib import Path
import csv
import math
from typing import List, Dict


from common import find_channel_measurements


class GainLinearityAnalyzer:
    """
    Analyze gain and linearity for CH0 ~ CH15 using Row 20 ~ Row 22.

    For each channel:
        x = the three input/DAC values supplied by X_VALUES
        y = posAmp from Row 20, Row 21, Row 22

    Linear fit:
        y = Gain * x + Offset

    Acceptance criteria:
        1. Gain:
               Mean_Gain - 3 * STD_Gain
               <= channel Gain <=
               Mean_Gain + 3 * STD_Gain

           The mean and STD are calculated from all 16 channels.

        2. Nonlinearity:
               Nonlinearity_Percent < 0.5%

    Note:
        STD below uses population standard deviation by default
        because all 16 channels are being evaluated.
    """

    ROW_NUMBERS = (20, 21, 22)
    CHANNELS = range(16)

    NONLINEARITY_LIMIT_PERCENT = 0.5
    GAIN_STD_MULTIPLIER = 3.0

    def __init__(
        self,
        csv_file: Path,
        x_values: List[float],
    ):
        self.csv_file = Path(csv_file)

        if len(x_values) != 3:
            raise ValueError(
                "x_values must contain exactly 3 values "
                "for rows 20, 21, and 22."
            )

        self.x_values = [
            float(x) for x in x_values
        ]

        self.rows = []

    # ==================================================
    # Read CSV
    # ==================================================

    def read_file(self) -> None:
        with self.csv_file.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            self.rows = list(csv.reader(f))

    # ==================================================
    # Get row
    # ==================================================

    def get_row(self, row_number: int):
        row_index = row_number - 1

        if len(self.rows) <= row_index:
            raise ValueError(
                f"Row {row_number} does not exist."
            )

        return self.rows[row_index]

    # ==================================================
    # Get posAmp
    # ==================================================

    def get_posamp(
        self,
        row_number: int,
        channel_number: int,
    ) -> float:
        """
        Search the entire row for CHx and return posAmp.
        """

        row = self.get_row(row_number)

        measurement = find_channel_measurements(
            row,
            channel_number,
        )

        if measurement is None:
            raise ValueError(
                f"CH{channel_number} not found or "
                f"measurement could not be parsed "
                f"in row {row_number}."
            )

        return float(measurement["posAmp"])

    # ==================================================
    # Linear fit
    # ==================================================

    @staticmethod
    def linear_fit(
        x_values: List[float],
        y_values: List[float],
    ):
        """
        Least-squares linear fit:

            y = gain * x + offset
        """

        if len(x_values) < 2:
            raise ValueError(
                "At least two points are required."
            )

        x_mean = sum(x_values) / len(x_values)
        y_mean = sum(y_values) / len(y_values)

        numerator = sum(
            (x - x_mean) * (y - y_mean)
            for x, y in zip(x_values, y_values)
        )

        denominator = sum(
            (x - x_mean) ** 2
            for x in x_values
        )

        if denominator == 0:
            raise ValueError(
                "All x values are identical."
            )

        gain = numerator / denominator
        offset = y_mean - gain * x_mean

        return gain, offset

    # ==================================================
    # Non-linearity
    # ==================================================

    @staticmethod
    def calculate_nonlinearity(
        x_values: List[float],
        y_values: List[float],
        gain: float,
        offset: float,
    ):
        """
        Calculate maximum deviation from the fitted line.

        INL (%) is normalized to the fitted full-scale output span.
        """

        fitted_values = [
            gain * x + offset
            for x in x_values
        ]

        residuals = [
            y - fitted
            for y, fitted in zip(
                y_values,
                fitted_values,
            )
        ]

        max_abs_residual = max(
            abs(value)
            for value in residuals
        )

        fitted_span = (
            max(fitted_values)
            - min(fitted_values)
        )

        if fitted_span == 0:
            nonlinearity_percent = math.nan
        else:
            nonlinearity_percent = (
                max_abs_residual
                / fitted_span
                * 100.0
            )

        return (
            fitted_values,
            residuals,
            max_abs_residual,
            nonlinearity_percent,
        )

    # ==================================================
    # Analyze each channel
    # ==================================================

    def analyze_channels(self) -> List[Dict]:
        """
        Calculate gain and linearity for CH0 ~ CH15.

        Acceptance checks are applied after all channel fits
        have been calculated.
        """

        self.read_file()

        results = []

        for channel in self.CHANNELS:

            try:
                y_values = [
                    self.get_posamp(
                        row_number,
                        channel,
                    )
                    for row_number in self.ROW_NUMBERS
                ]

                gain, offset = self.linear_fit(
                    self.x_values,
                    y_values,
                )

                (
                    fitted_values,
                    residuals,
                    max_abs_residual,
                    nonlinearity_percent,
                ) = self.calculate_nonlinearity(
                    self.x_values,
                    y_values,
                    gain,
                    offset,
                )

                results.append({
                    "Channel": f"CH{channel}",

                    "X_Row20": self.x_values[0],
                    "X_Row21": self.x_values[1],
                    "X_Row22": self.x_values[2],

                    "posAmp_Row20": y_values[0],
                    "posAmp_Row21": y_values[1],
                    "posAmp_Row22": y_values[2],

                    "Gain": gain,
                    "Offset": offset,

                    "Fit_Row20": fitted_values[0],
                    "Fit_Row21": fitted_values[1],
                    "Fit_Row22": fitted_values[2],

                    "Residual_Row20": residuals[0],
                    "Residual_Row21": residuals[1],
                    "Residual_Row22": residuals[2],

                    "Max_Abs_Residual": max_abs_residual,
                    "Nonlinearity_Percent": nonlinearity_percent,

                    "Gain_Result": "",
                    "Nonlinearity_Result": "",
                    "Overall_Result": "",
                    "Fail_Code": "",
                })

            except Exception as exc:

                results.append({
                    "Channel": f"CH{channel}",

                    "X_Row20": self.x_values[0],
                    "X_Row21": self.x_values[1],
                    "X_Row22": self.x_values[2],

                    "posAmp_Row20": "",
                    "posAmp_Row21": "",
                    "posAmp_Row22": "",

                    "Gain": "",
                    "Offset": "",

                    "Fit_Row20": "",
                    "Fit_Row21": "",
                    "Fit_Row22": "",

                    "Residual_Row20": "",
                    "Residual_Row21": "",
                    "Residual_Row22": "",

                    "Max_Abs_Residual": "",
                    "Nonlinearity_Percent": "",

                    "Gain_Result": "FAIL",
                    "Nonlinearity_Result": "FAIL",
                    "Overall_Result": "FAIL",
                    "Fail_Code": str(exc),
                })

        return results

    # ==================================================
    # Gain acceptance
    # ==================================================

    def apply_acceptance_criteria(
        self,
        results: List[Dict],
    ) -> List[Dict]:
        """
        Apply acceptance criteria after all 16 channels
        have been analyzed.

        Gain criterion:
            mean - 3*STD <= Gain <= mean + 3*STD

        Nonlinearity criterion:
            Nonlinearity_Percent < 0.1
        """

        valid_gains = [
            row["Gain"]
            for row in results
            if isinstance(row.get("Gain"), (int, float))
            and math.isfinite(row["Gain"])
        ]

        # --------------------------------------------------
        # Need all 16 channels for gain statistics.
        # --------------------------------------------------

        if len(valid_gains) != 16:
            gain_mean = math.nan
            gain_std = math.nan
            gain_lower = math.nan
            gain_upper = math.nan
        else:
            gain_mean = (
                sum(valid_gains)
                / len(valid_gains)
            )

            # Population STD of all 16 channels.
            gain_std = math.sqrt(
                sum(
                    (gain - gain_mean) ** 2
                    for gain in valid_gains
                )
                / len(valid_gains)
            )

            gain_lower = (
                gain_mean
                - self.GAIN_STD_MULTIPLIER * gain_std
            )

            gain_upper = (
                gain_mean
                + self.GAIN_STD_MULTIPLIER * gain_std
            )

        # --------------------------------------------------
        # Apply criteria to every channel.
        # --------------------------------------------------

        for row in results:

            gain = row.get("Gain")
            nonlinearity = row.get(
                "Nonlinearity_Percent"
            )

            # Gain acceptance
            if (
                isinstance(gain, (int, float))
                and math.isfinite(gain)
                and math.isfinite(gain_lower)
                and gain_lower <= gain <= gain_upper
            ):
                row["Gain_Result"] = "PASS"

            else:
                row["Gain_Result"] = "FAIL"

                if row.get("Fail_Code"):
                    row["Fail_Code"] += " | "

                if not math.isfinite(gain_mean):
                    row["Fail_Code"] += (
                        "FAIL: gain statistics unavailable; "
                        "all 16 channel gains are required"
                    )
                else:
                    row["Fail_Code"] += (
                        f"FAIL: Gain out of 3STD range "
                        f"({gain_lower:.6g} ~ {gain_upper:.6g}): "
                        f"{gain}"
                    )

            # Nonlinearity acceptance
            if (
                isinstance(nonlinearity, (int, float))
                and math.isfinite(nonlinearity)
                and nonlinearity
                < self.NONLINEARITY_LIMIT_PERCENT
            ):
                row["Nonlinearity_Result"] = "PASS"

            else:
                row["Nonlinearity_Result"] = "FAIL"

                if row.get("Fail_Code"):
                    row["Fail_Code"] += " | "

                if isinstance(nonlinearity, (int, float)):
                    row["Fail_Code"] += (
                        f"FAIL: Nonlinearity >= "
                        f"{self.NONLINEARITY_LIMIT_PERCENT}%: "
                        f"{nonlinearity}"
                    )
                else:
                    row["Fail_Code"] += (
                        "FAIL: Nonlinearity cannot be calculated"
                    )

            # Overall channel result
            if (
                row["Gain_Result"] == "PASS"
                and row["Nonlinearity_Result"] == "PASS"
            ):
                row["Overall_Result"] = "PASS"
            else:
                row["Overall_Result"] = "FAIL"

            # Add group gain statistics.
            row["Gain_Mean_16CH"] = gain_mean
            row["Gain_STD_16CH"] = gain_std
            row["Gain_Lower_3STD"] = gain_lower
            row["Gain_Upper_3STD"] = gain_upper

        return results

    # ==================================================
    # Full analysis
    # ==================================================

    def analyze(self) -> List[Dict]:
        """
        Run channel analysis followed by acceptance criteria.
        """

        results = self.analyze_channels()

        results = self.apply_acceptance_criteria(
            results
        )

        return results


def export_results(
    results: List[Dict],
    output_file: Path,
) -> None:
    """
    Export results to CSV.
    """

    if not results:
        return

    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = list(results[0].keys())

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


# ======================================================
# Main
# ======================================================

if __name__ == "__main__":

    CSV_FILE = Path(
        r"S:\RTS_DAT_LArASIC_QC\B006T0001\results\006_01186_20251006165356_Tray59_SKT3_LN.csv"
    )

    OUTPUT_FILE = Path(
        r"S:\RTS_DAT_LArASIC_QC\Acceptance\gain_linearity_ln.csv"
    )

    # Replace these with the actual input/DAC values
    # represented by Row 20, Row 21, and Row 22.
    X_VALUES = [
        4.7*32*0.185,
        4.7*16*0.185,
        4.7*24*0.185,
    ]

    analyzer = GainLinearityAnalyzer(
        CSV_FILE,
        X_VALUES,
    )

    results = analyzer.analyze()

    export_results(
        results,
        OUTPUT_FILE,
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )
