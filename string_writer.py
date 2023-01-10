import datetime
import typing as T
from contextlib import contextmanager

class StringWriter:
    def __init__(self):
        self.s = ""
        self._indent = 0
    
    def _yield_args(self, *args: T.Any) -> T.Generator[str, None, None]:
        for arg in args:
            if arg is None:
                yield ""
            elif isinstance(arg, (str, int, datetime.timedelta)):
                yield str(arg)
            elif hasattr(arg, 'compile'):
                getattr(arg, 'compile')(self)
            else:
                raise Exception(f"[_yield_args]: {arg}")
    
    def write(self, *args: T.Any) -> 'StringWriter':
        print(self.s, args)
        print(id(self))
        self.s += ''.join(self._yield_args(*args))
        print(self.s)
        print('-'*10)
        return self
    
    def write_line(self, *args: T.Any) -> 'StringWriter':
        return self.write(*args, "\n", '  '*self._indent)
    
    @contextmanager
    def indented(self):
        self._indent += 1
        yield
        self._indent -= 1
    
    def __str__(self) -> str:
        return self.s