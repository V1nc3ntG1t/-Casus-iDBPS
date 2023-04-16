import pandas as pd
import os


class Preparation:
    def __init__(self, path):
        self.path = path
        self.clean_df = None
        self.save_df()

    def merge_session1(self, df_session1_raw, df_session1_video):
        import pandas as pd

        # Drop all the rows where there is cycled yet
        begin_data = True
        for index, row in df_session1_raw.iterrows():
            if begin_data:
                if row['Cadence (RPM)'] > 0:
                    df_session1_raw = df_session1_raw.loc[index:]
                    begin_data = False

        # Save the clean dataset & dropping all the unneeded columns
        df_session1_raw.reset_index(inplace=True, drop=True)

        # Convert list items in video dataset
        Xtemp = df_session1_video.drop(columns=['HR', 'PWR', 'heartRateZone']).copy()
        X = []
        temp = []
        # Extracting values in lists in lists
        for index, row in Xtemp.iterrows():
            for i in range(1, 479):
                for g in range(0, 3):
                    temp.append(row[i][0][g])
            X.append(temp)
            temp = []

        df_vid_temp = pd.DataFrame(X, columns=list(range(0, len(X[0]))))
        df_session1_video.reset_index(inplace=True, drop=True)
        df_video = df_vid_temp.merge(df_session1_video['TS'], left_index=True, right_index=True)

        # Merge video data and raw data from session 1
        df_session1 = df_session1_raw.merge(df_video, left_on='idTime', right_on='TS')
        df_session1 = df_session1.drop(columns=['TS', 'Unnamed: 0'])
        return df_session1

    def merge_session1_session2(self, df_session1, df_session2):
        dfs = [df_session1, df_session2]

        count = 0
        for df in dfs:
            if count == 0:
                df = df.rename(columns={'idHeartrate': 'Heart Rate (BPM)', 'idPower': 'Power (W)'})

            # Drop all the rows where there is not a workout
            old_row = None
            begin_data = True
            end_data = True
            for index, row in df.iterrows():
                if begin_data:
                    if row['Power (W)'] < 100:
                        pass
                    else:
                        df = df.loc[index:]
                        begin_data = False
                elif end_data:
                    if row['Power (W)'] < old_row['Power (W)']:
                        df = df.loc[:index - 1]
                        end_data = False
                old_row = row

            # Save the clean dataset & dropping all the unneeded columns
            df.reset_index(inplace=True, drop=True)

            # Drop irrelevant columns what wont be available for a model
            df = df.drop(
                    columns=['Date (dd/mm/yyyy)', 'Time (HH:MM:SS)', 'VO2 (mL/min)', 'VCO2 (mL/min)',
           'RER', 'Energy Expenditure (kJ/min)', 'Energy Expenditure (kcal/min)',
           'FiO2 (%)', 'FeO2 (%)', 'FiCO2 (%)', 'FeCO2 (%)', 'Flow (sL/min)',
           'Pressure Ambient (mbar)', 'Temperature Flow (Degrees Celsius)',
           'Relative Humidity Flow (%)', 'Specific VO2 (mL/min/kg)',
           'Specific VCO2 (mL/min/kg)', 'Test Phase (1, 2 or 3)',
           'Time From Start (ms/10)', 'Distance Traveled From Start (m)',
           'Axis Rotations From Start (rotations)', 'Work Load From Start (J)',
           'Cadence (RPM)', 'Heart Rate (BPM)', 'Speed (km/h)', 'Transmission',
           'Power (W)', 'Specific Power (W/kg)', 'Inclination (%)',
           'Pedal Pressure (N)'])

            if count == 0:
                df = df.drop(columns=['Respiratory Rate (1/min)', 'Ventilation (sL/min)'])

                time = df['idTime'].loc[0]
                df['idTime'] = df['idTime']-time

            if count == 1:
                # Define time id
                df['idTime'] = None
                for index, row in df.iterrows():
                    df['idTime'][index] = 5 * int(index) * 1000

            dfs[count] = df

            count += 1

        # Merge session 1 and 2
        df_clean = dfs[0].merge(dfs[1], left_on='idTime', right_on='idTime')
        df_clean.drop(columns=['idTime'], inplace=True)

        return df_clean

    def save_df(self):
        # Loop through each file and save the path
        path_input = f"{self.path}/data/input/"
        path_output = f"{self.path}/data/output_video/"
        path_clean_dataset = f"{self.path}/data/clean_dataset/"

        # Saving all file directories
        files_path = []
        for filename in os.listdir(path_input):
            f_dir = os.path.join(path_input, filename)
            if f_dir.endswith('csv'):  # saving csv files dir
                files_path.append(f_dir)
        for filename in os.listdir(path_output):
            f_dir = os.path.join(path_output, filename)
            if f_dir.endswith('csv'):  # saving csv files dir
                files_path.append(f_dir)
            if f_dir.endswith('json'):  # saving csv files dir
                files_path.append(f_dir)

        # making a dictionary of all the dfs sorted on the session
        session_dfs = {}
        for file_path in files_path:
            if file_path.endswith("_raw_data.csv"):
                session = file_path[file_path.rfind("-") + 1:-13]
                try:
                    session_dfs[session]["session1_raw_df"] = pd.read_csv(file_path, sep=",")
                except:
                    session_dfs[session] = {}
                    session_dfs[session]["session1_raw_df"] = pd.read_csv(file_path, sep=",")
            elif file_path.endswith(".csv"):
                session = file_path[file_path.rfind("-") + 2:]
                session, _ = session.split('.')
                try:
                    session_dfs[session]["session2_df"] = pd.read_csv(file_path, sep=",")
                except:
                    session_dfs[session] = {}
                    session_dfs[session]["session2_df"] = pd.read_csv(file_path, sep=",")
            elif file_path.endswith(".json"):
                session = file_path[file_path.rfind("-") + 1:-16]
                try:
                    session_dfs[session]["session1_video_df"] = pd.read_json(file_path, orient='index')
                except:
                    session_dfs[session] = {}
                    session_dfs[session]["session1_video_df"] = pd.read_json(file_path, orient='index')

        # Make clean df
        for session in session_dfs:
            df_session1 = self.merge_session1(session_dfs[session]["session1_raw_df"],
                                              session_dfs[session]["session1_video_df"],)
            new_clean_df = self.merge_session1_session2(df_session1, session_dfs[session]["session2_df"])

            # Concat the clean dfs from the df
            try:
                self.clean_df = pd.concat([self.clean_df, new_clean_df])
            except:
                self.clean_df = new_clean_df

        self.clean_df.to_csv(f"{path_clean_dataset}/dataset.csv")