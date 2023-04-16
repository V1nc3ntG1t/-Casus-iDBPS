# Converts MNIST-formatted files at the passed-in input path to training data output path and test_pipeline data output path
import os
from pathlib import Path
from mldesigner import command_component, Input, Output
from prep.prepare_data import Preparation
import pandas as pd


@command_component(
    name="prep_data",
    version="1",
    display_name="Prep Data",
    description="Convert data to CSV file, and split to training and test_pipeline data",
    environment=dict(
        conda_file=Path(__file__).parent / "conda.yaml",
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
    ),
)
def prepare_data_component(
    session_dfs,
):

    clean_df = None
    for session in session_dfs:
        data_preperation = Preparation(session_dfs[session]["session1_raw_df"],
                                       session_dfs[session]["session1_video_df"], session_dfs[session]["session2_df"])
        df = data_preperation.get_df()

        # Concat the clean dfs from the df
        try:
            clean_df = pd.concat([clean_df, df])
        except:
            clean_df = df

    return clean_df