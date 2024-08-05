# DAMSimple: A GUI for the Simple Visualization of DAM Data
Version 1.0.0
(by Kenneth O'Dell Jr.)

![damnsimple-fly](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/1b2b437b-9b65-4bdd-afda-5f5fd0f955aa)
The DAMSimple fly is AI-generated.

## Example of the GUI:
![image](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/2ba4f9b1-6c68-4c13-82ab-fe6c42ac2f41)

## Exclude Animals:
![checkboxes](https://github.com/user-attachments/assets/803a3f94-2b84-4244-a25a-4b00d752082b)


## Example Experiment Directory (After Processing):
![Screenshot from 2024-06-26 16-48-09](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/8be7abc6-7097-466b-85fe-5b921d4001df)


## Get a Quick Final Graph:
![Monitor11_final_all_30_min_fig_11](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/96bc12ec-db28-4f16-92e2-ce4a13fa1773)


## Description
...coming soon...


## Installation

**All needed files are in the DamnSimple.zip, which are available according to OS under releases:**

    https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/releases

I built this as a standalone binary to avoid the need to install the dependencies since some organizations have a chokehold on their systems such that one cannot install things as one pleases.
That is annoying.
Handing someone a USB stick or a zipped folder circumvents this annoyance. 

I mainly use Linux, and the program tested fine on Linux Mint 21.3, on Debian 12 stable, and on my tiny Raspberry Pi 4 running Kali Linux.
But not everyone uses Linux, so I made a build for Windows, too.


**Important Notes:**

  The executable is located in the 'bin' directory.
  Do not move the _internal directory, as this is needed by the executable.
  Do not move the icon directory.
  Directories containing your experimental data should be sibling directories to the bin directory.
  An example_data directory is provided to test the program.

  For Windows, you will want to override the file path character limit.
  Naturally, this was not a problem on Linux, but it can be a problem on Windows.
  Why do I like longer file path names?
  This is because the long file paths are used as a minimalistic identifier and description of the data slicing that the program performs.
  In other words, the file paths tell you useful information about the derived data.
  This seemed more intuitive than creating additional files.



## How to Use
...coming soon...
#### With regards to the light-dark bars drawn on the graphs:
The LD bars are purely for aesthetic purposes, and none of the calculations are impacted by the photoregime parameters.
Thus, the date for the DD analaysis start is simply for drawing total dark bars.
When entering the DD analysis start date, use the date before the transition day.
E.g., if 2024-03-31 is the transition day, then enter 2024-03-30.
It is up to the user to verify the correctness of the outputted graphs, in case unforeseen contingencies (e.g., data formatting) somehow affect the output.


## Example Data

The Monitor11.txt example data comes from the tutorial for Rethomics, which is a framework for high-throughput behavioral analysis.
See https://rethomics.github.io/damr.html

