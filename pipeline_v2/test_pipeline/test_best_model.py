import math
import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


class TestBestModel():
    def __init__(self, path, clean_df):
        self.path = path
        self.clean_df = clean_df

    def select_best_model(self):
        # Define the directory containing the pickled models
        model_dir = f'{self.path}/models_versions'

        # Define the test_pipeline dataset (X_test, y_test)
        test_df = self.clean_df.sample(n=1000, random_state=42)

        # Split the data into predictors and target variabele
        X = test_df.drop(columns=['Respiratory Rate (1/min)', 'Ventilation (sL/min)'])
        y = test_df[['Respiratory Rate (1/min)', 'Ventilation (sL/min)']]

        # Initialize variables to track the best model and its score
        best_model = None
        best_score = np.inf

        # Loop through each pickle file in the directory
        for filename in os.listdir(model_dir):
            if filename.endswith('.pkl'):
                # Load the pickled model from file
                with open(os.path.join(model_dir, filename), 'rb') as f:
                    model = pickle.load(f)

                # Evaluate the model on the test_pipeline dataset
                y_pred = model.predict(X)
                score = math.sqrt(mean_squared_error(y, y_pred))

                # Update the best model and score if this model is better
                if score < best_score:
                    best_model = model
                    best_score = score

        return best_model
