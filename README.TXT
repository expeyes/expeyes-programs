This directory contains all the expEYES programs and libraries - version 3.0  

BUILDING FROM THE SOURCE
========================

To build the package from the source, here are the required dependencies:
- python2.7
- lyx
- texlive binaries, fonts and packages
- image-magick
- gcc-avr and its utilities

To build and install the package, unfold the archive in some directory
and type the following commands:

  make; make install; sh postinst

TO RUN THE PROGRAMS
===================

You need to install the following modules and their dependences.

- python-imaging-tk
- tix
- python-tk
- python-scipy
- xmgrace
- python-pygrace
- python-serial
- python-usb
- udev

To start the expEYES main program:

$ expeyes

For expEYES Junior:

$ expeyes-junior

Each of the commands expeyes and expeyes-junior has its own manpage.


