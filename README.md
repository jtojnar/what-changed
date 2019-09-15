# what-changed

This is a simple tool for finding out what changes were made between two versions of a software project. Currently, GNOME mirrors are supported as a source.

## Tools
### `changelogs`

You can run it as follows:

```
./changelogs.py glib 2.52.2 2.54.6
```

### `commits`

Analyze the commits in the current working directory for updates.

Pass the first and last commit refs as arguments.

```
./commits.py a756e266d6e0f8bd0f58acb91ff57f101dd8ac7c HEAD
```

The last commit can be omitted, in which case it will default to `HEAD`.

```
./commits.py a756e266d6e0f8bd0f58acb91ff57f101dd8ac7c
```

Commits need to follow Nixpkgs guidelines on commit messages, that is match the following format:

```
attrname: old.version → new.version
```

The project name will be obtained by evaluating the `pname` attribute of the expression denoted by the passed attribute name.
