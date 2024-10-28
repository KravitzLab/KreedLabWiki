#import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit, minimize
from scipy.stats import linregress
from scipy.signal import butter, filtfilt

#%%
folder = r"C:\Users\kravitza.PSYCH\Downloads"
filename = folder + r"\M402_banditRT_wcenter_102220242024-10-22T14_37_56.csv"
dfraw = pd.read_csv(filename, header=0)
dfraw['TimeStampAdjusted'] = dfraw['Time'] - dfraw['Time'][0] 
dfraw.rename(columns={'Isosbestic': 'UV', 'Fluorescence': 'Fluorescence'}, inplace=True)
dfraw = dfraw.loc[:, ~dfraw.columns.str.contains('^Unnamed')]

#%%
#create a new copy to work with (we can go back to this step if we need to without re-importing the .csv file)
df = dfraw.copy()

#discard first 6000 samples (~200 =s)
df = df.copy()[6000:]

# Initialize a figure with 2 subplots, arranged vertically
fig, axs = plt.subplots(2, 1, figsize=(10, 6))  # 'figsize' is optional, adjust it as needed

# First subplot for 'Fluorescence'
axs[0].plot(df['TimeStampAdjusted'], df['Fluorescence'], 'g', label='Fluorescence')
axs[0].set_title('Fluorescence Signal')  # Set title for the first subplot
axs[0].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[0].set_ylabel('Signal (AU)')  # Set y-axis label for the first subplot
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)

# Second subplot for 'UV'
axs[1].plot(df['TimeStampAdjusted'], df['UV'], 'b', label='UV')
axs[1].set_title('UV Signal')  # Set title for the second subplot
axs[1].set_xlabel('Time (seconds)')  # Set x-axis label for the second subplot
axs[1].set_ylabel('Signal (AU)')  # Set y-axis label for the second subplot
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)

# Adjust layout to prevent overlap
plt.tight_layout()

#%%
def double_exponential(t, const, amp_fast, amp_slow, tau_slow, tau_multiplier):
    '''Compute a double exponential function with constant offset.
    Parameters:
    t       : Time vector in seconds.
    const   : Amplitude of the constant offset.
    amp_fast: Amplitude of the fast component.
    amp_slow: Amplitude of the slow component.
    tau_slow: Time constant of slow component in seconds.
    tau_multiplier: Time constant of fast component relative to slow.
    '''
    tau_fast = tau_slow*tau_multiplier
    return const+amp_slow*np.exp(-t/tau_slow)+amp_fast*np.exp(-t/tau_fast)

#Fit curve to Fluorescence signal
max_sig = np.max(df['Fluorescence'])
#set boundaries for how much of the traces to use for curve fitting
bounds = ([0      , 0      , 0      , 0  , 0],
          [max_sig, max_sig, max_sig, 36000, 1])
inital_params = [max_sig/2, max_sig/4, max_sig/4, 7500, 0.1]
time_seconds = df['TimeStampAdjusted']
raw_Fluorescence = df['Fluorescence']
Fluorescence_params, param_cov = curve_fit(double_exponential, time_seconds, raw_Fluorescence,
                                  p0=inital_params, bounds=bounds, maxfev=1000)
Fluorescence_expfit = double_exponential(time_seconds, *Fluorescence_params)

#Fit curve to iso signal
max_sig = np.max(df['UV'])
#set boundaries for how much of the traces to use for curve fitting
bounds = ([0      , 0      , 0      , 0  , 0],
          [max_sig, max_sig, max_sig, 36000, 1])
inital_params = [max_sig/2, max_sig/4, max_sig/4, 7500, 0.1]
raw_iso = df['UV']
iso_params, param_cov = curve_fit(double_exponential, time_seconds, raw_iso,
                                  p0=inital_params, bounds=bounds, maxfev=1000)
iso_expfit = double_exponential(time_seconds, *iso_params)

# Initialize a figure with 2 subplots, arranged vertically
fig, axs = plt.subplots(2, 1, figsize=(10, 6))  # 'figsize' is optional, adjust it as needed

# First subplot for 'Fluorescence'
axs[0].plot(time_seconds, raw_Fluorescence, 'g', label='Fluorescence')
axs[0].plot(time_seconds, Fluorescence_expfit, 'r', label='Fluorescence')
axs[0].set_title('Fluorescence Signal (AU)')  # Set title for the first subplot
axs[0].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[0].set_ylabel('Signal')  # Set y-axis label for the first subplot
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)

# First subplot for 'Fluorescence'
axs[1].plot(time_seconds, raw_iso, 'b', label='Iso')
axs[1].plot(time_seconds, iso_expfit, 'r', label='Iso')
axs[1].set_title('Isosbestic Signal (AU)')  # Set title for the first subplot
axs[1].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[1].set_ylabel('Signal')  # Set y-axis label for the first subplot
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)

# Adjust layout to prevent overlap
plt.tight_layout()
#%%
Fluorescence_debleached = raw_Fluorescence - Fluorescence_expfit
iso_debleached = raw_iso - iso_expfit

# Initialize a figure with 2 subplots, arranged vertically
fig, axs = plt.subplots(2, 1, figsize=(10, 6))  # 'figsize' is optional, adjust it as needed

# First subplot for 'Fluorescence'
axs[0].plot(time_seconds, Fluorescence_debleached, 'g', label='Fluorescence')
axs[0].set_title('Fluorescence Signal')  # Set title for the first subplot
axs[0].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[0].set_ylabel('Signal (AU)')  # Set y-axis label for the first subplot
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)

# Second subplot for 'UV'
axs[1].plot(time_seconds, iso_debleached, 'b', label='UV')
axs[1].set_title('UV Signal')  # Set title for the second subplot
axs[1].set_xlabel('Time (seconds)')  # Set x-axis label for the second subplot
axs[1].set_ylabel('Signal (AU)')  # Set y-axis label for the second subplot
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)

# Adjust layout to prevent overlap
plt.tight_layout()

#%% motion correction by finding the best linear fit of the UV signal to the fluorescence signal
# then we will subtract the estimated motion from the fluorescence signal
# we will use the data that was bleaching correct first using the double exponential fit
slope, intercept, r_value, p_value, std_err = linregress(x=Fluorescence_debleached, y=iso_debleached)
plt.scatter(Fluorescence_debleached[::5], iso_debleached[::5],alpha=0.1, marker='.', color='b', label = "raw")
x = np.array(plt.xlim())
plt.plot(x, intercept+slope*x, color='b', linestyle = "--")
plt.ylabel('debleached UV')
plt.xlabel('debleached Fluorescence')
plt.title('UV - Fluorescence correlation.')

# Remove top and right spines
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

#%% Compute the estimated motion of the fluorescence signal and subtract to get motion correct signal
Fitted_UV = intercept + slope * iso_debleached
Fluorescence_corrected = Fluorescence_debleached - Fitted_UV

plt.scatter(Fluorescence_debleached[::5], Fitted_UV[::5], alpha=0.1, marker='.', color='r', label = "scaled")
x = np.array(plt.xlim())
plt.ylabel('debleached UV')
plt.xlabel('debleached Fluorescence')
plt.title('UV - Fluorescence correlation.')

plt.legend(frameon=False)

# Remove top and right spines
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)


#%%
# Create a figure with 3 subplots, arranged vertically
fig, axs = plt.subplots(3, 1, figsize=(10, 6))  # 'figsize' is optional, adjust as needed

# First subplot for 'Fluorescence debleached'
axs[0].plot(time_seconds, Fluorescence_debleached, label='Fluorescence debleached')
axs[0].set_title('Fluorescence Debleached')  # Set title for the first subplot
axs[0].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[0].set_ylabel('Signal (AU)')  # Set y-axis label for the first subplot
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)

# Third subplot for 'estimated motion'
axs[1].plot(time_seconds, Fitted_UV, 'gray', label='Estimated Motion')
axs[1].set_title('Estimated Motion')  # Set title for the third subplot
axs[1].set_xlabel('Time (seconds)')  # Set x-axis label for the third subplot
axs[1].set_ylabel('Signal (AU)')  # Set y-axis label for the third subplot
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)

# Second subplot for 'fluorsence motion corrected'
axs[2].plot(time_seconds, Fluorescence_corrected, 'g', label='Fluorescence motion corrected')
axs[2].set_title('Fluorescence Motion Corrected')  # Set title for the second subplot
axs[2].set_xlabel('Time (seconds)')  # Set x-axis label for the second subplot
axs[2].set_ylabel('Signal (AU)')  # Set y-axis label for the second subplot
axs[2].spines['right'].set_visible(False)
axs[2].spines['top'].set_visible(False)

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()

#%%
# Assuming Fluorescence_corrected is a pandas Series
# Sample rate and desired cutoff frequencies (in Hz).
fs = 50  # Adjust to your signal's actual sample rate
lowcut = 0.005
highcut = 5

# Design the Butterworth band-pass filter
def butter_bandpass(lowcut, highcut, fs, order=3):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=3):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data.values)
    return y

# Apply the filter to your data.
Fluorescence_corrected_filtered = butter_bandpass_filter(Fluorescence_corrected, lowcut, highcut, fs, order=3)

fig = plt.figure(figsize=(10, 6))  # You can adjust the overall figure size as needed

# First row, first subplot: Original Data (full series)
# Spanning two columns for double width
ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)
ax1.plot(time_seconds, Fluorescence_corrected)
ax1.set_title('Original Data (All)')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.set_ylabel('Signal (AU)')  # Set y-axis label for the third subplot

# First row, second subplot: Original Data (60s-120s)
# Occupying one column
ax2 = plt.subplot2grid((2, 3), (0, 2))
ax2.plot(time_seconds[3000:6000], Fluorescence_corrected[3000:6000])
ax2.set_title('Original Data (60s-120s)')
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)

# Second row, first subplot: Filtered Data (full series)
# Spanning two columns for double width
ax3 = plt.subplot2grid((2, 3), (1, 0), colspan=2)
ax3.plot(time_seconds, Fluorescence_corrected_filtered, color="darkred", alpha=0.7)
ax3.set_title('Filtered Data: ' + str(lowcut) + 'Hz to ' + str(highcut) + 'Hz')
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_ylabel('Signal (AU)')  # Set y-axis label for the third subplot

# Second row, second subplot: Filtered Data (60s-120s)
# Occupying one column
ax4 = plt.subplot2grid((2, 3), (1, 2))
ax4.plot(time_seconds[3000:6000], Fluorescence_corrected_filtered[3000:6000], color="darkred", alpha=0.7)
ax4.set_title('Filtered Data (60s-120s)')
ax4.spines['right'].set_visible(False)
ax4.spines['top'].set_visible(False)

plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()

#%%
df["Fluorescence_Corrected"] = Fluorescence_corrected_filtered

# Calculate the mean and standard deviation of the 'Fluorescence_Corrected' column
mean = df['Fluorescence_Corrected'].mean()
std_dev = df['Fluorescence_Corrected'].std()

# Calculate z-scores for the 'Fluorescence_Corrected' column
df['Fluorescence_Corrected_Z'] = (df['Fluorescence_Corrected'] - mean) / std_dev

# Create a figure with 3 subplots, arranged vertically
fig, axs = plt.subplots(2, 1, figsize=(8, 4))  # 'figsize' is optional, adjust as needed

# First subplot for 'Fluorescence Z-Scored'
axs[0].plot(df['Time'], df['Fluorescence_Corrected'], label='Fluorescence Corrected')
axs[0].set_title('Fluorescence Corrected')  # Set title for the first subplot
axs[0].set_xlabel('Time (seconds)')  # Set x-axis label for the first subplot
axs[0].set_ylabel('Signal (AU)')  # Set y-axis label for the first subplot
axs[0].spines['right'].set_visible(False)
axs[0].spines['top'].set_visible(False)

# Third subplot for 'estimated motion'
axs[1].plot(df['Time'], df['Fluorescence_Corrected_Z'], 'gray', label='Fluorescence Z Scored')
axs[1].set_title('Fluorescence Z Scored')  # Set title for the third subplot
axs[1].set_xlabel('Time (seconds)')  # Set x-axis label for the third subplot
axs[1].set_ylabel('Z Score')  # Set y-axis label for the third subplot
axs[1].spines['right'].set_visible(False)
axs[1].spines['top'].set_visible(False)

plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()

#%%
# Generate a new filename with '_processed' appended before the file extension
new_filename = filename.rsplit('.', 1)[0] + '_processed.' + filename.rsplit('.', 1)[1]

# Save the processed DataFrame back to a CSV
df.to_csv(new_filename, index=False)
print(f"Processed file saved as '{new_filename}'.")    

#%%
import pandas as pd

# Copy the dataset for processing
data = df.copy()

# Step 1: Identify transitions from False to True in the "Reward" column
data['Reward_Transition'] = (data['Reward'] & ~data['Reward'].shift(1).fillna(False))

# Step 2: Filter rows where a transition occurred
filtered_data = data[data['Reward_Transition']]

# Step 3: Calculate time differences between consecutive transitions
filtered_data['TimeDifference'] = filtered_data['TimeStampAdjusted'].diff()

# Step 4: Identify trains of events with <300ms within a train and >=300ms between trains
filtered_data['TrainID'] = (filtered_data['TimeDifference'] >= 0.300).cumsum()

# Calculate train sizes and identify valid pulse trains with 1 to 7 pulses
train_sizes = filtered_data.groupby('TrainID').size().reset_index(name='TrainSize')
valid_trains = train_sizes[train_sizes['TrainSize'].between(1, 7)]

# Identify trains with exactly 7 events
seven_pulse_trains = valid_trains[valid_trains['TrainSize'] == 7]['TrainID']

# Step 5: Split the 7-pulse trains into the first 6 events and the last 1 event
modified_train_starts = []
for train_id in seven_pulse_trains:
    train_events = filtered_data[filtered_data['TrainID'] == train_id]
    first_6_pulse_event = train_events.iloc[0:6].iloc[0]
    modified_train_starts.append({'TimeStampAdjusted': first_6_pulse_event['TimeStampAdjusted'], 'TrainSize': 6})
    last_1_pulse_event = train_events.iloc[-1]
    modified_train_starts.append({'TimeStampAdjusted': last_1_pulse_event['TimeStampAdjusted'], 'TrainSize': 1})

# Remove the original 7-pulse trains from the main result
filtered_valid_trains = valid_trains[valid_trains['TrainSize'] != 7]
modified_train_starts_df = pd.DataFrame(modified_train_starts)

# Combine the modified entries with other valid trains
start_times_df = filtered_data.merge(filtered_valid_trains, on='TrainID')
start_times_df = start_times_df.groupby('TrainID').first()[['TimeStampAdjusted', 'TrainSize']]

# Step 6: Concatenate the modified entries with the filtered valid trains
final_result = pd.concat([start_times_df.reset_index(), modified_train_starts_df])

# Sort by TimeStampAdjusted to maintain chronological order
final_result_sorted = final_result.sort_values(by='TimeStampAdjusted').reset_index(drop=True)

# Display the final sorted result
final_result_sorted

#%%
# Let's proceed with the task to restructure the sorted results into a wide format based on the provided mapping.
# Load the final sorted result first and transform it according to the provided pulse categories.

# Map pulse categories based on the provided chart

pulse_mapping = {
    1: 'Center',
    2: 'Left',
    3: 'Right',
    4: 'Rewarded',
    5: 'Unrewarded',
    6: 'Pellet drop',
    7: 'Pellet Retrieval'
}

final_result_sorted['Category'] = final_result_sorted['TrainSize'].map(pulse_mapping)

# Convert to wide format, each category as a column with respective timestamps
aligned_df = final_result_sorted.pivot(columns='Category', values='TimeStampAdjusted')