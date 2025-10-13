# trim_v2.py

import re
import math
import string

DELIMS = "-_/"
ALNUM = set(string.ascii_lowercase + string.digits)
VOWELS = set('aeiouyäö')

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
    if not name:
        return name
    
    original = name
    s = name
    
    # (1) Clean dangling delimiters
    s = s.rstrip(delims)
    if not s:
        return original[:max(1, min_len)]
    
    # (2) Drop 1-2 character tail segments
    # Handles: 'alpha-x' → 'alpha', 'helper-bu' → 'helper'
    short_segment_trimmed = False  
    for sep in delims:
        i = s.rfind(sep)
        if i != -1:
            segment_len = len(s) - i - 1
            if 1 <= segment_len <= 2:
                candidate = s[:i].rstrip(delims)
                if candidate and len(candidate) >= min_len:
                    s = candidate
                    short_segment_trimmed = True  
                    break
    
    # If we trimmed a short segment, skip morphological analysis and go to final validation
    if short_segment_trimmed: 
        # Skip to step 8
        trim_amount = len(original) - len(s)
        if max_length and trim_amount > 3:
            threshold = 0.7 * max_length
            if len(s) < threshold:
                return original
        return s
    
    # (3) Avoid clearly awkward endings
    # Letters rare at word/name boundaries: q, w, x, j, v, z
    awkward_finals = set("qwxjvz")
    if s and s[-1].lower() in awkward_finals:
        # Try backing off to previous delimiter
        cut = max((s.rfind(d) for d in delims), default=-1)
        if cut > 0:
            candidate = s[:cut].rstrip(delims)
            if candidate and len(candidate) >= min_len:
                s = candidate
    
    # (4) Handle incomplete morphemes (truncated words)
    # Detect patterns like 'vectorizatio', 'repositor', 'optimiz'
    if len(s) >= 3:
        last_two = s[-2:].lower()
        last_three = s[-3:].lower() if len(s) >= 3 else ""
        
        # Common incomplete endings that suggest truncation
        incomplete_detected = False
        
        # Pattern: 'repositor' (vowel + consonant at end, likely missing 'y')
        if len(last_two) == 2 and last_two[0] in VOWELS and last_two[1] not in VOWELS:
            incomplete_detected = True
        
        # Pattern: 'optimiz' (consonant cluster after vowel)
        elif (len(last_three) >= 2 and 
              last_two[0] not in VOWELS and 
              last_two[1] not in VOWELS and
              len(s) >= 3 and s[-3].lower() in VOWELS):
            incomplete_detected = True
        
        # Pattern: 'vectorizatio' (incomplete suffix)
        elif last_three in ('tio', 'sio', 'tia', 'sia'):
            incomplete_detected = True
        
        if incomplete_detected:
            # Look for delimiter to back off to
            cut = max((s.rfind(d) for d in delims), default=-1)
            if cut > 0:
                candidate = s[:cut].rstrip(delims)
                if candidate and len(candidate) >= min_len:
                    s = candidate
    
    # (5) Final cleanup: ensure last character is alphanumeric
    s = s.rstrip(string.punctuation + string.whitespace)
    
    # (6) Emergency fallback: if we still have issues, find best boundary
    if not s or len(s) < 3:
        # Walk backwards from original to find first delimiter or good boundary
        for i in range(len(original) - 1, max(0, min_len - 1), -1):
            if original[i] in delims:
                candidate = original[:i].rstrip(delims)
                if candidate and len(candidate) >= 3:
                    return candidate
        
        # Hard fallback: just take prefix
        return original[:max(min_len, 3)].rstrip(delims + string.punctuation)
    
    # (7) Token count validation: if too few tokens, try to preserve more
    if count_tokens(s, delims) < min_tokens and len(s) < len(original):
        # Find the Nth delimiter from the start to keep min_tokens
        delim_positions = [i for i, c in enumerate(original) if c in delims]
        if len(delim_positions) >= min_tokens - 1:
            cut_pos = delim_positions[min_tokens - 2] + 1
            # Extend our trim to include more tokens
            if cut_pos > len(s):
                candidate = original[:cut_pos].rstrip(delims)
                if candidate:
                    s = candidate
    
    # (8) Target length validation: don't trim if result is too short relative to target
    # BUT: Allow trimming short segments (1-2 chars) regardless of target length
    
    # Calculate how much we trimmed
    trim_amount = len(original) - len(s)
    
    # Only enforce 70% rule if we trimmed a SIGNIFICANT amount (more than just 1-2 chars)
    if max_length and trim_amount > 3:
        threshold = 0.7 * max_length
        if len(s) < threshold and len(s) < len(original):
            return original  # Don't trim, too far from target
    
    return s if s else original[:min_len].rstrip(delims)