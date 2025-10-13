# trim_v1.py

import re
import math
import string

DELIMS = "-_/"
ALNUM = set(string.ascii_lowercase + string.digits)

def count_tokens(s: str, delims: str = DELIMS) -> int:
    """Count non-empty tokens split on the given delimiters."""
    return len([t for t in re.split(f"[{re.escape(delims)}]+", s) if t])

def trim_to_token(
    name: str,
    min_len: int = 5,
    min_tokens: int = 2,
    boundary_window: float = 0.12,
    delims: str = DELIMS,
    max_length: int = None, 
) -> str:
    if not name or len(name) < min_len:
        return name
    
    original = name
    
    # Remove trailing delimiters
    s = name.rstrip(delims)
    if not s or s[-1].lower() not in ALNUM:
        return s
    
    # Find last delimiter
    last_delim_pos = max((s.rfind(d) for d in delims), default=-1)
    if last_delim_pos == -1:
        return s

    # Priority 1: Always trim short segments (1-2 chars)
    segment_len = len(s) - last_delim_pos - 1
    if 1 <= segment_len <= 2:
        candidate = s[:last_delim_pos].rstrip(delims)
        if candidate and len(candidate) >= min_len:
            # Short segment trimmed - skip 70% check and return immediately
            return candidate
    
    # Check if delimiter is within the boundary window
    distance_from_end = len(s) - last_delim_pos - 1
    window = math.ceil(boundary_window * len(s))
    
    if distance_from_end > window:
        return s
    
    # Try trimming at the delimiter
    candidate = s[:last_delim_pos].rstrip(delims)
    
    # Check constraints
    if len(candidate) < min_len or count_tokens(candidate, delims) < min_tokens:
        return s

    # Only trim if result stays reasonably close to target (70%+)
    # BUT: Only enforce this for SIGNIFICANT trims (>3 chars)
    trim_amount = len(original) - len(candidate)
    if max_length and trim_amount > 3:
        if len(candidate) < (0.7 * max_length):
            return s
    
    return candidate