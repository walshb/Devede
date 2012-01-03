#!/usr/bin/env python

import sys
import cPickle
import pprint
import optparse
import ConfigParser

import devede_file


def main():
    parser = optparse.OptionParser()
    parser.add_option("-r", "--raw", dest="raw",
                      help="raw output", default=False, action='store_true')

    options, args = parser.parse_args()

    if args:
        stream = open(args[0])
    else:
        stream = sys.stdin

    structure = read_structure(stream)

    pprint.pprint(structure)

if __name__ == '__main__':
    main()
