import pandas as pd

import os
import glob

import matplotlib
import matplotlib.pyplot as plt
from datetime import time as dt_time
from datetime import datetime, timedelta
import matplotlib.dates as mdates


###################################################
################ FUNCTION DEFINITIONS #############
###################################################
# These are the minor plotting functions that will be used in the main tasks.
# Algorithm for drawing LD bars in graphs
def drawLD(
    minute_ticks,
    ax1,
    morning_ramp_start=dt_time(6, 0),
    evening_ramp_start=dt_time(18, 0),
    evening_ramp_end=dt_time(21, 0),
    ramp_time=timedelta(hours=3),
    ramp_end_date=datetime.strptime("9999-12-30", "%Y-%m-%d"),
):
    # Iterate through the minute_ticks. That is, we iterate through each minute in the range of dates we are plotting.
    for minute_tick in minute_ticks:  # minute_tick is the current datetime in the loop
        if (
            minute_tick.date() <= ramp_end_date.date()
        ):  # If the date is less than or equal to the ramp_end_date
            # First two conditionals draw the twilight periods
            if minute_tick == datetime.combine(
                minute_tick.date(), morning_ramp_start
            ):  # The morning ramp starts here
                ax1.axvspan(
                    minute_tick, minute_tick + ramp_time, facecolor="gray", alpha=0.2
                )

            if minute_tick == datetime.combine(
                minute_tick.date(), evening_ramp_start
            ):  # The evening ramp starts here
                ax1.axvspan(
                    minute_tick, minute_tick + ramp_time, facecolor="gray", alpha=0.2
                )

            # Drawing the night (black) bars requires consideration of three cases.
            # This draws the night bars. Note that I create a new datetime object with the date and the evening_ramp_end time.
            # This is because we must compare times within the same date. The user only enters time, however. Thus, I use the input time and the current date of the minute tick.

            # Case 1: The evening_ramp_end is less than the morning_ramp_start
            if datetime.combine(
                minute_tick.date(), evening_ramp_end
            ) < datetime.combine(minute_tick.date(), morning_ramp_start):
                if minute_tick > datetime.combine(
                    minute_tick.date(), evening_ramp_end
                ) and (
                    minute_tick
                    < datetime.combine(minute_tick.date(), morning_ramp_start)
                ):
                    ax1.axvspan(
                        minute_tick,
                        minute_tick + pd.Timedelta(minutes=1),
                        facecolor="black",
                        alpha=0.3,
                    )

            # Case 2: The evening_ramp_end is greater than the morning_ramp_start
            elif datetime.combine(
                minute_tick.date(), evening_ramp_end
            ) > datetime.combine(minute_tick.date(), morning_ramp_start):
                if minute_tick > datetime.combine(minute_tick.date(), evening_ramp_end):
                    ax1.axvspan(
                        minute_tick,
                        minute_tick + pd.Timedelta(minutes=1),
                        facecolor="black",
                        alpha=0.3,
                    )
                # Section of night BEFORE the morning ramp starts.
                if minute_tick < datetime.combine(
                    minute_tick.date(), morning_ramp_start
                ):
                    ax1.axvspan(
                        minute_tick,
                        minute_tick + pd.Timedelta(minutes=1),
                        facecolor="black",
                        alpha=0.3,
                    )

            # Case 3: They are equal
            elif datetime.combine(
                minute_tick.date(), evening_ramp_end
            ) == datetime.combine(minute_tick.date(), morning_ramp_start):
                # Do nothing
                pass
        else:
            # If the date is greater than the ramp_end_date, then we are in the DD period.
            ax1.axvspan(
                minute_tick,
                minute_tick + pd.Timedelta(minutes=1),
                facecolor="black",
                alpha=0.3,
            )


# End LD algorithm

####################
# BASIC PLOTTING FUNCTIONS
####################


# First two functions handle the raw, unsliced data
# FOR PLOTTING ALL ANIMALS
def plot_raw(data: pd.DataFrame, _i: int, monitor_name: str = "Monitor"):
    data.plot(kind="line", legend=False, figsize=(12, 8))  # figsize is in inches

    # Create DataFormatter for the x-axis
    xformatter = mdates.DateFormatter("%Y-%m-%d")

    # get the current axes
    axs = plt.gca()

    # set the x-axis formatter!
    axs.xaxis.set_major_formatter(xformatter)

    axs.xaxis.set_major_locator(
        mdates.DayLocator(interval=1)
    )  # Set major tick every 3 days
    axs.xaxis.set_major_formatter(
        mdates.DateFormatter("%d %b %y")
    )  # Format the datetime as 'HH:MM', instead of showing the whole dt
    plt.tick_params("x", labelrotation=90)

    # Customize the aesthetics
    plt.title(monitor_name + " Raw Locomotor Activity")
    plt.xlabel("Local Time")
    plt.ylabel("Counts per minute")

    plt.grid(False)
    return plt


# Create a figure and a grid of subplots
# FOR PLOTTING INDIVIDUAL ANIMALS
def subplots_raw(
    data: pd.DataFrame, _j: int, days: int = 1, monitor_name: str = "Monitor"
):
    # Grid dimensions for our main figure that holds our axs subplots
    nrows = 4
    ncols = 8

    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(30, 15)
    )  # nrows = 4 and ncols = 8 for a 4x8 grid of subplots

    # We now have a 4x8 matrix of Axes objects corresponding to our subplot grid.
    # To make this easier to iterate through, I can flatten it into a 1D array.
    axs = axs.flatten()

    for i, (name, series) in enumerate(
        data.items()
    ):  # items() returns (column names, Series) pairs that can be iterated over
        axs[i].plot(
            series.index, series.values
        )  # Plots index on x-axis, and series' values on y-axis
        axs[i].set_title(name)

        # Aesthetics
        # Reformat the x-axis labels using datetime
        axs[i].xaxis.set_major_locator(
            mdates.DayLocator(interval=days)
        )  # Set major tick every 3 days
        axs[i].xaxis.set_major_formatter(
            mdates.DateFormatter("%b %d")
        )  # Format the datetime as 'HH:MM', instead of showing the whole dt

        axs[i].tick_params("x", labelrotation=90)
        axs[i].set_ylabel("counts/min", fontsize=12)
        axs[i].set_xlabel("date", fontsize=8)

    fig.suptitle(monitor_name + " Raw Locomotor Activity Individuals", fontsize=20)
    plt.tight_layout()
    return plt


# Next two functions handle all sliced data (including smoothed, zscored, etc)


# FOR PLOTTING ALL ANIMALS
def plot_sliced_all(
    data: pd.DataFrame,
    num_days: int,
    start_slice: str,
    end_slice: str,
    monitor_name: str = "",
    morning_ramp_start=dt_time(6, 0),
    evening_ramp_start=dt_time(18, 0),
    evening_ramp_end=dt_time(21, 0),
    ramp_time=timedelta(hours=3),
    ramp_end_date=datetime.strptime("9999-12-30", "%Y-%m-%d"),
    graph_title: str = "Untitled",
    yaxis_label: str = "Y-axis",
    xaxis_label: str = "X-axis",
    xticks: str = "6h",
):
    # Assuming `data` is your DataFrame, we will create a plot with a single subplot.
    fig, ax1 = plt.subplots(figsize=(12, 12))
    # Thus, we only have one Axes object, and that's our entire dataframe.
    data.plot(ax=ax1, legend=False)

    # We need to do this MANUALLY
    # Manually set the x-axis limits to a smaller range
    start_time = pd.to_datetime(
        start_slice
    )  # replace 'your_start_time' with the actual start time. I use slice_start from earlier
    end_time = start_time + timedelta(
        hours=24 * num_days
    )  # end time is start_time plus 240 hours later
    ax1.set_xlim([start_time, end_time])  # set the x-axis limit

    # This date range will set the x-axis ticks. We go from start to end, defined intervals. Default is 6h.
    date_range = pd.date_range(start=start_time, end=end_time, freq=xticks)

    # Set the x-axis ticks. There is one tick per interval, as defined in date_range
    ax1.set_xticks(date_range)

    # Generate the labels for the ticks
    # Converts each item in date_range to a string, with the format %H:%M drawn from the date time.
    labels = [interval.strftime("%H:%M") for interval in date_range]

    # Set the x-axis labels
    ax1.set_xticklabels(
        labels, rotation=90
    )  # Rotate the labels to make them more readable

    # This date range is for drawing the LD bars at minute precision.
    # Minute ticks, so we have minute precision in specifying the light and dark bars
    minute_ticks = pd.date_range(start=start_time, end=end_time, freq="1min")

    ### DRAW LIGHT AND DARK BARS ###
    drawLD(
        minute_ticks,
        ax1,
        morning_ramp_start,
        evening_ramp_start,
        evening_ramp_end,
        ramp_time,
        ramp_end_date,
    )
    ### END OF LIGHT AND DARK BARS ###

    # Set titles and axes names
    ax1.set_title(
        monitor_name
        + f" {graph_title} "  # Unique str for specifying type of data of the graph.
        + str(num_days)
        + "_days_"
        + start_slice
        + "_to_"
        + end_slice,
        fontsize=16,
    )
    ax1.set_ylabel(yaxis_label, fontsize=14)
    ax1.set_xlabel(xaxis_label, fontsize=14)

    plt.tight_layout()
    return plt


# FOR PLOTTING SEPARATE INDIVIDUALS VIA SUBPLOTS
def plot_sliced_individuals(
    data: pd.DataFrame,
    num_days: int,
    start_time: str,
    end_time: str,
    days: int = 1,
    monitor_name: str = "",
    morning_ramp_start=dt_time(6, 0),
    evening_ramp_start=dt_time(18, 0),
    evening_ramp_end=dt_time(21, 0),
    ramp_time=timedelta(hours=3),
    ramp_end_date=datetime.strptime("9999-12-30", "%Y-%m-%d"),
    graph_title: str = "Untitled",
    yaxis_label: str = "Y-axis",
    xaxis_label: str = "X-axis",
):
    # Grid dimensions for our main figure that holds our axs subplots
    nrows = 4
    ncols = 8

    fig, axs = plt.subplots(
        nrows=nrows, ncols=ncols, figsize=(30, 15)
    )  # nrows = 4 and ncols = 8 for a 4x8 grid of subplots

    # We now have a 4x8 matrix of Axes objects corresponding to our subplot grid.
    # To make this easier to iterate through, I can flatten it into a 1D array.
    axs = axs.flatten()

    for i, (name, series) in enumerate(
        data.items()
    ):  # items() returns (column names, Series) pairs that can be iterated over
        axs[i].plot(
            series.index, series.values
        )  # Plots index on x-axis, and series' values on y-axis
        axs[i].set_title(name)

        # Aesthetics
        # Reformat the x-axis labels using datetime
        axs[i].xaxis.set_major_locator(
            mdates.DayLocator(interval=days)
        )  # Set major tick every n days
        axs[i].xaxis.set_major_formatter(
            mdates.DateFormatter("%b %d")
        )  # Format the datetime as 'HH:MM', instead of showing the whole dt

        axs[i].tick_params("x", labelrotation=90)
        axs[i].set_ylabel(yaxis_label, fontsize=12)
        axs[i].set_xlabel(xaxis_label, fontsize=8)

        # Minute ticks, so we have minute precision in specifying the light and dark bars
        minute_ticks = pd.date_range(start=start_time, end=end_time, freq="1min")

        ### DRAW LIGHT AND DARK BARS ###
        drawLD(
            minute_ticks,
            axs[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
        )
        ### END OF LIGHT AND DARK BARS ###

    fig.suptitle(
        monitor_name
        + f" {graph_title} "
        + str(num_days)
        + "_days_"
        + start_time
        + "_to_"
        + end_time,
        fontsize=16,
    )
    plt.tight_layout()
    return plt


####################
# END BASIC PLOTTING FUNCTIONS
####################


###################################################
################ MAIN TASKS ## ####################
###################################################

# The basic plotting functions can be used for multiple types of the processed data (i.e., running average, zscored)
# The task functions pass information regarding the graph title, axis labels and saves the plot to a specific directory.
# Also, the task functions take a list of dataframes and thus iterates through all currently loaded monitor files.


# figs 1 and 2
def rawPlot(
    monitor_files: list[pd.DataFrame], just_file_names: list[str], result_path: str
):
    #################
    # Plot the entire raw data
    #################
    # Iterate through monitors and plot raw data
    for i, monitor in enumerate(monitor_files):
        plot = plot_raw(monitor, i, just_file_names[i].replace(".txt", ""))
        plot.savefig(
            result_path
            + "/fig_01/"
            + just_file_names[i].replace(".txt", "")
            + "_raw_data_fig_01.png"
        )
        plt.close()
        print(
            f"Saved raw data plot to {result_path + '/fig_01/' + just_file_names[i].replace('.txt', '') + '_raw_data_fig1.png'}"
        )

        #################
        # Subplots for each animal
        ################

        for j, monitor in enumerate(monitor_files):
            plot = subplots_raw(
                monitor,
                j,
                3,  # Intervals of days for the x-axis
                just_file_names[j].replace(".txt", ""),
            )
            plot.savefig(
                result_path
                + "/fig_02/"
                + just_file_names[j].replace(".txt", "")
                + "_raw_individuals_fig_02.png"
            )
            plt.close()
            print(
                f"Saved raw individuals data plot to {result_path + '/fig_02/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_fig_02.png'}"
            )


# fig 3
def slicedPlot(
    monitor_slices: list[pd.DataFrame],
    just_file_names: list[str],
    sliced_path: str,
    start_slice: str,
    end_slice: str,
    num_days: int,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
):
    #################
    # Plot the sliced raw data
    #################

    for i, monitor in enumerate(monitor_slices):
        plot = plot_sliced_all(
            monitor,
            num_days,
            start_slice,
            end_slice,
            just_file_names[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "raw sliced",
            "counts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_03/"
            + just_file_names[i].replace(".txt", "")
            + "_raw_sliced_data_fig_03.png"
        )
        plt.close()
        print(
            f"Saved raw sliced data plot to {sliced_path + '/fig_03/' + just_file_names[i].replace('.txt', '') + '_raw_sliced_data_fig_03.png'}"
        )


# fig 4
def slicedIndividualPlot(
    monitor_slices: list[pd.DataFrame],
    just_file_names: list[str],
    sliced_path: str,
    start_slice: str,
    end_slice: str,
    num_days: int,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
):
    #################
    # Subplots of sliced raw data for each animal
    ################
    for j, slice in enumerate(monitor_slices):
        plot = plot_sliced_individuals(
            slice,
            num_days,
            start_slice,
            end_slice,
            1,
            just_file_names[j],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "raw sliced",
            "counts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_04/"
            + just_file_names[j].replace(".txt", "")
            + "_raw_individuals_sliced_fig_04.png"
        )
        plt.close()
        print(
            f"Saved raw individuals sliced data plot to {sliced_path + '/fig_04/' + just_file_names[j].replace('.txt', '') + '_raw_individuals_sliced_fig_04.png'}"
        )


# fig 5
def smoothedPlot(
    smoothed_monitors: list[pd.DataFrame],
    just_file_names: list[str],
    num_days: int,
    start_slice: str,
    end_slice: str,
    smoothing_window: int,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
    sliced_path: str,
):
    #################
    # Plot the sliced running average!
    ################
    # Iterate through monitors and plot the data
    for i, monitor in enumerate(smoothed_monitors):
        plot = plot_sliced_all(
            monitor,
            num_days,
            start_slice,
            end_slice,
            just_file_names[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "running avg",
            "smoothed cnts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_05/"
            + just_file_names[i].replace(".txt", "")
            + "_smoothed_all_"
            + str(smoothing_window)
            + "_min_"
            + "fig_05.png"
        )
        plt.close()

        print(
            f"Saved smoothed data plot to {sliced_path}",
            "/fig_05/",
            just_file_names[i].replace(".txt", ""),
            "_smoothed_all_",
            str(smoothing_window),
            "_min_",
            "fig_05.png",
        )


# fig 6
def smoothedPlotIndividual(
    smoothed_monitors: list[pd.DataFrame],
    just_file_names: list[str],
    num_days: int,
    smoothing_window: int,
    start_slice: str,
    end_slice: str,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
    sliced_path: str,
):
    #################
    # Plot the sliced running average!
    ################
    # Iterate through monitors and plot the data
    for i, monitor in enumerate(smoothed_monitors):
        plot = plot_sliced_individuals(
            monitor,
            num_days,
            start_slice,
            end_slice,
            1,
            just_file_names[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "running avg",
            "smoothed cnts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_06/"
            + just_file_names[i].replace(".txt", "")
            + "_smoothed_individuals_"
            + str(smoothing_window)
            + "_min_"
            + "fig_06.png"
        )
        plt.close()

        print(
            f"Saved smoothed data plot to {sliced_path}",
            "/fig_06/",
            just_file_names[i].replace(".txt", ""),
            "_smoothed_individuals_",
            str(smoothing_window),
            "_min_",
            "fig_06.png",
        )


# fig 7
def zscoredPlot(
    zscored_monitors: list[pd.DataFrame],
    just_file_names: list[str],
    num_days: int,
    start_slice: str,
    end_slice: str,
    smoothing_window: int,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
    sliced_path: str,
):
    #################
    # Plot the sliced zscored data
    ################
    # Iterate through monitors and plot
    for i, monitor in enumerate(zscored_monitors):
        plot = plot_sliced_all(
            monitor,
            num_days,
            start_slice,
            end_slice,
            just_file_names[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "z-scored",
            "zscored cnts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_07/"
            + just_file_names[i].replace(".txt", "")
            + "_zscored_all_"
            + str(smoothing_window)
            + "_min_"
            + "fig_07.png"
        )
        plt.close()

        print(
            f"Saved zscored data plot to {sliced_path}",
            "/fig_07/",
            just_file_names[i].replace(".txt", ""),
            "_zscored_all_",
            str(smoothing_window),
            "_min_",
            "fig_07.png",
        )


# fig 8
def zscoredIndividual(
    zscored_monitors: list[pd.DataFrame],
    just_file_names: list[str],
    num_days: int,
    smoothing_window: int,
    start_slice: str,
    end_slice: str,
    morning_ramp_start: dt_time,
    evening_ramp_start: dt_time,
    evening_ramp_end: dt_time,
    ramp_time: timedelta,
    ramp_end_date: datetime,
    sliced_path: str,
):
    #################
    # Plot the sliced zscored data
    ################
    # Iterate through monitors and plot
    for i, monitor in enumerate(zscored_monitors):
        plot = plot_sliced_individuals(
            monitor,
            num_days,
            start_slice,
            end_slice,
            1,
            just_file_names[i],
            morning_ramp_start,
            evening_ramp_start,
            evening_ramp_end,
            ramp_time,
            ramp_end_date,
            "z-scored",
            "zscored cnts/min",
            "local time",
        )

        plot.savefig(
            sliced_path
            + "/fig_08/"
            + just_file_names[i].replace(".txt", "")
            + "_zscored_individuals_"
            + str(smoothing_window)
            + "_min_"
            + "fig_08.png"
        )
        plt.close()

        print(
            f"Saved zscored data subplots to {sliced_path}",
            "/fig_08/",
            just_file_names[i].replace(".txt", ""),
            "_zscored_individuals_",
            str(smoothing_window),
            "_min_",
            "fig_08.png",
        )


###################################################
################ END OF MAIN TASKS ## #############
###################################################


# Guard to prevent script run on import
if __name__ == "__main__":
    exclude_animals = EXCLUDE_ANIMALS_VAR.get()
    main(args, exclude_animals)
