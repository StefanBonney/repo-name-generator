# tests/ui/test_ui.py
# Simple unit tests for ui. Focus: Input validation works correctly or other similar functionality checks.


import builtins
import pytest
from src.ui.ui import UI

def test_ui_defaults_basic_mode(monkeypatch):
    """
    TEST
    What: UI returns default values when user presses Enter on all prompts
    Why: Defaults should be used without typing values
    How: Mock input to return empty strings, verify returned dict has defaults
    """
    
    # This replaces keyboard input with these responses (in order)
    fake_inputs = iter([
        "test",  # seed (can't be empty)
        "",      # length → defaults to 10
        "",      # k → defaults to 2  
        "",      # n_suggestions → defaults to 5
        "",      # data_size → defaults to None
        "",      # prefix → defaults to ""
        "",      # use_eos → defaults to False
    ])
    
    # Make input() return our fake responses
    monkeypatch.setattr(builtins, "input", lambda prompt: next(fake_inputs))
    
    ui = UI()
    result = ui.get_user_input(experimental_mode=False)
    
    # Check we got defaults
    assert result["seed"] == "test"
    assert result["length"] == 10
    assert result["k"] == 2
    assert result["n_suggestions"] == 5
    assert result["data_size"] is None
    assert result["prefix"] == ""
    assert result["use_eos"] is False

def test_ui_custom_values(monkeypatch):
    """
    TEST
    What: UI correctly accepts and returns custom user-provided values
    Why: Users need to specify non-default parameters for different use cases
    How: Mock input with custom values, verify returned dict matches inputs
    """
    
    fake_inputs = iter([
        "my",        # seed
        "15",        # length
        "3",         # k
        "10",        # n_suggestions
        "1000",      # data_size
        "prefix-",   # prefix
        "yes"        # use_eos
    ])
    
    monkeypatch.setattr(builtins, "input", lambda prompt: next(fake_inputs))
    
    ui = UI()
    result = ui.get_user_input(experimental_mode=False)
    
    assert result["seed"] == "my"
    assert result["length"] == 15
    assert result["k"] == 3
    assert result["n_suggestions"] == 10
    assert result["data_size"] == 1000
    assert result["prefix"] == "prefix-"
    assert result["use_eos"] is True

def test_ui_validates_invalid_integer_input(monkeypatch, capsys):
    """
    TEST
    What: UI rejects invalid integer input and shows error, then accepts valid input
    Why: Verify validation loop catches bad input and guides user to correct it
    How: Provide "kkjl" for length field, then "15", check error message printed
    """
    
    fake_inputs = iter([
        "test",  # seed
        "kkjl",  # length → INVALID (not an integer)
        "15",    # length → VALID
        "",      # k → defaults to 2
        "",      # n_suggestions → defaults to 5
        "",      # data_size → defaults to None
        "",      # prefix → defaults to ""
        "no"     # use_eos
    ])
    
    monkeypatch.setattr(builtins, "input", lambda prompt: next(fake_inputs))
    
    ui = UI()
    result = ui.get_user_input(experimental_mode=False)
    
    # Should eventually accept the valid value
    assert result["length"] == 15
    
    # Check for the actual error message from _validate_int_input
    output = capsys.readouterr().out
    assert "Enter an integer or leave empty." in output