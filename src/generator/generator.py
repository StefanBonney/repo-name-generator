# src/generator/generator.py
# generator: samples next characters from trie.next_char_counts to produce repo names.

import random
from typing import Optional, Dict
from src.trie.trie import Trie
from src.utils.generator_debug_v2 import print_generation_summary
import time
from src.utils.generator_trim import trim_to_token

#===============================================================
# Generator class: uses a Trie to generate names based on k-gram contexts   
#===============================================================
class Generator:
    def __init__(self, trie: Trie, debug: bool = False, training_data=None, enable_trim: bool = False):
        self.trie = trie
        self.k = trie.get_k()
        self.debug = debug
        self.training_set = set(training_data) if training_data else set() # For filtering exact copies (case-sensitive, to match base)
        self.enable_trim = enable_trim

    #*******************************************************[find_node]
    def find_node(self, context: str):
        """Navigate trie to find node for given k-gram context
        
        Used by generate() with context = result[-k:].
        Example (k=2, result="hello"):
            context = "lo"
            Walk: root -> 'l' -> 'o' (if any step missing, return None).
        The returned node's .get_next_counts() gives frequencies of next chars after context.
        """
        current_node = self.trie.get_root()
        for char in context:
            children = current_node.get_children()
            current_node = children.get(char)
            if current_node is None:        
                return None
        return current_node
    
    #*******************************************************[weighted_random_choice]
    def weighted_random_choice(self, next_counts: Dict[str, int]) -> str:
        """Pick a character weighted by frequency - base version without temperature"""
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

    #*******************************************************[generate]
    def generate(self, seed: str = "", max_length: int = 10) -> str:
        """Generate a single name - base version without EOS handling

        Loop:
            1) context = result[-k:]  (sliding window; if len(result) < k, use result)
            2) node = find_node(context)        # walk root -> chars in context; None stops
            3) next_counts = node.get_next_counts()
               e.g., after "lo": {'g': 12, 'c': 7, ...}
            4) next_char = weighted_random_choice(next_counts)
               (prob. ∝ counts). Continue until max_length reached.
            5) result += next_char and repeat until len(result) == max_length or no continuation.
        
        Note: Currently requires seed of at least k characters to work properly.
        Empty/short(less than k) seeds will return empty/short results.
        """
        result = seed
        path_log = []
        
        # Generate until we hit max_length
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
            
            # Check for EOS if we're using an EOS trie
            if hasattr(self.trie, 'EOS') and next_char == self.trie.EOS:
                break  # Stop generation at EOS
    
            # Otherwise continue adding characters
            result += next_char
        
        return (result, path_log) if self.debug else result

    #*******************************************************[generate_batch]
    def generate_batch(self, seed: str, max_length: int, n: int = 5, process_start_time: float = None, data_size: int = 0) -> list:
        """Generate multiple name candidates with duplicate filtering
        
        Args:
            seed: Starting text.
            max_length: Max length per sample.
            n: Number of samples to generate.
            process_start_time: If provided, used to compute/print elapsed time.
            data_size: Training corpus size (for debug reporting).

        Returns:
            List[str]: n generated names (no duplicates from training data).

        Notes:
            - Filters out exact matches with training data
            - Prevents duplicate results in the batch
            - Internally calls generate() up to n*10 times to handle filtering
            - If debug=True:
                * collects per-sample paths (context → chosen_char),
                * prints a summary (uniques, avg length, etc.),
                * saves a JSON log with samples, analysis, and paths.
        """
        results = []
        paths = []
        attempts = 0
        max_attempts = n * 10  # Prevent infinite loop

        while len(results) < n and attempts < max_attempts:
            if self.debug:
                name, path_log = self.generate(seed, max_length)
            else:
                name = self.generate(seed, max_length)
                path_log = None
            
            # Optionally trim the name to a token boundary
            if self.enable_trim and name:
                name = trim_to_token(name)
            
            # Filter out training data duplicates and already generated names
            if name and name not in self.training_set and name not in results:
                results.append(name)
                if self.debug:
                    paths.append(path_log)
            
            attempts += 1

        total_time = time.time() - process_start_time if process_start_time else 0
        
        # Debug output if enabled
        if self.debug:
            config = {
                "generator_type": "base",
                "use_eos": False,
                "temperature": 1.0,
                "use_context_shifting": False,
                "enable_trim": self.enable_trim
            }
            print_generation_summary(
                self.k,
                seed,
                max_length,
                results,
                n_requested=n,
                log_prefix="generator_debug",
                generation_time=total_time,
                data_size=data_size,
                paths=paths,
                config=config
            )
        return results