from pathlib import Path
import csv
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
    # Four-channel group outlier check
    # ==================================================

    @staticmethod
    def _group_mean_excluding_two_largest(values):
        """Mean of 10 values after removing the two largest from 12."""
        if len(values) != 12:
            raise ValueError("Expected exactly 12 values.")

        remaining = sorted(values)[:-2]
        return sum(remaining) / len(remaining)

    def check_row_group_criteria(self):
        """Run the RMS four-channel group criterion for Rows 20-22."""
        self.read_file()
        return _check_rms_group_criteria(self.rows, (20, 21, 22))

    # ==================================================
    # Analyze all channels
    # ==================================================

    def analyze(self):
        """
        Analyze CH0 ~ CH15.
        """

        self.read_file()

        results = []

        group_check = self.check_row_group_criteria()
        group_check_30_32_33 = _check_rms_group_criteria(self.rows, (30, 32, 33))

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

                    "Result": "PASS" if group_check["Result"] == "PASS" else "FAIL",
                    "Fail_Code": group_check["Fail_Code"],
                    "Group_Criteria_Result": group_check["Result"],
                    "Group_Criteria_Measure": "RMS",
                    "Rows30_32_33_Group_Criteria_Result": group_check_30_32_33["fail_code"] == "",
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
                    "Fail_Code": str(exc) + (
                        f" | {group_check['Fail_Code']}"
                        if group_check["Fail_Code"]
                        else ""
                    ),
                    "Group_Criteria_Result": group_check["Result"],
                    "Group_Criteria_Measure": "RMS",
                    "Rows30_32_33_Group_Criteria_Result": group_check_30_32_33["fail_code"] == "",
                })

        return results



def _check_rms_group_criteria(rows, row_numbers=(20, 21, 22)):
    """
    RMS four-channel group criterion.

    For each selected row:
      A0 = mean RMS of CH0-CH3
      A1 = mean of the other 12 RMS values after removing the 2 largest
      B0 = mean RMS of CH4-CH7
      B1 = same calculation using channels outside CH4-CH7
      C0 = mean RMS of CH8-CH11
      C1 = same calculation using channels outside CH8-CH11
      D0 = mean RMS of CH12-CH15
      D1 = same calculation using channels outside CH12-CH15

    A row fails only when all four channels in any group are
    greater than 1.5 times that group's reference mean.

    The combined criterion fails only when at least two selected rows fail.
    """
    groups = {
        'A': (range(0, 4), [ch for ch in range(16) if ch not in range(0, 4)]),
        'B': (range(4, 8), [ch for ch in range(16) if ch not in range(4, 8)]),
        'C': (range(8, 12), [ch for ch in range(16) if ch not in range(8, 12)]),
        'D': (range(12, 16), [ch for ch in range(16) if ch not in range(12, 16)]),
    }
    parsed = {}
    row_failures_summary = []
    failed_row_count = 0

    for row_number in row_numbers:
        row_index = row_number - 1
        if len(rows) <= row_index:
            failed_row_count += 1
            msg=f'Row {row_number}: row is missing'
            row_failures_summary.append(msg)
            parsed[f'Row{row_number}_Result']='FAIL'
            parsed[f'Row{row_number}_Fail_Code']='row is missing'
            continue

        row=rows[row_index]
        rms_values={}
        parse_failures=[]
        for ch in range(16):
            m=find_channel_measurements(row,ch)
            if m is None:
                parse_failures.append(f'CH{ch} not found or rms could not be parsed')
            else:
                rms_values[ch]=m['rms']

        if len(rms_values)!=16:
            failed_row_count += 1
            fail_code=' | '.join(parse_failures)
            row_failures_summary.append(f'Row {row_number}: {fail_code}')
            parsed[f'Row{row_number}_Result']='FAIL'
            parsed[f'Row{row_number}_Fail_Code']=fail_code
            continue

        stats={}
        group_failures=[]
        for name,(group_channels,reference_channels) in groups.items():
            group_values=[rms_values[ch] for ch in group_channels]
            reference_values=[rms_values[ch] for ch in reference_channels]
            group_mean=sum(group_values)/4.0
            reference_mean=sum(sorted(reference_values)[:-2])/10.0
            limit=1.5*reference_mean
            exceeding=[ch for ch in group_channels if rms_values[ch]>limit]
            group_failed=(len(exceeding)==4)
            stats[f'{name}0']=group_mean
            stats[f'{name}1']=reference_mean
            stats[f'{name}_Limit']=limit
            stats[f'{name}_Result']='FAIL' if group_failed else 'PASS'
            if group_failed:
                details=', '.join(f'CH{ch}={rms_values[ch]}' for ch in group_channels)
                group_failures.append(f'Group {name}: all 4 channels ({details}) > 1.5*{name}1={limit:.6g}')

        row_failed=bool(group_failures)
        if row_failed:
            failed_row_count += 1
            fail_code=' | '.join(group_failures)
            row_failures_summary.append(f'Row {row_number}: {fail_code}')
        else:
            fail_code=''
        parsed[f'Row{row_number}_Result']='FAIL' if row_failed else 'PASS'
        parsed[f'Row{row_number}_Fail_Code']=fail_code
        parsed[f'Row{row_number}_Group_Criteria']=stats

    parsed['Failed_Row_Count']=failed_row_count
    if failed_row_count >= 2:
        return False, {'fail_code': f'FAIL: {failed_row_count} of selected rows failed; at least 2 failed rows trigger combined failure. ' + ' | '.join(row_failures_summary), **parsed}
    return True, {'fail_code':'', **parsed}


def check_row20_21_22_group(rows, file_type):
    """Public Rows 20-22 RMS group checker.

    A group fails only when all 4 channels exceed 1.5 times its
    reference RMS mean. The combined check fails only when at least
    2 of Rows 20, 21, and 22 fail.
    """
    if file_type not in ("RT", "LN"):
        return False, {
            "fail_code": f"FAIL: unsupported file type: {file_type}"
        }
    return _check_rms_group_criteria(rows, (20, 21, 22))


def check_rows30_32_33_group(rows, file_type):
    """Apply the same RMS four-channel group criterion to Rows 30, 32, 33."""
    if file_type not in ('RT','LN'):
        return False, {'fail_code': f'FAIL: unsupported file type: {file_type}'}
    return _check_rms_group_criteria(rows, (30, 32, 33))



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


CHECK_FUNCTIONS = {
    "check_row20_21_22_group": check_row20_21_22_group,
    "check_rows30_32_33_group": check_rows30_32_33_group,
    "GainLinearityAnalyzer": GainLinearityAnalyzer,
}


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
