# src/generator/generator_factory.py
# Build-and-run entry point for the name generator. Invokes the generator to produce example names (deterministic or stochastic).

from src.generator.generator import Generator
from src.generator.generator_experimental import GeneratorExperimental

def build(trie, n_suggestions=5, debug=False, temperature=1.0, 
          use_context_shifting=False, eos_threshold=0.4, max_shifts=3,
          training_data=None,
          enable_trim=False):
    """Build generator with configuration
    
    Args:
        trie: The trie data structure
        n_suggestions: Number of suggestions to generate
        debug: Enable debug output
        temperature: Temperature for experimental generator (ignored in base)
        use_context_shifting: Enable context shifting (triggers experimental generator)
        eos_threshold: EOS threshold for experimental generator
        max_shifts: Max shifts for experimental generator
        training_data: Training data for duplicate filtering 
    
    Returns: 
        Generator (base) or GeneratorExperimental depending on flags.
        Experimental mode is on if temperature != 1.0 OR use_context_shifting is True.
    """
    # Use experimental generator if any experimental features are enabled
    if temperature != 1.0 or use_context_shifting:
        gen = GeneratorExperimental(
            trie, 
            debug=debug, 
            temperature=temperature,
            use_context_shifting=use_context_shifting,
            eos_threshold=eos_threshold,
            max_shifts=max_shifts,
            training_data=training_data,
            enable_trim=enable_trim
        )
    else:
        # Use base generator (with training data for duplicate filtering)
        gen = Generator(trie, debug=debug, training_data=training_data, enable_trim=enable_trim)
    
    gen.n_suggestions = n_suggestions 
    return gen