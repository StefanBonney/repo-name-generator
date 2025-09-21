# tests/test_generator_realistic.py
# Tests with representative repository name data. Focus: Algorithm works with actual envisioned project data patterns and outputs.

import random
from pathlib import Path
from src.trie.trie import Trie
from src.generator.generator import Generator
import re


def test_generator_produces_repo_like_patterns(repo_root):
    """Test that generated names follow repository naming patterns"""
    t = Trie(k=2)
    
    # Load 2000 names to get good patterns
    data_path = repo_root / "data" / "training_data.txt"
    training_words = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 2000:
                break
            word = line.strip()
            if word:
                t.add_word(word)
                training_words.append(word)
    
    gen = Generator(t)
    
    # Generate many samples
    generated = []
    for i in range(50):
        random.seed(i)
        # Try different seeds
        seeds = ["re", "py", "js", "web", "api", "cli"]
        seed = seeds[i % len(seeds)]
        result = gen.generate(seed, 15)
        if result and len(result) > 3:
            generated.append(result)
    
    # Pattern checks
    # 1. Should have some with hyphens (common in repos)
    with_hyphens = [g for g in generated if '-' in g]
    assert len(with_hyphens) > 0, "No hyphenated names generated (unusual for repo names)"
    
    # 2. Should have mix of lengths
    lengths = set(len(g) for g in generated)
    assert len(lengths) > 3, "All generated names are same length (unrealistic)"
    
    # 3. Should not all be exact copies from training
    exact_copies = [g for g in generated if g in training_words]
    assert len(exact_copies) < len(generated), "Only generating exact copies, no new combinations"

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