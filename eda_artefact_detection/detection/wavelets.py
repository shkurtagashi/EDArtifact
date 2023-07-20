import numpy as np
from scipy.stats import linregress


def compute_statistical_wavelet(df, window_size=5, sampling_rate=4):
    """
    This function computes the statistical and wavelets features for each preprocessed component of the EDA signal.
    The features are calculated over the 5 second non-overlapping segments.

    INPUT:
        df: requires a dataframe with columns named:
        'EDA', 'EDA_Phasic', 'Time', 'Wavelet1', 'Wavelet2', 'Wavelet3'

    OUTPUT:
        df: returns the same dataframe with the following features calculated for each column defined in columns variable:
            median:        median value of the 5 second windo
            mean:          average value
            std:           standard deviation
            var:           variance of the signal
            slope:         slope of the signal
            min:           minimum value
            max:           maximum value
            fdmean:        mean of the first derivative
            fdstd:         standard deviation of the first derivative
            sdmean:        mean of the second derivative
            sdstd:         standard deviation of the second derivative
            drange:        dynamic range
    """

    columns = ["EDA", "EDA_Phasic", "Wavelet1", "Wavelet2", "Wavelet3"]
    window_size = window_size * sampling_rate

    for col in columns:
        data = df[col]
        name = col
        time = range(1, window_size+1)

        (
            medians,
            means,
            stds,
            variances,
            mins,
            maxs,
            fdmeans,
            sdmeans,
            fdstds,
            sdstds,
            dranges,
            slopes,
        ) = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for i in range(0, len(data)):
            eda = data[i]
            fd = np.gradient(eda)
            fdmeans.append(np.mean(fd))
            sd = np.gradient(fd)
            sdmeans.append(np.mean(sd))
            fdstds.append(np.std(fd))
            sdstds.append(np.std(sd))
            dranges.append(np.max(eda) - np.min(eda))
            medians.append(np.median(eda))
            means.append(np.mean(eda))
            stds.append(np.std(eda))
            variances.append(np.var(eda))
            mins.append(np.min(eda))
            maxs.append(np.max(eda))
            slope, intercept, r_value, p_value, std_err = linregress(time, data[i])
            slopes.append(slope)

        df[name + "_median"] = medians
        df[name + "_mean"] = means
        df[name + "_std"] = stds
        df[name + "_var"] = variances
        df[name + "_slope"] = slopes
        df[name + "_min"] = mins
        df[name + "_max"] = maxs
        df[name + "_fdmean"] = fdmeans
        df[name + "_fdstd"] = fdstds
        df[name + "_sdmean"] = sdmeans
        df[name + "_sdstd"] = sdstds
        df[name + "_drange"] = dranges

    print("3. Statistical and wavelets feature extraction completed")

    return df
