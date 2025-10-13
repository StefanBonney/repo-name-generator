# tests/trie/test_trie_4_experimental.py
# Experimental Trie (EOS-enabled) checks.

from src.trie.trie_eos import TrieEOS as TrieE

def node_path(root, s: str):
    cur = root
    for ch in s:
        cur = cur.get_children()[ch]
    return cur

def test_trie_eos_marks_terminal_kgram():
    """
    TEST
    What: EOS-enabled trie records EOS at terminal k-gram
    Why: Experimental path relies on EOS for early stopping/context shifting
    How: Add 'hi' (k=2); walk to 'hi'; assert next counts contain EOS:1
    """
    t = TrieE(k=2)
    t.add_word("hi")

    hi = node_path(t.get_root(), "hi")
    assert t.EOS in hi.get_next_counts()
    assert hi.get_next_counts()[t.EOS] == 1

def test_trie_eos_keeps_regular_transitions():
    """
    TEST
    What: Non-terminal transitions remain intact alongside EOS on terminals
    Why: Ensure EOS addition doesn't break normal next-char counts
    How: Add 'hello' (k=2); check 'he'→'l' count and 'lo' has EOS:1
    """
    t = TrieE(k=2)
    t.add_word("hello")

    he = node_path(t.get_root(), "he")
    assert he.get_next_counts() == {"l": 1}

    lo = node_path(t.get_root(), "lo")
    assert lo.get_next_counts() == {t.EOS: 1}

def test_trie_eos_multiple_words_accumulate_eos():
    """
    TEST
    What: Multiple words ending with same k-gram accumulate EOS counts
    Why: Verify EOS counts work like regular character counts
    How: Add words ending in 'ing'; check EOS count increases
    """
    t = TrieE(k=3)
    t.add_word("testing")
    t.add_word("coding")
    
    ing = node_path(t.get_root(), "ing")
    assert ing.get_next_counts()[t.EOS] == 2