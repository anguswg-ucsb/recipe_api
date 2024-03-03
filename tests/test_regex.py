# pytest library
import pytest

import re

# old imports
# import climatePy._utils as climatePy
# import climatePy._extract_sites as climatePy
# import climatePy._dap as climatePy
# import climatePy._shortcuts as climatePy


# import lambda_containers.extract_ingredients.parser.regex_patterns as regex_patterns
from lambda_containers.extract_ingredients.parser.regex_patterns3 import RegexPatterns, RecipeRegexPatterns

# regex_map = RegexPatterns()

@pytest.fixture
def regex_map():
    return RecipeRegexPatterns()

def test_quantity_range_pattern(regex_map):
    regex_map = RecipeRegexPatterns()
    input_string = "This is a test string with 1-2.5 oz range."

    ingredient_strings = [
    "1 2/3 - 2 1/2 cups of flour",
    "1 cup - 2 cups of sugar",
    "1.5 - 2.5  kg of sugar",
    "0.25-0.5 liters-milk",
    "10.75 11.25 oz of chocolate chips",
    "0.1 0.2 lb of butter",
    "1-2 3-4",
    "abc-xyz",
    "1 2 3 - 4 5 6 cups of flour"
    ]

    assert re.findall(regex_map.QUANTITY_RANGE, "1.5 - 2.5  kg of sugar") == ['1.5 - 2.5']
    assert re.findall(regex_map.QUANTITY_RANGE, "0.25-0.5 liters-milk") == ['0.25-0.5']
    assert re.findall(regex_map.QUANTITY_RANGE, "10.75 11.25 oz of chocolate chips") == []
    assert re.findall(regex_map.QUANTITY_RANGE, "0.1 0.2 lb of butter") == []
    assert re.findall(regex_map.QUANTITY_RANGE, "1-2 3-4") == ['1-2', '3-4']
    assert re.findall(regex_map.QUANTITY_RANGE, "abc-xyz") == []
    assert re.findall(regex_map.QUANTITY_RANGE, "1 2 3 - 4 5 6 cups of flour") == ['3 - 4']

    string_with_many_patterns = f"""¼ cup packed 1/2 - 12/16 brown sugar tbsp."""

    matches = regex_map.find_matches(string_with_many_patterns)

    for key, value in matches.items():
        print(f"{key}: {value}")


    assert matches['QUANTITY_RANGE_PATTERN'] == ['1-2.5 oz']

def test_quantity_word_pattern(regex_map):
    input_string = "This is a test string with 3 tbsp of sugar."
    matches = regex_patterns.find_matches(input_string)
    assert matches['QUANTITY_WORD_PATTERN'] == ['3 tbsp']
