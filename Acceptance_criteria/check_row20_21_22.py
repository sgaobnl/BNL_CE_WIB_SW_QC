from pathlib import Path
import csv
import re
import math

from common import find_channel_measurements


class GainLinearityAnalyzer:
    """
    Analyze posAmp gain and non-linearity using Row 20 ~ Row 22.

    For each CH0 ~ CH15:
        x = input/DAC values for Row 20, 21, 22
        y = posAmp values extracted from those rows

    Linear fit:
        y = gain * x + offset

    Non-linearity:
        maximum absolute deviation from the fitted line,
        expressed as % of the full-scale fitted span.
    """

    ROW_NUMBERS = (20, 21, 22)
    CHANNELS = range(16)

    def __init__(
        self,
        csv_file: Path,
        x_values,
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

    def read_file(self):
        with self.csv_file.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            self.rows = list(csv.reader(f))

    # ==================================================
    # Get row
    # ==================================================

    def get_row(self, row_number):
        index = row_number - 1

        if len(self.rows) <= index:
            raise ValueError(
                f"Row {row_number} does not exist."
            )

        return self.rows[index]

    # ==================================================
    # Get posAmp
    # ==================================================

    def get_posamp(self, row_number, channel_number):
        """
        Search the entire row for CHx and return its posAmp.
        """

        row = self.get_row(row_number)

        measurement = find_channel_measurements(
            row,
            channel_number,
        )

        if measurement is None:
            raise ValueError(
                f"CH{channel_number} not found or "
                f"posAmp could not be parsed "
                f"in row {row_number}."
            )

        return measurement["posAmp"]

    # ==================================================
    # Linear fit
    # ==================================================

    @staticmethod
    def linear_fit(x_values, y_values):
        """
        Least-squares linear fit:

            y = gain * x + offset

        Returns:
            gain, offset
        """

        n = len(x_values)

        if n < 2:
            raise ValueError(
                "At least two points are required."
            )

        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

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

        offset = (
            y_mean
            - gain * x_mean
        )

        return gain, offset

    # ==================================================
    # Non-linearity
    # ==================================================

    @staticmethod
    def calculate_nonlinearity(
        x_values,
        y_values,
        gain,
        offset,
    ):
        """
        Calculate:
            residual = measured - fitted

        Non-linearity is:
            max(abs(residual)) / full_scale_span * 100 %

        where full_scale_span is the fitted output span
        between the minimum and maximum x values.
        """

        fitted_values = [
            gain * x + offset
            for x in x_values
        ]

        residuals = [
            y - fitted
            for y, fitted
            in zip(y_values, fitted_values)
        ]

        max_abs_residual = max(
            abs(r)
            for r in residuals
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
    # Analyze all channels
    # ==================================================

    def analyze(self):
        """
        Analyze CH0 ~ CH15.
        """

        self.read_file()

        results = []

        for channel in self.CHANNELS:

            try:
                # --------------------------------------
                # Get posAmp from Row 20 ~ Row 22
                # --------------------------------------

                y_values = [
                    self.get_posamp(
                        row_number,
                        channel,
                    )
                    for row_number in self.ROW_NUMBERS
                ]

                # --------------------------------------
                # Linear fit
                # --------------------------------------

                gain, offset = self.linear_fit(
                    self.x_values,
                    y_values,
                )

                # --------------------------------------
                # Non-linearity
                # --------------------------------------

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

                    "Result": "PASS",
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

                    "Result": "FAIL",
                    "Fail_Code": str(exc),
                })

        return results


def export_results(
    results,
    output_file: Path,
):
    """
    Export gain/linearity results to CSV.
    """

    output_file = Path(output_file)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not results:
        return

    fieldnames = list(
        results[0].keys()
    )

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
        r"S:\RTS_DAT_LArASIC_QC\B006T0001\results\006_01186_20251006165356_Tray59_SKT3_RT.csv"
    )

    OUTPUT_FILE = Path(
        r"S:\RTS_DAT_LArASIC_QC\Acceptance\gain_linearity.csv"
    )

    # --------------------------------------------------
    # IMPORTANT:
    #
    # Replace these with the actual input/DAC values
    # corresponding to Row 20, Row 21, Row 22.
    #
    # Example only:
    # --------------------------------------------------

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
