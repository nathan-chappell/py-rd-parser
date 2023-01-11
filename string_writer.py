import datetime
import typing as T
from contextlib import contextmanager

class StringWriter:
    def __init__(self):
        self.s = ""
        self._indent = 0
    
    def write(self, *args: T.Any) -> 'StringWriter':
        for arg in args:
            if arg is None:
                continue
            elif isinstance(arg, (str, int, datetime.timedelta)):
                self.s += str(arg)
            elif hasattr(arg, 'compile'):
                getattr(arg, 'compile')(self)
            else:
                raise Exception(f"[write]: {arg}")
        return self
    
    def write_line(self, *args: T.Any) -> 'StringWriter':
        return self.write(*args, "\n")
    
    def indent(self) -> 'StringWriter':
        return self.write('  '*self._indent)
    
    @contextmanager
    def indented(self):
        try:
            self._indent += 1
            yield
        finally:
            self._indent -= 1
    
    def __str__(self) -> str:
        return self.s