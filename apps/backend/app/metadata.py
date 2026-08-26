import tomllib
from functools import lru_cache
from pathlib import Path

_PYPROJECT_PATH = Path(__file__).resolve().parent.parent / "pyproject.toml"


@lru_cache
def get_project_metadata() -> dict[str, str]:
    """Reads [project] from pyproject.toml so app title/version live in one place."""
    data = tomllib.loads(_PYPROJECT_PATH.read_text())
    return data["project"]
