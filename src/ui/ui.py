# src/ui/ui.py
# Handles user interaction and input/output.

class UI:
    def __init__(self, mode="basic"):
        self.mode = mode
    
    def get_user_input(self):
        print("\nNEW USER INPUT")
        seed = input("Enter seed text (or 'quit' to exit): ")
        if seed.lower() == 'quit':
            return None
        
        # INPUTS
        length = int(input("Max length (default 10): ") or "10")
        k = int(input("Markov degree k (default 2): ") or "2")
        n_suggestions = int(input("Number of suggestions (default 5): ") or "5")
        prefix = input("Prefix (optional): ")
        data_size = input("Training data size (default all, or number): ").strip()
        if not data_size or data_size.lower() == 'all':
            data_size = None
        else:
            data_size = int(data_size)
        
        return {
            'seed': seed,
            'length': length,
            'k': k,
            'prefix': prefix,
            'n_suggestions': n_suggestions,
            'data_size': data_size 
        }
    
    def show_results(self, results):
        """Show multiple results"""
        print("\nGenerated options:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result}")