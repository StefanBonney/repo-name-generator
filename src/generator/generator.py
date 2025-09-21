# src/generator/generator.py
# generator: samples next characters from trie.next_char_counts (deterministic or stochastic) to produce repo names.

import random
from typing import Optional, Dict
from src.trie.trie import Trie
from src.utils.generator_debug import print_generation_summary
import time
from datetime import datetime

class Generator:
    def __init__(self, trie: Trie, debug: bool = False):
        self.trie = trie
        self.k = trie.get_k()
        self.debug = debug 
    
    def find_node(self, context: str):
        """Navigate trie to find node for given k-gram context
        
        Used by generate() with context = result[-k:].
        Example (k=2, result="hello"):
            context = "lo"
            Walk: root -> 'l' -> 'o' (if any step missing, return None).
        The returned node’s .get_next_counts() gives frequencies of next chars after `context`.
        """
        current_node = self.trie.get_root()
        for char in context:
            children = current_node.get_children()
            current_node = children.get(char)
            if current_node is None:        
                return None
        return current_node
    
    def weighted_random_choice(self, next_counts: Dict[str, int]) -> str:
        """Pick a character weighted by frequency"""
        if not next_counts:
            return None
        
        # Build cumulative weights
        chars = list(next_counts.keys())
        weights = list(next_counts.values())
        total = sum(weights)
        
        # Random number from 1 to total
        r = random.randint(1, total)
        
        # Find which character this maps to
        cumsum = 0
        for char, count in next_counts.items():
            cumsum += count
            if r <= cumsum:
                return char
        
        return chars[-1]  # safety fallback
    
    def generate(self, seed: str = "", max_length: int = 10) -> str:
        """Generate a single name - simplest version

        Loop:
            1) context = result[-k:]  (sliding window; if len(result) < k, use result)
            2) node = find_node(context)        # walk root -> chars in context; None stops
            3) next_counts = node.get_next_counts()
               e.g., after "lo": {'g': 12, 'c': 7, ...}
            4) next_char = weighted_random_choice(next_counts)
               (prob. ∝ counts). If next_char == EOS, stop.
            5) result += next_char and repeat until len(result) == max_length or no continuation.
        
        Note: Currently requires seed of at least k characters to work properly.
        Empty/short(less than k) seeds will return empty/short results.
        """
        result = seed
        path_log = []
        
        # Generate until we hit max_length or EOS
        while len(result) < max_length:
            # Get context (last k chars)
            if len(result) >= self.k:
                context = result[-self.k:]
            else:
                context = result  # Use what we have
            
            # Find the node for this context
            node = self.find_node(context)
            if node is None:
                break  # Can't continue from this context
            
            # Get possible next characters
            next_counts = node.get_next_counts()
            if not next_counts:
                break  # No continuation possible
            
            # Pick next character
            next_char = self.weighted_random_choice(next_counts)

            if self.debug:
                path_log.append({"context": context, "chosen_char": next_char})
            
            # Check for end of sequence
            if next_char == self.trie.EOS:
                break
            
            result += next_char
        
        return (result, path_log) if self.debug else result

    def generate_batch(self, seed: str, max_length: int, n: int = 5, process_start_time: float = None, data_size: int = 0) -> list:
        """Generate multiple name candidates
        
        Args:
            seed: Starting text.
            max_length: Max length per sample.
            n: Number of samples to generate.
            process_start_time: If provided, used to compute/print elapsed time.
            data_size: Training corpus size (for debug reporting).

        Returns:
            List[str]: n generated names.

        Notes:
            - Internally calls generate() n times (sliding k-gram context).
            - If debug=True:
                * collects per-sample paths (context → chosen_char),
                * prints a summary (uniques, avg length, etc.),
                * saves a JSON log with samples, analysis, and paths.
        """
        results = []
        paths = []

        for _ in range(n):
            if self.debug:
                name, path_log = self.generate(seed, max_length)
                results.append(name)
                paths.append(path_log)
            else:
                name = self.generate(seed, max_length)            # string when debug=False
                results.append(name)

        total_time = time.time() - process_start_time 
        
        # Debug output if enabled
        if self.debug:
            # single call handles console + JSON logging
            print_generation_summary(
                self.k,
                seed,
                max_length,
                results,
                n_requested=n,
                log_prefix="generator_debug",
                generation_time=total_time,
                data_size=data_size,
                paths=paths
            )
        return results
    
    