# Concatenate FED files
# This script concatenates FED files from a list of CSV files and saves the result to a new CSV file.
# It assumes that the files are named in a way that allows for chronological sorting based on the timestamp column.
# It also checks for session type consistency and time gaps between files.

import pandas as pd

# List of CSV file paths - update this to reflect the files you want to concatenate
file_paths = [
    r'C:\Users\basugargic\Box\Kravitz Lab Box Drive\Mason\Cashikar FED Data\Round 1 FR1\FR1 Device 2 1521\FED002_010725_04.csv',
    r'C:\Users\basugargic\Box\Kravitz Lab Box Drive\Mason\Cashikar FED Data\Round 1 FR1\FR1 Device 2 1521\FED002_011225_02.csv'
    # Add more files here as needed
]

# Output file path - update this to reflect the desired output file location
output_file = r'C:\Users\basugargic\Box\Kravitz Lab Box Drive\Gargi\Cashikar_2025\FR1_Round\FED002_010725_concat.csv'

# Initialize an empty DataFrame for concatenation
df_combined = pd.DataFrame()

# List to hold (timestamp, file_path) tuples
file_info = []

# Loop through the files to get the first timestamp of each file
for file_path in file_paths:
    df = pd.read_csv(file_path, header=0)  # Read the file
    df['MM:DD:YYYY hh:mm:ss'] = pd.to_datetime(df['MM:DD:YYYY hh:mm:ss'])  # Convert timestamp to datetime
    first_timestamp = df['MM:DD:YYYY hh:mm:ss'].iloc[0]  # Get the first timestamp
    file_info.append((first_timestamp, file_path))  # Store the timestamp and file path

# Sort the files by the first timestamp (chronologically)
file_info.sort(key=lambda x: x[0])

# Reorder the file_paths based on the sorted timestamps
file_paths_sorted = [file_path for _, file_path in file_info]

# Initialize the combined DataFrame with the first sorted file
df_combined = pd.read_csv(file_paths_sorted[0], header=0)
df_combined['MM:DD:YYYY hh:mm:ss'] = pd.to_datetime(df_combined['MM:DD:YYYY hh:mm:ss'])

# Track the current maximum values of the counting columns
left_poke_max = df_combined['Left_Poke_Count'].max()
right_poke_max = df_combined['Right_Poke_Count'].max()
pellet_count_max = df_combined['Pellet_Count'].max()

# Loop through the rest of the sorted files
for file_path in file_paths_sorted[1:]:
    # Read the next file without headers
    df_new = pd.read_csv(file_path, header=0)

    # Ensure 'timestamp' column is in datetime format for the new file
    df_new['MM:DD:YYYY hh:mm:ss'] = pd.to_datetime(df_new['MM:DD:YYYY hh:mm:ss'])

    # Check if session types are the same in both files
    if df_combined['Session_type'].iloc[0] != df_new['Session_type'].iloc[0]:
        raise ValueError(f"Error: Session types are different between files! Cannot concatenate {file_path}.")

    # Check if the time gap between the last timestamp in the combined DataFrame and the first timestamp in the new file is greater than 24 hours
    time_gap = df_new['MM:DD:YYYY hh:mm:ss'].iloc[0] - df_combined['MM:DD:YYYY hh:mm:ss'].iloc[-1]
    if time_gap > pd.Timedelta(hours=24):
        print(f"Warning: Timestamps are not contiguous between {file_paths[0]} and {file_path}, please check the files")

    # Increment the count for the new DataFrame
    df_new['Left_Poke_Count'] += left_poke_max
    df_new['Right_Poke_Count'] += right_poke_max
    df_new['Pellet_Count'] += pellet_count_max

    # Append the new DataFrame to the combined DataFrame
    df_combined = pd.concat([df_combined, df_new], ignore_index=True)

    # Update the max values for the next file
    left_poke_max = df_combined['Left_Poke_Count'].max()
    right_poke_max = df_combined['Right_Poke_Count'].max()
    pellet_count_max = df_combined['Pellet_Count'].max()

# Save the concatenated DataFrame to a new CSV file in the desired folder
df_combined.to_csv(output_file, index=False)

print("CSV files have been concatenated successfully!")
