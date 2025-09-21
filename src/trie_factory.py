# src/trie_factory.py
# Build a Trie from words (k=2 by default); skips empty entries; DEBUG can print full dump + k-gram table.

from src.trie.trie import Trie
from src.utils.trie_debug import dump_trie, print_kgram_table

DEBUG = False  # set True to print debug output / False to suppress

def build(words, k=2, debug=False):
    """Build a Trie from an iterable of words."""
    t = Trie(k=k)
    for w in words:
        if not w:
            continue
        w = w.strip()
        if w:
            t.add_word(w)

    if debug:
        print("=== FULL TRIE DUMP ===")
        dump_trie(t.root)
        print_kgram_table(t)

    return t

# --- test words ---
#t = build(["hello", "help"], k=2)
#t = build(["parse", "words"], k=2)


# --- data from file ---
#with open("data/training_data.txt", encoding="utf-8") as f:
#    words = (line.strip() for line in f)
#t = build(words, k=2)