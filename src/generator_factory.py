# src/generator/generator_factory.py
# Build-and-run entry point for the name generator. Invokes the generator to produce example names (deterministic or stochastic).

from src.generator.generator import Generator
from src.generator.generator_experimental import GeneratorExperimental

def _sanitize(w: str) -> str:
    return w.replace(".", "").replace("/", "")

def build(trie, n_suggestions=5, debug=False, temperature=1.0, 
          use_eos_continuation_search=False, eos_threshold=0.4, max_continuation_attempts=3,
          training_data=None,
          enable_trim_v1=False, enable_trim_v2=False):
    """Build generator with configuration
    
    Args:
        trie: The trie data structure
        n_suggestions: Number of suggestions to generate
        debug: Enable debug output
        temperature: Temperature for experimental generator (ignored in base)
        use_eos_continuation_search: Enable EOS continuation search (triggers experimental generator)
        eos_threshold: EOS threshold for experimental generator
        max_continuation_attempts: Maximum continuation attempts for experimental generator
        training_data: Training data for duplicate filtering
        enable_trim_v1: Enable original trim algorithm
        enable_trim_v2: Enable morphologically-aware trim algorithm
    
    Returns: 
        Generator (base) or GeneratorExperimental depending on flags.
        Experimental mode is on if temperature != 1.0 OR use_eos_continuation_search is True.
    """
    if training_data is not None:
        training_data = [
            s for s in (_sanitize(w.strip()) for w in training_data if w)
            if s  # skip entries that become empty after sanitize
        ]

    # Use experimental generator if any experimental features are enabled (with training data for duplicate filtering)
    if temperature != 1.0 or use_eos_continuation_search:
        gen = GeneratorExperimental(
            trie, 
            debug=debug, 
            temperature=temperature,
            use_eos_continuation_search=use_eos_continuation_search,
            eos_threshold=eos_threshold,
            max_continuation_attempts=max_continuation_attempts,
            training_data=training_data,
            enable_trim_v1=enable_trim_v1,
            enable_trim_v2=enable_trim_v2
        )
    else:
        # Use base generator (with training data for duplicate filtering)
        gen = Generator(trie, debug=debug, training_data=training_data, 
                       enable_trim_v1=enable_trim_v1, enable_trim_v2=enable_trim_v2)
    
    gen.n_suggestions = n_suggestions 
    return gen