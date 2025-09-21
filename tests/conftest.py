from pathlib import Path
from typing import Optional, Callable, Any
import pytest

@pytest.fixture(scope="session")
def repo_root(pytestconfig) -> Path:
    # pytest’s idea of the repo root (where pyproject.toml lives)
    return Path(pytestconfig.rootpath)

@pytest.fixture
def find_node() -> Callable[[Any, str], Optional[Any]]:
    """
    Return a helper function that navigates the Trie by path, instead of having to get each node and transition.
    Usage in tests:
        def test_something(find_node):
            t = Trie(k=2)
            t.add_word("hello")
            he = node_for(t, "he")
            assert he is not None
    """
    def _find_node(trie, path: str):
        node = trie.get_root()
        for ch in path:
            node = node.get_children().get(ch)
            if node is None:
                return None
        return node
    return _find_node