# tests/generator/test_generator_4_experimental.py
# Experimental generator checks: factory routing and duplicate filtering.

import random
from src.trie.trie_eos import TrieEOS
from src.generator.generator_experimental import GeneratorExperimental
from src.generator_factory import build

def test_factory_chooses_experimental_when_flags():
    """
    TEST
    What: Factory returns experimental generator when experimental flags are set
    Why: Ensure correct routing between base and experimental implementations
    How: Build with temperature!=1.0 and with use_eos_continuation_search=True; both should produce GeneratorExperimental
    """
    t = TrieEOS(k=2)
    t.add_word("hello")

    # all other parameters default
    gen_temp = build(t, temperature=1.2)
    assert isinstance(gen_temp, GeneratorExperimental)

    gen_ctx = build(t, use_eos_continuation_search=True)
    assert isinstance(gen_ctx, GeneratorExperimental)


def test_experimental_filters_exact_training_copies():
    """
    TEST
    What: Experimental generator's batch filtering removes exact copies through rejection from training data
    Why: Parity with base generator's duplicate-avoidance
    How: Train with a tiny corpus that would otherwise generate an exact copy; ensure it is filtered out of the batch
    """
    t = TrieEOS(k=2)
    t.add_word("hi")  # minimal word; EOS edge present in TrieEOS

    gen = GeneratorExperimental(t, training_data=["hi"], temperature=1.0, use_eos_continuation_search=False)
    batch = gen.generate_batch(seed="hi", max_length=10, n=3)

    assert batch == [] # only possible output ('hi') was filtered out


def test_low_temperature_forces_most_probable_choice():
    """
    TEST
    What: Very low temperature should bias toward the most probable next char
    Why: Validate temperature scaling path in ExperimentalGenerator
    How: With 'ab'->{c:9,d:1}, temp≈0 → generate many names and check 3rd char (~90% 'c')
    """
    random.seed(1337)  # determinism

    t = TrieEOS(k=2)
    for _ in range(9): t.add_word("abc")
    t.add_word("abd")

    gen = GeneratorExperimental(t, training_data=["abc","abd"], temperature=0.01, use_eos_continuation_search=False)

    samples = [gen.generate(seed="ab", max_length=3) for _ in range(200)]  # enough samples
    thirds  = [s[2] for s in samples if len(s) >= 3]

    c = thirds.count("c"); d = thirds.count("d")
    ratio = c / len(thirds)

    # Robust assertions
    assert set(thirds) <= {"c","d"}
    assert ratio >= 0.80          #  probability band, avoids flakiness
    assert c > d                  # sanity: c is strictly the majority
