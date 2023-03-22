import pandas as pd
import numpy as np

SAMPLE_RATE = 4


def findPeaks(data, offset, start_WT, end_WT, thres=0, sampleRate=SAMPLE_RATE):
    """
    This function finds the peaks of an EDA signal and returns basic properties.
    Also, peak_end is assumed to be no later than the start of the next peak.

    ********* INPUTS **********
    data:        DataFrame with EDA as one of the columns and indexed by a datetimeIndex
    offset:      the number of rising samples and falling samples after a peak needed to be counted as a peak
    start_WT:    maximum number of seconds before the apex of a peak that is the "start" of the peak
    end_WT:      maximum number of seconds after the apex of a peak that is the "rec.t/2" of the peak, 50% of amp
    thres:       the minimum uS change required to register as a peak, defaults as 0 (i.e. all peaks count)
    sampleRate:  number of samples per second, default=8

    ********* OUTPUTS **********
    peaks:               list of binary, 1 if apex of SCR
    peak_start:          list of binary, 1 if start of SCR
    peak_start_times:    list of strings, if this index is the apex of an SCR, it contains datetime of start of peak
    peak_end:            list of binary, 1 if rec.t/2 of SCR
    peak_end_times:      list of strings, if this index is the apex of an SCR, it contains datetime of rec.t/2
    amplitude:           list of floats,  value of EDA at apex - value of EDA at start
    max_deriv:           list of floats, max derivative within 1 second of apex of SCR
    """

    EDA_deriv = data["EDA_Phasic"][1:].values - data["EDA_Phasic"][:-1].values
    peaks = np.zeros(len(EDA_deriv))
    peak_sign = np.sign(EDA_deriv)
    for i in range(int(offset), int(len(EDA_deriv) - offset)):
        if peak_sign[i] == 1 and peak_sign[i + 1] < 1:
            peaks[i] = 1
            for j in range(1, int(offset)):
                if peak_sign[i - j] < 1 or peak_sign[i + j] > -1:
                    peaks[i] = 0
                    break

    # Finding start of peaks
    peak_start = np.zeros(len(EDA_deriv))
    peak_start_times = [""] * len(data)
    max_deriv = np.zeros(len(data))
    rise_time = np.zeros(len(data))

    for i in range(0, len(peaks)):
        if peaks[i] == 1:
            temp_start = max(0, i - sampleRate)
            max_deriv[i] = max(EDA_deriv[temp_start:i])
            start_deriv = 0.01 * max_deriv[i]

            found = False
            find_start = i
            # has to peak within start_WT seconds
            while found == False and find_start > (i - start_WT * sampleRate):
                if EDA_deriv[find_start] < start_deriv:
                    found = True
                    peak_start[find_start] = 1
                    peak_start_times[i] = data.index[find_start]
                    rise_time[i] = get_seconds_and_microseconds(
                        data.index[i] - pd.to_datetime(peak_start_times[i])
                    )

                find_start = find_start - 1

            # If we didn't find a start
            if found == False:
                peak_start[i - start_WT * sampleRate] = 1
                peak_start_times[i] = data.index[i - start_WT * sampleRate]
                rise_time[i] = start_WT

            # Check if amplitude is too small
            if (
                thres > 0
                and (
                    data["EDA_Phasic"].iloc[i] - data["EDA_Phasic"][peak_start_times[i]]
                )
                < thres
            ):
                peaks[i] = 0
                peak_start[i] = 0
                peak_start_times[i] = ""
                max_deriv[i] = 0
                rise_time[i] = 0

    # Finding the end of the peak, amplitude of peak
    peak_end = np.zeros(len(data))
    peak_end_times = [""] * len(data)
    amplitude = np.zeros(len(data))
    decay_time = np.zeros(len(data))
    half_rise = [""] * len(data)
    SCR_width = np.zeros(len(data))

    for i in range(0, len(peaks)):
        if peaks[i] == 1:
            peak_amp = data["EDA_Phasic"].iloc[i]
            start_amp = data["EDA_Phasic"][peak_start_times[i]]
            amplitude[i] = peak_amp - start_amp

            half_amp = amplitude[i] * 0.5 + start_amp

            found = False
            find_end = i
            # has to decay within end_WT seconds
            while (
                found == False
                and find_end < (i + end_WT * sampleRate)
                and find_end < len(peaks)
            ):
                if data["EDA_Phasic"].iloc[find_end] < half_amp:
                    found = True
                    peak_end[find_end] = 1
                    peak_end_times[i] = data.index[find_end]
                    decay_time[i] = get_seconds_and_microseconds(
                        pd.to_datetime(peak_end_times[i]) - data.index[i]
                    )

                    # Find width
                    find_rise = i
                    found_rise = False
                    while found_rise == False:
                        if data["EDA_Phasic"].iloc[find_rise] < half_amp:
                            found_rise = True
                            half_rise[i] = data.index[find_rise]
                            SCR_width[i] = get_seconds_and_microseconds(
                                pd.to_datetime(peak_end_times[i])
                                - data.index[find_rise]
                            )
                        find_rise = find_rise - 1

                elif peak_start[find_end] == 1:
                    found = True
                    peak_end[find_end] = 1
                    peak_end_times[i] = data.index[find_end]
                find_end = find_end + 1

            # If we didn't find an end
            if found == False:
                min_index = np.argmin(
                    data["EDA_Phasic"].iloc[i : (i + end_WT * sampleRate)].tolist()
                )
                peak_end[i + min_index] = 1
                peak_end_times[i] = data.index[i + min_index]

    peaks = np.concatenate((peaks, np.array([0])))
    peak_start = np.concatenate((peak_start, np.array([0])))
    max_deriv = (
        max_deriv * sampleRate
    )  # now in change in amplitude over change in time form (uS/second)

    return (
        peaks,
        peak_start,
        peak_start_times,
        peak_end,
        peak_end_times,
        amplitude,
        max_deriv,
        rise_time,
        decay_time,
        SCR_width,
        half_rise,
    )


def get_seconds_and_microseconds(pandas_time):
    return pandas_time.seconds + pandas_time.microseconds * 1e-6


def compute_peaks_features(df, window_size: int, sampling_rate: int = 4):
    """
    This function computes the peaks features for each 5 second window in the EDA signal.

    INPUT:
        df:              requires a dataframe with columns 'EDA_Phasic' and 'Time'

    OUTPUT:
        df:              returns the same dataframe with new columnns that contain the following features:
        peaks_p:         number of peaks
        rise_time_p:     average rise time of the peaks
        max_deriv_p:     average value of the maximum derivative
        amp_p:           average amplitute of the peaks
        decay_time_p:    average decay time of the peaks
        SCR_width_p:     average width of the peak (SCR)
        auc_p:           average area under the peak
    """

    thresh = 0.01
    offset = 1
    start_WT = 3
    end_WT = 10
    window_size = window_size * sampling_rate

    data = df.EDA
    times = df.Time

    peaks, rise_times, max_derivs, amps, decay_times, SCR_widths, aucs = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

    for i in range(0, len(data)):
        data_df = pd.DataFrame(columns=["EDA_Phasic", "Time"])
        data_df.EDA_Phasic = pd.Series(list(data[i]))
        data_df.Time = pd.date_range(start=times[i], periods=window_size, freq="250ms")
        data_df.set_index(pd.DatetimeIndex(data_df["Time"]), inplace=True)

        returnedPeakData = findPeaks(
            data_df, offset * SAMPLE_RATE, start_WT, end_WT, thresh, SAMPLE_RATE
        )
        result_df = pd.DataFrame(
            columns=[
                "peaks",
                "amp",
                "max_deriv",
                "rise_time",
                "decay_time",
                "SCR_width",
            ]
        )
        result_df["peaks"] = returnedPeakData[0]
        result_df["amp"] = returnedPeakData[5]
        result_df["max_deriv"] = returnedPeakData[6]
        result_df["rise_time"] = returnedPeakData[7]
        result_df["decay_time"] = returnedPeakData[8]
        result_df["SCR_width"] = returnedPeakData[9]
        featureData = result_df[result_df.peaks == 1][
            ["peaks", "rise_time", "max_deriv", "amp", "decay_time", "SCR_width"]
        ]

        # Replace 0s with NaN, this is where the 50% of the peak was not found, too close to the next peak
        featureData[["SCR_width", "decay_time"]] = featureData[
            ["SCR_width", "decay_time"]
        ].replace(0, np.nan)
        featureData["AUC"] = featureData["amp"] * featureData["SCR_width"]

        peaks.append(len(featureData))
        amps.append(result_df[result_df.peaks != 0.0].amp.mean())
        max_derivs.append(result_df[result_df.peaks != 0.0].max_deriv.mean())
        rise_times.append(result_df[result_df.peaks != 0.0].rise_time.mean())
        decay_times.append(featureData[featureData.peaks != 0.0].decay_time.mean())
        SCR_widths.append(featureData[featureData.peaks != 0.0].SCR_width.mean())
        aucs.append(featureData[featureData.peaks != 0.0].AUC.mean())

    df["peaks_p"] = peaks
    df["rise_time_p"] = rise_times
    df["max_deriv_p"] = max_derivs
    df["amp_p"] = amps
    df["decay_time_p"] = decay_times
    df["SCR_width_p"] = SCR_widths
    df["auc_p"] = aucs

    print("4. Peaks feature extraction completed")

    return df
