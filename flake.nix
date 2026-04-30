{
  description = "Development environment for the Frampula Scacchi Hugo website";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              hugo
              dart-sass
              go
              nodejs_22
              python3
            ];

            shellHook = ''
              export HUGO_CACHEDIR="$PWD/.hugo-cache"
              mkdir -p "$HUGO_CACHEDIR"
              echo "Frampula Scacchi dev shell"
              echo "Run: hugo server --buildDrafts --cacheDir \"$HUGO_CACHEDIR\""
            '';
          };
        });

      apps = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          serve = {
            type = "app";
            program = toString (pkgs.writeShellScript "serve-frampula-site" ''
              set -eu
              cache_dir="$PWD/.hugo-cache"
              mkdir -p "$cache_dir"
              exec ${pkgs.hugo}/bin/hugo server --buildDrafts --cacheDir "$cache_dir" "$@"
            '');
          };

          serve-future = {
            type = "app";
            program = toString (pkgs.writeShellScript "serve-frampula-site-future" ''
              set -eu
              cache_dir="$PWD/.hugo-cache"
              mkdir -p "$cache_dir"
              exec ${pkgs.hugo}/bin/hugo server --buildDrafts --buildFuture --cacheDir "$cache_dir" "$@"
            '');
          };

          build = {
            type = "app";
            program = toString (pkgs.writeShellScript "build-frampula-site" ''
              set -eu
              cache_dir="$PWD/.hugo-cache"
              mkdir -p "$cache_dir"
              exec ${pkgs.hugo}/bin/hugo --gc --minify --cacheDir "$cache_dir" "$@"
            '');
          };
        });
    };
}
