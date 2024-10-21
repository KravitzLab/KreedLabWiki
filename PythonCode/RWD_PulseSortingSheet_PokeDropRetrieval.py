import pandas as pd

# Load the uploaded file
file_path = r"C:\Users\kravitza.PSYCH\Box\Kravitz Lab Box Drive\Chantelle\Justinpaper\AgRP\Photometry\M266fasted5spelletretrieval\Fluorescence_processed.csv"
data = pd.read_csv(file_path)

# Step 1: Filter for lines with "Input2*2*1" in the "Events" column
filtered_data = data[data['Events'].str.contains("Input2\\*2\\*1", na=False)]

# Step 2: Calculate the time difference between consecutive rows using the "TimeStampAdjusted" column
filtered_data['TimeDifference'] = filtered_data['TimeStampAdjusted'].diff()

# Step 3: Identify trains of events with <300ms within a train and >=300ms between trains
filtered_data['TrainID'] = (filtered_data['TimeDifference'] >= 0.300).cumsum()

# Calculate the size of each train
train_sizes = filtered_data.groupby('TrainID').size().reset_index(name='TrainSize')

# Step 4: Filter for trains with 1 to 4 events
valid_trains = train_sizes[train_sizes['TrainSize'].between(1, 4)]

# Identify trains with exactly 4 events
four_pulse_trains = valid_trains[valid_trains['TrainSize'] == 4]['TrainID']

# Split the 4-pulse trains into first 3 events and last event
modified_train_starts = []
for train_id in four_pulse_trains:
    train_events = filtered_data[filtered_data['TrainID'] == train_id]
    first_3_pulse_event = train_events.iloc[0:3].iloc[0]
    modified_train_starts.append({'TimeStampAdjusted': first_3_pulse_event['TimeStampAdjusted'], 'TrainSize': 3})
    last_1_pulse_event = train_events.iloc[-1]
    modified_train_starts.append({'TimeStampAdjusted': last_1_pulse_event['TimeStampAdjusted'], 'TrainSize': 1})

# Remove the original 4-pulse trains from the main result
filtered_valid_trains = valid_trains[valid_trains['TrainSize'] != 4]
modified_train_starts_df = pd.DataFrame(modified_train_starts)

# Combine the modified entries with other valid trains
start_times_df = filtered_data.merge(filtered_valid_trains, on='TrainID')
start_times_df = start_times_df.groupby('TrainID').first()[['TimeStampAdjusted', 'TrainSize']]
final_result = pd.concat([start_times_df.reset_index(), modified_train_starts_df])

# Sort by TimeStampAdjusted
final_result_sorted = final_result.sort_values(by='TimeStampAdjusted').reset_index(drop=True)

#%% Format pulse trains of 2, 3, or 4 as a table
# Extract train times based on the adjusted criteria
left_poke_times = final_result_sorted[final_result_sorted['TrainSize'] == 2]['TimeStampAdjusted'].tolist()
pellet_drop_times = final_result_sorted[final_result_sorted['TrainSize'] == 3]['TimeStampAdjusted'].tolist()
pellet_retrieval_times = final_result_sorted[final_result_sorted['TrainSize'] == 1]['TimeStampAdjusted'].tolist()

# Determine the maximum length among the three lists
max_len = max(len(left_poke_times), len(pellet_drop_times), len(pellet_retrieval_times))

# Ensure all lists have the same length by padding with NaN
left_poke_times.extend([float('nan')] * (max_len - len(left_poke_times)))
pellet_drop_times.extend([float('nan')] * (max_len - len(pellet_drop_times)))
pellet_retrieval_times.extend([float('nan')] * (max_len - len(pellet_retrieval_times)))

# Create a DataFrame with the aligned data
aligned_df = pd.DataFrame({
    'LeftPoke': left_poke_times,
    'PelletDrop': pellet_drop_times,
    'PelletRetrieval': pellet_retrieval_times
})


