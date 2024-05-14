import pandas as pd
import numpy as np

import os
import argparse
import glob

import matplotlib
import matplotlib.pyplot as plt
from datetime import time as dt_time

import matplotlib.dates as mdates
from datetime import datetime, timedelta


parser = argparse.ArgumentParser(description="Parse user input for the experiment details.")

parser.add_argument('directory', 
                    type=str, 
                    help='Enter name of the directory that contains your .txt data files.'
                    ' Produced figures will be placed in the results directory.')

parser.add_argument('start_time', 
                    type=str, 
                    help='Enter the start time in the format "YYYY-MM-DD HH:MM:SS". Be sure to use double-quotes')

parser.add_argument('end_time', 
                    type=str, 
                    help='Enter the end time in the format "YYYY-MM-DD HH:MM:SS". Be sure to use double-quotes.')

parser.add_argument('--DD_start_date', 
                    metavar='DD_start_date', 
                    type=str, 
                    nargs='?',
                    default='9999-12-30', # This is a placeholder date that ideally will be replaced by the user
                    help='The date in YYYY-MM-DD format (optional) provides the date for the end of LD and the start of DD')

parser.add_argument('--morning_ramp',
                     metavar='Morning ramp start time', 
                     type=str,
                       nargs='?', 
                       default='06:00', 
                       help='The time in HH:MM format provides light onset for the morning ramp')

parser.add_argument('--evening_ramp', 
                    metavar='Evening ramp start time', 
                    type=str, nargs='?', 
                    default='18:00', # You don't want to leave these default, honestly.
                    help='The time in HH:MM format provides light down-ramp for the evening ramp')

parser.add_argument('--night_start', 
                    metavar='Night start time', 
                    type=str, 
                    nargs='?', 
                    default='21:00', 
                    help='The time in HH:MM format provides the time when night (total dark) begins')

parser.add_argument('--ramp_duration', 
                    metavar='Duration in hours for the ramp', 
                    type=float, 
                    nargs='?', 
                    default=3.0, 
                    help='Duration (in hours) of the light ramps')

parser.add_argument('--exclude_animals', 
                    action='store_true', 
                    help='Specify "True" or "False" if you want to remove animals.')


args = parser.parse_args()

###################################################
################ HANDLING USER ARGUMENTS ##########
###################################################

start_slice = args.start_time # For taking the starting point when slicing the data later
end_slice = args.end_time

# DEFINE LD PERIODS FOR DRAWING LD BARS

# These are the datetime.time objects that define the start of the morning and evening ramps
morning_ramp_start = datetime.strptime(args.morning_ramp, '%H:%M').time()
evening_ramp_start = datetime.strptime(args.evening_ramp, '%H:%M').time()

evening_ramp_end = datetime.strptime(args.night_start, '%H:%M').time()

ramp_time = pd.Timedelta(hours=args.ramp_duration)  

# The ramp end date is when DD (total dark) begins.
ramp_end_date = datetime.strptime(args.DD_start_date, '%Y-%m-%d')

# calculate number of days in our slice
datetime_start = pd.to_datetime(start_slice)
datetime_end = pd.to_datetime(end_slice)

delta_datetime = datetime_end - datetime_start
num_days = delta_datetime.days

print("\n\n\n")
print("Running the analyze.py script, written by Kenneth O'Dell Jr.")
print("Today's date is: ", datetime.now())
print(f"You have sliced a total of {num_days} days")

# Create directories, if they don't exist.
dir_path = "../" + args.directory
cleaned_data_path = dir_path + "/cleaned_data_all_animals"
result_path = dir_path + "/results_pre_sliced_all_animals"
sliced_path = dir_path + "/sliced_data_all_animals_" + str(num_days) + "_days_" + start_slice + "_to_" + end_slice
exclude_animals_path = dir_path + "/excluded_animals"

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

# Directory for data and figures with excluded animals
if not os.path.exists(exclude_animals_path):
    os.makedirs(exclude_animals_path)
    print("Created exclude_animals directory")
else:
    print("OK. exclude_animals exists")

###################################################
################ FUNCTION DEFINITIONS #############
###################################################

# Function for drawing LD bars in graphs
def drawLD(minute_ticks, ax1):
    for minute_tick in minute_ticks:
            if minute_tick.date() <= ramp_end_date.date(): # If the date is less than the ramp_end_date
                
                # First two conditionals draw the twilight periods
                if minute_tick == datetime.combine(minute_tick.date(), morning_ramp_start): # The morning ramp starts here
                    ax1.axvspan(minute_tick, minute_tick + ramp_time, facecolor='gray', alpha=0.2)
                
                if minute_tick == datetime.combine(minute_tick.date(), evening_ramp_start): # The evening ramp starts here
                    ax1.axvspan(minute_tick, minute_tick + ramp_time, facecolor='gray', alpha=0.2)

                # This draws the night bars. Note that I create a new datetime object with the date and the evening_ramp_end time.
                # This is because we must compare times within the same date. The user only enters time, however.

                # Case 1: The evening_ramp_end is less than the morning_ramp_start
                if datetime.combine(minute_tick.date(), evening_ramp_end) < datetime.combine(minute_tick.date(), morning_ramp_start):
                    if (minute_tick > datetime.combine(minute_tick.date(), evening_ramp_end) and (minute_tick < datetime.combine(minute_tick.date(), morning_ramp_start))):
                        ax1.axvspan(minute_tick, minute_tick + pd.Timedelta(minutes=1), facecolor='black', alpha=0.3)  

                # Case 2: The evening_ramp_end is greater than the morning_ramp_start
                elif datetime.combine(minute_tick.date(), evening_ramp_end) > datetime.combine(minute_tick.date(), morning_ramp_start):
                    if (minute_tick > datetime.combine(minute_tick.date(), evening_ramp_end)):
                        ax1.axvspan(minute_tick, minute_tick + pd.Timedelta(minutes=1), facecolor='black', alpha=0.3)
                # Section of night BEFORE the morning ramp starts.
                    if (minute_tick < datetime.combine(minute_tick.date(), morning_ramp_start)):
                        ax1.axvspan(minute_tick, minute_tick + pd.Timedelta(minutes=1), facecolor='black', alpha=0.3)
                
                # Case 3: They are equal
                elif datetime.combine(minute_tick.date(), evening_ramp_end) == datetime.combine(minute_tick.date(), morning_ramp_start):
                    # Do nothing
                    pass
            else:
                # If the date is greater than the ramp_end_date, then we are in the DD period.
                ax1.axvspan(minute_tick, minute_tick + pd.Timedelta(minutes=1), facecolor='black', alpha=0.3)

def plot_raw(data: pd.DataFrame, i: int, monitor_name: str = "Monitor"):

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
    plt.title(monitor_name + " Raw Locomotor Activity")
    plt.xlabel("Local Time")
    plt.ylabel("Counts per minute")

    plt.grid(False)
    return plt

# Create a figure and a grid of subplots
def subplots_raw(data: pd.DataFrame,
                j: int,
                days: int = 1,
                monitor_name: str = "Monitor"):

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

    fig.suptitle(monitor_name + ' Raw Locomotor Activity Individuals', fontsize = 20) 
    plt.tight_layout()
    return plt

def plot_raw_sliced(data: pd.DataFrame, 
                    i: int, 
                    start_slice: str,
                    end_slice: str,
                    monitor_name: str = ""):

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

    # Minute ticks, so we have minute precision in specifying the light and dark bars
    minute_ticks = pd.date_range(start=start_time, end=end_time, freq='1min')


    ### DRAW LIGHT AND DARK BARS ###
    drawLD(minute_ticks, ax1)
    ### END OF LIGHT AND DARK BARS ###

    # Set titles and axes names
    ax1.set_title(monitor_name + ' Raw Locomotor Activity ' + str(num_days) + "_days_" + start_slice + "_to_" + end_slice, fontsize = 16)
    ax1.set_ylabel('Counts per minute', fontsize = 14)
    ax1.set_xlabel('Local time', fontsize = 14)

    plt.tight_layout()
    return plt

# Create a figure and a grid of subplots
def subplots_raw_sliced(data: pd.DataFrame, 
                        j: int, 
                        start_time: str, 
                        end_time: str, 
                        days: int = 1, 
                        monitor_name: str = ""):

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

        # Minute ticks, so we have minute precision in specifying the light and dark bars
        minute_ticks = pd.date_range(start=start_time, end=end_time, freq='1min')


        ### DRAW LIGHT AND DARK BARS ###
        drawLD(minute_ticks, axs[i])
        ### END OF LIGHT AND DARK BARS ###

    fig.suptitle(monitor_name + ' Raw Locomotor Activity ' + str(num_days) + "_days_" + start_slice + "_to_" + end_slice, fontsize = 16)
    plt.tight_layout()
    return plt
   
###################################################
################ MAIN FUNCTION ####################
###################################################

monitor_files = []          # Holds the Pandas DataFrame objects
monitor_file_names = []     # Holds the file paths of the monitor files
just_file_names = []        # Holds the file names without the path

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

#################
# If animals are to be excluded, we do so here!
#################

if args.exclude_animals:
    # ADD CODE HERE!!!
    # EXCLUDE ANIMALS
    # UPDATE monitor_files list
    # Basically run the same code as below, but with the exclusion of the animals you want to exclude.
    print("FOR TESTING - YOU ARE WANTING TO EXCLUDE ANIMALS, YES?!")

#################
# Else, plot all of the individuals!
#################

else:

    #################
    # Plot the entire raw data
    #################

    # Iterate through monitors and plot raw data
    for i, monitor in enumerate(monitor_files):

        plot_raw(monitor,
                 i,
                 just_file_names[i].replace('.txt', '')).savefig(result_path + '/fig_01/' + just_file_names[i].replace('.txt', '') + "_raw_data_fig_01.png")
        
        print(f"Saved raw data plot to {result_path + '/fig_01/' + just_file_names[i].replace('.txt', '') + '_raw_data_fig1.png'}")


    #################
    # Subplots for each animal
    ################
   
    for j, monitor in enumerate(monitor_files):
        
        subplots_raw(monitor,
                     j,
                     3, # Intervals of days for the x-axis
                     just_file_names[j].replace('.txt', '')).savefig(result_path + '/fig_02/' + just_file_names[j].replace('.txt', '') + "_raw_individuals_fig_02.png")
        
        print(f"Saved raw individuals data plot to {result_path + '/fig_02/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_fig_02.png'}")


    #################
    # Now we slice the data according to a date range
    #################

    # Slice our data
    monitor_slices = []
    for i, monitor in enumerate(monitor_files):
        monitor_slice = monitor[(monitor.index >= start_slice) & (monitor.index <= end_slice)]
        monitor_slices.append(monitor_slice)
        print(f"Sliced data for {just_file_names[i]}")
        print(f"Saved sliced data to {sliced_path + '/sliced_data' + f'/sliced_{just_file_names[i]}' }")
        monitor_slice.to_csv(sliced_path + '/sliced_data' + f"/sliced_{just_file_names[i]}", sep='\t')

    #################
    # Plot the SLICED raw data, show hour ticks...
    #################

    for i, monitor in enumerate(monitor_slices):

        plot_raw_sliced(monitor,
                        i,
                        start_slice,
                        end_slice,
                        just_file_names[i].replace('.txt', '')
                        ).savefig(sliced_path + '/fig_03/' + just_file_names[i].replace('.txt', '') + "_raw_sliced_data_fig_03.png")
        
        print(f"Saved raw data plot to {sliced_path + '/fig_03/' + just_file_names[i].replace('.txt', '') + '_raw_sliced_data_fig_03.png'}")


    #################
    # Subplots of SLICED raw data for each animal
    ################
 
    for j, slice in enumerate(monitor_slices):

        subplots_raw_sliced(slice,
                            j,
                            start_slice,
                            end_slice,
                            1, # Intervals of days for the x-axis
                            just_file_names[j].replace('.txt', '')
                            ).savefig(sliced_path + '/fig_04/' + just_file_names[j].replace('.txt', '') + "_raw_individuals_sliced_fig_04.png")
        
        print(f"Saved raw individuals sliced data plot to {sliced_path + '/fig_04/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_sliced_fig_04.png'}")

    #################
    # Calculate running average (in minutes) for each animal column
    ################


    ################
    # Calculate avg and std for each animal column
    ################