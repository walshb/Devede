#!/usr/bin/env python

import sys
import os

bindir = os.path.abspath(os.path.dirname(sys.argv[0]))

# these will be changed before installation
pkglibdir = bindir
pkgdatadir = os.path.join(bindir, 'pixmaps')
docdir = os.path.join(bindir, 'docs')
localedir = os.path.join(bindir, 'po')

sys.path.append(pkglibdir)

# prevent gtk issues
del os.environ['DISPLAY']

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
import devede_other

gettext.bindtextdomain('devede', localedir)
locale.setlocale(locale.LC_ALL,"")
gettext.textdomain('devede')
gettext.install("devede", localedir=localedir)

_ = gettext.gettext

def main():
    if len(sys.argv) == 1:
        sys.stderr.write('usage: devede_cli filename|args...\n')
        return 1

    assert os.path.exists(os.path.join(pkgdatadir, 'silence.ogg'))
    assert os.path.exists(os.path.join(pkgdatadir, 'base_pal.mpg'))
    assert os.path.exists(os.path.join(docdir, 'html', 'basic.html'))

    global_vars = devede_globals.get_default_globals(pkgdatadir, docdir)
    devede_file.init_defaults(global_vars)

    filename = None
    if sys.argv[1].startswith('--'):
        file_structure, file_globals = devede_file.parse_args(sys.argv[1:])
    else:
        filename = sys.argv[1]
        fp = io.open(filename, 'rb', buffering=10)
        file_structure, file_globals = devede_file.read(fp)
        fp.close()

    devede_other.load_config(global_vars) # load configuration

    devede_globals.check_programs(global_vars)

    structure = []
    loader = devede_loadsave.load_save_config(None, structure, global_vars, None)
    loader.load_data(filename, file_structure, file_globals)  # will update global_vars

    global_vars['number_actions'] = 3  # including DVD image
    global_vars['erase_temporary_files'] = False

    # let's try out this avconv thing.
    global_vars["encoder_video"] = "avconv"
    global_vars["encoder_menu"] = "avconv"

    mainwin = devede_main.main_window(global_vars, None)
    mainwin.structure = structure  # XXX refactor this
    mainwin.on_autosize_clicked(None)

    for title_data in structure:
        for file_props in title_data[1:]:
            sys.stderr.write('set "%s" vrate = %s\n' % (file_props['path'], file_props['vrate']))

    convertor = devede_convert.create_all(None, structure, global_vars, None)
    convertor.create_disc()

    gtk.main()

    return 0

if __name__ == '__main__':
    sys.exit(main())
