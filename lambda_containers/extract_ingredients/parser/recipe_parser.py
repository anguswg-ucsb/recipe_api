import re
from typing import List, Dict, Any, Union, Tuple, optional
from fractions import Fraction

# from regex_patterns import regex_patterns
# from regex_patterns import pattern_list, RegexPatterns
from lambda_containers.extract_ingredients.parser.regex_patterns import pattern_list, RegexPatterns

# regex_patterns = RegexPatterns(pattern_list)

# regex_patterns.patterns.keys()

# Step 1: Replace all em dashes, en dashes, and "~" with hyphens
# Step 2: Replace numbers with words with their numerical equivalents
# Step 3: Replace all unicode fractions with their decimal equivalents
# Step 4: Replace all fractions with their decimal equivalents
# Step 5: Remove trailing periods from units and replace all units with their standard abbreviations
# Step 6: Seperate any part of the string that is wrapped in paranthesis and treat this as its own string

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

    def _parse_fractions(self):
        """
        Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
        """
        # print("Parsing fractions")
        # regex_patterns.MULTI_PART_FRACTIONS_PATTERN

        # fractions = re.findall(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # [sum_parsed_fractions(parse_mixed_fraction(f)) for f in fractions]

        # ---- 2 methods to replace fractions in the original string with their sum  ----
        # # - Using findall() and then replacing the summed values with the original fractions string
        # # - Using finditer() and then replacing the original fractions with the summed values based on match indices
        # # findall() method 
        # fractions = re.findall(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)
        # # Replace fractions in the original string with their sum
        # updated_ingredient = ingredient
        # for f in fractions:
        #     parsed_fraction = parse_mixed_fraction(f)
        #     sum_fraction = sum_parsed_fractions(parsed_fraction)
        #     updated_ingredient = updated_ingredient.replace(f, str(sum_fraction))

        # print(updated_ingredient)

        # finditer() method
        fractions = re.finditer(regex_patterns.MULTI_PART_FRACTIONS_PATTERN, self.parsed_ingredient)

        # Replace fractions in the original string with their sum based on match indices
        # updated_ingredient = self.parsed_ingredient
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
            # updated_ingredient = updated_ingredient[:start_index] + str(sum_fraction) + updated_ingredient[end_index:]
            self.parsed_ingredient = self.parsed_ingredient[:start_index] + str(sum_fraction) + self.parsed_ingredient[end_index:]

            # Update the offset to account for the difference in length between the matched fraction and the sum of the fraction
            offset += len(str(sum_fraction)) - len(matched_fraction)




    def _parse_mixed_fraction(fraction_str: str) -> list:
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

    def _sum_parsed_fractions(fraction_list: list, truncate = 3) -> float:
        
        total = 0
        for i in fraction_list:
            total += Fraction(i)
        
        return round(float(total), truncate)
    
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

        print(f"Parsing fractions...")
        print(f" > BEFORE: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")
        self._parse_fractions()
        print(f" > AFTER: \n Ingredient: {self.ingredient} \n Parsed Ingredient: {self.parsed_ingredient} \n")


        print(f'---> Returning parsed ingredient: {self.parsed_ingredient} \n')
        return self.parsed_ingredient
    
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
    "1/3 pound of raw shrimp, peeled and deveined",
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