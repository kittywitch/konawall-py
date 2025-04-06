{
  lib,
  buildPythonPackage,
  python,
  psmisc,
  gobject-introspection,
  gtk3,
feh,
  dbus-python,
  wrapGAppsHook,
}: let
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  poetryBlock = pyproject.tool.poetry;
  dependencyReplacements = {
    wxpython = python.pkgs.wxPython_4_2;
  };
in
  buildPythonPackage rec {
    pname = poetryBlock.name;
    version = poetryBlock.version;

    src = ./.;

    doCheck = false;

    nativeBuildInputs = [
      wrapGAppsHook
      gobject-introspection
    ];

    propagatedBuildInputs = let
      dependencyNames = (lib.attrNames poetryBlock.dependencies) ++ ["setuptools" "pygobject3" "pystray" "dbus-python"];
      dependencies = map (name: python.pkgs.${name} or dependencyReplacements.${name}) dependencyNames;
    in
      dependencies ++ [
        feh
        psmisc
      gtk3
      dbus-python
      ];

    meta = with lib; {
      description = poetryBlock.description;
      homepage = poetryBlock.homepage;
      license = licenses.${toLower poetryBlock.license};
      maintainers = with lib.maintainers; [kittywitch];
    };
  }
