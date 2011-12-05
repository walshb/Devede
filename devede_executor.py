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


import signal
import os
import sys
import subprocess
import select
import time
if (sys.platform=="win32") or (sys.platform=="win64"):
	import win32api
	import win32process
	import win32con
	import time

import threading
import gobject


_log_fd = None


class executor:

	""" Base class for all launchers (Mplayer, Mencoder, SPUmux, DVDauthor, mkisofs...). """

	def __init__(self,filename=None,filefolder=None,progresbar=None):

		# FILENAME is the generic file name given by the user
		# FILEFOLDER is the path where all the temporary and finall files will be created
		# PROGRESBAR is the GtkProgressBar where the class will show the progress

		global _log_fd

		if _log_fd is None and filefolder is not None:
			log_filename = os.path.join(filefolder, 'devede.log')
			sys.stderr.write('\nlogging to %s\n' % log_filename)
			_log_fd = open(log_filename, 'w')

		self.initerror=False
		self.handle=None
		self.sep_stderr=False
		self.platform_win32=((sys.platform=="win32") or (sys.platform=="win64"))

		self.creationflags = 0
		if self.platform_win32:
			self.creationflags = win32process.CREATE_NO_WINDOW

		self.print_error="Undefined error"
		self.keep_output=False

		if filename!=None:
			self.bar=progresbar
			if progresbar!=None:
				progresbar.set_text(" ")
			self.filefolder=filefolder
			self.filename=filename
			self.printout=True
		else:
			self.bar=None
			self.filename=None
			self.filefolder=None
			self.printout=True


	def _log_data(self, data):
		if _log_fd:
			_log_fd.write(data)
			_log_fd.flush()
		else:
			sys.stderr.write(data)

	def _announce_launch(self, cmd, in_filename, out_filename):
		if isinstance(cmd, list):
			cmd = ' '.join(cmd)
		if in_filename:
			cmd += ' <%s' % in_filename
		if out_filename:
			cmd += ' >%s' % out_filename
		self._log_data('\n\n%s\n\n' % cmd)
		print "Launching program:", cmd


	def cancel(self):

		""" Called to kill this process. """

		if self.handle==None:
			return
		if (sys.platform=="win32") or (sys.platform=="win64"):
			try:
				win32api.TerminateProcess(int(self.handle._handle), -1)
			except Exception , err:
				print "Error: ", err
		else:
			os.kill(self.handle.pid,signal.SIGKILL)
		
	
	def _wait_end_internal(self):
		"""Wait until the process ends.
		Return the return code of the process."""

		if self.handle==None:
			return 0

		while self.pipes:
			self._read_line_from_output()

		if self.out_thread:
			self.out_thread.join()
		if self.err_thread:
			self.err_thread.join()

		self.handle.wait()

		return self.handle.returncode


	def wait_end(self):
		return self._wait_end_internal()


	def wait_end2(self):
		return self.wait_end()


	def launch_shell(self,program,read_chars=1024,output=True,stdinout=None):
		""" Launches a program from a command line shell. Usefull for programs like SPUMUX, which
		takes the input stream from STDIN and gives the output stream to STDOUT, or for programs
		like COPY, CP or LN """
		
		self.read_chars=read_chars
		self.output=output
		self.handle=None

		in_filename = None
		out_filename = None
		if stdinout:
			in_filename, out_filename = stdinout
		self._popen(program, in_filename=in_filename, out_filename=out_filename)

		if self.handle:
			return self._wait_end_internal()

		print "Fallo"
		return None


	def launch_program(self,program,read_chars=80,output=True,win32arg=True,with_stderr=True, sep_stderr=False,keep_out=False):

		""" Launches a program that can be located in any of the directories stored in PATHLIST """

		self.read_chars=read_chars
		self.output=output
		self.handle=None
		
		self.sep_stderr=sep_stderr
		self.keep_output=keep_out

		self._popen(program, in_filename=None, out_filename=None)


	def _popen(self, program, in_filename, out_filename):
		assert isinstance(program, list)

		bufsize = 4096

		stdin = None
		stdout = subprocess.PIPE
		stderr = subprocess.PIPE

		if in_filename:
			stdin = open(in_filename)
		if out_filename:
			stdout = open(out_filename, 'w')

		wd=sys.path[-1:] # working directory.  This works with py2exe
		if (sys.platform=="win32") or (sys.platform=="win64"):
			pathlist=[os.path.join(wd[0],"bin"),os.path.join(os.getcwd(),"bin"), r'C:\WINDOWS', r'C:\WINDOWS\system32', r'C:\WINNT']
		else:
			pathlist = os.environ['PATH'].split(':')

		self.out_thread = None
		self.err_thread = None

		self.cadena=""
		self.err_cadena=""

		self._announce_launch(program, in_filename, out_filename)

		self._log_data('pathlist = %s\n' % (pathlist,))

		for elemento in pathlist:
			self._log_data("elemento: %s\n" % (elemento,))
			full_path = os.path.join(elemento, program[0])
			if not os.path.exists(full_path):
				continue
			program2=program[:]
			program2[0] = full_path
			self._log_data(' popen %s\n' % (program2,))
			try:
				handle = subprocess.Popen(program2, bufsize=bufsize, \
					creationflags=self.creationflags, \
					stdin=stdin, stdout=stdout, stderr=stderr)
			except OSError:
				self._log_data('error launching %s\n' % (program2,))
				print "error in launch program\n"
				continue

			self.handle=handle
			self.pipes = []
			if stdout == subprocess.PIPE:
				self.pipes.append(handle.stdout)
			if stderr == subprocess.PIPE:
				self.pipes.append(handle.stderr)
			if (sys.platform=="win32") or (sys.platform=="win64"):
				handle.set_priority()
				if stdout == subprocess.PIPE:
					self.out_thread = PipeThread(stdout, bufsize)
					self.out_thread.start()
				if stderr == subprocess.PIPE:
					self.err_thread = PipeThread(stderr, bufsize)
					self.err_thread.start()

			break

		# Don't return any handle. The caller should call refresh or wait_end.
		return None


	def refresh(self):
		
		""" Reads STDOUT and STDERR and refreshes the progress bar. """

		if self.handle==None:
			return -1 # there's no program running

		while self.pipes:
			# keep calling _read_line_from_output to empty stdout and stderr
			if self._read_line_from_output():
				# nothing read this time
				break

		if not self.output:
			self.bar.pulse()
		elif self.set_progress_bar(): # progress_bar is defined in each subclass to fit the format
			self.cadena=""
		
		if not self.pipes and self.handle.poll() is not None:
			return 1 # process finished

		return 0 # 0: nothing to read; 1: program ended

	def _read_line_from_output(self):
		"""Return True if nothing read."""

		outdata = []
		errdata = []

		if self.platform_win32:
			if self.out_thread:
				outdata = self.out_thread.get_data()
			if self.err_thread:
				errdata = self.err_thread.get_data()
		else:
			readfhs = select.select(self.pipes, [], [], 0)[0]

			if self.handle.stdout in readfhs:
				outdata = [self.handle.stdout.readline(self.read_chars)]
			if self.handle.stderr in readfhs:
				errdata = [self.handle.stderr.readline(self.read_chars)]

		if '' in outdata:
			self.pipes.remove(self.handle.stdout)
		if '' in errdata:
			self.pipes.remove(self.handle.stderr)

		outdata = ''.join(outdata)
		errdata = ''.join(errdata)

		self._log_data(outdata)
		self._log_data(errdata)

		if self.output:
			self.cadena += outdata

			if self.sep_stderr:
				self.err_cadena += errdata
			else:
				self.cadena += errdata

		res = (len(outdata) + len(errdata) > 0)

		return not res


	def set_progress_bar(self):
		
		# By default, just do nothing
		if self.filename!=None:
			self.bar.pulse()

		if self.keep_output:
			return False
		else:
			return True


	def create_filename(self,filename,title,file,avi):

		""" Starting from the generic filename, adds the title and chapter numbers and the extension """

		currentfile=filename+"_"
		if title<10:
			currentfile+="0"
		currentfile+=str(title)+"_"

		if file<10:
			currentfile+="0"

		if avi:
			currentfile+=str(file)+'.avi'
		else:
			currentfile+=str(file)+'.mpg'
		return currentfile


	def remove_ansi(self,line):
		
		output=""
		while True:
			pos=line.find("\033[") # try with double-byte ESC
			jump=2
			if pos==-1:
				pos=line.find("\233") # if not, try with single-byte ESC
				jump=1
			if pos==-1: # no ANSI characters; we ended
				output+=line
				break
			
			output+=line[:pos]
			line=line[pos+jump:]

			while True:
				if len(line)==0:
					break
				if (ord(line[0])<64) or (ord(line[0])>126):
					line=line[1:]
				else:
					line=line[1:]
					break
		return output


class PipeThread(threading.Thread):
	def __init__(self, fin, chars=1024):
		threading.Thread.__init__(self)
		self.chars=chars
		self.fin = fin  # file in
		self.sout = []
		self.lock = threading.Lock()

	def run(self):
		while True:
			try:
				timer = threading.Timer(10, self._alarm_handler)
				data = self.fin.read(self.chars)
				timer.cancel()
				self._append_data(data)
				if not data:
					break
			except Exception, e:
				if not str(e) == 'timeout':  # something else went wrong ..
					pass
					#raise # got the timeout exception from alarm .. proc is hung; kill it
				break

	def _alarm_handler(self):
		print "Process read timeout exception"
		raise Exception("timeout")

	def _append_data(self, data):
		"""Appends to data. Not necessary to emit a GTK signal,
		as there's no GUI work to be done."""
		self.lock.acquire()
		self.sout.append(data)
		self.lock.release()

	def get_data(self):
		"""Gets and clears data."""
		self.lock.acquire()
		out = self.sout
		self.sout = []
		self.lock.release()
		return out

	def set_priority(self, pid=None, priority=0):

		"""
		Set the Priority of a Windows Process.  Priority is a value between 0-5 where
		2 is normal priority.  Defaults to lowest Priority.
		"""
		priority_classes=[win32process.IDLE_PRIORITY_CLASS,
						  win32process.BELOW_NORMAL_PRIORITY_CLASS,
						  win32process.NORMAL_PRIORITY_CLASS,
						  win32process.ABOVE_NORMAL_PRIORITY_CLASS,
						  win32process.HIGH_PRIORITY_CLASS,
						  win32process.REALTIME_PRIORITY_CLASS]
		if pid == None:
			pid=self.pid
		handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
		win32process.SetPriorityClass(handle, priority_classes[priority])
