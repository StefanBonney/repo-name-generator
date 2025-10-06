# tests/trie/test_trie_3_quality.py
# Tests with representative repository name data. Focus: Algorithm works with actual envisioned project data patterns and outputs.

from src.trie.trie import Trie

def node_path(root, s):
    cur = root
    for ch in s:
        cur = cur.get_children()[ch]
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
    # def node_path(root, s):        # s = "rea"
    # cur = root                     # Start at empty root
    # for ch in s:                   # ch = 'r', then 'e', then 'a'
    #   cur = cur.get_children()[ch] # Navigate: root→'r'→'e'→'a'
    # return cur                     # Return the 'a' node (which represents k-gram "rea")
    
    # "rea" should have 'c' as a possible next char (from "react")
    rea = node_path(t.get_root(), "rea")
    assert "c" in rea.get_next_counts()  # from "react"
    
    # "cli" is terminal in "vue-cli" → no next chars in base trie
    cli = node_path(t.get_root(), "cli")  
    assert cli.get_next_counts() == {}


def test_trie_learns_delimiter_patterns(repo_root):
    """
    TEST
    What: Trie correctly captures delimiter transitions (hyphen, underscore) from training data
    Why: Notebook analysis showed hyphen ratio 0.04-0.06 is optimal; trie must learn these patterns
    How: Load real training data with delimiters; verify k-grams before delimiters have correct next-char distributions
    """
    t = Trie(k=3)
    
    # Load subset of training data
    data_path = repo_root / "data" / "training_data.txt"
    delimiter_words = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            w = line.strip()
            if len(w) >= 3 and ('-' in w or '_' in w):
                t.add_word(w)
                delimiter_words.append(w)
    
    # Should have learned some delimiter patterns
    assert len(delimiter_words) > 0, "No delimiter patterns in training data subset"
    
    # Find a k-gram that precedes a hyphen in training data
    hyphen_trigrams = set()
    for word in delimiter_words:
        if '-' in word:
            idx = word.index('-')
            if idx >= 3:  # Need at least k chars before hyphen
                trigram = word[idx-3:idx]
                hyphen_trigrams.add(trigram)
    
    # Verify at least one learned pattern
    assert len(hyphen_trigrams) > 0, "No k-grams before hyphens found"
    
    # Check that trie learned the hyphen transition
    sample_trigram = list(hyphen_trigrams)[0]
    node = node_path(t.get_root(), sample_trigram)
    next_counts = node.get_next_counts()
    
    assert '-' in next_counts, \
        f"Trie failed to learn hyphen transition after '{sample_trigram}'"
    assert next_counts['-'] > 0, \
        f"Hyphen count should be positive for '{sample_trigram}'"


def test_trie_character_distribution_matches_corpus(repo_root):
    """
    TEST
    What: Trie's next-character probabilities reflect actual corpus character frequency
    Why: Notebook identified character contamination issues (periods, slashes); 
         trie learning must be validated against actual corpus statistics
    How: Load training data; for a common k-gram, verify next-char distribution 
         correlates with corpus frequency (not uniform/random)
    """
    t = Trie(k=3)
    
    # Load training data and track character frequencies
    data_path = repo_root / "data" / "training_data.txt"
    corpus_words = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)
                corpus_words.append(w)
    
    # Pick a common k-gram that appears multiple times
    test_trigram = "tes"
    
    # Manually count what actually follows "tes" in corpus
    actual_next_chars = {}
    for word in corpus_words:
        idx = word.find(test_trigram)
        while idx != -1 and idx + 3 < len(word):
            next_ch = word[idx + 3]
            actual_next_chars[next_ch] = actual_next_chars.get(next_ch, 0) + 1
            idx = word.find(test_trigram, idx + 1)
    
    if not actual_next_chars:
        # Fallback if "tes" not common - use any k-gram from first word
        if corpus_words and len(corpus_words[0]) >= 4:
            test_trigram = corpus_words[0][:3]
            next_ch = corpus_words[0][3]
            actual_next_chars = {next_ch: 1}
        else:
            assert False, "Insufficient test data"
    
    # Get trie's learned distribution
    try:
        node = node_path(t.get_root(), test_trigram)
        trie_next_counts = node.get_next_counts()
    except KeyError:
        assert False, f"Trie didn't learn common k-gram '{test_trigram}'"
    
    # Verify trie learned the same characters (allowing for some missing due to sampling)
    common_chars = set(actual_next_chars.keys()) & set(trie_next_counts.keys())
    coverage = len(common_chars) / len(actual_next_chars) if actual_next_chars else 0
    
    assert coverage >= 0.7, \
        f"Trie only learned {coverage:.1%} of actual next-chars for '{test_trigram}'"
    
    # Verify most frequent character in corpus is also most frequent in trie
    if actual_next_chars and trie_next_counts:
        corpus_top = max(actual_next_chars.items(), key=lambda x: x[1])[0]
        trie_top = max(trie_next_counts.items(), key=lambda x: x[1])[0]
        
        assert corpus_top == trie_top, \
            f"Trie's most frequent next-char ('{trie_top}') doesn't match corpus ('{corpus_top}')"