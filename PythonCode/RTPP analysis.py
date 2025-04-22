# -*- coding: utf-8 -*-
"""
Created on Mon May 13 22:44:01 2024

@author: Justin
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import Tk
import csv
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from scipy.stats import linregress


#%% batched processing -- first we will crop to 1800 seconds (30min) and concatenate the pairs of left and right files per mouse

def process_files(filename):
    # Processing a single file as per your specifications
    df = pd.read_csv(filename)
    df = df[['Item1.Timestamp', 'Item2', 'Item3', 'Item4']]
    df.columns = ['Timestamp', 'Stim', 'X', 'Y']
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Timestamp'] = df['Timestamp'] - df['Timestamp'].iloc[0]
    df['Timestamp'] = df['Timestamp'].dt.total_seconds()
    df = df[df['Timestamp'] < 1800]

    # Interpolate NaN values
    df.interpolate(method='linear', limit_direction='forward', axis=0, inplace=True)
    return df

def main():
    Tk().withdraw()  # Avoid full GUI
    print("Please select a directory containing CSV files.")
    directory = askdirectory()

    if directory:
        print(f"Directory selected: {directory}")
        preprocessed_dir = os.path.join(directory, 'preprocessed')
        concatenated_dir = os.path.join(directory, 'concatenated')
        os.makedirs(preprocessed_dir, exist_ok=True)
        os.makedirs(concatenated_dir, exist_ok=True)

        # Process each CSV in the directory
        processed_files = []
        for file in os.listdir(directory):
            if file.endswith('.csv'):
                print(f"Processing file: {file}")
                df = process_files(os.path.join(directory, file))
                processed_path = os.path.join(preprocessed_dir, file.replace('rtpp', 'processed'))
                df.to_csv(processed_path, index=False)
                processed_files.append(processed_path)
                print(f"File processed and saved to: {processed_path}")

        # Concatenate files based on the first seven characters
        file_groups = {}
        for file in processed_files:
            prefix = os.path.basename(file)[:6]
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(file)

        for prefix, files in file_groups.items():
            print(f"Concatenating files for prefix: {prefix}")
            df_list = []
            for f in files:
                df = pd.read_csv(f)
                # Check if filename contains 'right' and adjust 'Timestamp'
                if 'right' in os.path.basename(f):
                    df['Timestamp'] += 1800
                df_list.append(df)
            concatenated_df = pd.concat(df_list, ignore_index=True)
            concatenated_path = os.path.join(concatenated_dir, f"{prefix}_concatenated.csv")
            concatenated_df.to_csv(concatenated_path, index=False)
            print(f"Files concatenated and saved to: {concatenated_path}")

        print("All files have been processed and concatenated.")
    else:
        print("No directory was selected.")

if __name__ == "__main__":
    main()

#%% 

print("Please select a CSV file.")
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename()  # show an "Open" dialog box and return the path to the selected file

if filename:
    print(f"File selected: {filename}")
else:
    print("No file was selected.")

if filename:  # Checks if a filename has been selected
    df = pd.read_csv(filename)
    print("Uploaded file successfully loaded into DataFrame 'df'.")
else:
    print("No file uploaded or processing skipped due to no file selection.")

# Filter data for the first 1800 seconds and after 1800 seconds
df_first_1800 = df[df['Timestamp'] <= 1800]
df_after_1800 = df[df['Timestamp'] > 1800]

# Create a figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(15, 6), sharey=True)  # Shared y-axis for better comparison

fig.suptitle(filename, fontsize=16)

# Plotting for the first 1800 seconds
axs[0].plot(df_first_1800['X'], df_first_1800['Y'], linestyle='-', marker='', color='gray', alpha=0.6)
stim_points_first = df_first_1800[df_first_1800['Stim']]
axs[0].scatter(stim_points_first['X'], stim_points_first['Y'], color='#158DF0', s=10, alpha=0.25)
axs[0].set_title('Left Paired Stimulation')
axs[0].set_xlabel('X')
axs[0].set_ylabel('Y')

# Plotting for after 1800 seconds
axs[1].plot(df_after_1800['X'], df_after_1800['Y'], linestyle='-', marker='', color='gray', alpha=0.6)
stim_points_after = df_after_1800[df_after_1800['Stim']]
axs[1].scatter(stim_points_after['X'], stim_points_after['Y'], color='#158DF0', s=10, alpha=0.25)
axs[1].set_title('Right Paired Stimulation')
axs[1].set_xlabel('X')

# Remove x and y tick marks
for ax in axs:
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

plt.tight_layout()

plt.show()



#%% Let's visualize our grouped concatenated data

# Function to load and average data from a CSV file
def load_and_average(file_path, interval='60s'):
    data = pd.read_csv(file_path)
    data['Timestamp'] = pd.to_timedelta(data['Timestamp'], unit='s')
    data.set_index('Timestamp', inplace=True)
    averaged_data = data.resample(interval).mean().reset_index()
    averaged_data['file'] = file_path.split('/')[-1]
    return averaged_data

# Ask for the directory
print("Please select a directory containing CSV files.")
Tk().withdraw()
directory = askdirectory()

if not directory:
    print("No directory was selected.")
    exit()

# Load and average data from all files
all_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]
all_averaged_data = pd.concat([load_and_average(file) for file in all_files])

# Convert 'Timestamp' from Timedelta to total minutes for easier plotting
all_averaged_data['Timestamp_minutes'] = all_averaged_data['Timestamp'].dt.total_seconds() / 60

# Group by 'Timestamp_minutes' and calculate the mean of 'X' across all files
grouped_data = all_averaged_data.groupby('Timestamp_minutes')['X'].mean().reset_index()

# Create a larger plot for better visibility
plt.figure(figsize=(12, 6))

plt.rcParams['font.family'] = 'Arial'
plt.rc('font', size=24)

# Plot individual traces for each file
for file, df_group in all_averaged_data.groupby('file'):
    sns.lineplot(x='Timestamp_minutes', y='X', data=df_group, color='#158DF0', ci=None, linestyle='-', alpha=0.75, lw=0.75)

# Plot the combined average data in black
sns.lineplot(x='Timestamp_minutes', y='X', data=grouped_data, color='#1A36EB', label='Average (N=11 6M/5F)', ci=None, lw=2.5)

# Add the vertical line at x=1600 seconds (converted to minutes)
plt.axvline(x=1600/60, color='black', linestyle='--', label='Reversal')

plt.axhline(y=375, color='red', linestyle='--', label='Stimulation threshold')


# Set titles and labels
plt.title('')
plt.xlabel('Time (min)')
plt.ylabel('X Position (a.u.)')
plt.ylim(0, 800)
plt.legend(title='', bbox_to_anchor=(0.8, 1), loc='upper left')
sns.despine()

# Show the plot
plt.tight_layout()
plt.show()

#%%



#%%

# Load the data
file_path = r'C:\Users\wangjg\Box\Kravitz Lab Box Drive\Justin\VP GABA ChR2\RTPP\VP optofeeding with RTPP longform.csv'
data = pd.read_csv(file_path)
# Clean column names
data.columns = data.columns.str.strip()

# Separate data for 'chow' and 'HFD'
chow_data = data[data['Treatment'] == 'chow']
hfd_data = data[data['Treatment'] == 'HFD']

# Create the figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), sharex=True)

# Define colors
colors = {'chow': '#E8D0BE', 'HFD': '#D2DBEC'}

# ---- First subplot: Chow consumption vs. preference ----
ax1.scatter(chow_data['Consumption'], chow_data['Preference'], color='black', s=100, alpha=1, clip_on=False)
slope, intercept, r_value, p_value, std_err = linregress(chow_data['Consumption'], chow_data['Preference'])
r_squared = r_value**2

# Define line for regression line
x_vals = np.linspace(0, chow_data['Consumption'].max(), 100)
y_vals = slope * x_vals + intercept
ax1.plot(x_vals, y_vals, color='blue', linestyle='--', linewidth=3)

# Display R^2 value
ax1.text(0.5 * chow_data['Consumption'].max(), 0.95 * chow_data['Preference'].max(), 
         f'$R^2$ = {r_squared:.2f}', fontsize=16, color='blue')

# Customize subplot
ax1.set_xlabel('Consumption (g)', size=20)
ax1.set_ylabel('Preference (%)', size=20)
ax1.set_title('Chow', fontsize=24)

# ---- Second subplot: HFD consumption vs. preference ----
ax2.scatter(hfd_data['Consumption'], hfd_data['Preference'], color='black', s=100, alpha=1, clip_on=False)
slope, intercept, r_value, p_value, std_err = linregress(hfd_data['Consumption'], hfd_data['Preference'])
r_squared = r_value**2

# Define line for regression line
x_vals = np.linspace(0, hfd_data['Consumption'].max(), 100)
y_vals = slope * x_vals + intercept
ax2.plot(x_vals, y_vals, color='blue', linestyle='--', linewidth=3)

# Display R^2 value
ax2.text(0.5 * hfd_data['Consumption'].max(), 0.95 * hfd_data['Preference'].max(), 
         f'$R^2$ = {r_squared:.2f}', fontsize=16, color='blue')

# Customize subplot
ax2.set_xlabel('Consumption (g)', size=20)
ax2.set_ylabel('Preference (%)', size=20)
ax2.set_title('HFD', fontsize=24)

# Set tick parameters
for ax in (ax1, ax2):
    ax.tick_params(axis='both', which='major', labelsize=16)
    for spine in ax.spines.values():
        spine.set_linewidth(2)

plt.tight_layout()
sns.despine()

plt.show()


