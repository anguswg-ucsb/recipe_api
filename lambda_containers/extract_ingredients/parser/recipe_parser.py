import re
from typing import List, Dict, Any, Union, Tuple
from fractions import Fraction
from html import unescape
import warnings

# from regex_patterns import regex_patterns
# from regex_patterns import pattern_list, RegexPatterns
from lambda_containers.extract_ingredients.parser.regex_patterns import RecipeRegexPatterns

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

####################################################################################################
######################################## RecipeParser class ########################################
####################################################################################################

# # Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# # Step 2: Replace numbers with words with their numerical equivalents
# # Step 3: Replace all unicode fractions with their decimal equivalents
# # Step 4: Replace all fractions with their decimal equivalents
# # Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# # Step 6: Add or Multiply the numbers in a string separated by a space
# # Step 7: Seperate any part of the string that is wrapped in paranthesis and treat this as its own string

class RecipeParser:
    """
    A class to parse recipe ingredients into a standard format.

    Args:
        ingredient (str): The ingredient to parse.
    """

    def __init__(self, ingredient: str,  regex: RecipeRegexPatterns, debug = False):
        self.ingredient = ingredient
        self.parsed_ingredient = ingredient
        self.regex = regex
        self.debug = debug
        # self.normalized_string = self.parse()
        # self.normalized_string2 = self.parse2()

    def parsed_ingredient(self):
        
        return self.parsed_ingredient
    
    
    def _drop_special_dashes(self) -> None:
        # print("Dropping special dashes")
        self.parsed_ingredient = self.parsed_ingredient.replace("—", "-").replace("–", "-").replace("~", "-")
        return
    
    def _parse_number_words(self):
        """
        Replace number words with their corresponding numerical values in the parsed ingredient.
        """

        # print("Parsing number words")
        for word, regex_data in self.regex.NUMBER_WORDS_REGEX_MAP.items():
            pattern = regex_data[1]
            # print statement if word is found in ingredient and replaced
            if pattern.search(self.parsed_ingredient):
                print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}") if self.debug else None
            self.parsed_ingredient = pattern.sub(regex_data[0], self.parsed_ingredient)

    def _clean_html_and_unicode(self) -> None:
        """Unescape fractions from HTML code coded fractions to unicode fractions."""

        # Unescape HTML
        self.parsed_ingredient = unescape(self.parsed_ingredient)
        # regex.UNICODE_FRACTIONS
        # Replace unicode fractions with their decimal equivalents
        for unicode_fraction, decimal_fraction in self.regex.constants["UNICODE_FRACTIONS"].items():
            self.parsed_ingredient = self.parsed_ingredient.replace(unicode_fraction, decimal_fraction)

    def _add_whitespace(self):
        # regex pattern to match consecutive sequences of letters or digits
        pattern = self.regex.CONSECUTIVE_LETTERS_DIGITS        
        # pattern = re.compile(r'([a-zA-Z]+)(\d+)|(\d+)([a-zA-Z]+)')

        # replace consecutive sequences of letters or digits with whitespace-separated sequences
        self.parsed_ingredient = re.sub(pattern, r'\1 \2\3 \4', self.parsed_ingredient)

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
        fractions = re.findall(regex.FRACTION_PATTERN, self.parsed_ingredient)

        split_frac = [i.replace(" ", "").split("/") for i in frac]
        split_frac = [(int(f[0]), int(f[1])) for f in split_frac]
        fraction_decimal = [round(float(Fraction(f[0], f[1])), 3) for f in split_frac]

        # replace fractions in original string with decimal equivalents
        for i, f in enumerate(fractions):
            self.parsed_ingredient = self.parsed_ingredient.replace(f, str(fraction_decimal[i]))
    
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

        # fraction_str = "1 to 1/2 cups, 2 and 5 animals, 2 2 / 4 cats, 1 and 1/22 cups water melon"
        matches = regex.FRACTION_PATTERN.findall(self.parsed_ingredient)
        # matches = regex.FRACTION_PATTERN.findall(fraction_str)

        # Replace fractions with their decimal equivalents
        for match in matches:
            # print(f"Match: {match}")

            fraction_decimal = self._fraction_str_to_decimal(match)

            print(f"Fraction Decimal: {fraction_decimal}") if self.debug else None

            self.parsed_ingredient = self.parsed_ingredient.replace(match, str(fraction_decimal))


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

        self.parsed_ingredient = Q_TO_U.sub(r"\1 \2", self.parsed_ingredient)
        self.parsed_ingredient = U_TO_Q.sub(r"\1 \2", self.parsed_ingredient)
        self.parsed_ingredient = U_DASH_Q.sub(r"\1 - \2", self.parsed_ingredient)

    # Define the regular expression pattern to match numbers with a hyphen in between them
    def _update_ranges(self, ingredient, pattern, replacement_function=None):
        # self.parsed_ingredient
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
        
        all_ranges = re.finditer(regex.QUANTITY_DASH_QUANTITY, self.parsed_ingredient)
        # all_ranges = re.finditer(regex.QUANTITY_DASH_QUANTITY, ingredient)

        # initialize offset and replacement index values for updating the ingredient string, 
        # these will be used to keep track of the position of the match in the string
        offset = 0
        replacement_index = 0

        # Update the ingredient string with the merged values
        for match in all_ranges:
            # print(f"Ingredient string: {self.parsed_ingredient}")

            # Get the start and end positions of the match
            start, end = match.start(), match.end()

            print(f"Match: {match.group()} at positions {start}-{end}") if self.debug else None

            # Get the range values from the match
            range_values = re.findall(regex.QUANTITY_DASH_QUANTITY, match.group())

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
            self.parsed_ingredient = self.parsed_ingredient[:modified_start] + str(range_average) + self.parsed_ingredient[modified_end:]
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

        print(f"Before initial range update:\n {self.parsed_ingredient}") if self.debug else None
        # tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 -- 45 inches, cats do between 1  and 5 digs, i like between 1 and 2 mm'
        # Update ranges of numbers that are separated by one or more hyphens
        self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, self.regex.QUANTITY_DASH_QUANTITY)
        # self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, regex.QUANTITY_RANGE)
        # self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, regex.QUANTITY_RANGE_PATTERN)
        print(f"After initial range update:\n {self.parsed_ingredient}") if self.debug else None

        # Update ranges of numbers that are preceded by "between" and followed by "and" or "&"
        self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, self.regex.BETWEEN_QUANTITY_AND_QUANTITY, self._replace_and_with_hyphen)
        # self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, regex.BETWEEN_NUM_AND_NUM_PATTERN, self._replace_and_with_hyphen)
        print(f"After between and update:\n {self.parsed_ingredient}") if self.debug else None

        # Update ranges that are separated by "to" or "or"
        self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, self.regex.QUANTITY_TO_OR_QUANTITY, self._replace_to_or_with_hyphen)
        # self.parsed_ingredient = self._update_ranges(self.parsed_ingredient, regex.RANGE_WITH_TO_OR_PATTERN, self._replace_to_or_with_hyphen)
        print(f"After to or update:\n {self.parsed_ingredient}") if self.debug else None

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
        matches = self.regex.REPEAT_UNIT_RANGES.finditer(self.parsed_ingredient)
        # matches = pattern.finditer(self.parsed_ingredient)

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
                self.parsed_ingredient = self.parsed_ingredient.replace(original_string, f"{quantity1} - {quantity2} {unit1}")
                # print(f"Repeat units found: {unit1}")
                # print(f"Original string: {original_string}")
                # print(f"Quantity1: {quantity1}, Unit1: {unit1}, Quantity2: {quantity2}, Unit2: {unit2}")
                # print(f"----> REPEAT UNITS: {unit1}")
                # print("\n")
    
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

        # get the units from the ingredient string
        units = re.findall(self.regex.UNITS_PATTERN, self.parsed_ingredient)

        # spaced_nums = re.findall(regex.SPACE_SEP_NUMBERS, '2 0.5 cups of sugar 3 0.5 lbs of carrots')
        spaced_nums = re.findall(self.regex.SPACE_SEP_NUMBERS, self.parsed_ingredient)

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
        spaced_matches = re.finditer(self.regex.SPACE_SEP_NUMBERS, self.parsed_ingredient)

        # initialize offset and replacement index values for updating the ingredient string, 
        # these will be used to keep track of the position of the match in the string
        offset = 0
        replacement_index = 0

        # Update the ingredient string with the merged values
        for match in spaced_matches:
            # print(f"Ingredient string: {self.parsed_ingredient}")

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
            self.parsed_ingredient = self.parsed_ingredient[:modified_start] + str(merged_quantity) + self.parsed_ingredient[modified_end:]
            # ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]

            # Update the offset for subsequent replacements
            offset += len(merged_quantity) - (end - start)
            replacement_index += 1
            # print(f" --> Output ingredient: \n > '{self.parsed_ingredient}'")

    def _replace_a_or_an_units(self) -> None:
        """
        Replace "a" or "an" with "1" in the parsed ingredient if no number is present in the ingredient string.
        """
        # ingredient = "a lemon"

        # lowercase and split the ingredient string
        self.parsed_ingredient = self.parsed_ingredient.lower()
        split_ingredient = self.parsed_ingredient.split()

        matched_nums = re.findall(regex.ALL_NUMBERS, self.parsed_ingredient)

        if split_ingredient[0] in ["a", "an"] and not matched_nums:
            split_ingredient[0] = "1"
            # ingredient = " ".join(split_ingredient)
            self.parsed_ingredient = " ".join(split_ingredient)
            # return ingredient
        
    def _drop_special_characters(self):

        # Drop unwanted periods and replace them with whitespace
        self.parsed_ingredient = self.parsed_ingredient.replace(".", " ")

    ####### Deprecated ####### 
    def _parse_fractions(self):
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        # regex.MULTI_PART_FRACTIONS_PATTERN
        # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)

        # finditer() method
        fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)

        # Replace fractions in the original string with their sum based on match indices
        # updated_ingredient = self.parsed_ingredient
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
            self.parsed_ingredient = self.parsed_ingredient[:start_index] + " " + str(sum_fraction) + self.parsed_ingredient[end_index:]

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
    
    def parse2(self):
        
        # define a list containing the class methods that should be called in order on the input ingredient string
        methods = [
            self._drop_special_dashes,
            self._parse_number_words,
            self._clean_html_and_unicode,
            self._convert_fractions_to_decimals,
            self._fix_ranges,
            self._force_ws,
            self._remove_repeat_units,
            self._merge_multi_nums,
            self._replace_a_or_an_units,
            self._avg_ranges
        ]

        # call each method in the list on the input ingredient string
        for method in methods:
            print(f"Calling method: {method.__name__}") if self.debug else None
            print(f"> Starting ingredient: '{self.parsed_ingredient}'") if self.debug else None

            method()

            print(f"> Ending ingredient: '{self.parsed_ingredient}'") if self.debug else None
            
        print(f"Done, returning parsed ingredient: \n > '{self.parsed_ingredient}'") if self.debug else None

        # return the parsed ingredient string
        return self.parsed_ingredient

    def parse(self):

        print("BEFORE: \n > Ingredient: {self.ingredient} \n > Parsed Ingredient: {self.parsed_ingredient} \n") if self.debug else None
        print("Dropping special dashes...") if self.debug else None
        
        # Drop special cases of dashes with standard hyphens
        self._drop_special_dashes()

        # Convert all number words to numerical numbers
        print("Parsing number words...") if self.debug else None
        self._parse_number_words()

        print(f"Parsing HTML and unicode...") if self.debug else None
        # Clean HTML and unicode fractions
        self._clean_html_and_unicode()
        
        print(f"Converting fractions to decimals...") if self.debug else None
        self._convert_fractions_to_decimals()

        print(f"Fixing ranges...") if self.debug else None
        self._fix_ranges()

        # print(f"Converting fractions to decimals...")
        # # self._fractions_to_decimals()
        # print(f"Parsing fractions...")
        # self._parse_fractions()

        print(f"Forcing/Adding whitespace...") if self.debug else None
        self._force_ws()
        # self._add_whitespace()

        print(f"Removing repeat units...") if self.debug else None
        self._remove_repeat_units()

        print(f"Merging multi numbers...") if self.debug else None
        self._merge_multi_nums()

        print(f"AFTER: \n > Ingredient: {self.ingredient} \n > Parsed Ingredient: {self.parsed_ingredient} \n") if self.debug else None
        print(f'**********\n ---> Returning parsed ingredient: {self.parsed_ingredient} \n **********') if self.debug else None
        return self.parsed_ingredient
    
def _make_int_or_float_str(number_str: str) -> str:
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
    
# def _avg_ranges() -> None:
#         """
#         Replace ranges of numbers with their average in the parsed ingredient.
#         Examples:
#         "1-2 oz" -> "1.5 oz"
#         "1 - 2 ft" -> "1.5 ft"
#         """
#         # ingredient = '2 0.5 cups of sugar'
#         # ingredient = 'a lemon'
#         # ingredient = output[4]
#         # # ingredient = '1 - 2 oz of butter, 20 - 50 grams of peanuts'
#         # ingredient = '1 - 2 oz of butter, 20 - 50 of peanuts'
#         # for k, v in regex.find_matches(ingredient).items():
#         #     print(f"{k}: {v}")

#         all_ranges = re.finditer(regex.QUANTITY_DASH_QUANTITY, ingredient)
#         range_values = [re.findall(regex.QUANTITY_DASH_QUANTITY, i)[0] for i in all_ranges]
    
#         # split the range values into a list of lists
#         split_range_values = [i.split("-") for i in range_values]

#         # get the average of each of the range values
#         range_avgs = [sum([float(num_str) for num_str in i]) / 2 for i in split_range_values]
#         avg_values = [str((float(i) + float(j)) / 2) for i, j in range_values]

###############################################################################################################
######################################## Test the RecipeParser class ##########################################
###############################################################################################################
    
# ingredient_strings = [
#     "\u215b tbsp sugar",
#     "two to three tablespoons ~ of sugar, 1 2/3 tablespoons of water",
#     "1 1/2 cups diced tomatoes",
#     "1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1/4 cups of sugar",
#     "1 2/3 tablespoons of lettuce",
#     "1 and 3/3 tablespoons of lettuce",
#     "1/2 cup breadcrumbs",
#     "1/4 cup grated Parmesan cheese",
#     "warmed butter (1 - 2 sticks)"
#     ]
# ingredient = ingredient_strings[4]
# ingredient_strings = [
#     "1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces",
#     "4 (1/2-ounce each) processed American cheese slices",
#     "1 tablespoon all-purpose flour",
#     "McDonald's Tartar Sauce"
#     ]

ingredient_strings = [
    "a lemon",
    "a 1/2 lemon",
    "an orange",
    "1/2 an orange",
    "a 1-5lb lemon",
    "1-2oz of butter, 20-50 grams of peanuts",
    "1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces",
    "4 (1/2-ounce each) processed American cheese slices",
    "1 tablespoon all-purpose flour",
    "McDonald's Tartar Sauce",
    "12 ounces dry shell or orecchiette pasta",
    "4 tablespoons salted butter, divided",
    "2 large cloves garlic, minced",
    "1/4 teaspoon salt",
    "1/4 teaspoon freshly ground black pepper",
    "2 cups fresh, frozen, or canned corn kernels, divided",
    "1/2 cup freshly grated Parmesan cheese, plus more for serving",
    "1/4 teaspoon crushed red pepper (optional)",
    "1/3 cup torn fresh basil or mint, plus more for garnish",
    "1 tablespoon lemon juice"
]

regex = RecipeRegexPatterns()
# RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex, debug=False).parse2()
# parsey = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex, debug=True)
# parsey.parse2()
# parsey.parsed_ingredient
# regex.list_attrs()
output = []

for ingredient in ingredient_strings:
    # parsed_string = RecipeParser(ingredient, regex, debug=False)
    parser = RecipeParser(ingredient, regex=regex, debug=False)
    parser.parse2()
    parsed_string = parser.parsed_ingredient
    output.append(parsed_string)
    print(f"Original: {ingredient}")
    print(f"Parsed: {parsed_string}")
    print("\n")

# ingredient_parts = {
#     "quantity": None,
#     "min_quantity": None,
#     "max_quantity": None,
#     "unit": None,
#     "secondary_unit": None,
#     "name": None,
#     "preparation": None,
#     "notes": None
#     }

for out in output:
    print(out)
    # print("\n")

ingredient = output[4]

for k, v in regex.find_matches(ingredient).items():
    print(f"Key: {k} - {v}")
    # print(f"Value: {v}")
# final_parser.__name__
def final_parser(ingredient):
    """
    Parse the ingredient string into its component parts.
    """
    ingredient_parts = {
        "unit": None,
        "quantity": None,
        "min_quantity": None,
        "max_quantity": None,

        "secondary_unit": None,
        "secondary_quantity": None,
        "secondary_min_quantity": None,
        "secondary_max_quantity": None,
        
        "extra_units": None,
        "ingredient_name": None,
        "preparation": None,
        "notes": None,

        "raw_ingredient": ingredient,
        "quantity_unit_pairs": None
        }
    
    for k, v in regex.find_matches(ingredient).items():
        print(f"Key: {k} - {v}")

    # Set default values to populate
    unit = None
    quantity = None
    min_quantity = None
    max_quantity = None
    secondary_unit = None
    secondary_quantity = None
    secondary_min_quantity = None
    secondary_max_quantity = None
    quantity_unit_pairs = None

    # unit = None
    # secondary_unit = None
        
    # get all of the units in the ingredient string
    every_unit = regex.UNITS_PATTERN.findall(ingredient)

    # get the basic units in the ingredient string
    basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient)

    # get the nonbasic units in the ingredient string
    nonbasic_units = set(every_unit) - set(basic_units)

    # instances of a number followed by a unit
    number_then_unit = regex.ANY_NUMBER_THEN_UNIT.findall(ingredient)

    # look for quantity ranges (numbers separated by a hyphen, e.g. 1-2 cups of sugar)
    quantity_ranges = regex.QUANTITY_DASH_QUANTITY.findall(ingredient)
    quantity_unit_ranges = regex.QUANTITY_DASH_QUANTITY_UNIT.findall(ingredient)
    
    # 1. Deal with any quantity ranges
    # if a quantity unit range was found ("1 - 2 cups"), then lets try and get the range separated by the unit
    # by using the QUANTITY_DASH_QUANTITY pattern and the UNIT_PATTERN pattern
    if quantity_unit_ranges:
        range_values = [regex.QUANTITY_DASH_QUANTITY.findall(match)[0] for match in quantity_unit_ranges]
        range_units  = [regex.UNITS_PATTERN.findall(match)[0] for match in quantity_unit_ranges]

        # split the range values into a list of lists
        split_range_values = [i.split("-") for i in range_values]

        # get the average of each of the range values
        range_avgs = [sum([float(num_str) for num_str in i]) / 2 for i in split_range_values]
        # range_avgs = [sum([float(num_str) for num_str in i.split("-")]) / 2 for i in range_values]

        # Primary ingredient and quantities (i.e. use the first quantity and unit as the primary quantity and unit)
        unit = range_units[0]

        # get the quantity from the range avgs and the min and max values from the split range values
        quantity = range_avgs[0]
        
        min_quantity, max_quantity = float(split_range_values[0][0]), float(split_range_values[0][1])

        # Secondary ingredient and quantities (i.e. use the second quantity and unit as the secondary quantity and unit)
        secondary_unit = range_units[1:]

        # get the quantity from the range avgs and the min and max values from the split range values
        secondary_quantity = range_avgs[1:]


        print(f"Range Values: {range_values}\nRange Units: {range_units}\nRange Avgs: {range_avgs}\nQuantity: {quantity} ({min_quantity} - {max_quantity})")


    # if there are any quantity ranges, then we need to treat the 2 spaced numbers 2 seperate numbers, a min and max
    


    if number_then_unit:
        
        # get the quantities and units from the number then unit matches
        quantities = [regex.ALL_NUMBERS.findall(num)[0] for num in number_then_unit]
        units = [regex.UNITS_PATTERN.findall(num)[0] for num in number_then_unit]

        print(f"Number then units: {number_then_unit}\nQuantities: {quantities}\nUnits: {units}")

        primary_units = units[0] # the first unit is the primary unit
        secondary_units = units[1:] # any units after the first unit are secondary units

        # primary_units = [unit for unit in units if unit in regex.constants["BASIC_UNITS_SET"]]
        # secondary_units = set(units) - set(primary_units)
        primary_quantity = quantities[0]
        secondary_quantity = quantities[1:]

        print(f"Primary Unit: {primary_units}\nSecondary Units: {secondary_units}")

    basic_units = regex.BASIC_UNITS_PATTERN.findall(ingredient)
    all_units = regex.UNITS_PATTERN.findall(ingredient)




# ingred = "a"

def _a_or_an_units(ingredient: str) -> str:
    """
    Add "a" or "an" to the beginning of the ingredient string if it starts with a vowel.
    """
    ingredient = "a lemon"

    # lowercase and split the ingredient string
    ingredient = ingredient.lower()
    split_ingredient = ingredient.split()

    matched_nums = re.findall(regex.ALL_NUMBERS, ingredient)

    if split_ingredient[0] in ["a", "an"] and not matched_nums:
        split_ingredient[0] = "1"
        ingredient = " ".join(split_ingredient)
        return ingredient



    # check what Units are in the string (if any)
    matched_units = re.findall(regex.UNITS_PATTERN, ingredient)

    split_ingredient = ingredient.split()


    vowels = ["a", "e", "i", "o", "u"]
    first_letter = ingredient.split()[0][0].lower()
    return "an" if first_letter in vowels else "a"

ingred.split()


for key, val in regex.find_matches(output[0]).items():

    print(f"Key: {key}")
    print(f"Val: {val}")
    print("\n")

# regex.constants["UNICODE_FRACTIONS"]
parsed_string = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex)
parsed_string = RecipeParser(ingredient=f"""2 1/2 cups of sugar""", regex=regex)

# parsed_string = RecipeParser(ingredient='1 tablespoon all-purpose flour', regex=regex)
parsed_string = RecipeParser(ingredient="1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces", regex=regex)

# parsed_string = RecipeParser(f""""1 - 1 1/2 cups of sugar""", regex)
parsed = parsed_string.normalized_string
parsed
# ingredient = '2 0.5 cups of sugar'
# ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'
regex.SPACE_SEP_NUMBERS

# check if there are any spaced numbers (e.g. 2 1/2 cups of sugar or 2 8 ounce salmons)
spaced_nums = re.findall(regex.SPACE_SEP_NUMBERS, parsed)

# check what Units are in the string (if any)
matched_units = re.findall(regex.UNITS_PATTERN, parsed)
matched_units

matched_basic_units = re.findall(regex.BASIC_UNITS_PATTERN, parsed)
matched_basic_units

secondary_units = set(matched_units) - set(matched_basic_units)


# only do below if there are any units avaliable: (IF NO UNITS, treat multi numbers are multiplicative and )
# if this value is Truthy, then we need to treat the 2 spaced numbers as additive values,
# all other units will be multiplied (i.e. 2 8-ounce salmon fillets = 16 ounces of salmon)
volumetric_units = [i for i in matched_units if i in regex.constants["VOLUME_UNITS_SET"]]

has_spaced_nums      = bool(spaced_nums)
has_units            = bool(matched_units)
has_basic_units      = bool(matched_basic_units)
has_volumetric_units = bool(volumetric_units)

# has_single_number    = not bool(spaced_nums)



def pull_out_units(ingredient):
    """
    Pull out units from the ingredient string.
    """
    # Define the regular expression pattern to match units
    pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)')
    # Find all matches of units in the ingredient string
    matches = pattern.findall(ingredient)
    # Iterate over the matches and print them
    for match in matches:
        print(match)



spaced_nums

regex.list_attrs()

re.findall(regex.SPLIT_SPACED_NUMS, "2 1/2")

# check what Units are in the string (if any)
matched_units = re.findall(regex.UNITS_PATTERN, parsed)

# only do below if there are any units avaliable: (IF NO UNITS, treat multi numbers are multiplicative and )
# if this value is Truthy, then we need to treat the 2 spaced numbers as additive values,
# all other units will be multiplied (i.e. 2 8-ounce salmon fillets = 16 ounces of salmon)
volumetric_units = [i for i in matched_units if i in regex.constants["VOLUME_UNITS_SET"]]

VOLUME_UNITS_SET = set()

for key, pattern in regex.constants["VOLUME_UNITS"].items():

    print(f"key: {key}")
    print(f"Pattern: {pattern}")
    VOLUME_UNITS_SET.add(key)
    for val in pattern:
        VOLUME_UNITS_SET.add(val)

re.findall(regex.ALL_NUMBERS, " 1 cats are grate 88 for i like 2 dogs")
for match, pattern in regex.find_matches(parsed).items():
    print(f"Match: {match}")
    print(f"Pattern: {pattern}")
RecipeRegexPatterns()

RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
             regex).parse()

RecipeParser("2 1/2 cups diced tomatoes", 
             regex).parse()
RecipeParser("2oz-3oz diced tomatoes", 
             regex).parse()
RecipeParser('1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05 - 1/2', 
             regex).parse()
'1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'
RecipeParser("1-2 cups diced tomatoes", 
             regex).parse()
RecipeParser("1 cups diced tomatoes", 
             regex).parse()
RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
             regex)._fraction_str_to_decimal("2233")
# Example string
example_string = '1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'

# # Regular expression pattern to match decimal values with trailing zeros
# decimal_pattern = re.compile(r'\b(\d+(\.\d+)?\.0+)\b')

# # Find all matches of decimal values with trailing zeros in the string
# matches = decimal_pattern.findall(example_string)

# Regular expression pattern to match decimal values with trailing zeros
decimal_pattern = re.compile(r'\b(?<!\d)(\d+(\.\d+)?\.0+)\b')

# Find all matches of decimal values with trailing zeros in the string
matches = decimal_pattern.findall(example_string)


# Replace each match with its corresponding whole number
for match in matches:
    print(f"Match: {match}")
    whole_number = match[0].split('.')[0]  # Extract the whole number part
    print(f"whole_number: {whole_number}")
    example_string = example_string.replace(match[0], whole_number)
    print(f"Updated string: {example_string}")
    print(f"\n")

# Example string
example_string = '1.000 - 2.0 cups diced tomatoes 1.5 - 2.0 and 1.5 to 0.04 and 2.05'

# Regular expression pattern to match decimal values
decimal_pattern = re.compile(r'\b(\d+(\.\d+)?)\b')

# Function to check if a decimal value only has 0 values after the decimal point
def has_only_zeros(decimal):
    if '.' in decimal:
        _, fractional_part = decimal.split('.')
        return all(char == '0' for char in fractional_part)
    return False

# Find all matches of decimal values in the string
matches = decimal_pattern.findall(example_string)

# Replace invalid decimals with their whole number representation
for match in matches:
    decimal_value = match[0]
    if has_only_zeros(decimal_value):
        whole_number = str(int(float(decimal_value)))
        example_string = example_string.replace(decimal_value, whole_number)
print("Updated string:", example_string)

RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
             regex).parse()
RecipeParser("1-2 cups diced tomatoes", 
             regex).parse()
RecipeParser("1 cups diced tomatoes", 
             regex).parse()
RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1 - 1/4 cups of sugar", 
             regex)._fraction_str_to_decimal("2233")

fraction_str = "1 2/3"
fraction_str.split(" ")
# /^([0-9\/]+)-([\da-z\.-]+)\.([a-z\.]{2,5})$/
# /^([0-9\/]+)-([0-9\/]+)$/
# Regex for splititng whole numbers and fractions e.g. 1 1/2 -> ["1", "1/2"]
SPLIT_INTS_AND_FRACTIONS_PATTERN = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')

SPLIT_INTS_AND_FRACTIONS_PATTERN = re.compile(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$')
QUANTITY_RANGE_PATTERN = re.compile(r"\d+\s*(?:\s*-\s*)+\d+")

# INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'^(\d+\s*(?:\s*-\s*)+\d+)\s+((?:\d+\s*/\s*\d+)?)$')
INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'^(?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?)$')
INTS_AND_FRACTIONS_RANGE_PATTERN = re.compile(r'\A[0-9]+\s*\-\s*[0-9]+\Z')
# (?:[1-9][0-9]*|0)(?:\/[1-9][0-9]*)?

input_strings = ["2/3 - 4/5", "2/3 - 4/5", "2/ 3 - 4/ 5"]


"2-3"
for input_str in input_strings:
    # match = re.match(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)\s*-\s*(\d+)\s+((?:\d+\s*/\s*\d+)?)$', input_str)
    match =  re.match(INTS_AND_FRACTIONS_RANGE_PATTERN, input_str)
    if match:
        print(f"Match found - match: {match}")
        # first_whole_number = match.group(1)
        # first_fraction = match.group(2)
        # second_whole_number = match.group(3)
        # second_fraction = match.group(4)
        # print([first_whole_number, first_fraction, second_whole_number, second_fraction])

int_and_fraction = "1 22 / 33"

match = re.match(SPLIT_INTS_AND_FRACTIONS_PATTERN, int_and_fraction)
whole_number = match.group(1)
fraction_str = match.group(2)



split_fraction = [i.strip() for i in fraction_str.split("/")]
Fraction(int(split_fraction[0]), int(split_fraction[1]))

input_strings = ["1 2/3", "1 2 /3", "1 2/ 3", "1 22/  33"]

for input_str in input_strings:
    match = re.match(r'^(\d+)\s+((?:\d+\s*/\s*\d+)?)$', input_str)
    if match:
        whole_number = match.group(1)
        fraction = match.group(2)
        print([whole_number, fraction])
# Split the fraction string into its numerator and denominator
split_fraction = fraction_str.replace(" ", "").split("/")
numerator = int(split_fraction[0])
denominator = int(split_fraction[1])

# Convert the fraction to a decimal
# return round(float(Fraction(numerator, denominator)), 3)
tmp = "2/3"
tmp.split("/")
split_fraction = [i.strip() for i in tmp.split("/")]

if len(split_fraction) == 1:
    int(split_fraction[0])
numerator = int(split_fraction[0])
denominator = int(split_fraction[1])

# Convert the fraction to a decimal
round(float(Fraction(numerator, denominator)), 3)


RecipeParser("2lb - 1lb cherry tomatoes", regex).parse()

regex.patterns.keys()
parser = RecipeParser(ingredient, regex)
output = parser.parse()

output
RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1/4 cups of sugar", 
             regex).parse()
RecipeParser("2lb - 1lb cherry tomatoes", regex).parse()
# Regex pattern for finding quantity and units without space between them.
# Assumes the quantity is always a number and the units always a letter.
Q_TO_U = re.compile(r"(\d)\-?([a-zA-Z])")
U_TO_Q = re.compile(r"([a-zA-Z])(\d)")
U_DASH_Q = re.compile(r"([a-zA-Z])\-(\d)")

sentence = "2lb-1oz cherry tomatoes"
sentence = Q_TO_U.sub(r"\1 \2", sentence)
sentence = U_TO_Q.sub(r"\1 \2", sentence)
U_DASH_Q.sub(r"\1 - \2", sentence)

re.findall(regex.FRACTION_PATTERN, ingredient)
re.findall(regex.RANGE_WITH_TO_OR_PATTERN, output)
regex.QUANTITY_RANGE_PATTERN.sub(r"\1-\5", output)
regex.RANGE_WITH_TO_OR_PATTERN.search(output)
STRING_RANGE_PATTERN.sub(r"\1-\5", output)
STRING_RANGE_PATTERN = re.compile(
    r"([\d\.]+)\s*(\-)?\s*(to|or)\s*(\-)*\s*([\d\.]+(\-)?)"
)

iterfinder = re.finditer(regex.RANGE_WITH_TO_OR_PATTERN, output)

for match in iterfinder:
    print(match.group())
    print(match.start())
    print(match.end())
    print(match.span())
    print("\n")

# QUANTITY_RANGE_PATTERN
# # RANGE_WITH_TO_OR_PATTERN
# BETWEEN_NUM_AND_NUM_PATTERN

############################



F_PATTERN = r'([+-]?[^+-]+)'
import re
from fractions import Fraction

def parse_mixed_fraction(fraction_str: str) -> list:
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

def sum_parsed_fractions(fraction_list: list, truncate: int = 3 ) -> float:
    
    total = 0
    for i in fraction_list:
        total += Fraction(i)
    
    return round(float(total), truncate)

# Test the function
input_string1 = '1 2/3'
input_string2 = '1 2 /  3'

# input_string2 = '1 2 / 3'
print(parse_mixed_fraction(input_string1))  # Output: ['1', '2/3']
print(parse_mixed_fraction(input_string2))  # Output: ['1', '2/3']

ingredient_strings = [
    "2 tbsp sugar",
    "two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water",
    "3/4 tsp salt",
    "1 1/2 cups diced tomatoes",
    "2 cloves garlic, minced",
    "1/4 lb bacon, diced",
    "1/2 cup breadcrumbs",
    "1/4 cup grated Parmesan cheese",
    "warmed butter (1 - 2 sticks)",
    "honey, 1/2 tbsp of sugar",
    "- butter (1 - 2 sticks)",
    "peanut butter, 1-3 tbsp",
    "between 1/2 and 3/4 cups of sugar",
    "1/3 pound of raw shrimp, peeled and deveined",
    "1/4 cup of grated Parmesan cheese",
    ]

ingredient = ingredient_strings[1]

regex.patterns.keys()

def parse_mixed_fraction(fraction_str: str) -> list:
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

def sum_parsed_fractions(fraction_list: list, truncate: int = 3 ) -> float:
    
    total = 0
    for i in fraction_list:
        total += Fraction(i)
    
    return round(float(total), truncate)

ingredient = 'two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water'
# multifrac_pattern = re.compile('(\\d*\\s*\\d/\\d+)')
multifrac_pattern = regex.MULTI_PART_FRACTIONS_PATTERN

#### 2 methods to replace fractions in the original string with their sum 
# - Using findall() and then replacing the summed values with the original fractions string
# - Using finditer() and then replacing the original fractions with the summed values based on match indices
# findall() method 
fractions = re.findall(multifrac_pattern, ingredient)
# Replace fractions in the original string with their sum
updated_ingredient = ingredient
for f in fractions:
    parsed_fraction = parse_mixed_fraction(f)
    sum_fraction = sum_parsed_fractions(parsed_fraction)
    updated_ingredient = updated_ingredient.replace(f, str(sum_fraction))

# print(updated_ingredient)

# finditer() method
fractions = re.finditer(multifrac_pattern, ingredient)

# Replace fractions in the original string with their sum based on match indices
updated_ingredient = ingredient
offset = 0

for match in fractions:

    # keep track of the offset to adjust the index of the match
    start_index = match.start() + offset
    end_index = match.end() + offset
    matched_fraction = match.group()

    # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
    parsed_fraction = parse_mixed_fraction(matched_fraction)

    # Replace the matched fraction with the sum of the parsed fraction
    sum_fraction = sum_parsed_fractions(parsed_fraction)

    # Insert the sum of the fraction into the updated ingredient string
    updated_ingredient = updated_ingredient[:start_index] + str(sum_fraction) + updated_ingredient[end_index:]

    # Update the offset to account for the difference in length between the matched fraction and the sum of the fraction
    offset += len(str(sum_fraction)) - len(matched_fraction)
updated_ingredient

update_values = [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

parse_mixed_fraction(fractions[0])

matches = multifrac_pattern.search(ingredient)

for i in ingredient_strings:
    print(f"Ingredient: {i}")
    fracs = re.findall(multifrac_pattern, i)
    print(f"- Fractions: {fracs}")
    #clean the fractions
    for frac in fracs:
        print(f"---> Cleaned Fractions: {parse_mixed_fraction(frac)}")


    print("\n")
re.findall(multifrac_pattern, ingredient)
sfrac = ['1', '2/3']

float(Fraction(sfrac[0]) + Fraction(sfrac[1]))
matches.group(0)


regex = RecipeRegexPatterns(pattern_list)

ingredient_strings = [
    "2 tbsp sugar",
    "two to three tablespoons ~ of sugar, 1/2 cup of sugar (optional), 1 2/3 tablespoons of water",
    "3/4 tsp salt",
    "1 1/2 cups diced tomatoes",
    "2 cloves garlic, minced",
    "1/4 lb bacon, diced",
    "1/2 cup breadcrumbs",
    "1/4 cup grated Parmesan cheese",
    "warmed butter (1 - 2 sticks)",
    "honey, 1/2 tbsp of sugar",
    "- butter (1 - 2 sticks)",
    "peanut butter, 1-3 tbsp",
    "between 1/2 and 3/4 cups of sugar",
    "1/3 pound of raw shrimp, or 1/4 peeled and deveined",
    "1/4 cup of grated Parmesan cheese",
    ]

parsed_output = []
for i in ingredient_strings:
    parser = RecipeParser(i, regex)
    parsed_ingredient = parser.parse()
    parsed_output.append(parsed_ingredient)

for i in parsed_output:
    print(i)
    print(f"\n")

parser = RecipeParser(ingredient, regex)
ingredient = ingredient_strings[1]
parser = RecipeParser(ingredient, regex)

parser.ingredient
parser.parsed_ingredient

parsed_ingredient = parser.parse()
# Convert word numbers to numerical numbers
# regex.patterns.keys()
# ingredient = regex.NUMBER_WORDS_REGEX_MAP["two"][1].sub(regex.NUMBER_WORDS_REGEX_MAP["two"][0], ingredient)
# regex.NUMBER_WORDS_REGEX_MAP["two"][0]

for word, regex_data in regex.NUMBER_WORDS_REGEX_MAP.items():
    number_value = regex_data[0]
    pattern = regex_data[1]
    if pattern.search(ingredient):
        print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}")
    # print(f"Word: {word} \n Regex Data: {regex_data}")
    # regex_data[0]
    ingredient = pattern.sub(regex_data[0], ingredient)
    # ingredient
    # self.parsed_ingredient = pattern.sub(regex_data[0], self.parsed_ingredient)

regex = RecipeRegexPatterns(pattern_list)

parser = RecipeParser(ingredient, regex)

parser.ingredient
parser.parsed_ingredient

parsed_ingredient = parser.parse()
parser.parsed_ingredient
parser.ingredient
print(parsed_ingredient)





# def _parse_fractions(self):
#     """
#     Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
#     """
#     # print("Parsing fractions")
#     # regex.MULTI_PART_FRACTIONS_PATTERN
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)
#     # [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

#     # ---- 2 methods to replace fractions in the original string with their sum  ----
#     # - Using findall() and then replacing the summed values with the original fractions string
#     # - Using finditer() and then replacing the original fractions with the summed values based on match indices
#     # findall() method 
#     # fractions = re.findall(regex.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
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
#     #     # updated_ingredient = self.parsed_ingredient.replace(f, str(sum_fraction))
#     #     self.parsed_ingredient = self.parsed_ingredient.replace(f, str(sum_fraction))
#     # print(updated_ingredient)

#     # finditer() method
#     fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
#     # fractions = re.finditer(regex.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)

#     # Replace fractions in the original string with their sum based on match indices
#     # updated_ingredient = self.parsed_ingredient
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
#         self.parsed_ingredient = self.parsed_ingredient[:start_index] + " " + str(sum_fraction) + self.parsed_ingredient[end_index:]

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