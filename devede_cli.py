#!/usr/bin/env python

import sys
import os
import cPickle
import pprint
import optparse
import locale
import gettext
import gtk
import io

import devede_file
import devede_globals
import devede_newfiles
import devede_loadsave
import devede_convert
import devede_main

share_locale = './po/'
gettext.bindtextdomain('devede',share_locale)
locale.setlocale(locale.LC_ALL,"")
gettext.textdomain('devede')
gettext.install("devede",localedir=share_locale)

_ = gettext.gettext

def make_dvd(filename):
    ##pic_path = './pixmaps'
    ##other_path = '.'
    ##help_path = '.'
    pic_path = os.environ['HOME'] + '/opt/devede-head/share/devede'
    other_path = os.environ['HOME'] + '/opt/devede-head/share/devede'
    help_path = os.environ['HOME'] + '/opt/devede-head/share/doc/devede'

    assert os.path.exists(os.path.join(pic_path, 'silence.ogg'))
    assert os.path.exists(os.path.join(other_path, 'base_pal.mpg'))
    assert os.path.exists(os.path.join(help_path, 'html', 'basic.html'))

    global_vars = devede_globals.get_default_globals(pic_path, other_path, help_path)
    devede_globals.check_programs(global_vars)

    fp = io.open(filename, 'rb', buffering=10)
    file_structure, file_globals = devede_file.read(fp)
    fp.close()

    structure = []
    loader = devede_loadsave.load_save_config(None, structure, global_vars, None)
    loader.load_data(filename, file_structure, file_globals)  # will update global_vars

    global_vars['use_ffmpeg'] = True
    global_vars['warning_ffmpeg'] = False
    global_vars['number_actions'] = 3  # including DVD image
    global_vars['erase_temporary_files'] = False

    mainwin = devede_main.main_window(global_vars, None)
    mainwin.structure = structure  # XXX refactor this
    mainwin.on_autosize_clicked(None)

    for title_data in structure:
        for file_props in title_data[1:]:
            sys.stderr.write('set "%s" vrate = %s\n' % (file_props['path'], file_props['vrate']))

    convertor = devede_convert.create_all(None, structure, global_vars, None)
    convertor.create_disc()

    gtk.main()


def main():
    parser = optparse.OptionParser()

    options, args = parser.parse_args()

    make_dvd(args[0])

if __name__ == '__main__':
    main()
