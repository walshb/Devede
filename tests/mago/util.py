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

import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import logging

logger = logging.getLogger(__name__)

def create_png(filename):
    x = np.arange(6)
    y = np.arange(5)
    z = x * y[:,np.newaxis]

    p = plt.imshow(z)
    fig = plt.gcf()
    plt.clim()   # clamp the color limits
    plt.title("Test image")

    plt.savefig(filename)
    plt.close


def create_video(filename):
    create_png(filename + '.png')

    cmd = ['ffmpeg', '-f', 'image2', '-loop', '1', '-t', '10',
           '-i', filename + '.png', '-y', filename]
    logger.debug('%s' % (cmd,))
    proc = subprocess.Popen(cmd)
    proc.communicate()


def create_subs(filename):
    fp = open(filename, 'w')
    for i in xrange(4):
        fp.write('%s\r\n' % (i + 1))
        fp.write('00:00:%2d,000 --> 00:00:%2d,000\r\n' % (i * 2 + 1, i * 2 + 2))
        fp.write('Subtitle %s\r\n' % i)
        fp.write('\r\n')
    fp.close()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    create_video('blah.avi')
