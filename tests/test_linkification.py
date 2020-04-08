import unittest

from changelogs import LINK_PATTERN, link_match_url

def linkify(text: str) -> str:
    return LINK_PATTERN.sub(lambda m: link_match_url('foo', m), text)

class TestLinkification(unittest.TestCase):

    def test_matches_gl_mr(self):
        self.assertEqual(linkify('!5'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/5')
        self.assertEqual(linkify('!29'), 'https://gitlab.gnome.org/GNOME/foo/merge_requests/29')
        self.assertEqual(linkify('dada!29'), 'dada!29')
        self.assertEqual(linkify('!29boo'), '!29boo')

    def test_matches_gl_issue(self):
        self.assertEqual(linkify('#5'), 'https://gitlab.gnome.org/GNOME/foo/issues/5')
        self.assertEqual(linkify('#29'), 'https://gitlab.gnome.org/GNOME/foo/issues/29')
        self.assertEqual(linkify('dada#29'), 'dada#29')
        self.assertEqual(linkify('#29boo'), '#29boo')

if __name__ == '__main__':
    unittest.main()
