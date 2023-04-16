import os

import pandas as pd


class TestInputFiles():
    def __init__(self, path):
        self.path = path

    def test_input(self):
        # Defien input path
        path_input = f"{self.path}/data/input/"

        # Saving the dataframes to test_pipeline
        dfs = []

        # Converting xls files to usable dataframes
        for filename in os.listdir(path_input):
            f_dir = os.path.join(path_input, filename)

            if f_dir.endswith('csv'):  # saving csv files dir
                pass

            elif f_dir.endswith('xls'):  # handeling excel files and saving them as csv
                # Reading an excel file
                excel_file = pd.read_excel(f_dir)

                # Dropping the unneeded rows
                df = excel_file.loc[6:]
                df.columns = df.iloc[0]  # Save column names
                df = df.loc[8:]

                # Save the file as csv
                dfs.append(df)

        # Checking if dataframes match expected columns
        expected_columns = ['Date (dd/mm/yyyy)', 'Time (HH:MM:SS)', 'VO2 (mL/min)', 'VCO2 (mL/min)',
       'RER', 'Energy Expenditure (kJ/min)', 'Energy Expenditure (kcal/min)',
       'FiO2 (%)', 'FeO2 (%)', 'FiCO2 (%)', 'FeCO2 (%)', 'Flow (sL/min)',
       'Pressure Ambient (mbar)', 'Temperature Flow (Degrees Celsius)',
       'Relative Humidity Flow (%)', 'Specific VO2 (mL/min/kg)',
       'Specific VCO2 (mL/min/kg)', 'Respiratory Rate (1/min)',
       'Ventilation (sL/min)', 'Test Phase (1, 2 or 3)',
       'Time From Start (ms/10)', 'Distance Traveled From Start (m)',
       'Axis Rotations From Start (rotations)', 'Work Load From Start (J)',
       'Cadence (RPM)', 'Heart Rate (BPM)', 'Speed (km/h)', 'Transmission',
       'Power (W)', 'Specific Power (W/kg)', 'Inclination (%)',
       'Pedal Pressure (N)']
        for df in dfs:
            if all(col in df.columns for col in expected_columns):
                pass
            else:
                return False
        return True
