{
  description = "Tool for obtaining changelogs for Nixpkgs";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  inputs.utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem (system: let
    pkgs = import nixpkgs { inherit system; };
    overrides = [
      pkgs.poetry2nix.defaultPoetryOverrides
      (import ./overrides.nix { inherit pkgs; })
    ];
  in {
    devShell = pkgs.mkShell {
      buildInputs = [
        (pkgs.poetry2nix.mkPoetryEnv {
          projectDir = ./.;

          inherit overrides;
        })
        pkgs.poetry
      ];
    };

    packages.what-changed = pkgs.poetry2nix.mkPoetryApplication {
      projectDir = ./.;

      inherit overrides;

      passthru.execPath = "/bin/what-changed";
    };

    defaultPackage = self.packages.${system}.what-changed;

    apps.what-changed = utils.lib.mkApp { drv = self.packages.${system}.what-changed; };

    defaultApp = self.apps.${system}.what-changed;
  });
}
