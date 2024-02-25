import re
from typing import List, Dict, Any, Union, Tuple, optional
from fractions import Fraction
from html import unescape

# from regex_patterns import regex_patterns
# from regex_patterns import pattern_list, RegexPatterns
from lambda_containers.extract_ingredients.parser.regex_patterns import pattern_list, RegexPatterns

# regex_patterns = RegexPatterns(pattern_list)
# Define the regular expression pattern

def _remove_repeat_units(ingredient):
    """
    Remove repeat units from the ingredient string.
    """
    ingredient = "i like to eat 1 oz-2 oz with cats and 1ft-2ft of snow"
    # Define the regular expression pattern to match repeat units
    pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')
    matches = pattern.finditer(ingredient)

    for match in matches:
        print(match.group(0))
        print(match.group(1))
        print(match.group(2))
        print(match.group(3))
        print(match.group(4))

        original_string = match.group(0)
        quantity1 = match.group(1)
        unit1 = match.group(2)
        quantity2 = match.group(3)
        unit2 = match.group(4)

        if unit1 == unit2:
            print(f"Repeat units found: {unit1}")
            print(f"Original string: {original_string}")
            print(f"Quantity1: {quantity1}, Unit1: {unit1}, Quantity2: {quantity2}, Unit2: {unit2}")
            print(f"----> REPEAT UNITS: {unit1}")
            ingredient = ingredient.replace(original_string, f"{quantity1} - {quantity2} {unit1}")
            print("\n")

        print("\n")

    repeat_ranges = pattern.findall(ingredient)



    re.sub(pattern, r'\1 - \3\4', ingredient)
    # Replace repeat units with the first unit
    result = re.sub(pattern, r'\1 - \3', ingredient)
    return result

pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')
pattern = re.compile(r'(\d+)\s*([a-zA-Z]+)\s*-\s*(\d+)\s*([a-zA-Z]+)')

# Test the pattern
working_string = "1oz-2oz"

match = pattern.match(working_string)

faulty_string = "i like to eat 1oz-2oz with cats and 1ft-2ft of snow"
match2 = pattern.findall(faulty_string) # No match
match2

number1 = match.group(1)
string1 = match.group(2)
number2 = match.group(3)
string2 = match.group(4)

print(f"Number1: {number1}, String1: {string1}, Number2: {number2}, String2: {string2}")
if match:
    number1 = match.group(1)
    string1 = match.group(2)
    number2 = match.group(3)
    string2 = match.group(4)
    
    print(f"Number1: {number1}, String1: {string1}, Number2: {number2}, String2: {string2}")
else:
    print("No match")

# def remove_first_unit(input_string: str, units: list) -> str:
#     """
#     Removes the first instance of a unit from the input string.
    
#     Args:
#         input_string (str): The input string to process.
#         units (list): A list of possible units.
        
#     Returns:
#         str: The input string with the first instance of a unit removed.
#     """
#     # Construct a regex pattern to match the first instance of a unit
#     # pattern = r'\b(\d+\s*(' + '|'.join(units) + r')?)\s*-\s*(\d+\s*(' + '|'.join(units) + r'))\b'
#     # pattern = r'\b(\d+\s*(' + '|'.join(units) + r')?)?\s*-\s*(\d+)\s*(' + '|'.join(units) + r')\b'
#     pattern = r'\b(\d+)\s*(' + '|'.join(units) + r')\s*-\s*(\d+)\s*(' + '|'.join(units) + r')\b'
    
#     re.findall(regex_patterns.UNITS_PATTERN, input_string)

#     # Replace the first instance of a unit with an empty string
#     result = re.sub(pattern, r'\1 - \3', input_string, count=1)
    
#     return result

# # Test the function
# units = ["oz", "grams", "kg", "lbs"]
# input_string = "1oz-2oz"
# output_string = remove_first_unit(input_string, units)
# print("Original string:", input_string)
# print("String with first unit removed:", output_string)

# Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# Step 2: Replace numbers with words with their numerical equivalents
# Step 3: Replace all unicode fractions with their decimal equivalents
# Step 4: Replace all fractions with their decimal equivalents
# Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# Step 6: Seperate any part of the string that is wrapped in paranthesis and treat this as its own string
# Define the regular expression pattern to match numbers with a hyphen in between them
def update_ranges(input_string, pattern, replacement_function=None):

    # input_string = tmp
    # pattern = regex_patterns.BETWEEN_NUM_AND_NUM_PATTERN
    # replacement_function = replace_and_with_hyphen

    matches = pattern.findall(input_string)
    # matched_ranges = [match.split("-") for match in matches]

    if replacement_function:
        print(f"Replacement Function given")
        matched_ranges = [replacement_function(match).split("-") for match in matches]
    else:
        print(f"No Replacement Function given")
        matched_ranges = [match.split("-") for match in matches]

    updated_ranges = [" - ".join([str(int(i)) for i in match if i]) for match in matched_ranges]
    
    # Create a dictionary to map the matched ranges to the updated ranges
    ranges_map = dict(zip(matches, updated_ranges))

    # Replace the ranges in the original string with the updated ranges
    for original_range, updated_range in ranges_map.items():
        print(f"Original Range: {original_range}")
        print(f"Updated Range: {updated_range}")
        # if replacement_function:
        #     print(f"Replacement Function given")
        #     updated_range = replacement_function(updated_range)
        input_string = input_string.replace(original_range, updated_range)
        print("\n")

    return input_string

def replace_and_with_hyphen(match):
    # Replace "and" and "&" with hyphens
    return match.replace("and", "-").replace("&", "-")

# Test string
tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 -- 45 inches, cats do between 1  and 5 digs, i like between 1 and 2 mm'

# Update ranges matched by QUANTITY_RANGE_PATTERN
tmp = update_ranges(tmp, regex_patterns.QUANTITY_RANGE_PATTERN)

# Update ranges matched by BETWEEN_NUM_AND_NUM_PATTERN, with replacement function to replace "and" and "&"
tmp = update_ranges(tmp, regex_patterns.BETWEEN_NUM_AND_NUM_PATTERN, replace_and_with_hyphen)

class RecipeParser:
    """
    A class to parse recipe ingredients into a standard format.

    Args:
        ingredient (str): The ingredient to parse.
    """

    def __init__(self, ingredient: str,  regex_patterns: RegexPatterns):
        self.ingredient = ingredient
        self.parsed_ingredient = ingredient
        self.regex_patterns = regex_patterns

    def parsed_ingredient(self):
        
        return self.parsed_ingredient
    
    
    def _drop_special_dashes(self):
        # print("Dropping special dashes")
        self.parsed_ingredient = self.parsed_ingredient.replace("—", "-").replace("–", "-").replace("~", "-")
        return
    
    def _parse_number_words(self):
        """
        Replace number words with their corresponding numerical values in the parsed ingredient.
        """
        # print("Parsing number words")
        for word, regex_data in self.regex_patterns.NUMBER_WORDS_REGEX_MAP.items():
            pattern = regex_data[1]
            # print statement if word is found in ingredient and replaced
            if pattern.search(self.parsed_ingredient):
                print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}")
            self.parsed_ingredient = pattern.sub(regex_data[0], self.parsed_ingredient)

    def _clean_html_and_unicode(self) -> None:
        """Unescape fractions from HTML code coded fractions to unicode fractions."""

        # Unescape HTML
        self.parsed_ingredient = unescape(self.parsed_ingredient)
        # regex_patterns.UNICODE_FRACTIONS
        # Replace unicode fractions with their decimal equivalents
        for unicode_fraction, decimal_fraction in self.regex_patterns.UNICODE_FRACTIONS.items():
            self.parsed_ingredient = self.parsed_ingredient.replace(unicode_fraction, decimal_fraction)

    def _add_whitespace(self):
        # regex pattern to match consecutive sequences of letters or digits
        pattern = re.compile(r'([a-zA-Z]+)(\d+)|(\d+)([a-zA-Z]+)')

        # replace consecutive sequences of letters or digits with whitespace-separated sequences
        self.parsed_ingredient = re.sub(pattern, r'\1 \2\3 \4', self.parsed_ingredient)
    
    def _fractions_to_decimals(self) -> None:
        """
        Replace fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        fractions = re.findall(regex_patterns.FRACTION_PATTERN, self.parsed_ingredient)

        split_frac = [i.replace(" ", "").split("/") for i in frac]
        split_frac = [(int(f[0]), int(f[1])) for f in split_frac]
        fraction_decimal = [round(float(Fraction(f[0], f[1])), 3) for f in split_frac]

        # replace fractions in original string with decimal equivalents
        for i, f in enumerate(fractions):
            self.parsed_ingredient = self.parsed_ingredient.replace(f, str(fraction_decimal[i]))

    def _force_ws(self):
        
        """ Forces spaces between numbers and units and between units and numbers."""

        Q_TO_U = re.compile(r"(\d)\-?([a-zA-Z])")
        U_TO_Q = re.compile(r"([a-zA-Z])(\d)")
        U_DASH_Q = re.compile(r"([a-zA-Z])\-(\d)")

        self.parsed_ingredient = Q_TO_U.sub(r"\1 \2", self.parsed_ingredient)
        self.parsed_ingredient = U_TO_Q.sub(r"\1 \2", self.parsed_ingredient)
        self.parsed_ingredient = U_DASH_Q.sub(r"\1 - \2", self.parsed_ingredient)
    
    def _fix_ranges(self):
        """
        Fix ranges in the parsed ingredient.
        """
        # print("Fixing ranges")
        # Define the regular expression pattern to match ranges

        tmp ='i like to eat 1-2 oz with cats and 1 - 2 ft of snow and 1 -- 45 inches, cats do between 1  and 5 digs, i like between 1 and 2 mm'
        # matches = regex_patterns.QUANTITY_RANGE_PATTERN.findall(self.parsed_ingredient)
        matches = regex_patterns.QUANTITY_RANGE_PATTERN.findall(tmp)
        # matches = Q_TO_Q_PATTERN.findall(tmp)

        matched_ranges = [match.split("-") for match in matches]
        updated_ranges = [" - ".join([str(int(i)) for i in match if i]) for match in matched_ranges]

        # Create a dictionary to map the matched ranges to the updated ranges
        ranges_map = dict(zip(matches, updated_ranges))

        # Replace the ranges in the original string with the updated ranges
        for original_range, updated_range in ranges_map.items():
            print(f"Original Range: {original_range}")
            print(f"Updated Range: {updated_range}")
            # self.parsed_ingredient = self.parsed_ingredient.replace(original_range, updated_range)
            tmp = tmp.replace(original_range, updated_range)
            print("\n")

        # Find ranges that match the pattern "between 1 and 5"
        between_matches = regex_patterns.BETWEEN_NUM_AND_NUM_PATTERN.findall(tmp)
        between_matches


        # Replace "and" and "&" with hyphens
        replaced_matches = [match.replace("and", "-").replace("&", "-").split("-") for match in between_matches]
        [" - ".join([str(int(i)) for i in match if i]) for match in replaced_matches]

        replaced_matches = [match.replace("and", "-").replace("&", "-") for match in between_matches]
        updated_between_matches = [" - ".join([str(int(i)) for i in match.split("-") if i]) for match in replaced_matches]

        # Create a dictionary to map the matched ranges to the updated ranges
        updated_between_ranges = dict(zip(between_matches, updated_between_matches))

        # Replace the ranges in the original string with the updated ranges
        for original_range, updated_range in updated_between_ranges.items():
            print(f"Original Range: {original_range}")
            print(f"Updated Range: {updated_range}")
            # self.parsed_ingredient = self.parsed_ingredient.replace(original_range, updated_range)
            tmp = tmp.replace(original_range, updated_range)
            print("\n")

        


        # Split the ranges into a list of strings
        # between_matches = 

        between_matches.split(" and ")

        # Replace the ranges in the original string with the updated ranges
        for match in between_matches:
            print(match)
            # update the original string with the updated range
            tmp = tmp.replace(match, updated_ranges[between_matches.index(match)])
            print("\n")



        



        for match in matches:
            print(match)

            # update the original string with the updated range
            tmp = tmp.replace(match, updated_ranges[matches.index(match)])

            original_string = match
            quantity1 = match[0]
            quantity2 = match[1]

            # Replace the range with the average of the two quantities
            average = (int(quantity1) + int(quantity2)) / 2
            self.parsed_ingredient = self.parsed_ingredient.replace(original_string, str(average))

        for match in matches:
            print(match)



            original_string = match.group(0)
            quantity1 = match.group(1)
            quantity2 = match.group(2)

            # Replace the range with the average of the two quantities
            average = (int(quantity1) + int(quantity2)) / 2
            self.parsed_ingredient = self.parsed_ingredient.replace(original_string, str(average))

    def _parse_fractions(self):
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        # regex_patterns.MULTI_PART_FRACTIONS_PATTERN
        # fractions = re.findall(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # fractions = re.findall(regex_patterns.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)
        # [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

        # ---- 2 methods to replace fractions in the original string with their sum  ----
        # - Using findall() and then replacing the summed values with the original fractions string
        # - Using finditer() and then replacing the original fractions with the summed values based on match indices
        # findall() method 
        # fractions = re.findall(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # Replace fractions in the original string with their sum
        # updated_ingredient = ingredient
        # for f in fractions:
        #     print(f"Fraction: {f}")
        #     # remove "and" and "&" from the matched fraction
        #     matched_fraction = f.replace("and", " ").replace("&", " ")

        #     # Parse the matched fraction, make sure it's in the correct format, to be able to be summed
        #     parsed_fraction = self._parse_mixed_fraction(matched_fraction)

        #     # Replace the matched fraction with the sum of the parsed fraction
        #     sum_fraction = self._sum_parsed_fractions(parsed_fraction)
        #     # updated_ingredient = self.parsed_ingredient.replace(f, str(sum_fraction))
        #     self.parsed_ingredient = self.parsed_ingredient.replace(f, str(sum_fraction))
        # print(updated_ingredient)

        # finditer() method
        fractions = re.finditer(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # fractions = re.finditer(regex_patterns.MULTI_PART_FRACTIONS_PATTERN_AND, self.parsed_ingredient)

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

    def _sum_parsed_fractions(self, fraction_list: list, truncate = 3) -> float:
        
        total = 0
        for i in fraction_list:
            total += Fraction(i)
        
        return round(float(total), truncate)
    
    def _drop_special_characters(self):

        # Drop special cases of dashes with standard hyphens
        self.parsed_ingredient = self.parsed_ingredient.replace(".", " ")

    # def _fix_ranges(self):


    def parse(self):
        # Drop special cases of dashes with standard hyphens
        print("Dropping special dashes...")
        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        self._drop_special_dashes()

        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        # Convert all number words to numerical numbers
        print("Parsing number words...")
        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        self._parse_number_words()

        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        print(f"Parsing HTML and unicode...")

        # Clean HTML and unicode fractions
        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        self._clean_html_and_unicode()
        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        
        # print(f"Adding whitespace...")
        # print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        # # self._add_whitespace()
        # self._force_ws()
        # print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        # print(f"Parsing fractions...")

        # # Replace fractions with their decimal equivalents
        # print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        # # self._fractions_to_decimals()
        # print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        self._parse_fractions()
        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        print(f"Adding whitespace...")
        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        # self._add_whitespace()
        self._force_ws()
        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")

        print(f'---> Returning parsed ingredient: {self.parsed_ingredient} \n')
        return self.parsed_ingredient
    
#################### Test the RecipeParser class ####################
ingredient_strings = [
    "\u215b tbsp sugar",
    "two to three tablespoons ~ of sugar, 1 2/3 tablespoons of water",
    "3/4 tsp salt",
    "1 1/2 cups diced tomatoes",
    "1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1/4 cups of sugar",
    "1 2/3 tablespoons of lettuce",
    "1 and 3/3 tablespoons of lettuce",
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

ingredient = ingredient_strings[4]
regex_patterns = RegexPatterns(pattern_list)

regex_patterns.patterns.keys()
parser = RecipeParser(ingredient, regex_patterns)
output = parser.parse()

output
RecipeParser("1-2 cups diced tomatoes, tomatoes 1oz-2oz, between 1 and 3/4 cups of sugar, 1/4 cups of sugar", regex_patterns).parse()
RecipeParser("2lb - 1lb cherry tomatoes", regex_patterns).parse()
# Regex pattern for finding quantity and units without space between them.
# Assumes the quantity is always a number and the units always a letter.
Q_TO_U = re.compile(r"(\d)\-?([a-zA-Z])")
U_TO_Q = re.compile(r"([a-zA-Z])(\d)")
U_DASH_Q = re.compile(r"([a-zA-Z])\-(\d)")

sentence = "2lb-1oz cherry tomatoes"
sentence = Q_TO_U.sub(r"\1 \2", sentence)
sentence = U_TO_Q.sub(r"\1 \2", sentence)
U_DASH_Q.sub(r"\1 - \2", sentence)

re.findall(regex_patterns.FRACTION_PATTERN, ingredient)
re.findall(regex_patterns.RANGE_WITH_TO_OR_PATTERN, output)
regex_patterns.QUANTITY_RANGE_PATTERN.sub(r"\1-\5", output)
regex_patterns.RANGE_WITH_TO_OR_PATTERN.search(output)
STRING_RANGE_PATTERN.sub(r"\1-\5", output)
STRING_RANGE_PATTERN = re.compile(
    r"([\d\.]+)\s*(\-)?\s*(to|or)\s*(\-)*\s*([\d\.]+(\-)?)"
)

iterfinder = re.finditer(regex_patterns.RANGE_WITH_TO_OR_PATTERN, output)

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

regex_patterns.patterns.keys()

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
multifrac_pattern = regex_patterns.MULTI_PART_FRACTIONS_PATTERN

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


regex_patterns = RegexPatterns(pattern_list)

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
    parser = RecipeParser(i, regex_patterns)
    parsed_ingredient = parser.parse()
    parsed_output.append(parsed_ingredient)

for i in parsed_output:
    print(i)
    print(f"\n")

parser = RecipeParser(ingredient, regex_patterns)
ingredient = ingredient_strings[1]
parser = RecipeParser(ingredient, regex_patterns)

parser.ingredient
parser.parsed_ingredient

parsed_ingredient = parser.parse()
# Convert word numbers to numerical numbers
# regex_patterns.patterns.keys()
# ingredient = regex_patterns.NUMBER_WORDS_REGEX_MAP["two"][1].sub(regex_patterns.NUMBER_WORDS_REGEX_MAP["two"][0], ingredient)
# regex_patterns.NUMBER_WORDS_REGEX_MAP["two"][0]

for word, regex_data in regex_patterns.NUMBER_WORDS_REGEX_MAP.items():
    number_value = regex_data[0]
    pattern = regex_data[1]
    if pattern.search(ingredient):
        print(f"- Found {word} in ingredient. Replacing with {regex_data[0]}")
    # print(f"Word: {word} \n Regex Data: {regex_data}")
    # regex_data[0]
    ingredient = pattern.sub(regex_data[0], ingredient)
    # ingredient
    # self.parsed_ingredient = pattern.sub(regex_data[0], self.parsed_ingredient)

regex_patterns = RegexPatterns(pattern_list)

parser = RecipeParser(ingredient, regex_patterns)

parser.ingredient
parser.parsed_ingredient

parsed_ingredient = parser.parse()
parser.parsed_ingredient
parser.ingredient
print(parsed_ingredient)