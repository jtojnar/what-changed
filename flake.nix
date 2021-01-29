{
  description = "Tool for obtaining changelogs for Nixpkgs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  inputs.utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs { inherit system; };
  in {
    devShell = pkgs.mkShell {
      buildInputs = [
        self.packages.${system}.what-changed
        pkgs.poetry
      ];
    };

    packages.what-changed = pkgs.python3.pkgs.buildPythonApplication {
      pname = "what-changed";
      version = "0.0.0";

      format = "pyproject";

      src = ./.;

      nativeBuildInputs = [
        pkgs.poetry
      ];

      propagatedBuildInputs = with pkgs.python3.pkgs; [
        libversion
        requests
        pygit2
      ];

      passthru.execPath = "/bin/what-changed";
    };

    defaultPackage = self.packages.${system}.what-changed;

    apps.what-changed = utils.lib.mkApp { drv = self.packages.${system}.what-changed; };

    defaultApp = self.apps.${system}.what-changed;
  });
}
