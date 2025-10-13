# src/trie_factory.py
# Build a Trie from words (k=2 by default); skips empty entries; DEBUG can print full dump + k-gram table.

from src.trie.trie import Trie
from src.trie.trie_eos import TrieEOS
from src.utils.debug.trie_debug import dump_trie, print_kgram_table

DEBUG = False  # set True to print debug output / False to suppress

def _sanitize(w: str) -> str:
    # Only remove '.' and '/'
    return w.replace(".", "").replace("/", "")

def build(words, k=2, debug=False, use_eos=False):
    """Build a Trie from an iterable of words.
    
    Args:
        words: Iterable of training words
        k: Markov chain degree (default 2)
        debug: Whether to print debug output
        use_eos: Whether to use EOS-enabled trie (default False for base version)

    Returns:
        Trie (no EOS markers) when use_eos=False;
        TrieEOS (trained with word ending markers) when use_eos=True.
        
        In this project, experimental mode sets use_eos=True, so
        experimental runs yield TrieEOS while base runs yield Trie,
        although user can specify to use TrieEOS in base mode.
    """
    # Choose trie class based on use_eos flag
    if use_eos:
        t = TrieEOS(k=k)
    else:
        t = Trie(k=k)
    
    for w in words:
        if not w:
            continue
        w = w.strip()
        if not w:
            continue
        w = _sanitize(w)        # ← sanitize once here
        if not w:
            continue            # skip entries that become empty after sanitize
        t.add_word(w)

    if debug:
        print("=== FULL TRIE DUMP ===")
        dump_trie(t.root)
        print_kgram_table(t)

    return t