from scipy import signal
from scipy.signal import butter
import numpy as np
import cvxEDA
import pywt

"""Filter EDA data """


def butter_lowpass(cutoff, fs, order):
    nyq = 0.5 * fs
    # Normalization of the cutoff signal
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    return b, a


""" Apply the filter designed before """


def butter_lowpass_filter_filtfilt(data, cutoff, fs, order):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y


""" Decompose EDA data"""


def decomposition(eda, Fs=4) -> dict:
    y = np.array((eda))
    yn = (y - y.mean()) / y.std()
    [r, p, t, l, d, e, obj] = cvxEDA.cvxEDA(yn, 1.0 / Fs)
    return (np.array(a).ravel() for a in (r, p, t, l, d, e, obj))


def preprocess_eda_signals(df):
    """
    This function preprocesses the EDA data.

    INPUT:
        df: requires a dataframe with a column named 'EDA'

    OUTPUT:
        DF: returns the same dataframe with 6 new columnns
        'EDA_Filtered', 'EDA_Phasic', 'EDA_Tonic', 'Wavelet1', 'Wavelet2', 'Wavelet3'
    """

    df["EDA_Filtered"] = butter_lowpass_filter_filtfilt(
        data=df["EDA"], cutoff=0.6, fs=4, order=1
    )
    decomposition_results = cvxEDA.cvxEDA(df["EDA_Filtered"], 4)
    df["EDA_Phasic"] = decomposition_results["phasic component"]
    df["EDA_Tonic"] = decomposition_results["tonic component"]

    _, dtw3, dtw2, dtw1 = pywt.wavedec(df["EDA_Filtered"], "Haar", level=3)
    dtw3_duplicates = list(np.repeat(dtw3, 8))
    dtw2_duplicates = list(np.repeat(dtw2, 4))
    dtw1_duplicates = list(np.repeat(dtw1, 2))

    df["Wavelet3"] = dtw3_duplicates[: len(df)]
    df["Wavelet2"] = dtw2_duplicates[: len(df)]
    df["Wavelet1"] = dtw1_duplicates[: len(df)]

    print("1. EDA data preprocessing completed")

    return df
