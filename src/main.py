# /src/main.py
# Programme entry & orchestration: Handles UI initialization and user input, loads data, builds trie, constructs generator, and outputs N names.

import src.generator_factory as generator_factory
import src.trie_factory as trie_factory
import src.data_handler.data_handler as data_handler 
from src.ui.ui import UI
import time 
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Repository Name Generator')
    # Debugging options
    # Useable on any build of generator
    parser.add_argument('--debug-trie', action='store_true', # store_true makes the argument a boolean flag (True if present, False if absent)
                       help='Show trie structure when built')
    parser.add_argument('--debug-generator', action='store_true',
                       help='Show and log generator debug info')  
    parser.add_argument('--debug-main', action='store_true',
                       help='Show debug prints in main loop')
    parser.add_argument('--debug-all', action='store_true',
                       help='Enable all debug modes')
    # Trim options (mutually exclusive)
    trim_group = parser.add_mutually_exclusive_group()
    trim_group.add_argument('--enable-trim-v1', action='store_true',
                            help='Enable delimiter-based trim algorithm')
    trim_group.add_argument('--enable-trim-v2', action='store_true',
                            help='Enable morphologically-aware trim algorithm')
    # Options for Experimerntal Generator (always builds trie with <EOS> tokens)
    # default is to build a trie with no EOS tokens, and a standard generator not allowing for below additional features
    # but user can enable these options through command-line arguments and use the experimental generator
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='Generation temperature (default: 1.0)')
    parser.add_argument('--use-eos-continuation-search', action='store_true',
                        help='Enable EOS continuation search (alternative path exploration on hitting eos token, operates until threshold length reached)')
    # If P(EOS | context) ≥ eos-threshold, defer ending and try alternate continuation
    parser.add_argument('--eos-threshold', type=float, default=0.4,
                        help='EOS probability threshold for shifting (default: 0.4)')
    parser.add_argument('--max-continuation-attempts', type=int, default=3,
                        help='Maximum continuation search attempts (default: 3)')
    return parser.parse_args()

# Configuration from command line
# ---------------------------------------------------------------
args = parse_args()

DEBUG_TRIE = args.debug_trie or args.debug_all
DEBUG_GENERATOR = args.debug_generator or args.debug_all  
DEBUG_MAIN = args.debug_main or args.debug_all
TEMPERATURE = args.temperature
USE_EOS_CONTINUATION_SEARCH = args.use_eos_continuation_search
EOS_THRESHOLD = args.eos_threshold
MAX_CONTINUATION_ATTEMPTS = args.max_continuation_attempts
EXPERIMENTAL_MODE = (args.temperature != 1.0 or args.use_eos_continuation_search)
ENABLE_TRIM_V1 = args.enable_trim_v1
ENABLE_TRIM_V2 = args.enable_trim_v2
# ---------------------------------------------------------------

# Load training data 
# ---------------------------------------------------------------
#with open("data/training_data.txt", "r", encoding="utf-8") as f:
#    training_data = [line.strip() for line in f if line.strip()]
training_data = data_handler.load_training_data(
    "data/training_data.txt", 
)
# ---------------------------------------------------------------

ui = UI(mode="experimental" if EXPERIMENTAL_MODE else "basic")

# CACHED STATE (persist across UI loop) 
# Avoids time-intensive rebuilding 
# trie rebuilt only when k/data_size/use_eos changes,
# generator rebuilt only when n_suggestions changes. 
# ---------------------------------------------------------------
_cached_trie = None
_cached_k = None
_cached_data_size = None 
_cached_training_data = None
_cached_use_eos = None 

_gen = None
_gen_settings = None  # tuple capturing generator-related settings
# ---------------------------------------------------------------

while True:
    print()
    print("        ⭐⭐⭐ REPOSITORY NAME GENERATOR ⭐⭐⭐             ")

    
    if EXPERIMENTAL_MODE:
        print("\n*** Running in EXPERIMENTAL MODE (alternative generation features in use) ***")

    # 1) Get user input
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    user_input = ui.get_user_input(experimental_mode=EXPERIMENTAL_MODE)
    if user_input is None:  # user quit
        break

    # seed
    seed = user_input["seed"] 
    # max_length
    max_length = user_input["length"] 
    # n_suggestions
    n_suggestions = user_input["n_suggestions"]  
    # k
    k = user_input["k"]
    # data_size
    data_size = user_input["data_size"]  # how many lines of training data to use
    # use_eos
    if EXPERIMENTAL_MODE:
        USE_EOS = True  # always use EOS in experimental
    else:
        USE_EOS = user_input["use_eos"]  # user's choice in base mode
    # generator settings
    generator_settings = (user_input["n_suggestions"],) # tuple of current generator settings, currently only n_suggestions


    # Start processing
    process_start_time = time.time()  # start timing here
    if DEBUG_MAIN: print(f"\n----------------------------------(main loop debug output)")

    # 2) Reload data ONLY if data_size changes.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    
    # Check if the data needs to be reloaded (first run or data_size changed)
    data_reloaded = False
    if _cached_training_data is None or data_size != _cached_data_size:
        training_data = data_handler.load_training_data(
            "data/training_data.txt", 
            limit=data_size
        )
        _cached_training_data = training_data
        _cached_data_size = data_size
        data_reloaded = True # use a flag to signal a data change
        if DEBUG_MAIN: print(f"Training data reloaded with size: {len(_cached_training_data)}")
    else:
        # If no reload, use the cached data
        training_data = _cached_training_data # shallow copy
        
    # 3) Build new trie ONLY if 
    # - we dont have one yet
    # - OR k changed 
    # - OR data was just reloaded 
    # - OR EOS setting changed
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if data_reloaded or k != _cached_k or USE_EOS != _cached_use_eos:
        _cached_trie = trie_factory.build(training_data, k=k, debug=DEBUG_TRIE, use_eos=USE_EOS)
        _cached_k = k
        _cached_use_eos = USE_EOS  
        if DEBUG_MAIN: 
            print(f"Trie built with k={k}")
            mode = "with EOS" if USE_EOS else "without EOS"
            print(f"Using trie {mode}")

        # ... (rest of the generator update logic)
        if _gen is not None and _gen_settings == generator_settings:
            _gen.trie = _cached_trie
            _gen.k = _cached_trie.get_k()
            if DEBUG_MAIN: print("Generator updated with new trie")

    # 4) Build a new generator ONLY if 
    # - we don't have one yet 
    # - OR its settings changed (n_suggestions)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if _gen is None or _gen_settings != generator_settings:
        _gen = generator_factory.build(
            _cached_trie, 
            n_suggestions=n_suggestions, 
            debug=DEBUG_GENERATOR,
            temperature=TEMPERATURE,
            use_eos_continuation_search=USE_EOS_CONTINUATION_SEARCH,
            eos_threshold=EOS_THRESHOLD,                 
            max_continuation_attempts=MAX_CONTINUATION_ATTEMPTS,                     
            training_data=training_data,
            enable_trim_v1=ENABLE_TRIM_V1,
            enable_trim_v2=ENABLE_TRIM_V2             
        )
        if DEBUG_MAIN: print(f"Generator (re)built to produce {user_input['n_suggestions']} suggestions")
        _gen_settings = generator_settings

    # 5) Generate results
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    results = _gen.generate_batch(
        seed=seed, 
        max_length=max_length, 
        n=n_suggestions,
        process_start_time=process_start_time, # pass timing, we want it output to the logs also
        data_size=len(training_data)
    )

    # Get continuation flags if available, for displaying in UI
    continuation_flags = getattr(_gen, '_last_continuation_flags', None)

    # 6) Optional prefix handling
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if user_input["prefix"]:
        results = [f"{user_input['prefix']}{r}" for r in results]

    # 7) Show results
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    ui.show_results(results, continuation_flags=continuation_flags)