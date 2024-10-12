import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gridspec
     

filename = r"C:\Users\lexkr\Downloads\Fluorescence_processed.csv"
df = pd.read_csv(filename)

fig, ax = plt.subplots(figsize=(8, 4))  # Unpack the returned figure and axes objects
ax.plot(df['TimeStamp'], df['Fluorescence_Corrected_Z'], label='Fluorescence Corrected', color = "g")
ax.set_xlabel('Time (seconds)')  # Set x-axis label
ax.set_ylabel('Z Score')  # Set y-axis label

# Remove right and top spines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

#%%  identify pulses
# Filter the DataFrame for rows where the 'Events' column starts with "Input2"
input2_events = df[df['Events'].str.startswith("Input2", na=False)]

# Initialize lists to hold single and double pulses
single_pulses = []
double_pulses = []

# Define the time window (2 seconds)
time_window = 2

# Classify events as either single or double pulses based on the number of nearby events within 2 seconds
for index, row in input2_events.iterrows():
    current_time = row['TimeStampAdjusted']
    # Find events within 2 seconds of the current event
    nearby_events = input2_events[(input2_events['TimeStampAdjusted'] >= current_time - time_window) &
                                  (input2_events['TimeStampAdjusted'] <= current_time + time_window)]
    
    # Check the count of nearby events
    if len(nearby_events) < 3:
        single_pulses.append(row)
    else:
        double_pulses.append(row)

# Convert the lists to DataFrames for better manipulation
single_pulses_df = pd.DataFrame(single_pulses)
double_pulses_df = pd.DataFrame(double_pulses)

# Function to filter out events occurring within less than a threshold time (1 second)
def filter_events(events_df, time_threshold=1):
    # Create a new list to hold the filtered events
    filtered_events = []
    last_event_time = None

    # Loop through the DataFrame rows
    for index, row in events_df.iterrows():
        current_time = row['TimeStampAdjusted']
        
        # If this is the first event or more than 'time_threshold' seconds have passed since the last event, keep it
        if last_event_time is None or (current_time - last_event_time) > time_threshold:
            filtered_events.append(row)
            last_event_time = current_time

    # Convert the list back to a DataFrame
    return pd.DataFrame(filtered_events)

# Apply filtering to both Single Pulses and Double Pulses
pulse1 = filter_events(single_pulses_df)
pulse2 = filter_events(double_pulses_df)

#%%

timestamps = list(pulse2["TimeStampAdjusted"])[4:14]

# Reset the list to store slices from the "Fluorescence_Corrected" column
Fluorescence_corrected_slices = []

# Loop through each timestamp, extract slices, and append to the list
for timestamp in timestamps:
    # Find the index of the row closest to the timestamp
    event_index = df.index[df['TimeStampAdjusted'] == timestamp].tolist()[0]

    # Define the start and end indices for slicing
    start_index = max(event_index - 1000, 0)  # Ensure the start index is not negative
    end_index = min(event_index + 1001, len(df))  # Ensure the end index does not exceed the dataframe length

    # Extract the slice from the "Fluorescence_Corrected" column and append to the list
    Fluorescence_corrected_slice = df.loc[start_index:end_index, 'Fluorescence_Corrected_Z'].to_numpy()
    # Pad slices if they are shorter than 2001 elements to ensure uniform size
    if len(Fluorescence_corrected_slice) < 2001:
        pad_size = 2001 - len(Fluorescence_corrected_slice)
        Fluorescence_corrected_slice = np.pad(Fluorescence_corrected_slice, (0, pad_size), 'constant', constant_values=(np.nan,))
    Fluorescence_corrected_slices.append(Fluorescence_corrected_slice)

# Convert the list of slices into a 2D numpy array
Fluorescence_corrected_matrix = np.array(Fluorescence_corrected_slices)

# Recalculate the row offsets to match the dimensions of the averaged data
row_offsets_corrected = np.linspace(-1000/50, 1000/50, Fluorescence_corrected_matrix.shape[1])

# Recreate the figure with corrected dimensions
fig = plt.figure(figsize=(10, 10))

# Add the heatmap subplot
ax_heatmap = fig.add_axes([0.12, 0.3, 0.8, 0.2])  # left, bottom, width, height
sns.heatmap(Fluorescence_corrected_matrix, cmap="magma", cbar_kws={'label': 'Fluorescence'}, ax=ax_heatmap)
ax_heatmap.set_xlabel('')
ax_heatmap.set_ylabel('Trial')
ax_heatmap.set_xticks(np.linspace(0, Fluorescence_corrected_matrix.shape[1], 9))
ax_heatmap.set_xticklabels("")
ax_heatmap.grid(False)  # Remove grid lines

# Add vertical lines at specified times for the heatmap
for time in [-20, -10, 0, 10, 20]:
    ax_heatmap.axvline(x=(time + 20) * (Fluorescence_corrected_matrix.shape[1] / 40), color='white', linestyle='--')

# Add the line plot subplot with a narrower width
ax_line = fig.add_axes([0.09, 0.1, 0.7, 0.2])  # left, bottom, width, height
ax_line.plot(np.nanmean(Fluorescence_corrected_matrix, axis=0), color='blue', lw=2)
ax_line.set_xlabel('Seconds from Stimulation Train')
ax_line.set_ylabel('Average Fluorescence_Corrected')
ax_line.set_xticks(np.linspace(0, Fluorescence_corrected_matrix.shape[1], 9))
ax_line.set_xticklabels(np.round(np.linspace(-20, 20, 9), 2))
ax_line.grid(False)  # Remove grid lines
ax_line.spines['right'].set_visible(False)
ax_line.spines['top'].set_visible(False)

ax_line.set_ylim(-1.2,1)

#ax_heatmap.set_xlim(750,1300)
#ax_line.set_xlim(750,1300)
ax_line.text(1010,0.7,"Poke", fontsize=20)

# Add vertical lines at specified times for the line plot
for time in [-20, -10, 0, 10, 20]:
    ax_line.axvline(x=(time + 20) * (Fluorescence_corrected_matrix.shape[1] / 40), color='black', linestyle='--')

plt.show()
