import unittest

from changelogs import LINK_PATTERN, link_match_url

def linkify(text: str) -> str:
    return LINK_PATTERN.sub(lambda m: link_match_url('foo', m) or m.group(0), text)

class TestLinkification(unittest.TestCase):

    def test_matches_gl_mr(self):
        self.assertEqual(linkify('!5'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/5')
        self.assertEqual(linkify('!29'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/29')
        self.assertEqual(linkify('gitlab!52'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/52')
        self.assertEqual(linkify('GNOME/gcr!24'), 'https://gitlab.gnome.org/GNOME/gcr/merge_requests/24')
        self.assertEqual(linkify('MR!37'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/37')
        self.assertEqual(linkify('AMR!17'), 'AMR!17')
        self.assertEqual(linkify('dada!29'), 'dada!29')
        self.assertEqual(linkify('!29boo'), '!29boo')

    def test_matches_gl_issue(self):
        self.assertEqual(linkify('#5'), 'https://gitlab.gnome.org/GNOME/foo/issues/5')
        self.assertEqual(linkify('#29'), 'https://gitlab.gnome.org/GNOME/foo/issues/29')
        self.assertEqual(linkify('gitlab#52'), 'https://gitlab.gnome.org/GNOME/foo/issues/52')
        self.assertEqual(linkify('GNOME/gcr#24'), 'https://gitlab.gnome.org/GNOME/gcr/issues/24')
        self.assertEqual(linkify('dada#29'), 'dada#29')
        self.assertEqual(linkify('#29boo'), '#29boo')

    def test_matches_rst(self):
        self.assertEqual(linkify(':mr:`77`'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/77')

    def test_matches_evo(self):
        self.assertEqual(linkify('M!12'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/12')
        self.assertEqual(linkify('I#15'), 'https://gitlab.gnome.org/GNOME/foo/issues/15')
        self.assertEqual(linkify('I!13'), 'I!13')
        self.assertEqual(linkify('M#14'), 'M#14')
        self.assertEqual(linkify('AM#180'), 'AM#180')
        self.assertEqual(linkify('evo-I#52'), 'https://gitlab.gnome.org/GNOME/evolution/issues/52')
        self.assertEqual(linkify('evo-M!48'), 'https://gitlab.gnome.org/GNOME/evolution/merge_requests/48')
        self.assertEqual(linkify('evo-I!13'), 'evo-I!13')
        self.assertEqual(linkify('evo-M#14'), 'evo-M#14')
        self.assertEqual(linkify('moo-M!25'), 'moo-M!25')
        self.assertEqual(linkify('moo-I#19'), 'moo-I#19')

if __name__ == '__main__':
    unittest.main()
