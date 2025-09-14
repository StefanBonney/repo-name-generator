# tests/test_trie_performance.py
# Validates construction timing and memory efficiency. Focus: Algorithm speed, scalability, and optimal memory usage patterns.


import time
from src.trie.trie import Trie
# tests/test_trie_memory_limits.py
import gc, tracemalloc
import pytest
from pathlib import Path

def node_path(root, s):
    cur = root
    for ch in s:
        cur = cur.children[ch]
    return cur

def test_trie_performance_duration_under_set_limit():
    """
    TEST
    What: Trie construction performance with larger dataset
    Why : Algorithm scales reasonably for production use (1.5M training data)
    How : Timing trie construction and generation with 1000+ words
    """
    t = Trie(k=2)
    
    # Generate test data similar to real repo names
    #test_words = []
    #prefixes = ["react", "vue", "angular", "babel", "webpack", "jest", "eslint"]
    #suffixes = ["cli", "core", "plugin", "loader", "config", "utils", "dev"]
    
    #for prefix in prefixes:
    #    for suffix in suffixes:
    #        test_words.extend([prefix, suffix, f"{prefix}-{suffix}"])
        
    # Load first 1000 lines from actual training data
    test_words = []
    with open('data/training_data.txt', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:  # Stop at 1000 words for performance test
                break
            test_words.append(line.strip())
    
    # Test construction time
    start_time = time.time()
    for word in test_words:
        t.add_word(word)
    construction_time = time.time() - start_time
    
    # Should handle ~150 words in reasonable time (< 1 second)
    assert construction_time < 1.0, f"Trie construction too slow: {construction_time:.3f}s"
    
    # Verify structure is correct
    assert len(t.root.children) > 0
    assert sum(node_path(t.root, "re").next_char_counts.values()) > 0

def test_trie_memory_kgram_sharing_counts():
    """
    TEST
    What: Verify k-gram nodes are shared and counts reflect total occurrences across words
    Why : Ensures memory efficiency via node reuse (no duplication on shared paths)
    How : Insert ["hello","help","helm","held"]; check "he" and "el" frequencies and transitions
    """
    t = Trie(k=2)

    # Words that share many k-grams
    shared_words = ["hello", "help", "helm", "held"]
    for word in shared_words:
        t.add_word(word)

    # "he" occurs once in each of the 4 words -> 4 occurrences
    he_node = node_path(t.root, "he")
    assert sum(he_node.next_char_counts.values()) == 4

    # "el" also occurs once in each of the 4 words -> 4 occurrences
    el_node = node_path(t.root, "el")
    assert sum(el_node.next_char_counts.values()) == 4

    # verify the transition distribution from "el"
    # hello -> 'l', help -> 'p', helm -> 'm', held -> 'd'
    assert el_node.next_char_counts == {"l": 1, "p": 1, "m": 1, "d": 1}

    # final k-grams each end the word once
    for end in ["lo", "lp", "lm", "ld"]:
        end_node = node_path(t.root, end)
        assert end_node.next_char_counts.get(t.EOS, 0) == 1

@pytest.mark.perf
def test_trie_peak_memory_under_budget(repo_root):
    LIMIT_MB = 20   # tune per machine/CI
    N = 2000

    path = repo_root / "data" / "training_data.txt"
    words = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= N: break
            w = line.strip()
            if w: words.append(w)

    gc.collect()
    tracemalloc.start()
    t = Trie(k=2)
    for w in words:
        if len(w) >= t.k:
            t.add_word(w)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024*1024)
    assert peak_mb < LIMIT_MB, f"Peak {peak_mb:.2f} MiB > {LIMIT_MB} MiB"