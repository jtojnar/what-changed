# what-changed

This is a simple tool for finding out what changes were made between two versions of a software project. Currently, GNOME mirrors are supported as a source.

## Usage

With Flakes-enabled Nix, you can just execute `nix run github:jtojnar/what-changed args…` in your nixpkgs repository.

With legacy Nix, you can install the package by importing the Git repository and then using the `default` package: `nix-env -f https://github.com/jtojnar/what-changed/archive/master.tar.gz -iA default`

## Tools
### `what-changed between-versions`

You can run it as follows:

```
what-changed between-versions glib 2.52.2 2.54.6
```

### `what-changed between-commits`

Analyze the commits in the current working directory for updates.

Pass the first and last commit refs as arguments.

```
what-changed between-commits a756e266d6e0f8bd0f58acb91ff57f101dd8ac7c HEAD
```

The last commit can be omitted, in which case it will default to `HEAD`.

```
what-changed between-commits a756e266d6e0f8bd0f58acb91ff57f101dd8ac7c
```

Commits need to follow Nixpkgs guidelines on commit messages, that is match the following format:

```
attrname: old.version → new.version
```

The project name will be obtained by evaluating the `pname` attribute of the expression denoted by the passed attribute name.
