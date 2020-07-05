'''
Various helper functions.
'''

def indent(text: str) -> str:
    '''Prepend tab character before every line.'''
    return '\n'.join(list(map(lambda line: f'\t{line}', text.split('\n'))))
