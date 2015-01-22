'''
Copyright (c) 2015, Dr. Petr Cizmar @ PTB Braunschweig, Germany
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the PTB Braunschweig nor the names of its contributors
      may be used to endorse or promote products derived from this software without
      specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL PETR CIZMAR BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import tifffile as tiff
import os
import sys
import re

def parse_value(line):
  re_val = re.compile(r"\w+.*= *([0-9\.]+).*\%") # find the value in the string like "Brightness =  63.2 %"
  m = re_val.match(line)
  return float(m.group(1)) # convert the string to float and return it
  

def process_image(filename):
  f = open(filename) # open as a text file to read the headers
  brt = -1 # set both to -1 to spot changes at exit condition
  cnt = -1
  re_brt = re.compile("^Brightness.*=") # compile RegExes
  re_cnt = re.compile("^Contrast.*=")
  for l in f: # read lines form file
    if re_brt.match(l): #brightness
      brt = parse_value(l)
    if re_cnt.match(l): #contrast
      cnt = parse_value(l)
    if ( cnt != -1 and brt != -1): #if we know both values, we can stop processing and save some time
      break
  f.close()
  a = tiff.imread(filename) # open as a tiff file
  return [brt, cnt, a.min()]


if __name__ == "__main__":
  tiff_pattern = re.compile(".*\.tif+")
  if len(sys.argv) > 1: # no arguments, we take current directory
    dirname = sys.argv[1]
  else:
    dirname = "."
  brto = -1 #original vlaues of brightness and contrast
  cnto = -1
  group_index = 0
  grpzero = 0 # if group contains possible negatoive values
  for fn in sorted(os.listdir(dirname)): # list must be sorted of it can be shuffled by the OS
    if tiff_pattern.match(fn):
      [brt, cnt, minval] = process_image(os.path.join(dirname,fn)) # process image and get the results
      change = 0
      if brto != brt or cnto !=cnt: # values changed since last image
        brto = brt # put the current values to the old variables for the next cycle
        cnto = cnt
        change = 1

        if grpzero == 1: # if group conatins possible negative values
          print "mv group_%03d group_%03d_NEGATIVE" % (group_index, group_index) # change name of the directory, if it contains negative values
        group_index += 1 # change, therefore new group
        grpzero = 0 # still no negatives in the new group
      if change == 1:
        print "# ------------------------------------------" # separator comment
        print "mkdir group_%03d" % group_index # new directory/folder
      print "ln -sf \"%s\" group_%03d/ #%f, %f, %d" % (os.path.join(dirname,fn), group_index, brt, cnt, minval)
      if grpzero == 0 and minval == 0: # possible negative values found and still not indicated
        print "echo ZERO > group_%03d/ATTENTION_POSSIBLE_NEGATIVE_VALUES.txt" % group_index
        grpzero = 1 

  if grpzero == 1:
    print "mv group_%03d group_%03d_NEGATIVE" % (group_index, group_index) # change name of the directory, if it contains negative values, again at the total end

