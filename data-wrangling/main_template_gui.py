# tkinter for GUI
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import os
import glob
import sys # For outputting stoud to the text widget

import pandas as pd

#import matplotlib.dates as mdates
from datetime import datetime, timedelta
from datetime import time as dt_time

# My main analysis script. This is where all the fun stuff happens.
# Each figure that is produced is broken into tasks, e.g., plotRaw().
import main_template_analysis as t_analyze

# Class to redirect stdout to a text widget in the Gui
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, str):
        self.widget.insert(tk.END, str)
        self.widget.see(tk.END)

    def flush(self):
        pass  # This is needed for the file-like object.

# Global variables are defined with this via user entries in the appropriate fields.
def loadData():
    try:

        # Declare global variables
        global exclude_animals_var
        global start_slice
        global end_slice
        global morning_ramp_start
        global evening_ramp_start
        global evening_ramp_end
        global ramp_time
        global ramp_end_date

        global num_days

        global smoothing_window

        global dir_path
        global cleaned_data_path
        global result_path
        global sliced_path
        global exclude_animals_path
        global exclude_animals_path_data

        global monitor_files
        global monitor_file_names
        global just_file_names

        global smoothed_monitors

        # Define global variables from GUI fields
        exclude_animals = exclude_animals_var.get()
        
        start_slice = start_time_entry.get() # For taking the starting point when slicing the data later
        end_slice = end_time_entry.get() # For taking the ending point when slicing the data later

        # DEFINE LD PERIODS FOR DRAWING LD BARS
        # These are the datetime.time objects that define the start of the morning and evening ramps
        morning_ramp_start = datetime.strptime(morning_ramp_entry.get(), '%H:%M').time()
        evening_ramp_start = datetime.strptime(evening_ramp_entry.get(), '%H:%M').time()
        evening_ramp_end = datetime.strptime(night_start_entry.get(), '%H:%M').time()
        ramp_time = pd.Timedelta(hours=float(ramp_duration_entry.get()))  
        ramp_end_date = datetime.strptime(DD_start_date_entry.get(), '%Y-%m-%d')

        # calculate number of days in our slice
        datetime_start = pd.to_datetime(start_slice)
        datetime_end = pd.to_datetime(end_slice)
        delta_datetime = datetime_end - datetime_start
        num_days = delta_datetime.days

        # Running average
        smoothing_window = int(running_average_entry.get()) # The window for our running average, in minutes

        print("\n\n\n")
        print("Running the analyze.py script, written by Kenneth O'Dell Jr.")
        print("Today's date is: ", datetime.now())
        print(f"You have sliced a total of {num_days} days")

        # Create directories, if they don't exist.
        dir_path = "../" + directory_entry.get()
        cleaned_data_path = dir_path + "/cleaned_data_all_animals"
        result_path = dir_path + "/results_pre_sliced_all_animals"
        sliced_path = dir_path + "/sliced_data_all_animals_" + str(num_days) + "_days_" + start_slice + "_to_" + end_slice
        exclude_animals_path = dir_path + "/excluded_animals"
        exclude_animals_path_data = exclude_animals_path + "/excluded_animals_data"

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

        if not os.path.exists(sliced_path + '/fig_05'):
            os.makedirs(sliced_path + '/fig_05')
            print("Created fig_05 directory")
        else:
            print("OK. fig_05 exists")

        ###################################################
        ################ READ IN THE DATA #################
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
            print(f"Saved cleaned data to {cleaned_data_path + '/cleaned_' + just_file_names[i]}")

        # Slice our data
        monitor_slices = []
        for i, monitor in enumerate(monitor_files):
            monitor_slice = monitor[(monitor.index >= start_slice) & (monitor.index <= end_slice)]
            monitor_slices.append(monitor_slice)
            print(f"Sliced data for {just_file_names[i]}")
            print(f"Saved sliced data to {sliced_path + '/sliced_data' + f'/sliced_{just_file_names[i]}' }")
            monitor_slice.to_csv(sliced_path + '/sliced_data' + f"/sliced_{just_file_names[i]}", sep='\t')

        # Calculate running average (in minutes) for each animal column
        smoothed_monitors = [] # Holds the smoothed data for each monitor, as PandasData frames

        for i, monitor in enumerate(monitor_slices):
            smoothed_monitor = pd.DataFrame()
            for column in monitor.columns:
                smoothed_monitor[column + '_run_avg_' + str(smoothing_window)] = monitor[column].rolling(window=smoothing_window).mean()
            smoothed_monitor.index = monitor.index
            smoothed_monitors.append(smoothed_monitor)
            print(f"Calculated running average of {smoothing_window} min for {just_file_names[i]}")


        # Calculate avg and std for each animal column
            ## make some magic here...

        #################
        # If animals are to be excluded, we do so here!
        #################
        if exclude_animals:
            # Exclude animals directory
            if not os.path.exists(exclude_animals_path):
                os.makedirs(exclude_animals_path)
                print("Created exclude_animals directory")
            else:
                print("OK. exclude_animals exists")

            # Exclude animals directory data
            if not os.path.exists(exclude_animals_path_data):
                os.makedirs(exclude_animals_path_data)
                print("Created exclude_animals_data directory")
            else:
                print("OK. exclude_animals_data exists")

            # Exclude animals!
                
    except Exception as e:
        messagebox.showerror("Error", str(e))
# End loadData()


# Test function to see current 'loaded' global variables
def printGlobals():
    try:
        print("\n\n\n")
        print("Global variables:")
        print("exclude_animals_var: ", exclude_animals_var)
        print("start_slice: ", start_slice)
        print("end_slice: ", end_slice)
        print("morning_ramp_start: ", morning_ramp_start)
        print("evening_ramp_start: ", evening_ramp_start)
        print("evening_ramp_end: ", evening_ramp_end)
        print("ramp_time: ", ramp_time)
        print("ramp_end_date: ", ramp_end_date)
        print("num_days: ", num_days)
        print("smoothing_window: ", smoothing_window)
        print("dir_path: ", dir_path)
        print("cleaned_data_path: ", cleaned_data_path)
        print("result_path: ", result_path)
        print("sliced_path: ", sliced_path)
        print("exclude_animals_path: ", exclude_animals_path)
        print("exclude_animals_data_path: ", exclude_animals_path_data)
        print("monitor_files: ", monitor_files)
        print("monitor_file_names: ", monitor_file_names)
        print("just_file_names: ", just_file_names)
        print("smoothed_monitors: ", smoothed_monitors)
    except Exception as e:
        messagebox.showerror("Error", str(e))
# End printGlobals


# Plot raw data. This function will be called when the 'Plot raw' button is clicked.
def rawPlot():
    try:
        t_analyze.rawPlot(monitor_files, just_file_names, result_path) # Add global variables as arguments if needed
    except Exception as e:
        messagebox.showerror("Error", str(e))
# End plotRaw



# Main GUI
root = tk.Tk()
root.title("Damn Simple: A GUI for Simple Visualization of DAM Data")

font_size = 12

directory_label = tk.Label(root, text="Directory name (contains the data .txt files):", font=('sans',font_size, 'bold'))
directory_label.pack()
directory_entry = tk.Entry(root, font=('sans',font_size))
directory_entry.pack()

start_time_label = tk.Label(root, text="Start datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:", font=('sans',font_size, 'bold'))
start_time_label.pack()
start_time_entry = tk.Entry(root, font=('sans',font_size))
start_time_entry.pack()

end_time_label = tk.Label(root, text="End datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:", font=('sans',font_size, 'bold'))
end_time_label.pack()
end_time_entry = tk.Entry(root, font=('sans',font_size))
end_time_entry.pack()

DD_start_date_label = tk.Label(root, text="Start date for DD analysis (YYYY-MM-DD):", font=('sans',font_size, 'bold'))
DD_start_date_label.pack()
DD_start_date_entry = tk.Entry(root, font=('sans',font_size))
DD_start_date_entry.pack()

morning_ramp_label = tk.Label(root, text="Morning ramp time (HH:MM), e.g., 6:00 for 6 AM:", font=('sans',font_size, 'bold'))
morning_ramp_label.pack()
morning_ramp_entry = tk.Entry(root, font=('sans',font_size))
morning_ramp_entry.pack()

evening_ramp_label = tk.Label(root, text="Evening ramp time (HH:MM), e.g., 18:00 for 6 PM:", font=('sans',font_size, 'bold'))
evening_ramp_label.pack()
evening_ramp_entry = tk.Entry(root, font=('sans',font_size))
evening_ramp_entry.pack()

night_start_label = tk.Label(root, text="Night start time (HH:MM), e.g., 21:00 for 9 PM:", font=('sans',font_size, 'bold'))
night_start_label.pack()
night_start_entry = tk.Entry(root, font=('sans',font_size))
night_start_entry.pack()

ramp_duration_label = tk.Label(root, text="Duration of ramp in hours (e.g., 1.5):", font=('sans',font_size, 'bold'))
ramp_duration_label.pack()
ramp_duration_entry = tk.Entry(root, font=('sans',font_size))
ramp_duration_entry.pack()

running_average_label = tk.Label(root, text="Running average window size (e.g., 30):", font=('sans',font_size, 'bold'))
running_average_label.pack()
running_average_entry = tk.Entry(root, font=('sans',font_size))
running_average_entry.pack()

exclude_animals_var = tk.BooleanVar()
exclude_animals_checkbutton = tk.Checkbutton(root, text="Exclude Animals? Check for 'yes':",
                                            variable=exclude_animals_var,
                                            font=('sans',font_size))
exclude_animals_checkbutton.pack()


# Buttons
load_button = tk.Button(root, text="Load data", command=loadData, font=('sans',font_size))
load_button.pack()

print_globals_button = tk.Button(root, text="Print globals", command=printGlobals, font=('sans',font_size))
print_globals_button.pack()

plot_raw_button = tk.Button(root, text="Plot raw", command=rawPlot, font=('sans',font_size))
plot_raw_button.pack()

output_text = tk.Text(root)
output_text.pack()

# Redirect the stdout to the text widget
sys.stdout = TextRedirector(output_text)


root.mainloop()