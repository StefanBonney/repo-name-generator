# tests/trie/test_trie_1_basic.py
# Simple unit tests for basic Trie functionality. Focus: Individual methods work correctly with small inputs.

from src.trie.trie import Trie, TrieNode

def node_path(root, s):
    cur = root
    for ch in s:
        cur = cur.get_children()[ch]
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
    assert set(t.get_root().get_children().keys()) >= {"h", "e", "l"}

    # Test k-gram "he" -> 'l' (from "he"llo)
    he = node_path(t.get_root(), "he") # Navigate to the "he" node
    assert he.get_next_counts() == {"l": 1} # 'l' follows "he" once

    # Test k-gram "el" -> 'l' (from h"el"lo) 
    el = node_path(t.get_root(), "el") 
    assert el.get_next_counts() == {"l": 1} 

    # Test k-gram "ll" -> 'o' (from he"ll"o)
    ll = node_path(t.get_root(), "ll")
    assert ll.get_next_counts() == {"o": 1}

    # Test final k-gram "lo" -> {}
    lo = node_path(t.get_root(), "lo")
    assert lo.get_next_counts() == {} # terminal: no next chars

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
    he = node_path(t.get_root(), "he")
    assert he.get_next_counts() == {"l": 2} # 'l' follows "he" twice (hello + help)

    # Test k-gram "el" - appears in both words but with different next chars
    el = node_path(t.get_root(), "el")
    assert el.get_next_counts() == {"l": 1, "p": 1}

    # Test k-gram "ll" - only appears in "hello"
    ll = node_path(t.get_root(), "ll")
    assert ll.get_next_counts() == {"o": 1}

    # Terminal k-grams have no next characters
    lo = node_path(t.get_root(), "lo")
    lp = node_path(t.get_root(), "lp")
    assert lo.get_next_counts() == {}
    assert lp.get_next_counts() == {}

def test_trie_get_k_and_root_exist():
    """
    TEST
    What: Basic getters work (k, root)
    Why: Ensure returns expected values/types
    How: Trie(k=3) → get_k()==3; get_root() is TrieNode
    """
    t = Trie(k=3)
    assert t.get_k() == 3
    root = t.get_root()
    assert isinstance(root, TrieNode)

def test_trienode_children_and_next_counts_are_empty_initially():
    """
    TEST
    What: Fresh TrieNode is empty
    Why: Verify clean initialization
    How: Assert children=={} and next_counts=={}
    """
    node = TrieNode()
    assert node.get_children() == {}
    assert node.get_next_counts() == {}

def test_getter_add_word_short_creates_expected_transitions():
    """
    TEST
    What: Getters expose that the final k-gram is terminal for a short word ("hi") with k=2
    Why: Verify read-only (get_root/get_children/get_next_counts) surfaces end-of-word info
    How: Add "hi"; via getters walk to "hi"; assert no next characters (terminal)
    """
    t = Trie(k=2)
    t.add_word("hi")

    root = t.get_root()
    # First char 'h' should be a child of root
    assert "h" in root.get_children()
    # Walk to "h" -> "i"
    node_h = root.get_children()["h"]
    assert "i" in node_h.get_children()
    node_hi = node_h.get_children()["i"]

    # Since word == "hi", final k-gram = "hi" is terminal
    assert node_hi.get_next_counts() == {}

def test_getter_add_word_longer_creates_expected_transitions():
    """
    TEST
    What: Getters expose intermediate k-gram transitions for a longer word ("hello") with k=2
    Why: Ensure non-terminal next-char counts are observable via getters (no internals)
    How: Add "hello"; via getters walk to "he" and "el"; assert expected next_char_counts
    """
    t = Trie(k=2)
    t.add_word("hello")

    # "he" should predict 'l'
    node_h = t.get_root().get_children()["h"]
    node_he = node_h.get_children()["e"]
    assert node_he.get_next_counts() == {"l": 1}

    # "lo" should be terminal (no next characters)
    node_l  = t.get_root().get_children()["l"]
    node_lo = node_l.get_children()["o"]
    assert node_lo.get_next_counts() == {}

def test_getters_and_helper_expose_next_counts(find_node):
    """
    TEST
    What: Getters + traversal helper function, find_node, reach 'he' and expose its next-char counts
    Why : Verifies both the simple getters and the helper that is built on top of them; if either breaks, traversal or counts will fail
    How : Add 'hello' (k=2), walk to 'he' with node_for, assert next == {'l': 1}
    """
    t = Trie(k=2)
    t.add_word("hello")
    he = find_node(t, "he")
    assert he is not None                        # reached via getters
    assert he.get_next_counts() == {"l": 1}


def test_duplicate_insertions_increase_counts(find_node):
    t = Trie(k=2)
    t.add_word("hello")
    t.add_word("hello")  # add same word twice

    he = find_node(t, "he")
    el = find_node(t, "el")
    ll = find_node(t, "ll")

    assert he.get_next_counts() == {"l": 2}
    assert el.get_next_counts() == {"l": 2}
    assert ll.get_next_counts() == {"o": 2}