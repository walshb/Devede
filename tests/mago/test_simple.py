# Copyright (C) 2012 Ben Walsh
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Simple test of DeVeDe.
"""

from mago import TestCase
import unittest
import ldtp
import sys
import os
import subprocess

import util


def _get_file_and_subs():
    vid_fname = os.path.join(os.getcwd(), 'myvideo.avi')
    sub_fname = os.path.join(os.getcwd(), 'myvideo.srt')

    util.create_video(vid_fname)
    util.create_subs(sub_fname)

    return vid_fname, sub_fname


def _show_objects(win_name):
    ldtp.waittillguiexist(win_name)
    xxx = ldtp.getobjectlist(win_name)
    sys.stderr.write('%s\n' % (xxx,))


def _click(win_name, btn_name):
    ldtp.waittillguiexist(win_name, btn_name)

    for i in xrange(5):
        try:
            ldtp.click(win_name, btn_name)
            break
        except Exception, e:
            sys.stderr.write('%s\n' % (e,))
        ldtp.wait(2)


def _choosefile(fname, win_name='dlgSelectaFile'):
    ldtp.waittillguiexist(win_name, 'tblPlaces')

    ldtp.singleclickrow(win_name, 'tblPlaces', 'File System')

    _click(win_name, 'tbtnTypeafilename')

    # this will fail if our version of ldtp2 uses setCacheMask(pyatspi.cache.ALL)
    ldtp.waittillguiexist(win_name, 'txtLocation')

    ldtp.settextvalue(win_name, 'txtLocation', fname)

    _click(win_name, 'btnOpen')

    ldtp.waittillguinotexist(win_name)


class TestMinimal(TestCase):
    """The minimal test that can be written with mago
    """
    launcher = 'devede.py'
    #: This is optional. If it is not defined, mago tries to guess it by querying Xlib
    #window_name = 'frmKlondike'

    def test_minimal(self):
        """A really simple test

        This test verifies True is True. If it fails, then reinstall your system.
        """

        vid_fname, sub_fname = _get_file_and_subs()

        subprocess.call(['rm', '-rf', '/var/tmp/devede_test'])

        # Create Video DVD
        _click('frmDisctypeselection', 'btnVideoDVD*')

        ##_show_objects('frm*DeVeDe')

        # Add a file
        _click('frm*DeVeDe', 'btnAdd1')

        ##_show_objects('frmFileproperties')

        _click('frmFileproperties', 'btn(None)')  # no filename yet

        ##sys.stderr.write('%s\n' % (ldtp.getwindowlist(),))

        _choosefile(vid_fname)

        _click('frmFileproperties', 'btnAdd')  # add subtitles

        ##sys.stderr.write('%s\n' % (ldtp.getwindowlist(),))

        # Choose subtitles file
        _click('dlg*', 'btn(None)')  # no subtitles filename yet

        _choosefile(sub_fname)

        _click('dlg*', 'btnOK')

        _click('frmFileproperties', 'btnOK')

        _click('frm*DeVeDe', 'btnAdjustdiscusage')

        # Forward to disk output dialog
        _click('frm*DeVeDe', 'btnForward')

        ldtp.waittillguiexist('dlg*', 'cbo*')

        ##sys.stderr.write('%s\n' % (ldtp.getwindowlist(),))

        # Choose output folder
        ldtp.comboselect('dlg*', 'cbo*', 'Other...')

        _choosefile('/var/tmp', win_name='dlgChooseafolder')

        # Set DVD name
        ldtp.settextvalue('dlg*', 'txt*', 'devede_test')

        _click('dlg*', 'btnOK')

        # making the DVD now!
        ldtp.waittillguiexist('frmCreating*')

        ##sys.stderr.write('%s\n' % (ldtp.getwindowlist(),))

        # wait til OK, then click
        _click('dlg*', 'btnOK')

        self.assertTrue(os.path.exists('/var/tmp/devede_test/devede_test.iso')


if __name__ == "__main__":
    unittest.main()
