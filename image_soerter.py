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
    if ( cnt != -1 and brt != -1):
      break
  f.close()
  a = tiff.imread(filename) # open as a tiff file
  zero = "OK"
  #a = a.reshape(-1,1)
  if a.min() == 0:
    zero = "ZERO"
  return [brt, cnt, a.min()]


if __name__ == "__main__":
  tiff_pattern = re.compile(".*\.tif+")
  if len(sys.argv) > 1:
    dirname = sys.argv[1]
  else:
    dirname = "."
  brto = -1 #original vlaues of brightness and contrast
  cnto = -1
  group_index = 0
  grpzero = 0 # if group contains possible negatoive values
  for fn in sorted(os.listdir(dirname)): # list must be sorted of it can be shuffled by the OS
    if tiff_pattern.match(fn):
      [brt, cnt, minval] = process_image(os.path.join(dirname,fn))
      change = 0
      if brto != brt or cnto !=cnt:
        brto = brt
        cnto = cnt
        change = 1 # values changed since last image

        if grpzero == 1:
          print "mv group_%03d group_%03d_NEGATIVE" % (group_index, group_index)
        group_index += 1
        grpzero = 0
      if change == 1:
        print "# ------------------------------------------"
        print "mkdir group_%03d" % group_index
      print "ln -sf \"%s\" group_%03d/ #%f, %f, %d" % (os.path.join(dirname,fn), group_index, brt, cnt, minval)
      if grpzero == 0 and minval == 0:
        print "echo ZERO > group_%03d/ATTENTION_POSSIBLE_NEGATIVE_VALUES.txt" % group_index
        grpzero = 1

  if grpzero == 1:
    print "mv group_%03d group_%03d_NEGATIVE" % (group_index, group_index)

