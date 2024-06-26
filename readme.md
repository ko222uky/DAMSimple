# Damn Simple: A GUI for the Simple Visualization of DAM Data
Version 1.0
(by Kenneth O'Dell Jr.)

## Description



## Installation

I built this as a standalone binary to avoid the need to install the dependencies since some organizations have a chokehold on their systems such that one cannot install things as one pleases.
That is annoying.
Handing someone a USB stick or a zipped folder circumvents this annoyance. 

I mainly use Linux, and the program tested fine on Linux Mint 21.3, on Debian 12 stable, and on my tiny Raspberry Pi 4 running Kali Linux.
But not everyone uses Linux, so I made a build for Windows, too.

All needed files are in the DamnSimple directory, located in their respective system directory:

For Windows:

    src/pyinstaller_builds/windows/DamnSimple

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




## Example Data

The Monitor11.txt example data comes from the tutorial for Rethomics, which is a framework for high-throughput behavioral analysis.
See https://rethomics.github.io/damr.html

