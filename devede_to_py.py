#!/usr/bin/env python

import sys
import cPickle
import pprint
import optparse

def print_raw(stream):
    first_section = True
    while True:
        try:
            data = cPickle.load(stream)
        except EOFError:
            break
        if not first_section:
            print '########'
        pprint.pprint(data)
        first_section = False

_props_from_file = ['filename', 'owidth',  'oheight', 'olength', 'ovrate',
                    'oarate', 'arateunc', 'oaspect', 'audio_list', 'audio_stream',
                    'ofps', 'ofps2', 'filesize']

def print_clean(stream):
    marker = cPickle.load(stream)

    assert marker == 'DeVeDe'

    title_infos = cPickle.load(stream)

    structure = []
    for basic_info, file_info in title_infos:
        new_file_info = {}
        for key in file_info:
            if key not in _props_from_file:
                new_file_info[key] = file_info[key]
        structure.append([basic_info, new_file_info])

    global_vars = cPickle.load(stream)

    pprint.pprint((structure, global_vars))


def main():
    parser = optparse.OptionParser()
    parser.add_option("-r", "--raw", dest="raw",
                      help="raw output", default=False, action='store_true')

    options, args = parser.parse_args()

    if args:
        stream = open(args[0])
    else:
        stream = sys.stdin

    if options.raw:
        print_raw(stream)
    else:
        print_clean(stream)

if __name__ == '__main__':
    main()
