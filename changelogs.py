#!/usr/bin/env nix-shell
#! nix-shell -I nixpkgs=channel:nixos-unstable -p python3 -p python3.pkgs.libversion -p python3.pkgs.requests -i python3

from libversion import Version
from typing import Dict, Iterator, List, Optional, Tuple
import argparse
import json
import requests
import re
import sys

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

def fetch_text(uri: str) -> Optional[str]:
    '''Fetch text from a given URI.'''
    response = requests.get(uri)

    if response.ok:
        return response.text

    return None

VersionFiles = Dict[str, str]
VersionsFiles = Dict[str, VersionFiles]
Versions = List[str]
BranchFiles = Dict[str, List[str]]

LINK_PATTERN = re.compile(r'(?<!\w)(?P<prefix>!|#)(?P<number>[0-9]+)\b')

def link_match_url(pname: str, match: re.Match) -> str:
    '''Process regex match into a URL'''
    segments = {
        '!': 'merge_requests',
        '#': 'issues',
    }

    segment = segments[match.group('prefix')]
    number = match.group('number')
    url = f'https://gitlab.gnome.org/GNOME/{pname}/{segment}/{number}'

    return url

def ocs_8_link(label: str, url: str) -> str:
    '''Return OCS-8 hyperlink ANSI sequence.'''
    return f'\x1b]8;;{url}\x1b\\{label}\x1b]8;;\x1b\\'

def linkify(pname: str, text: str) -> str:
    '''Replace GitLab-style issue and merge request references in a text for OCS-8 hyperlinks.'''

    def replace_link(match: re.Match) -> str:
        label = match.group(0)
        return ocs_8_link(label, link_match_url(pname, match))

    return LINK_PATTERN.sub(replace_link, text)

def get_change(pname: str, version_name: str, group: VersionFiles, rich_text: bool) -> str:
    '''From a group of files for certain version, try to obtain files with changes. Either hand-written news or changes generated from the list of commits.'''

    changes = group.get('news', group.get('changes'))

    if changes:
        uri = f'https://ftp.gnome.org/pub/GNOME/sources/{pname}/{changes}'
        contents = fetch_text(uri)
        if rich_text:
            contents = linkify(pname, contents)

        return f'({uri})\n{contents}'

    return f'No file describing changes found for group in cluster with “{version_name}”'

def get_version_changes(pname: str, version: Version, version_files: VersionsFiles, rich_text: bool) -> str:
    return get_change(pname, version.value, version_files[version.value], rich_text)

def fetch_cache(pname: str) -> Tuple[VersionsFiles, Versions, BranchFiles]:
    '''Obtain a cache.json file for a given package and return the parsed content.'''
    cache_data = fetch_text(f'https://ftp.gnome.org/pub/GNOME/sources/{pname}/cache.json')
    cache = json.loads(cache_data)

    # The structure of cache.json: https://gitlab.gnome.org/Infrastructure/sysadmin-bin/blob/master/ftpadmin#L762
    if not isinstance(cache, list) or cache[0] != 4:
        print('Unknown format of cache.json file.', file=sys.stderr)
        sys.exit(1)

    _jsonversion, version_files, versions, branch_files = cache

    return (version_files[pname], versions[pname], branch_files)

def get_changes(pname: str, start_version: Version, end_version: Version, rich_text: bool) -> Iterator[str]:
    version_files, versions, _branch_files = fetch_cache(pname)

    def is_relevant(version):
        return start_version < version <= end_version

    relevant_versions = sorted(filter(is_relevant, map(Version, versions)))

    version_changes = map(lambda version: get_version_changes(pname, version, version_files, rich_text), relevant_versions)

    return version_changes

def main():
    parser = argparse.ArgumentParser(description='Obtain the list of changes between two versions of GNOME.')
    parser.add_argument('package-name', help='Name of the directory in https://download.gnome.org/sources/ containing the package.')
    parser.add_argument('start-version', help='Old version of package.')
    parser.add_argument('end-version', help='New version of package.')

    args = parser.parse_args()

    pname = getattr(args, 'package-name')
    start_version = Version(getattr(args, 'start-version'))
    end_version = Version(getattr(args, 'end-version'))
    rich_text = True

    for change in get_changes(pname, start_version, end_version, rich_text):
        print(change)

if __name__ == '__main__':
    main()
