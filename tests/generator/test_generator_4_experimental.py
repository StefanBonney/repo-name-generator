# tests/generator/test_generator_4_experimental.py
# Experimental generator checks: factory routing and duplicate filtering.

#import random
from src.trie.trie_eos import TrieEOS
from src.generator.generator_experimental import GeneratorExperimental
from src.generator_factory import build

def test_factory_chooses_experimental_when_flags():
    """
    TEST
    What: Factory returns experimental generator when experimental flags are set
    Why: Ensure correct routing between base and experimental implementations
    How: Build with temperature!=1.0 and with use_context_shifting=True; both should produce GeneratorExperimental
    """
    t = TrieEOS(k=2)
    t.add_word("hello")

    # all other parameters default
    gen_temp = build(t, temperature=1.2)
    assert isinstance(gen_temp, GeneratorExperimental)

    gen_ctx = build(t, use_context_shifting=True)
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

    gen = GeneratorExperimental(t, training_data=["hi"], temperature=1.0, use_context_shifting=False)
    batch = gen.generate_batch(seed="hi", max_length=10, n=3)

    assert batch == [] # only possible output ('hi') was filtered out



#def test_generation_stops_at_eos_marker():
#    """
#    TEST
#    What: Generator stops when encountering EOS even if max_length not reached
#    Why: Natural word endings should be respected over arbitrary length
#    How: Generate from "h" with max_length=10, verify stops at "hi" due to EOS
#    """
#    t = Trie(k=2)
#    t.add_word("hi")  # Short word that ends quickly
    
#    gen = Generator(t)
    
#    result = gen.generate("h", 10)
#    assert result == "hi"  # Should stop at natural end, not continue to 10