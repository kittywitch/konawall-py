from setuptools import setup

with open("README.MD", "r") as f:
    long_description = f.read()


import tomllib
with open("pyproject.toml", "rb") as f:
    pyproject = tomllib.load(f)
    poetryBlock = pyproject["tool"]["poetry"]

setup(
    name = poetryBlock["name"],
    version = poetryBlock["version"],
    author = poetryBlock["authors"][0].split(" <")[0],
    author_email = poetryBlock["authors"][0].split(" <")[1][:-1],
    description = poetryBlock["description"],
    long_description = long_description,
    entry_points = {
        "console_scripts": [
            "konawall = konawall.gui:main",
        ],
    },
)