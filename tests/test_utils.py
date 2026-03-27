import sys
import os
import math

# Add api folder to sys.path to easily import main
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.main import safe, to_usd

def test_safe():
    # Test typical values
    assert safe(123.456789) == 123.456789
    assert safe("12.34", d=1) == 12.3
    
    # Test None / missing
    assert safe(None) is None
    assert safe("") is None
    assert safe("invalid_text") is None
    
    # Test NaN and Infinity
    assert safe(float("nan")) is None
    assert safe(float("inf")) is None
    assert safe(float("-inf")) is None

def test_to_usd():
    # Test valid conversion
    assert to_usd(500000, 150) == round(500000 / 150, 2)
    
    # Test invalid inputs
    assert to_usd(None, 150) is None
    assert to_usd(500, None) is None
    assert to_usd(500, 0) is None
    assert to_usd(500, -10) == round(500 / -10, 2)

if __name__ == "__main__":
    print("Running tests...")
    test_safe()
    test_to_usd()
    print("All tests passed!")
