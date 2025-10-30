# src/generator/generator_experimental.py
# generator_experimental: samples next characters from trie_eos.next_char_counts with temperature scaling and optional EOS continuation search to produce repo names.

import random
from typing import Optional, Iterable, Set, Dict
#from collections import defaultdict 
from src.trie.trie_eos import TrieEOS
from src.utils.debug.generator_debug_v2 import print_generation_summary
import time
#from datetime import datetime
from src.utils.generator_trim_v1 import trim_to_token as trim_v1
from src.utils.generator_trim_v2 import trim_to_token as trim_v2

#===============================================================
# Generator class: uses a Trie to generate names based on k-gram contexts   
#===============================================================
class GeneratorExperimental:
    def __init__(self, trie: TrieEOS, debug: bool = False, temperature: float = 1.0,
                use_eos_continuation_search: bool = False,
                max_continuation_attempts: int = 3,
                training_data: Optional[Iterable[str]] = None,
                enable_trim_v1: bool = False,
                enable_trim_v2: bool = False):
        
        self.trie = trie
        self.k = trie.get_k()
        self.debug = debug 
        self.temperature = temperature
        # EOS continuation search
        self.use_eos_continuation_search = use_eos_continuation_search
        self.max_continuation_attempts = max_continuation_attempts
        # For filtering exact copies (case-sensitive, to match base)
        self.training_set = set(training_data) if training_data else set()
        # trimming
        self.enable_trim_v1 = enable_trim_v1
        self.enable_trim_v2 = enable_trim_v2

    #-------------------------------------------------------<find_node>
    def find_node(self, context: str):
        """
        Navigate trie to find node for given k-gram context
        
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

    #-------------------------------------------------------<weighted_random_choice>    
    def weighted_random_choice(self, next_counts: Dict[str, int]) -> str:
        """
        Sample a next character from frequency counts with temperature scaling.

        - T = 1.0: probabilities ∝ counts (baseline).
        - T < 1.0: sharpens (more deterministic; peaks amplified).
        - T > 1.0: flattens (more random; tails boosted)

        Returns None if no candidates.
        """
        if not next_counts: # empty dict or no next characters available
            return None     # skip this
        
        # Apply temperature scaling

        chars = list(next_counts.keys())     # chars = ['a', 'b', 'c']
        counts = list(next_counts.values())  # counts = [8, 4, 1]
        
        # Apply temperature (lower = more deterministic, higher = more random)
        # e.g. temperature = 1.5, more random
        if self.temperature > 0:
            import math
            # For each count: math.pow(count, 1/temperature)
            # 1/1.5 = 0.667 => math.pow(count, 0.667)
            # [math.pow(8, 0.667), math.pow(4, 0.667), math.pow(1, 0.667)] => raises counts to power 1/T [4.76, 2.52, 0.667]
            scaled_counts = [math.pow(c, 1/self.temperature) for c in counts] 
        else:
            # Handle temperature = 0 
            # deterministic, picks the most frequent
            # avoids divide-by-zero; gives a predictable “greedy” mode for repeatable outputs
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

    #-------------------------------------------------------<generate>
    def generate(self, seed: str = "", max_length: int = 10) -> str:
        """
        Generate a single name - with eos handling and optional continuation search

        Loop:
            1) context = result[-k:]  (if len(result) < k, use whole result)
            2) node = find_node(context); if missing or has no next_counts → stop
            3) next_counts = node.get_next_counts()
            4) next_char = weighted_random_choice(next_counts)  (prob ∝ counts)

             If next_char == EOS:
                - If continuation_search is enabled AND len(result) < 0.7 * max_length
                  AND shifts_used < max_continuation_attempts:
                    • exclude EOS and retry once (counts without EOS)
                    • increment shifts_used
                    • continue the loop without appending EOS
                - Else: accept EOS → stop
             Else:
                - append next_char to result

            5) repeat until len(result) == max_length or no continuation is possible
        
        Note: Currently requires seed of at least k characters to work properly.
        Empty/short(less than k) seeds will return empty/short results.
        """
        result = seed
        path_log = []
        shifts_used = 0 

        # Generate until we hit max_length or accept EOS
        while len(result) < max_length:
            # CONTEXT
            # Get context (last k chars)
            if len(result) >= self.k:
                context = result[-self.k:]
            else:
                context = result  # use what we have

            # NODE
            # Find the node for this context
            node = self.find_node(context)
            if node is None:
                break  # can't continue from this context
            
            # NEXT
            # Get possible next characters
            next_counts = node.get_next_counts()
            if not next_counts:
                break  # no continuation possible
            
            # Pick next character
            next_char = self.weighted_random_choice(next_counts)

            # EOS HANDLING
            # Check for EOS - with continuation on, if too short, try picking alternative
            if next_char == self.trie.EOS:
                min_acceptable_length = max_length * 0.7 # NOTE: hardcoded 70% threshold

                if (self.use_eos_continuation_search and 
                    len(result) < min_acceptable_length and 
                    shifts_used < self.max_continuation_attempts):

                    shifts_used += 1

                    if self.debug:
                        print(f"\nEOS Continuation Search (attempt {shifts_used}/{self.max_continuation_attempts})")
                        print(f"   Current: '{result}' (length {len(result)}, target {max_length})")
                        print(f"   Context: '{context}' → hit EOS (natural word ending)")
                        print(f"   Action: Removing EOS and picking alternative...")

                    # Remove EOS and pick again
                    next_counts_no_eos = {k: v for k, v in next_counts.items() if k != self.trie.EOS}

                    if next_counts_no_eos:
                        next_char = self.weighted_random_choice(next_counts_no_eos)
                        if self.debug:
                            print(f"   ✓ Success: continuing with '{next_char}'")
                    else:
                        # Only EOS available, must stop
                        break  
                else:
                    # Accept EOS
                    break

            # LOG PATH
            if self.debug:
                path_log.append({"context": context, "chosen_char": next_char})
                
            result += next_char

        # Track if continuation search was used
        continuation_used = shifts_used > 0

        # RETURN RESULT
        if self.debug:
            return (result, path_log, continuation_used)
        else:
            return result

    #-------------------------------------------------------<generate_batch>
    def generate_batch(self, seed: str, max_length: int, n: int = 5, process_start_time: float = None, data_size: int = 0) -> list:
        """
        Generate multiple name candidates with duplicate filtering
        
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
                • collects per-sample paths (context → chosen_char),
                • prints a summary (uniques, avg length, etc.),
                • saves a JSON log with samples, analysis, and paths.
        """
        results = []
        paths = []
        continuation_flags = []  # Track which names used continuation search
        attempts = 0
        max_attempts = n * 10  # Prevent infinite loop

        while len(results) < n and attempts < max_attempts:
            if self.debug:
                name, path_log, used_continuation = self.generate(seed, max_length)
            else:
                name = self.generate(seed, max_length)
                path_log = None
                used_continuation = False

            # Optionally trim the name to a token boundary
            if self.enable_trim_v2 and name:
                name = trim_v2(name, max_length=max_length)
            elif self.enable_trim_v1 and name:
                name = trim_v1(name, max_length=max_length)
            
            # Filter out training data duplicates and already generated names
            if name and name not in self.training_set and name not in results:
                results.append(name)
                continuation_flags.append(used_continuation)
                if self.debug:
                    paths.append(path_log)
            
            attempts += 1

        total_time = time.time() - process_start_time if process_start_time else 0
        
        # Debug output if enabled
        if self.debug:
            config = {
                "generator_type": "experimental",
                "use_eos": True,
                "temperature": self.temperature,
                "use_eos_continuation_search": self.use_eos_continuation_search,
                "enable_trim_v1": self.enable_trim_v1,
                "enable_trim_v2": self.enable_trim_v2,
                "max_continuation_attempts": self.max_continuation_attempts
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
        
        # Store flags for external access
        self._last_continuation_flags = continuation_flags
        
        return results