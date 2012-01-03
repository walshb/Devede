#!/usr/bin/env python

import sys
import cPickle
import pprint
import optparse
import io

import devede_file

def main():
    parser = optparse.OptionParser()

    options, args = parser.parse_args()

    if args:
        stream = io.open(args[0], 'rb', buffering=10)
    else:
        stream = io.open(sys.stdin.fileno(), 'rb', buffering=10)

    if stream.peek(2)[:2] == '([':
        structure, output_info = eval(stream.read())
    else:
        structure, output_info = devede_file.read(stream)
    devede_file.write(sys.stdout, structure, output_info, minimal=True)

if __name__ == '__main__':
    main()
