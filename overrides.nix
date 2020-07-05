{ pkgs }:

final: prev: {
  libversion = prev.libversion.overridePythonAttrs (old: {
    nativeBuildInputs = old.nativeBuildInputs ++ [
      pkgs.pkg-config
    ];

    buildInputs = old.buildInputs ++ [
      pkgs.libversion
    ];
  });

  pygit2 = prev.pygit2.overridePythonAttrs (old: {
    buildInputs = old.buildInputs ++ [
      pkgs.libgit2
    ];
  });
}
