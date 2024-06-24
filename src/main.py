# tkinter for GUI
import tkinter as tk
from tkinter import ttk  # access to the Tk themed widget set
from tkinter import messagebox

import threading
import queue  # To handle thread-safety for writing to GUI widget

import os
import glob
import sys  # For outputting stoud to the text widget


import traceback  # For error handling
import faulthandler

faulthandler.enable()

import pandas as pd

# import matplotlib.dates as mdates
# import matplotlib.dates as mdates
from datetime import datetime, timedelta
from datetime import time as dt_time

# My main analysis script. This is where all the fun stuff happens.
# Each figure that is produced is broken into tasks, e.g., plotRaw().
import main_template_analysis as t_analyze

# Create directory for ../log files
if not os.path.exists("../logs"):
    os.makedirs("../logs")
    print("Created logs directory")
else:
    print("OK. logs exists")

# Create a log file if it doesn't exist
LOG_FILE = "../logs/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
if not os.path.exists(LOG_FILE):
    # just open and close it
    open(LOG_FILE, "w").close()


# Class to redirect stdout to a text widget in the Gui
# Also redirects output to a log file
# And also writes to the terminal
class Logger(object):
    def __init__(self, widget, filename=LOG_FILE):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
        self.widget = widget
        self.queue = queue.Queue()

    def write(self, message):
        # We can write to the terminal and log file: That's thread-safe

        self.terminal.write(message)  # writes a message to the terminal
        self.log.write(message)  # writes a message to the log file

        # But we cannot write to our widget. So we put the message in a queue
        self.queue.put(message)  # puts the message in the queue

    def flush(self):
        pass

    def check_queue(self):
        while not self.queue.empty():  # While the queue is not empty...
            message = self.queue.get()  # Get the first message...

            # Write the message to the widget. This is thread-safe.
            self.widget.insert(tk.END, message)
            self.widget.see(tk.END)


# Functions to resize elements in the GUI
def resize_output_text(scale_value):
    # Update the font size based on the scale value
    output_text.config(font=("TkDefaultFont", int(scale_value)))


def update_font_size(scale_value):
    # Update the font size based on the scale value
    global font_size
    font_size = int(scale_value)
    for widget in all_widgets:
        widget.config(font=("sans", font_size))


def processData():
    # Process data, from RUNNING AVG to FINAL GRAPH
    pass


# Global variables are defined with this via user entries in the appropriate fields.
# This also processes the monitor data (prepared, sliced, smoothed, etc...)
def loadData():
    try:
        # Declare global variables
        global RECORDING_INTERVAL
        RECORDING_INTERVAL = 1  # 1 minute recording interval, which is the default.
        # I may let the user change this in the future

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
        global PREPARED_DATA_PATH
        global PREPARED_PATH
        global SLICED_PATH
        global EXCLUDE_ANIMALS_PATH
        global EXCLUDE_ANIMALS_PATH_DATA

        global MONITOR_FILES
        global MONITOR_SLICES
        global MONITOR_FILE_NAMES
        global JUST_FILE_NAMES

        # Define global variables from GUI fields
        exclude_animals = EXCLUDE_ANIMALS_VAR.get()

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
        PREPARED_DATA_PATH = DIR_PATH + "/prepared_data_raw_all_animals/prepared_data"
        PREPARED_PATH = DIR_PATH + "/prepared_data_raw_all_animals"
        SLICED_PATH = (
            DIR_PATH
            + "/sliced_data_all_animals_"
            + str(NUM_DAYS)
            + "_days_"
            + START_SLICE.replace(
                ":", "-"
            )  # So Windows doesn't throw a fit because of their beloved :C drive
            + "_to_"
            + END_SLICE.replace(":", "-")
        )
        EXCLUDE_ANIMALS_PATH = DIR_PATH + "/excluded_animals"

        EXCLUDE_ANIMALS_PATH_DATA = (
            EXCLUDE_ANIMALS_PATH
            + "/excluded_animals_data_"
            + str(NUM_DAYS)
            + "_days_"
            + START_SLICE.replace(":", "-")
            + "_to_"
            + END_SLICE.replace(":", "-")
        )

        if not os.path.exists(DIR_PATH):
            os.makedirs(DIR_PATH)
            print("Directory created: ", DIR_PATH)
        else:
            print("OK. Directory exists: ", DIR_PATH)

        if not os.path.exists(PREPARED_DATA_PATH):
            os.makedirs(PREPARED_DATA_PATH)
            print("Prepared data directory created: ", PREPARED_DATA_PATH)
        else:
            print("OK. Prepared data directory exists: ", PREPARED_DATA_PATH)

        if not os.path.exists(PREPARED_PATH):
            os.makedirs(PREPARED_PATH)
            print("Results created: ", PREPARED_PATH)
        else:
            print("OK. Results exists: ", PREPARED_PATH)

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
        if not os.path.exists(PREPARED_PATH + "/fig_01"):
            os.makedirs(PREPARED_PATH + "/fig_01")
            print("Created fig_01 directory")
        else:
            print("OK. fig_01 exists")

        if not os.path.exists(PREPARED_PATH + "/fig_02"):
            os.makedirs(PREPARED_PATH + "/fig_02")
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

        if not os.path.exists(SLICED_PATH + "/fig_06"):
            os.makedirs(SLICED_PATH + "/fig_06")
            print("Created fig_06 directory")
        else:
            print("OK. fig_06 exists")

        if not os.path.exists(SLICED_PATH + "/fig_07"):
            os.makedirs(SLICED_PATH + "/fig_07")
            print("Created fig_07 directory")
        else:
            print("OK. fig_07 exists")

        if not os.path.exists(SLICED_PATH + "/fig_08"):
            os.makedirs(SLICED_PATH + "/fig_08")
            print("Created fig_08 directory")
        else:
            print("OK. fig_08 exists")

        if not os.path.exists(SLICED_PATH + "/fig_09"):
            os.makedirs(SLICED_PATH + "/fig_09")
            print("Created fig_09 directory")
        else:
            print("OK. fig_09 exists")

        if not os.path.exists(SLICED_PATH + "/fig_10"):
            os.makedirs(SLICED_PATH + "/fig_10")
            print("Created fig_10 directory")
        else:
            print("OK. fig_10 exists")

        if not os.path.exists(SLICED_PATH + "/fig_11"):
            os.makedirs(SLICED_PATH + "/fig_11")
            print("Created fig_11 directory")
        else:
            print("OK. fig_11 exists")

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
            activity.index.name = "datetime"
            activity.columns = animal_nums

            MONITOR_FILES[i] = activity  # update the monitor df in our list

            activity.to_csv(
                PREPARED_DATA_PATH + f"/prepared_{JUST_FILE_NAMES[i]}", sep="\t"
            )
            print(f"Prepared data for {JUST_FILE_NAMES[i]}")
            print(
                f"Saved prepared data to {PREPARED_DATA_PATH + '/prepared_' + JUST_FILE_NAMES[i]}"
            )

        # Slice our data
        MONITOR_SLICES = []
        for i, monitor in enumerate(MONITOR_FILES):
            monitor_slice = monitor[
                (monitor.index >= START_SLICE) & (monitor.index <= END_SLICE)
            ]
            MONITOR_SLICES.append(monitor_slice)
            print(f"Sliced data for {JUST_FILE_NAMES[i]}")
            print(
                f"Saved sliced data to {SLICED_PATH + '/sliced_data' + f'/sliced_{JUST_FILE_NAMES[i]}' }"
            )
            monitor_slice.to_csv(
                SLICED_PATH + "/sliced_data" + f"/sliced_{JUST_FILE_NAMES[i]}", sep="\t"
            )

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
        ).start()  # Daemon is true. Background thread that terminates when main thread terminates.
    except Exception as e:
        messagebox.showerror("Error", str(e))


# End loadingThread


# Test function to see current 'loaded' global variables
def commit():
    try:
        print("Committing exclusions...")
        printExcluded()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# End printGlobals


def excludableAnimals(
    monitor_name: str,
):  # returns a list of tKinter checkbox variables
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
        font=("sans", font_size, "bold"),
    )
    options_window.configure(bg="#90EE90")
    options_window_label.pack()

    animal_vars = []  # Holds the checkbox tkinter variables

    # Create 32 checkboxes
    for i in range(1, 33):
        var = tk.BooleanVar()
        checkbutton = tk.Checkbutton(
            options_window, text=f"Animal {i}", variable=var, font=("sans", font_size)
        )
        checkbutton.pack()
        checkbutton.configure(bg="#90EE90", border=5, relief="raised", cursor="hand2")

        animal_vars.append(var)
        # The boolean values are not user-defined until the user actually checks some boxes (or not!)
        # So I need to obtain the boolean values later, when using them.
        # For that, I will use a list comprehension to get the boolean values from the checkbox entries

    close_button = tk.Button(
        options_window,
        text="Close",
        command=options_window.destroy,
        font=("sans", font_size),
    )
    close_button.configure(bg="#00FF7F", border=5, relief="raised", cursor="hand2")
    close_button.pack()

    return animal_vars


# End excludeAnimals


def onExclude():
    global ANIMALS_TO_EXCLUDE  # Holds tkinter checkbox variables, which will be appended here.
    ANIMALS_TO_EXCLUDE = []
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
            for monitor_name in JUST_FILE_NAMES:
                ANIMALS_TO_EXCLUDE.append(excludableAnimals(monitor_name))
        except Exception as e:
            print("ERROR: Did you load the data first?")
    else:
        print("Re-check to open the exclude animals window.")
        print("Close the old windows first.")
        ANIMALS_TO_EXCLUDE = []


# End onExclude


# This function also commits the exclusions defined in the check boxes. It saves the excluded animals data file.
def printExcluded():
    global EXCLUDE_COMMIT

    EXCLUDE_COMMIT = False

    global EXCLUDED_ANIMALS_BOOLS  # List of list of booleans, used for boolean slicing.
    global EXCLUDED_ANIMALS_MONITOR_FILES  # List of pd.DataFrames for future plotting
    global JUST_FILE_NAMES_EXCLUDED

    global EXCL_STR  # Later defined by the unique set of excluded animals

    global EXCLUDE_ANIMALS_UNIQUE_PATH  # directory path for the specific excluded animals data and figs. String defined by animals excluded.

    EXCLUDED_ANIMALS_BOOLS = []
    EXCLUDED_ANIMALS_MONITOR_FILES = []
    JUST_FILE_NAMES_EXCLUDED = []
    EXCLUDE_ANIMALS_UNIQUE_PATH = []

    print("Excluded animals based on Boolean-slicing:")
    # Re-initialize the list of boolean values for each animal to exclude

    for i, slice in enumerate(MONITOR_SLICES):
        EXCL_STR = "excl"  # This will be used to create a specific directory for the excluded animals
        # Reasponable to expect that different monitors will have different exclusions.
        # So each monitor file data may need its own exclusive directory
        # If one monitor is NOT excluded, it goes to an excl_none. This is redundant but helps with program flow.

        # List comprehension to get a list of boolean values from tkinter check variables
        # The boolean list is then appended to my global list
        EXCLUDED_ANIMALS_BOOLS.append([var.get() for var in ANIMALS_TO_EXCLUDE[i]])
        excluded_animal_columns = slice.columns[EXCLUDED_ANIMALS_BOOLS[i]]

        # A new list of file names for the excluded animals.
        JUST_FILE_NAMES_EXCLUDED.append("excluded_" + JUST_FILE_NAMES[i])

        print(
            f"{JUST_FILE_NAMES_EXCLUDED[i]}: Excluded animal indices: {excluded_animal_columns}"
        )

        # Concatenate the animal numbers to a string, which will be used to create a specific directory.
        # This lets us make multiple unique exclusions while saving the data.
        # And each exclusion is saved to a specific directory, for identification purposes.

        any_excl = False  # Sets as false. If an animal is excluded, below, it is assigned True.

        for j, bool in enumerate(EXCLUDED_ANIMALS_BOOLS[i]):
            if bool:
                any_excl = True
                EXCL_STR += "_" + str(j + 1)

        if any_excl == False:
            EXCL_STR += "_none"

        EXCLUDE_ANIMALS_UNIQUE_PATH.append(EXCLUDE_ANIMALS_PATH_DATA + "/" + EXCL_STR)

        if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i]):
            os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i])
            print("Created specific directory based on excluded animals")
        else:
            print(
                "OK. Looks like we've sliced these same individuals before. Directory exists"
            )

        # Save the excluded animals to a file
        EXCLUDED_ANIMALS_MONITOR_FILES.append(
            slice.drop(columns=excluded_animal_columns)
        )

        EXCLUDED_ANIMALS_MONITOR_FILES[i].to_csv(
            EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/" + JUST_FILE_NAMES_EXCLUDED[i],
            sep="\t",
        )
        print(
            f"Excluded animals saved to {EXCLUDE_ANIMALS_UNIQUE_PATH[i] + '/' + JUST_FILE_NAMES_EXCLUDED[i]}"
        )
        print("\n\n")

        EXCLUDE_COMMIT = True
    print("Exclusions committed! Starting data processing thread...")
    processDataThread()


def processData():
    # Batches will contain lists of ALL monitor data, both the unexcluded and excluded animals data
    global SLICED_BATCH
    global SMOOTHED_BATCH
    global ZSCORED_BATCH
    global FOLDED_AVG_BATCH
    global FINAL_DATA_BATCH

    # Globals for holding the data of the non-excluded animals data
    global SMOOTHED_MONITORS
    global AVG_AND_STD
    global ZSCORED_MONITORS
    global FOLDED_AVG_MONITORS
    global FINAL_DATA

    SMOOTHED_MONITORS = []
    AVG_AND_STD = []
    ZSCORED_MONITORS = []
    FOLDED_AVG_MONITORS = []
    FINAL_DATA = []

    # Batches hold all of the excluded animal monitor data, too, if we have excluded animal data.
    SLICED_BATCH = [MONITOR_SLICES]
    SMOOTHED_BATCH = [SMOOTHED_MONITORS]
    AVG_AND_STD_BATCH = [AVG_AND_STD]
    ZSCORED_BATCH = [ZSCORED_MONITORS]
    FOLDED_AVG_BATCH = [FOLDED_AVG_MONITORS]
    FINAL_DATA_BATCH = [FINAL_DATA]

    DIRECTORY_BATCH = [SLICED_PATH]
    JUST_FILE_NAMES_BATCH = [JUST_FILE_NAMES]

    if EXCLUDE_COMMIT:
        # globals for holding the data of the excluded animals data
        global EXCLUDED_ANIMALS_SMOOTHED
        global EXCLUDED_ANIMALS_AVG_STD
        global EXCLUDED_ANIMALS_ZSCORED
        global EXCLUDED_ANIMALS_FOLDED_AVG
        global EXCLUDED_FINAL_DATA

        EXCLUDED_ANIMALS_SMOOTHED = []
        EXCLUDED_ANIMALS_AVG_STD = []
        EXCLUDED_ANIMALS_ZSCORED = []
        EXCLUDED_ANIMALS_FOLDED_AVG = []
        EXCLUDED_FINAL_DATA = []

        try:
            print("Excluded animals data will be included in the data processing")

            # We want to append, not extend. Extend would add multiple elements. But we want to add a single element, which is another list.
            SLICED_BATCH.append(EXCLUDED_ANIMALS_MONITOR_FILES)
            SMOOTHED_BATCH.append(EXCLUDED_ANIMALS_SMOOTHED)
            AVG_AND_STD_BATCH.append(EXCLUDED_ANIMALS_AVG_STD)
            ZSCORED_BATCH.append(EXCLUDED_ANIMALS_ZSCORED)
            FOLDED_AVG_BATCH.append(EXCLUDED_ANIMALS_FOLDED_AVG)
            FINAL_DATA_BATCH.append(EXCLUDED_FINAL_DATA)

            DIRECTORY_BATCH.append(EXCLUDE_ANIMALS_UNIQUE_PATH)

            JUST_FILE_NAMES_BATCH.append(JUST_FILE_NAMES_EXCLUDED)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    else:
        print("Exclusions either not committed or in progress...")

    try:
        # MAIN OUTER LOOP
        for k, SLICED_DATA_LIST in enumerate(SLICED_BATCH):
            if k == 0:  # For the non-excluded animal data
                current_directory = DIRECTORY_BATCH[k]
                # smoothed data dir
                if not os.path.exists(DIRECTORY_BATCH[k] + "/smoothed_data"):
                    os.makedirs(DIRECTORY_BATCH[k] + "/smoothed_data")
                    print(f"Created {DIRECTORY_BATCH[k]}/smoothed_data directory")
                else:
                    print(f"OK. {DIRECTORY_BATCH[k]}/smoothed_data exists")

                # zscored data dir
                if not os.path.exists(DIRECTORY_BATCH[k] + "/z_scored_data"):
                    os.makedirs(DIRECTORY_BATCH[k] + "/z_scored_data")
                    print(f"Created {DIRECTORY_BATCH[k]}/z_scored_data directory")
                else:
                    print(f"OK. {DIRECTORY_BATCH[k]}/z_scored_data exists")

                # folded average data dir
                if not os.path.exists(DIRECTORY_BATCH[k] + "/folded_average_data"):
                    os.makedirs(DIRECTORY_BATCH[k] + "/folded_average_data")
                    print(f"Created {DIRECTORY_BATCH[k]}/folded_average_data directory")
                else:
                    print(f"OK. {DIRECTORY_BATCH[k]}/folded_average_data exists")
                
                # final data dir
                if not os.path.exists(DIRECTORY_BATCH[k] + "/final_avg_data"):
                    os.makedirs(DIRECTORY_BATCH[k] + "/final_avg_data")
                    print(f"Created {DIRECTORY_BATCH[k]}/final_avg_data directory")
                else:
                    print(f"OK. {DIRECTORY_BATCH[k]}/final_avg_data exists")

            if k > 0:  # This corresponds to our excluded animals.
                print("######################################\n\n")
                print(f"Now processing excluded animals data...")

                for path in DIRECTORY_BATCH[k]:
                    if not os.path.exists(path + "/smoothed_data"):
                        os.makedirs(path + "/smoothed_data")
                        print(f"Created {path}/smoothed_data directory")
                    else:
                        print(f"OK. {path} /smoothed_data exists")

                    # zscored data dir
                    if not os.path.exists(path + "/z_scored_data"):
                        os.makedirs(path + "/z_scored_data")
                        print(f"Created {path}/z_scored_data directory")
                    else:
                        print(f"OK. {path}/z_scored_data exists")

                    # folded average data dir
                    if not os.path.exists(path + "/folded_average_data"):
                        os.makedirs(path + "/folded_average_data")
                        print(f"Created {path}/folded_average_data directory")
                    else:
                        print(f"OK. {path}/folded_average_data exists")

                    # final avg data dir
                    if not os.path.exists(path + "/final_avg_data"):
                        os.makedirs(path + "/final_avg_data")
                        print(f"Created {path}/final_avg_data directory")
                    else:
                        print(f"OK. {path}/final_avg_data exists")

            # Calculate running average (in minutes) for each animal column
            for i, monitor in enumerate(SLICED_DATA_LIST):
                if (
                    k > 0
                ):  # For the excluded monitors, each monitor may have its own directory.
                    # And thus we expect DIRECTORY_BATCH[k>0] to be a list of directories...
                    current_directory = DIRECTORY_BATCH[k][i]

                # We define a FixedForwardWindowIndexer to calculate the forward looking moving average
                # This is slightly different than the default moving average, which is backward looking and excludes the first range of values by leaving them blank.
                indexer = pd.api.indexers.FixedForwardWindowIndexer(
                    window_size=SMOOTHING_WINDOW
                )

                smoothed_monitor = pd.DataFrame()

                avg_and_std = pd.DataFrame(
                    columns=monitor.columns, index=["mean", "std"]
                )
                avg_and_std.index.name = "statistic"

                for column in monitor.columns:
                    smoothed_column_name = column + "_run_avg_" + str(SMOOTHING_WINDOW)

                    smoothed_monitor[smoothed_column_name] = (
                        monitor[column].rolling(window=indexer, min_periods=1).mean()
                    )  # Change this to a forward looking moving average

                    # Let's also calculate average and std here.
                    # Note that avg and std are calculated from the SMOOTHED data.
                    avg_and_std.loc["mean", column] = smoothed_monitor[
                        smoothed_column_name
                    ].mean() # access specific cell under index "mean" and column "column"
                    avg_and_std.loc["std", column] = smoothed_monitor[
                        smoothed_column_name
                    ].std()

                smoothed_monitor.index = monitor.index

                smoothed_monitor.to_csv(
                    current_directory
                    + "/smoothed_data"
                    + "/"
                    + str(SMOOTHING_WINDOW)
                    + "min_running_avg_"
                    + JUST_FILE_NAMES_BATCH[k][i],
                    sep="\t",
                )
                print("Saved smoothed data to:")
                print(
                    current_directory
                    + "/smoothed_data"
                    + "/"
                    + str(SMOOTHING_WINDOW)
                    + "min_running_avg_"
                    + JUST_FILE_NAMES_BATCH[k][i]
                )

                avg_and_std.to_csv(  # Paired with z_scored data since avg and std relevant in calculating zscores
                    current_directory
                    + "/z_scored_data"
                    + "/column_average_and_std_"
                    + JUST_FILE_NAMES_BATCH[k][i],
                    sep="\t",
                )
                print("Saved average and std to:")
                print(
                    current_directory
                    + "/z_scored_data"
                    + "/column_average_and_std_"
                    + JUST_FILE_NAMES_BATCH[k][i]
                )

                SMOOTHED_BATCH[k].append(smoothed_monitor)

                AVG_AND_STD_BATCH[k].append(avg_and_std)

                print(
                    f"Calculated running average of {SMOOTHING_WINDOW} min for {JUST_FILE_NAMES_BATCH[k][i]}"
                )

            # Calculate avg and std for each animal column
            print("\n\n")
            print("Converting smoothed values to z-score...")

            for i, smoothed_monitor in enumerate(
                SMOOTHED_BATCH[k]
            ):  # We will use the smoothed data to calculate z-scores
                if k > 0:
                    print("Setting current directory for excluded animals...")
                    current_directory = DIRECTORY_BATCH[k][i]

                # I define the zscored_monitor to have the original column names (e.g., 'animal_1', 'animal_2', etc.)
                # It will use the smoothed_monitor index, which is the datetime index. Any of the sliced indices would work.
                # Define our zscored_monitor
                zscored_monitor = pd.DataFrame(
                    columns=SLICED_DATA_LIST[i].columns, index=smoothed_monitor.index
                )

                for j, column in enumerate(zscored_monitor.columns):
                    # Now, for each column in the zscored_monitor, I will assign to it a column of z-scores
                    # which are calculated from the smoothed_monitor files.
                    # I will use the mean and std from the AVG_AND_STD df to calculate the z-scores.

                    # for a specific column, which contains the animal ID, we calcualte the Z-score using that animal ID's mean and STD.
                    # I'm slicing in two different ways, which might confuse some. But I'm slicing the AVG_AND_STD df by the column name, which is the animal ID, using .loc
                    zscored_monitor[column] = smoothed_monitor.iloc[:, j].apply(
                        lambda x: (x - AVG_AND_STD_BATCH[k][i].loc["mean", column]) # accessing a specific cell that contains the mean...
                        / AVG_AND_STD_BATCH[k][i].loc["std", column] # accessing a specific cell that contains the std...
                    )

                ZSCORED_BATCH[k].append(zscored_monitor)

                zscored_monitor.to_csv(
                    current_directory
                    + "/z_scored_data"
                    + f"/zscored_{SMOOTHING_WINDOW}_min_run_avg_{JUST_FILE_NAMES_BATCH[k][i]}",
                    sep="\t",
                )

                print(
                    f"Saved z-scored data to {current_directory}/z_scored_data/zscored_{SMOOTHING_WINDOW}_min_run_avg_{JUST_FILE_NAMES_BATCH[k][i]}"
                )

            print("\n\n")

            # Calculate the folded average
            print("Calculating the folded average...")

            for i, zscored_monitor in enumerate(ZSCORED_BATCH[k]):
                if k > 0:
                    current_directory = DIRECTORY_BATCH[k][i]

                # New folded_avg_monitor will have indices up to 24 hrs. Here, since the index is in minutes, we will have 1440 minutes in a day + 1,...
                # so that the index goes from 00:00 to 00:00 the next day.
                folded_avg_monitor = pd.DataFrame(columns=zscored_monitor.columns)

                for column in zscored_monitor:
                    # Fold the data. We can group by the datetime's time, and then calculate the mean for each time.
                    folded_avg_monitor[column] = (
                        zscored_monitor[column]
                        .groupby(zscored_monitor.index.time)
                        .mean()
                    )

                # The following seems verbose, but it works to get the correct format.
                # Slice by the first index, which should be the first time bin, specified by the START_SLICE
                # Slicing by index name gives a Series where the column names are the index. We only want values.

                # Save the monitor by appending to our list of pd.DataFrames
                # Note that I save it BEFORE appending the first row to the end of the monitor.
                folded_avg_monitor.index.name = "time_bin"
                folded_avg_monitor_dummy = folded_avg_monitor.copy()
                folded_avg_monitor_dummy.index = pd.to_datetime(
                    folded_avg_monitor.index, format="%H:%M:%S"
                )
                FOLDED_AVG_BATCH[k].append(folded_avg_monitor_dummy)

                first_row = folded_avg_monitor.loc[
                    folded_avg_monitor.index[0]
                ].values  # If I don't use .values, I get a Series with the column names as the index

                # The shape of the values is (32, 1), which is 32 rows. I need 1 row, 32 columns.
                # Reshape to one row and an unknown number of columns (i.e., -1)

                first_row = first_row.reshape(1, -1)
                print(f"First row values: {first_row}")

                first_row_df = pd.DataFrame(
                    first_row, columns=folded_avg_monitor.columns
                )
                first_row_df.index = [
                    folded_avg_monitor.index[0]
                ]  # Set the index to the first time bin
                print("First row df:")
                print(first_row_df)

                # Now, we will concat the first row to the end of the folded_avg_monitor
                print(
                    "Concatenating first row to the end of the folded_avg_monitor...\n\n"
                )
                folded_avg_monitor = pd.concat(
                    [folded_avg_monitor, first_row_df], axis=0
                )

                folded_avg_monitor.index.name = "time_bin"
                folded_avg_monitor.to_csv(
                    current_directory
                    + "/folded_average_data"
                    + f"/folded_avg_{JUST_FILE_NAMES_BATCH[k][i]}",
                    sep="\t",
                )
                print(
                    f"Saved folded average data to {current_directory}/folded_average_data/folded_avg_{JUST_FILE_NAMES_BATCH[k][i]}"
                )

            print("\n\n")
            print("Calculating final average with SEM...")
            # Calculate final data
            for i, folded_avg_monitor in enumerate(FOLDED_AVG_BATCH[k]):
                if k > 0:
                    current_directory = DIRECTORY_BATCH[k][i]

                # Calculate the final data
                final_data = pd.DataFrame(index=folded_avg_monitor.index)

                final_data["final_mean"] = folded_avg_monitor.mean(axis=1) # axis 1 is row-wise
                final_data["SEM"] = folded_avg_monitor.sem(axis=1)

                FINAL_DATA_BATCH[k].append(final_data)

                # append first row to the end of the final data
                first_row = final_data.loc[final_data.index[0]].values
                first_row = first_row.reshape(1, -1)
                first_row_df = pd.DataFrame(first_row, columns=final_data.columns)
                first_row_df.index = [final_data.index[0]]
                final_data = pd.concat([final_data, first_row_df], axis=0)

                final_data.index = pd.to_datetime(final_data.index, format="%H:%M:%S").time
                final_data.index.name = "time_bin"

                final_data.to_csv(
                    current_directory
                    + "/final_avg_data"
                    + f"/final_data_{JUST_FILE_NAMES_BATCH[k][i]}",
                    sep="\t",
                )

                print(
                    f"Saved final data to {current_directory}/folded_average_data/final_data_{JUST_FILE_NAMES_BATCH[k][i]}"
                )

        print("\n\n")
        print("Data processing complete!")

    except Exception as e:
        messagebox.showerror("Error", str(e))


def processDataThread():
    try:
        threading.Thread(
            target=processData, daemon=True
        ).start()  # Daemon is false, to avoid abrupt termination when reading/writing files
    except Exception as e:
        messagebox.showerror("Error", str(e))


# End loadingThread


# Plot commands for GUI buttons
# Add argument for directory path


# Plot raw data. This function will be called when the 'Plot raw' button is clicked.
def rawPlot(monitor_files: list[pd.DataFrame]):
    try:
        t_analyze.rawPlot(
            monitor_files, JUST_FILE_NAMES, PREPARED_PATH
        )  # Add global variables as arguments if needed

        # Whereas the raw data consists of a LIST of monitors with a single path, the excluded animals data consists of a LIST of monitors with a LIST of paths.
        # How can I iterate through excluded animals data and pass the paths as separate strings while passing the single monitors as a list?
        # I simple pass the element as a new list. This way, I can iterate through the list of monitors and pass the list of paths as a single element.
        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_MONITOR_FILES):
            
                # create a fig_01 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_01"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_01")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_01 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_01 exists")

                # create a fig_02 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_02"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_02")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_02 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_02 exists")

                # Plot the raw for each unique excluded monitor data. 
                t_analyze.rawPlot(
                    [monitor], [JUST_FILE_NAMES_EXCLUDED[i]], EXCLUDE_ANIMALS_UNIQUE_PATH[i]
                )
        # Also note: The above is redundant, since the excluded animals data is already sliced. So it is not "raw" in the true sense.
        # I include this here just for completion.

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Plot raw sliced for all
def slicedPlot(monitor_slices: list[pd.DataFrame]):
    try:
        t_analyze.slicedPlot(
            monitor_slices,
            JUST_FILE_NAMES,
            SLICED_PATH,
            START_SLICE,
            END_SLICE,
            NUM_DAYS,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
        )  # Add global variables as arguments if needed

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_MONITOR_FILES):
            
                # create a fig_03 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_03"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_03")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_03 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_03 exists")

                # Plot the raw for each unique excluded monitor data. 
                t_analyze.slicedPlot(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                    START_SLICE,
                    END_SLICE,
                    NUM_DAYS,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Plot raw sliced for individuals
def slicedIndividualPlot(monitor_slices: list[pd.DataFrame]):
    try:
        t_analyze.slicedIndividualPlot(
            monitor_slices,
            JUST_FILE_NAMES,
            SLICED_PATH,
            START_SLICE,
            END_SLICE,
            NUM_DAYS,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
        )  # Add global variables as arguments if neede
        # Add global variables as arguments if needed

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_MONITOR_FILES):
            
                # create a fig_03 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_04"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_04")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_04 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_04 exists")

                # Plot the raw for each unique excluded monitor data. 
                t_analyze.slicedIndividualPlot(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                    START_SLICE,
                    END_SLICE,
                    NUM_DAYS,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def runningAveragePlot(smoothed_monitors: list[pd.DataFrame]):
    try:
        t_analyze.smoothedPlot(
            smoothed_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            START_SLICE,
            END_SLICE,
            SMOOTHING_WINDOW,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )


        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_SMOOTHED):
            
                # create a fig_03 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_05"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_05")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_05 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_05 exists")

                # Plot the raw for each unique excluded monitor data. 
                t_analyze.smoothedPlot(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    START_SLICE,
                    END_SLICE,
                    SMOOTHING_WINDOW,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def runningAverageIndividualPlot(smoothed_monitors: list[pd.DataFrame]):
    try:
        t_analyze.smoothedPlotIndividual(
            smoothed_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            SMOOTHING_WINDOW,
            START_SLICE,
            END_SLICE,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_SMOOTHED):
            
                # create a fig_03 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_06"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_06")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_06 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_06 exists")

                # Plot the raw for each unique excluded monitor data. 
                t_analyze.smoothedPlotIndividual(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    SMOOTHING_WINDOW,
                    START_SLICE,
                    END_SLICE,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def zscoredPlot(zscored_monitors: list[pd.DataFrame]):
    try:
        t_analyze.zscoredPlot(
            zscored_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            START_SLICE,
            END_SLICE,
            SMOOTHING_WINDOW,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_ZSCORED):
            
                # create a fig_06 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_07"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_07")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_07 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_07 exists")


                t_analyze.zscoredPlot(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    START_SLICE,
                    END_SLICE,
                    SMOOTHING_WINDOW,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def zscoredIndividualPlot(zscored_monitors: list[pd.DataFrame]):
    try:
        t_analyze.zscoredIndividual(
            zscored_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            SMOOTHING_WINDOW,
            START_SLICE,
            END_SLICE,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_ZSCORED):
            
                # create a fig_07 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_08"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_08")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_08 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_08 exists")

                t_analyze.zscoredIndividual(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    SMOOTHING_WINDOW,
                    START_SLICE,
                    END_SLICE,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def foldedAveragePlot(folded_avg_monitors: list[pd.DataFrame]):
    try:
        t_analyze.foldedPlot(
            folded_avg_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            "1900-01-01 00:00:00",
            "1900-01-01 23:59:00",
            SMOOTHING_WINDOW,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_FOLDED_AVG):
            
                # create a fig_08 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_09"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_09")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_09 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_09 exists")

                t_analyze.foldedPlot(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    "1900-01-01 00:00:00",
                    "1900-01-01 23:59:00",
                    SMOOTHING_WINDOW,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )
    except Exception as e:
        messagebox.showerror("Error", str(e))
        traceback.print_exc()


def foldedAverageIndividualPlot(folded_avg_monitors: list[pd.DataFrame]):
    try:
        t_analyze.foldedIndividual(
            folded_avg_monitors,
            JUST_FILE_NAMES,
            NUM_DAYS,
            SMOOTHING_WINDOW,
            "1900-01-01 00:00:00",
            "1900-01-01 23:59:00",
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH,
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_ANIMALS_FOLDED_AVG):
            
                # create a fig_09 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_10"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_10")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_10 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_10 exists")

                t_analyze.foldedIndividual(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    SMOOTHING_WINDOW,
                    "1900-01-01 00:00:00",
                    "1900-01-01 23:59:00",
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )
            
    except Exception as e:
        messagebox.showerror("Error", str(e))
        traceback.print_exc()

def finalAverageGraph(final_data: list[pd.DataFrame]):
    try:
        t_analyze.finalGraph(
            final_data,
            JUST_FILE_NAMES,
            NUM_DAYS,
            "1900-01-01 00:00:00",
            "1900-01-01 23:59:00",
            SMOOTHING_WINDOW,
            MORNING_RAMP_START,
            EVENING_RAMP_START,
            EVENING_RAMP_END,
            RAMP_TIME,
            RAMP_END_DATE,
            SLICED_PATH
        )

        if EXCLUDE_COMMIT:
            for i, monitor in enumerate(EXCLUDED_FINAL_DATA):
            
                # create a fig_10 directory for each monitor
                if not os.path.exists(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_11"):
                    os.makedirs(EXCLUDE_ANIMALS_UNIQUE_PATH[i] + "/fig_11")
                    print(f"Created {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_11 directory")
                else:
                    print(f"OK. {EXCLUDE_ANIMALS_UNIQUE_PATH[i]}/fig_11 exists")

                t_analyze.finalGraph(
                    [monitor],
                    [JUST_FILE_NAMES_EXCLUDED[i]],
                    NUM_DAYS,
                    "1900-01-01 00:00:00",
                    "1900-01-01 23:59:00",
                    SMOOTHING_WINDOW,
                    MORNING_RAMP_START,
                    EVENING_RAMP_START,
                    EVENING_RAMP_END,
                    RAMP_TIME,
                    RAMP_END_DATE,
                    EXCLUDE_ANIMALS_UNIQUE_PATH[i],
                )

    except Exception as e:
        messagebox.showerror("Error", str(e))
        traceback.print_exc()


# Main GUI
root = tk.Tk()
root.configure(bg="#90EE90", bd=25, relief="ridge", cursor="arrow")
all_widgets = []
font_size = 14

# icon bitmap
root.iconbitmap("icon/fly.ico")

# Create a scale widget for the font size
fontsize_scale_label = tk.Label(
    root,
    text="Slider to adjust font size",
    font=("sans", font_size, "bold"),
)
fontsize_scale_label.pack()
all_widgets.append(fontsize_scale_label)

font_scale_widget = tk.Scale(
    root,
    from_=5,
    to=60,
    orient="horizontal",
    length=1000,
    sliderlength=50,
    width=50,
    command=update_font_size,
    font=("sans", font_size, "bold"),
)
font_scale_widget.pack()
all_widgets.append(font_scale_widget)

root.title("Damn Simple: A GUI for Simple Visualization of DAM Data")
root.geometry("1200x1200")

#######################
# ENTRY FIELDS
#######################

directory_label = tk.Label(
    root,
    text="Directory name (contains the data .txt files):",
    font=("sans", font_size, "bold"),
)
directory_label.pack()
directory_entry = tk.Entry(root, font=("sans", font_size))
directory_entry.pack()
all_widgets.append(directory_label)
all_widgets.append(directory_entry)

start_time_label = tk.Label(
    root,
    text="Start datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:",
    font=("sans", font_size, "bold"),
)
start_time_label.pack()
start_time_entry = tk.Entry(root, font=("sans", font_size))
start_time_entry.pack()
all_widgets.append(start_time_label)
all_widgets.append(start_time_entry)

end_time_label = tk.Label(
    root,
    text="End datetime for slicing (YYYY-MM-DD HH:MM:SS). Keep formatting exact:",
    font=("sans", font_size, "bold"),
)
end_time_label.pack()
end_time_entry = tk.Entry(root, font=("sans", font_size))
end_time_entry.pack()
all_widgets.append(end_time_label)
all_widgets.append(end_time_entry)

DD_start_date_label = tk.Label(
    root,
    text="Start date for DD analysis (YYYY-MM-DD)\nEnter out-of-bounds date for no DD analysis:",
    font=("sans", font_size, "bold"),
)
DD_start_date_label.pack()
DD_start_date_entry = tk.Entry(root, font=("sans", font_size))
DD_start_date_entry.pack()
all_widgets.append(DD_start_date_label)
all_widgets.append(DD_start_date_entry)

morning_ramp_label = tk.Label(
    root,
    text="Morning ramp time (HH:MM), e.g., 6:00 for 6 AM:",
    font=("sans", font_size, "bold"),
)
morning_ramp_label.pack()
morning_ramp_entry = tk.Entry(root, font=("sans", font_size))
morning_ramp_entry.pack()
all_widgets.append(morning_ramp_label)
all_widgets.append(morning_ramp_entry)

evening_ramp_label = tk.Label(
    root,
    text="Evening ramp time (HH:MM), e.g., 18:00 for 6 PM:",
    font=("sans", font_size, "bold"),
)
evening_ramp_label.pack()
evening_ramp_entry = tk.Entry(root, font=("sans", font_size))
evening_ramp_entry.pack()
all_widgets.append(evening_ramp_label)
all_widgets.append(evening_ramp_entry)

night_start_label = tk.Label(
    root,
    text="Night start time (HH:MM), e.g., 21:00 for 9 PM:",
    font=("sans", font_size, "bold"),
)
night_start_label.pack()
night_start_entry = tk.Entry(root, font=("sans", font_size))
night_start_entry.pack()
all_widgets.append(night_start_label)
all_widgets.append(night_start_entry)

ramp_duration_label = tk.Label(
    root,
    text="Duration of ramp in hours (e.g., 1.5):",
    font=("sans", font_size, "bold"),
)
ramp_duration_label.pack()
ramp_duration_entry = tk.Entry(root, font=("sans", font_size))
ramp_duration_entry.pack()
all_widgets.append(ramp_duration_label)
all_widgets.append(ramp_duration_entry)

running_average_label = tk.Label(
    root,
    text="Running average window size (e.g., 30):",
    font=("sans", font_size, "bold"),
)
running_average_label.pack()
all_widgets.append(running_average_label)

running_average_entry = tk.Entry(root, font=("sans", font_size))
running_average_entry.pack()
all_widgets.append(running_average_entry)

#######################
# BUTTONS AND CHECKS
#######################

# Load the data and set major global variables
load_button = tk.Button(
    root, text="1. Load data", command=loadData, font=("sans", font_size)
)
load_button.pack()
all_widgets.append(load_button)

# Define excluded animals
EXCLUDE_ANIMALS_VAR = tk.BooleanVar()
EXCLUDE_ANIMALS_VAR.trace_add("write", lambda *args: onExclude())
exclude_animals_checkbutton = tk.Checkbutton(
    root,
    text="2. Define exclusions (even if none)",
    variable=EXCLUDE_ANIMALS_VAR,
    font=("sans", font_size),
)
exclude_animals_checkbutton.pack()
all_widgets.append(exclude_animals_checkbutton)
all_widgets.append(exclude_animals_checkbutton)

# Commit the exclusions, if any. Print globals to verify correctness and the exclusions.
commit_button = tk.Button(
    root,
    text="3. Commit exclusions and process data",
    command=commit,
    font=("sans", font_size),
)
commit_button.pack()
all_widgets.append(commit_button)

# BUTTONS FOR PLOTTING
# Create a separate frame for the buttons, so I can use a grid layout
button_frame = tk.Frame(root)
button_frame.configure(bg="#90EE90")
button_frame.pack()
button_frame_label = tk.Label(
    button_frame, text="Plotting options", font=("sans", font_size, "bold")
)
button_frame_label.grid(row=0, column=0, columnspan=5)
all_widgets.append(button_frame_label)


# Plot raw data
plot_raw_button_label = tk.Label(
    button_frame, text="Fig. 1 & 2", font=("sans", font_size - 2)
)
plot_raw_button_label.grid(row=1, column=0)
all_widgets.append(plot_raw_button_label)

plot_raw_button = tk.Button(
    button_frame,
    text="Raw data",
    command=lambda: rawPlot(MONITOR_FILES),
    font=("sans", font_size),
)
plot_raw_button.grid(row=2, column=0)
all_widgets.append(plot_raw_button)

# Plot sliced
plot_sliced_button_label = tk.Label(
    button_frame, text="Fig. 3", font=("sans", font_size - 2)
)
plot_sliced_button_label.grid(row=1, column=1)
all_widgets.append(plot_sliced_button_label)

plot_sliced_button = tk.Button(
    button_frame,
    text="Sliced all",
    command=lambda: slicedPlot(MONITOR_SLICES),
    font=("sans", font_size),
)
plot_sliced_button.grid(row=2, column=1)
all_widgets.append(plot_sliced_button)

# Plot sliced for individuals
plot_sliced_individual_button_label = tk.Label(
    button_frame, text="Fig. 4", font=("sans", font_size - 2)
)
plot_sliced_individual_button_label.grid(row=1, column=2)
all_widgets.append(plot_sliced_individual_button_label)

plot_sliced_individual_button = tk.Button(
    button_frame,
    text="Sliced subplots",
    command=lambda: slicedIndividualPlot(MONITOR_SLICES),
    font=("sans", font_size),
)
plot_sliced_individual_button.grid(row=2, column=2)
all_widgets.append(plot_sliced_individual_button)

# Plot running average all
plot_running_average_button_label = tk.Label(
    button_frame, text="Fig. 5", font=("sans", font_size - 2)
)
plot_running_average_button_label.grid(row=1, column=3)
all_widgets.append(plot_running_average_button_label)

plot_running_average_button = tk.Button(
    button_frame,
    text="Run. avg. all",
    command=lambda: runningAveragePlot(SMOOTHED_MONITORS),
    font=("sans", font_size),
)
plot_running_average_button.grid(row=2, column=3)
all_widgets.append(plot_running_average_button)

# Plot running average individuals
plot_running_average_individual_button_label = tk.Label(
    button_frame, text="Fig. 6", font=("sans", font_size - 2)
)
plot_running_average_individual_button_label.grid(row=1, column=4)
all_widgets.append(plot_running_average_individual_button_label)

plot_running_average_individual_button = tk.Button(
    button_frame,
    text="Run. avg. subplots",
    command=lambda: runningAverageIndividualPlot(SMOOTHED_MONITORS),
    font=("sans", font_size),
)
plot_running_average_individual_button.grid(row=2, column=4)
all_widgets.append(plot_running_average_individual_button)

# Plot z-scored all
plot_zscored_button_label = tk.Label(
    button_frame, text="Fig. 7", font=("sans", font_size - 2)
)
plot_zscored_button_label.grid(row=3, column=0)
all_widgets.append(plot_zscored_button_label)

plot_zscored_button = tk.Button(
    button_frame,
    text="Z-scored all",
    command=lambda: zscoredPlot(ZSCORED_MONITORS),
    font=("sans", font_size),
)
plot_zscored_button.grid(row=4, column=0)
all_widgets.append(plot_zscored_button)

# Plot z-scored individuals
plot_zscored_individual_button_label = tk.Label(
    button_frame, text="Fig. 8", font=("sans", font_size - 2)
)
plot_zscored_individual_button_label.grid(row=3, column=1)
all_widgets.append(plot_zscored_individual_button_label)

plot_zscored_individual_button = tk.Button(
    button_frame,
    text="Z-scored subplots",
    command=lambda: zscoredIndividualPlot(ZSCORED_MONITORS),
    font=("sans", font_size),
)
plot_zscored_individual_button.grid(row=4, column=1)
all_widgets.append(plot_zscored_individual_button)

# Plot folded average all
plot_folded_avg_button_label = tk.Label(
    button_frame, text="Fig. 9", font=("sans", font_size - 2)
)
plot_folded_avg_button_label.grid(row=3, column=2)
all_widgets.append(plot_folded_avg_button_label)

plot_folded_avg_button = tk.Button(
    button_frame,
    text="Folded avg. all",
    command=lambda: foldedAveragePlot(FOLDED_AVG_MONITORS),
    font=("sans", font_size),
)
plot_folded_avg_button.grid(row=4, column=2)
all_widgets.append(plot_folded_avg_button)


# Plot folded average individuals
plot_folded_avg_individual_button_label = tk.Label(
    button_frame, text="Fig. 10", font=("sans", font_size - 2)
)
plot_folded_avg_individual_button_label.grid(row=3, column=3)
all_widgets.append(plot_folded_avg_individual_button_label)

plot_folded_avg_individual_button = tk.Button(
    button_frame,
    text="Folded avg. subplots",
    command=lambda: foldedAverageIndividualPlot(FOLDED_AVG_MONITORS),
    font=("sans", font_size),
)
plot_folded_avg_individual_button.grid(row=4, column=3)
all_widgets.append(plot_folded_avg_individual_button)

# Plot final graph, which is the average FOLDED average among all individuals
plot_final_graph_button_label = tk.Label(
    button_frame, text="Fig. 11", font=("sans", font_size - 2)
)
plot_final_graph_button_label.grid(row=3, column=4)
all_widgets.append(plot_final_graph_button_label)

plot_final_graph_button = tk.Button(
    button_frame,
    text="Final graph",
    command=lambda: finalAverageGraph(FINAL_DATA),
    font=("sans", font_size),
)
plot_final_graph_button.grid(row=4, column=4)
all_widgets.append(plot_final_graph_button)

#######################
# END OF BUTTONS
#######################

#######################
# HANDLING OUTPUT TEXT
#######################


# scale output text
scale_output_label = tk.Label(
    root,
    text="Output Text",
    font=("sans", font_size, "bold"),
)
scale_output_label.pack()
all_widgets.append(scale_output_label)

scale_output_text = tk.Scale(
    root, from_=10, to=30, length=1000, orient="horizontal", command=resize_output_text
)
scale_output_text.pack()
all_widgets.append(scale_output_text)

# output text widget
output_text = tk.Text(root, width=100, height=30, wrap=tk.WORD, font=("sans", 8))
output_text.pack()

# Create logger instance using our widget
# Logs are saved with current timestampe

logger = Logger(output_text, LOG_FILE)

# Print statements normally call sys.stdout.write,...
# But we redirect output to our logger instance
# Now, print calls logger.write, which appends the text to the Text widget
sys.stdout = logger


def check_queue():
    logger.check_queue()
    root.after(100, check_queue)  # Check every 100 ms. This is a recursive call.


root.after(100, check_queue)

# Other formatting for my widgets
for widget in all_widgets:
    if isinstance(widget, tk.Button) or isinstance(widget, tk.Checkbutton):
        widget.configure(bg="#00FF7F", border=5, relief="raised", cursor="hand2")
    elif isinstance(widget, tk.Label):
        widget.configure(bg="#90EE90")
    elif isinstance(widget, tk.Scale):
        widget.configure(bg="#90EE90", bd=5, relief="ridge", cursor="hand2")

root.mainloop()
