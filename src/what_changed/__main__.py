from .commits import main as handle_commits
from .changelogs import main as handle_changelogs
from .formatters import HtmlFormatter, TerminalFormatter
import argparse
import sys


def main():
    parser = argparse.ArgumentParser()

    formatters = {
        "plain": ("No postprocessing", lambda: None),
        "html": ("Add HTML links", HtmlFormatter),
        "terminal": ("Add ANSI terminal escape sequences for hyperlinks", TerminalFormatter),
    }

    parser.add_argument("--format", dest="formatter", help="Output format for post-processing (e.g. for adding hyperlinks).", default="terminal", choices=formatters.keys())

    subparsers = parser.add_subparsers()

    # create the parser for the "foo" command
    parser_changelogs = subparsers.add_parser("between-versions", description="Obtain the list of changes between two versions of GNOME.")
    parser_changelogs.add_argument("package-name", help="Name of the directory in https://download.gnome.org/sources/ containing the package.")
    parser_changelogs.add_argument("start-version", help="Old version of package.")
    parser_changelogs.add_argument("end-version", help="New version of package.")
    parser_changelogs.set_defaults(func=handle_changelogs)

    # create the parser for the "bar" command
    parser_commits = subparsers.add_parser("between-commits", description="Obtain the list of changes for updates in commit range.")
    parser_commits.add_argument("start-commit", help="First commit.")
    parser_commits.add_argument("end-commit", help="Last commit (defaults to HEAD).", nargs="?", default="HEAD")
    parser_commits.set_defaults(func=handle_commits)

    args = parser.parse_args()
    setattr(args, "formatter", formatters[getattr(args, "formatter")][1]())

    if "func" in args:
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
