import typing as T
import datetime
from dataclasses import dataclass, field

from string_writer import StringWriter


@dataclass
class HtmlElement:
    name: str
    attributes: T.Dict[str, str] = field(default_factory=dict)
    children: T.List["HtmlElement"] | str = field(default_factory=list)

    # fmt: off
    _void_elements = ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen', 'link', 'meta', 'param', 'source', 'track', 'wbr')

    def compile(self, writer: StringWriter) -> StringWriter:
        writer.indent().write(f'<', self.name)
        
        for k,v in self.attributes.items():
            writer.write(' ', k, '="', v, '" ')

        if isinstance(self.children, (str, int, datetime.timedelta)):
            return writer.write_line('>', self.children, '</', self.name, '>')
        elif self.children:
            writer.write_line('>')
            with writer.indented():
                writer.write(*self.children)
            return writer.indent().write_line(f'</', self.name, '>')
        elif self.name in self._void_elements:
            return writer.write_line(' />')
        else:
            return writer.write_line('></', self.name, '>')
