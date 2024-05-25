# tkinter for GUI
import tkinter as tk
from tkinter import ttk  # access to the Tk themed widget set
from tkinter import ttk  # access to the Tk themed widget set
from tkinter import messagebox

import threading

import os
import glob
import sys  # For outputting stoud to the text widget
import sys  # For outputting stoud to the text widget

import pandas as pd

# import matplotlib.dates as mdates
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
        global SMOOTHED_DIR_PATH
        global Z_SCORED_PATH
        global FOLDED_AVERAGE_PATH

        global MONITOR_FILES
        global MONITOR_SLICES
        global MONITOR_FILE_NAMES
        global JUST_FILE_NAMES

        global SMOOTHED_MONITORS

        global AVG_AND_STD
        global ZSCORED_MONITORS

        global FOLDED_AVG_MONITORS


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
        SMOOTHED_DIR_PATH = SLICED_PATH + "/smoothed_data"
        Z_SCORED_PATH = SLICED_PATH + "/z_scored_data"
        FOLDED_AVERAGE_PATH = SLICED_PATH + "/folded_average_data"
   

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

        # Smoothed data directory
        if not os.path.exists(SMOOTHED_DIR_PATH):
            os.makedirs(SMOOTHED_DIR_PATH)
            print("Smoothed data directory created: ", SMOOTHED_DIR_PATH)
        else:
            print("OK. Smoothed data directory exists: ", SMOOTHED_DIR_PATH)

        # Z-scored data directory
        if not os.path.exists(Z_SCORED_PATH):
            os.makedirs(Z_SCORED_PATH)
            print("Z-scored data directory created: ", Z_SCORED_PATH)
        else:
            print("OK. Z-scored data directory exists: ", Z_SCORED_PATH)

        # Folded average data directory
        if not os.path.exists(FOLDED_AVERAGE_PATH):
            os.makedirs(FOLDED_AVERAGE_PATH)
            print("Folded average data directory created: ", FOLDED_AVERAGE_PATH)
        else:
            print("OK. Folded average data directory exists: ", FOLDED_AVERAGE_PATH)

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

        # THIS NEXT SECTION MAY BE PLACED INTO A SEPARATE FUNCTION FOR REUSABILITY
        # Calculate running average (in minutes) for each animal column
        SMOOTHED_MONITORS = (
            []
        )  # Holds the smoothed data for each monitor, as PandasData frames

        for i, monitor in enumerate(MONITOR_SLICES):
            # We define a FixedForwardWindowIndexer to calculate the forward looking moving average
            # This is slightly different than the default moving average, which is backward looking and excludes the first range of values by leaving them blank.
            indexer = pd.api.indexers.FixedForwardWindowIndexer(
                window_size=SMOOTHING_WINDOW
            )

            smoothed_monitor = pd.DataFrame()

            # Let's create a df to hold basic statistics...mean and std
            AVG_AND_STD = pd.DataFrame(columns=monitor.columns, index=["mean", "std"])
            AVG_AND_STD.index.name = "statistic"

            for column in monitor.columns:
                smoothed_column_name = column + "_run_avg_" + str(SMOOTHING_WINDOW)
                smoothed_monitor[smoothed_column_name] = (
                    monitor[column].rolling(window=indexer, min_periods=1).mean()
                )  # Change this to a forward looking moving average

                # Let's also calculate average and std here.
                # Note that avg and std are calculated from the SMOOTHED data.
                AVG_AND_STD.loc["mean", column] = smoothed_monitor[
                    smoothed_column_name
                ].mean()
                AVG_AND_STD.loc["std", column] = smoothed_monitor[
                    smoothed_column_name
                ].std()

            smoothed_monitor.index = monitor.index
            smoothed_monitor.to_csv(
                SMOOTHED_DIR_PATH
                + f"/smoothed_"
                + str(SMOOTHING_WINDOW)
                + "min_"
                + JUST_FILE_NAMES[i],
                sep="\t",
            )

            AVG_AND_STD.to_csv(
                SMOOTHED_DIR_PATH + f"/column_average_and_std_" + JUST_FILE_NAMES[i],
                sep="\t",
            )
            SMOOTHED_MONITORS.append(smoothed_monitor)

            print(
                f"Calculated running average of {SMOOTHING_WINDOW} min for {JUST_FILE_NAMES[i]}"
            )

        # Calculate avg and std for each animal column
        print("\n\n")
        print("Converting smoothed values to z-score...")
        ZSCORED_MONITORS = []
        for i, smoothed_monitor in enumerate(
            SMOOTHED_MONITORS
        ):  # We will use the smoothed data to calculate z-scores

            # I define the zscored_monitor to have the original column names (e.g., 'animal_1', 'animal_2', etc.)
            # It will use the smoothed_monitor index, which is the datetime index. Any of the sliced indices would work.
            # Define our zscored_monitor
            zscored_monitor = pd.DataFrame(
                columns=MONITOR_FILES[i].columns, index=smoothed_monitor.index
            )

            for j, column in enumerate(zscored_monitor.columns):
                # Now, for each column in the zscored_monitor, I will assign it to a column of z-scores
                # which are calculated from the smoothed_monitor files.
                # I will use the mean and std from the AVG_AND_STD df to calculate the z-scores.
                zscored_monitor[column] = smoothed_monitor.iloc[:, j].apply(
                    lambda x: (x - AVG_AND_STD.loc["mean", column])
                    / AVG_AND_STD.loc["std", column]
                )

            ZSCORED_MONITORS.append(zscored_monitor)
            zscored_monitor.to_csv(
                Z_SCORED_PATH
                + f"/zscored_{SMOOTHING_WINDOW}_min_run_avg_{JUST_FILE_NAMES[i]}",
                sep="\t",
            )
            print(
                f"Saved z-scored data to {Z_SCORED_PATH + f'/zscored_{SMOOTHING_WINDOW}_min_run_avg_{JUST_FILE_NAMES[i]}' }"
            )

        print("\n\n")
        
        # Calculate the folded average
        print("Calculating the folded average...")
        FOLDED_AVG_MONITORS = []

        for i, zscored_monitor in enumerate(ZSCORED_MONITORS):
            # New folded_avg_monitor will have indices up to 24 hrs. Here, since the index is in minutes, we will have 1440 minutes in a day + 1,...
            # so that the index goes from 00:00 to 00:00 the next day.
            folded_avg_monitor = pd.DataFrame(columns = zscored_monitor.columns)
            folded_avg_monitor.index.name = "time_bin"
            for column in zscored_monitor:
                # Fold the data. We can group by the datetime's time, and then calculate the mean for each time.
                folded_avg_monitor[column] = zscored_monitor[column].groupby(zscored_monitor.index.time).mean()

            folded_avg_monitor = folded_avg_monitor.append(folded_avg_monitor.iloc[1,:]) # Append the first row to the end to make the plot look nice
            FOLDED_AVG_MONITORS.append(folded_avg_monitor)
            folded_avg_monitor.to_csv(FOLDED_AVERAGE_PATH + f"/folded_avg_{JUST_FILE_NAMES[i]}", sep="\t")
            print(f"Saved folded average data to {FOLDED_AVERAGE_PATH + f'/folded_avg_{JUST_FILE_NAMES[i]}' }")
            



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
        print("PREPARED_DATA_PATH: ", PREPARED_DATA_PATH)
        print("PREPARED_PATH: ", PREPARED_PATH)
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


# This function also commits the exclusions defined in the check boxes. It saves the excluded animals data file.
def printExcluded():
    global EXCLUDED_ANIMALS_BOOLS
    global EXCLUDED_ANIMALS_MONITOR_FILES  # List of pd.DataFrames for future plotting
    global EXCLUDED_ANIMALS_SMOOTHED
    global EXCLUDED_ANIMALS_AVG_STD
    global EXCLUDED_ANIMALS_ZSCORED

    global EXCL_STR     # Later defined by the unique set of excluded animals

    EXCL_STR = "excl_"  # This will be used to create a specific directory for the excluded animals

    EXCLUDED_ANIMALS_BOOLS = []
    EXCLUDED_ANIMALS_MONITOR_FILES = []

    print("Excluded animals based on Boolean-slicing:")
    # Re-initialize the list of boolean values for each animal to exclude

    for i, slice in enumerate(MONITOR_SLICES):
        # List comprehension to get a list of boolean values from tkinter check variables
        # The boolean list is then appended to my global list
        EXCLUDED_ANIMALS_BOOLS.append([var.get() for var in ANIMALS_TO_EXCLUDE[i]])
        excluded_animal_columns = slice.columns[EXCLUDED_ANIMALS_BOOLS[i]]
        print(
            f"{JUST_FILE_NAMES[i]}: Excluded animal indices: {excluded_animal_columns}"
        )

        # Concatenate the animal numbers to a string, which will be used to create a specific directory.
        # This lets us make multiple unique exclusions while saving the data.
        # And each exclusion is saved to a specific directory, for identification purposes.
        for j, bool in enumerate(EXCLUDED_ANIMALS_BOOLS[i]):
            if bool:
                EXCL_STR += "_" + str(j + 1)

        if not os.path.exists(EXCLUDE_ANIMALS_PATH_DATA + EXCL_STR):
            os.makedirs(EXCLUDE_ANIMALS_PATH_DATA + EXCL_STR)
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
            EXCLUDE_ANIMALS_PATH_DATA + EXCL_STR + "/excluded_" + JUST_FILE_NAMES[i],
            sep="\t",
        )
        print(
            f"Excluded animals saved to {EXCLUDE_ANIMALS_PATH_DATA + EXCL_STR + '/excluded_' + JUST_FILE_NAMES[i]}"
        )

        print("\n\n")


# Plot functions


# Plot raw data. This function will be called when the 'Plot raw' button is clicked.
def rawPlot(monitor_files: list[pd.DataFrame]):
    try:
        t_analyze.rawPlot(
            monitor_files, JUST_FILE_NAMES, PREPARED_PATH
        )  # Add global variables as arguments if needed
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
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Main GUI
root = tk.Tk()
root.configure(bg="#90EE90", bd=25, relief="ridge", cursor="arrow")
all_widgets = []
font_size = 14

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
    from_=10,
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
    root, text="Load data", command=loadData, font=("sans", font_size)
)
load_button.pack()
all_widgets.append(load_button)

# Define excluded animals
EXCLUDE_ANIMALS_VAR = tk.BooleanVar()
EXCLUDE_ANIMALS_VAR.trace_add("write", lambda *args: onExclude())
exclude_animals_checkbutton = tk.Checkbutton(
    root,
    text="Exclude Animals? Check for 'yes':",
    variable=EXCLUDE_ANIMALS_VAR,
    font=("sans", font_size),
)
exclude_animals_checkbutton.pack()
all_widgets.append(exclude_animals_checkbutton)
all_widgets.append(exclude_animals_checkbutton)

# Commit the exclusions, if any. Print globals to verify correctness and the exclusions.
print_globals_button = tk.Button(
    root,
    text="Print globals and commit exclusions",
    command=printGlobals,
    font=("sans", font_size),
)
print_globals_button.pack()
all_widgets.append(print_globals_button)

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
    button_frame, text="Fig. 1 & 2", font=("sans", font_size-2)
)
plot_raw_button_label.grid(row=1, column=0)
all_widgets.append(plot_raw_button_label)

plot_raw_button = tk.Button(
    button_frame,
    text="Raw data",
    command=lambda: rawPlot(MONITOR_FILES),
    font=("sans", font_size)
)
plot_raw_button.grid(row=2, column=0)
all_widgets.append(plot_raw_button)

# Plot sliced
plot_sliced_button_label = tk.Label(
    button_frame, text="Fig. 3", font=("sans", font_size-2)
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
    button_frame, text="Fig. 4", font=("sans", font_size-2)
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
    button_frame, text="Fig. 5", font=("sans", font_size-2)
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
    button_frame, text="Fig. 6", font=("sans", font_size-2)
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
    button_frame, text="Fig. 7", font=("sans", font_size-2)
)
plot_zscored_button_label.grid(row=3, column=1)
all_widgets.append(plot_zscored_button_label)

plot_zscored_button = tk.Button(
    button_frame,
    text="Z-scored all",
    command=lambda: zscoredPlot(ZSCORED_MONITORS),
    font=("sans", font_size),
)
plot_zscored_button.grid(row=4, column=1)
all_widgets.append(plot_zscored_button)

# Plot z-scored individuals
plot_zscored_individual_button_label = tk.Label(
    button_frame, text="Fig. 8", font=("sans", font_size-2)
)
plot_zscored_individual_button_label.grid(row=3, column=2)
all_widgets.append(plot_zscored_individual_button_label)

plot_zscored_individual_button = tk.Button(
    button_frame,
    text="Z-scored subplots",
    command=lambda: zscoredIndividualPlot(ZSCORED_MONITORS),
    font=("sans", font_size),
)
plot_zscored_individual_button.grid(row=4, column=2)
all_widgets.append(plot_zscored_individual_button)



#######################
# END OF BUTTONS
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
output_text = tk.Text(root, width=100, height=30, wrap=tk.WORD, font=("sans", 12))
output_text.pack()

# Redirect the stdout to the text widget
sys.stdout = TextRedirector(output_text)

# Other formatting for my widgets
for widget in all_widgets:
    if isinstance(widget, tk.Button) or isinstance(widget, tk.Checkbutton):
        widget.configure(bg="#00FF7F", border=5, relief="raised", cursor="hand2")
    elif isinstance(widget, tk.Label):
        widget.configure(bg="#90EE90")
    elif isinstance(widget, tk.Scale):
        widget.configure(bg="#90EE90", bd=5, relief="ridge", cursor="hand2")


root.mainloop()
