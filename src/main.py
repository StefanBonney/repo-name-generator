# /src/main.py
# Programme entry & orchestration: Handles UI initialization and user input, loads data, builds trie, constructs generator, and outputs N names.

import src.generator_factory as generator_factory
import src.trie_factory as trie_factory
import src.data_handler.data_handler as data_handler 
from src.ui.ui import UI
import time 
import argparse

def parse_args():
    '''
    Usage examples:
    ----------------
    # Default: Base generator with base trie (no EOS)
    python -m src.main
    
    # Base generator with debug output
    python -m src.main --debug-generator
    
    # Experimental: Temperature automatically triggers EOS trie
    python -m src.main --temperature 1.5
    
    # Experimental: Context-shifting automatically triggers EOS trie  
    python -m src.main --use-context-shifting --eos-threshold 0.3
    
    # Experimental: Multiple features together
    python -m src.main --temperature 0.8 --use-context-shifting --max-shifts 5
    
    # Debug everything with experimental features
    python -m src.main --debug-all --temperature 1.2
    
    # Compare base vs experimental:
    #   Base:         python -m src.main
    #   Experimental: python -m src.main --temperature 1.2
    '''
    parser = argparse.ArgumentParser(description='Repository Name Generator')
    # Debugging options
    # Useable on any build of generator
    parser.add_argument('--debug-trie', action='store_true', 
                       help='Show trie structure when built')
    parser.add_argument('--debug-generator', action='store_true',
                       help='Show and log generator debug info')  
    parser.add_argument('--debug-main', action='store_true',
                       help='Show debug prints in main loop')
    parser.add_argument('--debug-all', action='store_true',
                       help='Enable all debug modes')
    # Options for Base Generator and Experimental Generator
    parser.add_argument('--enable-trim', action='store_true',
                   help='Trim incomplete tokens at end of generated names')
    # Options for Experimerntal Generator (builds trie with <EOS> tokens)
    # default is to build a trie with no EOS tokens, and a standard generator not allowing for below options
    # but user can enable these options through command-line arguments to experiment with the experimental generator
    parser.add_argument('--temperature', type=float, default=1.0,
                       help='Generation temperature (default: 1.0)')
    parser.add_argument('--use-context-shifting', action='store_true',
                   help='Enable EOS-triggered context shifting')
    parser.add_argument('--eos-threshold', type=float, default=0.4,
                   help='EOS probability threshold for shifting (default: 0.4)')
    parser.add_argument('--max-shifts', type=int, default=3,
                   help='Max Shifts per k-gram (default: 3)')
    return parser.parse_args()

# Configuration from command line
# ---------------------------------------------------------------
args = parse_args()

DEBUG_TRIE = args.debug_trie or args.debug_all
DEBUG_GENERATOR = args.debug_generator or args.debug_all  
DEBUG_MAIN = args.debug_main or args.debug_all
TEMPERATURE = args.temperature
USE_CONTEXT_SHIFTING = args.use_context_shifting
EOS_THRESHOLD = args.eos_threshold
MAX_SHIFTS = args.max_shifts
EXPERIMENTAL_MODE = (args.temperature != 1.0 or args.use_context_shifting) 
ENABLE_TRIM = args.enable_trim
# ---------------------------------------------------------------

# Load training data 
# ----------------------------------------------------------
#with open("data/training_data.txt", "r", encoding="utf-8") as f:
#    training_data = [line.strip() for line in f if line.strip()]
training_data = data_handler.load_training_data(
    "data/training_data.txt", 
)
# ----------------------------------------------------------------------------

ui = UI()

# CACHED STATE (persist across UI loop) 
# ----------------------------------------------------------------------------
_cached_trie = None
_cached_k = None
_cached_data_size = None 
_cached_training_data = None
_cached_use_eos = None 

_gen = None
_gen_settings = None  # tuple capturing generator-related settings
# ----------------------------------------------------------------------------

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

    k = user_input["k"]
    generator_settings = (user_input["n_suggestions"],) # tuple of current generator settings
    data_size = user_input["data_size"]  # how many lines of training data to use

    if EXPERIMENTAL_MODE:
        USE_EOS = True  # Always use EOS in experimental
    else:
        USE_EOS = user_input["use_eos"]  # User's choice in base mode


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
        data_reloaded = True # Use a flag to signal a data change
        if DEBUG_MAIN: print(f"Training data reloaded with size: {len(_cached_training_data)}")
    else:
        # If no reload, use the cached data
        training_data = _cached_training_data # shallow copy
        
    # 3) Rebuild the trie ONLY IF k changed OR data was just reloaded OR EOS setting changed
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if data_reloaded or k != _cached_k or USE_EOS != _cached_use_eos:
        _cached_trie = trie_factory.build(training_data, k=k, debug=DEBUG_TRIE, use_eos=USE_EOS)
        _cached_k = k
        _cached_use_eos = USE_EOS  
        if DEBUG_MAIN: 
            print(f"Trie rebuilt with k={k}")
            mode = "with EOS" if USE_EOS else "without EOS"
            print(f"Using trie {mode}")

        # ... (rest of the generator update logic)
        if _gen is not None and _gen_settings == generator_settings:
            _gen.trie = _cached_trie
            _gen.k = _cached_trie.get_k()
            if DEBUG_MAIN: print("Generator updated with new trie")

    # 4) Build a new generator ONLY if its settings changed OR we don't have one yet
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if _gen is None or _gen_settings != generator_settings:
        _gen = generator_factory.build(
            _cached_trie, 
            n_suggestions=user_input["n_suggestions"], 
            debug=DEBUG_GENERATOR,
            temperature=TEMPERATURE,
            use_context_shifting=USE_CONTEXT_SHIFTING,  
            eos_threshold=EOS_THRESHOLD,                 
            max_shifts=MAX_SHIFTS,                       
            training_data=training_data,
            enable_trim=ENABLE_TRIM                 
        )
        if DEBUG_MAIN: print(f"Generator (re)built to produce {user_input['n_suggestions']} suggestions")
        _gen_settings = generator_settings

    # 5) Generate results
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    results = _gen.generate_batch(
        seed=user_input["seed"], 
        max_length=user_input["length"], 
        n=user_input["n_suggestions"],
        process_start_time=process_start_time, # Pass timing, we want it output to the logs also
        data_size=len(training_data)
    )

    # 6) Optional prefix handling
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

    if user_input["prefix"]:
        results = [f"{user_input['prefix']}{r}" for r in results]

    ui.show_results(results)