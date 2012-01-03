#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

# append the directories where we install the devede's own modules
tipo=-1

try:
	fichero=open("./interface/wmain.ui","r")
	fichero.close()
	tipo=2
	found=True
except:
	found=False	

if found==False:
	try:
		fichero=open("/usr/share/devede/wmain.ui","r")
		fichero.close()
		tipo=0
		found=True
	except:
		found=False

if found==False:
	try:
		fichero=open("/usr/local/share/devede/wmain.ui","r")
		fichero.close()
		tipo=1
		found=True
	except:
		found=False

if tipo==0:
	#gettext.bindtextdomain('devede', '/usr/share/locale')
	#Note also before python 2.3 you need the following if
	#you need translations from non python code (glibc,libglade etc.)
	#there are other access points to this function
	#gtk.glade.bindtextdomain("devede","/usr/share/locale")
	#arbol=gtk.Builder("/usr/share/devede/devede.glade",domain="devede")
	# append the directories where we install the devede's own modules

	share_locale="/usr/share/locale"
	glade="/usr/share/devede"
	sys.path.append("/usr/lib/devede")
	font_path="/usr/share/devede"
	pic_path="/usr/share/devede"
	other_path="/usr/share/devede"
	help_path="/usr/share/doc/devede"
	print "Using package-installed files"
	
elif tipo==1:
	# if the files aren't at /usr, try with /usr/local
	#gettext.bindtextdomain('devede', '/usr/share/locale')
	#Note also before python 2.3 you need the following if
	#you need translations from non python code (glibc,libglade etc.)
	#there are other access points to this function
	#gtk.glade.bindtextdomain("devede","/usr/share/locale")
	#arbol=gtk.Builder("/usr/local/share/devede/devede.glade",domain="devede")

	share_locale="/usr/share/locale" # Are you sure?
	# if the files aren't at /usr, try with /usr/local
	glade="/usr/local/share/devede"
	sys.path.append("/usr/local/lib/devede")
	font_path="/usr/local/share/devede"
	pic_path="/usr/local/share/devede"
	other_path="/usr/local/share/devede"
	help_path="/usr/local/share/doc/devede"
	print "Using local-installed files"
	
elif tipo==2:
	# if the files aren't at /usr/local, try with ./
	#gettext.bindtextdomain('devede', './po/')
	#Note also before python 2.3 you need the following if
	#you need translations from non python code (glibc,libglade etc.)
	#there are other access points to this function
	#gtk.glade.bindtextdomain("devede","/usr/share/locale")
	#arbol=gtk.Builder("./devede.glade",domain="devede")
	
	# if the files aren't at /usr/local, try with ./
	share_locale="./po/"
	glade="./interface"
	sys.path.append(os.getcwd())#("./")
	font_path=os.getcwd()#"./"
	pic_path=os.path.join(font_path, "pixmaps") #pic_path=font_path
	other_path=os.path.join(font_path,"pixmaps")
	help_path=os.path.join(font_path,"doc")
	print "Using direct files"
	
else:
	print "Can't locate extra files. Aborting."
	sys.exit(1)


#####################
#   GetText Stuff   #
#####################

gettext.bindtextdomain('devede',share_locale)
locale.setlocale(locale.LC_ALL,"")
gettext.textdomain('devede')
gettext.install("devede",localedir=share_locale) # None is sys default locale
#   Note also before python 2.3 you need the following if
#   you need translations from non python code (glibc,libglade etc.)
#   there are other access points to this function
#gtk.glade.bindtextdomain("devede",share_locale)

arbol=gtk.Builder()
arbol.set_translation_domain("devede")

#   To actually call the gettext translation functions
#   just replace your strings "string" with gettext("string")
#   The following shortcut are usually used:
_ = gettext.gettext

try:
	import devede_other
except:
	print "Failed to load modules DEVEDE_OTHER. Exiting"
	sys.exit(1)
try:
	import devede_convert
except:
	print "Failed to load modules DEVEDE_CONVERT. Exiting"
	sys.exit(1)
try:
	import devede_newfiles
except:
	print "Failed to load module DEVEDE_NEWFILES. Exiting"
	sys.exit(1)
try:
	import devede_xml_menu
except:
	print "Failed to load module DEVEDE_XML_MENU"
	sys.exit(1)

try:
	import devede_disctype
except:
	print "Failed to load module DEVEDE_DISCTYPE"
	sys.exit(1)

try:
	import devede_fonts
except:
	print "Failed to load module DEVEDE_FONTS"
	sys.exit(1)


home=devede_other.get_home_directory()

#locale.setlocale(locale.LC_ALL,"")
#gettext.textdomain('devede')
#_ = gettext.gettext

# global variables used (they are stored in a single dictionary to
# avoid true global variables):
# there are these two that aren't stored in the dictionary because they are very widely used:
# arbol
# structure

if pic_path[-1]!=os.sep:
	pic_path+=os.sep

global_vars = devede_globals.get_default_globals(pic_path, other_path, help_path, glade)

print "Cores: "+str(global_vars["cores"])

if font_path[-1]!=os.sep:
	font_path+=os.sep
font_path+="devedesans.ttf"
global_vars["font_path"]=font_path

print "Entro en fonts"
fonts_found=devede_fonts.prepare_devede_font(home,font_path)
print "Salgo de fonts"

devede_other.load_config(global_vars) # load configuration

devede_globals.check_programs(global_vars)

def program_exit(widget):
	
	gtk.main_quit()


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
