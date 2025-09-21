# src/data_handler/data_handler.py
# Data loading & preprocessing entry point: handles data related preprocessing tasks.

def load_training_data(filepath: str, limit: int = None):
    """Load training data with optional size limit"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            word = line.strip()
            if word:
                data.append(word)
    return data