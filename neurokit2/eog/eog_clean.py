# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

from ..misc import as_vector
from ..signal import signal_filter


def eog_clean(eog_signal, sampling_rate=1000, method="agarwal2019"):
    """Clean an EOG signal.

    Prepare a raw EOG signal for eye blinks detection.

    Parameters
    ----------
    eog_signal : list or array or Series
        The raw EOG channel.
    sampling_rate : int
        The sampling frequency of `eog_signal` (in Hz, i.e., samples/second).
        Defaults to 1000.
    method : str
        The processing pipeline to apply. Can be one of 'agarwal2019' (default) or
        'mne' (requires the MNE package to be installed).

    Returns
    -------
    array
        Vector containing the cleaned EOG signal.

    See Also
    --------
    signal_filter, eog_peaks

    Examples
    --------
    Examples
    --------
    >>> import neurokit2 as nk
    >>>
    >>> # Get data
    >>> eog_signal = nk.data('eog_100hz')["vEOG"]
    >>>
    >>> # Clean
    >>> agarwal2019 = nk.eog_clean(eog_signal, sampling_rate=100, method='agarwal2019')
    >>> mne = nk.eog_clean(eog_signal, sampling_rate=100, method='mne')
    >>>
    >>> # Visualize
    >>> fig = pd.DataFrame({"Raw": eog_signal,
    ...                     "agarwal2019": agarwal2019,
    ...                     "MNE": mne}).plot() #doctest: +ELLIPSIS
    <matplotlib.axes._subplots.AxesSubplot at ...>


    References
    ----------
    - Agarwal, M., & Sivakumar, R. (2019). Blink: A Fully Automated Unsupervised Algorithm for
    Eye-Blink Detection in EEG Signals. In 2019 57th Annual Allerton Conference on Communication,
    Control, and Computing (Allerton) (pp. 1113-1121). IEEE.

    """
    # Sanitize input
    eog_signal = as_vector(eog_signal)

    # Apply method
    method = method.lower()
    if method in ["agarwal", "agarwal2019"]:
        clean = _eog_clean_agarwal2019(eog_signal, sampling_rate=sampling_rate)
    elif method in ["mne"]:
        clean = _eog_clean_mne(eog_signal, sampling_rate=sampling_rate)
    else:
        raise ValueError(
            "NeuroKit error: eog_clean(): 'method' should be "
            "one of 'agarwal2019', 'mne'."
        )


    return clean


# =============================================================================
# Methods
# =============================================================================
def _eog_clean_agarwal2019(eog_signal, sampling_rate=1000):
    """garwal, M., & Sivakumar, R. (2019). Blink: A Fully Automated Unsupervised Algorithm for
    Eye-Blink Detection in EEG Signals. In 2019 57th Annual Allerton Conference on Communication,
    Control, and Computing (Allerton) (pp. 1113-1121). IEEE.
    """
    return signal_filter(
        eog_signal, sampling_rate=sampling_rate, method="butterworth", order=4, lowcut=None, highcut=10
    )


def _eog_clean_brainstorm(eog_signal, sampling_rate=1000):
    """EOG cleaning implemented by default in Brainstorm.

    https://neuroimage.usc.edu/brainstorm/Tutorials/TutRawSsp
    """
    return signal_filter(
        eog_signal, sampling_rate=sampling_rate, method="butterworth", order=4, lowcut=1.5, highcut=15
    )



def _eog_clean_mne(eog_signal, sampling_rate=1000):
    """EOG cleaning implemented by default in MNE.

    https://github.com/mne-tools/mne-python/blob/master/mne/preprocessing/eog.py
    """
    # Make sure MNE is installed
    try:
        import mne
    except ImportError:
        raise ImportError(
            "NeuroKit error: signal_filter(): the 'mne' module is required for this method to run. ",
            "Please install it first (`pip install mne`).",
        )

    # Filter
    clean = mne.filter.filter_data(
        eog_signal,
        sampling_rate,
        l_freq=1,
        h_freq=10,
        filter_length="10s",
        l_trans_bandwidth=0.5,
        h_trans_bandwidth=0.5,
        phase='zero-double',
        fir_window='hann',
        fir_design='firwin2',
        verbose=False)

    return clean
