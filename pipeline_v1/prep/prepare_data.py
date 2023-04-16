class Preparation:
    def __init__(self, df_session1_raw, df_session1_video, df_session2):
        self.df_session1_raw = df_session1_raw
        self.df_session1_video = df_session1_video
        self.df_session2 = df_session2

    def merge_session1(self):
        import pandas as pd

        # Drop all the rows where there is cycled yet
        begin_data = True
        for index, row in self.df_session1_raw.iterrows():
            if begin_data:
                if row['Cadence (RPM)'] > 0:
                    self.df_session1_raw = self.df_session1_raw.loc[index:]
                    begin_data = False

        # Save the clean dataset & dropping all the unneeded columns
        self.df_session1_raw.reset_index(inplace=True, drop=True)

        # Convert list items in video dataset
        Xtemp = self.df_session1_video.drop(columns=['HR', 'PWR', 'heartRateZone']).copy()
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
        self.df_session1_video.reset_index(inplace=True, drop=True)
        df_video = df_vid_temp.merge(self.df_session1_video['TS'], left_index=True, right_index=True)

        # Merge video data and raw data from session 1
        df_session1 = self.df_session1_raw.merge(df_video, left_on='idTime', right_on='TS')
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

        return df_clean

    def get_df(self):
        df_session1 = self.merge_session1()
        clean_df = self.merge_session1_session2(df_session1, self.df_session2)
        return clean_df