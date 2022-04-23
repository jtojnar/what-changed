{
  description = "Tool for obtaining changelogs for Nixpkgs";

  inputs = {
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils, ... }: utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
      };
    in
    {
      devShells = {
        default = pkgs.mkShell {
          nativeBuildInputs = [
            pkgs.python3.pkgs.black
            pkgs.python3.pkgs.poetry
            pkgs.pkg-config
            pkgs.python3.pkgs.mypy
          ];

          buildInputs = self.packages.${system}.what-changed.propagatedBuildInputs;
        };
      };

      packages = rec {
        what-changed = pkgs.python3.pkgs.buildPythonApplication {
          pname = "what-changed";
          version = "0.0.0";

          format = "pyproject";

          src = ./.;

          nativeBuildInputs = [
            pkgs.python3.pkgs.poetry-core
          ];

          propagatedBuildInputs = with pkgs.python3.pkgs; [
            libversion
            requests
            pygit2
          ];

          passthru.execPath = "/bin/what-changed";
        };

        default = what-changed;
      };

      apps = rec {
        what-changed = utils.lib.mkApp {
          drv = self.packages.${system}.what-changed;
        };

        default = what-changed;
      };
    }
  );
}
