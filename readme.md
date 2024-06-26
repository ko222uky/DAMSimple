# Damn Simple: A GUI for the Simple Visualization of DAM Data
Version 1.0
(by Kenneth O'Dell Jr.)

![damnsimple-fly](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/1b2b437b-9b65-4bdd-afda-5f5fd0f955aa)
The DamnSimple fly is AI-generated.

## Example of the GUI:
![image](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/2ba4f9b1-6c68-4c13-82ab-fe6c42ac2f41)

## Exclude Animals:
![image](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/035c1fd6-d832-476e-bd1c-c1a8f3605aad)

## Example Experiment Directory (After Processing):
![Screenshot from 2024-06-26 16-48-09](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/8be7abc6-7097-466b-85fe-5b921d4001df)


## Get a Quick Final Graph:
![Monitor11_final_all_30_min_fig_11](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/assets/111385224/96bc12ec-db28-4f16-92e2-ce4a13fa1773)


## Description
...coming soon...


## Installation

I built this as a standalone binary to avoid the need to install the dependencies since some organizations have a chokehold on their systems such that one cannot install things as one pleases.
That is annoying.
Handing someone a USB stick or a zipped folder circumvents this annoyance. 

I mainly use Linux, and the program tested fine on Linux Mint 21.3, on Debian 12 stable, and on my tiny Raspberry Pi 4 running Kali Linux.
But not everyone uses Linux, so I made a build for Windows, too.

All needed files are in the DamnSimple directory, which are available according to OS:

For Windows:

    [src/pyinstaller_builds/windows/DamnSimple](https://github.com/ko222uky/DamnSimpleLocomotorAnalysis/releases)

For Linux:

    src/pyinstaller_builds/linux/DamnSimple

Important Notes:

  The executable is located in the 'bin' directory.
  Do not move the _internal directory.
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



## Example Data

The Monitor11.txt example data comes from the tutorial for Rethomics, which is a framework for high-throughput behavioral analysis.
See https://rethomics.github.io/damr.html

