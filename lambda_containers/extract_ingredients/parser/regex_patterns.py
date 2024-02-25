# Description: This module contains all the regex patterns used in the recipe parser. 
# As well as a class to hold all regex patterns used in the recipe parser.

import re
from typing import Dict, List, Tuple, Union

# import lambda_containers.extract_ingredients.parser.static_values
from lambda_containers.extract_ingredients.parser.static_values import NUMBER_WORDS, NUMBER_WORDS_REGEX_MAP, UNICODE_FRACTIONS, UNITS, UNITS_PATTERN, ANY_NUMBER_THEN_UNIT_PATTERN, UNIT_THEN_ANY_NUMBER_PATTERN

# Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# Step 2: Replace numbers with words with their numerical equivalents
# Step 3: Replace all unicode fractions with their decimal equivalents
# Step 4: Replace all fractions with their decimal equivalents
# Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# Step 6: Seperate any part of the string that is wrapped in PARENTHESES and treat this as its own string

# matches numbers with a hyphen in between them]
QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*(?:\s*-\s*)+\d+")
# QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*-\s*\d+")
# QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*[\-]\d+")

# match situation where there is a number followed by a space and then a word and then a number or a fraction
QUANTITY_WORD_PATTERN = re.compile(r"(\d+\s\w+\s\d+/\d+|\d+\s\w+)")

# Regex pattern for fraction parts, finds all the fraction parts in a string (e.g. 1/2, 1/4, 3/4). 
# A number followed by 0+ white space characters followed by a number then a forward slash then another number.
FRACTION_PATTERN = re.compile(r'\d*\s*/\s*\d+')

# Regex pattern for fraction parts.
# Matches 0+ numbers followed by 0+ white space characters followed by a number then
# a forward slash then another number.
MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*\d/\d+)")

# Updated regex pattern for multi-part fractions that includes "and" or "&" in between the numbers
MULTI_PART_FRACTIONS_PATTERN_AND = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)")

# Updated regex pattern for multi-part fractions
MULTI_PART_FRACTIONS_PATTERN = re.compile(r"(\d*\s*(?:and|&)?\s*\d/\d+)")

# Match pattern where there is a number followed by 0+ spaces and then another number or a fraction
NUM_SPACE_FRACTION_PATTERN = re.compile(r'\d+\s+\d*\s*/\s*\d+')

# match pattern where there is a number followed by a space and then a word and or a "&" then a number or a fraction
NUM_AND_FRACTION_PATTERN = re.compile(r'\d+\s+(?:and|&)\s+\d*\s*/\s*\d+')

# match pattern where there is a number followed by a space and then a word and or a "to" then a number or a fraction
RANGE_WITH_TO_OR_PATTERN = re.compile(r'\b\s*((?:\d*\s*/\s*\d+|\d+)\s+(?:to|or)\s+(?:\d*\s*/\s*\d+|\d+))')
# RANGE_WITH_TO_OR_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:-\s*|\b(?:to|or)\s+)\s*(\d+(?:\.\d+)?)')
# RANGE_WITH_TO_OR_PATTERN2 = re.compile(r'\b\s*((?:\d*\s*/\s*\d+|\d+)\s+(?:to|or)\s+(?:\d*\s*/\s*\d+|\d+))')

# Regex pattern for matching "between" followed by a number or a fraction, then "and" or "&", 
# and then another number or a fraction
BETWEEN_NUM_AND_NUM_PATTERN = re.compile(r'\bbetween\b\s*((?:\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(?:\d*\s*/\s*\d+|\d+))')
# BETWEEN_NUM_AND_NUM_PATTERN = re.compile(r'between\s+(\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(\d*\s*/\s*\d+|\d+)')

# tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 -- 45 inches, cats do between 1 and 5 digs'

# Regex to match number (QUANTITY) then unit abbreviation (single string as unit)
QUANTITY_THEN_UNIT_ABBR_PATTERN = re.compile(r"(\d)\-?([a-zA-Z])") # 3g = 3 g

# Regex to match number (QUANTITY) then unit word (single string as unit)
QUANTITY_THEN_UNIT_WORD_PATTERN = re.compile(r"(\d+)\-?([a-zA-Z]+)") #  "3tbsp vegetable oil" = 3 tbsp

# Match various patterns of units followed by a quantity
# - unit-quantity (e.g. 3-grams)
# - unit, quantity (e.g. 3,grams)
# - unit/quantity (e.g. 3/grams)
# - unit(quantity (e.g. 3(grams)
UNITS_HYPHEN_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)-(\d+)")
UNITS_COMMA_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+),(\d+)")
UNITS_SLASH_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)/(\d+)")
UNITS_PARENTHESES_QUANTITY_PATTERN = re.compile(r"([a-zA-Z]+)\((\d+)")

# Regex pattern to match ranges where the unit appears after both quantities e.g.
# 100 g - 200 g. This assumes the quantites and units have already been seperated
# by a single space and that all number are decimals.
# This regex matches: <quantity> <unit> - <quantity> <unit>, returning
# the full match and each quantity and unit as capture groups.
DUPE_UNIT_RANGES_PATTERN = re.compile(
    r"(([\d\.]+)\s([a-zA-Z]+)\s\-\s([\d\.]+)\s([a-zA-Z]+))", re.I
)

# Regex pattern to match a decimal number followed by an "x" followed by a space
# e.g. 0.5 x, 1 x, 2 x. The number is captured in a capture group.
QUANTITY_X_PATTERN = re.compile(r"([\d\.]+)\s[xX]\s*")

# List of tuples containing variable name and corresponding compiled regex pattern
pattern_list = [
    ('UNITS', UNITS),
    ('UNITS_PATTERN', UNITS_PATTERN),
    # ('SINGLE_NUMBER_THEN_UNIT_PATTERN', SINGLE_NUMBER_THEN_UNIT_PATTERN),
    ('UNICODE_FRACTIONS', UNICODE_FRACTIONS),
    ('NUMBER_WORDS_REGEX_MAP', NUMBER_WORDS_REGEX_MAP),            
    ('ANY_NUMBER_THEN_UNIT_PATTERN', ANY_NUMBER_THEN_UNIT_PATTERN),
    ('UNIT_THEN_ANY_NUMBER_PATTERN', UNIT_THEN_ANY_NUMBER_PATTERN),
    ('QUANTITY_RANGE_PATTERN', QUANTITY_RANGE_PATTERN),
    ('QUANTITY_WORD_PATTERN', QUANTITY_WORD_PATTERN),
    ('FRACTION_PATTERN', FRACTION_PATTERN),
    ('MULTI_PART_FRACTIONS_PATTERN', MULTI_PART_FRACTIONS_PATTERN),
    ('NUM_SPACE_FRACTION_PATTERN', NUM_SPACE_FRACTION_PATTERN),
    ('MULTI_PART_FRACTIONS_PATTERN_AND', MULTI_PART_FRACTIONS_PATTERN_AND),
    ('NUM_AND_FRACTION_PATTERN', NUM_AND_FRACTION_PATTERN),
    ('RANGE_WITH_TO_OR_PATTERN', RANGE_WITH_TO_OR_PATTERN),
    ('BETWEEN_NUM_AND_NUM_PATTERN', BETWEEN_NUM_AND_NUM_PATTERN),
    ('QUANTITY_THEN_UNIT_ABBR_PATTERN', QUANTITY_THEN_UNIT_ABBR_PATTERN),
    ('QUANTITY_THEN_UNIT_WORD_PATTERN', QUANTITY_THEN_UNIT_WORD_PATTERN),
    ('UNITS_HYPHEN_QUANTITY_PATTERN', UNITS_HYPHEN_QUANTITY_PATTERN),
    ('UNITS_COMMA_QUANTITY_PATTERN', UNITS_COMMA_QUANTITY_PATTERN),
    ('UNITS_SLASH_QUANTITY_PATTERN', UNITS_SLASH_QUANTITY_PATTERN),
    ('UNITS_PARENTHESES_QUANTITY_PATTERN', UNITS_PARENTHESES_QUANTITY_PATTERN),
]

class RegexPatterns:
    """
    A class to hold all regex patterns used in the recipe parser.
    Args:
        patterns: a list of tuples containing variable name and corresponding compiled regex pattern
    """
    def __init__(self, patterns: List[Tuple[str, str]]) -> None:
        self.patterns = {}
        self._create_patterns(patterns)

    def _create_patterns(self, patterns: List[Tuple[str, str]]) -> None:
        """
        Create instance variables for each regex pattern.
        """
        for name, pattern in patterns:
            setattr(self, name, pattern)
            self.patterns[name] = getattr(self, name)
    
    def find_matches(self, input_string: str) -> Dict[str, List[Union[str, Tuple[str]]]]:

        """
        Find all matches in the input string for each regex pattern.
        Returns a dictionary with pattern names as keys and corresponding matches as values.
        """
        matches = {}
        for name, pattern in self.patterns.items():
            matches[name] = re.findall(pattern, input_string)
        return matches
    
# # Instantiate the RegexPatterns class with the list of patterns
# regex_patterns = RegexPatterns(pattern_list)
# regex_pat = RegexPatterns(pattern_list)

# for name, pattern in regex_patterns.patterns.items():
#     print(f"Pattern name: {name}, pattern: {pattern}")


# regex_patterns.QUANTITY_RANGE_PATTERN
# regex_patterns.SINGLE_NUMBER_THEN_UNIT_PATTERN

# input_string = "1/2 cup of sugar, 4 cups of my favorite cheese"
# matches = regex_patterns.find_matches(input_string)
# matches.values()


# # List of tuples containing variable name and corresponding regex pattern
# pattern_list = [
#     ('UNITS_PATTERN', r"([a-zA-Z]+)"),
#     ('SINGLE_NUMBER_THEN_UNIT_PATTERN', r"(\d+)([a-zA-Z]+)"),
#     ('QUANTITY_RANGE_PATTERN', r"\d+\s*[\-]\d+"),
#     ('QUANTITY_WORD_PATTERN', r"(\d+\s\w+\s\d+/\d+|\d+\s\w+)"),
#     ('FRACTION_PATTERN', r'\d*\s*/\s*\d+'),
#     ('MULTI_PART_FRACTIONS_PATTERN', r"(\d*\s*\d/\d+)"),
#     ('NUM_SPACE_FRACTION_PATTERN', r'\d+\s+\d*\s*/\s*\d+'),
#     ('NUM_AND_FRACTION_PATTERN', r'\d+\s+(?:and|&)\s+\d*\s*/\s*\d+'),
#     ('RANGE_WITH_TO_OR_PATTERN', r'(\d+(?:\.\d+)?)\s*(?:-\s*|\b(?:to|or)\s+)\s*(\d+(?:\.\d+)?)'),
#     ('BETWEEN_NUM_AND_NUM_PATTERN', r'between\s+(\d*\s*/\s*\d+|\d+)\s+(?:and|&)\s+(\d*\s*/\s*\d+|\d+)'),
#     ('QUANTITY_THEN_UNIT_ABBR_PATTERN', r"(\d)\-?([a-zA-Z])"),
#     ('QUANTITY_THEN_UNIT_WORD_PATTERN', r"(\d+)\-?([a-zA-Z]+)"),
#     ('UNITS_HYPHEN_QUANTITY_PATTERN', r"([a-zA-Z]+)-(\d+)"),
#     ('UNITS_COMMA_QUANTITY_PATTERN', r"([a-zA-Z]+),(\d+)"),
#     ('UNITS_SLASH_QUANTITY_PATTERN', r"([a-zA-Z]+)/(\d+)"),
#     ('UNITS_PARENTHESES_QUANTITY_PATTERN', r"([a-zA-Z]+)\((\d+)"),
# ]
# class RegexPatterns:
#     """
#     A class to hold all regex patterns used in the recipe parser.
#     """
#     def __init__(self,
#                     UNITS_PATTERN,
#                     SINGLE_NUMBER_THEN_UNIT_PATTERN,
#                     ANY_NUMBER_THEN_UNIT_PATTERN,
#                     UNIT_THEN_ANY_NUMBER_PATTERN,
#                     QUANTITY_RANGE_PATTERN,
#                     QUANTITY_WORD_PATTERN,
#                     FRACTION_PATTERN,
#                     MULTI_PART_FRACTIONS_PATTERN,
#                     NUM_SPACE_FRACTION_PATTERN,
#                     NUM_AND_FRACTION_PATTERN,
#                     RANGE_WITH_TO_OR_PATTERN,
#                     BETWEEN_NUM_AND_NUM_PATTERN,
#                     QUANTITY_THEN_UNIT_ABBR_PATTERN,
#                     QUANTITY_THEN_UNIT_WORD_PATTERN,
#                     UNITS_HYPHEN_QUANTITY_PATTERN,
#                     UNITS_COMMA_QUANTITY_PATTERN,
#                     UNITS_SLASH_QUANTITY_PATTERN,
#                     UNITS_PARENTHESES_QUANTITY_PATTERN
#                  ):
#         self.UNITS_PATTERN = UNITS_PATTERN
#         self.SINGLE_NUMBER_THEN_UNIT_PATTERN = SINGLE_NUMBER_THEN_UNIT_PATTERN
#         self.ANY_NUMBER_THEN_UNIT_PATTERN = ANY_NUMBER_THEN_UNIT_PATTERN
#         self.UNIT_THEN_ANY_NUMBER_PATTERN = UNIT_THEN_ANY_NUMBER_PATTERN
#         self.FRACTION_PATTERN = FRACTION_PATTERN
#         self.MULTI_PART_FRACTIONS_PATTERN = MULTI_PART_FRACTIONS_PATTERN
#         self.QUANTITY_RANGE_PATTERN = QUANTITY_RANGE_PATTERN
#         self.QUANTITY_WORD_PATTERN = QUANTITY_WORD_PATTERN
#         self.FRACTION_PATTERN = FRACTION_PATTERN
#         self.NUM_SPACE_FRACTION_PATTERN = NUM_SPACE_FRACTION_PATTERN
#         self.NUM_AND_FRACTION_PATTERN = NUM_AND_FRACTION_PATTERN
#         self.RANGE_WITH_TO_OR_PATTERN = RANGE_WITH_TO_OR_PATTERN
#         self.BETWEEN_NUM_AND_NUM_PATTERN = BETWEEN_NUM_AND_NUM_PATTERN
#         self.QUANTITY_THEN_UNIT_ABBR_PATTERN = QUANTITY_THEN_UNIT_ABBR_PATTERN
#         self.QUANTITY_THEN_UNIT_WORD_PATTERN = QUANTITY_THEN_UNIT_WORD_PATTERN
        

#     @staticmethod
#     def find_fraction_parts(ingredient):
#         """
#         Find all multipart fraction parts in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the fraction parts of the ingredient
#         """
#         return MULTI_PART_FRACTIONS_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_quantity_range(ingredient):
#         """
#         Find all quantity ranges in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the quantity ranges of the ingredient
#         """
#         return QUANTITY_RANGE_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_quantity_word(ingredient):
#         """
#         Find all quantity words in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the quantity words of the ingredient
#         """
#         return QUANTITY_WORD_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_fractions(ingredient):
#         """
#         Find all fractions in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the fractions of the ingredient
#         """
#         return FRACTION_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_num_space_fraction(ingredient):
#         """
#         Find all number space fraction in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the number space fraction of the ingredient
#         """
#         return NUM_SPACE_FRACTION_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_num_and_fraction(ingredient):
#         """
#         Find all number and fraction in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the number and fraction of the ingredient
#         """
#         return NUM_AND_FRACTION_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_range_string(ingredient):
#         """
#         Find all range string in a string.

#         :param ingredient: a string representing an ingredient
#         :return: a list of strings representing the range string of the ingredient
#         """
#         return RANGE_STRING_PATTERN.findall(ingredient)

#     @staticmethod
#     def find_between_num_and_num(ingredient):
#         """
#         Find all between number and number in a string.
