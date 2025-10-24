# src/ui/ui.py
# Handles user interaction and input/output. Also handles input validation.

class UI:
    def __init__(self, mode="basic"):
        self.mode = mode

    def _validate_int_input(self, prompt, default, rng=None, allow_all=False, positive=False):
        """
        Empty → default. If allow_all and user types 'all', return None.
        rng: (lo, hi) or None. If positive=True, value must be > 0.
        """
        while True:
            # if empty/special values
            s = input(prompt).strip()
            if s == "":
                return default                      # user pressed Enter → fall back to system default
            if allow_all and s.lower() == "all":    # user typed "all" → return None as meaning "use all" data
                return None
            # validate integer input, and prompt again if invalid
            try:
                v = int(s)
                if positive and v <= 0:
                    print("Enter a positive integer or leave empty."); continue
                if rng:
                    lo, hi = rng
                    if v < lo or v > hi:
                        print(f"Enter a value in [{lo}–{hi}] or leave empty."); continue
                return v
            except ValueError:
                print("Enter an integer or leave empty.")

    def get_user_input(self, experimental_mode: bool = False):
        """
        Get user input for parameters
        """
        print("\nNEW USER INPUT")
        print()
        print("(Press Enter to accept default values)")
        print() 
        # input
        seed = input("Starting letters (or 'quit' to exit): ").strip()
        if seed.lower() == "quit":
            raise SystemExit(0)
        # validated inputs
        length        = self._validate_int_input("Max length (default 10): ", 10, rng=(1, 50))  # rng=(lo, hi): inclusive bounds; input must be in [1, 50]
        k             = self._validate_int_input("Markov degree k (default 2): ", 2, rng=(2, 10))
        n_suggestions = self._validate_int_input("Number of suggestions (default 5): ", 5, rng=(1, 100))
        data_size     = self._validate_int_input("Training data size (default all, or number): ", None,
                                         allow_all=True, positive=True) # allow_all=True: accept "all" → return None (caller = use full dataset); positive=True: numeric input must be > 0
        # input
        prefix = input("Prefix (optional): ").strip()
        # input
        # EOS option - only if not already in experimental mode
        experimental_mode = (self.mode == "experimental")
        if experimental_mode:
            print("(Using EOS trie - experimental mode active)")
            use_eos = True
        else:
            eos_input = input("Use EOS markers for natural word endings? (yes for EOS, default: no): ").strip().lower()
            use_eos = eos_input in ("y", "yes")

        return {
            "seed": seed,
            "length": length,
            "k": k,
            "prefix": prefix,
            "n_suggestions": n_suggestions,
            "data_size": data_size,
            "use_eos": use_eos,
        }

    
    def show_results(self, results, continuation_flags=None):
        """
        Display the generated results with optional continuation markers (if debug is set to on).
        """
        print("\nGenerated options:")
        for i, name in enumerate(results, 1):
            marker = " (extended)" if continuation_flags and i-1 < len(continuation_flags) and continuation_flags[i-1] else ""
            print(f"  {i}. {name}{marker}")
        
        if continuation_flags and any(continuation_flags):
            extended_count = sum(continuation_flags)
            print(f"\n {extended_count}/{len(results)} names were extended beyond natural word boundaries")