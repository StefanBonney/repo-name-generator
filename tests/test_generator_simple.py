# tests/test_trie_simple.py
# Simple unit tests for basic Generator functionality. Focus: Individual methods work correctly with small inputs.

import random
from pathlib import Path
from src.trie.trie import Trie
from src.generator.generator import Generator

def test_seed_preservation_in_generated_output():
    """
    TEST
    What: Generator preserves the seed at the beginning of generated text
    Why: Seed-based generation must always start with the provided seed
    How: Generate from "he" seed, verify output starts with "he"
    """
    t = Trie(k=2)
    test_words = ["hello", "help", "hero"]
    for w in test_words:
        t.add_word(w)
    
    gen = Generator(t)
    random.seed(42)
    
    result = gen.generate("he", 8)
    assert result.startswith("he")
    assert len(result) > 2  # Should generate beyond just the seed

def test_max_length_constraint_is_respected():
    """
    TEST
    What: Generator stops at or before max_length parameter
    Why: Check user specified output length is respected
    How: Generate with various max_length values, verify none exceed limit
    """
    t = Trie(k=2)
    t.add_word("infinite")  # Long word for testing
    
    gen = Generator(t)
    
    for max_len in [3, 5, 7]:
        result = gen.generate("in", max_len)
        assert len(result) <= max_len

#def test_generation_stops_at_eos_marker():
    """
    TEST
    What: Generator stops when encountering EOS even if max_length not reached
    Why: Natural word endings should be respected over arbitrary length
    How: Generate from "h" with max_length=10, verify stops at "hi" due to EOS
    """
#    t = Trie(k=2)
#    t.add_word("hi")  # Short word that ends quickly
    
#    gen = Generator(t)
    
#    result = gen.generate("h", 10)
#    assert result == "hi"  # Should stop at natural end, not continue to 10

def test_invalid_seed_returns_empty_or_seed():
    """
    TEST
    What: Generator handles seeds that don't exist in trie gracefully
    Why: User might provide seeds not in training data
    How: Try to generate from "zz" which doesn't exist, verify safe handling
    """
    t = Trie(k=2)
    t.add_word("hello")
    
    gen = Generator(t)
    
    result = gen.generate("zz", 10)
    # Should either return empty or just the seed
    assert result == "" or result == "zz"