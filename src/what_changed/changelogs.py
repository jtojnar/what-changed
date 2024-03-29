from .formatters import Formatter
from .utils import fetch_text
from libversion import Version
from typing import Dict, Iterator, List, Optional, Tuple
import json
import re
import sys

VersionFiles = Dict[str, str]
VersionsFiles = Dict[str, VersionFiles]
Versions = List[str]
BranchFiles = Dict[str, List[str]]

LINK_PATTERN = re.compile(
    r"""
     (?<!\w)(?:gitlab|(?P<cross>GNOME/[a-z-]+))?(?P<prefix>(?:MR)?!|\#)(?P<number>[0-9]+)\b # common GitLab references !12, #15, GNOME/gcr!24, gitlab#25, gitlab!37, MR!17
    |:(?P<rst_prefix>(issue|mr)):`(?P<rst_number>[0-9]+)` # reStructuredText references: :issue:`15`, :mr:`12`
    |(?<!\w)(?:(?P<evo_cross>[a-z]+)-)?(?P<evo_prefix>M!|I\#)(?P<evo_number>[0-9]+)\b # used by mcrha’s projects: M!12, I#15, evo-I#25
    |LP:\#(?P<launchpad_number>[0-9]+) # launchpad link: LP:#1234567
""",
    re.VERBOSE,
)


def link_match_url(pname: str, match: re.Match) -> Optional[str]:
    """Process regex match into a URL"""
    if match.group("number"):
        segments = {
            "!": "merge_requests",
            "MR!": "merge_requests",
            "#": "issues",
        }

        repo = match.group("cross") or f"GNOME/{pname}"
        segment = segments[match.group("prefix")]
        number = match.group("number")
    elif match.group("rst_number"):
        segments = {
            "issue": "issues",
            "mr": "merge_requests",
        }

        repo = f"GNOME/{pname}"
        segment = segments[match.group("rst_prefix")]
        number = match.group("rst_number")
    elif match.group("evo_number"):
        xlink_mapping = {
            "evo": "evolution",
            "eds": "evolution-data-server",
            "ews": "evolution-ews",
            None: pname,
        }
        segments = {
            "M!": "merge_requests",
            "I#": "issues",
        }

        if match.group("evo_cross") not in xlink_mapping:
            return None

        repo = "GNOME/{}".format(xlink_mapping[match.group("evo_cross")])
        segment = segments[match.group("evo_prefix")]
        number = match.group("evo_number")
    elif match.group("launchpad_number"):
        number = match.group("launchpad_number")

        # We are using the Launchpad project, it will be redirected to the correct one.
        return f"https://bugs.launchpad.net/launchpad/+bug/{number}"

    return f"https://gitlab.gnome.org/{repo}/{segment}/{number}"


def linkify(pname: str, text: str, formatter: Formatter) -> str:
    """Replace GitLab-style issue and merge request references in a text for hyperlinks."""

    def replace_link(match: re.Match) -> str:
        label = match.group(0)
        url = link_match_url(pname, match)
        return formatter.link(label, url) if url else label

    return LINK_PATTERN.sub(replace_link, text)


def get_change(pname: str, version_name: str, group: VersionFiles, formatter: Optional[Formatter]) -> str:
    """From a group of files for certain version, try to obtain files with changes. Either hand-written news or changes generated from the list of commits."""

    changes = group.get("news", group.get("changes"))

    if changes:
        uri = f"https://ftp.gnome.org/pub/GNOME/sources/{pname}/{changes}"
        contents = fetch_text(uri)
        if not contents:
            contents = "Unable to fetch"
        if formatter:
            contents = linkify(pname, contents, formatter)

        return f"({uri})\n{contents}"

    return f"No file describing changes found for group in cluster with “{version_name}”"


def get_version_changes(pname: str, version: Version, version_files: VersionsFiles, formatter: Optional[Formatter]) -> str:
    return get_change(pname, version.value, version_files[version.value], formatter)


def fetch_cache(pname: str) -> Tuple[VersionsFiles, Versions, BranchFiles]:
    """Obtain a cache.json file for a given package and return the parsed content."""
    cache_data = fetch_text(f"https://ftp.gnome.org/pub/GNOME/sources/{pname}/cache.json")
    if not cache_data:
        print(f"Unable to fetch cache.json for {pname}.", file=sys.stderr)
        sys.exit(1)

    cache = json.loads(cache_data)

    # The structure of cache.json: https://gitlab.gnome.org/Infrastructure/sysadmin-bin/blob/master/ftpadmin#L762
    if not isinstance(cache, list) or cache[0] != 4:
        print("Unknown format of cache.json file.", file=sys.stderr)
        sys.exit(1)

    _jsonversion, version_files, versions, branch_files = cache

    return (version_files[pname], versions[pname], branch_files)


def get_changes(pname: str, start_version: Version, end_version: Version, formatter: Optional[Formatter]) -> Iterator[str]:
    version_files, versions, _branch_files = fetch_cache(pname)

    def is_relevant(version):
        return start_version < version <= end_version

    relevant_versions = sorted(filter(is_relevant, map(Version, versions)))

    version_changes = map(lambda version: get_version_changes(pname, version, version_files, formatter), relevant_versions)

    return version_changes


def main(args):
    pname = getattr(args, "package-name")
    start_version = Version(getattr(args, "start-version"))
    end_version = Version(getattr(args, "end-version"))
    formatter = getattr(args, "formatter")

    for change in get_changes(pname, start_version, end_version, formatter):
        print(change)
