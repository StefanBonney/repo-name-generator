# tests/generator/test_generator_3_quality.py
# Quality checks with representative repo-like data.
# Focus: novelty vs training set, and repo-style patterns.

import random
from src.trie.trie import Trie
from src.generator.generator import Generator
import re


def test_generator_creates_plausible_combinations(repo_root):
    """Test that generator combines learned patterns in new ways"""
    t = Trie(k=3)
    
    # Load data with clear patterns
    data_path = repo_root / "data" / "training_data.txt" 
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1000:
                break
            word = line.strip()
            if len(word) >= 3:  # Need at least k chars
                t.add_word(word)
    
    gen = Generator(t)
    random.seed(42)
    
    # Generate from "web" - common in repo names
    web_names = [gen.generate("web", 12) for _ in range(10)]
    web_names = [w for w in web_names if w]  # Remove empty
    
    # Should create variations
    assert len(set(web_names)) > 1, "All 'web' generations identical"
    
    # Check for common repo patterns using regex
    # Pattern: word-word or word_word format
    separator_pattern = re.compile(r'^[a-z0-9]+[-_][a-z0-9]+')
    has_separator_pattern = any(separator_pattern.match(w) for w in web_names)
    
    # Not required but likely given repo naming conventions
    if len(web_names) > 5:
        assert has_separator_pattern, "No typical word-word patterns found"

def test_generator_handles_special_repo_patterns(repo_root):
    """Test generation with special repository naming patterns"""
    t = Trie(k=2)
    
    # Load subset
    data_path = repo_root / "data" / "training_data.txt"
    special_pattern_names = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 1500:
                break
            word = line.strip()
            if word:
                t.add_word(word)
                # Track special patterns
                if any(c in word for c in ['-', '_', '.', '@']):
                    special_pattern_names.append(word)
    
    gen = Generator(t)
    
    # If we found special patterns in training data
    if special_pattern_names:
        # Generate and check if special characters appear
        generated_with_special = []
        for i in range(20):
            random.seed(100 + i)
            # Use seeds from actual special pattern names
            if special_pattern_names:
                seed = special_pattern_names[i % len(special_pattern_names)][:2]
                result = gen.generate(seed, 12)
                if any(c in result for c in ['-', '_', '.', '@']):
                    generated_with_special.append(result)
        
        # Should generate some names with special characters
        assert len(generated_with_special) > 0, "Never generates special chars despite training data having them"


def test_generated_names_are_novel(repo_root):
    """
    TEST
    What: Generated names aren't exact copies from training data
    Why: Quality requirement—novel combinations, not memorization
    How: Train on a large real dataset; generate a small batch; assert no exact copies and some variety
    """
    t = Trie(k=3)

    # Load a decent slice of the corpus
    data_path = repo_root / "data" / "training_data.txt"
    training_words = []
    with open(data_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)
                training_words.append(w)

    gen = Generator(t, training_data=training_words)

    # Make global RNG deterministic so this test is reproducible
    random.seed(123)
    seeds = ["rea", "web", "typ", "cli", "api", "dat"]
    generated = []
    # modest oversampling via multiple seeds
    for s in seeds:
        for _ in range(5):
            name = gen.generate(s, max_length=16)
            if name:
                generated.append(name)

    training_set = set(training_words)
    assert all(g not in training_set for g in generated), "Found exact copies from training data"
    assert len(set(generated)) >= 3, "Expected at least 3 unique outputs"

def test_hyphenated_repo_style_patterns_present(repo_root):
    """
    TEST
    What: Generator produces some hyphenated outputs (common in repo names)
    Why: Reflect typical naming conventions (word-word)
    How: Train on real data; generate several names; expect at least one hyphenated
    """
    t = Trie(k=3)

    data_path = repo_root / "data" / "training_data.txt"
    with open(data_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)

    gen = Generator(t)

    random.seed(321)
    seeds = ["rea", "web", "typ", "cli", "api", "dat"]
    outputs = []
    for s in seeds:
        for _ in range(6):
            n = gen.generate(s, max_length=16)
            if n:
                outputs.append(n)

    assert any("-" in o for o in outputs), "No hyphenated names produced"


def test_diversity_and_similarity(repo_root):
    """
    TEST
    What: Outputs are not near-copies yet remain plausibly similar to training patterns
    Why: To see balance in novelty and learned structure 
    How: Train on real data; compute bigram Dice similarity of each output to its closest training word;
         assert all < 0.95 (no near-copies) and at least one >= 0.4 (moderate similarity).
    """
    def bigrams(s: str):
        s = "".join(ch for ch in s.lower() if ch.isalnum())
        return {s[i:i+2] for i in range(len(s)-1)} if len(s) >= 2 else set()

    def dice(a: set, b: set) -> float:
        if not a and not b:
            return 0.0
        return 2 * len(a & b) / (len(a) + len(b))

    # Train
    t = Trie(k=3)
    data_path = repo_root / "data" / "training_data.txt"
    training_words = []
    with open(data_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            w = line.strip()
            if len(w) >= 3:
                t.add_word(w)
                training_words.append(w)

    gen = Generator(t, training_data=training_words)

    random.seed(888) 
    seeds = ["rea", "web", "typ", "cli", "api", "dat"]
    outputs = []
    for s in seeds:
        for _ in range(6):
            n = gen.generate(s, max_length=16)
            if n:
                outputs.append(n)

    # Similarity vs nearest training word
    training_bigrams = [bigrams(w) for w in training_words]
    max_sims = []
    for o in outputs:
        ob = bigrams(o)
        if not ob:
            continue
        best = 0.0
        for tb in training_bigrams:
            if not tb:
                continue
            # Dice similarity
            inter = len(ob & tb)
            denom = len(ob) + len(tb)
            sim = 0.0 if denom == 0 else (2 * inter) / denom
            if sim > best:
                best = sim
        max_sims.append(best)

    # Diversity & similarity thresholds
    assert all(s < 0.95 for s in max_sims), "Found outputs too similar to training data"
    assert any(s >= 0.4 for s in max_sims), "No outputs show moderate similarity to training patterns"
