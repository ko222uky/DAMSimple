import pandas as pd
import numpy as np

import os
import argparse
import glob

import matplotlib
import matplotlib.pyplot as plt


import matplotlib.dates as mdates
from datetime import datetime, timedelta


parser = argparse.ArgumentParser(description="Parse user input for the experiment directory name.")

parser.add_argument('directory', type=str, help='Enter name of the directory that contains your .txt data files.'
                    ' Produced figures will be placed in the results directory.')

parser.add_argument('start_time', type=str, help='Enter the start time in the format "YYYY-MM-DD HH:MM:SS". Be sure to use double-quotes')

parser.add_argument('end_time', type=str, help='Enter the end time in the format "YYYY-MM-DD HH:MM:SS". Be sure to use double-quotes.')

args = parser.parse_args()

# FROM ARGUMENTS
dir_path = "../" + args.directory
cleaned_data_path = dir_path + "/cleaned_data"
result_path = dir_path + "/results_pre_sliced"

start_slice = args.start_time
end_slice = args.end_time

# calculate number of days in our slice
datetime_start = pd.to_datetime(start_slice)
datetime_end = pd.to_datetime(end_slice)

delta_datetime = datetime_end - datetime_start
num_days = delta_datetime.days
print("\n\n\n")
print("Running the analyze.py script, written by Kenneth O'Dell Jr.")
print("Today's date is: ", datetime.now())
print(f"You have sliced a total of {num_days} days")

sliced_path = dir_path + "/sliced_data_" + str(num_days) + "_days_" + start_slice + "_to_" + end_slice

# Create directories, if they don't exist.
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    print("Directory created: ", dir_path)
else:
    print("OK. Directory exists: ", dir_path)

if not os.path.exists(cleaned_data_path):
    os.makedirs(cleaned_data_path)
    print("Cleaned data directory created: ", cleaned_data_path)
else:
    print("OK. Cleaned data directory exists: ", cleaned_data_path)

if not os.path.exists(result_path):
    os.makedirs(result_path)
    print("Results created: ", result_path)
else:
    print("OK. Results exists: ", result_path)

# Sliced data range
if not os.path.exists(sliced_path):
    os.makedirs(sliced_path)
    print("Sliced data directory created: ", sliced_path)
else:
    print("OK. Sliced data directory exists: ", sliced_path)
# Sliced data in the sliced directory
if not os.path.exists(sliced_path + '/sliced_data'):
    os.makedirs(sliced_path + '/sliced_data')
    print("Sliced data directory created: ", sliced_path + '/sliced_data')
else:
    print("OK. Sliced data directory exists: ", sliced_path + '/sliced_data')

# figure directories
if not os.path.exists(result_path + '/fig_01'):
    os.makedirs(result_path + '/fig_01')
    print("Created fig_01 directory")
else:
    print("OK. fig_01 exists")

if not os.path.exists(result_path + '/fig_02'):
    os.makedirs(result_path + '/fig_02')
    print("Created fig_02 directory")
else:
    print("OK. fig_02 exists")

if not os.path.exists(sliced_path + '/fig_03'):
    os.makedirs(sliced_path + '/fig_03')
    print("Created fig_03 directory")
else:
    print("OK. fig_03 exists")

if not os.path.exists(sliced_path + '/fig_04'):
    os.makedirs(sliced_path + '/fig_04')
    print("Created fig_04 directory")
else:
    print("OK. fig_04 exists")
#
#
# Load the data
monitor_files = []
monitor_file_names = []
just_file_names = []   

for i, txt in enumerate(glob.glob(os.path.join(dir_path, '*txt'))):
    monitor = pd.read_csv(txt, sep='\t', header=None)
    print(f"Loaded monitor data from {txt}")
    monitor_files.append(monitor)
    monitor_file_names.append(txt)

    just_file_names.append(monitor_file_names[i][len(dir_path)+1:])

# Check to see that our monitor files are correct
for monitor in monitor_files:
    monitor.info()

# Obtain datetimes for each monitor
# The resulting format should be compatible withn Rethomics in R.
time_col = []
date_col = []
datetime_index = []

for i, monitor in enumerate(monitor_files):
    time_col.append(monitor.iloc[:,2])
    date_col.append(monitor.iloc[:,1])
    concat_datetime = date_col[i] + " " + time_col[i]
    datetime_index.append(pd.to_datetime(concat_datetime, format='%d %b %y %H:%M:%S'))
    print(f"Converted date and time columns to datetime for {monitor_file_names[i]}")

# New column names for the animals
column_nums = pd.Series(range(1, 33)) # For monitors that hold 32 animals
animal_nums = "animal_" + column_nums.astype(str)


# Clean the data by grabbing only activity columns
for i, monitor in enumerate(monitor_files):
    activity = monitor.iloc[: , 10:42]
    activity.index = datetime_index[i]
    activity.columns = animal_nums
    
    monitor_files[i] = activity # update the monitor df in our list

    activity.to_csv(cleaned_data_path + f"/cleaned_{just_file_names[i]}", sep='\t')
    print(f"Cleaned data for {just_file_names[i]}")
    print(f"Saved cleaned data to {cleaned_data_path + "/cleaned_" + just_file_names[i]}")


# Plot the entire raw data
# 
#
#
# Define function first...
def plot_raw(data: pd.DataFrame, i: int):

    data.plot(kind='line', legend=False, figsize = (12, 8)) # figsize is in inches

    # Create DataFormatter for the x-axis
    xformatter = mdates.DateFormatter('%Y-%m-%d')

    # get the current axes
    axs = plt.gca()

    # set the x-axis formatter!
    axs.xaxis.set_major_formatter(xformatter)

    axs.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Set major tick every 3 days
    axs.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %y'))  # Format the datetime as 'HH:MM', instead of showing the whole dt
    plt.tick_params('x', labelrotation=90)
   
    # Customize the aesthetics
    plt.title("Raw Locomotor Activity")
    plt.xlabel("Local Time")
    plt.ylabel("Counts per minute")

    plt.grid(False)

    plt.savefig(result_path + '/fig_01/' + just_file_names[i].replace('.txt', '') + "_raw_data_fig_01.png")
    print(f"Saved raw data plot to {result_path + '/fig_01/' + just_file_names[i].replace('.txt', '') + '_raw_data_fig1.png'}")

# Iterate through monitors and plot raw data
for i, monitor in enumerate(monitor_files):
    plot_raw(monitor, i)



# Subplots for each animal
# 
#
#
# Create a figure and a grid of subplots
def subplots_raw(data: pd.DataFrame, j: int, days: int = 1):

    # Grid dimensions for our main figure that holds our axs subplots
    nrows = 4
    ncols = 8

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(30,15)) # nrows = 4 and ncols = 8 for a 4x8 grid of subplots

    # We now have a 4x8 matrix of Axes objects corresponding to our subplot grid.
    # To make this easier to iterate through, I can flatten it into a 1D array.
    axs = axs.flatten()

    for i, (name, series) in enumerate(data.items()): # items() returns (column names, Series) pairs that can be iterated over
        axs[i].plot(series.index, series.values) # Plots index on x-axis, and series' values on y-axis
        axs[i].set_title(name)
        
        # Aesthetics

        # Reformat the x-axis labels using datetime
        axs[i].xaxis.set_major_locator(mdates.DayLocator(interval=days))  # Set major tick every 3 days
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Format the datetime as 'HH:MM', instead of showing the whole dt

        axs[i].tick_params('x', labelrotation=90)
        axs[i].set_ylabel('counts/min', fontsize = 12)
        axs[i].set_xlabel('date', fontsize = 8)

        
    plt.tight_layout()

    plt.savefig(result_path + '/fig_02/' + just_file_names[j].replace('.txt', '') + "_raw_individuals_fig_02.png")
    print(f"Saved raw individuals data plot to {result_path + '/fig_02/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_fig_02.png'}")

for j, monitor in enumerate(monitor_files):
    subplots_raw(monitor, j, 3)

# Now we slice the data according to a date range
#
#
#
# Slice our data
monitor_slices = []
for i, monitor in enumerate(monitor_files):
    monitor_slice = monitor[(monitor.index >= start_slice) & (monitor.index <= end_slice)]
    monitor_slices.append(monitor_slice)
    print(f"Sliced data for {just_file_names[i]}")
    print(f"Saved sliced data to {sliced_path + '/sliced_data' + f'/sliced_{just_file_names[i]}' }")
    monitor_slice.to_csv(sliced_path + '/sliced_data' + f"/sliced_{just_file_names[i]}", sep='\t')


# Plot the SLICED raw data, show hour ticks...
#
#
#
def plot_raw_sliced(data: pd.DataFrame, i: int, start_slice: str, end_slice: str):

    # Assuming `data` is your DataFrame, we will create a plot with a single subplot.
    fig, ax1 = plt.subplots(figsize=(12, 12))
    # Thus, we only have one Axes object, and that's our entire dataframe.
    data.plot(ax=ax1, legend=False)

    # We need to do this MANUALLY
    # Manually set the x-axis limits to a smaller range
    start_time = pd.to_datetime(start_slice)  # replace 'your_start_time' with the actual start time. I use slice_start from earlier
    end_time = start_time + timedelta(hours=24*num_days)  # end time is start_time plus 240 hours later
    ax1.set_xlim([start_time, end_time]) # set the x-axis limit

    # This is the range for the dates and/or times. We go from start to end, in 6h intervals
    # This should actually be a list of datetime objects
    date_range = pd.date_range(start=start_time, end=end_time, freq='6h')

    # Set the x-axis ticks. There is one tick per interval, as defined in date_range
    ax1.set_xticks(date_range)

    # Generate the labels for the ticks
    # Converts each item in date_range to a string, with the format %H:%M drawn from the date time.
    labels = [time.strftime('%H:%M') for time in date_range]

    # Set the x-axis labels
    ax1.set_xticklabels(labels, rotation=90)  # Rotate the labels to make them more readable

    # Set titles and axes names
    ax1.set_title('Raw Locomotor Activity ' + str(num_days) + "_days_" + start_slice + "_to_" + end_slice, fontsize = 16)
    ax1.set_ylabel('Counts per minute', fontsize = 14)
    ax1.set_xlabel('Local time', fontsize = 14)

    plt.tight_layout()
    plt.savefig(sliced_path + '/fig_03/' + just_file_names[i].replace('.txt', '') + "_raw_sliced_data_fig_03.png")
    print(f"Saved raw data plot to {sliced_path + '/fig_03/' + just_file_names[i].replace('.txt', '') + '_raw_sliced_data_fig_03.png'}")


for i, monitor in enumerate(monitor_slices):
    plot_raw_sliced(monitor, i, start_slice, end_slice)


    # Subplots for each animal
# 
#
#
# Create a figure and a grid of subplots
def subplots_raw_sliced(data: pd.DataFrame, j: int, days: int = 1):

    # Grid dimensions for our main figure that holds our axs subplots
    nrows = 4
    ncols = 8

    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(30,15)) # nrows = 4 and ncols = 8 for a 4x8 grid of subplots

    # We now have a 4x8 matrix of Axes objects corresponding to our subplot grid.
    # To make this easier to iterate through, I can flatten it into a 1D array.
    axs = axs.flatten()

    for i, (name, series) in enumerate(data.items()): # items() returns (column names, Series) pairs that can be iterated over
        axs[i].plot(series.index, series.values) # Plots index on x-axis, and series' values on y-axis
        axs[i].set_title(name)
        
        # Aesthetics

        # Reformat the x-axis labels using datetime
        axs[i].xaxis.set_major_locator(mdates.DayLocator(interval=days))  # Set major tick every 3 days
        axs[i].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Format the datetime as 'HH:MM', instead of showing the whole dt

        axs[i].tick_params('x', labelrotation=90)
        axs[i].set_ylabel('counts/min', fontsize = 12)
        axs[i].set_xlabel('date', fontsize = 8)

        
    plt.tight_layout()

    plt.savefig(sliced_path + '/fig_04/' + just_file_names[j].replace('.txt', '') + "_raw_individuals_sliced_fig_04.png")
    print(f"Saved raw individuals sliced data plot to {sliced_path + '/fig_04/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_sliced_fig_04.png'}")

for j, slice in enumerate(monitor_slices):
    subplots_raw_sliced(slice, j)