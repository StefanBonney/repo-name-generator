from pathlib import Path
import pytest

@pytest.fixture(scope="session")
def repo_root(pytestconfig) -> Path:
    # pytest’s idea of the repo root (where pyproject.toml lives)
    return Path(pytestconfig.rootpath)
