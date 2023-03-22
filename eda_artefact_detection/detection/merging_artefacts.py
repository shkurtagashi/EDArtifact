def label_artifacts(database_wo_flats_artifacts, database):
    """
    This function adds the "Artifacts" column to the initial dataframe provided.

    INPUT:
        database_wo_flats_artifacts:        requires as input the dataframe without flat responses
        database:                           requires as input the initial dataframe with EDA and Time colmns

    OUTPUT:
        database:                           returns the database dataframe with a new column "Artifact"s
    """

    database_wo_flats_artifacts = database_wo_flats_artifacts.explode("Time_array")

    # Add a new column that will contain the labeled artifacts (0 refers to clean, 1 refers to artifact)
    database["Artifact"] = 0

    # Add the identified artifacts from dataframe without flat responses to the initial dataframe with EDA and Time columns
    database.loc[
        database.Time.isin(database_wo_flats_artifacts.Time_array), "Artifact"
    ] = database_wo_flats_artifacts.loc[
        database_wo_flats_artifacts.Time_array.isin(database.Time), "Artifact"
    ].values

    # Label EDA < 0.05 as artifact
    database.loc[database.EDA < 0.05, "Artifact"] = 1

    print("7. Preparing final database with labeled artifacts completed")

    return database
