import xgboost


def predict_shape_artifacts(features, df, model_path: str):
    """
    This function computes whether a 5-second EDA segment is an artifact or not

    INPUT:
        features:      list of features used as input in the model
        df:            requires a dataframe with columns 'EDA_Phasic' and 'Time'

    OUTPUT:
        df:            returns the same dataframe with new columnn "Artifact" that contains
        a value of 1 when an artifact is predected and 0 otherwise.

    """
    df = df.fillna(-1)

    # Normalize the features before providing as input to the model
    #     scaler = MinMaxScaler()
    #     for i in features:
    #         df[i] = scaler.fit_transform(df[[i]])

    # Select only the features that have been used in the paper
    df_subselect = df[features]
    test_data = df_subselect.values

    # Load the trained model
    model = xgboost.XGBClassifier()
    try:
        model.load_model(model_path)
    except Exception as e:
        print(f'Error loading model: {e}')
        raise RuntimeError(f'Failed to load xgboost model. See previous print for error detail. Input path give: {model_path}')
        
    # model = pickle.load(open('SA_Detection.sav', 'rb'))

    # Use the loaded model to find artifacts
    results = model.predict(test_data)

    # Create a new column that shows whether the window contains an artifact (1) or not (0)
    df["Artifact"] = list(results)

    print("6. EDA artifacts detection completed")

    return df
