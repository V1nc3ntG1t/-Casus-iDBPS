# import necessary libraries
import os
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from bayes_opt import BayesianOptimization


class Model:
    def __init__(self, df):
        self.df = df
        self.X_train = None
        self.y_train = None
        self.rf = None

    def create_model(self, path):
        # Split the data into predictors and target variabele
        X = self.df.drop(columns=['Respiratory Rate (1/min)', 'Ventilation (sL/min)'])
        y = self.df[['Respiratory Rate (1/min)', 'Ventilation (sL/min)']]

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Set train_X, train_y global
        self.X_train = X_train
        self.y_train = y_train

        # Evaluate model
        rf = self.evaluate_model()
        self.rf = rf
        self.save_model(path)  # Save the model
        return rf


    def evaluate_model(self):
        # Create Bayesian Optimization
        rf_bo = BayesianOptimization(self.bo_params_rf, {
            'n_estimators': (100, 1000),
            'max_depth': (1, 20),
            'max_features': (0.1, 1),
            'min_samples_split': (2, 12)
        })

        # getting best hyperparameters from bayesian optimization
        results = rf_bo.maximize(n_iter=250, init_points=20, acq='ei')
        params = rf_bo.max['params']
        params['n_estimators'] = round(params['n_estimators'])
        params['min_samples_split'] = round(params['min_samples_split'])
        params['max_depth'] = round(params['max_depth'])

        # making random forest model with the best hyperparameters
        rf_bo = RandomForestRegressor(min_samples_split=params['min_samples_split'],
                                       max_depth=params['max_depth'],
                                       max_features=params['max_features'],
                                       n_estimators=params['n_estimators'],
                                       bootstrap=False)

        # fitting the rf with the best hyperparameters according to the bayesian
        rf_bo.fit(self.X_train, self.y_train)

        return rf_bo

    def bo_params_rf(self, min_samples_split, max_depth, max_features, n_estimators):
        # Optimizing the hyperparameters due to bayesian optimalization
        params = {
            'min_samples_split': round(min_samples_split),
            'max_depth': round(max_depth),
            'max_features': max_features,
            'n_estimators': round(n_estimators)
        }

        clf = RandomForestRegressor(min_samples_split=int(params['min_samples_split']),
                                     max_depth=int(params['max_depth']),
                                     max_features=params['max_features'],
                                     n_estimators=int(params['n_estimators']),
                                     bootstrap=False,
                                     n_jobs=-1)
        # Cross validation
        k = 10
        score = cross_val_score(clf, self.X_train, self.y_train, cv=k, scoring='accuracy', n_jobs=-1)
        return score

    def save_model(self, path):
        # Initialize counters for files and directories
        num_models = 0

        # Walk through the directory and count files
        for root, dirs, files in os.walk(path):
            num_models += len(files)

        # Save model
        filename = f'{path}/models_versions/random_forest_v{num_models+1}.pkl'
        pickle.dump(self.rf, open(filename, 'wb'))
