"""Check that a build packs the shared year files and does not vendor them in git."""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path


def main() -> None:
    python_root = Path(__file__).resolve().parents[1]
    repo_root = python_root.parent
    dist = python_root / "dist"
    wheels = sorted(dist.glob("*.whl"))
    sdists = sorted(dist.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise SystemExit(
            f"Expected one wheel and one sdist in {dist}, found {wheels} and {sdists}."
        )

    year_files = sorted(
        path.name
        for path in (repo_root / "data").iterdir()
        if path.is_file() and len(path.stem) == 4 and path.stem.isdigit() and path.suffix == ".json"
    )
    if year_files != ["2026.json", "2027.json"]:
        raise SystemExit(f"Unexpected repository year files: {year_files}.")

    vendored = python_root / "src" / "indonesia_holidays" / "data"
    if (python_root / "data").exists() or vendored.exists():
        raise SystemExit(
            "Year files were copied into python/. Keep them only in the repository data/ directory."
        )

    with zipfile.ZipFile(wheels[0]) as wheel:
        names = set(wheel.namelist())
        for name in year_files:
            archived = f"indonesia_holidays/data/{name}"
            if archived not in names:
                raise SystemExit(f"{wheels[0].name} is missing {archived}.")
            if wheel.read(archived) != (repo_root / "data" / name).read_bytes():
                raise SystemExit(f"{archived} does not match the repository file.")
        if any(name.startswith("data/") for name in names):
            raise SystemExit("The wheel also contains a top-level data/ copy.")
        if "indonesia_holidays/LICENSE" not in names:
            raise SystemExit("The wheel is missing indonesia_holidays/LICENSE.")

    with tarfile.open(sdists[0]) as sdist:
        archived_names = sdist.getnames()
        for name in year_files:
            matches = [item for item in archived_names if item.endswith(f"/data/{name}")]
            if len(matches) != 1:
                raise SystemExit(
                    f"{sdists[0].name} should contain data/{name} once, found {matches}."
                )
            extracted = sdist.extractfile(matches[0])
            if extracted is None or extracted.read() != (repo_root / "data" / name).read_bytes():
                raise SystemExit(f"sdist {name} does not match the repository file.")
        vendored_in_sdist = any(
            item.endswith(f"/src/indonesia_holidays/data/{name}")
            for item in archived_names
            for name in year_files
        )
        if vendored_in_sdist:
            raise SystemExit("The sdist vendors year files inside the package source tree.")

    _import_installed_wheel(wheels[0])
    print(f"Verified {wheels[0].name} and {sdists[0].name}.")


def _import_installed_wheel(wheel: Path) -> None:
    """Import the wheel from a clean directory so the checkout fallback cannot run.

    ``pip install --target`` avoids ``venv``, which is not available in every
    build image. ``PYTHONPATH`` points only at that target, and the process
    cwd is the temp directory rather than the repository.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "site"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-deps",
                "--target",
                str(target),
                str(wheel),
            ],
            check=True,
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(target)
        env["IH_TARGET"] = str(target)
        probe = """
import os
from datetime import date
from pathlib import Path
import indonesia_holidays
from indonesia_holidays import get_holiday, is_holiday, list_supported_years
installed = Path(indonesia_holidays.__file__).resolve()
assert installed.is_relative_to(Path(os.environ["IH_TARGET"]))
assert list_supported_years() == (2026, 2027)
assert is_holiday(date(2026, 1, 1)) is True
holiday = get_holiday("2026-08-17")
assert holiday is not None and holiday.date == "2026-08-17" and isinstance(holiday.date, str)
packaged = installed.parent / "data"
assert (packaged / "2026.json").is_file()
assert (packaged / "2027.json").is_file()
print("wheel import ok")
"""
        subprocess.run(
            [sys.executable, "-c", probe],
            cwd=temp_dir,
            env=env,
            check=True,
        )


if __name__ == "__main__":
    main()
