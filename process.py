#!/usr/bin/python
# coding=utf-8

from meta import FCOMMeta
from factory import FCOMFactory
from globals import *

import sys


def main():
    global g_paths
    if len(sys.argv) != 3:
        print "Usage: ", sys.argv[0], "start_file output_dir"
        sys.exit(1)
    g_paths.initialise(*sys.argv)
    fcm = FCOMMeta()
    ff = FCOMFactory(fcm)
    ff.build_fcom()


if __name__ == "__main__":
    main()


