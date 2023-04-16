import os
import pandas as pd
import transform_video_data.data_generator as dgen


def get_file_name(path):
    file_name = path[path.rfind('/') + 1:]
    # Splits out the file-type designation
    file_name, file_extension = file_name.split('.')
    return file_name


def prepare_csv_file(csv_path, path_output, vid_path):
    import pandas as pd

    # Read csv as df
    df = pd.read_csv(csv_path, sep=",")

    # Drop all the rows where there is cycled yet
    begin_data = True
    for index, row in df.iterrows():
        if begin_data:
            if row['Cadence (RPM)'] > 0:
                df = df.loc[index:]
                begin_data = False

    # Save the clean dataset & dropping all the unneeded columns
    df.reset_index(inplace=True, drop=True)

    # Define time id
    df['idTime'] = None
    for index, row in df.iterrows():
        df['idTime'][index] = 5 * int(index) * 1000

    df = df.rename(columns={'Heart Rate (BPM)': 'idHeartrate', 'Power (W)': 'idPower'})

    # Save this df as csv
    df.to_csv(f"{path_output}/{get_file_name(vid_path)}_raw_data.csv")

    return df


class Transform:
    def __init__(self, path):
        import subprocess
        subprocess.run(["python", "-V"])
        subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.run(["pip", "install", "mediapipe", "moviepy"])

        self.path = path
        self.save_data()

    def save_data(self):
        # Loop through each file and save the path
        path_input = f"{self.path}/data/input/"
        path_output = f"{self.path}/data/output_video/"

        # Converting xls files to csv
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
                with open(path_input + f'/{filename[:-4]}.csv', 'w', newline='') as f:
                    # df.to_csv(f, index=False)
                    df.to_csv(f, index=None, header=True)

        # Saving all file directories
        videos_path = []
        csv_files_path = []
        for filename in os.listdir(path_input):
            f_dir = os.path.join(path_input, filename)

            if f_dir.endswith('MP4') or f_dir.endswith('mp4'):  # saving mp4 files dir
                videos_path.append(f_dir)

            elif f_dir.endswith('csv'):  # saving csv files dir
                csv_files_path.append(f_dir)

        # making a dictionary of all the files sorted on the session
        session_files = {}
        for video_path in videos_path:
            session_video = video_path[video_path.rfind("-") + 1:]
            # Splits out the file-type designation
            session_video, _ = session_video.split('.')
            session1 = None
            session2 = None
            for csv_file_path in csv_files_path:
                session_csv_file = csv_file_path[csv_file_path.rfind("-") + 1:]
                # Splits out the file-type designation
                session_csv_file, _ = session_csv_file.split('.')
                # Checking if the csv file is from session 1 or 2
                if session_csv_file[1:] == session_video:
                    if csv_file_path.__contains__('session 1'):
                        session1 = csv_file_path
                    elif csv_file_path.__contains__('session 2'):
                        session2 = csv_file_path
            # Adding the files dir to files dictionary
            if session1 is not None and session2 is not None:
                session_files[f"Session {session_video}"] = {
                    "video_path": video_path,
                    "csv_session1_path": session1,
                    "csv_session2_path": session2,
                }

        for session in session_files:
            # Generate a df from the video and csv file
            generator = dgen.Generator(session_files[session]["video_path"],
                                       prepare_csv_file(session_files[session]["csv_session1_path"],
                                                             path_output,
                                                             session_files[session]["video_path"]),
                                       path_output)
            generator.generate_data()