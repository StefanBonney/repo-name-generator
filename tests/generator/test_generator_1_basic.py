# tests/generator/test_generator_1_basic.py
# Simple unit tests for basic Generator functionality. Focus: Individual methods work correctly with small inputs.

import random
#from pathlib import Path
from src.trie.trie import Trie
from src.generator.generator import Generator
from src.generator_factory import build as build_gen
from src.trie_factory import build as build_trie

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
    # With current base generator, we return the seed when no path exists
    assert result == "zz"

def test_generate_stops_immediately_when_context_unseen():
    """
    TEST
    What: Base generator stops when the seed context isn't in the trie
    Why: Users may provide unseen/short seeds; generator must fail safe without crashing
    How: Build a trie without 'zz' context, call generate('zz', 10), and
         verify the result is unchanged seed 
    """
    t = Trie(k=2)
    for w in ["hello", "help", "helm"]:
        t.add_word(w)

    g = Generator(t)
    out = g.generate(seed="zz", max_length=10)

    assert out in {"zz"}


def test_batch_dedup_respects_max_attempts_and_returns_empty():
    """
    TEST
    What: Batch generation filters out training-set duplicates and exits via max-attempts when only duplicates are possible
    Why: Prevents leaking training items and infinite loops
    How: Trie with only 'ab' (k=1). Generator has training_data=['ab'].
         Request 3 names from seed 'a' and max_length=2 → generator can only make 'ab',
         which is filtered every time → returns [] after hitting max_attempts.
    """
    t = Trie(k=1)
    t.add_word("ab")  # only possible outcome

    gen = Generator(t, training_data=["ab"]) 

    out = gen.generate_batch(seed="a", max_length=2, n=3)
    assert out == []

def test_batch_uniqueness_limits_duplicates():
    """
    TEST
    What: Batch generation keeps outputs unique and stops after max-attempts if only one name is possible
    Why: Covers the batch de-dup branch (within-batch uniqueness) and max-attempts exit
    How: Trie(k=1) only allows 'aa'. Ask for n=3 -> only 'aa' can be produced repeatedly,
         so result should contain it once (or at most once) and then stop.
    """
    t = Trie(k=1)
    t.add_word("aa")  # the only producible name

    gen = Generator(t)
    out = gen.generate_batch(seed="a", max_length=2, n=3)

    assert "aa" in out
    assert len(set(out)) == 1          # unique within batch
    assert len(out) == 1               # couldn't fill n=3 because only one unique exists

def test_seed_with_slash_returns_seed_unchanged():
    """
    TEST
    What: Seed containing '/' cannot be continued because training data is sanitized
    Why: We strip '.' and '/' when building the trie, so contexts with these chars don't exist
    How: Build trie via factory, then call generator with seed 'cli/' and expect the result is unchanged
    """
    # factory strips '.' and '/' from training; trie has no slash transitions
    t = build_trie(["client/lib.", "clientlib"], k=2, use_eos=False)

    gen = build_gen(t, temperature=1.0)  # base generator
    out = gen.generate(seed="cli/", max_length=10)

    assert out == "cli/"  # cannot advance; returns the seed as-is