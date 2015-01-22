import tifffile as tiff
import os
import sys

def process_image(filename):
  a = tiff.imread(filename)


if __name__ == "__main__":
  if len(sys.argv) > 1:
    dirname = sys.argv[1]
  else:
    dirname = "."
  for fn in os.listdir(dirname):
    print os.join(dirname,fn)


