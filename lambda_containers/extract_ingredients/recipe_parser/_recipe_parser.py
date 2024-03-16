# Authors: Angus Watters, Melissa Terry 

import re
from typing import List, Dict, Any, Union, Tuple
from fractions import Fraction
from html import unescape
import warnings

# from regex_patterns import regex_patterns
# from regex_patterns import pattern_list, RegexPatterns


# # import regex class module
# # from . import regex_patterns RecipeRegexPatterns 

from ._regex_patterns import RecipeRegexPatterns

# # import for for local development
# from lambda_containers.extract_ingredients.recipe_parser import RecipeRegexPatterns
# from recipe_parser import RecipeRegexPatterns

# OLD / LOCAL import statements 
# from lambda_containers.extract_ingredients.parser.regex_patterns import RecipeRegexPatterns # OLD STATEMENT
# from parser.regex_patterns import RecipeRegexPatterns # MAYBE NEW STATEMENT

# from regex_patterns import RecipeRegexPatterns
# from parser.regex_patterns import RecipeRegexPatterns

####################################################################################################
######################################## RecipeParser class ########################################
####################################################################################################

# Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# Step 2: Replace numbers with words with their numerical equivalents
# Step 3: Replace all unicode fractions with their decimal equivalents
# Step 4: Replace unicode fraction character with standard fraction character (i.e. \u2044 to /)
# Step 4: Replace all fractions with their decimal equivalents
# Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# Step 6: Add or Multiply the numbers in a string separated by a space
# Step 7: Seperate any part of the string that is wrapped in parenthesis and set aside this content to be used later 
# Step 8: Attempt to pull out the first quantity and unit 
# Step 9: Check if required (set self.required)
# Step 9: TODO: Parse parenthesis content and update best_quantity/best_unit if applicable

class RecipeParser:
    """
    A class to parse recipe ingredients into a standard format.

    Args:
        ingredient (str): The ingredient to parse.
        regex (RecipeRegexPatterns): The regular expression patterns class to use for parsing the ingredient.
        debug (bool): Whether to print debug statements (default is False)
    """

    def __init__(self, ingredient: str,  regex: RecipeRegexPatterns, debug = False):
        self.ingredient          = ingredient
        self.standard_ingredient = ingredient
        
        self.reduced_ingredient  = None    # parenthesis removed from the ingredient string
        self.parenthesis_content = None  # content of the parenthesis removed from the ingredient string

        self.quantity       = None    # the best quantity found in the ingredient string
        self.unit           = None    # the best unit found in the ingredient string


        # make member variables for seconday quantities and units
        self.secondary_quantity = None
        self.secondary_unit     = None

        # "standard units" are the commonplace names for the found units (i.e. the standard unit of "oz" is "ounce")
        self.standard_unit = None 
        self.standard_secondary_unit = None

        # stash the best quantity and unit for testing/debugging
        self.stashed_quantity    = None 
        self.stashed_unit        = None

        self.required            = True    # default sets the ingredient as a required ingredient

        self.parenthesis_notes   = []

        self.regex = regex
        self.debug = debug

        self.found_units         = None    # where units will get stored after being parsed (temporarily)
    
        self.parenthesis_obj = {
            "raw_ingredient": "",
            "standard_ingredient": "",
            "reduced_ingredient": self.reduced_ingredient,
            "parenthesis_content": ""
            }

    def _standard_ingredient(self):
        
        return self.standard_ingredient
    
    def _find_units(self, ingredient: str) -> List[str]:
        """
        Find units in the ingredient string.
        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            List[str]: A list of units found in the ingredient string.
        """

        # split the input string on whitespaces
        split_ingredient = ingredient.split()

        matched_units = [i for i in split_ingredient if i in self.regex.constants["UNITS"]]

        return matched_units
    
    def _drop_special_dashes(self) -> None:
        # print("Dropping special dashes")
        self.standard_ingredient = self.standard_ingredient.replace("—", "-").replace("–", "-").replace("~", "-")
        return
    
    def _parse_number_words(self):
        """
        Replace number words with their corresponding numerical values in the parsed ingredient.
        """

        # print("Parsing number words")
        for word, regex_data in self.regex.NUMBER_WORDS_REGEX_MAP.items():
            pattern = regex_data[1]
            # print statement if word is found in ingredient and replaced
            if pattern.search(self.standard_ingredient):
                print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}") if self.debug else None
            self.standard_ingredient = pattern.sub(regex_data[0], self.standard_ingredient)

    def _clean_html_and_unicode(self) -> None:
        """Unescape fractions from HTML code coded fractions to unicode fractions."""

        # Unescape HTML
        self.standard_ingredient = unescape(self.standard_ingredient)

        # Replace unicode fractions with their decimal equivalents
        for unicode_fraction, decimal_fraction in self.regex.constants["UNICODE_FRACTIONS"].items():
            self.standard_ingredient = self.standard_ingredient.replace(unicode_fraction, f" {decimal_fraction}")
            # self.standard_ingredient = self.standard_ingredient.replace(unicode_fraction, decimal_fraction)

    def _replace_unicode_fraction_slashes(self) -> None:
        """Replace unicode fraction slashes with standard slashes in the parsed ingredient."""

        # Replace unicode fraction slashes with standard slashes
        self.standard_ingredient = self.standard_ingredient.replace('\u2044', '/') # could use .replace('\u2044', '\u002F'), or just .replace("⁄", "/")

    def _add_whitespace(self):
        # regex pattern to match consecutive sequences of letters or digits
        pattern = self.regex.CONSECUTIVE_LETTERS_DIGITS        
        # pattern = re.compile(r'([a-zA-Z]+)(\d+)|(\d+)([a-zA-Z]+)')

        # replace consecutive sequences of letters or digits with whitespace-separated sequences
        self.standard_ingredient = re.sub(pattern, r'\1 \2\3 \4', self.standard_ingredient)

    def _make_int_or_float_str(self, number_str: str) -> str:
        """ Convert a string representation of a number to its integer or float equivalent.
        If the number is a whole number, return the integer value as a string. If the number is a decimal, return the float value as a string.
        Args:
            number_str (str): The string representation of the number.
        Returns:
            str: The integer or float value of the number as a string.
        
        Examples:
        >>> make_int_or_float_str("1.0") 
        "1"
        >>> make_int_or_float_str("1")
        "1"
        >>> make_int_or_float_str("0.25")
        "0.25"
        """
        number = float(number_str.strip())  # Convert string to float
        if number == int(number):  # Check if float is equal to its integer value
            return str(int(number))  # Return integer value if it's a whole number
        else:
            return str(number)  # Return float if it's a decimal
        
    def _fractions_to_decimals(self) -> None:
        """
        Replace fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        fractions = re.findall(self.regex.FRACTION_PATTERN, self.standard_ingredient)

        split_frac = [i.replace(" ", "").split("/") for i in frac]
        split_frac = [(int(f[0]), int(f[1])) for f in split_frac]
        fraction_decimal = [round(float(Fraction(f[0], f[1])), 3) for f in split_frac]

        # replace fractions in original string with decimal equivalents
        for i, f in enumerate(fractions):
            self.standard_ingredient = self.standard_ingredient.replace(f, str(fraction_decimal[i]))
    
    def _fraction_str_to_decimal(self, fraction_str: str) -> float:
        """
        Convert a string representation of a fraction to its decimal equivalent.
        """
        # Split the fraction string into its numerator and denominator
        split_fraction = [i.strip() for i in fraction_str.split("/")]
        # print(f"Split Fraction: {split_fraction}") if self.debug else None

        # If the fraction is a whole number, return the number
        if len(split_fraction) == 1:
            # print(f"---> Only one part: {split_fraction[0]}")

            converted_number = self._make_int_or_float_str(split_fraction[0])

            # print(f"---> OLD Output: {round(float(split_fraction[0]), 3)}")
            # print(f"---> NEW Output: {converted_number}")
            return converted_number

        numerator = int(split_fraction[0])
        denominator = int(split_fraction[1])

        # Convert the fraction to a decimal
        # return round(float(Fraction(numerator, denominator)), 3)
        return self._make_int_or_float_str(str(round(float(Fraction(numerator, denominator)), 3)))
    
    def _convert_fractions_to_decimals(self) -> None:
        """
        Convert fractions in the parsed ingredient to their decimal equivalents.
        """
        
        # std_ingred = '1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)'
        # regex.FRACTION_PATTERN.findall(std_ingred)

        # fraction_str = "1 to 1/2 cups, 2 and 5 animals, 2 2 / 4 cats, 1 and 1/22 cups water melon"
        matches = self.regex.FRACTION_PATTERN.findall(self.standard_ingredient)
        # matches = regex.FRACTION_PATTERN.findall(fraction_str)

        # Replace fractions with their decimal equivalents
        for match in matches:
            # print(f"Match: {match}")

            fraction_decimal = self._fraction_str_to_decimal(match)

            print(f"Fraction Decimal: {fraction_decimal}") if self.debug else None

            self.standard_ingredient = self.standard_ingredient.replace(match, str(fraction_decimal))


    def _force_ws(self):
        
        """Forces spaces between numbers and units and between units and numbers.
        End result is a string with a space between numbers and units and between units and numbers.
        Examples:
        "1cup" becomes "1 cup"
        "cup1" becomes "cup 1" 
        and ultimately "1cup" becomes "1 - cup" and "cup1" becomes "cup - 1"
        """

        Q_TO_U = re.compile(r"(\d)\-?([a-zA-Z])")  # 1cup
        U_TO_Q = re.compile(r"([a-zA-Z])(\d)")     # cup1
        U_DASH_Q = re.compile(r"([a-zA-Z])\-(\d)") # cup - 1

        self.standard_ingredient = Q_TO_U.sub(r"\1 \2", self.standard_ingredient)
        self.standard_ingredient = U_TO_Q.sub(r"\1 \2", self.standard_ingredient)
        self.standard_ingredient = U_DASH_Q.sub(r"\1 - \2", self.standard_ingredient)

    # Define the regular expression pattern to match numbers with a hyphen in between them
    def _update_ranges(self, ingredient, pattern, replacement_function=None):
        # self.standard_ingredient
        # ingredient = "1.0 - 2.0 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 0.75 cups of sugar, 1.0 - 0.25 cups of sugar"
        # pattern = regex.BETWEEN_NUM_AND_NUM_PATTERN
        
        # replacement_function = replace_and_with_hyphen

        # input_string = tmp
        # pattern = regex.BETWEEN_NUM_AND_NUM_PATTERN
        # replacement_function = replace_and_with_hyphen

        matches = pattern.findall(ingredient)
        # matched_ranges = [match.split("-") for match in matches]

        if replacement_function:
            # print(f"Replacement Function given")
            matched_ranges = [replacement_function(match).split("-") for match in matches]
        else:
            # print(f"No Replacement Function given")
            matched_ranges = [match.split("-") for match in matches]

        # print(f"Matched Ranges: \n > {matched_ranges}") if self.debug else None

        updated_ranges = [" - ".join([str(self._fraction_str_to_decimal(i)) for i in match if i]) for match in matched_ranges]
        # updated_ranges = [" - ".join([str(int(i)) for i in match if i]) for match in matched_ranges]
        
        # Create a dictionary to map the matched ranges to the updated ranges
        ranges_map = dict(zip(matches, updated_ranges))

        # Replace the ranges in the original string with the updated ranges
        for original_range, updated_range in ranges_map.items():
            # print(f"Original Range: {original_range}")
            # print(f"Updated Range: {updated_range}")
            # if replacement_function:
            #     print(f"Replacement Function given")
            #     updated_range = replacement_function(updated_range)
            ingredient = ingredient.replace(original_range, updated_range)
            print("\n")

        return ingredient
    
    def _avg_ranges(self) -> None:
        """
        Replace ranges of numbers with their average in the parsed ingredient.
        Examples:
        "1-2 oz" -> "1.5 oz"
        "1 - 2 ft" -> "1.5 ft"
        """

        # ingredient = '2 0.5 cups of sugar'
        # ingredient = 'a lemon'
        # ingredient = "1.5 lb of sugar"
        # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

        # ingredient = output[4]
        # # ingredient = '1 - 2 oz of butter, 20 - 50 grams of peanuts'
        # ingredient = '1 - 2 oz of butter, 20 - 50 of peanuts'
        # for k, v in regex.find_matches(ingredient).items():
        #     print(f"{k}: {v}")

        # all_ranges = re.findall(regex.QUANTITY_DASH_QUANTITY_UNIT, ingredient)
        # all_ranges = re.finditer(regex.QUANTITY_DASH_QUANTITY_UNIT, ingredient)
        
        all_ranges = re.finditer(self.regex.QUANTITY_DASH_QUANTITY, self.standard_ingredient)
        # all_ranges = re.finditer(regex.QUANTITY_DASH_QUANTITY, ingredient)

        # initialize offset and replacement index values for updating the ingredient string, 
        # these will be used to keep track of the position of the match in the string
        offset = 0
        replacement_index = 0

        # Update the ingredient string with the merged values
        for match in all_ranges:
            # print(f"Ingredient string: {self.standard_ingredient}")

            # Get the start and end positions of the match
            start, end = match.start(), match.end()

            print(f"Match: {match.group()} at positions {start}-{end}") if self.debug else None

            # Get the range values from the match
            range_values = re.findall(self.regex.QUANTITY_DASH_QUANTITY, match.group())

            print(f"Range Values: {range_values}") if self.debug else None
            
            # split the range values into a list of lists
            split_range_values = [i.split("-") for i in range_values]

            # get the average of each of the range values
            range_avgs    = [sum([float(num_str) for num_str in i]) / 2 for i in split_range_values][0]
            range_average = self._make_int_or_float_str(str(range_avgs))

            print(f"Range Averages: {range_average}") if self.debug else None

            # Calculate the start and end positions in the modified string
            modified_start = start + offset
            modified_end = end + offset

            # print(f" -> Modified match positions: {modified_start}-{modified_end}")
            # print(f"Replacing {match.group()} with '{merged_quantity}'...")
            
            # Construct the modified string with the replacement applied
            self.standard_ingredient = self.standard_ingredient[:modified_start] + str(range_average) + self.standard_ingredient[modified_end:]
            # ingredient = ingredient[:modified_start] + str(range_average) + ingredient[modified_end:]

            # Update the offset for subsequent replacements
            offset += len(range_average) - (end - start)
            # replacement_index += 1
            # print(f" --> Output ingredient: \n > '{ingredient}'")

    def _replace_and_with_hyphen(self, match):
        # Replace "and" and "&" with hyphens
        return match.replace("and", "-").replace("&", "-")
    
    # def replace_and_with_hyphen(match):
    #     # Replace "and" and "&" with hyphens
    #     return match.replace("and", "-").replace("&", "-")
    
    def _replace_to_or_with_hyphen(self, match):
        # Replace "and" and "&" with hyphens
        return match.replace("to", "-").replace("or", "-")

    def _fix_ranges(self):
        """
        Fix ranges in the parsed ingredient.
        Given a parsed ingredient, this method will fix ranges of numbers that are separated by one or more hyphens, ranges of numbers that are preceded by "between" and followed by "and" or "&", and ranges that are separated by "to" or "or".
        Examples:
        - "1-2 oz" -> "1 - 2 oz"
        - "between 1 and 5" -> "1 - 5"
        - "1 to 5" -> "1 - 5"

        """
        # print("Fixing ranges")
        # Define the regular expression pattern to match ranges

        print(f"Before initial range update:\n {self.standard_ingredient}") if self.debug else None
        # tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 -- 45 inches, cats do between 1  and 5 digs, i like between 1 and 2 mm'
        # Update ranges of numbers that are separated by one or more hyphens
        self.standard_ingredient = self._update_ranges(self.standard_ingredient, self.regex.QUANTITY_DASH_QUANTITY)
        # self.standard_ingredient = self._update_ranges(self.standard_ingredient, regex.QUANTITY_RANGE)
        # self.standard_ingredient = self._update_ranges(self.standard_ingredient, regex.QUANTITY_RANGE_PATTERN)
        print(f"After initial range update:\n {self.standard_ingredient}") if self.debug else None

        # Update ranges of numbers that are preceded by "between" and followed by "and" or "&"
        self.standard_ingredient = self._update_ranges(self.standard_ingredient, self.regex.BETWEEN_QUANTITY_AND_QUANTITY, self._replace_and_with_hyphen)
        # self.standard_ingredient = self._update_ranges(self.standard_ingredient, regex.BETWEEN_NUM_AND_NUM_PATTERN, self._replace_and_with_hyphen)
        print(f"After between and update:\n {self.standard_ingredient}") if self.debug else None

        # Update ranges that are separated by "to" or "or"
        self.standard_ingredient = self._update_ranges(self.standard_ingredient, self.regex.QUANTITY_TO_OR_QUANTITY, self._replace_to_or_with_hyphen)
        # self.standard_ingredient = self._update_ranges(self.standard_ingredient, regex.RANGE_WITH_TO_OR_PATTERN, self._replace_to_or_with_hyphen)
        print(f"After to or update:\n {self.standard_ingredient}") if self.debug else None

    def _remove_repeat_units(self) -> None:
        """
        Remove repeat units from the ingredient string.
        Examples:
        "2 oz - 3 oz diced tomatoes" -> "2 - 3 oz diced tomatoes"
        "3cups-4 cups of cats" -> "3 - 4 cups of cats"
        """
        # ingredient = '2 oz - 3 oz diced tomatoes, 3cups-4 cups of cats, 2cups 1/2 cups'
        # ingredient = "i like to eat 1 oz-2 oz with cats and 1ft-2ft of snow"
        # Define the regular expression pattern to match repeat units

        # pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')
        # pattern = re.compile(r'(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)\s*-\s*(\d+(?:\.\d+|/\d+)?)\s*([a-zA-Z]+)')
        # pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')

        # get any strings that match the pattern 1<unitA> - 2<unitA> or 1<unitA> - 2<unitB>
        matches = self.regex.REPEAT_UNIT_RANGES.finditer(self.standard_ingredient)
        # matches = pattern.finditer(self.standard_ingredient)

        for match in matches:
            # print(match.group(0))
            # print(match.group(1))
            # print(match.group(2))
            # print(match.group(3))
            # print(match.group(4))

            # original string matched by the pattern (used for replacement)
            original_string = match.group(0)

            # quantities from first quantity/unit pair
            quantity1 = match.group(1)
            unit1     = match.group(2)

            # quantities from second quantity/unit pair
            quantity2 = match.group(3)
            unit2     = match.group(4)

            # if the units are the same, replace the original string with the quantities and units
            if unit1 == unit2:
                self.standard_ingredient = self.standard_ingredient.replace(original_string, f"{quantity1} - {quantity2} {unit1}")
                # print(f"Repeat units found: {unit1}")
                # print(f"Original string: {original_string}")
                # print(f"Quantity1: {quantity1}, Unit1: {unit1}, Quantity2: {quantity2}, Unit2: {unit2}")
                # print(f"----> REPEAT UNITS: {unit1}")
                # print("\n")
    
    def _remove_x_separators(self):
        """
        Remove "x" separators from the ingredient string and replace with whitespace
        Examples:
            >>> _removed_x_separators("1x2 cups")
            '1 2 cups'
            >>> _remove_x_separators("5 x cartons of eggs")
            "5   cartons of eggs"
        """

        def replace_x(match):
            return match.group().replace('x', ' ').replace('X', ' ')

        # Replace "x"/"X" separators with whitespace
        self.standard_ingredient = self.regex.X_AFTER_NUMBER.sub(replace_x, self.standard_ingredient)


    def _merge_spaced_numbers(self, spaced_numbers: str) -> str:
        """ Add or multiply the numbers in a string separated by a space.
        If the second number is less than 1, then add the two numbers together, otherwise multiply them together.
        This was the most generic form of dealing with numbers seperated by spaces that i could come up with
        (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means to multiply the numbers 2 8 oz means 16 oz)
        Args:
            spaced_numbers (str): A string of numbers separated by a space.
        Returns:
            str: string containing the sum OR the product of the numbers in the string. 
        Examples:
            >>> _merge_spaced_numbers('2 0.5')
            '2.5'
            >>> _merge_spaced_numbers('2 8')
            '16'
        """

        # spaced_numbers = '0.5'

        # Get the numbers from the spaced seperated string
        split_numbers = re.findall(self.regex.SPLIT_SPACED_NUMS, spaced_numbers)

        # If the second number is less than 1, then add the two numbers together, otherwise multiply them together
        # This was the most generic form of dealing with numbers seperated by spaces 
        # (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means to multiply the numbers 2 8 oz means 16 oz)
        try:
            merged_totals = [self._make_int_or_float_str(str(float(first) + float(second)) if float(second) < 1 else str(float(first) * float(second))) for first, second in split_numbers]
        except:
            warnings.warn(f"error while merging {split_numbers}...")
            merged_totals = [""]
        # # READABLE VERSION of above list comprehension: 
        # This is the above list comprehensions split out into 2 list comprehensions for readability
        # merged_totals = [float(first) + float(second) if float(second) < 1 else float(first) * float(second) for first, second in split_numbers]

        # return merged_totals
        return merged_totals[0] if merged_totals else ""

    def _which_merge_on_spaced_numbers(self, spaced_numbers: str) -> str:
        """ Inform whether to add or multiply the numbers in a string separated by a space.
        Args:
            spaced_numbers (str): A string of numbers separated by a space.
        Returns:
            str: string indicating whether to add or multiply the numbers in the string.
        """

        split_numbers = re.findall(self.regex.SPLIT_SPACED_NUMS, spaced_numbers)
        # split_numbers = [("2", "1")]

        # If the second number is less than 1, then note the numbers should be "added", otherwise they should be "multiplied"
        # This was the most generic form of dealing with numbers seperated by spaces 
        # (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means
        #  to multiply the numbers 2 8 oz means 16 oz)
        try:
            add_or_multiply = ["add" if float(second) < 1 else "multiply" for first, second in split_numbers]
        except:
            warnings.warn(f"error while deciding whether to note '{split_numbers}' as numbers to 'add' or 'multiply'...")
            add_or_multiply = [""]

        return add_or_multiply[0] if add_or_multiply else ""
    
    def _merge_multi_nums2(self) -> None:
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient (v2).
        Assumes that numeric values in string have been padded with a space between numbers and non numeric characters and
        that any fractions have been converted to their decimal equivalents.
        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            str: The parsed ingredient string with the numbers separated by a space merged into a single number (either added or multiplied).
        
        >>> _merge_multi_nums('2 0.5 cups of sugar')
        '2.5 cups of sugar'
        >>> _merge_multi_nums('1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces')
        '1.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'
        """

        # ingredient = '2 0.5 cups of sugar'
        # ingredient = 'a lemon'
        # ingredient = "1.5 lb of sugar"
        # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

        # # original ingred: "1½-2½cup of sugar"
        # ingredient = '1 0.5 - 2 0.5 cup of sugar'
        # ingredient = '1 0.5 - 2 0.5 of sugar'
        # ingredient = '1 1/2 - 2 1/2 cup of sugar'

        # go the spaced numbers matches and get each spaced seperated numbers match AND 
        # try and get the units that follow them so we can correctly match each spaced number with its corresponding unit
        spaced_nums = []
        units = []

        # Create iterable of the matched spaced numbers to insert updated values into the original string
        spaced_matches = re.finditer(self.regex.SPACE_SEP_NUMBERS, self.standard_ingredient)
        # spaced_matches = re.finditer(regex_map.SPACE_SEP_NUMBERS, ingredient)

        # initialize offset and replacement index values for updating the ingredient string, 
        # these will be used to keep track of the position of the match in the string
        offset = 0
        replacement_index = 0

        # Update the ingredient string with the merged values
        for match in spaced_matches:
            # print(f"Ingredient string: {ingredient}")

            # Get the start and end positions of the match
            start, end = match.start(), match.end()

            # search for the first unit that comes after the spaced numbers
            unit_after_match = re.search(self.regex.UNITS_PATTERN,  self.standard_ingredient[end:])
            # unit_after_match = re.search(regex_map.UNITS_PATTERN, ingredient[end:])
            
            if unit_after_match:
                print(f"unit after match: > '{unit_after_match.group()}'")
                units.append(unit_after_match.group())

            # add the spaced number to the list
            spaced_nums.append(match.group())

            # print(f"Match: {match.group()} at positions {start}-{end}")
            merged_quantity = self._merge_spaced_numbers(match.group())
            merge_operation = self._which_merge_on_spaced_numbers(match.group())

            print(f"merged_quantity: {merged_quantity}") if self.debug else None
            print(f"merge_operation: {merge_operation}\n") if self.debug else None

            # Calculate the start and end positions in the modified string
            modified_start = start + offset
            modified_end = end + offset

            # print(f" -> Modified match positions: {modified_start}-{modified_end}")
            print(f"Replacing {match.group()} with '{merged_quantity}'...") if self.debug else None
            
            # Construct the modified string with the replacement applied
            self.standard_ingredient = self.standard_ingredient[:modified_start] + str(merged_quantity) + self.standard_ingredient[modified_end:]
            # ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]

            # Update the offset for subsequent replacements
            offset += len(merged_quantity) - (end - start)
            replacement_index += 1

    def _merge_multi_nums(self) -> None:
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
        Assumes that numeric values in string have been padded with a space between numbers and non numeric characters and
        that any fractions have been converted to their decimal equivalents.
        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            str: The parsed ingredient string with the numbers separated by a space merged into a single number (either added or multiplied).
        
        >>> _merge_multi_nums('2 0.5 cups of sugar')
        '2.5 cups of sugar'
        >>> _merge_multi_nums('1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces')
        '1.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'
        """

        # ingredient = '2 0.5 cups of sugar'
        # ingredient = 'a lemon'
        # ingredient = "1.5 lb of sugar"
        # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

        # # original ingred: "1½-2½cup of sugar"
        # ingredient = '1 0.5 - 2 0.5 cup of sugar'
        # ingredient = '1 1/2 - 2 1/2 cup of sugar'
        
        # get the units from the ingredient string
        # units = re.findall(regex_map.UNITS_PATTERN, ingredient)
        units = re.findall(self.regex.UNITS_PATTERN, self.standard_ingredient)

        # spaced_nums = re.findall(regex.SPACE_SEP_NUMBERS, '2 0.5 cups of sugar 3 0.5 lbs of carrots')
        spaced_nums = re.findall(self.regex.SPACE_SEP_NUMBERS, self.standard_ingredient)

        # Merge the numbers from the space seperated string of numbers
        merged_values = [self._merge_spaced_numbers(num_pair) for num_pair in spaced_nums]

        # Was the operation to merge the numbers an addition or a multiplication?
        merge_type = [self._which_merge_on_spaced_numbers(num_pair) for num_pair in spaced_nums]

        # ---- METHOD 1 ----
        # METHOD 1: Create a list of dictionaries with the units and their converted quantities
        merged_unit_quantities = [{"units":u, "quantities": q, "merge_operation": m} for u, q, m in zip(units, merged_values, merge_type)]
        # merged_unit_quantities = [{"units":u, "quantities": q} for u, q in zip(units, merged_values)] # not including merge_type

        # map the spaced numbers to the units and their converted quantities
        # Key is the spaced numbers, value is a dictionary with the units, merged quantities, and the merge operation
        conversions_map = dict(zip(spaced_nums, merged_unit_quantities))

        # ---- METHOD 2 ----
        # METHOD 2: Create a LIST of dictionaries with the original string, the units, their converted quantities, and the merge method (keep track of iteration index and index the matches by position)
        conversions_list = [{"input_numbers": n, "units":u, "quantities": q, "merge_operation": m} for n, u, q, m in zip(spaced_nums, units, merged_values, merge_type)]

        # print(f"Number of matched spaced numbers: {len(spaced_nums)}")
        # print(f"Number of converted matches (map): {len(conversions_map)}")
        # print(f"Number of converted matches (list): {len(conversions_list)}")

        if len(spaced_nums) != len(conversions_map):
            warnings.warn(f"Number of spaced numbers and number of converted matches (MAP) are not equal...")

        if len(spaced_nums) != len(conversions_list):    
            warnings.warn(f"Number of spaced numbers and number of converted matches (LIST) are not equal...")
        
        # Create iterable of the matched spaced numbers to insert updated values into the original string
        spaced_matches = re.finditer(self.regex.SPACE_SEP_NUMBERS, self.standard_ingredient)

        # initialize offset and replacement index values for updating the ingredient string, 
        # these will be used to keep track of the position of the match in the string
        offset = 0
        replacement_index = 0

        # Update the ingredient string with the merged values
        for match in spaced_matches:
            # print(f"Ingredient string: {self.standard_ingredient}")

            # Get the start and end positions of the match
            start, end = match.start(), match.end()

            # print(f"Match: {match.group()} at positions {start}-{end}")

            # Get key value pair in the conversions_map that corresponds to the current match and the new quantity values to sub in
            conversions = conversions_map[match.group()]
            # conversions = conversions_list[replacement_index]

            # print(f"Conversions: {conversions}")

            # starting_quantity = conversions["input_numbers"]
            merged_quantity = conversions["quantities"]
            merge_operation = conversions["merge_operation"] # add or multiply

            # print(f"Starting quantity {starting_quantity}")
            # print(f"Merged Quantity: {merged_quantity}") if self.debug else None

            # Calculate the start and end positions in the modified string
            modified_start = start + offset
            modified_end = end + offset

            # print(f" -> Modified match positions: {modified_start}-{modified_end}")
            # print(f"Replacing {match.group()} with '{merged_quantity}'...")
            
            # Construct the modified string with the replacement applied
            self.standard_ingredient = self.standard_ingredient[:modified_start] + str(merged_quantity) + self.standard_ingredient[modified_end:]
            # ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]

            # Update the offset for subsequent replacements
            offset += len(merged_quantity) - (end - start)
            replacement_index += 1
            # print(f" --> Output ingredient: \n > '{self.standard_ingredient}'")

    def _replace_a_or_an_units(self) -> None:
        """
        Replace "a" or "an" with "1" in the parsed ingredient if no number is present in the ingredient string.
        """
        # ingredient = "a lemon"

        # lowercase and split the ingredient string
        self.standard_ingredient = self.standard_ingredient.lower()
        split_ingredient = self.standard_ingredient.split()

        matched_nums = re.findall(self.regex.ALL_NUMBERS, self.standard_ingredient)

        if split_ingredient[0] in ["a", "an"] and not matched_nums:
            split_ingredient[0] = "1"
            # ingredient = " ".join(split_ingredient)
            self.standard_ingredient = " ".join(split_ingredient)
            # return ingredient
        
    def _drop_special_characters(self):

        # Drop unwanted periods and replace them with whitespace
        self.standard_ingredient = self.standard_ingredient.replace(".", " ")

    ####### Deprecated ####### 
    def _parse_fractions(self):
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        # regex.MULTI_PART_FRACTIONS_PATTERN
        # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.standard_ingredient)
        # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.standard_ingredient)

        # finditer() method
        fractions = re.finditer(self.regex.MULTI_PART_FRACTIONS_PATTERN, self.standard_ingredient)
        # fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.standard_ingredient)

        # Replace fractions in the original string with their sum based on match indices
        # updated_ingredient = self.standard_ingredient
        offset = 0

        for match in fractions:

            # keep track of the offset to adjust the index of the match
            start_index = match.start() + offset
            end_index = match.end() + offset
            matched_fraction = match.group()

            print(f"Matched Fraction: {matched_fraction}")
            # remove "and" and "&" from the matched fraction
            matched_fraction = matched_fraction.replace("and", " ").replace("&", " ")

            print(f"Matched Fraction after removing AND: {matched_fraction}")

            # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
            parsed_fraction = self._parse_mixed_fraction(matched_fraction)

            print(f"Parsed Fraction: {parsed_fraction}")

            # Replace the matched fraction with the sum of the parse    d fraction
            sum_fraction = self._sum_parsed_fractions(parsed_fraction)

            print(f"Sum Fraction: {sum_fraction}")
            # Insert the sum of the fraction into the updated ingredient string
            # updated_ingredient = updated_ingredient[:start_index] + str(sum_fraction) + updated_ingredient[end_index:]
            self.standard_ingredient = self.standard_ingredient[:start_index] + " " + str(sum_fraction) + self.standard_ingredient[end_index:]

            # Update the offset to account for the difference in length between the matched fraction and the sum of the fraction
            offset += len(str(sum_fraction)) - len(matched_fraction)

    ####### Deprecated ####### 
    def _parse_mixed_fraction(self, fraction_str: str) -> list:
        # Remove whitespace to the left and right of a slash
        cleaned_fractions = re.sub(r'\s*/\s*', '/', fraction_str)

        # print(f"Cleaned Fractions: {cleaned_fractions}")

        # Define the regular expression pattern to match the mixed fraction
        pattern = re.compile(r'\b(\d+)\s*(\d+/\d+)\b')
        match = pattern.search(cleaned_fractions)
        
        if match:
            whole_number = match.group(1)
            fraction = match.group(2)
            return [whole_number, fraction]
        else:
            # If no match found, split the string based on space and return
            return cleaned_fractions.split()
        
    ####### Deprecated ####### 
    def _sum_parsed_fractions(self, fraction_list: list, truncate = 3) -> float:
        
        total = 0
        for i in fraction_list:
            total += Fraction(i)
        
        return round(float(total), truncate)
    
    def _separate_parenthesis(self):

        # ingredient = '0.25 teaspoon crushed red pepper (optional)'
        # ingredient = '0.25 teaspoon (6 ounces options) crushed (optional) red pepper'
        # ingred = "1/2 (8 ounce) steaks with almonds"

        # for k, v in regex.find_matches(ingredient).items():
        #     print(f"Key: {k} - {v}")

        # split the ingredient string by the open/close parenthesis sets
        no_parenthesis = re.split(self.regex.SPLIT_BY_PARENTHESIS, self.standard_ingredient)
        # no_parenthesis = re.split(self.regex.SPLIT_BY_PARENTHESIS, ingredient)

        # remove any leading or trailing whitespace from the split strings and join them back together
        no_parenthesis = " ".join([i.strip() for i in no_parenthesis])

        # get the set of paranthesis values
        parentheses = re.findall(self.regex.SPLIT_BY_PARENTHESIS, self.standard_ingredient)
        # parentheses = re.findall(self.regex.SPLIT_BY_PARENTHESIS, ingredient)
        # ingredient, no_parenthesis, parentheses
        
        # update the paranthensis object with the parsed values
        self.parenthesis_obj["raw_ingredient"] = self.ingredient
        self.parenthesis_obj["standard_ingredient"] = self.standard_ingredient
        self.parenthesis_obj["reduced_ingredient"] = no_parenthesis
        self.parenthesis_obj["parenthesis_content"] = parentheses
        
        # set "reduced_ingredient" to the parsed ingredient with parenthesis removed
        self.reduced_ingredient = no_parenthesis

        # set "parenthesis_content" to the parsed parenthesis strings
        self.parenthesis_content = parentheses

        # parsed_parenthesis = {"raw_string" : ingredient, 
        #                     "parenthesis_removed" : no_parenthesis, 
        #                     "parenthesis":parentheses
        #                     }
    
    # return parsed_parenthesis
    def _pull_units(self):
        """
        Pull out all of the units in the string
        Returns a dictionary containing all of the units found in the ingredient string (all units, basic units, nonbasic units, volumetric units, and a flag indicating if the ingredient has a unit).
        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            dict: A dictionary containing all of the units found in the ingredient string (all units, basic units, nonbasic units, volumetric units, and a flag indicating if the ingredient has a unit).
        Examples:
            >>> pull_units('0.25 teaspoon crushed red pepper (optional)')
            {'units': ['teaspoon'],
                'basic_units': ['teaspoon'],
                'nonbasic_units': [],
                'volumetric_units': ['teaspoon'],
                'has_unit': True}
            >>> pull_units('1 1/2 cups diced tomatoes, 2 tablespoons of sugar, 1 stick of butter')
            {'units': ['cups', 'tablespoons', 'stick'],
                'basic_units': ['cups', 'tablespoons', 'stick'],
                'nonbasic_units': ['stick'],
                'volumetric_units': ['cups', 'tablespoons'],
                'has_unit': True}
        """

        # # ingredient = '0.25 teaspoon crushed red pepper (optional)'
        # for k, v in regex.find_matches(ingredient).items():
        #     print(f"Key: {k} - {v}")
        
        if not self.reduced_ingredient:
            return None
        
        # initliaze the has_unit flag to True, if no units are found, then the flag will be set to False
        has_unit = True

        # get all of the units in the ingredient string
        all_units = self.regex.UNITS_PATTERN.findall(self.reduced_ingredient)

        # get the basic units in the ingredient string by checking if the units are in the basic units set
        basic_units = [unit for unit in all_units if unit in self.regex.constants["BASIC_UNITS_SET"]]
        # basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient) # Does the same thing but uses regex, probably better to NOT regex backtrack if we can avoid it..

        # get the nonbasic units in the ingredient string by checking if the units are not in the basic units set
        nonbasic_units = list(set(all_units) - set(basic_units))

        # get the volumetric units in the ingredient string by checking if the units are in the volumetric units set
        volumetric_units = [unit for unit in all_units if unit in self.regex.constants["VOLUME_UNITS_SET"]]
        # volumetric_units = regex.VOLUME_UNITS_PATTERN.findall(ingredient) 

        # if no units are found, then set the has_unit flag to False
        if not all_units and not basic_units and not nonbasic_units and not volumetric_units:
            has_unit = False

        self.found_units = {"units" : all_units,
                    "basic_units" : basic_units,
                    "nonbasic_units" : nonbasic_units,
                    "volumetric_units" : volumetric_units,
                    "has_unit" : has_unit}
        
        # found_units = {"units" : all_units, 
        #             "basic_units" : basic_units, 
        #             "nonbasic_units" : nonbasic_units, 
        #             "volumetric_units" : volumetric_units,
        #             "has_unit" : has_unit}
        
        # return found_units
    
    def _pull_first_unit(self): 
        """
        Pull out the first unit in the string
        Returns the first unit found in the ingredient string.
        """
        # get the first unit in the ingredient string
        first_unit = self.found_units["units"][0] if self.found_units["units"] else ""

        return first_unit
    
    def standardize(self):
        
        # define a list containing the class methods that should be called in order on the input ingredient string
        methods = [
            self._drop_special_dashes,
            self._parse_number_words,
            self._clean_html_and_unicode,
            self._replace_unicode_fraction_slashes,
            self._convert_fractions_to_decimals,
            self._fix_ranges,
            # self._remove_x_separators,
            self._force_ws,
            self._remove_repeat_units,
            self._remove_x_separators,
            # self._merge_multi_nums,
            self._merge_multi_nums2,
            self._replace_a_or_an_units,
            self._avg_ranges,
            self._separate_parenthesis,
            self._pull_units
        ]

        # call each method in the list on the input ingredient string
        for method in methods:
            print(f"Calling method: {method.__name__}") if self.debug else None
            print(f"> Starting ingredient: '{self.standard_ingredient}'") if self.debug else None

            method()

            print(f"> Ending ingredient: '{self.standard_ingredient}'") if self.debug else None
            
        print(f"Done, returning standardized ingredient: \n > '{self.standard_ingredient}'") if self.debug else None

        # return the parsed ingredient string
        return self.standard_ingredient
    
    def extract_first_quantity_unit(self) -> None:

        """
        Extract the first unit and quantity from an ingredient string.
        Function will extract the first unit and quantity from the ingredient string and set the self.quantity and self.unit member variables.
        Quantities and ingredients are extracted in this order and if any of the previous steps are successful, the function will return early.
        1. Check for basic units (e.g. 1 cup, 2 tablespoons)
        2. Check for nonbasic units (e.g. 1 fillet, 2 carrot sticks)
        3. Check for quantity only, no units (e.g. 1, 2)

        If none of the above steps are successful, then the self.quantity and self.unit member variables will be set to None.

        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            dict: A dictionary containing the first unit and quantity found in the ingredient string.
        Examples:
            >>> extract_first_unit_quantity('1 1/2 cups diced tomatoes, 2 tablespoons of sugar, 1 stick of butter')
            {'quantity': '1 1/2', 'unit': 'cups'}
            >>> extract_first_unit_quantity('2 1/2 cups of sugar')
            {'quantity': '2 1/2', 'unit': 'cups'}
        """

        # ingredient = parser.reduced_ingredient
        # reduced_ingredient = 'salmon fillets '
        # # regex.print_matches(ingredient)
        
        # # set default values for the best quantity and unit
        # best_quantity = None
        # best_unit = None
        
        # ---- STEP 1: CHECK FOR QUANTITY - BASIC UNITS (e.g. 1 cup, 2 tablespoons) ----
        # Example: "1.5 cup of sugar" -> quantity: "1.5", unit: "cup"

        # get the first number followed by a basic unit in the ingredient string
        basic_unit_matches = self.regex.QUANTITY_BASIC_UNIT_GROUPS.findall(self.reduced_ingredient)
        # basic_unit_matches = regex.QUANTITY_BASIC_UNIT_GROUPS.findall(reduced_ingredient)

        # remove any empty matches
        valid_basic_units = [i for i in basic_unit_matches if len(i) > 0]

        # debugging message
        basic_units_message = f"Valid basic units: {valid_basic_units}" if valid_basic_units else f"No valid basic units found..."
        print(basic_units_message)
        # print(basic_units_message) if self.debug else None

        # if we have valid single number quantities, then set the self.quantity and the self.unit member variables and exit the function
        if basic_unit_matches and valid_basic_units:
            self.quantity = valid_basic_units[0][0].strip()
            self.unit = valid_basic_units[0][1].strip()
            # return {"quantity": self.quantity, "unit": self.unit}
            return 

        # ---- STEP 2: CHECK FOR QUANTITY - NONBASIC UNITS (e.g. 1 fillet, 2 carrot sticks) ----
        # Example: "1 fillet of salmon" -> quantity: "1", unit: "fillet"

        # If no basic units are found, then check for anumber followed by a nonbasic units
        nonbasic_unit_matches = self.regex.QUANTITY_NON_BASIC_UNIT_GROUPS.findall(self.reduced_ingredient)
        # nonbasic_unit_matches = regex.QUANTITY_NON_BASIC_UNIT_GROUPS.findall(reduced_ingredient)

        # remove any empty matches
        valid_nonbasic_units = [i for i in nonbasic_unit_matches if len(i) > 0]

        # debugging message
        nonbasic_units_message = f"Valid non basic units: {valid_nonbasic_units}" if valid_nonbasic_units else f"No valid non basic units found..."
        print(nonbasic_units_message)
        # print(nonbasic_units_message) if self.debug else None

        # if we found a number followed by a non basic unit, then set the self.quantity and the self.unit member variables and exit the function
        if nonbasic_unit_matches and valid_nonbasic_units:
            self.quantity = valid_nonbasic_units[0][0].strip()
            self.unit = valid_nonbasic_units[0][1].strip()
            # return {"quantity": self.quantity, "unit": self.unit}
            return
        
        # ---- STEP 3: CHECK FOR ANY QUANTITIES or ANY UNITS in the string, and use the first instances (if they exist) ----
        # Example: "cups, 2 juice of lemon" -> quantity: "2", unit: "juice"

        # if neither basic nor nonbasic units are found, then get all of the numbers and all of the units
        quantity_matches = self.regex.ALL_NUMBERS.findall(self.reduced_ingredient)
        unit_matches     = self.regex.UNITS_PATTERN.findall(self.reduced_ingredient)

        # quantity_matches = regex.ALL_NUMBERS.findall(reduced_ingredient)
        # unit_matches     = regex.UNITS_PATTERN.findall(reduced_ingredient)

        # remove any empty matches
        valid_quantities = [i for i in quantity_matches if len(i) > 0]
        valid_units     = [i for i in unit_matches if len(i) > 0]

        # debugging messages
        all_quantities_message = f"Valid quantities: {valid_quantities}" if valid_quantities else f"No valid quantities found..."
        all_units_message = f"Valid units: {valid_units}" if valid_units else f"No valid units found..."

        print(all_quantities_message)
        print(all_units_message)

        # if either have valid quantities then set the best quantity and best unit to 
        # the first valid quantity and units found, otherwise set as None
        # TODO: Drop this "if valid_quantities or valid_units"...?
        if valid_quantities or valid_units:
            self.quantity = valid_quantities[0].strip() if valid_quantities else None
            self.unit = valid_units[0].strip() if valid_units else None
            # return {"quantity": self.quantity, "unit": self.unit}
            return

        # # ---- STEP 3: CHECK FOR QUANTITY - NO UNITS (e.g. 1, 2) ----

        # # if neither basic nor nonbasic units are found, then get the first number
        # quantity_matches = self.regex.ALL_NUMBERS.findall(self.reduced_ingredient)
        # # quantity_matches = regex.ALL_NUMBERS.findall(reduced_ingredient)
        # # remove any empty matches
        # valid_quantities = [i for i in quantity_matches if len(i) > 0]
        # # debugging message
        # quantity_only_message = f"Valid quantities: {valid_quantities}" if valid_quantities else f"No valid quantities found..."
        # print(quantity_only_message)
        # # print(quantity_only_message) if self.debug else None
        # # if we have valid single number quantities, then return the first one
        # if quantity_matches and valid_quantities:
        #     self.quantity = valid_quantities[0].strip()
        #     # return {"quantity": self.quantity, "unit": self.unit}
        #     return
            
        # # ---- STEP 4: UNITS ONLY ----
        # regex.print_matches(reduced_ingredient)
        # unit_matches = regex.UNITS_PATTERN.findall(reduced_ingredient)

        # ---- STEP 4: NO MATCHES ----
        # just print a message if no valid quantities or units are found and return None
        # best_quantity and best_unit are set to None by default and will remain that way if no units or quantities were found.
        no_matches_message = f"No valid quantities or units found..."
        print(no_matches_message)
        # print(no_matches_message) if self.debug else None
        # return {"quantity": self.quantity, "unit": self.unit}
        return 
    
    def _check_if_required_parenthesis(self, parenthesis_list: list) -> bool:
        """
        Check if the parenthesis content contains the word "optional".
        Args:
            parenthesis_list (list): A list of strings containing the content of the parenthesis in the ingredient string.
        Returns:
            bool: A boolean indicating whether the word "optional" is found in the parenthesis content.
        """
        # parenthesis_list = parenthesis_list

        optional_set = set(["option", "options", "optional", "opt.", "opts.", "opt", "opts", "unrequired"])
        required_set = set(["required", "requirement", "req.", "req"])
        
        # regex match for the words "optional" or "required" in the parenthesis content
        optional_match_flag = any([True if self.regex.OPTIONAL_STRING.findall(i) else False for i in parenthesis_list])
        required_match_flag = any([True if self.regex.REQUIRED_STRING.findall(i) else False for i in parenthesis_list])
        # optional_matches = [regex.OPTIONAL_STRING.findall(i) for i in parenthesis_list]
        # required_matches = [regex.REQUIRED_STRING.findall(i) for i in parenthesis_list]

        # check if any of the words in the parenthesis content are in the optional or required sets
        optional_str_flag = any([any([True if word in optional_set else False for word in i.replace("(", "").replace(")", "").replace(",", " ").split()]) for i in parenthesis_list])
        required_str_flag = any([any([True if word in required_set else False for word in i.replace("(", "").replace(")", "").replace(",", " ").split()]) for i in parenthesis_list])
        
        is_required = (True if required_match_flag or required_str_flag else False) or (False if optional_match_flag or optional_str_flag else True)

        # if required_match_flag or required_str_flag:
        #     is_required = True
        # elif optional_match_flag or optional_str_flag:


        return is_required

    def _check_if_required_string(self, ingredient: str) -> bool:
        """
        Check the ingredient string for optional or required text
        Args:
            ingredient (str): The ingredient string to parse.
        Returns:
            bool: A boolean indicating whether the ingredient is required or not.
        """
        # ingredient = reduced
        optional_set = set(["option", "options", "optional", "opt.", "opts.", "opt", "opts", "unrequired"])
        required_set = set(["required", "requirement", "req.", "req"])

        # regex match for the words "optional" or "required" in the ingredient string
        optional_match_flag = True if self.regex.OPTIONAL_STRING.findall(ingredient) else False
        required_match_flag = True if self.regex.REQUIRED_STRING.findall(ingredient) else False
        
        # check if any of the words in the ingredient string are in the optional or required sets
        optional_str_flag = any([True if word in optional_set else False for word in ingredient.replace(",", " ").split()])
        required_str_flag = any([True if word in required_set else False for word in ingredient.replace(",", " ").split()])

        # if any "required" strings were matched or found, or if no "optional" strings were matched or found, then the ingredient is required
        is_required = (True if required_match_flag or required_str_flag else False) or (False if optional_match_flag or optional_str_flag else True)

        return is_required
    
    def _is_required(self) -> bool:
        """
        Check if the ingredient is required or optional
        Returns a boolean indicating whether the ingredient is required or optional.
        """

        # check if the ingredient string contains the word "optional" or "required"
        ingredient_is_required = self._check_if_required_string(self.reduced_ingredient)

        # check the parenthesis content for the word "optional" or "required"
        parenthesis_is_required = self._check_if_required_parenthesis(self.parenthesis_content)

        # if BOTH of the above conditions are True then return True otherwise return False
        return True if ingredient_is_required and parenthesis_is_required else False
    
    def _address_quantity_only_parenthesis(self, parenthesis: str) -> None:
        """
        Address the case where the parenthesis content only contains a quantity.
        Attempts to update self.quantity, self.unit, self.secondary_quantity, and self.secondary_unit given 
        information from the parenthesis string and the current self.quantity and self.unit
        (e.g. "(3)", "(2.5)", "(1/2)")
        Args:
            parenthesis (str): The content of the parenthesis in the ingredient string.

        Returns:
            None
        """
        
        print(f"""
        Ingredient: '{self.reduced_ingredient}'
        Parenthesis: '{parenthesis}'
        self.quantity: '{self.quantity}'
        Unit: '{self.unit}'""") if self.debug else None
        
        # Set a None Description
        description = None

        # pull out the parenthesis quantity values
        numbers_only = self.regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(parenthesis)
        # numbers_only = [item for i in [self.regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]
        
        # if no numbers only parenthesis, then just return the original ingredient
        if not numbers_only:
            print(f"\n > Return early from QUANTITY parenthesis") if self.debug else None
            description = f"not a quantity only parenthesis"
            self.parenthesis_notes.append(description)
            return

        # pull out the self.quantity from the parenthesis
        parenthesis_quantity = numbers_only[0]

        # if there is not a unit or a quantity, then we can use the parenthesis number as the quantity and
        #  return the ingredient with the new quantity
        # TODO: OR the unit MIGHT be the food OR might be a "SOMETIMES_UNIT", maybe do that check here, not sure yet...
        if not self.quantity and not self.unit:
            description = f"maybe unit is: the 'food' or a 'sometimes unit'"
            self.parenthesis_notes.append(description)

            self.quantity = parenthesis_quantity
            return
        
        # if there is a quantity but no unit, we can try to merge (multiply) the current quantity and the parenthesis quantity 
        # then the unit is also likely the food 
        # TODO: OR the unit MIGHT be the food OR might be a "SOMETIMES_UNIT", maybe do that check here, not sure yet...
        if self.quantity and not self.unit:
            updated_quantity = str(float(self.quantity) * float(parenthesis_quantity))
            
            description = f"maybe unit is: the 'food' or a 'sometimes unit'"
            self.parenthesis_notes.append(description)

            # set the secondary quantity to the ORIGINAL quantity/units
            self.secondary_quantity = self.quantity 

            # Update the quantity with the updated merged quantity
            self.quantity = updated_quantity
            
            # return [updated_quantity, self.unit, description]
            return
        
        # if there is a unit but no quantity, then we can use the parenthesis number as the quantity and 
        # return the ingredient with the new quantity
        if not self.quantity and self.unit:
            # updated_quantity = numbers_only[0]
            description = f"used quantity from parenthesis"
            self.parenthesis_notes.append(description)

            # set the secondary quantity to the ORIGINAL quantity/units
            self.secondary_quantity = self.quantity 

            # set the quantity to the parenthesis quantity
            self.quantity = parenthesis_quantity

            return

        # if there is a quantity and a unit, then we can try
        # to merge (multiply) the current quantity and the parenthesis quantity
        # then return the ingredient with the new quantity
        if self.quantity and self.unit:
            # if there is a quantity and a unit, then we can try to merge (multiply) the current quantity and the parenthesis quantity
            # then return the ingredient with the new quantity

            description = f"multiplied starting quantity with parenthesis quantity"
            self.parenthesis_notes.append(description)

            updated_quantity = str(float(self.quantity) * float(parenthesis_quantity))

            # set the secondary quantity to the ORIGINAL quantity/units
            self.secondary_quantity = self.quantity 

            # Update the quantity with the updated merged quantity (original quantity * parenthesis quantity)
            self.quantity = updated_quantity

            return

        description = f"used quantity from parenthesis with quantity only"
        self.parenthesis_notes.append(description)
        
        # set the secondary quantity to the ORIGINAL quantity/units
        self.secondary_quantity = self.quantity 

        # update the quantity with the parenthesis quantity value
        self.quantity = parenthesis_quantity

        return
    
    def _address_equivalence_parenthesis(self, parenthesis: str) -> None:
        """
        Address the case where the parenthesis content contains any equivalence strings like "about" or "approximately", followed by a quantity and then a unit later in the sting.
        Attempts to update self.quantity, self.unit, self.secondary_quantity, and self.secondary_unit given 
        information from the parenthesis string and the current self.quantity and self.unit
        e.g. "(about 3 ounces)", "(about a 1/3 cup)", "(approximately 1 large tablespoon)"

        Args:
            parenthesis (str): A string containing parenthesis from the ingredients string
        Returns:
            None
        """


        print(f"""
        Ingredient: '{self.reduced_ingredient}'
        Parenthesis: '{parenthesis}'
        Quantity: '{self.quantity}'
        Unit: '{self.unit}'""") if self.debug else None
        
        # Set a None Description
        description = None

        # check for the equivelency pattern (e.g. "<equivelent string> <quantity> <unit>" )
        equivalent_quantity_unit = self.regex.EQUIV_QUANTITY_UNIT_GROUPS.findall(parenthesis)
        # equivalent_quantity_unit = [item for i in [regex.EQUIV_QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] for item in i]

        # remove parenthesis and then split on whitespace
        split_parenthesis = parenthesis.replace("(", "").replace(")", "").split()

        # Case when: NO equivelence quantity unit matches 
        #           OR parenthesis contains a quantity per unit like string in the parenthesis (i.e. "(about 2 ounces each)" contains "each")
        # Then return early with NO UPDATES and keep the current quantity/unit as is
        if not equivalent_quantity_unit or any([True if i in self.regex.constants["QUANTITY_PER_UNIT_STRINGS"] else False for i in split_parenthesis]):
            print(f"\n > Return early from EQUIVALENCE parenthesis") if self.debug else None
            description = f"not a equivalence quantity unit parenthesis"
            self.parenthesis_notes.append(description)
            return
        
        # pull out the suffix word, parenthesis quantity and unit
        parenthesis_suffix, parenthesis_quantity, parenthesis_unit = equivalent_quantity_unit[0]
        
        # Case when: NO quantity, NO unit:
            # if no quantity AND no unit, then we can use the parenthesis quantity-unit as our quantity and unit
        if not self.quantity and not self.unit:

            description = f"used equivalence quantity unit as our quantity and unit"
            self.parenthesis_notes.append(description)

            # set quantity/unit to the parenthesis values
            self.quantity = parenthesis_quantity
            self.unit = parenthesis_unit

            return
        
        # Case when: YES quantity, NO unit:
            # we can assume the equivelent quantity units 
            # in the parenthesis are actually a better fit for the quantities and units so 
            # we can use those are our quantities/units and then stash the original quantity in the "description" field 
            # with a "maybe quantity is " prefix in front of the original quantity for maybe use later on
        if self.quantity and not self.unit:

            # stash the old quantity with a trailing string before changing best_quantity
            description = f"maybe quantity is: {' '.join(self.quantity)}"
            self.parenthesis_notes.append(description)

            # make the secondary_quantity the starting quantity before converting the quantity to the value found in the parenthesis
            self.secondary_quantity = self.quantity

            # set the quantity/unit to the parenthesis values
            self.quantity = parenthesis_quantity
            self.unit = parenthesis_unit

            return 

        # Case when: NO quantity, YES unit:
            # if there is no quantity BUT there IS a unit, then the parenthesis units/quantities are probably "better" so use the
            # parenthesis quantity/units and then stash the old unit in the description
        if not self.quantity and self.unit:

            # stash the old quantity with a trailing "maybe"
            description = f"maybe unit is: {self.unit}"
            self.parenthesis_notes.append(description)

            # make the secondary_unit the starting unit before converting the unit to the unit string found in the parenthesis
            self.secondary_unit = self.unit

            self.quantity = parenthesis_quantity
            self.unit = parenthesis_unit

            # return [parenthesis_quantity, parenthesis_unit, description]
            return 
        
        # Case when: YES quantity, YES unit:
            # if we already have a quantity AND a unit, then we likely found an equivalent quantity/unit
            # we will choose to use the quantity/unit pairing that is has a unit in the BASIC_UNITS_SET
        if self.quantity and self.unit:
            parenthesis_unit_is_basic = parenthesis_unit in self.regex.constants["BASIC_UNITS_SET"]
            unit_is_basic = self.unit in self.regex.constants["BASIC_UNITS_SET"]

            # Case when BOTH are basic units:  (# TODO: Maybe we should use parenthesis quantity/unit instead...?)
            #   use the original quantity/unit (stash the parenthesis in the description)
            if parenthesis_unit_is_basic and unit_is_basic:
                description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
                self.parenthesis_notes.append(description)
                # return [self.quantity, self.unit, description]

                # set the secondary quantity/units to the values in the parenthesis
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit

                return
            
            # Case when NEITHER are basic units:    # TODO: this can be put into the above condition but thought separated was more readible.
            #   use the original quantity/unit (stash the parenthesis in the description)
            if not parenthesis_unit_is_basic and not unit_is_basic:
                description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
                self.parenthesis_notes.append(description)
                # return [self.quantity, self.unit, description]
                
                # set the secondary quantity/units to the values in the parenthesis
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit

                return

            # Case when: YES basic parenthesis unit, NO basic original unit: 
            #   then use the parenthesis quantity/unit (stash the original in the description)
            if parenthesis_unit_is_basic:
                description = f"maybe quantity/unit is: {self.quantity}/{self.unit}"
                self.parenthesis_notes.append(description)
                
                # set the secondary quantity/units to the original quantity/units
                self.secondary_quantity = self.quantity
                self.secondary_unit = self.unit

                # update the primary quantities/units to the parenthesis values
                self.quantity = parenthesis_quantity
                self.unit = parenthesis_unit
                
                # return [parenthesis_quantity, parenthesis_unit, description]
                return

            # Case when: NO basic parenthesis unit, YES basic original unit: 
            #   then use the original quantity/unit (stash the parenthesis in the description)
            if unit_is_basic:
                description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the original quantity/units
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit

                return

        description = f"used quantity/units from parenthesis with equivalent quantity/units"
        self.parenthesis_notes.append(description)

        # set the secondary quantity/units to the original quantity/units
        self.secondary_quantity = self.quantity
        self.secondary_unit = self.unit

        self.quantity = parenthesis_quantity
        self.unit = parenthesis_unit

        return
    
    def _address_quantity_unit_only_parenthesis(self, parenthesis: str) -> None:
        """
        Address the case where the parenthesis content contains exactly a quantity and unit (NOT prefixed by any equivalence strings like "about" or "approximately").
        Attempts to update self.quantity, self.unit, self.secondary_quantity, and self.secondary_unit given 
        information from the parenthesis string and the current self.quantity and self.unit
        e.g. "(3 ounces)", "(3 ounces each)", "(a 4 cup scoop)"

        Args:
            parenthesis (str): A string containing parenthesis from the ingredients string
        Returns:
            None
        """


        print(f"""
        Ingredient: '{self.reduced_ingredient}'
        Parenthesis: '{parenthesis}'
        Quantity: '{self.quantity}'
        Unit: '{self.unit}'""") if self.debug else None

        # Set a None Description
        description = None

        # pull out quantity unit only pattern
        quantity_unit_only = self.regex.QUANTITY_UNIT_GROUPS.findall(parenthesis)
        # quantity_unit_only = [item for i in [self.regex.QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] for item in i]

        # if no numbers only parenthesis, then just return the original ingredient
        if not quantity_unit_only:
            print(f"\n > Return early from QUANTITY UNIT parenthesis") if self.debug else None
            description = f"not a quantity unit only parenthesis"
            self.parenthesis_notes.append(description)
            # return [self.quantity, unit, description]
            return
        
        # pull out the parenthesis quantity and unit
        parenthesis_quantity, parenthesis_unit = quantity_unit_only[0]

        # Case when: NO quantity, NO unit:
            # if no quantity AND no unit, then we can use the parenthesis self.quantity-unit as our self.quantity and unit
        if not self.quantity and not self.unit:
            # updated_quantity, updated_unit = quantity_unit_only[0]
            print(f"\n > Case when: NO quantity, NO unit") if self.debug else None

            description = f"used quantity/unit from parenthesis with no quantity/unit"
            self.parenthesis_notes.append(description)

            # set the secondary quantity/units to the original quantity/units
            self.secondary_quantity = self.quantity
            self.secondary_unit = self.unit

            self.quantity = parenthesis_quantity
            self.unit = parenthesis_unit

            # return [parenthesis_quantity, parenthesis_unit, description]
            return

        # Case when: YES quantity, NO unit:
            # if there is a quantity but no unit, we can try to merge (multiply) the current quantity and the parenthesis quantity 
            # then use the unit in the parenthesis
        if self.quantity and not self.unit:
            print(f"\n > Case when: YES quantity, NO unit") if self.debug else None

            # quantity_unit_only[0][0]
            updated_quantity = str(float(self.quantity) * float(parenthesis_quantity))

            description = f"multiplied starting quantity with parenthesis quantity"
            self.parenthesis_notes.append(description)

            # set the secondary quantity/units to the original quantity/units
            self.secondary_quantity = self.quantity
            self.secondary_unit = self.unit
            
            self.quantity = updated_quantity
            self.unit = parenthesis_unit

            # return [updated_quantity, parenthesis_unit, description]
            return

        # Case when: NO quantity, YES unit:
            # if there is no quantity BUT there IS a unit, then the parenthesis units/quantities are either:
            # 1. A description/note (i.e. cut 0.5 inch slices)
            # 2. A quantity and unit (i.e. 2 ounces)
            # either case, just return the parenthesis units to use those
        if not self.quantity and self.unit:
            print(f"\n > Case when: NO quantity, YES unit") if self.debug else None

            description = f"No quantity but has units, used parenthesis. maybe quantity/unit is: {self.quantity}/{self.unit}"
            self.parenthesis_notes.append(description)

            # set the secondary quantity/units to the original quantity/units
            self.secondary_quantity = self.quantity
            self.secondary_unit = self.unit

            self.quantity = parenthesis_quantity
            self.unit = parenthesis_unit

            # return [parenthesis_quantity, parenthesis_unit, description]
            return

        # # Case when: YES quantity, YES unit:
        #     # if we already have a quantity AND a unit, then we likely just found a description and that is all.
        # if self.quantity and self.unit:
        #     # use the parenthesis values as a description and join the values together 
        #     description = f"maybe quantity/unit is: {' '.join(quantity_unit_only[0])}"
        #     self.parenthesis_notes.append(description)
        #     # return [self.quantity, unit, description]
        #     return

        # Case when: YES quantity, YES unit:
            # if we already have a quantity AND a unit, then we likely just found a description 
            # OR we may have found an equivalence quantity unit.
            # we will choose to use the quantity/unit pairing that is has a unit in the BASIC_UNITS_SET
        if self.quantity and self.unit:
            print(f"\n > Case when: YES quantity, YES unit") if self.debug else None

            # flags for if original unit/parenthesis unit are in the set of basic units (BASIC_UNITS_SET) or not
            parenthesis_unit_is_basic = parenthesis_unit in self.regex.constants["BASIC_UNITS_SET"]
            unit_is_basic = self.unit in self.regex.constants["BASIC_UNITS_SET"]

            # Case when BOTH are basic units: 
            #   use the original quantity/unit (stash the parenthesis in the description)
            if parenthesis_unit_is_basic and unit_is_basic:
                print(f"\n >>> Case when: BASIC parenthesis unit, BASIC unit") if self.debug else None

                description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the parenthesis quantity/units
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit
                return
            
            # Case when NEITHER are basic units:    # TODO: this can be put into the above condition but thought separated was more readible.
            #   use the original quantity/unit AND set the secondary quantity/units to the PARENTHESIS values 
            #   (stash the parenthesis in the description)
            if not parenthesis_unit_is_basic and not unit_is_basic:
                print(f"\n >>> Case when: NOT BASIC parenthesis unit, NOT BASIC unit") if self.debug else None
                description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the parenthesis quantity/units
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit
                return

            # Case when: YES basic parenthesis unit, NO basic original unit (EXPLICIT):
            #  Try to merge (multiply) the current quantity and the parenthesis quantity
            #  AND set the secondary quantity/units to the ORIGINAL values
            if parenthesis_unit_is_basic and not unit_is_basic:
                print(f"\n >>> Case when: BASIC parenthesis unit, NOT BASIC unit (EXPLICIT)") if self.debug else None
                updated_quantity = str(float(self.quantity) * float(parenthesis_quantity))

                description = f"multiplied starting quantity with parenthesis quantity"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the original quantity/units
                self.secondary_quantity = self.quantity
                self.secondary_unit = self.unit

                self.quantity = updated_quantity
                self.unit = parenthesis_unit

                return

            # TODO: I think this condition can be dropped, gets covered by previous condition...
            # Case when: YES basic parenthesis unit, NO basic original unit (IMPLICITLY): 
            #   then use the parenthesis quantity/unit AND set the secondary quantity/units to the ORIGINAL values
            #   (stash the original in the description)
            if parenthesis_unit_is_basic:
                print(f"\n >>> Case when: BASIC parenthesis unit, NOT BASIC unit (IMPLICIT)") if self.debug else None
                description = f"maybe quantity/unit is: {self.quantity}/{self.unit}"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the original quantity/units
                self.secondary_quantity = self.quantity
                self.secondary_unit = self.unit

                self.quantity = parenthesis_quantity
                self.unit = parenthesis_unit

                return

            # Case when: NO basic parenthesis unit, YES basic original unit: 
            #   then just keep the original quantity/unit AND set the secondary quantity/units to the PARENTHESIS values
            #   (stash the original in the description)
            if unit_is_basic:
                print(f"\n >>> Case when: NOT BASIC parenthesis unit, BASIC unit (IMPLICIT)") if self.debug else None
                description = f"maybe quantity/unit is: {self.quantity}/{self.unit}"
                self.parenthesis_notes.append(description)

                # set the secondary quantity/units to the parenthesis quantity/units
                self.secondary_quantity = parenthesis_quantity
                self.secondary_unit = parenthesis_unit

                return
        
        print(f"\n ----> Case when: ALL OTHER CASES FAILED") if self.debug else None

        # TODO: Don't think this should ever happen, need to rethink this part
        # Case when: All other conditions were NOT met:
            # just set the quantity/unit to the parenthesis values 
            # and then put the original quantity/units in the secondary quantity/units
        description = f"used quantity/units from parenthesis with quantity/units only"
        self.parenthesis_notes.append(description)

        # set the secondary quantity/units to the ORIGINAL quantity/units
        self.secondary_quantity = self.quantity 
        self.secondary_unit = self.unit

        # set the primary quantity/units to the parenthesis quantity/units
        self.quantity = parenthesis_quantity
        self.unit = parenthesis_unit

        return
    
    def _add_standard_units(self) -> None:
        """
        Add standard units to the parsed ingredient if they are present in the
        constants units to standard units map.
        If the "unit"/"secondary_unit" exists and it is present in the unit to standard unit map, 
        then get the standard unit name for the unit and set the "standard_unit" and "standard_secondary_unit" member variables.
        """

        if self.unit and self.unit in self.regex.constants["UNIT_TO_STANDARD_UNIT"]:
            self.standard_unit = self.regex.constants["UNIT_TO_STANDARD_UNIT"][self.unit]
        
        if self.secondary_unit and self.secondary_unit in self.regex.constants["UNIT_TO_STANDARD_UNIT"]:
            self.standard_secondary_unit = self.regex.constants["UNIT_TO_STANDARD_UNIT"][self.secondary_unit]

        return 
    
    def _prioritize_weight_units(self) -> None:
        """
        Prioritize weight units over volume units if both are present in the parsed ingredient.
        If the first unit is not a weight unit but the secondary_unit is a weight unit, then swap them so 
        the weight unit is always given as the primary unit.
        (i.e. unit = "cups", secondary_unit = "ounces" --> Swap them so that unit = "ounces" and secondary_unit = "cups")
        """

        # # if the first unit is already a weight, just return early
        if self.unit in self.regex.constants["WEIGHT_UNITS_SET"]:
            return 
        
        # TODO: first part of this if statement is probably redundent...
        # if the first unit is NOT a weight and the second unit IS a weight, then swap them
        if self.unit not in self.regex.constants["WEIGHT_UNITS_SET"] and self.secondary_unit in self.regex.constants["WEIGHT_UNITS_SET"]:

            print(f"Swapping first quantity/units with second quantity/units")
            # print(f"Swapping first quantity/units with second quantity/units") if self.debug else None

            # switch the units and quantities with the secondary units and quantities
            self.quantity, self.secondary_quantity = self.secondary_quantity, self.quantity
            self.unit, self.secondary_unit = self.secondary_unit,  self.unit
            self.standard_unit, self.standard_secondary_unit = self.standard_secondary_unit, self.standard_unit

            # parsed_obj["quantity"], parsed_obj["secondary_quantity"] = parsed_obj["secondary_quantity"], parsed_obj["quantity"]
            # parsed_obj["unit"], parsed_obj["secondary_unit"] = parsed_obj["secondary_unit"], parsed_obj["unit"]
            # parsed_obj["standard_unit"], parsed_obj["standard_secondary_unit"] = parsed_obj["standard_secondary_unit"], parsed_obj["standard_unit"]
        
        return 

    def parse(self):
        # TODO: process parenthesis content

        print(f"Standardizing ingredient: \n > '{self.ingredient}'") if self.debug else None
        # print(f"Standardizing ingredient: \n > '{self.ingredient}'")

        # ----------------------------------- STEP 1 ------------------------------------------
        # ---- Get the input ingredient string into a standardized form ----
        # -------------------------------------------------------------------------------------

        # run the standardization method to cleanup raw ingredient and create the "standard_ingredient" and "reduced_ingredient" member variables 
        self.standardize()

        print(f"Standardized ingredient: \n > '{self.standard_ingredient}'") if self.debug else None
        print(f"Reduced ingredient: \n > '{self.reduced_ingredient}'") if self.debug else None
        print(f"Extracting first quantity and unit from reduced ingredient: \n > '{self.reduced_ingredient}'") if self.debug else None
        # print(f"Standardized ingredient: \n > '{self.standard_ingredient}'")
        # print(f"Reduced ingredient: \n > '{self.reduced_ingredient}'")
        # print(f"Extracting first quantity and unit from reduced ingredient: \n > '{self.reduced_ingredient}'")

        # ----------------------------------- STEP 2 ------------------------------------------
        # ---- Check if there is any indication of the ingredient being required/optional ----
        # -------------------------------------------------------------------------------------

        # run the is_required method to check if the ingredient is required or optional and set the "is_required" member variable to the result
        self.is_required = self._is_required()

        print(f"Is the ingredient required? {self.is_required}") if self.debug else None

        # ----------------------------------- STEP 3 ------------------------------------------
        # ---- Extract first options of quantities and units from the "reduced_ingredient" ----
        # -------------------------------------------------------------------------------------

        #  reduced_ingredient ---> (i.e. standardized ingredient with parenthesis content removed)
        # run the extract_first_quantity_unit method to extract the first unit and quantity from the ingredient string
        self.extract_first_quantity_unit()

        # ----------------------------------- STEP 4 ------------------------------------------
        # ---- Address any parenthesis that were in the ingredient  ----
        # -------------------------------------------------------------------------------------
        # NOTE: Stash the best_quantity and best_units before preceeding (for debugging)

        # stash the best quantity and unit for testing/debugging
        self.stashed_quantity    = self.quantity 
        self.stashed_unit        = self.unit

        print()
        print(f"CHECKING INGREDIENT AFTER STASH: {self.ingredient}")
        print(f"Ingredient: {self.ingredient}")
        print(f" > Standard ingredient: {self.standard_ingredient}")
        print(f"   > Stashed Quantity ingredient: {self.stashed_quantity}")
        print(f"   > Stashed unit ingredient: {self.stashed_unit}")
        print(f"   > Parenthesis content: {self.parenthesis_content}")
        print()

        # loop through each of the parenthesis in the parenthesis content and apply address_parenthesis functions 
        for parenthesis in self.parenthesis_content:
            print(f"Addressing parenthesis: '{parenthesis}'") if self.debug else None

            # address the case where the parenthesis content only contains a quantity
            print(f"> Apply QUANTITY Parenthesis to: '{self.quantity} {self.unit}'") if self.debug else None
            self._address_quantity_only_parenthesis(parenthesis)
            
            print(f"> Apply EQUIVALENCE Parenthesis to: '{self.quantity} {self.unit}'") if self.debug else None
            self._address_equivalence_parenthesis(parenthesis)

            print(f"> Apply QUANTITY UNIT Parenthesis to: '{self.quantity} {self.unit}'") if self.debug else None
            self._address_quantity_unit_only_parenthesis(parenthesis)

        # ----------------------------------- STEP 5 ------------------------------------------
        # ---- Get the standard names of the units and secondary units ----
        # -------------------------------------------------------------------------------------
        print(f"Adding standard unit names for {self.unit} and {self.secondary_unit}") if self.debug else None

        self._add_standard_units()

        # ----------------------------------- STEP 6 ------------------------------------------
        # ---- Prioritize weight units and always place the weight unit as the primary ingredient if it exists ----
        # -------------------------------------------------------------------------------------
        print(f"Prioritizing weight units") if self.debug else None

        self._prioritize_weight_units()


    def to_json(self) -> dict:
        """
        Convert the RecipeParser object to a dictionary.
        Returns:
            dict: A dictionary containing the RecipeParser object's member variables.
        """
        return {
            "ingredient": self.ingredient,
            "standardized_ingredient": self.standard_ingredient,
            # "reduced_ingredient": self.reduced_ingredient,
            "quantity": self.quantity,
            "unit": self.unit,
            "standard_unit": self.standard_unit,
            "secondary_quantity": self.secondary_quantity,
            "secondary_unit": self.secondary_unit,
            "standard_secondary_unit": self.standard_secondary_unit,
            "is_required": self.is_required,
            "parenthesis_content": self.parenthesis_content,
            "parenthesis_notes": self.parenthesis_notes,
            "stashed_quantity" : self.stashed_quantity,
            "stashed_unit" : self.stashed_unit
        }

# regex = RecipeRegexPatterns()

# parenthesis = [ "(2 ounces)", 
#                 "(about 3 cups)",
#                 "(3)",
#                 "(3 ounces each)", 
#                 "(3 each)",
#                 "(about 4 cups each)", 
#                 "(about a couple of 3 tablespoons)", 
#                 "(3 ounces about)"
#                   ]
# regex.print_matches(parenthesis[3])

# ingredient = "(about a couple of 3 tablespoons)"
# split_ingredient = ingredient.replace("(", "").replace(")", "").split()
# print(f"split_ingredient: {split_ingredient}")
# regex.constants.keys()
# [i for i in split_ingredient if i in regex.constants["AP:"]]
# for p in parenthesis:

#     # parsed_p = p.replace("(", "").replace(")", "").split()
#     # quantity_units = regex.QUANTITY_UNIT_GROUPS(p)
#     quantity_units = regex.QUANTITY_UNIT_GROUPS.findall(p)
#     print(f"p: {p}")
#     print(f"quantity_units: {quantity_units}")
#     print()
#     # print(f"parsed_p: {parsed_p}")

# ###############################################################################################################
# ######################################## check_if_required() function ##########################################
# ###############################################################################################################
# ingredient = "1/4 teaspoon crushed (0.25 ounces) (required) red pepper (optional)"
# ingredient = "1/4 teaspoon crushed red peppe"
# ingredient = "1 large yellow onion, cut into 1/4-inch-thick slices (about 3 cups)"
# # ingredient = "salmon fillets (3)"
# # # # # # ingredient = "salmon (3)"
# # # # ingredient = "2 8 ounce salmon fillets (3)"
# # # # ingredient = "2 salmon fillets (3)"
# # # # ingredient = "4 salmon fillets (8 ounces)"
# ingredient = "4 salmon fillets (8-ounces)"

# # # # # # # # # # ingredient = "1/4 teaspoon crushed (optional) red pepper"
# regex = RecipeRegexPatterns()
# parser = RecipeParser(ingredient=ingredient, regex=regex, debug=False)
# parser.parse()
# parser.to_json()
# parser.parenthesis_content
# parser.reduced_ingredient
# parser.is_required
# parser.best_quantity
# parser.best_unit
# parser.parenthesis_notes

# address_equivalence_parenthesis(parser.reduced_ingredient, 
#                                   parser.parenthesis_content,
#                                   parser.best_quantity, 
#                                   parser.best_unit)
# address_quantity_only_parenthesis(parser.reduced_ingredient, 
#                                   parser.parenthesis_content,
#                                   parser.best_quantity, 
#                                   parser.best_unit)
# address_quantity_unit_only_parenthesis(parser.reduced_ingredient, parser.parenthesis_content, parser.best_quantity, parser.best_unit)
# def address_equivalence_parenthesis(self, parenthesis: str) -> None:
#     """
#     Address the case where the parenthesis content contains exactly a quantity and unit only
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#          List[str]: List of strings containing [updated quantity, updated unit, and description]
#     """

#     # unit = parser.best_unit
#     # quantity = parser.best_quantity
#     # ingredient = parser.reduced_ingredient
#     # parenthesis = parser.parenthesis_content

#     print(f"""
#     Ingredient: '{ingredient}'
#     Parenthesis: '{parenthesis}'
#     Quantity: '{self.quantity}'
#     Unit: '{self.unit}'""")

#     # parenthesis
#     # regex.print_matches("(8- dfs ounces)")
#     # regex.print_matches(parenthesis[0])
#     # parenthesis = ["(optional)", "(2 ounces)", "(about 3 cups)", "(3)"]

#     # [item for i in [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]
#     # [regex.QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] 
#     # [regex.QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
#     # [QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
    
#     # Set a None Description
#     description = None

#     # check for the equivelency pattern (e.g. "<equivelent string> <quantity> <unit>" )
#     equivalent_quantity_unit = regex.EQUIV_QUANTITY_UNIT_GROUPS.findall(parenthesis)
#     # equivalent_quantity_unit = [item for i in [regex.EQUIV_QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] for item in i]

#     # if there is NO equivelence quantity unit matches, then just return the original ingredient
#     if not equivalent_quantity_unit:
#         description = f"not a equivalence quantity unit parenthesis"
#         self.parenthesis_notes.append(description)
#         # return [self.quantity, self.unit, description]
#         return
    
#     # pull out the suffix word, parenthesis quantity and unit
#     parenthesis_suffix, parenthesis_quantity, parenthesis_unit = equivalent_quantity_unit[0]

#     # if no quantity AND no unit, then we can use the parenthesis quantity-unit as our quantity and unit
#     if not self.quantity and not self.unit:
#         # updated_quantity, updated_unit = quantity_unit_only[0]
#         # [item for i in list(quantity_unit_only[0][1:]) for item in i]

#         description = f"used equivalence quantity unit as our quantity and unit"
        # self.parenthesis_notes.append(description)

        # self.quantity = parenthesis_quantity
        # self.unit = parenthesis_unit

#         # return [parenthesis_quantity, parenthesis_unit, description]
#         return
    
#     # if there is a quantity but no unit, we can assume the equivelent quantity units 
#     # in the parenthesis are actually a better fit for the quantities and units so 
#     # we can use those are our quantities/units and then stash the original quantity in the "description" field 
#     # with a "maybe quantity is " prefix in front of the original quantity for maybe use later on
#     if self.quantity and not self.unit:

#         # stash the old quantity with a trailing string before changing best_quantity
#         description = f"maybe quantity is: {' '.join(self.quantity)}"
#         self.parenthesis_notes.append(description)

#         self.quantity = parenthesis_quantity
#         self.unit = parenthesis_unit

#         # return [parenthesis_quantity, parenthesis_unit, description]
#         return 

#     # if there is no quantity BUT there IS a unit, then the parenthesis units/quantities are probably "better" so use the
#     # parenthesis quantity/units and then stash the old unit in the description
#     if not self.quantity and self.unit:

#         # stash the old quantity with a trailing "maybe"
#         description = f"maybe unit is: {self.unit}"
#         self.parenthesis_notes.append(description)

#         self.quantity = parenthesis_quantity
#         self.unit = parenthesis_unit

#         # return [parenthesis_quantity, parenthesis_unit, description]
#         return 

#     # if we already have a quantity AND a unit, then we likely found an equivalent quantity/unit
#     # we will choose to use the quantity/unit pairing that is has a unit in the BASIC_UNITS_SET
#     # Case when BOTH are basic units: then we will use the original quantity/unit (# TODO: Maybe we should use parenthesis quantity/unit instead...?)
#     # Case when NEITHER are basic units: then we will use the original quantity/unit (# TODO: Maybe we should use parenthesis quantity/unit instead...?)
#     if self.quantity and unit:
#         parenthesis_unit_is_basic = parenthesis_unit in regex.constants["BASIC_UNITS_SET"]
#         unit_is_basic = self.unit in regex.constants["BASIC_UNITS_SET"]

#         # Case when BOTH are basic units: 
#         #   use the original quantity/unit (stash the parenthesis in the description)
#         if parenthesis_unit_is_basic and unit_is_basic:
#             description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
#             self.parenthesis_notes.append(description)
#             # return [self.quantity, self.unit, description]
#             return
        
#         # Case when NEITHER are basic units:    # TODO: this can be put into the above condition but thought separated was more readible.
#         #   use the original quantity/unit (stash the parenthesis in the description)
#         if not parenthesis_unit_is_basic and not unit_is_basic:
#             description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
#             self.parenthesis_notes.append(description)
#             # return [self.quantity, self.unit, description]
#             return

#         # Case when the parenthesis unit is a basic unit (original is NOT basic unit): 
#         #   then use the parenthesis quantity/unit (stash the original in the description)
#         if parenthesis_unit_is_basic:
#             description = f"maybe quantity/unit is: {self.quantity}/{self.unit}"
#             self.parenthesis_notes.append(description)

#             self.quantity = parenthesis_quantity
#             self.unit = parenthesis_unit
            
#             # return [parenthesis_quantity, parenthesis_unit, description]
#             return
        
#         # Case when the original unit is a basic unit (parenthesis is NOT basic unit): 
#         #   then use the original quantity/unit (stash the parenthesis in the description)
#         if parenthesis_unit_is_basic:
#             description = f"maybe quantity/unit is: {self.quantity}/{self.unit}"
#             self.parenthesis_notes.append(description)

#             self.quantity = parenthesis_quantity
#             self.unit = parenthesis_unit

#             # return [parenthesis_quantity, parenthesis_unit, description]
#             return

#     # return [quantity, unit, description]
#     description = f"used quantity/units from parenthesis with equivalent quantity/units"
#     self.parenthesis_notes.append(description)

#     self.quantity = parenthesis_quantity
#     self.unit = parenthesis_unit
#     # return [parenthesis_quantity, parenthesis_unit, description]
#     return

# def address_equivalence_parenthesis(ingredient: str, parenthesis: str, quantity: str, unit: str) -> List[str]:
#     """
#     Address the case where the parenthesis content contains exactly a quantity and unit only
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#          List[str]: List of strings containing [updated quantity, updated unit, and description]
#     """

#     # unit = parser.best_unit
#     # quantity = parser.best_quantity
#     # ingredient = parser.reduced_ingredient
#     # parenthesis = parser.parenthesis_content

#     print(f"""
#     Ingredient: '{ingredient}'
#     Parenthesis: '{parenthesis}'
#     Quantity: '{quantity}'
#     Unit: '{unit}'""")

#     # parenthesis
#     # regex.print_matches("(8- dfs ounces)")
#     # regex.print_matches(parenthesis[0])
#     # parenthesis = ["(optional)", "(2 ounces)", "(about 3 cups)", "(3)"]

#     # [item for i in [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]
#     # [regex.QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] 
#     # [regex.QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
#     # [QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
    
#     # Set a None Description
#     description = None

#     # check for the equivelency pattern (e.g. "<equivelent string> <quantity> <unit>" )
#     equivalent_quantity_unit = [item for i in [regex.EQUIV_QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] for item in i]

#     # if there is NO equivelence quantity unit matches, then just return the original ingredient
#     if not equivalent_quantity_unit:
#         return [quantity, unit, description]
    
#     # pull out the suffix word, parenthesis quantity and unit
#     parenthesis_suffix, parenthesis_quantity, parenthesis_unit = equivalent_quantity_unit[0]

#     # if no quantity AND no unit, then we can use the parenthesis quantity-unit as our quantity and unit
#     if not quantity and not unit:
#         # updated_quantity, updated_unit = quantity_unit_only[0]
#         # [item for i in list(quantity_unit_only[0][1:]) for item in i]
#         return [parenthesis_quantity, parenthesis_unit, description]
    
#     # if there is a quantity but no unit, we can assume the equivelent quantity units 
#     # in the parenthesis are actually a better fit for the quantities and units so 
#     # we can use those are our quantities/units and then stash the original quantity in the "description" field 
#     # with a "maybe quantity is " prefix in front of the original quantity for maybe use later on
#     if quantity and not unit:

#         # stash the old quantity with a trailing "maybe"
#         description = f"maybe quantity is: {' '.join(quantity)}"

#         return [parenthesis_quantity, parenthesis_unit, description]

#     # if there is no quantity BUT there IS a unit, then the parenthesis units/quantities are probably "better" so use the
#     # parenthesis quantity/units and then stash the old unit in the description
#     if not quantity and unit:
#         # stash the old quantity with a trailing "maybe"
#         description = f"maybe unit is: {unit}"

#         return [parenthesis_quantity, parenthesis_unit, description]

#     # if we already have a quantity AND a unit, then we likely found an equivalent quantity/unit
#     # we will choose to use the quantity/unit pairing that is has a unit in the BASIC_UNITS_SET
#     # Case when BOTH are basic units: then we will use the original quantity/unit (# TODO: Maybe we should use parenthesis quantity/unit instead...?)
#     # Case when NEITHER are basic units: then we will use the original quantity/unit (# TODO: Maybe we should use parenthesis quantity/unit instead...?)
#     if quantity and unit:
#         parenthesis_unit_is_basic = parenthesis_unit in regex.constants["BASIC_UNITS_SET"]
#         unit_is_basic = unit in regex.constants["BASIC_UNITS_SET"]

#         # Case when BOTH are basic units: 
#         #   use the original quantity/unit (stash the parenthesis in the description)
#         if parenthesis_unit_is_basic and unit_is_basic:
#             description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
#             return [quantity, unit, description]
        
#         # Case when NEITHER are basic units:    # TODO: this can be put into the above condition but thought separated was more readible.
#         #   use the original quantity/unit (stash the parenthesis in the description)
#         if not parenthesis_unit_is_basic and not unit_is_basic:
#             description = f"maybe quantity/unit is: {parenthesis_quantity}/{parenthesis_unit}"
#             return [quantity, unit, description]

#         # Case when the parenthesis unit is a basic unit (original is NOT basic unit): 
#         #   then use the parenthesis quantity/unit (stash the original in the description)
#         if parenthesis_unit_is_basic:
#             description = f"maybe quantity/unit is: {quantity}/{unit}"
#             return [parenthesis_quantity, parenthesis_unit, description]
        
#         # Case when the original unit is a basic unit (parenthesis is NOT basic unit): 
#         #   then use the original quantity/unit (stash the parenthesis in the description)
#         if parenthesis_unit_is_basic:
#             description = f"maybe quantity/unit is: {quantity}/{unit}"
#             return [parenthesis_quantity, parenthesis_unit, description]

#     # return [quantity, unit, description]
#     description = f"used quantity/units from parenthesis with equivalent quantity/units"
#     return [parenthesis_quantity, parenthesis_unit, description]


# # # # unit = parser.best_unit
# # # # quant = parser.best_quantity
# def _address_quantity_unit_only_parenthesis(self, parenthesis: str) -> None:
#     """
#     Address the case where the parenthesis content contains exactly a quantity and unit only
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         None
#     """

#     # unit = parser.best_unit
#     # quantity = parser.best_quantity
#     # ingredient = parser.reduced_ingredient
#     # parenthesis = parser.parenthesis_content

#     print(f"""
#     Ingredient: '{self.reduced_ingredient}'
#     Parenthesis: '{parenthesis}'
#     Quantity: '{self.quantity}'
#     Unit: '{self.unit}'""")

#     # parenthesis
#     # regex.print_matches("(8- dfs ounces)")
#     # regex.print_matches(parenthesis[0])
#     # parenthesis = ["(optional)", "(2 ounces)", "(about 3 cups)", "(3)"]

#     # [item for i in [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]
#     # [regex.QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] 
#     # [regex.QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
#     # [QUANTITY_UNIT_ONLY_GROUPS.findall(i) for i in parenthesis] 
    
#     # Set a None Description
#     description = None

#     quantity_unit_only = self.regex.QUANTITY_UNIT_GROUPS.findall(parenthesis)
#     # quantity_unit_only = [item for i in [self.regex.QUANTITY_UNIT_GROUPS.findall(i) for i in parenthesis] for item in i]

#     # if no numbers only parenthesis, then just return the original ingredient
#     if not quantity_unit_only:
#         description = f"not a quantity unit only parenthesis"
#         self.parenthesis_notes.append(description)
#         # return [self.quantity, unit, description]
#         return
    
#     # pull out the parenthesis quantity and unit
#     parenthesis_quantity, parenthesis_unit = quantity_unit_only[0]

#     # if no quantity AND no unit, then we can use the parenthesis self.quantity-unit as our self.quantity and unit
#     if not self.quantity and not self.unit:
#         # updated_quantity, updated_unit = quantity_unit_only[0]

#         description = f"used quantity/unit from parenthesis with no quantity/unit"
#         self.parenthesis_notes.append(description)

#         self.quantity = parenthesis_quantity
#         self.unit = parenthesis_unit

#         # return [parenthesis_quantity, parenthesis_unit, description]
#         return
    
#     # if there is a quantity but no unit, we can try to merge (multiply) the current quantity and the parenthesis quantity 
#     # then use the unit in the parenthesis
#     if self.quantity and not self.unit:
#         # quantity_unit_only[0][0]
#         updated_quantity = str(float(self.quantity) * float(parenthesis_quantity))

#         description = f"multiplied starting quantity with parenthesis quantity"
#         self.parenthesis_notes.append(description)

#         self.quantity = updated_quantity
#         self.unit = parenthesis_unit

#         # return [updated_quantity, parenthesis_unit, description]
#         return

#     # if there is no quantity BUT there IS a unit, then the parenthesis units/quantities are either:
#     # 1. A description/note (i.e. cut 0.5 inch slices)
#     # 2. A quantity and unit (i.e. 2 ounces)
#     # either case, just return the parenthesis units to use those
#     if not self.quantity and self.unit:
        
#         description = f"No quantity but has units, used parenthesis. maybe quantity/unit is: {self.quantity}/{self.unit}"
#         self.parenthesis_notes.append(description)

#         self.quantity = parenthesis_quantity
#         self.unit = parenthesis_unit

#         # return [parenthesis_quantity, parenthesis_unit, description]
#         return

#     # if we already have a quantity AND a unit, then we likely just found a description and that is all.
#     if self.quantity and self.unit:
#         # use the parenthesis values as a description and join the values together 
#         description = f"maybe quantity/unit is: {' '.join(quantity_unit_only[0])}"
#         self.parenthesis_notes.append(description)
#         # return [self.quantity, unit, description]
#         return
    
#     description = f"used quantity/units from parenthesis with quantity/units only"
#     self.parenthesis_notes.append(description)

#     self.quantity = parenthesis_quantity
#     self.unit = parenthesis_unit
#     # return [parenthesis_quantity, parenthesis_unit, description]
#     return

# def address_quantity_only_parenthesis(ingredient: str, parenthesis: str, quantity: str, unit: str) -> List[str]:
#     """
#     Address the case where the parenthesis content only contains a quantity.
#     Args:
#         ingredient (str): The ingredient string to parse.

#     Returns:
#         List[str]: List of strings containing [updated quantity, updated unit, and description]
#     """

#     # unit = parser.best_unit
#     # quantity = parser.best_quantity
#     # reduced = parser.reduced_ingredient
#     # parenthesis = parser.parenthesis_content

#     print(f"""
#     Ingredient: '{ingredient}'
#     Parenthesis: '{parenthesis}'
#     Quantity: '{quantity}'
#     Unit: '{unit}'""")

#     # parenthesis = ["(optional)", "(2 ounces)", "(about 3 cups)", "(3)"]

#     # [item for i in [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]
    
#     # Set a None Description
#     description = None

#     # pull out the parenthesis quantity values
#     numbers_only = [item for i in [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in parenthesis] for item in i]

#     # if no numbers only parenthesis, then just return the original ingredient
#     if not numbers_only:
#         return [quantity, unit, description]

#     # pull out the quantity from the parenthesis
#     parenthesis_quantity = numbers_only[0]

#     # if there is not a unit or a quantity, then we can use the parenthesis number as the quantity and
#     #  return the ingredient with the new quantity
#     # TODO: OR the unit MIGHT be the food OR might be a "SOMETIMES_UNIT", maybe do that check here, not sure yet...
#     if not quantity and not unit:
#         # updated_quantity = numbers_only[0]
#         description = f"maybe unit is: the 'food' or a 'sometimes unit'"
#         return [parenthesis_quantity, unit, description]
    
#     # if there is a quantity but no unit, we can try to merge (multiply) the current quantity and the parenthesis quantity 
#     # then the unit is also likely the food 
#     # TODO: OR the unit MIGHT be the food OR might be a "SOMETIMES_UNIT", maybe do that check here, not sure yet...
#     if quantity and not unit:
#         updated_quantity = str(float(quantity) * float(parenthesis_quantity))
#         description = f"maybe unit is: the 'food' or a 'sometimes unit'"
#         return [updated_quantity, unit, description]

#     # if there is a unit but no quantity, then we can use the parenthesis number as the quantity and 
#     # return the ingredient with the new quantity
#     if not quantity and unit:
#         # updated_quantity = numbers_only[0]
#         return [parenthesis_quantity, unit, description]

#     if quantity and unit:
#         # if there is a quantity and a unit, then we can try to merge (multiply) the current quantity and the parenthesis quantity
#         # then return the ingredient with the new quantity
#         updated_quantity = str(float(quantity) * float(parenthesis_quantity))
#         return [updated_quantity, unit, description]

#     description = f"used quantity from parenthesis with quantity only"
#     return [parenthesis_quantity, unit, description]


# ###############################################################################################################
# ######################################## Test the RecipeParser class ##########################################
# ###############################################################################################################
        
# ingredient_strings = [
#     "a 1/2 lemon",
#     "an orange",
#     "1 1/3 cups ground almonds",
#     "a 1-5lb lemon",
#     "1 1/2 cups plus 2 tablespoons sugar, divided",
#     "1/2 cup freshly grated Parmesan cheese, plus more for serving",
#     "1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)",
#     "4 (1/2-ounce each) processed American cheese slices",
#     "1-2oz of butter, 20-50 grams of peanuts",
#     "1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces",
#     "1 tablespoon all-purpose flour",
#     "4 tablespoons salted butter, divided",
#     "2 large cloves garlic, minced",
#     "1/4 teaspoon salt",
#     "1/4 teaspoon crushed red pepper (optional)"
# ]

# ingredient_strings = [
#     "a lemon",
#     "a 1/2 lemon",
#     "an orange",
#     "1 1/3 cups ground almonds",
#     "1 (8 ounce) container plain yogurt",
#     "a 1-5lb lemon",
#     "1 1/2 cups plus 2 tablespoons sugar, divided",
#     "1/3 cup torn fresh basil or mint, plus more for garnish"
#     # "1/2 cup freshly grated Parmesan cheese, plus more for serving",
#     # "1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)",
#     # "4 (1/2-ounce each) processed American cheese slices",
#     # "1 (16 ounce) skinless salmon fillet (1 inch thick)",
#     # "1-2oz of butter, 20-50 grams of peanuts",
#     # "1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces",
#     # "1 tablespoon all-purpose flour",
#     # "McDonald's Tartar Sauce",
#     # "4 tablespoons salted butter, divided",
#     # "2 large cloves garlic, minced",
#     # "1/4 teaspoon salt",
#     # "1/4 teaspoon crushed red pepper (optional)"
# ]

# ingredient_strings = [
#     "1 (8 ounce) container plain yogurt",
#     "1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)",
#     "4 (1/2-ounce each) processed American cheese slices (optional)",
#     "1 (16 ounce) skinless salmon fillet (1 inch thick)",
#     "1/4 teaspoon crushed red pepper (optional)",
#     "salmon fillets (2)",
#     "salmon fillets (2 8 ounces)",
#     "sugar (2 1/4 cups)",
#     "1 steak (8-ounces  )",
#     "1 steak (8-ounces  ) grassfed only please (optional)"
# ]

# regex = RecipeRegexPatterns()

# for ingredient in ingredient_strings:
#     print(f"Original: '{ingredient}'")
#     # ingredient = "1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)"
#     parser = RecipeParser(ingredient, regex=regex, debug=False)
#     parser.parse()

#     print(f"Standardized: '{parser.standard_ingredient}'")
#     print(f"""Reduced:\n > '{parser.reduced_ingredient}'
#         \n   Quant: > '{parser.best_quantity}'\n   Unit:  > '{parser.best_unit}'""")
#     # print(f"Quantity:\n > '{parser.best_quantity}'")
#     # print(f"Unit:\n > '{parser.best_unit}'")
#     # print(f"Units: {parser.found_units}")
#     print("\n")

# ingredient = "4 (1/2-ounce) processed American cheese slices (optional)"
# ingredient =     "sugar (2 1/4 cups)"
# ingredient = "1 (16 ounce) skinless salmon fillet (1-inch thick)"
# ingredient = "salmon fillets (2)"
# ingredient = "4 salmon fillets (2)"
# ingredient = "4 salmon kitties (2)"

# ingredient = "1 (16 ounce) skinless salmon fillet (1-inch thick)"

# regex = RecipeRegexPatterns()
# parser = RecipeParser(ingredient, regex=regex, debug=False)
# parser.parse()
# parser.standard_ingredient
# parser.standard_ingredient.replace("ounce", "")
# parser.reduced_ingredient
# extract_first_quantity_unit(parser.reduced_ingredient, regex)

# def extract_first_quantity_unit(ingredient: str, regex: RecipeRegexPatterns) -> dict:
#     """
#     Extract the first unit and quantity from an ingredient string.
#     Args:
#         ingredient (str): The ingredient string to parse.
#         regex (RecipeRegexPatterns): An instance of the RecipeRegexPatterns class.
#     Returns:
#         dict: A dictionary containing the first unit and quantity found in the ingredient string.
#     Examples:
#         >>> extract_first_unit_quantity('1 1/2 cups diced tomatoes, 2 tablespoons of sugar, 1 stick of butter', regex)
#         {'first_unit': 'cups', 'first_quantity': '1 1/2'}
#         >>> extract_first_unit_quantity('2 1/2 cups of sugar', regex)
#         {'first_unit': 'cups', 'first_quantity': '2 1/2'}
#     """

#     # ingredient = parser.reduced_ingredient
#     # # regex.print_matches(ingredient)

#     # set default values for the best quantity and unit
#     best_quantity = None
#     best_unit = None

#     # get the first number followed by a basic unit in the ingredient string
#     basic_unit_matches = regex.QUANTITY_BASIC_UNIT_GROUPS.findall(ingredient)
    
#     # remove any empty matches
#     valid_basic_units = [i for i in basic_unit_matches if len(i) > 0]

#     print(f"Valid basic units: {valid_basic_units}") if valid_basic_units else print(f"No valid basic units found...")

#     if basic_unit_matches and valid_basic_units:
#         best_quantity = valid_basic_units[0][0].strip()
#         best_unit = valid_basic_units[0][1].strip()

#         return {"first_unit": best_unit, "first_quantity": best_quantity}
#     # else:

#     # If no basic units are found, then check for anumber followed by a nonbasic units
#     nonbasic_unit_matches = regex.QUANTITY_NON_BASIC_UNIT_GROUPS.findall(ingredient)
    
#     # remove any empty matches
#     valid_nonbasic_units = [i for i in nonbasic_unit_matches if len(i) > 0]

#     print(f"Valid non basic units: {valid_nonbasic_units}") if valid_nonbasic_units else print(f"No valid non basic units found...")

#     if nonbasic_unit_matches and valid_nonbasic_units:
#         best_quantity = valid_nonbasic_units[0][0].strip()
#         best_unit = valid_nonbasic_units[0][1].strip()

#         return {"first_unit": best_unit, "first_quantity": best_quantity}


#     # if neither basic nor nonbasic units are found, then get the first number
#     quantity_matches = regex.ALL_NUMBERS.findall(ingredient)

#     # remove any empty matches
#     valid_quantities = [i for i in quantity_matches if len(i) > 0]

#     print(f"Valid quantities: {valid_quantities}") if valid_quantities else print(f"No valid quantities found...")

#     if quantity_matches and valid_quantities:
#         best_quantity = valid_quantities[0].strip()
#         return {"first_unit": best_unit, "first_quantity": best_quantity}
    
#     return {"first_unit": best_unit, "first_quantity": best_quantity}



#     # # get the first unit in the ingredient string
#     # first_unit = regex.UNITS_PATTERN.search(ingredient)

#     # # get the first quantity in the ingredient string
#     # first_quantity = regex.ALL_NUMBERS.search(ingredient)

#     # # return the first unit and quantity
#     # return {"first_unit": first_unit.group() if first_unit else "", "first_quantity": first_quantity.group() if first_quantity else ""}

# simple = parser.reduced_ingredient

# regex.print_matches(parser.standard_ingredient.replace("4", ""))
# regex.print_matches(parser.reduced_ingredient)


# parser.found_units
# parser._pull_first_unit()
# ingredient = parser.standard_ingredient

# para_obj = parser.parenthesis_obj

# for k, v in para_obj.items():
#     print(f"Key: {k} - {v}")




# # RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex, debug=False).parse2()
# # parsey = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex, debug=True)

# # parsey.parse2()
# # parsey.standard_ingredient
# # regex.list_attrs()

# output = []

# for ingredient in ingredient_strings:
#     # parsed_string = RecipeParser(ingredient, regex, debug=False)
#     parser = RecipeParser(ingredient, regex=regex, debug=False)
#     parser.parse2()
#     parsed_string = parser.standard_ingredient
#     output.append(parsed_string)
#     print(f"Original: {ingredient}")
#     print(f"Parsed: {parsed_string}")
#     print("\n")

# for out in output:
#     print(out)

# ingredient = output[-2]
# # ingredient = output[4]
# ingredient

# for k, v in regex.find_matches(ingredient).items():
#     print(f"Key: {k} - {v}")

# re.split(regex.SPLIT_BY_PARENTHESIS, ingredient)
# for k, v in regex.find_matches("1 for (8-ounce  ) cup of (juice) options").items():
#     print(f"Key: {k} - {v}")
#     # print(f"Value: {v}")

# # final_parser.__name__
    
# def _make_int_or_float_str(number_str: str) -> str:
#     """ Convert a string representation of a number to its integer or float equivalent.
#     If the number is a whole number, return the integer value as a string. If the number is a decimal, return the float value as a string.
#     Args:
#         number_str (str): The string representation of the number.
#     Returns:
#         str: The integer or float value of the number as a string.
#     """
#     number = float(number_str.strip())  # Convert string to float
#     if number == int(number):  # Check if float is equal to its integer value
#         return str(int(number))  # Return integer value if it's a whole number
#     else:
#         return str(number)  # Return float if it's a decimal
        
# def pull_quantities(ingredient, regex):

#     """Pull out all of the numbers in the string and return them as a list.
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         list: A list of all the numbers in the ingredient string. An empty list is returned if no numbers are found.
#     """
#     # ingredient = '0.25 teaspoon crushed red pepper (optional)'
#     # for k, v in regex.find_matches(ingredient).items():
#     #     print(f"Key: {k} - {v}")

#     # for k, v in regex.find_matches("123 i love cats42 cups and a cat, 5587 dogs, 35.5 nuts").items():
#     #     print(f"Key: {k} - {v}")
#     # number_then_unit = regex.ANY_NUMBER_THEN_UNIT.findall(ingredient)

#     quantities = regex.ALL_NUMBERS.findall(ingredient)

#     return quantities

# def pull_units(ingredient, regex):

#     """
#     Pull out all of the units in the string
#     Returns a dictionary containing all of the units found in the ingredient string (all units, basic units, nonbasic units, volumetric units, and a flag indicating if the ingredient has a unit).
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         dict: A dictionary containing all of the units found in the ingredient string (all units, basic units, nonbasic units, volumetric units, and a flag indicating if the ingredient has a unit).
#     Examples:
#         >>> pull_units('0.25 teaspoon crushed red pepper (optional)')
#         {'units': ['teaspoon'],
#             'basic_units': ['teaspoon'],
#             'nonbasic_units': [],
#             'volumetric_units': ['teaspoon'],
#             'has_unit': True}
#         >>> pull_units('1 1/2 cups diced tomatoes, 2 tablespoons of sugar, 1 stick of butter')
#         {'units': ['cups', 'tablespoons', 'stick'],
#             'basic_units': ['cups', 'tablespoons', 'stick'],
#             'nonbasic_units': ['stick'],
#             'volumetric_units': ['cups', 'tablespoons'],
#             'has_unit': True}
#     """

#     # # ingredient = '0.25 teaspoon crushed red pepper (optional)'
#     # for k, v in regex.find_matches(ingredient).items():
#     #     print(f"Key: {k} - {v}")

#     # initliaze the has_unit flag to True, if no units are found, then the flag will be set to False
#     has_unit = True

#     # get all of the units in the ingredient string
#     all_units = regex.UNITS_PATTERN.findall(ingredient)

#     # get the basic units in the ingredient string by checking if the units are in the basic units set
#     basic_units = [unit for unit in all_units if unit in regex.constants["BASIC_UNITS_SET"]]
#     # basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient) # Does the same thing but uses regex, probably better to NOT regex backtrack if we can avoid it..

#     # get the nonbasic units in the ingredient string by checking if the units are not in the basic units set
#     nonbasic_units = list(set(all_units) - set(basic_units))

#     # get the volumetric units in the ingredient string by checking if the units are in the volumetric units set
#     volumetric_units = [unit for unit in all_units if unit in regex.constants["VOLUME_UNITS_SET"]]
#     # volumetric_units = regex.VOLUME_UNITS_PATTERN.findall(ingredient) 

#     # if no units are found, then set the has_unit flag to False
#     if not all_units and not basic_units and not nonbasic_units and not volumetric_units:
#         has_unit = False

#     found_units = {"units" : all_units, 
#                   "basic_units" : basic_units, 
#                   "nonbasic_units" : nonbasic_units, 
#                   "volumetric_units" : volumetric_units,
#                   "has_unit" : has_unit}
    
#     return found_units

# def pull_number_units(ingredient, regex):
#     """
#     Pull out all of the number unit pairs in the string
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         list: A list of all the number unit pairs in the ingredient string. An empty list is returned if no number unit pairs are found.
#     Examples:
#         >>> pull_number_units('0.25 teaspoon crushed red pepper (optional)')
#         [('0.25', 'teaspoon')]

#         >>> pull_number_units('1 1/2 cups diced tomatoes, 2 tablespoons of sugar, 1 stick of butter')


#     """
    
#     # get all of the number unit pairs in the ingredient string
#     number_unit_pairs = regex.ANY_NUMBER_THEN_UNIT.findall(out)
#     number_anything_unit = regex.ANY_NUMBER_THEN_ANYTHING_THEN_UNIT.findall(out)

#     return number_unit_pairs

# def _separate_parenthesis(ingredient, regex):

#     # ingredient = '0.25 teaspoon crushed red pepper (optional)'
#     # ingredient = '0.25 teaspoon (6 ounces options) crushed (optional) red pepper'
#     # ingred = "1/2 (8 ounce) steaks with almonds"

#     # for k, v in regex.find_matches(ingredient).items():
#     #     print(f"Key: {k} - {v}")

#     # split the ingredient string by the open/close parenthesis sets
#     no_parenthesis = re.split(regex.SPLIT_BY_PARENTHESIS, ingredient)

#     # remove any leading or trailing whitespace from the split strings and join them back together
#     no_parenthesis = " ".join([i.strip() for i in no_parenthesis])

#     # get the set of paranthesis values
#     parentheses = re.findall(regex.SPLIT_BY_PARENTHESIS, ingredient)

#     # ingredient, no_parenthesis, parentheses
#     # [i for i in parentheses]

#     # check for an "option" or "optional" string from the parenthesis
#     optional_match = re.findall(regex.OPTIONAL_STRING, ingredient)

#     # if the optional string is found in the parenthesis, then the ingredient is not required
#     required = False if optional_match else True
#     # required = True if not optional_match else False

#     # create the paranthensis object with the parsed values
#     parsed_parenthesis = {"raw_ingredient" : ingredient, 
#                         "reduced_ingredient" : no_parenthesis, 
#                         "parenthesis_content" : parentheses,
#                         "required" : required,
#                         }
    
#     return parsed_parenthesis

# def get_quantities_and_units(ingredient, regex):

#     # ingredient = '4 (1/2-ounce each) processed American cheese slices'
    
#     ingredient_parts = _separate_parenthesis(ingredient, regex)
#     for k, v in ingredient_parts.items():
#         print(f"Key: {k} - {v}")

#     # ingredient with the parenthesis removed
#     reduced_ingredient = ingredient_parts["reduced_ingredient"]

#     # try and pull out the quantities and units from the ingredient string
#     units = pull_units(reduced_ingredient, regex)

#     quantities = pull_quantities(reduced_ingredient, regex)
#     # units["units"]
#     # []
#     # add the quantities and units to the ingredient parts dictionary
#     ingredient_parts["quantities"]  = quantities
#     ingredient_parts["units"]       = units
#     # ingredient_parts["units"]       = units["units"]
#     # ingredient_parts["basic_units"] = units["basic_units"]
#     # ingredient_parts["has_unit"]    = units["has_unit"]




#     # ingredient_parts = {"quantities": quantities, 
#     #                     "units": units["units"], 
#     #                     "notes" : [],
#     #                     "required": True,
#     #                     "has_unit": units["has_unit"],
#     #                     "raw_ingredient": ingredient
#     #                     }
#     # _separate_parenthesis(ingredient, regex)

# def parse_ingredient_parts(ingredient_parts, regex):

#     # ingredient_parts = {
#     #     'raw_ingredient': '4 (1/2-ounce each) processed American cheese slices', 
#     #     'reduced_ingredient': '4 processed American cheese slices', 
#     #     'parenthesis_content': ['(1/2-ounce each)'], 
#     #     'quantities': ['4'], 
#     #     'units': ['slices'], 
#     #     'has_unit': True}

#     # get the "type" of parenthesis content using regex 
#     regex.print_matches(ingredient_parts["parenthesis_content"][0])
#     regex.print_matches("( 1/2  l ounce  )")
#     regex.PARENTHESIS_WITH_NUMBER_ANYTHING_UNIT
#     ingredient_parts.keys()
#     ingredient_parts["quantities"]
#     ingredient_parts["units"]
    
#     reduced_ingredient = ingredient_parts["reduced_ingredient"]
    
#     units_map = ingredient_parts["units"]

#     # unit booleans 
#     has_any_unit           = units_map["has_unit"]
#     has_both_units         = True if units_map["basic_units"] and units_map["nonbasic_units"] else False
#     has_basic_unit_only    = True if units_map["basic_units"] and units_map["nonbasic_units"] else False
#     has_nonbasic_unit_only = True if units_map["nonbasic_units"] and not units_map["basic_units"] else False

#     # unit lists
#     all_units      = units_map["units"]
#     basic_units    = units_map["basic_units"]
#     nonbasic_units = units_map["nonbasic_units"]

#     # quantities booleans
#     has_quantities = True if ingredient_parts["quantities"] else False

#     # quantities lists
#     quantities = ingredient_parts["quantities"]

#     print(f"""Factoring in parenthesis content: {ingredient_parts['parenthesis_content']}
#     Pulled units: {all_units}
#     - Ingredient has a unit: {has_any_unit}
#     - Ingredient has basic units: {has_basic_unit_only}
#     - Ingredient has nonbasic units: {has_nonbasic_unit_only}
#     Pulled quantities: {quantities}
#     - Ingredient has quantities: {has_quantities}""")

#     # Extract ALL of the strings that are in parenthesis
#     parenthesis_values = [regex.PARENTHESIS_VALUES.findall(i) for i in ingredient_parts["parenthesis_content"]]

#     # extract parenthesis that have only a number in them (e.g. (2)) likely indicates the quantity of the ingredient
#     numbers_only = [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in ingredient_parts["parenthesis_content"]]
#     # numbers_only = [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in ingredient_parts["parenthesis_content"]]
#     numbers_only = [i for subitem in numbers_only for i in subitem]
#     # numbers_only = [i[0] for i in numbers_only if i]
#     # numbers_only = []
#     # for i in ingredient_parts["parenthesis_content"]:
#     #     matches = regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i)
#     #     numbers_only.append(matches[0] if matches else "")

#     # numbers_only = [regex.PARENTHESIS_WITH_NUMBERS_ONLY.findall(i) for i in ["(2)"]]

#     # extract parenthesis that have a number and a unit in them (e.g. (2 ounces), (1/2-ounce))
#     quantity_unit = [regex.PARENTHESIS_WITH_NUMBER_UNIT.findall(i) for i in ingredient_parts["parenthesis_content"]]
#     quantity_unit = [i for subitem in quantity_unit for i in subitem]
#     # quantity_unit = [q[0] for q in quantity_unit if q]

#     # quantity_anything_unit = [regex.PARENTHESIS_WITH_NUMBER_ANYTHING_UNIT.findall(i) for i in ingredient_parts["parenthesis_content"]]
#     quantity_anything_unit = [regex.ANY_NUMBER_THEN_ANYTHING_THEN_UNIT.findall(i) for i in ingredient_parts["parenthesis_content"]]
#     quantity_anything_unit = [i for subitem in quantity_anything_unit for i in subitem]

#     for k, v in ingredient_parts.items():
#         print(f"Key: {k} - '{v}'")

#     if numbers_only:
#         print(f"Processing numbers only parenthesis: {numbers_only}")
#         # if we don't already have a quantity, and we don't have a unit, then we can assume that the number in the parenthesis is the quantity
#         # and the unit is the food or None for now
#         if not has_quantities and not has_any_unit:
#         # if not ingredient_parts["quantities"] and not ingredient_parts["units"]:
#             # [i for i in numbers_only]
#             print(f"Found quantity: '{numbers_only}'")
#             print(f"Unit is likely food or None")

#             new_quantity = float(numbers_only[0])
#             updated_quantity = [_make_int_or_float_str(str(new_quantity))]
        
#         # we have a quantity, but no unit then we multiply/merge the quantity and the parenthesis quantity and then the unit is the food maybe
#         elif has_quantities and not has_any_unit:
#             merged_quantity = float(quantities[0]) * float(numbers_only[0])
#             updated_quantity = [_make_int_or_float_str(str(merged_quantity))]

#             # UNIT IS THE FOOD (probably)
#             # pass

#         # if we don't already have a quantity,but we do have a unit, then we can guess we found a quantity
#         elif not has_quantities and has_any_unit:
#             # no quantity but a unit
#             updated_quantity = [_make_int_or_float_str(str(float(numbers_only[0])))]
        
#         # we have a quanity and a unit, so we can try to merge the quantity and the parenthesis quantity numbers (multiply?)
#         #  and then keep the current unit (probably)
#         elif has_quantities and has_any_unit:
#             # multiply the quantity and the parenthesis quantity
#             merged_quantity = float(quantities[0]) * float(numbers_only[0])
#             updated_quantity = [_make_int_or_float_str(str(merged_quantity))]

#             # first_basic_unit = [i for i in all_units if i in basic_units]       # get the first BASIC units in all_units
#             # first_nonbasic_unit = [i for i in all_units if i in nonbasic_units] # get the first NON BASIC units in all_units

#             # # if we have a basic unit, then we can assume that the unit is the basic unit, otherwise we can assume that the unit is the nonbasic unit
#             # if has_basic_unit_only:
#             #     selected_unit = basic_units[0]
#             # elif has_nonbasic_unit_only:
#             #     selected_unit = nonbasic_units[0]
#             # else:
#             #     selected_unit = None
#     def check_quantity_anything_unit(parenthesis_str, ingredient_parts, regex):

        
#         # parenthesis_str = quantity_anything_unit[0]
#         print(f"Checking quantity anything unit: {parenthesis_str}")

#         reduced_ingredient = ingredient_parts["reduced_ingredient"]
    
#         units_map = ingredient_parts["units"]

#         # unit booleans 
#         has_any_unit           = units_map["has_unit"]
#         has_both_units         = True if units_map["basic_units"] and units_map["nonbasic_units"] else False
#         has_basic_unit_only    = True if units_map["basic_units"] and units_map["nonbasic_units"] else False
#         has_nonbasic_unit_only = True if units_map["nonbasic_units"] and not units_map["basic_units"] else False

#         # unit lists
#         all_units      = units_map["units"]
#         basic_units    = units_map["basic_units"]
#         nonbasic_units = units_map["nonbasic_units"]

#         # quantities booleans
#         has_quantities = True if ingredient_parts["quantities"] else False

#         # quantities lists
#         quantities = ingredient_parts["quantities"]

#         # parenthesis 
#         parenthesis_quantities = pull_quantities(parenthesis_str, regex)
#         parenthesis_units    = pull_units(parenthesis_str, regex)

#         found_unit     = parenthesis_units["units"][0]
#         found_quantity = parenthesis_quantities[0]

#         print(f"Main Unit: '{main_unit}'\nMain Quantity: '{main_quantity}'")

#         # if we don't already have a quantity, and we don't have a unit, then we can assume that the number in the parenthesis is the quantity
#         if not has_quantities and not has_any_unit:
#             print(f"Quantity unit: {quantity_unit}")
#             # [i for i in numbers_only]
#             print(f"Found quantity: '{found_quantity}'")
#             print(f"Found unit: '{found_unit}'")
#             # quantity_unit
#             # para_quantity = pull_quantities(quantity_unit[0], regex)
#             # para_units = pull_units(quantity_unit[0], regex)

#             return found_quantity, found_unit
        
#         # if we have a quantity but no unit, then we can merge (mulitply) our quantity with the quantity in the parenthesis and the unit is the unit in the match
#         if has_quantities and not has_any_unit:
#             print(f"Quantity unit: {quantity_unit}")
#             print(f"Quantity anything unit: {quantity_anything_unit}")
#             # [i for i in numbers_only]
#             print(f"Found quantity: '{quantity_unit}'")
#             # quantity_unit
#             # para_quantity = pull_quantities(quantity_unit[0], regex)
#             # para_units = pull_units(quantity_unit[0], regex)

#             updated_quantity = float(found_quantity) * float(quantities[0])

#             return main_quantity, main_unit


#         if units and quantities:
#             return True
#         else:
#             return False
#     if quantity_anything_unit:
#         print(f"quantity_anything_unit: {quantity_anything_unit}")

#         para_quantity = pull_quantities(quantity_anything_unit[0], regex)
#         para_units    = pull_units(quantity_anything_unit[0], regex)

#         main_unit     = para_units["units"][0]
#         main_quantity = para_quantity[0]

#         print(f"Main Unit: '{main_unit}'\nMain Quantity: '{main_quantity}'")

#         # if we don't already have a quantity, and we don't have a unit, then we can assume that the number in the parenthesis is the quantity
#         if not ingredient_parts["quantities"] and not ingredient_parts["units"]:
#             print(f"Quantity unit: {quantity_unit}")
#             print(f"Quantity anything unit: {quantity_anything_unit}")
#             # [i for i in numbers_only]
#             print(f"Found quantity: '{quantity_unit}'")
#             quantity_unit
#             para_quantity = pull_quantities(quantity_unit[0], regex)
#             para_units = pull_units(quantity_unit[0], regex)

#             regex.print_matches("1/2 ifggdssf ounce")
#             regex.ANY_NUMBER_THEN_UNIT.findall("1/2-ounce")
#             para_quantity, para_unit = [i.replace("(", "").replace(")", "").split() for i in quantity_unit][0]

#             new_quantity = float(quantity_unit[0][0])

#             pass
#         # if we don't already have a quantity,but we do have a unit, then we can guess we found 
#             # a description of the ingredient OR a better quanity / unit combo
#         if not ingredient_parts["quantities"] and ingredient_parts["units"]:
#             pass
#         # we have a quanity and a unit, so we can assume that the number in the parenthesis is a description of the ingredient
#         if ingredient_parts["quantities"] and ingredient_parts["units"]:
#             pass
#         # we have a quantity, but no unit 
#         if ingredient_parts["quantities"] and not ingredient_parts["units"]:
#             pass
# ###############################################################################################################
# ######################################## END OF CURRENT TESTS for the RecipeParser class ############
# ###############################################################################################################

# def separate_parenthesis(ingredient, regex):

#     # ingredient = '0.25 teaspoon crushed red pepper (optional)'
#     # ingredient = '0.25 teaspoon (6 ounces options) crushed (optional) red pepper'
#     # ingred = "1/2 (8 ounce) steaks with almonds"

#     # for k, v in regex.find_matches(ingredient).items():
#     #     print(f"Key: {k} - {v}")

#     # split the ingredient string by the open/close parenthesis sets
#     no_parenthesis = re.split(regex.SPLIT_BY_PARENTHESIS, ingredient)

#     # remove any leading or trailing whitespace from the split strings and join them back together
#     no_parenthesis = " ".join([i.strip() for i in no_parenthesis])

#     # get the set of paranthesis values
#     parentheses = re.findall(regex.SPLIT_BY_PARENTHESIS, ingredient)
#     # ingredient, no_parenthesis, parentheses

#     parsed_parenthesis = {"raw_string" : ingredient, 
#                         "parenthesis_removed" : no_parenthesis, 
#                         "parenthesis":parentheses}
    
#     return parsed_parenthesis

# for out in output:
#     print(f"Test string: '{out}'")
#     out = para_obj["reduced_ingredient"]
#     extracted_quantities = pull_quantities(out, regex)
#     extracted_units = pull_units(out, regex)
#     extracted_parenthesis = separate_parenthesis(out, regex)

#     print(f"Quantities: {extracted_quantities}")
#     print(f"""All Units: {extracted_units['units']}""")

#     print(f"Basic Units: {extracted_units['basic_units']}")
#     print(f"""Nonbasic Units: {extracted_units["nonbasic_units"]}""")

#     print(f"""Removed parenthesis: {extracted_parenthesis["parenthesis_removed"]}""")
#     print(f"""Parenthesis: {extracted_parenthesis["parenthesis"]}""")
#     print("\n")

# def final_parser(ingredient):
#     """
#     Parse the ingredient string into its component parts.
#     """
#     ingredient_parts = {
#         "unit": None,
#         "quantity": None,
#         "min_quantity": None,
#         "max_quantity": None,

#         "secondary_unit": None,
#         "secondary_quantity": None,
#         "secondary_min_quantity": None,
#         "secondary_max_quantity": None,
        
#         "extra_units": None,
#         "ingredient_name": None,
#         "preparation": None,
#         "notes": None,

#         "raw_ingredient": ingredient,
#         "quantity_unit_pairs": None
#         }
    
#     for k, v in regex.find_matches(ingredient).items():
#         print(f"Key: {k} - {v}")

#     # Set default values to populate
#     unit = None
#     quantity = None
#     min_quantity = None
#     max_quantity = None
#     secondary_unit = None
#     secondary_quantity = None
#     secondary_min_quantity = None
#     secondary_max_quantity = None
#     quantity_unit_pairs = None

#     # unit = None
#     # secondary_unit = None
        
#     # get all of the units in the ingredient string
#     every_unit = regex.UNITS_PATTERN.findall(ingredient)

#     # get the basic units in the ingredient string
#     basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient)

#     # get the nonbasic units in the ingredient string
#     nonbasic_units = set(every_unit) - set(basic_units)

#     # instances of a number followed by a unit
#     number_then_unit = regex.ANY_NUMBER_THEN_UNIT.findall(ingredient)

#     # look for quantity ranges (numbers separated by a hyphen, e.g. 1-2 cups of sugar)
#     quantity_ranges = regex.QUANTITY_DASH_QUANTITY.findall(ingredient)
#     quantity_unit_ranges = regex.QUANTITY_DASH_QUANTITY_UNIT.findall(ingredient)
    
#     # 1. Deal with any quantity ranges
#     # if a quantity unit range was found ("1 - 2 cups"), then lets try and get the range separated by the unit
#     # by using the QUANTITY_DASH_QUANTITY pattern and the UNIT_PATTERN pattern
#     if quantity_unit_ranges:
#         range_values = [regex.QUANTITY_DASH_QUANTITY.findall(match)[0] for match in quantity_unit_ranges]
#         range_units  = [regex.UNITS_PATTERN.findall(match)[0] for match in quantity_unit_ranges]

#         # split the range values into a list of lists
#         split_range_values = [i.split("-") for i in range_values]

#         # get the average of each of the range values
#         range_avgs = [sum([float(num_str) for num_str in i]) / 2 for i in split_range_values]
#         # range_avgs = [sum([float(num_str) for num_str in i.split("-")]) / 2 for i in range_values]

#         # Primary ingredient and quantities (i.e. use the first quantity and unit as the primary quantity and unit)
#         unit = range_units[0]

#         # get the quantity from the range avgs and the min and max values from the split range values
#         quantity = range_avgs[0]
        
#         min_quantity, max_quantity = float(split_range_values[0][0]), float(split_range_values[0][1])

#         # Secondary ingredient and quantities (i.e. use the second quantity and unit as the secondary quantity and unit)
#         secondary_unit = range_units[1:]

#         # get the quantity from the range avgs and the min and max values from the split range values
#         secondary_quantity = range_avgs[1:]


#         print(f"Range Values: {range_values}\nRange Units: {range_units}\nRange Avgs: {range_avgs}\nQuantity: {quantity} ({min_quantity} - {max_quantity})")


#     # if there are any quantity ranges, then we need to treat the 2 spaced numbers 2 seperate numbers, a min and max
    


#     if number_then_unit:
        
#         # get the quantities and units from the number then unit matches
#         quantities = [regex.ALL_NUMBERS.findall(num)[0] for num in number_then_unit]
#         units = [regex.UNITS_PATTERN.findall(num)[0] for num in number_then_unit]

#         print(f"Number then units: {number_then_unit}\nQuantities: {quantities}\nUnits: {units}")

#         primary_units = units[0] # the first unit is the primary unit
#         secondary_units = units[1:] # any units after the first unit are secondary units

#         # primary_units = [unit for unit in units if unit in regex.constants["BASIC_UNITS_SET"]]
#         # secondary_units = set(units) - set(primary_units)
#         primary_quantity = quantities[0]
#         secondary_quantity = quantities[1:]

#         print(f"Primary Unit: {primary_units}\nSecondary Units: {secondary_units}")

#     basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient)
#     all_units = regex.UNITS_PATTERN.findall(ingredient)

# def _a_or_an_units(ingredient: str) -> str:
#     """
#     Add "a" or "an" to the beginning of the ingredient string if it starts with a vowel.
#     """
#     ingredient = "a lemon"

#     # lowercase and split the ingredient string
#     ingredient = ingredient.lower()
#     split_ingredient = ingredient.split()

#     matched_nums = re.findall(regex.ALL_NUMBERS, ingredient)

#     if split_ingredient[0] in ["a", "an"] and not matched_nums:
#         split_ingredient[0] = "1"
#         ingredient = " ".join(split_ingredient)
#         return ingredient

#     # check what Units are in the string (if any)
#     matched_units = re.findall(regex.UNITS_PATTERN, ingredient)

#     split_ingredient = ingredient.split()


#     vowels = ["a", "e", "i", "o", "u"]
#     first_letter = ingredient.split()[0][0].lower()
#     return "an" if first_letter in vowels else "a"

# # regex.constants["UNICODE_FRACTIONS"]
# parsed_string = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex)
# parsed_string = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex)

# # parsed_string = RecipeParser(ingredient='1 tablespoon all-purpose flour', regex=regex)
# parsed_string = RecipeParser(ingredient="1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces", regex=regex)

# # parsed_string = RecipeParser(f""""1 - 1 1/2 cups of sugar""", regex)
# parsed = parsed_string.normalized_string
# parsed
# # ingredient = '2 0.5 cups of sugar'
# # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

# # check if there are any spaced numbers (e.g. 2 1/2 cups of sugar or 2 8 ounce salmons)
# spaced_nums = re.findall(regex.SPACE_SEP_NUMBERS, parsed)

# # check what Units are in the string (if any)
# matched_units = re.findall(regex.UNITS_PATTERN, parsed)
# matched_units

# matched_basic_units = re.findall(regex.BASIC_UNITS_PATTERN, parsed)
# matched_basic_units

# secondary_units = set(matched_units) - set(matched_basic_units)


# # only do below if there are any units avaliable: (IF NO UNITS, treat multi numbers are multiplicative and )
# # if this value is Truthy, then we need to treat the 2 spaced numbers as additive values,
# # all other units will be multiplied (i.e. 2 8-ounce salmon fillets = 16 ounces of salmon)
# volumetric_units = [i for i in matched_units if i in regex.constants["VOLUME_UNITS_SET"]]

# has_spaced_nums      = bool(spaced_nums)
# has_units            = bool(matched_units)
# has_basic_units      = bool(matched_basic_units)
# has_volumetric_units = bool(volumetric_units)
# # has_single_number    = not bool(spaced_nums)

# def pull_out_units(ingredient):
#     """
#     Pull out units from the ingredient string.
#     """
#     # Define the regular expression pattern to match units
#     pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)')
#     # Find all matches of units in the ingredient string
#     matches = pattern.findall(ingredient)
#     # Iterate over the matches and print them
#     for match in matches:
#         print(match)

# # check what Units are in the string (if any)
# matched_units = re.findall(regex.UNITS_PATTERN, parsed)

# # only do below if there are any units avaliable: (IF NO UNITS, treat multi numbers are multiplicative and )
# # if this value is Truthy, then we need to treat the 2 spaced numbers as additive values,
# # all other units will be multiplied (i.e. 2 8-ounce salmon fillets = 16 ounces of salmon)
# volumetric_units = [i for i in matched_units if i in regex.constants["VOLUME_UNITS_SET"]]

# VOLUME_UNITS_SET = set()

# for key, pattern in regex.constants["VOLUME_UNITS"].items():

#     print(f"key: {key}")
#     print(f"Pattern: {pattern}")
#     VOLUME_UNITS_SET.add(key)
#     for val in pattern:
#         VOLUME_UNITS_SET.add(val)

# re.findall(regex.ALL_NUMBERS, " 1 cats are grate 88 for i like 2 dogs")
# for match, pattern in regex.find_matches(parsed).items():
#     print(f"Match: {match}")
#     print(f"Pattern: {pattern}")
# RecipeRegexPatterns()

# RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
#              regex).parse()

# RecipeParser("2 1/2 cups diced tomatoes", 
#              regex).parse()
# RecipeParser("2oz-3oz diced tomatoes", 
#              regex).parse()
# RecipeParser('1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05 - 1/2', 
#              regex).parse()
# '1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'
# RecipeParser("1-2 cups diced tomatoes", 
#              regex).parse()
# RecipeParser("1 cups diced tomatoes", 
#              regex).parse()
# RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
#              regex)._fraction_str_to_decimal("2233")
# # Example string
# example_string = '1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'

# # # Regular expression pattern to match decimal values with trailing zeros
# # decimal_pattern = re.compile(r'\b(\d+(\.\d+)?\.0+)\b')

# # # Find all matches of decimal values with trailing zeros in the string
# # matches = decimal_pattern.findall(example_string)

# # Regular expression pattern to match decimal values with trailing zeros
# decimal_pattern = re.compile(r'\b(?<!\d)(\d+(\.\d+)?\.0+)\b')

# # Find all matches of decimal values with trailing zeros in the string
# matches = decimal_pattern.findall(example_string)


# # Replace each match with its corresponding whole number
# for match in matches:
#     print(f"Match: {match}")
#     whole_number = match[0].split('.')[0]  # Extract the whole number part
#     print(f"whole_number: {whole_number}")
#     example_string = example_string.replace(match[0], whole_number)
#     print(f"Updated string: {example_string}")
#     print(f"\n")

# # Example string
# example_string = '1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'

# # Regular expression pattern to match decimal values
# decimal_pattern = re.compile(r'\b(\d+(\.\d+)?)\b')

# # Function to check if a decimal value only has 0 values after the decimal point
# def has_only_zeros(decimal):
#     if '.' in decimal:
#         _, fractional_part = decimal.split('.')
#         return all(char == '0' for char in fractional_part)
#     return False

# # Find all matches of decimal values in the string
# matches = decimal_pattern.findall(example_string)

# # Replace invalid decimals with their whole number representation
# for match in matches:
#     decimal_value = match[0]
#     if has_only_zeros(decimal_value):
#         whole_number = str(int(float(decimal_value)))
#         example_string = example_string.replace(decimal_value, whole_number)
# print("Updated string:", example_string)

# RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
#              regex).parse()
# RecipeParser("1-2 cups diced tomatoes", 
#              regex).parse()
# RecipeParser("1 cups diced tomatoes", 
#              regex).parse()
# RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
#              regex)._fraction_str_to_decimal("2233")

# fraction_str = "1 2/3"
# fraction_str.split(" ")
# # /^([0-9\/]+)-([\da-z\.-]+)\.([a-z\.]{2,5})$/
# # /^([0-9\/]+)-([0-9\/]+)$/
# # Regex for splititng whole numbers and fractions e.g. 1 1/2 -> ["1", "1/2"]
# SPLIT_INTS_AND_FRACTIONS_PATTERN = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')

# SPLIT_INTS_AND_FRACTIONS_PATTERN = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')
# QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*(?:\s*-\s*)+\d+")

# # INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'^(\d+\s*(?:\s*-\s*)+\d+)\s+((?:\d+\s*/\s*\d+)?)$')
# INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'^(?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?)$')
# INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'\A[0-9]+\s*\-\s*[0-9]+\Z')
# # (?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?

# input_strings = ["2/3 - 4/5", "2/3 - 4/5", "2/ 3 - 4/ 5"]


# "2-3"
# for input_str in input_strings:
#     # match = re.match(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)\s*-\s*(\d+)\s+((?:\d+\s*/\s*\d+)?)$', input_str)
#     match =  re.match(INTS_AND_FRACTIONS_RANGE_PATTERN, input_str)
#     if match:
#         print(f"Match found - match: {match}")
#         # first_whole_number = match.group(1)
#         # first_fraction = match.group(2)
#         # second_whole_number = match.group(3)
#         # second_fraction = match.group(4)
#         # print([first_whole_number, first_fraction, second_whole_number, second_fraction])

# int_and_fraction = "1 22 / 33"

# match = re.match(SPLIT_INTS_AND_FRACTIONS_PATTERN, int_and_fraction)
# whole_number = match.group(1)
# fraction_str = match.group(2)



# split_fraction = [i.strip() for i in fraction_str.split("/")]
# Fraction(int(split_fraction[0]), int(split_fraction[1]))

# input_strings = ["1 2/3", "1 2 /3", "1 2/ 3", "1 22/  33"]

# for input_str in input_strings:
#     match = re.match(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$', input_str)
#     if match:
#         whole_number = match.group(1)
#         fraction = match.group(2)
#         print([whole_number, fraction])
# # Split the fraction string into its numerator and denominator
# split_fraction = fraction_str.replace(" ", "").split("/")
# numerator = int(split_fraction[0])
# denominator = int(split_fraction[1])

# # Convert the fraction to a decimal
# # return round(float(Fraction(numerator, denominator)), 3)
# tmp = "2/3"
# tmp.split("/")
# split_fraction = [i.strip() for i in tmp.split("/")]

# if len(split_fraction) == 1:
#     int(split_fraction[0])
# numerator = int(split_fraction[0])
# denominator = int(split_fraction[1])

# # Convert the fraction to a decimal
# round(float(Fraction(numerator, denominator)), 3)


# RecipeParser("2lb - 1lb cherry tomatoes", regex).parse()

# regex.patterns.keys()
# parser = RecipeParser(ingredient, regex)
# output = parser.parse()

# output
# RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1/4 cups of sugar", 
#              regex).parse()
# RecipeParser("2lb - 1lb cherry tomatoes", regex).parse()
# # Regex pattern for finding quantity and units without space between them.
# # Assumes the quantity is always a number and the units always a letter.
# Q_TO_U = re.compile(r"(\d)\-?([a-zA-Z])")
# U_TO_Q = re.compile(r"([a-zA-Z])(\d)")
# U_DASH_Q = re.compile(r"([a-zA-Z])\-(\d)")

# sentence = "2lb-1oz cherry tomatoes"
# sentence = Q_TO_U.sub(r"\1 \2", sentence)
# sentence = U_TO_Q.sub(r"\1 \2", sentence)
# U_DASH_Q.sub(r"\1 - \2", sentence)

# re.findall(regex.FRACTION_PATTERN, ingredient)
# re.findall(regex.RANGE_WITH_TO_OR_PATTERN, output)
# regex.QUANTITY_RANGE_PATTERN.sub(r"\1-\5", output)
# regex.RANGE_WITH_TO_OR_PATTERN.search(output)
# STRING_RANGE_PATTERN.sub(r"\1-\5", output)
# STRING_RANGE_PATTERN = re.compile(
#     r"([\d\.]+)\s*(\-)?\s*(to|or)\s*(\-)*\s*([\d\.]+(\-)?)"
# )

# iterfinder = re.finditer(regex.RANGE_WITH_TO_OR_PATTERN, output)

# for match in iterfinder:
#     print(match.group())
#     print(match.start())
#     print(match.end())
#     print(match.span())
#     print("\n")

# # QUANTITY_RANGE_PATTERN
# # # RANGE_WITH_TO_OR_PATTERN
# # BETWEEN_NUM_AND_NUM_PATTERN

# ############################



# F_PATTERN = r'([+-]?[^+-]+)'
# import re
# from fractions import Fraction

# def parse_mixed_fraction(fraction_str: str) -> list:
#     # Remove whitespace to the left and right of a slash
#     cleaned_fractions = re.sub(r'\s*/\s*', '/', fraction_str)

#     # print(f"Cleaned Fractions: {cleaned_fractions}")

#     # Define the regular expression pattern to match the mixed fraction
#     pattern = re.compile(r'\b(\d+)\s*(\d+/\d+)\b')
#     match = pattern.search(cleaned_fractions)
    
#     if match:
#         whole_number = match.group(1)
#         fraction = match.group(2)
#         return [whole_number, fraction]
#     else:
#         # If no match found, split the string based on space and return
#         return cleaned_fractions.split()

# def sum_parsed_fractions(fraction_list: list, truncate: int = 3 ) -> float:
    
#     total = 0
#     for i in fraction_list:
#         total += Fraction(i)
    
#     return round(float(total), truncate)

# # Test the function
# input_string1 = '1 2/3'
# input_string2 = '1 2 /  3'

# # input_string2 = '1 2 / 3'
# print(parse_mixed_fraction(input_string1))  # Output: ['1', '2/3']
# print(parse_mixed_fraction(input_string2))  # Output: ['1', '2/3']

# ingredient_strings = [
#     "2 tbsp sugar",
#     "two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water",
#     "3/4 tsp salt",
#     "1 1/2 cups diced tomatoes",
#     "2 cloves garlic, minced",
#     "1/4 lb bacon, diced",
#     "1/2 cup breadcrumbs",
#     "1/4 cup grated Parmesan cheese",
#     "warmed butter (1 - 2 sticks)",
#     "honey, 1/2 tbsp of sugar",
#     "- butter (1 - 2 sticks)",
#     "peanut butter, 1-3 tbsp",
#     "between 1/2 and 3/4 cups of sugar",
#     "1/3 pound of raw shrimp, peeled and deveined",
#     "1/4 cup of grated Parmesan cheese",
#     ]

# ingredient = ingredient_strings[1]

# regex.patterns.keys()

# def parse_mixed_fraction(fraction_str: str) -> list:
#     # Remove whitespace to the left and right of a slash
#     cleaned_fractions = re.sub(r'\s*/\s*', '/', fraction_str)

#     # print(f"Cleaned Fractions: {cleaned_fractions}")

#     # Define the regular expression pattern to match the mixed fraction
#     pattern = re.compile(r'\b(\d+)\s*(\d+/\d+)\b')
#     match = pattern.search(cleaned_fractions)
    
#     if match:
#         whole_number = match.group(1)
#         fraction = match.group(2)
#         return [whole_number, fraction]
#     else:
#         # If no match found, split the string based on space and return
#         return cleaned_fractions.split()

# def sum_parsed_fractions(fraction_list: list, truncate: int = 3 ) -> float:
    
#     total = 0
#     for i in fraction_list:
#         total += Fraction(i)
    
#     return round(float(total), truncate)

# ingredient = 'two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water'
# # multifrac_pattern = re.compile('(\\d*\\s*\\d/\\d+)')
# multifrac_pattern = regex.MULTI_PART_FRACTIONS_PATTERN

# #### 2 methods to replace fractions in the original string with their sum 
# # - Using findall() and then replacing the summed values with the original fractions string
# # - Using finditer() and then replacing the original fractions with the summed values based on match indices
# # findall() method 
# fractions = re.findall(multifrac_pattern, ingredient)
# # Replace fractions in the original string with their sum
# updated_ingredient = ingredient
# for f in fractions:
#     parsed_fraction = parse_mixed_fraction(f)
#     sum_fraction = sum_parsed_fractions(parsed_fraction)
#     updated_ingredient = updated_ingredient.replace(f, str(sum_fraction))

# # print(updated_ingredient)

# # finditer() method
# fractions = re.finditer(multifrac_pattern, ingredient)

# # Replace fractions in the original string with their sum based on match indices
# updated_ingredient = ingredient
# offset = 0

# for match in fractions:

#     # keep track of the offset to adjust the index of the match
#     start_index = match.start() + offset
#     end_index = match.end() + offset
#     matched_fraction = match.group()

#     # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
#     parsed_fraction = parse_mixed_fraction(matched_fraction)

#     # Replace the matched fraction with the sum of the parsed fraction
#     sum_fraction = sum_parsed_fractions(parsed_fraction)

#     # Insert the sum of the fraction into the updated ingredient string
#     updated_ingredient = updated_ingredient[:start_index] + str(sum_fraction) + updated_ingredient[end_index:]

#     # Update the offset to account for the difference in length between the matched fraction and the sum of the fraction
#     offset += len(str(sum_fraction)) - len(matched_fraction)
# updated_ingredient

# update_values = [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

# parse_mixed_fraction(fractions[0])

# matches = multifrac_pattern.search(ingredient)

# for i in ingredient_strings:
#     print(f"Ingredient: {i}")
#     fracs = re.findall(multifrac_pattern, i)
#     print(f"- Fractions: {fracs}")
#     #clean the fractions
#     for frac in fracs:
#         print(f"---> Cleaned Fractions: {parse_mixed_fraction(frac)}")


#     print("\n")
# re.findall(multifrac_pattern, ingredient)
# sfrac = ['1', '2/3']

# float(Fraction(sfrac[0]) + Fraction(sfrac[1]))
# matches.group(0)


# regex = RecipeRegexPatterns(pattern_list)

# ingredient_strings = [
#     "2 tbsp sugar",
#     "two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water",
#     "3/4 tsp salt",
#     "1 1/2 cups diced tomatoes",
#     "2 cloves garlic, minced",
#     "1/4 lb bacon, diced",
#     "1/2 cup breadcrumbs",
#     "1/4 cup grated Parmesan cheese",
#     "warmed butter (1 - 2 sticks)",
#     "honey, 1/2 tbsp of sugar",
#     "- butter (1 - 2 sticks)",
#     "peanut butter, 1-3 tbsp",
#     "between 1/2 and 3/4 cups of sugar",
#     "1/3 pound of raw shrimp, or 1/4 peeled and deveined",
#     "1/4 cup of grated Parmesan cheese",
#     ]

# parsed_output = []
# for i in ingredient_strings:
#     parser = RecipeParser(i, regex)
#     standard_ingredient = parser.parse()
#     parsed_output.append(standard_ingredient)

# for i in parsed_output:
#     print(i)
#     print(f"\n")

# parser = RecipeParser(ingredient, regex)
# ingredient = ingredient_strings[1]
# parser = RecipeParser(ingredient, regex)

# parser.ingredient
# parser.standard_ingredient

# standard_ingredient = parser.parse()
# # Convert word numbers to numerical numbers
# # regex.patterns.keys()
# # ingredient = regex.NUMBER_WORDS_REGEX_MAP["two"][1].sub(regex.NUMBER_WORDS_REGEX_MAP["two"][0], ingredient)
# # regex.NUMBER_WORDS_REGEX_MAP["two"][0]

# for word, regex_data in regex.NUMBER_WORDS_REGEX_MAP.items():
#     number_value = regex_data[0]
#     pattern = regex_data[1]
#     if pattern.search(ingredient):
#         print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}")
#     # print(f"Word: {word} \n Regex Data: {regex_data}")
#     # regex_data[0]
#     ingredient = pattern.sub(regex_data[0], ingredient)
#     # ingredient
#     # self.standard_ingredient = pattern.sub(regex_data[0], self.standard_ingredient)

# regex = RecipeRegexPatterns(pattern_list)

# parser = RecipeParser(ingredient, regex)

# parser.ingredient
# parser.standard_ingredient

# standard_ingredient = parser.parse()
# parser.standard_ingredient
# parser.ingredient
# print(standard_ingredient)

# def _parse_fractions(self):
#     """
#     Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
#     """
#     # print("Parsing fractions")
#     # regex.MULTI_PART_FRACTIONS_PATTERN
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.standard_ingredient)
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.standard_ingredient)
#     # [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

#     # ---- 2 methods to replace fractions in the original string with their sum  ----
#     # - Using findall() and then replacing the summed values with the original fractions string
#     # - Using finditer() and then replacing the original fractions with the summed values based on match indices
#     # findall() method 
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.standard_ingredient)
#     # Replace fractions in the original string with their sum
#     # updated_ingredient = ingredient
#     # for f in fractions:
#     #     print(f"Fraction: {f}")
#     #     # remove "and" and "&" from the matched fraction
#     #     matched_fraction = f.replace("and", " ").replace("&", " ")

#     #     # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
#     #     parsed_fraction = self._parse_mixed_fraction(matched_fraction)

#     #     # Replace the matched fraction with the sum of the parsed fraction
#     #     sum_fraction = self._sum_parsed_fractions(parsed_fraction)
#     #     # updated_ingredient = self.standard_ingredient.replace(f, str(sum_fraction))
#     #     self.standard_ingredient = self.standard_ingredient.replace(f, str(sum_fraction))
#     # print(updated_ingredient)

#     # finditer() method
#     fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN, self.standard_ingredient)
#     # fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.standard_ingredient)

#     # Replace fractions in the original string with their sum based on match indices
#     # updated_ingredient = self.standard_ingredient
#     offset = 0

#     for match in fractions:

#         # keep track of the offset to adjust the index of the match
#         start_index = match.start() + offset
#         end_index = match.end() + offset
#         matched_fraction = match.group()

#         print(f"Matched Fraction: {matched_fraction}")
#         # remove "and" and "&" from the matched fraction
#         matched_fraction = matched_fraction.replace("and", " ").replace("&", " ")

#         print(f"Matched Fraction after removing AND: {matched_fraction}")

#         # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
#         parsed_fraction = self._parse_mixed_fraction(matched_fraction)

#         print(f"Parsed Fraction: {parsed_fraction}")

#         # Replace the matched fraction with the sum of the parse    d fraction
#         sum_fraction = self._sum_parsed_fractions(parsed_fraction)

#         print(f"Sum Fraction: {sum_fraction}")
#         # Insert the sum of the fraction into the updated ingredient string
#         # updated_ingredient = updated_ingredient[:start_index] + str(sum_fraction) + updated_ingredient[end_index:]
#         self.standard_ingredient = self.standard_ingredient[:start_index] + " " + str(sum_fraction) + self.standard_ingredient[end_index:]

#         # Update the offset to account for the difference in length between the matched fraction and the sum of the fraction
#         offset += len(str(sum_fraction)) - len(matched_fraction)

# def _parse_mixed_fraction(self, fraction_str: str) -> list:
#     # Remove whitespace to the left and right of a slash
#     cleaned_fractions = re.sub(r'\s*/\s*', '/', fraction_str)

#     # print(f"Cleaned Fractions: {cleaned_fractions}")

#     # Define the regular expression pattern to match the mixed fraction
#     pattern = re.compile(r'\b(\d+)\s*(\d+/\d+)\b')
#     match = pattern.search(cleaned_fractions)
    
#     if match:
#         whole_number = match.group(1)
#         fraction = match.group(2)
#         return [whole_number, fraction]
#     else:
#         # If no match found, split the string based on space and return
#         return cleaned_fractions.split()

# def _sum_parsed_fractions(self, fraction_list: list, truncate = 3) -> float:
    
#     total = 0
#     for i in fraction_list:
#         total += Fraction(i)
    
#     return round(float(total), truncate)


# # # Test the function
# # units = ["oz", "grams", "kg", "lbs"]
# # input_string = "1oz-2oz"
# # output_string = remove_first_unit(input_string, units)
# # print("Original string:", input_string)
# # print("String with first unit removed:", output_string)

# # Define the regular expression pattern to match numbers with a hyphen in between them
# def update_ranges(input_string, pattern, replacement_function=None):
#     # input_string = tmp
#     # pattern = regex_patterns.BETWEEN_NUM_AND_NUM_PATTERN
#     # replacement_function = replace_and_with_hyphen

#     matches = pattern.findall(input_string)
#     # matched_ranges = [match.split("-") for match in matches]
#     if replacement_function:
#         print(f"Replacement Function given")
#         matched_ranges = [replacement_function(match).split("-") for match in matches]
#     else:
#         print(f"No Replacement Function given")
#         matched_ranges = [match.split("-") for match in matches]
#     print(f"Matched Ranges: \n > {matched_ranges}")
#     updated_ranges = [" - ".join([str(int(i)) for i in match if i]) for match in matched_ranges]
#     # Create a dictionary to map the matched ranges to the updated ranges
#     ranges_map = dict(zip(matches, updated_ranges))
#     # Replace the ranges in the original string with the updated ranges
#     for original_range, updated_range in ranges_map.items():
#         print(f"Original Range: {original_range}")
#         print(f"Updated Range: {updated_range}")
#         # if replacement_function:
#         #     print(f"Replacement Function given")
#         #     updated_range = replacement_function(updated_range)
#         input_string = input_string.replace(original_range, updated_range)
#         print("\n")
#     return input_string
# def replace_and_with_hyphen(match):
#     # Replace "and" and "&" with hyphens
#     return match.replace("and", "-").replace("&", "-")
# def replace_to_or_with_hyphen(match):
#     # Replace "and" and "&" with hyphens
#     return match.replace("to", "-").replace("or", "-")
# # Test string
# tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 to 4 peanuts, cats do between 1  and 5 digs, i like between 1 and 2 mm'
# # Update ranges matched by QUANTITY_RANGE_PATTERN
# tmp = update_ranges(tmp, regex_patterns.QUANTITY_RANGE_PATTERN)

# # Update ranges matched by BETWEEN_NUM_AND_NUM_PATTERN, with replacement function to replace "and" and "&"
# tmp = update_ranges(tmp, regex_patterns.BETWEEN_NUM_AND_NUM_PATTERN, replace_and_with_hyphen)

# regex_patterns.RANGE_WITH_TO_OR_PATTERN.findall(tmp)
# self.regex_patterns.CONSECUTIVE_LETTERS_DIGITS
# CONSECUTIVE_LETTERS_DIGITS = re.compile(r'([a-zA-Z]+)(\d+)|(\d+)([a-zA-Z]+)')

# # Test strings
# test_strings = [
#     "apple123",
#     "banana456",
#     "123orange",
#     "789grape",
#     "apple123banana456",
#     "123orange789grape",
#     "apple123orange789",
#     "123456apple"
# ]

# # Iterate over test strings and apply the regex pattern
# for test_str in test_strings:
#     print(f"The test string is: > '{test_str}'")
#     print(f"found strs: \n > '{re.findall(pattern, test_str)}'")
#     new_str = re.sub(pattern, r'\1 \2\3 \4', test_str)
#     print(f"new str: \n > '{new_str}'")
#     print("\n")