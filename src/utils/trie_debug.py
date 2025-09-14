# src/utils/trie_debug.py
# Debug helpers: dump_trie(node) prints the subtree (children + next_char_counts); print_kgram_table(trie) lists all depth-k k-grams with total next counts and their distributions.

from typing import Dict, List, Tuple


def dump_trie(node, name: str = "root", indent: int = 0) -> None:
    """Recursive, full dump of the trie nodes (structure + next_char_counts)."""
    pad = "  " * indent
    print(f"{pad}{name}: {node}")
    for ch in sorted(node.children.keys()):
        dump_trie(node.children[ch], repr(ch), indent + 1)

def print_kgram_table(trie) -> None:
    """List all depth-k nodes as k-gram -> (total_count, next_char_counts)."""
    rows: List[Tuple[str, int, Dict[str, int]]] = []

    def dfs(node, path: List[str]) -> None:
        if len(path) == trie.k:
            total = sum(node.next_char_counts.values())
            rows.append(("".join(path), total, dict(sorted(node.next_char_counts.items()))))
            return
        for ch in sorted(node.children.keys()):
            dfs(node.children[ch], path + [ch])

    dfs(trie.root, [])
    print("\n=== k-gram table (depth == k) ===")
    for kg, total, nxt in sorted(rows):
        print(f"{kg!r}: total={total}, next={nxt}")

