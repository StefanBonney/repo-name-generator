# src/generator/generator_experimental.py
# generator: samples next characters from trie.next_char_counts (deterministic or stochastic) to produce repo names.

import random
from typing import Optional, Iterable, Set, Dict
#from collections import defaultdict 
from src.trie.trie_eos import TrieEOS
from src.utils.generator_debug_v2 import print_generation_summary
import time
#from datetime import datetime
from src.utils.generator_trim import trim_to_token

#===============================================================
# Generator class: uses a Trie to generate names based on k-gram contexts   
#===============================================================
class GeneratorExperimental:
    def __init__(self, trie: TrieEOS, debug: bool = False, temperature: float = 1.0,
                use_context_shifting: bool = False, 
                eos_threshold: float = 0.4, 
                max_shifts: int = 3,
                training_data: Optional[Iterable[str]] = None,
                enable_trim: bool = False):
        
        self.trie = trie
        self.k = trie.get_k()
        self.debug = debug 
        self.temperature = temperature
        #---------------
        # context-shifting
        self.use_context_shifting = use_context_shifting
        self.eos_threshold = eos_threshold
        self.max_shifts = max_shifts
        # For filtering exact copies (case-sensitive, to match base)
        self.training_set = set(training_data) if training_data else set()
        # trimming
        self.enable_trim = enable_trim


    #*******************************************************[find_node]
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
    
    #*******************************************************[find_alternative_context]
    def find_alternative_context(self, context):
        """Try incrementing last character: 'erk' -> 'erl', 'erm', ... 'erz'"""
        if not context:
            return None
        
        last_char = context[-1]
    
        # Try next letters after the last character
        for ascii_val in range(ord(last_char) + 1, ord('z') + 1):
            candidate = context[:-1] + chr(ascii_val)
            node = self.find_node(candidate)
            if node and node.get_next_counts():
                return candidate
            
        return None  # Nothing found, continue with original context
    
    #*******************************************************[weighted_random_choice]
    def weighted_random_choice(self, next_counts: Dict[str, int]) -> str:
        """Pick a character weighted by frequency"""
        if not next_counts: # empty dict or no next characters available
            return None     # skip this
        
        #--------------------------------------------------
        # Apply temperature scaling

        chars = list(next_counts.keys())     # chars = ['a', 'b', 'c']
        counts = list(next_counts.values())  # counts = [8, 4, 1]
        
        # Apply temperature (lower = more deterministic, higher = more random)
        # e.g. temperature = 1.5, more random
        if self.temperature > 0:
            import math
            # For each count: math.pow(count, 1/temperature)
            # 1/1.5 = 0.667 = math.pow(count, 0.667)
            # [math.pow(8, 0.667), math.pow(4, 0.667), math.pow(1, 0.667)] = squares each count [4.76, 2.52, 0.667]
            scaled_counts = [math.pow(c, 1/self.temperature) for c in counts] 
        else:
            # Handle temperature = 0 (deterministic)
            max_count = max(counts)
            scaled_counts = [1 if c == max_count else 0 for c in counts]
        
        # Create weighted selection based on scaled counts
        total = sum(scaled_counts) # 4.76 + 2.52 + 1.0 = 8.28
        if total == 0:
            return chars[0]
            
        r = random.random() * total # e.g. r = 6.1 (random between 0-8.28)
        cumsum = 0
        # Loop through chars and scaled_counts together:
        # First iteration: char='a', scaled_count=4.76
        for char, scaled_count in zip(chars, scaled_counts):
            cumsum += scaled_count # cumsum = 0 + 4.76 = 4.76
            if r <= cumsum:        # 6.1 <= 4.76, NO
            # Second iteration: char='b', scaled_count=2.52  
            # cumsum += scaled_count  # cumsum = 4.76 + 2.52 = 7.28
            # if r <= cumsum:         # 6.1 <= 7.28, YES        
                return char           # return 'b'
        return chars[-1]

    #*******************************************************[generate]
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
        shifts_used = 0 
        
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

            if (self.use_context_shifting and 
                len(result) > len(seed) and 
                shifts_used < self.max_shifts):
    
                total_counts = sum(next_counts.values())
                eos_probability = next_counts.get(self.trie.EOS, 0) / total_counts if total_counts > 0 else 0
    
                if eos_probability > self.eos_threshold:
                    alternative = self.find_alternative_context(context)
                    if alternative:
                        result = result[:-self.k] + alternative
                        shifts_used += 1
                        if self.debug:
                            print(f"Context shift: '{context}' -> '{alternative}' (EOS: {eos_probability:.2f})")
                        continue
            
            # Pick next character
            next_char = self.weighted_random_choice(next_counts)

            if self.debug:
                path_log.append({"context": context, "chosen_char": next_char})
            
            # Check for end of sequence
            if next_char == self.trie.EOS:
                break
            
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
        if self.debug:
            config = {
                "generator_type": "experimental",
                "use_eos": True,
                "temperature": self.temperature,
                "use_context_shifting": self.use_context_shifting,
                "enable_trim": self.enable_trim,
                "eos_threshold": self.eos_threshold,
                "max_shifts": self.max_shifts
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