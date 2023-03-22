import pandas as pd
from eda_artefact_detection.detection.preprocess import preprocess_eda_signals
from eda_artefact_detection.detection.merging_artefacts import label_artifacts
from eda_artefact_detection.detection.predict import predict_shape_artifacts
from eda_artefact_detection.detection.peaks import compute_peaks_features
from eda_artefact_detection.detection.wavelets import compute_statistical_wavelet
from eda_artefact_detection.detection.segment import segment_eda_data


def remove_flat_responses(df):
    """
    This function computes the peaks features for each 5 second window in the EDA signal.

    INPUT:
        df:        requires a dataframe with the calculated EDA slope feature

    OUTPUT:
        df:        returns a dataframe with only the 5-second windows that are not flat responses
    """

    eda_flats = df.EDA_slope.between(-0.002, 0.002)
    df["Flat"] = eda_flats.values
    df["Flat"] = df.Flat.astype(int).values
    df_wo_flat = df[df.Flat == 0]

    print("5. Flat responses removed")

    return df_wo_flat


def make_timestamp_idx(dataframe: pd.DataFrame, data_name: str) -> pd.DataFrame:
    """A simple method to make the timestamp in a dataframe as the index for it.

    Parameters
    ----------
    dataframe : DataFrame
        dataframe to make timestamp index
    side : str
        side, 'left' or 'right', to work on
    data_name : str
        type of data, e.g. "ACC" or "EDA"
    individual_name : str | None, optional
        name of the individual to work on, e.g. 's034', by default None

    Returns
    -------
    DataFrame
        returns the dataframe with the new index
    """
    #     NOTE: tested the alterative with regex, i.e. split on "." and then cast to int directly
    #     and the time is similar
    # dataframe.attrs["sampling frequency"] = int(float(dataframe.columns[0][-1]))
    # dataframe.attrs["start timestamp [unixtime]"] = dataframe.columns[0][0]
    dataframe.attrs["start timestamp"] = pd.to_datetime(
        dataframe.attrs["start timestamp [unixtime]"], unit="s", utc=True
    )
    dataframe.attrs["start timestamp"] = dataframe.attrs["start timestamp"].tz_convert(
        "Europe/Rome"
    )

    if data_name == "ACC":
        dataframe.columns = [f"{data_name}_{axis}" for axis in ["x", "y", "z"]]
    index_timestamps = pd.date_range(
        start=dataframe.attrs["start timestamp"],
        periods=len(dataframe.index),
        freq=f"{1/dataframe.attrs['sampling frequency']*1000}ms",
    )

    dataframe.index = index_timestamps
    dataframe.attrs["start timestamp"] = str(dataframe.attrs["start timestamp"])
    return dataframe.sort_index()


def compute_eda_artifacts(
    file_path: str,
    model_path: str,
    show_database: bool = False,
    convert_dataframe: bool = False,
    output_path: str | None = None,
    header: None | int | list[int] = None,
    window_size: int = 5
):
    # Read EDA data file
    if file_path.split(".")[-1] == "csv":
        database = pd.read_csv(file_path, header=header)
    elif file_path.split(".")[-1] == "xlsx":
        database = pd.read_excel(file_path, header=header)
    elif file_path.split(".")[-1] == "parquet":
        database = pd.read_parquet(file_path, header=header)

    if convert_dataframe:
        if "mixed-EDA" in database.columns:
            database = database.reset_index(inplace=False, drop=False)
            database = database.rename(
                columns={"mixed-EDA": "EDA", "timestamp": "Time"}
            )
        else:
            database.attrs["sampling frequency"] = int(float(database.columns[0][-1]))
            database.attrs["start timestamp [unixtime]"] = database.columns[0][0]
            database = make_timestamp_idx(database, data_name="EDA")
            database = database.reset_index(inplace=False, drop=False)
            database.columns = ["Time", "EDA"]

    if show_database:
        print(database)
    # Ensure the length of the signal to be a modulo of 20 EDA samples, which correspond to a 5-second window
    sampling_rate: int = 4
    if not (len(database) % (window_size * sampling_rate)) == 0:
        database = database[: -(len(database) % (window_size * sampling_rate))]
    database_copy = database.copy()

    # 1. Preprocess the EDA signals
    database_preprocessed = preprocess_eda_signals(database_copy)

    # 2. Segment EDA data
    database_segmented = segment_eda_data(
        database_preprocessed, window_size=window_size
    )

    # 3.1 Compute statistical and wavelet features
    database_features = compute_statistical_wavelet(database_segmented, window_size)

    # 3.2 Compute peaks features
    database_features = compute_peaks_features(database_features, window_size)

    # 4. Remove flat responses
    database_wo_flats = remove_flat_responses(database_features)

    features = [
        "EDA_median",
        "EDA_mean",
        "EDA_std",
        "EDA_slope",
        "EDA_min",
        "EDA_max",
        "EDA_fdmean",
        "EDA_fdstd",
        "EDA_sdmean",
        "EDA_sdstd",
        "EDA_drange",
        "EDA_Phasic_median",
        "EDA_Phasic_mean",
        "EDA_Phasic_std",
        "EDA_Phasic_slope",
        "EDA_Phasic_min",
        "EDA_Phasic_max",
        "EDA_Phasic_fdmean",
        "EDA_Phasic_fdstd",
        "EDA_Phasic_sdmean",
        "EDA_Phasic_sdstd",
        "EDA_Phasic_drange",
        "peaks_p",
        "rise_time_p",
        "amp_p",
        "decay_time_p",
        "SCR_width_p",
        "auc_p",
        "Wavelet3_mean",
        "Wavelet3_median",
        "Wavelet3_std",
        "Wavelet2_mean",
        "Wavelet2_median",
        "Wavelet2_std",
        "Wavelet1_mean",
        "Wavelet1_median",
        "Wavelet1_std",
    ]

    # 5. Identify artifacts in EDA
    database_wo_flats_artifacts = predict_shape_artifacts(features, database_wo_flats, model_path=model_path)

    # 6. Prepare final database with labeled artifacts
    database_w_artifacts = label_artifacts(database_wo_flats_artifacts, database)

    # Write the file with eda artifacts labeled in the same file path as the original file
    if not output_path:
        database.to_csv(file_path[:-4] + "_artifacts.csv", index=False)
    else:
        database.to_csv(output_path, index=False)
