# Description: This module contains all the regex patterns used in the recipe parser. 
# As well as a class to hold all regex patterns used in the recipe parser (version 2)

import re
from typing import Dict, List, Tuple, Union

# import lambda_containers.extract_ingredients.parser.static_values
# from lambda_containers.extract_ingredients.parser.static_values import NUMBER_WORDS, NUMBER_WORDS_REGEX_MAP, UNICODE_FRACTIONS, UNICODE_FRACTIONS_PATTERN, UNITS, UNITS_PATTERN, ANY_NUMBER_THEN_UNIT_PATTERN, UNIT_THEN_ANY_NUMBER_PATTERN
from lambda_containers.extract_ingredients.parser._constants import (
    NUMBER_WORDS, 
    FRACTION_WORDS,
    UNICODE_FRACTIONS,
    UNITS,
    BASIC_UNITS,
    VOLUME_UNITS,
    CASUAL_QUANTITIES,
    UNIT_MODIFIERS,
    PREP_WORDS,
    UNITS_SET,
    BASIC_UNITS_SET,
    VOLUME_UNITS_SET
)

# import _constants modules
# from . import _constants
# from .static_values import NUMBER_WORDS, NUMBER_WORDS_REGEX_MAP, UNICODE_FRACTIONS, UNITS, UNITS_PATTERN, ANY_NUMBER_THEN_UNIT_PATTERN, UNIT_THEN_ANY_NUMBER_PATTERN
from ._constants import (
    NUMBER_WORDS, 
    FRACTION_WORDS,
    UNICODE_FRACTIONS,
    UNITS,
    BASIC_UNITS,
    VOLUME_UNITS,
    CASUAL_QUANTITIES,
    UNIT_MODIFIERS,
    PREP_WORDS,
    UNITS_SET,
    BASIC_UNITS_SET,
    VOLUME_UNITS_SET
)

# -----------------------------------------------------------------------------
# --------------------------- Conversion patterns -----------------------------
# Patterns for converting: 
# - Number words to numerical values
# - Fractions represented as words to fraction strings
# - Unicode fractions to decimals
# -----------------------------------------------------------------------------

# Create a map of number words to their numerical values
NUMBER_WORDS_REGEX_MAP = {}
for word, value in NUMBER_WORDS.items():
    # print(f"Word: {word} \nValue: {value}")
    NUMBER_WORDS_REGEX_MAP[word] = [str(value), re.compile(r'\b' + word + r'\b', re.IGNORECASE)]
    # print(f"\n")

# Matches unicode fractions in the string
UNICODE_FRACTIONS_PATTERN = re.compile( r'\b(?:' + '|'.join(re.escape(word) for word in UNICODE_FRACTIONS.keys()) + r')\b', re.IGNORECASE)

# -----------------------------------------------------------------------------
# --------------------------- Units patterns -----------------------------
# Patterns for matching:
# - units in a string
# - matching a number followed by a unit
# - matching a unit followed by a number
# -----------------------------------------------------------------------------

# Generate the regular expression pattern for units in the string
any_unit_pattern = '|'.join('|'.join(variants) for variants in UNITS.values())

# just the basic units 
basic_unit_pattern = '|'.join('|'.join(variants) for variants in BASIC_UNITS.values())

# Generate the regular expression pattern for units in the string
volume_units_strings = '|'.join('|'.join(variants) for variants in VOLUME_UNITS.values())

# create a regular expression pattern to match the units in a string
UNITS_PATTERN = re.compile(r'\b(?:' + any_unit_pattern + r')\b', re.IGNORECASE)
# UNITS_PATTERN = re.compile(r'\b(?:' + '|'.join('|'.join(variants) for variants in UNITS.values()) + r')\b', re.IGNORECASE)

# match just the basic units
BASIC_UNITS_PATTERN = re.compile(r'\b(?:' + basic_unit_pattern + r')\b', re.IGNORECASE)

# create a regular expression pattern to match specifically volume units in a string
VOLUME_UNITS_PATTERN = re.compile(r'\b(?:' + volume_units_strings + r')\b', re.IGNORECASE)

# match any unit?
ANY_UNIT_PATTERN = re.compile(r'\b(?:' + any_unit_pattern + r')\b', re.IGNORECASE)

# -----------------------------------------------------------------------------
# --------------------------- Unit/Number or Number/Unit patterns -----------------------------
# Patterns for matching:
# - a number followed by a unit
# - a unit followed by a number
# - a number followed by a unit followed by any text (full unit and abbreviation)
# - a unit followed by a number followed by any text (full unit and abbreviation)
# - a number/decimal/fraction followed by a space and then another number/decimal/fraction
# - a number/decimal/fraction followed by a space and then another number/decimal/fraction followed by a unit
# -----------------------------------------------------------------------------

# Construct the regular expression pattern that matches the number (including fractions and decimals)
# followed by 0+ spaces and then a unit in UNITS dictionary
ANY_NUMBER_THEN_UNIT = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*(?:' + any_unit_pattern + r')\b')
# ANY_NUMBER_THEN_UNIT = r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*(?:' + any_unit_pattern + r')\b'

# Construct the regular expression pattern that matches the number (including fractions and decimals)
# followed by any text and then a unit in UNITS dictionary
ANY_NUMBER_THEN_ANYTHING_THEN_UNIT = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*.*?\s*(?:' + any_unit_pattern + r')\b')

# Regular expression pattern to match any number/decimals/fraction in a string padded by atleast 1+ whitespaces
ANY_NUMBER = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b')

# Match ALL numbers in a string regardless of padding
ALL_NUMBERS = re.compile(r'(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)')

# Match any number/decimal/fraction followed by a space and then another number/decimal/fraction
# (e.g "1 1/2", "3 1/4", "3 0.5", "2.5 3/4")
SPACE_SEP_NUMBERS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s*(?:\d+/\d+|\d+\.\d+)\b')

# regex for matching numbers/fractions/decimals separated by "and" or "&" (e.g. "1/2 and 3/4", "1/2 & 3/4")
AND_SEP_NUMBERS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)(?:\s*(?:and|&)\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+))+\b')

# Match any number/decimal/fraction followed by a space and then a number/decimal/fraction
# (e.g "1 1/2", "3 1/4", "3 0.5", "2.5 3/4")
SPACE_SEP_NUMBERS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s+(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b')

# Match any number/decimal/fraction followed by 'x' or 'X' and then another number/decimal/fraction
# (e.g "1 x 5", "1X1.5", "2.5x20")
X_SEP_NUMBERS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)(?:\s*[xX]\s*)(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b')

# # This is VERY similar to above regex but just swaps "*" and "+" as to enforce the first pattern MUST MATCH atleast 1 time 
# SPACE_SEP_NUMBERS_OR_ANY_NUMBER_AFTER_WS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b') 
# SPACE_SEP_NUMBERS_OG  = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s*(?:\d+/\d+|\d+\.\d+)\b')
# SPACE_SEP_NUMBERS2 = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)(?:\s+\d*\.\d+|\s+\d+\s*/\s*\d+|\s+\d+)+\b')

# re.findall(SPACE_SEP_NUMBERS, '5 1.75oz of chocolate') # Output: ['5 1'] Expected: ['5 1.75'] (Wrong)
# re.findall(SPACE_SEP_NUMBERS, '5 15oz of chocolate') # Output: [] Expected: ['5 15'] (Wrong)
# re.findall(SPACE_SEP_NUMBERS, '5 1.75 oz of chocolate') # Output: ['5 1.75'] Expected: ['5 1.75'] (Correct)
# re.findall(SPACE_SEP_NUMBERS, '5 1/2oz of chocolate') # Output: ['5 1'] Expected: ['5 1/2'] (Wrong)

# Regular expression to match strings wrapped in parentheses, including the parentheses
PARENTHESIS_REGEX = re.compile(r'\((.*?)\)')

# Regular expression to match parentheses containing only a whole number, decimal, or fraction
PARENTHESIS_WITH_NUMBERS_ONLY = re.compile(r'\((\d*(?:\.\d+|\s*/\s*\d+|\d+))\)')

# Regular expression to match parentheses containing a number followed by a unit
# PARENTHESIS_WITH_UNITS = re.compile(r'\((\d*(?:\.\d+|\s*/\s*\d+|\d+))\s+(?:' + any_unit_pattern + r')\)')
PARENTHESIS_WITH_UNITS = re.compile(r'\((\d*(?:\.\d+|\s*/\s*\d+|\d+)\s+(?:' + any_unit_pattern + r'))\)')
PARENTHESIS_WITH_UNITS = re.compile(r'\((\d*(?:\.\d+|\s*/\s*\d+|\d+)\s*[-\s]*' + any_unit_pattern + r')\)')

PARENTHESIS_REGEX.findall("1 cup of oats (2 ounces) in a big mixing bowl")
PARENTHESIS_WITH_NUMBERS_ONLY.findall("1 cup of oats (2 ounces) in a big mixing bowl")
PARENTHESIS_WITH_UNITS.findall("1 cup of oats (2ounces) in a big mixing bowl")

PARENTHESIS_REGEX.findall("1 cup of oats (25) in a big mixing bowl")
PARENTHESIS_WITH_NUMBERS_ONLY.findall("1 cup of oats (25) in a big mixing bowl")
PARENTHESIS_WITH_UNITS.findall("1 cup of oats (25) in a big mixing bowl")

# Example string
example_string = "1 cup of oats (2 ounces) in a big mixing bowl"

# Find all matches
matches = PARENTHESIS_NUMBER_REGEX.findall(example_string)

# Print the matches
for match in matches:
    print(match)
# a number/decimal/fraction followed by 1+ spaces to another number/decimal/fraction followed by a 0+ spaces then a VOLUME unit
# (e.g. 1/2 cup, 1 1/2 cups, 1 1/2 tablespoon)
SPACED_NUMS_THEN_VOLUME_UNITS = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s*(?:\d+/\d+|\d+\.\d+)\s*(?:' + volume_units_strings + r')\b')

# Construct the regular expression pattern that matches the number (including fractions and decimals)
# followed by 0+ spaces and then a unit in UNITS dictionary (EXPIREMENTAL, probably throw away)
ANY_NUMBER_THEN_UNIT_CAPTURE = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*(.*?)*(?:' + any_unit_pattern + r')\b')

# Construct the regular expression pattern that matches the unit followed by 0+ spaces
# and then a number (including fractions and decimals)
UNIT_THEN_ANY_NUMBER = re.compile(r'\b(?:' + any_unit_pattern + r')\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b')
# UNIT_THEN_ANY_NUMBER = r'\b(?:' + any_unit_pattern + r')\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b'

# Regex to match number (QUANTITY) then unit abbreviation (single string as unit)
NUMBER_THEN_UNIT_ABBR = re.compile(r"(\d)\-?([a-zA-Z])") # 3g = 3 g

# Regex to match number (QUANTITY) then unit word (full word string as unit)
NUMBER_THEN_UNIT_WORD = re.compile(r"(\d+)\-?([a-zA-Z]+)") #  "3tbsp vegetable oil" = 3 tbsp

# -----------------------------------------------------------------------------
# --------------------------- RANGE PATTERNS ----------------------------------
# Patterns to match a number followed by a hyphen and then another number
# Handles cases with whole numbers, decimals, and fractions:
# - Whole number - Whole number
# - Whole number - Decimal
# - Whole number - Fraction
# - Decimal - Decimal
# - Decimal - Whole number
# - Decimal - Fraction
# - Fraction - Fraction
# - Fraction - Decimal
# - Fraction - Whole number
# Range patterns for some common language patterns:
# - "1/2 to 3/4"
# - "1/2 or 3/4"
# - "between 1/2 and 3/4"
# -----------------------------------------------------------------------------

# matches ANY numbers/decimals/fractions followed by a hypen to ANY numbers/decimals/fractions 
# This pattern does a really good job of matching almost ANY hypen separated numbers in a string
QUANTITY_DASH_QUANTITY = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")
# ANY_QUANTITY_RANGE = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")
# QUANTITY_DASH_QUANTITY = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")

# These are sub patterns of the QUANTITY_DASH_QUANTITY that match specific types of numbers
# Likely these won't be used but they are here for reference, as a sanity check, 
# for testing, and to use as a starting point

# Starts with a whole number:
WHOLE_NUMBER_DASH_WHOLE_NUMBER = re.compile(r"\d+\s*-\s*\d+")
WHOLE_NUMBER_DASH_DECIMAL = re.compile(r"\d+\s*-\s*\d+\.\d+")
WHOLE_NUMBER_DASH_FRACTION = re.compile(r"\d+\s*-\s*\d+/\d+")

# Starts with a decimal:
DECIMAL_DASH_DECIMAL = re.compile(r"\d+\.\d+\s*-\s*\d+\.\d+")
DECIMAL_DASH_WHOLE_NUMBER = re.compile(r"\d+\.\d+\s*-\s*\d+")
DECIMAL_DASH_FRACTION = re.compile(r"\d+\.\d+\s*-\s*\d+/\d+")

# Starts with a fraction:
FRACTION_DASH_FRACTION = re.compile(r"\d+/\d+\s*-\s*\d+/\d+")
FRACTION_DASH_DECIMAL = re.compile(r"\d+/\d+\s*-\s*\d+\.\d+")
FRACTION_DASH_WHOLE_NUMBER = re.compile(r"\d+/\d+\s*-\s*\d+")

#### (Old version of the QUANTITY_DASH_QUANTITY)
QUANTITY_RANGE = re.compile(r"\d+(?:\.\d+)?\s*(?:\s*-\s*)+\d+(?:\.\d+)?") #  matches numbers AND decimals with a hyphen in between them
# QUANTITY_RANGE = re.compile(r"\d+\s*(?:\s*-\s*)+\d+") #  matches numbers with a hyphen in between them (only whole numbers seperated by hypens)

# match pattern for a range of number/decimal/fraction with "to" or "or" in between them (e.g. "1/2 to 3/4", "1/2 or 3/4")
QUANTITY_TO_OR_QUANTITY = re.compile(r'\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:to|or)\s*(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))') # Works for if there is NO space between the number and the words "to" or "or" for either the first or second numbers
# RANGE_WITH_TO_OR = re.compile(r'\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:to|or)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))') # requires a space between the number and the word and or the "to" or "or" and the number,fraction, or decimal

# Regex pattern for matching "between" followed by a number/decimal/fraction, then "and" or "&", 
# and then another number/decimal/fraction (e.g. "between 1/2 and 3/4")
BETWEEN_QUANTITY_AND_QUANTITY = re.compile(r'\bbetween\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:and|&)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))')
# BETWEEN_NUM_AND_NUM = re.compile(r'\bbetween\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:and|&)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))')
# BETWEEN_NUM_AND_NUM = re.compile(r'\bbetween\b\s*((?:\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(?:\d*\s*/\s*\d+|\d+))')
# BETWEEN_NUM_AND_NUM = re.compile(r'between\s+(\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(\d*\s*/\s*\d+|\d+)')

# -----------------------------------------------------------------------------
# --------------------------- Fraction specific PATTERNS -----------------------
# Regular expressions for fraction specific pattern matching tasks
# Patterns to match:
# - General fraction match
# - match fraction parts in a string
# - match multi-part fractions in a string
# - match multi-part fractions with "and" or "&" in between the numbers
# - match whole numbers and fractions
# - match a number followed by a space and then a word and then a number or a fraction
# -----------------------------------------------------------------------------

# Regex pattern for fraction parts, finds all the fraction parts in a string (e.g. 1/2, 1/4, 3/4). 
# A number followed by 0+ white space characters followed by a number then a forward slash then another number.
FRACTION_PATTERN = re.compile(r'\d*\s*/\s*\d+')

# Regex for splititng whole numbers and fractions e.g. 1 1/2 -> ["1", "1/2"]
# TODO: extend this to include decimals as well
SPLIT_INTS_AND_FRACTIONS = re.compile(r'^(\d+(?:/\d+|\.\d+)?)\s+(\d+(?:/\d+|\.\d+)?)$')
# SPLIT_INTS_AND_FRACTIONS = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')
# SPLIT_INTS_AND_FRACTIONS = re.compile(r'^(\d+)\s+(\d+(?:/\d+|\.\d+)?)$')

# Regex for capturing and splitting whitespace seperated numbers/decimals/fractions 
# (e.g. 1 1/2 -> ["1", "1/2"], "2 2.3 -> ["2", "2.3"])
SPLIT_SPACED_NUMS   = re.compile(r'^(\d+(?:/\d+|\.\d+)?)\s+(\d+(?:/\d+|\.\d+)?)$')
# NUMS_SPLIT_BY_SPACES = re.compile(r'^(\d+(?:/\d+|\.\d+)?)\s+(\d+(?:/\d+|\.\d+)?)$')

# -----------------------------------------------------------------------------
# --------------------------- DEPRECATED fraction specific patterns ---------
# -----------------------------------------------------------------------------
# Regex pattern for fraction parts.
# Matches 0+ numbers followed by 0+ white space characters followed by a number then
# a forward slash then another number.
MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)") # (Deprecated, replaced by AND_SEP_NUMBERS)
# MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*\d/\d+)")

# Updated regex pattern for multi-part fractions that includes "and" or "&" in between the numbers
MULTI_PART_FRACTIONS_PATTERN_AND = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)")

# TODO: Specific situation that seems to come up primarily in volume measurements where a whole number is followed
# TODO: by a space then a fraction then a space then a unit (e.g. 1 1/2 cups) which is equivalent to 1.5 cups and NOT 0.5 cups
# TODO: Using a specific "VOLUME_UNITS" dictionary to match these specific cases by the following pattern:
# TODO: <number> <1+ spaces> <fraction> <0+ spaces> <units from VOLUME_UNITS dictionary>
# MIXED_FRACTION_FOR_VOLUME_PATTERN = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)+\s*(?:\d+/\d+|\d+\.\d+)\b')

# -----------------------------------------------------------------------------
# --------------------------- Repeated strings PATTERNS -----------------------
# Patterns to match specific cases when a known unit string is repeated in a string
# This is typically seen in ranges where the unit appears after both quantities (e.g. 100 g - 200 g)
# These regular expressions are used for removing the unit from the string if its repeated
# -----------------------------------------------------------------------------

# Regex pattern to match hypen seperated numbers/decimals/fractions followed by a unit
REPEAT_UNIT_RANGES = re.compile(r'(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)\s*-\s*(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)')
# REPEAT_UNIT_RANGES = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')

# -----------------------------------------------------------------------------
# --------------------------- Misc. patterns -----------------------------
# Patterns for converting: 
# - Pattern for finding consecutive letters and digits in a string so whitespace can be added
# -----------------------------------------------------------------------------
CONSECUTIVE_LETTERS_DIGITS = re.compile(r'([a-zA-Z]+)(\d+)|(\d+)([a-zA-Z]+)')

# -----------------------------------------------------------------------------
# --------------------------- Class to store all regex patterns -----------------------
# A class to hold all regex patterns used in the recipe parser (version 2)
# - Each pattern is stored as a class attribute and the class 
# - RecipeRegexPatterns class has a single method that applies ALL of the 
#     regex patterns to a given string and return a dictionary of matches (for testing mainly)
# -----------------------------------------------------------------------------
# regex variables and maps to put in the class:

class RecipeRegexPatterns:
    """
    A class to hold all regex patterns used in recipe parsing.
    """

    def __init__(self) -> None:
        # Constant data values and lookup tables
        self.constants = {
            "NUMBER_WORDS": NUMBER_WORDS,
            "FRACTION_WORDS": FRACTION_WORDS,
            "UNICODE_FRACTIONS": UNICODE_FRACTIONS,
            "UNITS": UNITS,
            "BASIC_UNITS": BASIC_UNITS,
            "VOLUME_UNITS": VOLUME_UNITS,
            "UNITS_SET": UNITS_SET,
            "BASIC_UNITS_SET": BASIC_UNITS_SET,
            "VOLUME_UNITS_SET": VOLUME_UNITS_SET,
            "CASUAL_QUANTITIES": CASUAL_QUANTITIES,
            "UNIT_MODIFIERS": UNIT_MODIFIERS,
            "PREP_WORDS": PREP_WORDS
        }

        # Define regex patterns
        # string numbers to number map
        self.NUMBER_WORDS_REGEX_MAP = NUMBER_WORDS_REGEX_MAP

        # unicode fractions
        self.UNICODE_FRACTIONS_PATTERN = UNICODE_FRACTIONS_PATTERN
        
        # unit matching patterns
        self.UNITS_PATTERN = UNITS_PATTERN
        self.BASIC_UNITS_PATTERN = BASIC_UNITS_PATTERN
        self.VOLUME_UNITS_PATTERN = VOLUME_UNITS_PATTERN

        # unit/number or number/unit matching patterns
        self.ANY_NUMBER_THEN_UNIT = ANY_NUMBER_THEN_UNIT
        self.ANY_NUMBER_THEN_ANYTHING_THEN_UNIT = ANY_NUMBER_THEN_ANYTHING_THEN_UNIT
        self.ANY_UNIT_PATTERN = ANY_UNIT_PATTERN
        self.ANY_NUMBER = ANY_NUMBER
        self.ALL_NUMBERS = ALL_NUMBERS
        self.SPACE_SEP_NUMBERS = SPACE_SEP_NUMBERS
        self.SPACED_NUMS_THEN_VOLUME_UNITS = SPACED_NUMS_THEN_VOLUME_UNITS
        self.ANY_NUMBER_THEN_UNIT_CAPTURE = ANY_NUMBER_THEN_UNIT_CAPTURE
        self.NUMBER_THEN_UNIT_ABBR = NUMBER_THEN_UNIT_ABBR
        self.NUMBER_THEN_UNIT_WORD = NUMBER_THEN_UNIT_WORD

        # range patterns
        self.QUANTITY_DASH_QUANTITY = QUANTITY_DASH_QUANTITY
        self.QUANTITY_RANGE = QUANTITY_RANGE
        self.QUANTITY_TO_OR_QUANTITY = QUANTITY_TO_OR_QUANTITY
        self.BETWEEN_QUANTITY_AND_QUANTITY = BETWEEN_QUANTITY_AND_QUANTITY
        self.WHOLE_NUMBER_DASH_WHOLE_NUMBER = WHOLE_NUMBER_DASH_WHOLE_NUMBER
        self.WHOLE_NUMBER_DASH_DECIMAL = WHOLE_NUMBER_DASH_DECIMAL
        self.WHOLE_NUMBER_DASH_FRACTION = WHOLE_NUMBER_DASH_FRACTION
        self.DECIMAL_DASH_DECIMAL = DECIMAL_DASH_DECIMAL
        self.DECIMAL_DASH_WHOLE_NUMBER = DECIMAL_DASH_WHOLE_NUMBER
        self.DECIMAL_DASH_FRACTION = DECIMAL_DASH_FRACTION
        self.FRACTION_DASH_FRACTION = FRACTION_DASH_FRACTION
        self.FRACTION_DASH_DECIMAL = FRACTION_DASH_DECIMAL
        self.FRACTION_DASH_WHOLE_NUMBER = FRACTION_DASH_WHOLE_NUMBER

        # fraction specific patterns
        self.FRACTION_PATTERN = FRACTION_PATTERN
        self.SPLIT_SPACED_NUMS = SPLIT_SPACED_NUMS
        self.SPLIT_INTS_AND_FRACTIONS = SPLIT_INTS_AND_FRACTIONS
        self.MULTI_PART_FRACTIONS_PATTERN = MULTI_PART_FRACTIONS_PATTERN # Deprecated
        self.MULTI_PART_FRACTIONS_PATTERN_AND = MULTI_PART_FRACTIONS_PATTERN_AND # Deprecated
        
        # repeated unit string patterns
        self.REPEAT_UNIT_RANGES = REPEAT_UNIT_RANGES

        # miscellaneous patterns
        self.CONSECUTIVE_LETTERS_DIGITS = CONSECUTIVE_LETTERS_DIGITS

    def find_matches(self, input_string: str) -> Dict[str, List[Union[str, Tuple[str]]]]:
        """
        Find all matches in the input string for each regex pattern.
        Returns a dictionary with pattern names as keys and corresponding matches as values.
        """

        matches = {}
        for name, pattern in self.__dict__.items():
            if isinstance(pattern, re.Pattern):
                matches[name] = pattern.findall(input_string)
        return matches
    
    def list_attrs(self) -> None:
        """
        List all the attributes of the class.
        """ 

        # attrs = [name for name in self.__dict__]

        for name, pattern in self.__dict__.items():
            print(f"- {name} ({type(self.__dict__[name]).__name__})")
            if isinstance(self.__dict__[name], dict):
                print(f"  > {len(self.__dict__[name])} items")
                # for key, value in self.__dict__[name].items():
                #     print(f"   - {key}")
        # return [name for name in self.__dict__ if isinstance(self.__dict__[name], re.Pattern)]
    
    def get_desc(self, pattern_name: str) -> str:
        """
        Get the description of a specific regex pattern.
        Returns the description of the pattern if found, otherwise returns an empty string.
        """

        # Define descriptions for each pattern
        descriptions = {
            ### Constants and lookup tables
            "NUMBER_WORDS": "Dictionary of number words to numerical values.",
            "FRACTION_WORDS": "Dictionary of fraction words to numerical values.",
            "UNICODE_FRACTIONS": "Dictionary of unicode fractions to numerical values.",

            # dictionaries of units
            "UNITS": "Dictionary of units used in the recipe parser (All units, including basic, volume, and specific units).",
            "BASIC_UNITS": "Dictionary of basic units used in the recipe parser (The most common units).",
            "VOLUME_UNITS": "Dictionary of volume units used in the recipe parser (Units used for measuring volume).",

            # sets of all unit words
            "UNITS_SET": "Set of units used in the recipe parser (All units, including basic, volume, and specific units).",
            "BASIC_UNITS_SET": "Set of basic units used in the recipe parser (The most common units).",
            "VOLUME_UNITS_SET": "Set of volume units used in the recipe parser (Units used for measuring volume).",

            "CASUAL_QUANTITIES": "Dictionary of casual quantities used in the recipe parser.",
            "UNIT_MODIFIERS": "Set of unit modifier words for lookups in recipe parser.",
            "PREP_WORDS": "Set of preparation words for lookups in recipe parser.",
            "NUMBER_WORDS_REGEX_MAP": "Dictionary of regex patterns to match number words in a string (i.e. 'one' : '1', 'two' : '2').",
            
            ### Regex patterns
            "UNICODE_FRACTIONS_PATTERN": "Matches unicode fractions in the string.",
            "UNITS_PATTERN": "Matches units in a string.",
            "BASIC_UNITS_PATTERN": "Matches just the basic units from the BASIC_UNITS dictionary.",
            "VOLUME_UNITS_PATTERN": "Matches specifically volume units in a string.",
            "ANY_NUMBER_THEN_UNIT": "Matches a number followed by a unit.",
            "ANY_NUMBER_THEN_ANYTHING_THEN_UNIT": "Matches a number followed by any text and then a unit.",
            "ANY_UNIT_PATTERN": "Matches any unit.",
            "ANY_NUMBER": "Matches any number/decimal/fraction in a string padded by atleast 1+ whitespaces.",
            "ALL_NUMBERS": "Matches ALL number/decimal/fraction in a string regardless of padding.",
            "SPACE_SEP_NUMBERS": "Matches any number/decimal/fraction followed by a space and then another number/decimal/fraction.",
            "SPACED_NUMS_THEN_VOLUME_UNITS": "Matches a number/decimal/fraction followed by 1+ spaces to another number/decimal/fraction followed by a 0+ spaces then a VOLUME unit.",
            "ANY_NUMBER_THEN_UNIT_CAPTURE": "Matches a number followed by any text and then a unit.",
            "NUMBER_THEN_UNIT_ABBR": "Matches a number followed by a unit abbreviation.",
            "NUMBER_THEN_UNIT_WORD": "Matches a number followed by a unit word (full word string as unit).",
            "QUANTITY_DASH_QUANTITY": "Matches numbers/decimals/fractions followed by a hyphen to numbers/decimals/fractions.",
            "QUANTITY_RANGE": "Matches numbers/decimals/fractions with a hyphen in between them.",
            "QUANTITY_TO_OR_QUANTITY": "Matches numbers/decimals/fractions separated by 'to' or 'or'.",
            "BETWEEN_QUANTITY_AND_QUANTITY": "Matches numbers/decimals/fractions separated by 'between' and 'and'.",
            "WHOLE_NUMBER_DASH_WHOLE_NUMBER": "Matches whole numbers separated by a hyphen.",
            "WHOLE_NUMBER_DASH_DECIMAL": "Matches whole number followed by a decimal separated by a hyphen.",
            "WHOLE_NUMBER_DASH_FRACTION": "Matches whole number followed by a fraction separated by a hyphen.",
            "DECIMAL_DASH_DECIMAL": "Matches decimals separated by a hyphen.",
            "DECIMAL_DASH_WHOLE_NUMBER": "Matches decimal followed by a whole number separated by a hyphen.",
            "DECIMAL_DASH_FRACTION": "Matches decimal followed by a fraction separated by a hyphen.",
            "FRACTION_DASH_FRACTION": "Matches fractions separated by a hyphen.",
            "FRACTION_DASH_DECIMAL": "Matches fraction followed by a decimal separated by a hyphen.",
            "FRACTION_DASH_WHOLE_NUMBER": "Matches fraction followed by a whole number separated by a hyphen.",
            "FRACTION_PATTERN": "Matches fraction parts in a string.",
            "SPLIT_SPACED_NUMS": "Splits numbers/decimals/fractions separated by 1+ whitespaces into a capture group (i.e '1.5 1/2' -> ['1.5', '1/2']).",
            "SPLIT_INTS_AND_FRACTIONS": "Splits whole numbers and fractions separated by 1+ whitespaces into a capture group (i.e '1 1/2' -> ['1', '1/2']). (Deprecated)",
            "MULTI_PART_FRACTIONS_PATTERN": "Matches multi-part fractions in a string. (Deprecated)",
            "MULTI_PART_FRACTIONS_PATTERN_AND": "Matches multi-part fractions with 'and' or '&' in between the numbers. (Deprecated)",
            "REPEAT_UNIT_RANGES": "Matches repeated unit strings in a string.",
            "CONSECUTIVE_LETTERS_DIGITS": "Matches consecutive letters and digits in a string.",
        }

        # Retrieve description based on pattern name
        return descriptions.get(pattern_name, "")


# # -----------------------------------------------------------------------------
# # --------------------------- TESTING PATTERNS -----------------------
# # -----------------------------------------------------------------------------

# # test any quantity range pattern
# input_string = "This is a test string with 1.5 -2/5 oz range." 
# re.findall(QUANTITY_DASH_QUANTITY, input_string) # ['1.5 -2/5']
# input_string = "This is a test string with 1- 2.5 oz range."
# re.findall(QUANTITY_DASH_QUANTITY, input_string) # ['1- 2.5']
# input_string = "This is a test string with 1-2.5 oz range."
# re.findall(QUANTITY_DASH_QUANTITY, input_string) # ['1-2.5']

# # match situation where there is a number followed by a space and then a word and then a number or a fraction
# QUANTITY_WORD = re.compile(r"(\d+\s\w+\s\d+/\d+|\d+\s\w+)")

# # test quantity word pattern
# input_string = "This is a test string with 3 tbsp of sugar."
# re.findall(QUANTITY_WORD, input_string)
# input_string = "This is a test string with 3 1/2 tbsp of sugar."
# re.findall(QUANTITY_WORD, input_string) # ['3 1/2 tbsp']

# # # Regular expressions
# # WHOLE_NUMBER_DASH_WHOLE_NUMBER = re.compile(r"(\d+)\s*-\s*(\d+)")
# # WHOLE_NUMBER_DASH_DECIMAL = re.compile(r"(\d+)\s*-\s*(\d+\.\d+)")
# # WHOLE_NUMBER_DASH_FRACTION = re.compile(r"(\d+)\s*-\s*(\d+/\d+)")
# # DECIMAL_DASH_DECIMAL = re.compile(r"(\d+\.\d+)\s*-\s*(\d+\.\d+)")
# # DECIMAL_DASH_WHOLE_NUMBER = re.compile(r"(\d+\.\d+)\s*-\s*(\d+)")
# # DECIMAL_DASH_FRACTION = re.compile(r"(\d+\.\d+)\s*-\s*(\d+/\d+)")
# # FRACTION_DASH_FRACTION = re.compile(r"(\d+/\d+)\s*-\s*(\d+/\d+)")
# # FRACTION_DASH_DECIMAL = re.compile(r"(\d+/\d+)\s*-\s*(\d+\.\d+)")
# # FRACTION_DASH_WHOLE_NUMBER = re.compile(r"(\d+/\d+)\s*-\s*(\d+)")

# # # Regular expressions
# # WHOLE_NUMBER_DASH_WHOLE_NUMBER = re.compile(r"\d+\s*-\s*\d+")
# # WHOLE_NUMBER_DASH_DECIMAL = re.compile(r"\d+\s*-\s*\d+\.\d+")
# # WHOLE_NUMBER_DASH_FRACTION = re.compile(r"\d+\s*-\s*\d+/\d+")
# # DECIMAL_DASH_DECIMAL = re.compile(r"\d+\.\d+\s*-\s*\d+\.\d+")
# # DECIMAL_DASH_WHOLE_NUMBER = re.compile(r"\d+\.\d+\s*-\s*\d+")
# # DECIMAL_DASH_FRACTION = re.compile(r"\d+\.\d+\s*-\s*\d+/\d+")
# # FRACTION_DASH_FRACTION = re.compile(r"\d+/\d+\s*-\s*\d+/\d+")
# # FRACTION_DASH_DECIMAL = re.compile(r"\d+/\d+\s*-\s*\d+\.\d+")
# # FRACTION_DASH_WHOLE_NUMBER = re.compile(r"\d+/\d+\s*-\s*\d+")

# # Test cases
# test_cases = [
#     "This is a test string with 1.5 -2/5 oz range.",
#     "This is a test string with 1- 2.5 oz range.",
#     "This is a test string with 1-2.5 oz range.",
#     "This is a test string with 1.5-2.75 oz range.",
#     "This is a test string with 2/3 -3/4 oz range.",
#     "This is a test string with 2/3 -4.5 oz range.",
#     "This is a test string with 2/3 -4 oz range.",
#     "This is a test string with 5/6 or 3 oz range.",
#     "This is a test string with between 5/6 & 3 oz range.",
#     "This is a test string with between 5/6 and 3 oz range.",
#     "This is a test string with 5/6 -3 oz range.",
#     "This is a test string with 2.5 -3/4 oz range.",
#     "This is a test string with 2.5 -4 oz range.",
# ]

# # Run tests
# for i, test in enumerate(test_cases, 1):
#     print(f"Test Case {i}: \n > '{test}'")
#     print(f"ANY quantity Range: {re.findall(QUANTITY_DASH_QUANTITY, test)}")
#     print(f"OLD quantity Range: {re.findall(QUANTITY_RANGE, test)}")
#     print("Whole Number - Whole Number:", re.findall(WHOLE_NUMBER_DASH_WHOLE_NUMBER, test))
#     print("Whole Number - Decimal:", re.findall(WHOLE_NUMBER_DASH_DECIMAL, test))
#     print("Whole Number - Fraction:", re.findall(WHOLE_NUMBER_DASH_FRACTION, test))
#     print("Decimal - Decimal:", re.findall(DECIMAL_DASH_DECIMAL, test))
#     print("Decimal - Whole Number:", re.findall(DECIMAL_DASH_WHOLE_NUMBER, test))
#     print("Decimal - Fraction:", re.findall(DECIMAL_DASH_FRACTION, test))
#     print("Fraction - Fraction:", re.findall(FRACTION_DASH_FRACTION, test))
#     print("Fraction - Decimal:", re.findall(FRACTION_DASH_DECIMAL, test))
#     print("Fraction - Whole Number:", re.findall(FRACTION_DASH_WHOLE_NUMBER, test))
#     print(f"BETWEEN quantity and quantity: {re.findall(BETWEEN_QUANTITY_AND_QUANTITY, test)}")
#     print(f"QUANTITY TO OR QUANTITY: {re.findall(QUANTITY_TO_OR_QUANTITY, test)}")
#     print("-" * 50)

# NUMBER_WORDS_REGEX_MAP
# UNICODE_FRACTIONS
# FRACTION_PATTERN
# QUANTITY_RANGE_PATTERN
# BETWEEN_NUM_AND_NUM_PATTERN
# RANGE_WITH_TO_OR_PATTERN
# MULTI_PART_FRACTIONS_PATTERN
    

# -----------------------------------------------------------------------------
# --------------------------- OLD CODE BELOW -----------------------
# -----------------------------------------------------------------------------

# # Description: This module contains all the regex patterns used in the recipe parser. 
# # As well as a class to hold all regex patterns used in the recipe parser.

# import re
# from typing import Dict, List, Tuple, Union

# # import lambda_containers.extract_ingredients.parser.static_values
# from lambda_containers.extract_ingredients.parser.static_values import NUMBER_WORDS, NUMBER_WORDS_REGEX_MAP, UNICODE_FRACTIONS, UNICODE_FRACTIONS_PATTERN, UNITS, UNITS_PATTERN, ANY_NUMBER_THEN_UNIT_PATTERN, UNIT_THEN_ANY_NUMBER_PATTERN
# # import static_values modules
# # from . import static_values
# from .static_values import NUMBER_WORDS, NUMBER_WORDS_REGEX_MAP, UNICODE_FRACTIONS, UNITS, UNITS_PATTERN, ANY_NUMBER_THEN_UNIT_PATTERN, UNIT_THEN_ANY_NUMBER_PATTERN

# # Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# # Step 2: Replace numbers with words with their numerical equivalents
# # Step 3: Replace all unicode fractions with their decimal equivalents
# # Step 4: Replace all fractions with their decimal equivalents
# # Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# # Step 6: Seperate any part of the string that is wrapped in PARENTHESES and treat this as its own string

# # Can you extend this regex so that it is able to select whole numbers, decimal values and fractions seperated by a hypen. Right now it is able to match whole numbers and decimals but it is not able to extract fractions correctly? 
# # # matches numbers/decimal nubmers with a hyphen in between the numbers and 0 or more white spaces
# # QUANTITY_RANGE_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*(?:\s*-\s*)+\d+(?:\.\d+)?") #  matches numbers AND decimals with a hyphen in between them

# # string_with_whole_numbers_range = f"""1-2 3-4"""
# # re.findall(QUANTITY_RANGE_PATTERN, string_with_whole_numbers_range) # correctly parses to ['1-2', '3-4']

# # string_with_fractions_range = f"""¼ cup packed 1/2 - 12/16 brown sugar tbsp."""
# # re.findall(QUANTITY_RANGE_PATTERN, string_with_fractions_range) # incorrectly ['2 - 12'] but should be ['1/2 - 12/16']

# # string_with_decimal_range = f"""1.5 - 2.5  kg of sugar"""
# # re.findall(QUANTITY_RANGE_PATTERN, string_with_decimal_range) # correctly parses to ['1.5 - 2.5']

# # # QUANTITY_RANGE: ['2 - 12']
# # QUANTITY_RANGE_PATTERN = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")

# # string_with_whole_numbers_range = "1-2 3-4"
# # print(re.findall(QUANTITY_RANGE_PATTERN, string_with_whole_numbers_range))  # ['1-2', '3-4']

# # string_with_fractions_range = "¼ cup packed 1/2 - 12/16 brown sugar tbsp."
# # print(re.findall(QUANTITY_RANGE_PATTERN, string_with_fractions_range))  # ['1/2 - 12/16']

# # string_with_decimal_range = "1.5 - 2.5 kg of sugar"
# # print(re.findall(QUANTITY_RANGE_PATTERN, string_with_decimal_range)) 

# # matches numbers/decimal nubmers with a hyphen in between the numbers and 0 or more white spaces
# QUANTITY_RANGE_PATTERN = re.compile(r"\d+(?:\.\d+)?\s*(?:\s*-\s*)+\d+(?:\.\d+)?") #  matches numbers AND decimals with a hyphen in between them
# # QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*(?:\s*-\s*)+\d+") #  matches numbers with a hyphen in between them (only whole numbers seperated by hypens)

# # matches numbers/decimals/fractions with a hyphen in between the numbers/decimals/fractions and 0 or more white spaces
# ANY_QUANTITY_RANGE_PATTERN = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")

# # match situation where there is a number followed by a space and then a word and then a number or a fraction
# QUANTITY_WORD_PATTERN = re.compile(r"(\d+\s\w+\s\d+/\d+|\d+\s\w+)")

# # Regex pattern for fraction parts, finds all the fraction parts in a string (e.g. 1/2, 1/4, 3/4). 
# # A number followed by 0+ white space characters followed by a number then a forward slash then another number.
# FRACTION_PATTERN = re.compile(r'\d*\s*/\s*\d+')

# # Regex pattern for fraction parts.
# # Matches 0+ numbers followed by 0+ white space characters followed by a number then
# # a forward slash then another number.
# MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*\d/\d+)")

# # Updated regex pattern for multi-part fractions that includes "and" or "&" in between the numbers
# MULTI_PART_FRACTIONS_PATTERN_AND = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)")

# # Updated regex pattern for multi-part fractions
# MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)")

# # Regex for splititng whole numbers and fractions e.g. 1 1/2 -> ["1", "1/2"]
# SPLIT_INTS_AND_FRACTIONS_PATTERN = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')

# # Match pattern where there is a number followed by 0+ spaces and then another number or a fraction
# NUM_SPACE_FRACTION_PATTERN = re.compile(r'\d+\s+\d*\s*/\s*\d+')

# # match pattern where there is a number followed by a space and then a word and or a "&" then a number or a fraction
# NUM_AND_FRACTION_PATTERN = re.compile(r'\d+\s+(?:and|&)\s+\d*\s*/\s*\d+')

# # match pattern where there is a number followed by a space and then a word and or a "to" then a NUMBER or a FRACTION or a DECIMAL
# RANGE_WITH_TO_OR_PATTERN = re.compile(r'\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:to|or)\s*(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))') # Works for if there is NO space between the number and the words "to" or "or" for either the first or second numbers
# # RANGE_WITH_TO_OR_PATTERN = re.compile(r'\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:to|or)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))') # requires a space between the number and the word and or the "to" or "or" and the number,fraction, or decimal

# # Regex pattern for matching "between" followed by a number or a fraction, then "and" or "&", 
# # and then another NUMBER or a FRACTION or a DECIMAL
# BETWEEN_NUM_AND_NUM_PATTERN = re.compile(r'\bbetween\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:and|&)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))')
# # BETWEEN_NUM_AND_NUM_PATTERN = re.compile(r'\bbetween\b\s*((?:\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(?:\d*\s*/\s*\d+|\d+))')
# # BETWEEN_NUM_AND_NUM_PATTERN = re.compile(r'between\s+(\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(\d*\s*/\s*\d+|\d+)')

# # Regex to match number (QUANTITY) then unit abbreviation (single string as unit)
# QUANTITY_THEN_UNIT_ABBR_PATTERN = re.compile(r"(\d)\-?([a-zA-Z])") # 3g = 3 g

# # Regex to match number (QUANTITY) then unit word (single string as unit)
# QUANTITY_THEN_UNIT_WORD_PATTERN = re.compile(r"(\d+)\-?([a-zA-Z]+)") #  "3tbsp vegetable oil" = 3 tbsp

# # Match various patterns of units followed by a quantity
# # - unit-quantity (e.g. 3-grams)
# # - unit, quantity (e.g. 3,grams)
# # - unit/quantity (e.g. 3/grams)
# # - unit(quantity (e.g. 3(grams)
# UNITS_HYPHEN_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)-(\d+)")
# UNITS_COMMA_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+),(\d+)")
# UNITS_SLASH_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)/(\d+)")
# UNITS_PARENTHESES_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)\((\d+)")

# # Regex pattern to match ranges where the unit appears after both quantities e.g.
# # 100 g - 200 g. This assumes the quantites and units have already been seperated
# # by a single space and that all number are decimals.
# # This regex matches: <quantity> <unit> - <quantity> <unit>, returning
# # the full match and each quantity and unit as capture groups.
# DUPE_UNIT_RANGES_PATTERN = re.compile(
#     r"(([\d\.]+)\s([a-zA-Z]+)\s\-\s([\d\.]+)\s([a-zA-Z]+))", re.I
# )

# REPEAT_UNIT_RANGES_PATTERN = re.compile(r'(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)\s*-\s*(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)')
# # REPEAT_UNIT_RANGES_PATTERN = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')

# # tmp = "1oz-2oz of cheese" # [('1', 'oz', '2', 'oz')]
# # tmp2 = "1oz-2.5oz of sugar" # []
# # REPEAT_UNIT_RANGES_PATTERN = re.compile(r'(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)\s*-\s*(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)')

# # # Test cases
# # tmp = "1oz-2oz of cheese"  # [('1', 'oz', '2', 'oz')]
# # tmp2 = "1oz -2.5oz of sugar"  # [('1', 'oz', '2.5', 'oz')]
# # tmp3 = "1/2oz-3oz of sugar"  # [('1/2', 'oz', '3', 'oz')]

# # matches_tmp = REPEAT_UNIT_RANGES_PATTERN.findall(tmp)
# # matches_tmp2 = REPEAT_UNIT_RANGES_PATTERN.findall(tmp2)
# # matches_tmp3 = REPEAT_UNIT_RANGES_PATTERN.findall(tmp3)

# # print(matches_tmp)
# # print(matches_tmp2)
# # print(matches_tmp3)
# # Regex pattern to match a decimal number followed by an "x" followed by a space
# # e.g. 0.5 x, 1 x, 2 x. The number is captured in a capture group.
# QUANTITY_X_PATTERN = re.compile(r"([\d\.]+)\s[xX]\s*")

# # List of tuples containing variable name and corresponding compiled regex pattern
# pattern_list = [
#     ('UNITS', UNITS),
#     ('UNITS_PATTERN', UNITS_PATTERN),
#     # ('SINGLE_NUMBER_THEN_UNIT_PATTERN', SINGLE_NUMBER_THEN_UNIT_PATTERN),
#     ('UNICODE_FRACTIONS', UNICODE_FRACTIONS),
#     ('UNICODE_FRACTIONS_PATTERN', UNICODE_FRACTIONS_PATTERN),
#     ('NUMBER_WORDS_REGEX_MAP', NUMBER_WORDS_REGEX_MAP),            
#     ('ANY_NUMBER_THEN_UNIT_PATTERN', ANY_NUMBER_THEN_UNIT_PATTERN),
#     ('UNIT_THEN_ANY_NUMBER_PATTERN', UNIT_THEN_ANY_NUMBER_PATTERN),
#     ('QUANTITY_RANGE_PATTERN', QUANTITY_RANGE_PATTERN),
#     ('ANY_QUANTITY_RANGE_PATTERN', ANY_QUANTITY_RANGE_PATTERN),
#     ('QUANTITY_WORD_PATTERN', QUANTITY_WORD_PATTERN),
#     ('FRACTION_PATTERN', FRACTION_PATTERN),
#     ('MULTI_PART_FRACTIONS_PATTERN', MULTI_PART_FRACTIONS_PATTERN),
#     ('NUM_SPACE_FRACTION_PATTERN', NUM_SPACE_FRACTION_PATTERN),
#     ('MULTI_PART_FRACTIONS_PATTERN_AND', MULTI_PART_FRACTIONS_PATTERN_AND),
#     ('NUM_AND_FRACTION_PATTERN', NUM_AND_FRACTION_PATTERN),
#     ('RANGE_WITH_TO_OR_PATTERN', RANGE_WITH_TO_OR_PATTERN),
#     ('BETWEEN_NUM_AND_NUM_PATTERN', BETWEEN_NUM_AND_NUM_PATTERN),
#     ('QUANTITY_THEN_UNIT_ABBR_PATTERN', QUANTITY_THEN_UNIT_ABBR_PATTERN),
#     ('QUANTITY_THEN_UNIT_WORD_PATTERN', QUANTITY_THEN_UNIT_WORD_PATTERN),
#     ('UNITS_HYPHEN_QUANTITY_PATTERN', UNITS_HYPHEN_QUANTITY_PATTERN),
#     ('UNITS_COMMA_QUANTITY_PATTERN', UNITS_COMMA_QUANTITY_PATTERN),
#     ('UNITS_SLASH_QUANTITY_PATTERN', UNITS_SLASH_QUANTITY_PATTERN),
#     ('UNITS_PARENTHESES_QUANTITY_PATTERN', UNITS_PARENTHESES_QUANTITY_PATTERN),
# ]

# class RegexPatterns:
#     """
#     A class to hold all regex patterns used in the recipe parser.
#     Args:
#         patterns: a list of tuples containing variable name and corresponding compiled regex pattern
#     """
#     def __init__(self, patterns: List[Tuple[str, str]] = pattern_list) -> None:
#         self.patterns = {}
#         self._create_patterns(patterns)

#     def _create_patterns(self, patterns: List[Tuple[str, str]]) -> None:
#         """
#         Create instance variables for each regex pattern.
#         """
#         for name, pattern in patterns:
#             setattr(self, name, pattern)
#             self.patterns[name] = getattr(self, name)
    
#     def find_matches(self, input_string: str) -> Dict[str, List[Union[str, Tuple[str]]]]:

#         """
#         Find all matches in the input string for each regex pattern.
#         Returns a dictionary with pattern names as keys and corresponding matches as values.
#         """
#         matches = {}
#         for name, pattern in self.patterns.items():
#             matches[name] = re.findall(pattern, input_string)
#         return matches

# class RecipeRegexPatterns:
#     """
#     A class to hold all regex patterns used in recipe parsing.
#     """

#     def __init__(self) -> None:
#         # Define regex patterns
#         self.UNITS = UNITS
#         self.UNITS_PATTERN = UNITS_PATTERN
#         self.UNICODE_FRACTIONS = UNICODE_FRACTIONS
#         self.UNICODE_FRACTIONS_PATTERN = UNICODE_FRACTIONS_PATTERN
#         self.ANY_NUMBER_THEN_UNIT_PATTERN = ANY_NUMBER_THEN_UNIT_PATTERN
#         self.UNIT_THEN_ANY_NUMBER_PATTERN = UNIT_THEN_ANY_NUMBER_PATTERN
#         self.NUMBER_WORDS_REGEX_MAP = NUMBER_WORDS_REGEX_MAP
#         self.QUANTITY_RANGE = re.compile(r"\d+(?:\.\d+)?\s*(?:\s*-\s*)+\d+(?:\.\d+)?")
#         self.ANY_QUANTITY_RANGE = re.compile(r"\d+(?:/\d+|\.\d+)?\s*-\s*\d+(?:/\d+|\.\d+)?")
#         self.QUANTITY_WORD = re.compile(r"(\d+\s\w+\s\d+/\d+|\d+\s\w+)")
#         self.FRACTION = re.compile(r'\d*\s*/\s*\d+')
#         self.MULTI_PART_FRACTIONS = re.compile(r"(\d*\s*\d/\d+)")
#         self.NUM_SPACE_FRACTION = re.compile(r'\d+\s+\d*\s*/\s*\d+')
#         self.NUM_AND_FRACTION = re.compile(r'\d+\s+(?:and|&)\s+\d*\s*/\s*\d+')
#         self.RANGE_WITH_TO_OR = re.compile(r'\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?:to|or)\s*(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))')
#         self.BETWEEN_NUM_AND_NUM = re.compile(r'\bbetween\b\s*((?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?)\s+(?:and|&)\s+(?:\d+(?:\.\d+)?\s*(?:/)?\s*\d+(?:\.\d+)?|\d+(?:\.\d+)?))')
#         self.QUANTITY_THEN_UNIT_ABBR = re.compile(r"(\d)\-?([a-zA-Z])")
#         self.QUANTITY_THEN_UNIT_WORD = re.compile(r"(\d+)\-?([a-zA-Z]+)")
#         self.UNITS_HYPHEN_QUANTITY = re.compile(r"([a-zA-Z]+)-(\d+)")
#         self.UNITS_COMMA_QUANTITY = re.compile(r"([a-zA-Z]+),(\d+)")
#         self.UNITS_SLASH_QUANTITY = re.compile(r"([a-zA-Z]+)/(\d+)")
#         self.UNITS_PARENTHESES_QUANTITY = re.compile(r"([a-zA-Z]+)\((\d+)")
#         self.DUPE_UNIT_RANGES = re.compile(r"(([\d\.]+)\s([a-zA-Z]+)\s\-\s([\d\.]+)\s([a-zA-Z]+))", re.I)
#         self.REPEAT_UNIT_RANGES = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')
#         self.QUANTITY_X = re.compile(r"([\d\.]+)\s[xX]\s*")

#     def find_matches(self, input_string: str) -> Dict[str, List[Union[str, Tuple[str]]]]:
#         """
#         Find all matches in the input string for each regex pattern.
#         Returns a dictionary with pattern names as keys and corresponding matches as values.
#         """

#         matches = {}
#         for name, pattern in self.__dict__.items():
#             if isinstance(pattern, re.Pattern):
#                 matches[name] = pattern.findall(input_string)
#         return matches
