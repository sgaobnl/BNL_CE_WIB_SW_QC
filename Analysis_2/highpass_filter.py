# -*- coding: utf-8 -*-
"""
File Name: init_femb.py
Optimized high-pass / band-stop filter utilities.

Optimization notes:
- hp_flt_applied() no longer calculates an unused 1,000,000-point
  frequency response on every call.
- Butterworth coefficients are cached by (fs, passfreq, order).
- The public function signatures are preserved.
- scipy.signal.filtfilt is retained because it is faster than
  sosfiltfilt for the 2,000-20,000 point arrays targeted here.
"""

from functools import lru_cache

import numpy as np
from scipy import signal


# Cache is useful when many channels/traces use the same filter settings.
@lru_cache(maxsize=32)
def _butter_hp_coefficients(fs=2000000, passfreq=500, flt_order=3):
    """Return cached Butterworth high-pass coefficients."""
    nyquist_rate = fs / 2.0
    wn = passfreq / nyquist_rate
    return signal.butter(
        N=flt_order,
        Wn=wn,
        btype="highpass",
    )


def hp_FIR_applied(
    pre_flt_data,
    fs=2000000,
    flt_stopfreq=300,
    flt_passfreq=600,
    flt_order=1,
):
    """Apply the original FIR high-pass filter."""
    nyquist_rate = fs / 2.0
    desired = (0, 0, 1, 1)
    bands = (0, flt_stopfreq, flt_passfreq, nyquist_rate)

    flt_coefs = signal.firls(
        flt_order,
        bands,
        desired,
        nyq=nyquist_rate,
    )

    return signal.filtfilt(
        flt_coefs,
        [1],
        pre_flt_data,
    )


def butter_hp_flt(fs=2000000, passfreq=500, flt_order=3):
    """Return cached Butterworth high-pass coefficients."""
    return _butter_hp_coefficients(
        fs,
        passfreq,
        flt_order,
    )


def butter_bandstop_flt(
    fs=2000000,
    stopfreq=300,
    passfreq=600,
    flt_order=2,
):
    """Return Butterworth band-stop coefficients."""
    nyquist_rate = fs / 2.0
    wn = [
        stopfreq / nyquist_rate,
        passfreq / nyquist_rate,
    ]
    return signal.butter(
        N=flt_order,
        Wn=wn,
        btype="bandstop",
    )


def hp_flt_applied(
    smp_data,
    fs=2000000,
    passfreq=500,
    flt_order=3,
):
    """
    Apply the Butterworth high-pass filter.

    The original implementation did this on every call:
        signal.freqz(b, a, worN=int(fs/2))

    With fs=2 MHz that creates a 1,000,000-point frequency response,
    but the result is never used. Removing it is the main speedup.

    np.asarray(..., dtype=float) avoids repeated conversion work when
    callers provide Python lists while leaving NumPy arrays efficient.
    """
    b, a = _butter_hp_coefficients(
        fs,
        passfreq,
        flt_order,
    )

    data = np.asarray(smp_data, dtype=float)

    return signal.filtfilt(
        b,
        a,
        data,
    )


if __name__ == "__main__":
    # Example:
    # chndata_hf = hp_flt_applied(
    #     chndata,
    #     fs=1953125,
    #     passfreq=10000,
    # )
    pass
