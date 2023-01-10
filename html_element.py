import typing as T
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
        writer.write('<', self.name)
        
        for k,v in self.attributes.items():
            writer.write(' ', k, '="', v, '" ')

        if self.children:
            writer.write_line('>')
            with writer.indented():
                if isinstance(self.children, str):
                    writer.write(self.children)
                else:
                    writer.write(*self.children)
            writer.write_line('<', self.name, '/>')
        elif self.name in self._void_elements:
            writer.write_line(' />')
        else:
            writer.write_line('><', self.name, '/>')

        return writer
