# src/trie_factory.py
# Build a Trie from words (k=2 by default); skips empty entries; DEBUG can print full dump + k-gram table.

from src.trie.trie import Trie
from src.trie.trie_eos import TrieEOS
from src.utils.debug.trie_debug import dump_trie, print_kgram_table

def _sanitize(w: str) -> str:
    # remove '.' and '/'
    return w.replace(".", "").replace("/", "")

def build(words, k=2, debug=False, use_eos=False):
    """Build a Trie from an iterable of words.
    
    Args:
        words: Iterable of training words
        k: Markov chain degree (default 2)
        debug: Whether to print debug output
        use_eos: Whether to use EOS-enabled trie. Default False for base version, experimental passed with True.

    Returns:
        Trie (no EOS markers) when use_eos=False;
        TrieEOS (trained with word ending markers) when use_eos=True.
    """
    # Choose trie class based on use_eos flag
    if use_eos:
        t = TrieEOS(k=k)
    else:
        t = Trie(k=k)
    
    for w in words:
        if not w:                  
            continue
        w = _sanitize(w.strip())   # trim whitespace, then drop '.' and '/'
        if not w:                    # skip if stripping/sanitizing emptied it
            continue
        t.add_word(w)

    if debug:
        # Diagnostic dump: first print the full trie structure (children + next-char counts),
        # then a depth-k k-gram table with aggregate next-char distributions.
        # NOTE: very verbose on large corpora—use for small slices while debugging.
        print("=== FULL TRIE DUMP ===")
        dump_trie(t.get_root())
        print_kgram_table(t)

    return t