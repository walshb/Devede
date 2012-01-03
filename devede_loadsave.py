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

import pygtk # for testing GTK version number
pygtk.require ('2.0')
import gtk
import pickle
import os
import sys

import devede_other
import devede_dialogs
import devede_newfiles

class load_save_config:
	
	def __init__(self,gladefile,structure,global_vars,tree):
		
		self.tree=tree
		self.gladefile=gladefile
		self.structure=structure
		self.global_vars=global_vars
		
	def load(self,file_name):
		
		""" This method loads a configuration file """
		
		self.done = False
		
		if (len(self.structure)>1) or (len(self.structure[0])>1):
			w = devede_dialogs.ask_overwrite_onload(self.gladefile)
			retval = w.run()
			w = None
			if retval!=-8:
				return

		if file_name==None:
			tree=devede_other.create_tree(self,"wloadconfig",self.gladefile,False)
			window = tree.get_object("wloadconfig")
			
			filter = gtk.FileFilter()
			filter.add_pattern("*.devede")
			filter.set_name(".devede")
			window.add_filter(filter)
			
			window.show()
			retval = window.run()
			window.hide()
			if retval!=-5:
				window.destroy()
				window = None
				return
			
			file_name=window.get_filename()
			window.destroy()
			window = None
		
		try:
			output=open(file_name)
		except:
			w = devede_dialogs.show_error(self.gladefile,_("Can't open the file."))
			w = None
			return
	
		try:
			values=pickle.load(output)
		except:
			w = devede_dialogs.show_error(self.gladefile,_("That file doesn't contain a disc structure."))
			w = None
			return
		
		if values!="DeVeDe":
			w = devede_dialogs.show_error(self.gladefile,_("That file doesn't contain a disc structure."))
			w = None
			return
		
		global_vars2={}
		try:
			values=pickle.load(output)
			global_vars2=pickle.load(output)
		except:
			w = devede_dialogs.show_error(self.gladefile,_("That file doesn't contain a DeVeDe structure."))
			w = None
			return
	
		
		output.close()

		self.load_data(file_name, values, global_vars2)

		if global_vars2.has_key("erase_files")==False:
			w=self.tree.get_object("create_iso")
			w.set_active(True)


	def load_data(self, file_name, file_structure, global_vars2):
		"""Update data structures using values and global_vars2."""

		all_file_props = []
		for title_data in file_structure:
			all_file_props.extend(title_data[1:])

		not_found=[]
		for file_props in all_file_props:
			try:
				os.stat(file_props["path"])
			except:
				not_found.append(str(file_props["path"]))
				continue

			newfile = devede_newfiles.newfile(global_vars2['PAL'], global_vars2['disctocreate'])
			newfile.init_properties_from_file(file_props['path'])
			for key in newfile.file_properties:
				if key in file_props:  # already overridden by user
					sys.stderr.write('%s overridden in config file.\n' % key)
					if key not in ('path', 'audio_stream', 'audio_list'):
						sys.exit(1)
				else:
					file_props[key] = newfile.file_properties[key]

			if 'sub_list' not in file_props:
				file_props["sub_list"] = []
				if file_props["subtitles"]:
					tmp={}
					tmp["subtitles"] = file_props["subtitles"]
					tmp["sub_codepage"] = file_props["sub_codepage"]
					tmp["sub_language"]="EN (ENGLISH)"
					tmp["subtitles_up"] = file_props["subtitles_up"]
					del file_props["subtitles"]
					del file_props["sub_codepage"]
					del file_props["subtitles_up"]
					file_props["sub_list"].append(tmp)


		if len(not_found)!=0:
			t_string=_("Can't find the following movie files. Please, add them and try to load the disc structure again.\n")
			for element in not_found:
				t_string+="\n"+element
			w = devede_dialogs.show_error(self.gladefile,t_string)
			w = None
			return
		
		try:
			os.stat(global_vars2["menu_bg"])
		except:
			w = devede_dialogs.show_error(self.gladefile,_("Can't find the menu background. I'll open the disc structure anyway with the default menu background, so don't forget to fix it before creating the disc."))
			w = None
			global_vars2["menu_bg"]=os.path.join(self.global_vars["path"],"backgrounds","default_bg.png")
			
		use_default_sound=False
	
		if False==global_vars2.has_key("menu_sound"):
			use_default_sound=True
		else:
			if (global_vars2["menu_sound"][-11:]=="silence.mp3"):
				global_vars2["menu_sound"]=os.path.join(self.global_vars["path"],"silence.ogg")
			try:
				os.stat(global_vars2["menu_sound"])
			except:
				use_default_sound=True
				w = devede_dialogs.show_error(self.gladefile,_("Can't find the menu soundtrack file. I'll open the disc structure anyway with a silent soundtrack, so don't forget to fix it before creating the disc."))
				w = None
		
		if (use_default_sound):
			global_vars2["menu_sound"]=os.path.join(self.global_vars["path"],"silence.ogg")

		if False==global_vars2.has_key("with_menu"):
			global_vars2["with_menu"]=True
		
		if False==global_vars2.has_key("menu_halignment"):
			global_vars2["menu_halignment"]=2 # center
			
		if False==global_vars2.has_key("menu_shadow_color"):
			global_vars2["menu_shadow_color"]=[0,0,0,0]
			
		if False==global_vars2.has_key("menu_title_shadow"):
			global_vars2["menu_title_shadow"]=[0,0,0,0]

		test=devede_newfiles.file_get_params()
		check,channels=test.read_file_values(global_vars2["menu_sound"],True)
		if (check!=False) or (channels!=1):
			global_vars2["menu_sound"]=os.path.join(self.global_vars["path"],"silence.ogg")
			w = devede_dialogs.show_error(self.gladefile,_("The menu soundtrack seems damaged. Using the default silent soundtrack."))
			w = None
			check,channels=test.read_file_values(global_vars2["menu_sound"],True)

		global_vars2["menu_sound_duration"]=test.length
		test=None

		while (len(self.structure)>0):
			self.structure.pop()
		
		for element in file_structure:
			self.structure.append(element)
		for element in global_vars2:
			self.global_vars[element]=global_vars2[element]
		
		if self.global_vars.has_key("menu_top_margin")==False:
			self.global_vars["menu_top_margin"]=0.125
			self.global_vars["menu_bottom_margin"]=0.125
			self.global_vars["menu_left_margin"]=0.1
			self.global_vars["menu_right_margin"]=0.1
		
		if self.global_vars.has_key("menu_bgcolor")==False:
			self.global_vars["menu_bgcolor"]=[0,0,0,49152]
			self.global_vars["menu_font_color"]=[65535,65535,65535]
			self.global_vars["menu_selc_color"]=[0,65535,65535,65535]
			self.global_vars["menu_alignment"]=2 # middle

		if self.global_vars.has_key("menu_title_text")==False:
			self.global_vars["menu_title_color"]=[0,0,0,65535]
			self.global_vars["menu_title_text"]=""
			self.global_vars["menu_title_fontname"]="Sans 14"

		self.global_vars["struct_name"]=file_name # update the path
		
		self.done = True


	def save(self,mode):
	
		""" This method stores the current disc structure in a file. If MODE is True,
			it will ask before a new name. If it's False and there's a filename
			(from a previous save), it will overwrite the old file """
	
		if mode or (self.global_vars["struct_name"]==""):
			tree=devede_other.create_tree(self,"wsaveconfig",self.gladefile,False)
			saveconfig=tree.get_object("wsaveconfig")
			
			filter=gtk.FileFilter()
			filter.add_pattern("*.devede")
			filter.set_name(".devede")
			saveconfig=tree.get_object("wsaveconfig")
			saveconfig.add_filter(filter)
			saveconfig.set_do_overwrite_confirmation(True)

			saveconfig.show()
			value=saveconfig.run()
			saveconfig.hide()
			if value!=-5:
				saveconfig.destroy()
				saveconfig=None
				return
			fname=saveconfig.get_filename()
			saveconfig.destroy()
			saveconfig=None
			
			if fname==None:
				w=devede_dialogs.show_error(self.gladefile,_("No filename"))
				w=None
				return

			if (len(fname)<7) or (fname[-7:]!=".devede"):
				fname+=".devede"

			self.global_vars["struct_name"]=fname
		
		try:
			output=open(self.global_vars["struct_name"],"wb")
			id="DeVeDe"
			pickle.dump(id,output)
			pickle.dump(self.structure,output)
			vars={}
			vars["disctocreate"]=self.global_vars["disctocreate"]
			vars["titlecounter"]=self.global_vars["titlecounter"]
			vars["do_menu"]=self.global_vars["do_menu"]
			vars["with_menu"]=self.global_vars["with_menu"]
			vars["menu_widescreen"]=self.global_vars["menu_widescreen"]
			vars["PAL"]=self.global_vars["PAL"]
			vars["menu_bg"]=self.global_vars["menu_bg"]
			vars["menu_sound"]=self.global_vars["menu_sound"]
			vars["menu_bgcolor"]=self.global_vars["menu_bgcolor"]
			vars["menu_font_color"]=self.global_vars["menu_font_color"]
			vars["menu_selc_color"]=self.global_vars["menu_selc_color"]
			vars["menu_shadow_color"]=self.global_vars["menu_shadow_color"]
			vars["menu_alignment"]=self.global_vars["menu_alignment"]
			vars["menu_halignment"]=self.global_vars["menu_halignment"]
			vars["struct_name"]=self.global_vars["struct_name"]
			vars["fontname"]=self.global_vars["fontname"]
			vars["menu_title_color"]=self.global_vars["menu_title_color"]
			vars["menu_title_shadow"]=self.global_vars["menu_title_shadow"]
			vars["menu_title_text"]=self.global_vars["menu_title_text"]
			vars["menu_title_fontname"]=self.global_vars["menu_title_fontname"]
			vars["menu_top_margin"]=self.global_vars["menu_top_margin"]
			vars["menu_bottom_margin"]=self.global_vars["menu_bottom_margin"]
			vars["menu_left_margin"]=self.global_vars["menu_left_margin"]
			vars["menu_right_margin"]=self.global_vars["menu_right_margin"]

			if self.tree.get_object("create_iso").get_active():
				vars["action_todo"]=2
			elif self.tree.get_object("create_dvd").get_active():
				vars["action_todo"]=1
			else:
				vars["action_todo"]=0

			print "Action: "+str(vars["action_todo"])
			print "Variables: "+str(vars)
			pickle.dump(vars,output)
			output.close()
		except:
			w=devede_dialogs.show_error(self.gladefile,_("Can't save the file."))
			w=None

