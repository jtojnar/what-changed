import html

class Formatter(object):
    pass

class TerminalFormatter(object):
    def link(self, label: str, url: str) -> str:
        '''Return OCS-8 hyperlink ANSI sequence.'''
        return f'\x1b]8;;{url}\x1b\\{label}\x1b]8;;\x1b\\'

class HtmlFormatter(object):
    def link(self, label: str, url: str) -> str:
        '''Return HTML link.'''
        quoted_url = html.escape(url, quote=True)
        return f'<a href="{quoted_url}">{label}</a>'
