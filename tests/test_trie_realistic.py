# tests/test_trie_realistic.py
# Tests with representative repository name data. Focus: Algorithm works with actual envisioned project data patterns and outputs.

from src.trie.trie import Trie

def node_path(root, s):
    cur = root
    for ch in s:
        cur = cur.children[ch]
    return cur

def test_trie_with_representative_data():
    """
    TEST
    What: Trie with realistic repository names (representative inputs) returns expected k-gram structure 
    Why: To ensure the trie handles real-world data, not just contrived examples   
    How: Adding several common repo names, then checking key k-grams and their next-character distributions
    """
    t = Trie(k=3)
    realistic_names = [
        "react-router", "vue-cli", "typescript-eslint", 
        "babel-core", "webpack-dev-server", "jest-junit"
    ]
    
    for name in realistic_names:
        t.add_word(name)
    
    # Test that common patterns are captured
    # def node_path(root, s):       # s = "rea"
    # cur = root                    # Start at empty root
    # for ch in s:                  # ch = 'r', then 'e', then 'a'
    #   cur = cur.children[ch]      # Navigate: root→'r'→'e'→'a'
    # return cur                    # Return the 'a' node (which represents k-gram "rea")
    
    rea = node_path(t.root, "rea")
    assert "c" in rea.next_char_counts  # from "react"
    
    cli = node_path(t.root, "cli")  
    assert t.EOS in cli.next_char_counts  # "cli" can end words
