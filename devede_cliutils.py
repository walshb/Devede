import sys
import traceback

def error_exit(msg):
    sys.stdout.flush()
    sys.stderr.write('%s\n' % (msg,))
    sys.exit(1)

def handle_exception():
    sys.stdout.flush()
    traceback.print_exc()
    sys.exit(1)

class TextProgressBar(object):
    def set_text(self, text):
        sys.stderr.write('%s\n' % (text,))

    def set_fraction(self, frac):
        sys.stderr.write('%s\n' % (100.0 * frac,))

    def pulse(self):
        sys.stderr.write('.')
