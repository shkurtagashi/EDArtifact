import pandas as pd
from itertools import chain
import pandas as pd


def segment_eda_data(df, window_size: int, sampling_rate: int = 4):
    """
    This function segments the EDA signal into 5 second non-overlapping segments.
    The sampling frequency of our sensor was 4HZ, thereby, the window size for segmenting the data is 20 samples
    5 seconds*4Hz = 20 data samples.

    INPUT:
        df: requires a dataframe with columns named:
        'EDA_Filtered', 'EDA_Phasic', 'Wavelet1', 'Wavelet2', 'Wavelet3', 'Time'

    OUTPUT:
        df: returns a new dataframe with 6 new columnns
        'EDA_Filtered', 'EDA_Phasic', 'Time', 'Wavelet1', 'Wavelet2', 'Wavelet3'
        Each cell in the dataframe contains an array of 20 values.
    """

    window_size = window_size * sampling_rate
    eda = df.EDA_Filtered.values.reshape(-1, window_size)
    eda_phasic = df.EDA_Phasic.values.reshape(-1, window_size)
    time = df.Time.values.reshape(-1, window_size)
    wavelet3 = df.Wavelet3.values.reshape(-1, window_size)
    wavelet2 = df.Wavelet2.values.reshape(-1, window_size)
    wavelet1 = df.Wavelet1.values.reshape(-1, window_size)

    df = pd.DataFrame(
        columns=["EDA", "EDA_Phasic", "Time", "Wavelet3", "Wavelet2", "Wavelet1"]
    )
    df.EDA = pd.Series(list(eda))
    df.EDA_Phasic = pd.Series(list(eda_phasic))
    df.Time = pd.Series(list(time))
    df.Wavelet3 = pd.Series(list(wavelet3))
    df.Wavelet2 = pd.Series(list(wavelet2))
    df.Wavelet1 = pd.Series(list(wavelet1))

    eda_times = chain.from_iterable(zip(*df.Time.values))
    eda_times = list(eda_times)
    eda_times = eda_times[: len(df)]

    df["Time_array"] = pd.Series(list(time))
    df["Time"] = eda_times

    print("2. EDA data segmentation completed")

    return df
