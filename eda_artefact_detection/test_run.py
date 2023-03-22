from support import compute_eda_artifacts
file_path = "/Users/leonardoalchieri/Datasets/USILaughs/participants/s037/left/EDA.csv"
model_path = "/Users/leonardoalchieri/Desktop/GIT/EDArtifact/EDArtifacts_Detection/SA_Detection.json"
compute_eda_artifacts(
    file_path,
    show_database=True,
    convert_dataframe=True,
    output_path="test.csv",
    header=[0, 1],
    window_size=4,
    model_path=model_path
)

