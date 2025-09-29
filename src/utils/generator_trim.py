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
) -> str:
    """
    Trim at the last delimiter if it's near the end of the string.
    
    Args:
        name: String to potentially trim
        min_len: Minimum length to keep
        min_tokens: Minimum number of tokens to keep
        boundary_window: Relative window (fraction of length) for trimming
        delims: Delimiter characters
    
    Returns:
        Trimmed string or original if trimming conditions not met
    """
    if not name or len(name) < min_len:
        return name
    
    # Remove trailing delimiters
    s = name.rstrip(delims)
    if not s or s[-1].lower() not in ALNUM:
        return s
    
    # Find last delimiter
    last_delim_pos = max((s.rfind(d) for d in delims), default=-1)
    if last_delim_pos == -1:
        return s
    
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
    
    return candidate