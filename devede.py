#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:noet:ts=8:sts=8:sw=8

# Copyright 2006-2009 (C) Raster Software Vigo (Sergio Costas)
# Copyright 2006-2009 (C) Peter Gill - win32 parts

# This file is part of DeVeDe
#
# DeVeDe is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# DeVeDe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os

bindir = os.path.abspath(os.path.dirname(sys.argv[0]))

# these will be changed before installation
pkglibdir = bindir
pkgdatadir = os.path.join(bindir, 'pixmaps')
docdir = os.path.join(bindir, 'docs')
localedir = os.path.join(bindir, 'po')
glade = os.path.join(bindir, 'interface')
font_path = bindir

sys.path.append(pkglibdir)

import pygtk # for testing GTK version number
pygtk.require ('2.0')
import gtk
import gobject
import locale
import gettext
import stat
import shutil
import pickle
import cairo

print "DeVeDe 3.21.0"
if (sys.platform!="win32") and (sys.platform!="win64"):
	try:
		print "Locale: "+str(os.environ["LANG"])
	except:
		print "Locale not defined"

#####################
#   GetText Stuff   #
#####################

gettext.bindtextdomain('devede', localedir)
locale.setlocale(locale.LC_ALL,"")
gettext.textdomain('devede')
gettext.install("devede",localedir=localedir) # None is sys default locale
#   Note also before python 2.3 you need the following if
#   you need translations from non python code (glibc,libglade etc.)
#   there are other access points to this function
#gtk.glade.bindtextdomain("devede", localedir)

arbol=gtk.Builder()
arbol.set_translation_domain("devede")

#   To actually call the gettext translation functions
#   just replace your strings "string" with gettext("string")
#   The following shortcut are usually used:
_ = gettext.gettext


import devede_other
import devede_convert
import devede_newfiles
import devede_xml_menu
import devede_disctype
import devede_fonts
import devede_globals
import devede_file

home=devede_other.get_home_directory()

#locale.setlocale(locale.LC_ALL,"")
#gettext.textdomain('devede')
#_ = gettext.gettext

# global variables used (they are stored in a single dictionary to
# avoid true global variables):
# there are these two that aren't stored in the dictionary because they are very widely used:
# arbol
# structure

global_vars = devede_globals.get_default_globals(pkgdatadir, docdir, glade)
devede_file.init_defaults(global_vars)

global_vars[""]=""

print "Cores: "+str(global_vars["cores"])

global_vars["font_path"] = os.path.join(font_path, 'devedesans.ttf')

print "Entro en fonts"
fonts_found=devede_fonts.prepare_devede_font(home,font_path)
print "Salgo de fonts"

devede_other.load_config(global_vars) # load configuration

devede_globals.check_programs(global_vars)

def program_exit(widget):
	
	gtk.main_quit()


errors = ''
if errors!="":
	arbol.add_from_file(os.path.join(glade,"wprograms.ui"))
	w=arbol.get_object("programs_label")
	w.set_text(errors)
	wprograms=arbol.get_object("wprograms")
	wprograms.show()
	w=arbol.get_object("program_exit")
	w.connect("clicked",program_exit)
	wprograms.connect("destroy",program_exit)
elif fonts_found==False:
	arbol.add_from_file(os.path.join(glade,"wnofonts.ui"))
	wprograms=arbol.get_object("wnofonts")
	wprograms.show()
	w=arbol.get_object("fonts_program_exit")
	w.connect("clicked",program_exit)
	wprograms.connect("destroy",program_exit)
else:
	new_file=devede_disctype.disctype(global_vars)

gtk.main()
print "Saving configuration"
devede_other.save_config(global_vars)
print "Exiting"
print "Have a nice day"
sys.stdout.flush()
sys.stderr.flush()
