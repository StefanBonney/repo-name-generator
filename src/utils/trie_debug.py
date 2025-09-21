# src/utils/trie_debug.py
# Debug helpers: dump_trie(node) prints the subtree (children + next_char_counts); print_kgram_table(trie) lists all depth-k k-grams with total next counts and their distributions.

from typing import Dict, List, Tuple


def dump_trie(node, name: str = "root", indent: int = 0) -> None:
    """Recursive, full dump of the trie nodes (structure + next_char_counts)."""
    pad = "  " * indent
    children = node.get_children()
    next_counts = node.get_next_counts()
    print(f"{pad}{name}: children={list(children.keys())}, next={next_counts}")
    for ch in sorted(children.keys()):
        dump_trie(children[ch], repr(ch), indent + 1)

def print_kgram_table(trie) -> None:
    """List all depth-k nodes as k-gram -> (total_count, next_char_counts)."""
    rows: List[Tuple[str, int, Dict[str, int]]] = []

    def dfs(node, path: List[str]) -> None:
        if len(path) == trie.get_k():
            nxt = node.get_next_counts()
            total = sum(nxt.values())
            rows.append(("".join(path), total, dict(sorted(nxt.items()))))
            return
        children = node.get_children()
        for ch in sorted(children.keys()):
            dfs(children[ch], path + [ch])

    dfs(trie.get_root(), [])
    print("\n=== k-gram table (depth == k) ===")
    for kg, total, nxt in sorted(rows):
        print(f"{kg!r}: total={total}, next={nxt}")

