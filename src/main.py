# /src/main.py
# Programme entry & orchestration: Handles UI initialization and user input, loads data, builds trie, constructs generator, and outputs N names.

import src.generator_factory as generator_factory
import src.trie_factory as trie_factory
import src.data_handler.data_handler as data_handler 
from src.ui.ui import UI
import time 

# Configuration 
# ---------------------------------------------------------------
DEBUG_TRIE = False      # show trie structure when (re)built
DEBUG_GENERATOR = True # print + log generator debug
DEBUG_MAIN = True # debug prints in main loop
# ----------------------------------------------------------------------------

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

_gen = None
_gen_settings = None  # tuple capturing generator-related settings
# ----------------------------------------------------------------------------

while True:
    print()
    print("***************************************************************")
    print("*               REPOSITORY NAME GENERATOR                     *")
    print("***************************************************************")
    user_input = ui.get_user_input()
    if user_input is None:  # user quit
        break

    k = user_input["k"]
    generator_settings = (user_input["n_suggestions"],) # tuple of current generator settings
    data_size = user_input["data_size"]  # how many lines of training data to use


    
    process_start_time = time.time()  # start timing here

    if DEBUG_MAIN: print(f"\n----------------------------------(main loop debug output)")

    # 1) Reload data ONLY if data_size changes.
    
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
        
    # 2) Rebuild the trie ONLY IF k changed OR data was just reloaded.
    if data_reloaded or k != _cached_k:
        _cached_trie = trie_factory.build(training_data, k=k, debug=DEBUG_TRIE)
        _cached_k = k
        if DEBUG_MAIN: print(f"Trie rebuilt with k={k}")

        # ... (rest of the generator update logic)
        if _gen is not None and _gen_settings == generator_settings:
            _gen.trie = _cached_trie
            _gen.k = _cached_trie.get_k()
            if DEBUG_MAIN: print("Generator updated with new trie")

    # 3) Build a new generator ONLY if its settings changed or we don't have one yet

    if _gen is None or _gen_settings != generator_settings:
        _gen = generator_factory.build(
            _cached_trie, 
            n_suggestions=user_input["n_suggestions"], 
            debug=DEBUG_GENERATOR
        )
        if DEBUG_MAIN: print(f"Generator (re)built to produce {user_input['n_suggestions']} suggestions")
        _gen_settings = generator_settings

    # 4) Generate results

    results = _gen.generate_batch(
        seed=user_input["seed"], 
        max_length=user_input["length"], 
        n=user_input["n_suggestions"],
        process_start_time=process_start_time, # Pass timing, we want it output to the logs also
        data_size=len(training_data)
    )

    # 5) Optional prefix handling

    if user_input["prefix"]:
        results = [f"{user_input['prefix']}{r}" for r in results]

    ui.show_results(results)