# tests/trie/test_trie_5_eos_quality.py
# Experimental Trie (EOS-enabled) checks: quality

from src.trie.trie_eos import TrieEOS as TrieEOS


def node_path(root, s: str):
    cur = root
    for ch in s:
        cur = cur.get_children()[ch]
    return cur

def test_trie_learns_delimiter_patterns(repo_root):
    """
    TEST
    What: Trie learns hyphen transitions at healthy ratio
    Why: Notebook showed hyphen_ratio 0.04-0.06 is optimal for quality
    How: Load training data; verify hyphen transition ratio is in reasonable range
    """
    t = TrieEOS(k=3)
    
    data_path = repo_root / "data" / "training_data.txt"
    total_transitions = 0
    hyphen_transitions = 0
    
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)
    
    # Count all transitions and hyphen transitions in the trie
    def count_transitions(node):
        nonlocal total_transitions, hyphen_transitions
        next_counts = node.get_next_counts()
        for char, count in next_counts.items():
            if char != t.EOS:  # Exclude EOS from ratio calculation
                total_transitions += count
                if char == '-':
                    hyphen_transitions += count
        for child in node.get_children().values():
            count_transitions(child)
    
    count_transitions(t.get_root())
    
    assert total_transitions > 0, "No transitions learned"
    
    hyphen_ratio = hyphen_transitions / total_transitions if total_transitions > 0 else 0
    
    # Notebook optimal: 0.04-0.06, but allow wider range for robustness
    assert 0.02 <= hyphen_ratio <= 0.15, \
        f"Hyphen ratio {hyphen_ratio:.3f} outside healthy range (0.02-0.15)"


def test_trie_eos_enables_early_stopping(repo_root):
    """
    TEST
    What: Terminal k-grams have EOS at healthy ratio
    Why: Notebook analysis showed EOS improves boundary detection
    How: Load training data; verify reasonable proportion of terminal k-grams learned EOS
    """
    t = TrieEOS(k=3)
    
    data_path = repo_root / "data" / "training_data.txt"
    words = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 100:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)
                words.append(w)
    
    # Check terminal k-grams have EOS
    terminal_kgrams = [w[-3:] for w in words]
    eos_count = 0
    valid_count = 0
    
    for kgram in terminal_kgrams:
        try:
            node = node_path(t.get_root(), kgram)
            valid_count += 1
            if t.EOS in node.get_next_counts():
                eos_count += 1
        except KeyError:
            pass
    
    assert valid_count > 0, "No terminal k-grams found in trie"
    
    eos_ratio = eos_count / valid_count
    
    # At least 50% of terminal k-grams should have EOS (healthy boundary)
    assert eos_ratio >= 0.5, \
        f"Only {eos_ratio:.1%} of terminal k-grams have EOS (expected ≥50%)"