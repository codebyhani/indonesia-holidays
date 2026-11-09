"""Pack repository-root year files into the sdist and the wheel.

The JSON stays in git only at ``data/``. This hook runs when the package is
built. It does not write those files back into ``python/``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):  # type: ignore[type-arg]
    """Copy ``data/YYYY.json`` and ``LICENSE`` into the distribution."""

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        del version
        root = Path(self.root).resolve()
        is_year_file = _load_is_year_file(root)
        data_dir = _find_data_dir(root, is_year_file)
        year_files = sorted(
            path for path in data_dir.iterdir() if path.is_file() and is_year_file(path.name)
        )
        if not year_files:
            raise RuntimeError(f"No data/YYYY.json files were found in {data_dir}.")

        force_include = build_data.get("force_include")
        if not isinstance(force_include, dict):
            force_include = {}
            build_data["force_include"] = force_include

        for path in year_files:
            if self.target_name == "wheel":
                force_include[str(path)] = f"indonesia_holidays/data/{path.name}"
            elif _is_outside_project(root, path):
                force_include[str(path)] = f"data/{path.name}"

        license_path = _find_license(root)
        if self.target_name == "wheel":
            force_include[str(license_path)] = "indonesia_holidays/LICENSE"
        elif _is_outside_project(root, license_path):
            force_include[str(license_path)] = "LICENSE"


def _load_is_year_file(root: Path) -> Any:
    """Load ``is_year_file`` without importing the package (that reads the JSON)."""
    path = root / "src" / "indonesia_holidays" / "years.py"
    spec = importlib.util.spec_from_file_location("indonesia_holidays_years", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load year-file rules from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    is_year_file = getattr(module, "is_year_file", None)
    if not callable(is_year_file):
        raise RuntimeError(f"{path} does not define is_year_file.")
    return is_year_file


def _find_data_dir(root: Path, is_year_file: Any) -> Path:
    local = root / "data"
    if _contains_year_file(local, is_year_file):
        return local
    repo = root.parent / "data"
    # The TypeScript package marks the repository root. An unpacked sdist has no such tree.
    if (root.parent / "src" / "index.ts").is_file() and _contains_year_file(repo, is_year_file):
        return repo
    raise RuntimeError(
        "Holiday JSON was not found. Expected data/YYYY.json next to the "
        "repository README, or inside this source distribution."
    )


def _find_license(root: Path) -> Path:
    if (root.parent / "src" / "index.ts").is_file():
        parent_license = root.parent / "LICENSE"
        if parent_license.is_file():
            return parent_license
    local_license = root / "LICENSE"
    if local_license.is_file():
        return local_license
    raise RuntimeError("MIT LICENSE was not found for the Python distribution.")


def _contains_year_file(directory: Path, is_year_file: Any) -> bool:
    if not directory.is_dir():
        return False
    return any(path.is_file() and is_year_file(path.name) for path in directory.iterdir())


def _is_outside_project(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return True
    return False
