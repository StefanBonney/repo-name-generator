# tests/test_trie_simple.py
# Simple unit tests for basic Trie functionality. Focus: Individual methods work correctly with small inputs.

from src.trie.trie import Trie

def node_path(root, s):
    cur = root
    for ch in s:
        cur = cur.children[ch]
    return cur

def test_add_word_hello_k2_structure():
    """
    TEST
    What: Basic trie construction from single word with k=2
    Why: Trie correctly stores k-grams and next-character transitions
    How: Adding "hello", then navigating to each k-gram node and asserting correct next_char_counts
    """
    t = Trie(k=2)
    t.add_word("hello")

    # Verify the root has branches for all starting characters of k-grams: h(e), e(l), l(l)
    assert set(t.root.children.keys()) >= {"h", "e", "l"}

    # Test k-gram "he" -> 'l' (from "he"llo)
    he = node_path(t.root, "he") # Navigate to the "he" node
    assert he.next_char_counts == {"l": 1} # 'l' follows "he" once

    # Test k-gram "el" -> 'l' (from h"el"lo) 
    el = node_path(t.root, "el") 
    assert el.next_char_counts == {"l": 1} 

    # Test k-gram "ll" -> 'o' (from he"ll"o)
    ll = node_path(t.root, "ll")
    assert ll.next_char_counts == {"o": 1}

    # Test final k-gram "lo" -> <EOS> (word ends after "lo")
    lo = node_path(t.root, "lo")
    assert lo.next_char_counts == {t.EOS: 1}

def test_add_word_help_updates_counts():
    """
    TEST
    What: Trie updating with multiple words sharing k-grams
    Why: To show counts accumulate and probabilistic next-character options work
    How: Adding two words with shared k-grams, then verifying next-character counts aggregate and multiple next-chars are tracked
    """
    t = Trie(k=2)
    t.add_word("hello") # First word: creates initial structure
    t.add_word("help") # Second word: should update existing paths

    # Test k-gram "he" appears in both words
    he = node_path(t.root, "he")
    assert he.next_char_counts == {"l": 2} # 'l' follows "he" twice (hello + help)

    # Test k-gram "el" - appears in both words but with different next chars
    el = node_path(t.root, "el")
    assert el.next_char_counts == {"l": 1, "p": 1}

    # Test k-gram "ll" - only appears in "hello"
    ll = node_path(t.root, "ll")
    assert ll.next_char_counts == {"o": 1}

    # Test both final k-grams have EOS markers
    lo = node_path(t.root, "lo")
    lp = node_path(t.root, "lp")
    assert lo.next_char_counts == {t.EOS: 1}
    assert lp.next_char_counts == {t.EOS: 1}
