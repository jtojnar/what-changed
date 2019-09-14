#!/usr/bin/env nix-shell
#! nix-shell -p python3 -p python3.pkgs.libversion -p python3.pkgs.beautifulsoup4 -p python3.pkgs.requests -i python3

from bs4 import BeautifulSoup
from enum import Enum
from itertools import chain, groupby
from libversion import Version
from typing import Generator, Iterator, NamedTuple, Tuple
import argparse
import re
import requests

class Kind(Enum):
    '''Types of items in a directory listing.'''
    PARENT = 0
    DIR = 1
    FILE = 2

def kind_from_src(src: str) -> Kind:
    '''Convert icon path to a type of an item. Unfortunately, there is no good way to obtain file type from Apache directory listing so we are relying on item icons to discriminate the files.'''
    mappings = {
        '/icons/back.png': Kind.PARENT,
        '/icons/folder.png': Kind.DIR,
        '/icons/unknown.png': Kind.FILE,
        '/icons/compressed.png': Kind.FILE,
    }

    return mappings.get(src, Kind.FILE)

class Item(NamedTuple):
    name: str
    url: str
    kind: Kind

def version_branch(version: str) -> str:
    '''Extract branch (major plus minor segments) out of a version string.'''
    return '.'.join(version.split('.')[0:2])

def version_major(version: str) -> str:
    '''Extract major segment out of a version string.'''
    return version.split('.')[0]

def version_minor(version: str) -> str:
    '''Extract minor segment out of a version string.'''
    return version.split('.')[1]

def version_patch(version: str) -> str:
    '''Extract patch segment out of a version string.'''
    return version.split('.')[2]

def fetch_text(uri: str) -> str:
    '''Fetch text from a given URI.'''
    return requests.get(uri).text

def list_dir(url: str) -> Generator[Item, None, None]:
    '''Parse Apache directory listing from GNOME web servers.'''
    page = fetch_text(url)
    soup = BeautifulSoup(page, 'html.parser')

    for row in soup.find_all('tr'):
        img = row.select_one('td img')

        if img:
            kind = kind_from_src(img.get('src'))

            if kind != Kind.PARENT:
                link = row.find('a')

                yield Item(
                    name=link.get('href'),
                    url=url + link.get('href'),
                    kind=kind,
                )

def get_branch_dirs(pname: str) -> Iterator[Item]:
    url = f'https://download.gnome.org/sources/{pname}/'

    items = list_dir(url)

    return filter(lambda i: i.kind == Kind.DIR, items)

def name_to_base(name: str) -> str:
    '''Find a base part of a file name (i.e. ${project}-${version}).'''
    suffix_pattern = re.compile(r'\.(tar\.(xz|bz2|gz)|changes|news|sha256sum)$')

    if not suffix_pattern.search(name):
        raise RuntimeError(f'Unexpected file name “{name}”')

    return suffix_pattern.sub('', name)

def name_to_version(pname: str, name: str) -> Version:
    '''Extract just a version from a file name.'''
    return Version(name_to_base(name).lstrip(f'{pname}-'))

def get_change(group: Tuple[str, Iterator[Item]]) -> str:
    '''From a group of files for certain version, try to obtain files with changes. Either hand-written news or changes generated from the list of commits.'''
    name, files = group

    changes = None

    for file in files:
        if file.name.endswith('.changes'):
            changes = file.url
        elif file.name.endswith('.news'):
            changes = file.url
            break

    if changes:
        # There are no hand-written news, only a list of commits
        return fetch_text(changes)

    return f'No file describing changes found for group in cluster with “{name}”'

def get_branch_changes(branch: Item, pname: str, start_version: Version, end_version: Version):
    all_files = list_dir(branch.url)
    branch_name = branch.name.rstrip('/')

    version_files = filter(lambda i: i.kind == Kind.FILE and i.name.startswith(f'{pname}-{branch_name}.') and start_version <= name_to_version(pname, i.name) <= end_version, all_files)

    # the files already appear to be sorted
    version_file_groups = groupby(version_files, lambda i: name_to_base(i.name))

    return map(get_change, version_file_groups)

def get_changes(pname: str, start_version: Version, end_version: Version) -> Iterator[Item]:
    start_branch = Version(version_branch(start_version.value))
    end_branch = Version(version_branch(end_version.value))

    def is_relevant(branch):
        version = Version(branch.name.rstrip('/'))

        return start_branch <= version <= end_branch

    relevant_branches = filter(is_relevant, get_branch_dirs(pname))

    changes = map(lambda branch: get_branch_changes(branch, pname, start_version, end_version), relevant_branches)

    return chain(*changes)

def main():
    parser = argparse.ArgumentParser(description='Obtain the list of changes between two versions of GNOME.')
    parser.add_argument('package-name', help='Name of the directory in https://download.gnome.org/sources/ containing the package.')
    parser.add_argument('start-version', help='Old version of package.')
    parser.add_argument('end-version', help='New version of package.')

    args = parser.parse_args()

    pname = getattr(args, 'package-name')
    start_version = Version(getattr(args, 'start-version'))
    end_version = Version(getattr(args, 'end-version'))

    for change in get_changes(pname, start_version, end_version):
        print(change)

if __name__ == '__main__':
    main()
