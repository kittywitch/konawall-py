{
  lib,
  buildPythonPackage,
  python311Packages,
}: let
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  poetryBlock = pyproject.tool.poetry;
  dependencyReplacements = {
    wxpython = python311Packages.wxPython_4_2;
  };
in
  buildPythonPackage rec {
    pname = poetryBlock.name;
    version = poetryBlock.version;

    src = ./.;

    doCheck = false;

    propagatedBuildInputs = let
      dependencyNames = (lib.attrNames poetryBlock.dependencies) ++ ["dbus-python"];
      dependencies = map (name: python311Packages.${name} or dependencyReplacements.${name}) dependencyNames;
    in
      dependencies;

    meta = with lib; {
      description = poetryBlock.description;
      homepage = poetryBlock.homepage;
      license = licenses.${toLower poetryBlock.license};
      maintainers = with lib.maintainers; [kittywitch];
    };
  }
