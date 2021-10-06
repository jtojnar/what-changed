"""
Various helper functions.
"""

from typing import Optional
import requests


def version_branch(version: str) -> str:
    """Extract branch (major plus minor segments) out of a version string."""
    return ".".join(version.split(".")[0:2])


def version_major(version: str) -> str:
    """Extract major segment out of a version string."""
    return version.split(".")[0]


def version_minor(version: str) -> str:
    """Extract minor segment out of a version string."""
    return version.split(".")[1]


def version_patch(version: str) -> str:
    """Extract patch segment out of a version string."""
    return version.split(".")[2]


def fetch_text(uri: str) -> Optional[str]:
    """Fetch text from a given URI."""
    response = requests.get(uri)

    # GNOME files are likely UTF-8 so let’s not fallback to ISO
    if response.encoding is None:
        response.encoding = "utf-8"

    if response.ok:
        return response.text

    return None


def indent(text: str) -> str:
    """Prepend tab character before every line."""
    return "\n".join(list(map(lambda line: f"\t{line}", text.split("\n"))))
