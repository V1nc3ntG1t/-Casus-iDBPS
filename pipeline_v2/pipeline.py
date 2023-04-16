import subprocess
subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
# install packages from requirements.txt
# subprocess.run(["pip", "install", "-r", "requirements.txt"])
subprocess.run(["pip", "install", "mediapipe", "moviepy"])
subprocess.run(["pip", "install", "bayesian-optimization"])
subprocess.run(["pip", "install", "-r", "requirements.txt"])


# TODO: globale requirements doc
import json
import sys
import time
import os

# Prepare Job Input
PATH = os.getcwd()  # This is not for docker

# Define and load command component
from transform_video_data.pipeline_video_to_data import Transform
from data_preperation.prepare_data import Preparation
from train_evaluate_model.create_model import Model
from test_pipeline.test_input_files import TestInputFiles
from test_pipeline.test_best_model import TestBestModel


def idbps_pipeline(path):
    # Test: Check input data
    if TestInputFiles(path).test_input() == False:
        print("The input is incorrect")
        return

    # Build: Transform video
    Transform(path)

    # Build: Prepare data
    clean_df = Preparation(path).clean_df

    # Build: Train & evaluate model
    model = Model(clean_df).create_model(path)

    # Test: Choose best model
    best_model = TestBestModel(path, clean_df).select_best_model()

    # Deploy: Deploy the model
    # TODO: This is not implemented yet
    # Temporary - save it as JSON (so it can be used in a js web-application)
    # Convert the trained model to a JSON object
    model_json = json.dumps(best_model, default=lambda o: o.__dict__, indent=4)

    # Save the JSON object to a file
    with open("make_the_model_available/model.json", "w") as outfile:
        outfile.write(model_json)


idbps_pipeline(PATH)

choice = input("Choose the way you want to start the pipeline\n"
               "A: Force start the pipeline once\n"
               "B: Keep the pipeline running\n"
               "Enter choice: ")

if choice == "A":
    # Force
    idbps_pipeline(PATH)

if choice == "B":
    # Automatically
    while True:
        # Code executed here
        time.sleep(86400)
        idbps_pipeline(PATH)

else:
    os.execl(sys.executable, sys.executable, *sys.argv)
