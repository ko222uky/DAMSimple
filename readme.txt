Created by Kenneth O'Dell Jr.

The example data herein comes from the tutorial section of the Rethomics framework (https://rethomics.github.io/)

The initial goal was to re-create the time series filtering and normalization that was used in an Excel sheet in the Syed lab at the University of Kentucky.
That template was prone to breaking due to what I think was software rot, as well as careless handling by users.

############ Requirements ############

When I tested the the .ipynb and .py, my current environment had the following installed packages.
This can be viewed in the requirements.txt and installed via:

$ pip install -r requirements.txt

*Note* Some extra packages may be in that environment. 

############ Running the script ############

Be sure to have a directory representing the locomotor experiment name (assuming TriKinetics DAM monitor.txt files).

I recommend snakecase, e.g., 'your-experiment-name-here'

Place the monitor.txt files inside the new directory that you created.

Next, just activate your environment:

$ conda activate [your-environment-name]

Run the script while in the data-wrangling directory.
For help, use:

$ python analyze.py -h

The experiment directory name is required.
The start and end datetimes for slicing the data are required.

The other arguments are optional, but highly recommended to provide.
The default values of the optional flags were mainly used in testing.

You should include as arguments:

--morning_ramp HH:MM
--evening_ramp HH:MM
--night_start HH:MM
--ramp_duration {float}
--running_average MM        # Running average is in minutes
--exclude_animals           # Including this will perform analyses and save results to a separate directory for excluded animals

Here's an example of running the script:

$ python analyze.py rethomics-tutorial-data "2017-07-01 00:00:00" "2017-07-05 00:00:00" --DD_start_date 2017-07-03 --morning_ramp 6:00 --evening_ramp 18:00 --night_start 21:00 --ramp_duration 3 --running_average 60

If you wish to exclude animals (i.e., remove columns), then add the --exclude_animals flag at the end.
This will process data and place it in a separate directory for excluded animals.


############ Creating a log of the output ############

Data is processed and figures are placed in their appropriate directories.
If the directories do not exist, the script will create them.

If you want a log of the output, run the script and add >> log.txt to append the output to the text file.

$ python analyze.py your-experiment-directory "YYYY-MM-DD HH:MM:SS" "YYYY-MM-DD HH:MM:SS" >> log.txt
