#!/usr/bin/env python

import json
from subprocess import check_call, getoutput
from typing import Any, cast

import tomlkit
from tomlkit.container import Container


def update_pyproject(new_version: str):
    with open("pyproject.toml") as f:
        pyproject = tomlkit.load(f)

    project = cast(Container, pyproject["project"])
    project["version"] = new_version

    with open("pyproject.toml", "w") as f:
        tomlkit.dump(pyproject, f)  # pyright: ignore[reportUnknownMemberType]


def update_manifest(new_version: str):
    with open("custom_components/hubitat/manifest.json") as f:
        manifest: dict[str, Any] = json.load(f)

    manifest["version"] = new_version

    with open("custom_components/hubitat/manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


latest = getoutput("git describe --tags --abbrev=0")
version = latest[1:]
[major, minor, patch] = version.split(".")
if "-pre" in patch:
    patch = int(patch.split("-")[0])
else:
    patch = int(patch) + 1
new_version = f"{major}.{minor}.{patch}"

if input(f"Publish version {new_version} [y/N]? ") != "y":
    print("Aborting")
    exit(0)

update_pyproject(new_version)
update_manifest(new_version)

_ = check_call('git commit --all -m "Update version number"', shell=True)
_ = check_call(f"git tag v{new_version}", shell=True)
_ = check_call("git push", shell=True)
_ = check_call("git push --tags", shell=True)
