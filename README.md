# SEM Image Groupper

This is a script which takes a directory/folder with SEM images in TIFF format
and sorts it into groups with the same settings of brightness and contrast and
marks all groups which contain zero-clipped images. It is crucial for analyses
of image series to have the same settings and unclipped images. This python
script just creates a shell script which finally does the job. This script
itself does not do any changes to the image series. Run it, take a look what's
gonna be done and if you like it, run the shell script.
