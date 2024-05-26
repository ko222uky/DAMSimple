

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
            folded_avg_monitor = pd.DataFrame(columns=zscored_monitor.columns)
            folded_avg_monitor.index.name = "time_bin"
            for column in zscored_monitor:
                # Fold the data. We can group by the datetime's time, and then calculate the mean for each time.
                folded_avg_monitor[column] = (
                    zscored_monitor[column].groupby(zscored_monitor.index.time).mean()
                )

            # The following seems verbose, but it works to get the correct format.
            # Slice by the first index, which should be the first time bin, specified by the START_SLICE
            # Slicing by index name gives a Series where the column names are the index. We only want values.

            first_row_values = folded_avg_monitor.loc[
                folded_avg_monitor.index[0]
            ].values  # If I don't use .values, I get a Series with the column names as the index

            # The shape of the values is (32, 1), which is 32 rows. I need 1 row, 32 columns.
            # Reshape to one row and an unknown number of columns (i.e., -1)

            first_row_values = first_row_values.reshape(1, -1)
            print(f"First row values: {first_row_values}")

            first_row_df = pd.DataFrame(
                first_row_values, columns=folded_avg_monitor.columns
            )
            first_row_df.index = [
                folded_avg_monitor.index[0]
            ]  # Set the index to the first time bin
            print("First row df:")
            print(first_row_df)

            # Now, we will concat the first row to the end of the folded_avg_monitor
            print("Concatenating first row to the end of the folded_avg_monitor...\n\n")
            folded_avg_monitor = pd.concat([folded_avg_monitor, first_row_df], axis=0)

            # Save the monitor by appending to our list of pd.DataFrames
            FOLDED_AVG_MONITORS.append(folded_avg_monitor)

            folded_avg_monitor.to_csv(
                FOLDED_AVERAGE_PATH + f"/folded_avg_{JUST_FILE_NAMES[i]}", sep="\t"
            )
            print(
                f"Saved folded average data to {FOLDED_AVERAGE_PATH + f'/folded_avg_{JUST_FILE_NAMES[i]}' }"
            )
