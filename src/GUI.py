# tkinter for GUI
import tkinter as tk
from tkinter import ttk  # access to the Tk themed widget set
from tkinter import messagebox

import threading

import os
import glob
import sys  # For outputting stoud to the text widget

import pandas as pd

# import matplotlib.dates as mdates
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

        global START_SLICE
        global END_SLICE
        global MORNING_RAMP_START
        global EVENING_RAMP_START
        global EVENING_RAMP_END
        global RAMP_TIME
        global RAMP_END_DATE

        global NUM_DAYS

        global SMOOTHING_WINDOW

        global DIR_PATH
        global CLEANED_DATA_PATH
        global RESULT_PATH
        global SLICED_PATH
        global EXCLUDE_ANIMALS_PATH
        global EXCLUDE_ANIMALS_PATH_DATA

        global MONITOR_FILES
        global MONITOR_FILE_NAMES
        global JUST_FILE_NAMES

        global SMOOTHED_MONITORS

        START_SLICE = (
            start_time_entry.get()
        )  # For taking the starting point when slicing the data later
        END_SLICE = (
            end_time_entry.get()
        )  # For taking the ending point when slicing the data later

        # DEFINE LD PERIODS FOR DRAWING LD BARS
        # These are the datetime.time objects that define the start of the morning and evening ramps
        MORNING_RAMP_START = datetime.strptime(morning_ramp_entry.get(), "%H:%M").time()
        EVENING_RAMP_START = datetime.strptime(evening_ramp_entry.get(), "%H:%M").time()

        # Start of the night period
        # night_start = EVENING_RAMP_START.hour + 3 # 3 hours after the evening ramp start; I should have done it this way! Doh!
        EVENING_RAMP_END = datetime.strptime(night_start_entry.get(), "%H:%M").time()

        # The duration of the ramp in hours
        RAMP_TIME = pd.Timedelta(hours=float(ramp_duration_entry.get()))

        # The end date of the ramp
        RAMP_END_DATE = datetime.strptime(DD_start_date_entry.get(), "%Y-%m-%d")

        # calculate number of days in our slice
        datetime_start = pd.to_datetime(START_SLICE)
        datetime_end = pd.to_datetime(END_SLICE)
        delta_datetime = datetime_end - datetime_start
        NUM_DAYS = delta_datetime.days

        # Running average
        SMOOTHING_WINDOW = int(
            running_average_entry.get()
        )  # The window for our running average, in minutes

        print("\n\n\n")
        print("#############################################\n")
        print("Loading the data...")
        print("Today's date is: ", datetime.now())
        print(f"You have sliced a total of {NUM_DAYS} days")

        # Create directories, if they don't exist.
        # I realized I could've used the Pathlib library for this, but I'm new to Python, haha.
        DIR_PATH = "../" + directory_entry.get()
        CLEANED_DATA_PATH = DIR_PATH + "/cleaned_data_all_animals"
        RESULT_PATH = DIR_PATH + "/results_pre_sliced_all_animals"
        SLICED_PATH = (
            DIR_PATH
            + "/sliced_data_all_animals_"
            + str(NUM_DAYS)
            + "_days_"
            + START_SLICE
            + "_to_"
            + END_SLICE
        )
        EXCLUDE_ANIMALS_PATH = DIR_PATH + "/excluded_animals"
        EXCLUDE_ANIMALS_PATH_DATA = (
            EXCLUDE_ANIMALS_PATH
            + "/excluded_animals_data_"
            + str(NUM_DAYS)
            + "_days_"
            + START_SLICE
            + "_to_"
            + END_SLICE
        )

        if not os.path.exists(DIR_PATH):
            os.makedirs(DIR_PATH)
            print("Directory created: ", DIR_PATH)
        else:
            print("OK. Directory exists: ", DIR_PATH)

        if not os.path.exists(CLEANED_DATA_PATH):
            os.makedirs(CLEANED_DATA_PATH)
            print("Cleaned data directory created: ", CLEANED_DATA_PATH)
        else:
            print("OK. Cleaned data directory exists: ", CLEANED_DATA_PATH)

        if not os.path.exists(RESULT_PATH):
            os.makedirs(RESULT_PATH)
            print("Results created: ", RESULT_PATH)
        else:
            print("OK. Results exists: ", RESULT_PATH)

        # Sliced data range
        if not os.path.exists(SLICED_PATH):
            os.makedirs(SLICED_PATH)
            print("Sliced data directory created: ", SLICED_PATH)
        else:
            print("OK. Sliced data directory exists: ", SLICED_PATH)

        # Sliced data in the sliced directory
        if not os.path.exists(SLICED_PATH + "/sliced_data"):
            os.makedirs(SLICED_PATH + "/sliced_data")
            print("Sliced data directory created: ", SLICED_PATH + "/sliced_data")
        else:
            print("OK. Sliced data directory exists: ", SLICED_PATH + "/sliced_data")

        # figure directories
        if not os.path.exists(RESULT_PATH + "/fig_01"):
            os.makedirs(RESULT_PATH + "/fig_01")
            print("Created fig_01 directory")
        else:
            print("OK. fig_01 exists")

        if not os.path.exists(RESULT_PATH + "/fig_02"):
            os.makedirs(RESULT_PATH + "/fig_02")
            print("Created fig_02 directory")
        else:
            print("OK. fig_02 exists")

        if not os.path.exists(SLICED_PATH + "/fig_03"):
            os.makedirs(SLICED_PATH + "/fig_03")
            print("Created fig_03 directory")
        else:
            print("OK. fig_03 exists")

        if not os.path.exists(SLICED_PATH + "/fig_04"):
            os.makedirs(SLICED_PATH + "/fig_04")
            print("Created fig_04 directory")
        else:
            print("OK. fig_04 exists")

        if not os.path.exists(SLICED_PATH + "/fig_05"):
            os.makedirs(SLICED_PATH + "/fig_05")
            print("Created fig_05 directory")
        else:
            print("OK. fig_05 exists")

        ###################################################
        ################ READ IN THE DATA #################
        ###################################################

        MONITOR_FILES = []  # Holds the Pandas DataFrame objects
        MONITOR_FILE_NAMES = []  # Holds the file paths of the monitor files
        JUST_FILE_NAMES = []  # Holds the file names without the path

        for i, txt in enumerate(glob.glob(os.path.join(DIR_PATH, "*txt"))):
            monitor = pd.read_csv(txt, sep="\t", header=None)
            print(f"Loaded monitor data from {txt}")
            MONITOR_FILES.append(monitor)
            MONITOR_FILE_NAMES.append(txt)

            JUST_FILE_NAMES.append(MONITOR_FILE_NAMES[i][len(DIR_PATH) + 1 :])

        # Check to see that our monitor files are correct
        for monitor in MONITOR_FILES:
            monitor.info()

        # Obtain datetimes for each monitor
        # The resulting format should be compatible withn Rethomics in R.
        time_col = (
            []
        )  # Holds the time columns. But I realize I may not need this at all.
        date_col = []  # This, too, may be superfluous! But I have it anyways!
        datetime_index = []

        for i, monitor in enumerate(MONITOR_FILES):
            time_col.append(monitor.iloc[:, 2])
            date_col.append(monitor.iloc[:, 1])
            concat_datetime = date_col[i] + " " + time_col[i]
            datetime_index.append(
                pd.to_datetime(concat_datetime, format="%d %b %y %H:%M:%S")
            )
            print(
                f"Converted date and time columns to datetime for {MONITOR_FILE_NAMES[i]}"
            )

        # New column names for the animals
        column_nums = pd.Series(range(1, 33))  # For monitors that hold 32 animals
        animal_nums = "animal_" + column_nums.astype(str)

        # Clean the data by grabbing only activity columns
        for i, monitor in enumerate(MONITOR_FILES):
            activity = monitor.iloc[:, 10:42]
            activity.index = datetime_index[i]
            activity.columns = animal_nums

            MONITOR_FILES[i] = activity  # update the monitor df in our list

            activity.to_csv(
                CLEANED_DATA_PATH + f"/cleaned_{JUST_FILE_NAMES[i]}", sep="\t"
            )
            print(f"Cleaned data for {JUST_FILE_NAMES[i]}")
            print(
                f"Saved cleaned data to {CLEANED_DATA_PATH + '/cleaned_' + JUST_FILE_NAMES[i]}"
            )

        # Slice our data
        monitor_slices = []
        for i, monitor in enumerate(MONITOR_FILES):
            monitor_slice = monitor[
                (monitor.index >= START_SLICE) & (monitor.index <= END_SLICE)
            ]
            monitor_slices.append(monitor_slice)
            print(f"Sliced data for {JUST_FILE_NAMES[i]}")
            print(
                f"Saved sliced data to {SLICED_PATH + '/sliced_data' + f'/sliced_{JUST_FILE_NAMES[i]}' }"
            )
            monitor_slice.to_csv(
                SLICED_PATH + "/sliced_data" + f"/sliced_{JUST_FILE_NAMES[i]}", sep="\t"
            )

        # Calculate running average (in minutes) for each animal column
        SMOOTHED_MONITORS = (
            []
        )  # Holds the smoothed data for each monitor, as PandasData frames

        for i, monitor in enumerate(monitor_slices):
            smoothed_monitor = pd.DataFrame()
            for column in monitor.columns:
                smoothed_monitor[column + "_run_avg_" + str(SMOOTHING_WINDOW)] = (
                    monitor[column].rolling(window=SMOOTHING_WINDOW).mean()
                )  # Change this to a forward looking moving average
            smoothed_monitor.index = monitor.index
            SMOOTHED_MONITORS.append(smoothed_monitor)
            print(
                f"Calculated running average of {SMOOTHING_WINDOW} min for {JUST_FILE_NAMES[i]}"
            )

        # Calculate avg and std for each animal column
        ## make some magic here...

        print("\nData loaded successfully!\n\n\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# End loadData()


# Load data thread. This function will be called when the 'Load data' button is clicked.
# Since I do not use matplotlib's GUI backend, I can't use the 'plot' function in a separate thread.
# But I can at least load the data and preprocess it in a separate thread...
def loadingThread():
    try:
        threading.Thread(
            target=loadData, daemon=True
        ).start()  # Daemon is false, to avoid abrupt termination when reading/writing files
    except Exception as e:
        messagebox.showerror("Error", str(e))


# End loadingThread


# Test function to see current 'loaded' global variables
def printGlobals():
    try:
        print("\n\n\n")
        print("#############################################\n")
        print("Global variables:")
        print("START_SLICE: ", START_SLICE)
        print("END_SLICE: ", END_SLICE)
        print("MORNING_RAMP_START: ", MORNING_RAMP_START)
        print("EVENING_RAMP_START: ", EVENING_RAMP_START)
        print("EVENING_RAMP_END: ", EVENING_RAMP_END)
        print("RAMP_TIME: ", RAMP_TIME)
        print("RAMP_END_DATE: ", RAMP_END_DATE)
        print("NUM_DAYS: ", NUM_DAYS)
        print("SMOOTHING_WINDOW: ", SMOOTHING_WINDOW)

        print("\n\n")

        print("DIR_PATH: ", DIR_PATH)
        print("CLEANED_DATA_PATH: ", CLEANED_DATA_PATH)
        print("RESULT_PATH: ", RESULT_PATH)
        print("SLICED_PATH: ", SLICED_PATH)
        print("EXCLUDE_ANIMALS_PATH: ", EXCLUDE_ANIMALS_PATH)
        print("EXCLUDE_ANIMALS_PATH_DATA: ", EXCLUDE_ANIMALS_PATH_DATA)

        print("\n\n")

        print("MONITOR_FILES: ", MONITOR_FILES)
        print("MONITOR_FILE_NAMES: ", MONITOR_FILE_NAMES)
        print("JUST_FILE_NAMES: ", JUST_FILE_NAMES)
        print("SMOOTHED_MONITORS: ", SMOOTHED_MONITORS)
        print("#############################################\n")

        printExcluded()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# End printGlobals


def excludableAnimals(monitor_name: str):
    if monitor_name is None:
        print("Data file name is not defined. Monitor name is None.")
        return

    # Create a new Toplevel window
    options_window = tk.Toplevel(root)
    options_window.title(f"{monitor_name} Excludable Animals")
    options_window.geometry("800x1200")

    options_window_label = tk.Label(
        options_window,
        text=f"Check boxes to drop that animal from {monitor_name}.",
        font=("sans", 12, "bold"),
    )
    options_window_label.pack()

    animal_vars = []  # Holds the checkbox tkinter variables

    # Create 32 checkboxes
    for i in range(1, 33):
        var = tk.BooleanVar()
        checkbutton = tk.Checkbutton(
            options_window, text=f"Animal {i}", variable=var, font=("sans", 14)
        )
        checkbutton.pack()
        animal_vars.append(var)
        # The boolean values are not user-defined until the user actually checks some boxes (or not!)
        # So I need to obtain the boolean values later, when using them.
        # For that, I will use a list comprehension to get the boolean values from the checkbox entries

    close_button = tk.Button(
        options_window, text="Close", command=options_window.destroy
    )
    close_button.pack()

    return animal_vars


# End excludeAnimals


def onExclude():
    global ANIMALS_TO_EXCLUDE

    #################
    # If animals are to be excluded, we do so here!
    #################
    if EXCLUDE_ANIMALS_VAR.get():
        # Exclude animals directory
        if not os.path.exists(EXCLUDE_ANIMALS_PATH):
            os.makedirs(EXCLUDE_ANIMALS_PATH)
            print("Created exclude_animals directory")
        else:
            print("OK. exclude_animals exists")

        # Exclude animals directory data
        if not os.path.exists(EXCLUDE_ANIMALS_PATH_DATA):
            os.makedirs(EXCLUDE_ANIMALS_PATH_DATA)
            print("Created exclude_animals_data directory")
        else:
            print("OK. exclude_animals_data exists")

        # Exclude animals!
        # If checked, generate and show the options window
        try:
            ANIMALS_TO_EXCLUDE = []
            for monitor_name in JUST_FILE_NAMES:
                ANIMALS_TO_EXCLUDE.append(excludableAnimals(monitor_name))
        except Exception as e:
            print("ERROR: Did you load the data first?")
    else:
        print("Re-check to open the exclude animals window.")
        ANIMALS_TO_EXCLUDE = []


# End onExclude


def printExcluded():
    global EXCLUDED_ANIMALS_BOOLS

    print("Excluded animals based on Boolean-slicing:")
    # Re-initialize the list of boolean values for each animal to exclude

    EXCLUDED_ANIMALS_BOOLS = []

    for i, monitor in enumerate(MONITOR_FILES):
        # List comprehension to get a list of boolean values from tkinter check variables
        # The boolean list is then appended to my global list
        EXCLUDED_ANIMALS_BOOLS.append([var.get() for var in ANIMALS_TO_EXCLUDE[i]])
        print(
            f"{JUST_FILE_NAMES[i]}: Excluded animal indices: {monitor.columns[EXCLUDED_ANIMALS_BOOLS[i]]}"
        )
    print("\n\n")


# Plot raw data. This function will be called when the 'Plot raw' button is clicked.
def rawPlot():
    try:
        print("\n\n\n")
        print("#############################################\n")
        print("Plotting raw data...")
        t_analyze.rawPlot(
            MONITOR_FILES, JUST_FILE_NAMES, RESULT_PATH
        )  # Add global variables as arguments if needed
    except Exception as e:
        messagebox.showerror("Error", str(e))


# End plotRaw


# Main GUI
root = tk.Tk()
root.title("Damn Simple: A GUI for Simple Visualization of DAM Data")
root.geometry("1000x800")

font_size = 14

directory_label = tk.Label(
    root,
    text="Directory name (contains the data .txt files):",
    font=("sans", font_size, "bold"),
)
directory_label.pack()
directory_entry = tk.Entry(root, font=("sans", font_size))
directory_entry.pack()

start_time_label = tk.Label(
    root,
    text="Start datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:",
    font=("sans", font_size, "bold"),
)
start_time_label.pack()
start_time_entry = tk.Entry(root, font=("sans", font_size))
start_time_entry.pack()

end_time_label = tk.Label(
    root,
    text="End datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:",
    font=("sans", font_size, "bold"),
)
end_time_label.pack()
end_time_entry = tk.Entry(root, font=("sans", font_size))
end_time_entry.pack()

DD_start_date_label = tk.Label(
    root,
    text="Start date for DD analysis (YYYY-MM-DD)\nEnter out-of-bounds date for no DD analysis:",
    font=("sans", font_size, "bold"),
)
DD_start_date_label.pack()
DD_start_date_entry = tk.Entry(root, font=("sans", font_size))
DD_start_date_entry.pack()

morning_ramp_label = tk.Label(
    root,
    text="Morning ramp time (HH:MM), e.g., 6:00 for 6 AM:",
    font=("sans", font_size, "bold"),
)
morning_ramp_label.pack()
morning_ramp_entry = tk.Entry(root, font=("sans", font_size))
morning_ramp_entry.pack()

evening_ramp_label = tk.Label(
    root,
    text="Evening ramp time (HH:MM), e.g., 18:00 for 6 PM:",
    font=("sans", font_size, "bold"),
)
evening_ramp_label.pack()
evening_ramp_entry = tk.Entry(root, font=("sans", font_size))
evening_ramp_entry.pack()

night_start_label = tk.Label(
    root,
    text="Night start time (HH:MM), e.g., 21:00 for 9 PM:",
    font=("sans", font_size, "bold"),
)
night_start_label.pack()
night_start_entry = tk.Entry(root, font=("sans", font_size))
night_start_entry.pack()

ramp_duration_label = tk.Label(
    root,
    text="Duration of ramp in hours (e.g., 1.5):",
    font=("sans", font_size, "bold"),
)
ramp_duration_label.pack()
ramp_duration_entry = tk.Entry(root, font=("sans", font_size))
ramp_duration_entry.pack()

running_average_label = tk.Label(
    root,
    text="Running average window size (e.g., 30):",
    font=("sans", font_size, "bold"),
)
running_average_label.pack()
running_average_entry = tk.Entry(root, font=("sans", font_size))
running_average_entry.pack()

load_button = tk.Button(
    root, text="Load & Slice data", command=loadingThread, font=("sans", font_size)
)
load_button.pack()

EXCLUDE_ANIMALS_VAR = tk.BooleanVar()
EXCLUDE_ANIMALS_VAR.trace_add("write", lambda *args: onExclude())
exclude_animals_checkbutton = tk.Checkbutton(
    root,
    text="Exclude Animals? Check for 'yes':",
    variable=EXCLUDE_ANIMALS_VAR,
    font=("sans", font_size),
)
exclude_animals_checkbutton.pack()

print_globals_button = tk.Button(
    root, text="Print/check globals", command=printGlobals, font=("sans", font_size)
)
print_globals_button.pack()

plot_raw_button = tk.Button(
    root, text="Plot raw", command=rawPlot, font=("sans", font_size)
)
plot_raw_button.pack()

output_text = tk.Text(root, width=100, height=30, wrap=tk.WORD, font=("sans", 12))
output_text.pack()

# Redirect the stdout to the text widget
sys.stdout = TextRedirector(output_text)

root.mainloop()
