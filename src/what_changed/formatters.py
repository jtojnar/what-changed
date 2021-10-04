import html
import abc

class Formatter(object, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def link(self, label: str, url: str) -> str:
        raise NotImplementedError

class TerminalFormatter(Formatter):
    def link(self, label: str, url: str) -> str:
        '''Return OCS-8 hyperlink ANSI sequence.'''
        return f'\x1b]8;;{url}\x1b\\{label}\x1b]8;;\x1b\\'

class HtmlFormatter(Formatter):
    def link(self, label: str, url: str) -> str:
        '''Return HTML link.'''
        quoted_url = html.escape(url, quote=True)
        return f'<a href="{quoted_url}">{label}</a>'
