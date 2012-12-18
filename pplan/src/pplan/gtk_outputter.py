import gobject

class GTKOutputter:
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar

    def writeln(self, s):
        print s

    def _set_fraction(self, frac):
        self.progress_bar.set_fraction(frac)

    def set_fraction(self, frac):
        gobject.idle_add(self._set_fraction, frac)
