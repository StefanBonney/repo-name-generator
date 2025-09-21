# src/generator/build_generator.py
# Build-and-run entry point for the name generator. Invokes the generator to produce example names (deterministic or stochastic).


# Could add strategy selection, random seed setting, temperature parameters

from src.generator.generator import Generator

def build(trie, n_suggestions=5, debug=False):
    """Build generator with configuration"""
    gen = Generator(trie, debug=debug)
    gen.n_suggestions = n_suggestions 
    return gen