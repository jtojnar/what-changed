#!/usr/bin/env nix-shell
#! nix-shell -p python3 -p python3.pkgs.libversion -p python3.pkgs.requests -p python3.pkgs.pygit2 -i python3

from changelogs import get_changes
from libversion import Version
from pygit2 import Commit, Repository, GIT_SORT_TOPOLOGICAL
from typing import Generator, Optional, Tuple
from utils import indent
import argparse
import os
import subprocess
import re

def get_message_heading(message: str) -> str:
    '''Get a first line of commit message.'''
    return message.split('\n')[0]

def get_pname_for_attrname(attrname: str) -> Optional[str]:
    '''Obtain project name by evaluating the `pname` attribute of the expression denoted by the passed attribute name.'''
    pname = subprocess.run(['nix', 'eval', '-f', '.', f'{attrname}.pname', '--raw'], stdout=subprocess.PIPE, encoding='utf-8')

    if pname.returncode == 0:
        return pname.stdout

    return None

def parse_commit_heading(heading: str) -> Optional[Tuple[str, Version, Version]]:
    '''Parse nixpkgs-style commit header.'''
    msg_pattern = re.compile(r'^(?P<attrname>[^:]+):\s*(?P<old_version>.+)\s*(?:→|->)\s*(?P<new_version>.+)$')
    match = msg_pattern.match(heading)

    if match:
        attrname = match.group('attrname').strip()

        if attrname.startswith('fixup!') or attrname.startswith('squash!'):
            return None

        old_version = Version(match.group('old_version').strip())
        new_version = Version(match.group('new_version').strip())

        return (attrname, old_version, new_version)

    return None

def get_changes_for_commits(repo: Repository, start_commit: Commit, end_commit: Commit) -> Generator[Tuple[str, str, str], None, None]:
    for commit in repo.walk(end_commit.id, GIT_SORT_TOPOLOGICAL):
        heading = get_message_heading(commit.message)
        heading_info = parse_commit_heading(heading)

        changes = None

        if heading_info:
            attrname, old_version, new_version = heading_info
            pname = get_pname_for_attrname(attrname)

            if pname:
                changes = '\n\n'.join(list(get_changes(pname, old_version, new_version)))

        if not changes:
            changes = 'Unable to recognize updated package.'

        yield (commit.id, heading, changes)

        if commit.id == start_commit.id:
            # no need to continue further
            break

def main():
    parser = argparse.ArgumentParser(description='Obtain the list of changes for updates in commit range.')
    parser.add_argument('start-commit', help='First commit.')
    parser.add_argument('end-commit', help='Last commit (defaults to HEAD).', nargs='?', default='HEAD')

    args = parser.parse_args()

    repo = Repository(os.getcwd())

    start_commit = repo.revparse_single(getattr(args, 'start-commit'))
    end_commit = repo.revparse_single(getattr(args, 'end-commit'))

    for commit, heading, changes in get_changes_for_commits(repo, start_commit, end_commit):
        print(f'{commit}: {heading}')
        print(indent(changes))

if __name__ == '__main__':
    main()
