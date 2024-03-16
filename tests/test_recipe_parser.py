# pytest library
import pytest

import re

# from recipe_parser import RecipeRegexPatterns
from lambda_containers.extract_ingredients.recipe_parser import RecipeRegexPatterns, RecipeParser

# regex_map = RecipeRegexPatterns()

@pytest.fixture
def regex_map():
    return RecipeRegexPatterns()

# ingredient_strings = [
#     "a lemon",
#     "a 1/2 lemon",
#     "an orange",
#     "1 1/3 cups ground almonds",
#     "1 (8 ounce) container plain yogurt",
#     "a 1-5lb lemon",
#     "1 1/2 cups plus 2 tablespoons sugar, divided",
#     "1/3 cup torn fresh basil or mint, plus more for garnish",
#     # "1/2 cup freshly grated Parmesan cheese, plus more for serving",
#     # "1⁄4 cup prepared lemon curd (from 10-to-12 ounce jar)",
#     "4 (1/2-ounce each) processed American cheese slices",
#     "1 (16 ounce) skinless salmon fillet (1 inch thick)",
#     # "1-2oz of butter, 20-50 grams of peanuts",
#     # "1 1/2 pounds skinless, boneless chicken breasts, cut into 1/2-inch pieces",
#     # "1 tablespoon all-purpose flour",
#     "McDonald's Tartar Sauce"
#     # "4 tablespoons salted butter, divided",
#     # "2 large cloves garlic, minced",
#     # "1/4 teaspoon salt",
#     # "1/4 teaspoon crushed red pepper (optional)"
# ]

# -------------------------------------------------------------------------------
# ---- Simple standard form ingredients tests ----
# Standard form: "1 cup of sugar" (quantity, unit, ingredient)
# -------------------------------------------------------------------------------

def test_standard_formatted_ingredients(regex_map):

    parse1 = RecipeParser("2 tablespoons of sugar", regex_map)
    parse1.parse()
    parsed_ingredient = parse1.to_json()
    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == 'tablespoons'
    assert parsed_ingredient['is_required'] == True

    parse2 = RecipeParser("1/2 cup of sugar", regex_map)
    parse2.parse()
    parsed_ingredient = parse2.to_json()
    assert parsed_ingredient['quantity'] == "0.5"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

    parse3 = RecipeParser("1 1/2 cups of sugar", regex_map)
    parse3.parse()
    parsed_ingredient = parse3.to_json()
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_quantity_and_unit(regex_map):
    parse = RecipeParser("3 pounds of beef", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "3"
    assert parsed_ingredient['unit'] == 'pounds'
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- Multinumber (space separated) tests ----
# -------------------------------------------------------------------------------

def test_simple_multinumber_1(regex_map):
    parse = RecipeParser("1 1/2 cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_simple_multinumber_2(regex_map):
    parse = RecipeParser("1 1/2  cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_simple_multinumber_3(regex_map):
    parse = RecipeParser("1 1/2 1/4 cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '1.5 0.25 cups of sugar'
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_multiple_multinumber_1(regex_map):
    parse = RecipeParser("1 1/2 1/4 1/8 cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '1.5 0.375 cups of sugar'
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_multiple_multinumber_2(regex_map):
    parse = RecipeParser("1 1/2 1/4 1/8 1/16 cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '1.5 0.375 0.062 cups of sugar'
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_multiple_multinumber_3(regex_map):
    parse = RecipeParser("1.5 2/3 cups of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '2.167 cups of sugar'
    assert parsed_ingredient['quantity'] == "2.167"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_multiple_multinumber_3(regex_map):
    parse = RecipeParser("3 12 cups of sugar (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '36 cups of sugar (optional)'
    assert parsed_ingredient['quantity'] == "36"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == False


# -------------------------------------------------------------------------------
# ---- Multinumber (space separated) tests ----
# -------------------------------------------------------------------------------
# ingredient = "1 package (8 oz) sliced fresh mushrooms (about 3 cups)"
# ingredient = "1 package (about 3 cups) sliced fresh mushrooms (8 oz)"

# parse = RecipeParser(ingredient, regex_map)
# parse.parse()
# parsed_ingredient = parse.to_json()
# parsed_ingredient

def test_multiple_multinumber_ranges_1(regex_map):
    parse = RecipeParser("3 - 12 1/2 cups of sugar (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '7.75 cups of sugar (optional)'
    assert parsed_ingredient['quantity'] == "7.75"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == False

def test_multiple_multinumber_ranges_2(regex_map):
    parse = RecipeParser("3 - 12 1/2 1/4 cups of sugar (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '7.75 0.25 cups of sugar (optional)'
    assert parsed_ingredient['quantity'] == "7.75"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == False

def test_multiple_multinumber_ranges_3(regex_map):
    parse = RecipeParser("2 1/2 - 4  cups of sugar (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '3.25  cups of sugar (optional)'
    assert parsed_ingredient['quantity'] == "3.25"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['standard_unit'] == 'cup'
    assert parsed_ingredient['is_required'] == False

# parse = RecipeParser('1.5 0.25 cups of sugar', regex_map)
# parse.parse()
# parsed_ingredient = parse.to_json()
# parsed_ingredient
# TODO: Maybe implement this which makes sure to always reduce any SPACE_SEP_NUMBERS to a single number
# TODO:  where possible and do this RECURSIVELY until there are no space separated numbers left. 
# TODO: I've got to see/think if this is a risky approach, just need to narrow down the base case of the recursion...
# ingredient = "1 1/2 1/4 cups of sugar"
# while regex_map.SPACE_SEP_NUMBERS.findall(ingredient):
#     print(f"Start ingredient: {ingredient}")
#     print(f"Continuing reducing multinumbers...")

#     parse = RecipeParser(ingredient, regex_map)
#     parse.parse()

#     ingredient = parsed_ingredient["standardized_ingredient"]
#     print(f"--> End ingredient: {ingredient}")
#     print(f"\n")

# regex_map.print_matches(ingredient)
# regex_map.print_matches("1.75 cups of sugar")

# -------------------------------------------------------------------------------
# ---- Badly designed ingredients tests ----
# -------------------------------------------------------------------------------
    
def test_quantity_only(regex_map):
    parse = RecipeParser("2", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == None
    assert parsed_ingredient['is_required'] == True

def test_no_quantity(regex_map):
    parse = RecipeParser("sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == None
    assert parsed_ingredient['unit'] == None
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- Fraction processing tests ----
# -------------------------------------------------------------------------------
    
def test_fraction_as_quantity(regex_map):
    parse = RecipeParser("1/4 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.25"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_fraction_as_quantity_2(regex_map):
    parse = RecipeParser("1 1/4 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "1.25"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- Fraction/Range tests ----
# -------------------------------------------------------------------------------
    
def test_fraction_range_as_quantity_1(regex_map):
    parse = RecipeParser("1-1/2 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_fraction_range_as_quantity_2(regex_map):
    parse = RecipeParser("1/2-1 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_fraction_dupe_units_range_quantity_1(regex_map):
    parse = RecipeParser("1cup-1/2 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_fraction_dupe_units_range_quantity_2(regex_map):
    parse = RecipeParser("1/2 cup-1 cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_fraction_dupe_units_range_quantity_3(regex_map):
    parse = RecipeParser("1/2cup-1cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == "0.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True
# -------------------------------------------------------------------------------
# ---- Unicode fraction tests ----
# -------------------------------------------------------------------------------
def test_single_unicode_fractions_1(regex_map):
    parse = RecipeParser("½cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == ' 0.5 cup of sugar' # TODO: add a strip() to the end of the standardized_ingredient
    assert parsed_ingredient['quantity'] == "0.5"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_single_unicode_fractions_2(regex_map):
    parse = RecipeParser("⅓ sugar cups", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == ' 0.333 sugar cups' # TODO: add a strip() to the end of the standardized_ingredient
    assert parsed_ingredient['quantity'] == "0.333"
    assert parsed_ingredient['unit'] == 'cups'
    assert parsed_ingredient['is_required'] == True

def test_unicode_fractions_1(regex_map):
    parse = RecipeParser("1½cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '1.5 cup of sugar'
    assert parsed_ingredient['quantity'] == "1.5"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_unicode_fractions_2(regex_map):
    parse = RecipeParser("1⅓cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '1.333 cup of sugar'
    assert parsed_ingredient['quantity'] == "1.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_unicode_fractions_3(regex_map):
    parse = RecipeParser("2  ⅓cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient["standardized_ingredient"] == '2.333 cup of sugar'
    assert parsed_ingredient['quantity'] == "2.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- Unicode fraction/range tests ----
# -------------------------------------------------------------------------------
    
def test_unicode_fraction_range_1(regex_map):
    parse = RecipeParser("1-1½cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '1.25 cup of sugar'
    assert parsed_ingredient['quantity'] == "1.25"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_unicode_fraction_range_2(regex_map):
    parse = RecipeParser("1½-2cup of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '1.75 cup of sugar'
    assert parsed_ingredient['quantity'] == "1.75"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

def test_unicode_fraction_range_3(regex_map):
    parse = RecipeParser("1½-2½cup of sugar", regex_map, debug=True)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '2 cup of sugar'
    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- X Separator tests ----
# -------------------------------------------------------------------------------
def test_x_separator_1(regex_map):
    parse = RecipeParser("1x 2 tablespoons of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == "2 tablespoons of sugar"

    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == 'tablespoons'
    assert parsed_ingredient['is_required'] == True

def test_x_separator_2(regex_map):
    parse = RecipeParser("1x2 tablespoons of sugar", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == "2 tablespoons of sugar"

    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == 'tablespoons'
    assert parsed_ingredient['is_required'] == True

def test_x_separator_3(regex_map):
    parse = RecipeParser("3 X 4lb hamburger patties", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient["standardized_ingredient"] == '12 lb hamburger patties'

    assert parsed_ingredient['quantity'] == "12"
    assert parsed_ingredient['unit'] == 'lb'
    assert parsed_ingredient['is_required'] == True

# -------------------------------------------------------------------------------
# ---- Optional ingredient (no parenthesis) tests ----
# -------------------------------------------------------------------------------
def test_optional_ingredient_1(regex_map):
    parse = RecipeParser("1/3 cup sugar, optional", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "0.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == False
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 0

def test_optional_ingredient_2(regex_map):
    parse = RecipeParser("1/3 cup sugar, opt", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "0.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == False
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 0

# -------------------------------------------------------------------------------
# ---- Optional ingredient (with parenthesis) tests ----
# -------------------------------------------------------------------------------
def test_optional_parenthesis_1(regex_map):
    parse = RecipeParser("1/3 cup sugar (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "0.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == False
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

def test_optional_parenthesis_2(regex_map):
    parse = RecipeParser("1/3 cup sugar (opt)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "0.333"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == False
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

# -------------------------------------------------------------------------------
# ---- Parenthesis (quantity only) tests ----
# -------------------------------------------------------------------------------
def test_quantity_only_parenthesis_1(regex_map):
    parse = RecipeParser("salmon steaks (2)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == None
    assert parsed_ingredient['is_required'] == True
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

def test_quantity_only_parenthesis_2(regex_map):
    parse = RecipeParser("salmon steaks (2) (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "2"
    assert parsed_ingredient['unit'] == None
    assert parsed_ingredient['is_required'] == False
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 6

def test_quantity_only_parenthesis_3(regex_map):
    parse = RecipeParser("chicken breasts (4)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "4"
    assert parsed_ingredient['unit'] == "breasts"
    assert parsed_ingredient["standard_unit"] == "breast"
    
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert parsed_ingredient['standard_secondary_unit'] == None

    assert parsed_ingredient['is_required'] == True
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

def test_quantity_only_parenthesis_4(regex_map):
    parse = RecipeParser("3 chicken breasts (4) (optional)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "12.0"
    assert parsed_ingredient['unit'] == "breasts"
    assert parsed_ingredient["standard_unit"] == "breast"
    
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert parsed_ingredient['standard_secondary_unit'] == None

    assert parsed_ingredient['is_required'] == False
    assert len(parsed_ingredient["parenthesis_notes"]) == 6

def test_quantity_only_parenthesis_5(regex_map):
    parse = RecipeParser("3 1/2 chicken breasts (4)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "14.0"
    assert parsed_ingredient['unit'] == "breasts"
    assert parsed_ingredient["standard_unit"] == "breast"
    
    assert parsed_ingredient['secondary_quantity'] == "3.5"
    assert parsed_ingredient['secondary_unit'] == None
    assert parsed_ingredient['standard_secondary_unit'] == None

    assert parsed_ingredient['is_required'] == True
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

# -------------------------------------------------------------------------------
# ---- Parenthesis (quantity unit only) tests ----
# -------------------------------------------------------------------------------

def test_quantity_and_unit_parenthesis_1(regex_map):
    parse = RecipeParser("4 chicken wings (8 oz)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "32.0"
    assert parsed_ingredient['unit'] == "oz"
    assert parsed_ingredient["standard_unit"] == "'ounce"
    
    assert parsed_ingredient['secondary_quantity'] == "4"
    assert parsed_ingredient['secondary_unit'] == "wings"
    assert parsed_ingredient['standard_secondary_unit'] == "wing"

    assert parsed_ingredient['is_required'] == True
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

def test_quantity_and_unit_parenthesis_2(regex_map):
    parse = RecipeParser(" chicken breast (12 ounces)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "12"
    assert parsed_ingredient['unit'] == "ounces"
    assert parsed_ingredient["standard_unit"] == "ounce"

    assert parsed_ingredient['secondary_quantity'] == None  # TODO: maybe this case should get a quantity of 1, but for now it's None
    assert parsed_ingredient['secondary_unit'] == "breast"
    assert parsed_ingredient['standard_secondary_unit'] == "breast"

    assert parsed_ingredient['is_required'] == True
    assert len(parsed_ingredient["parenthesis_notes"]) == 3


def test_quantity_and_unit_parenthesis_3(regex_map):
    parse = RecipeParser("1/2 cup sugar (8 ounces)", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "8"
    assert parsed_ingredient['unit'] == "ounces"
    assert parsed_ingredient["standard_unit"] == "ounce"
    
    assert parsed_ingredient['secondary_quantity'] == "0.5"
    assert parsed_ingredient['secondary_unit'] == "cup"
    assert parsed_ingredient['standard_secondary_unit'] == "cup"

    assert parsed_ingredient['is_required'] == True
    
    assert len(parsed_ingredient["parenthesis_notes"]) == 3



# -------------------------------------------------------------------------------
# ---- Assortment of different ingredients seen in the "wild" tests ----
# -------------------------------------------------------------------------------
def test_wild_ingredients(regex_map):

    parse = RecipeParser("1 (10 ounce) package frozen chopped spinach, thawed, drained and squeezed dry", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "10.0"
    assert parsed_ingredient['unit'] == 'ounce'
    assert parsed_ingredient['is_required'] == True
    assert parsed_ingredient['secondary_quantity'] == "1"
    assert parsed_ingredient['secondary_unit'] == "package"

    parse = RecipeParser("1 (8 ounce) container plain yogurt", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "8.0"
    assert parsed_ingredient['unit'] == 'ounce'
    assert parsed_ingredient['is_required'] == True
    assert parsed_ingredient['secondary_quantity'] == "1"
    assert parsed_ingredient['secondary_unit'] == "container"
    assert len(parsed_ingredient["parenthesis_notes"]) == 3

    parse = RecipeParser("salt to taste", regex_map, debug= True)
    parse.parse()
    parsed_ingredient = parse.to_json()
    assert parsed_ingredient['quantity'] == None
    assert parsed_ingredient['unit'] == None
    assert parsed_ingredient['is_required'] == True
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert parsed_ingredient["parenthesis_notes"] == []

    parse = RecipeParser("1/2 cup freshly grated Parmesan cheese, plus more for serving", regex_map)
    parse.parse()
    parsed_ingredient = parse.to_json()

    assert parsed_ingredient['quantity'] == "0.5"
    assert parsed_ingredient['unit'] == 'cup'
    assert parsed_ingredient['is_required'] == True
    assert parsed_ingredient['secondary_quantity'] == None
    assert parsed_ingredient['secondary_unit'] == None
    assert len(parsed_ingredient["parenthesis_notes"]) == 0

################################################################################################
# CODE from 03/15/2024
# '30 g cake flour (¼ cup minus 1 tsp; weigh your flour or use the “fluff and sprinkle“ method and level it off; you can make your own Homemade Cake Flour) ¼ 1'
# parse1 = RecipeParser("30 g cake flour (¼ cup minus 1 tsp; weigh your flour or use the “fluff and sprinkle“ method and level it off; you can make your own Homemade Cake Flour) ¼ 1", regex_map)
# parse1.parse()
# parsed_obj = parse1.to_json()
# parsed_obj
# for key, val in parsed_obj.items():
#     print(f"{key}: > '{val}'")
#     print()

# parse1 = RecipeParser("1-4 cups of sugar, lightly chopped (about 8 oz) but please don't do it", regex_map)
# # parse1 = RecipeParser("8 ounces of sugar (about 3 cups)", regex_map, debug = True)
# parse1.parse()
# ingredient_object = parse1.to_json()
# ingredient_object

# for key, val in ingredient_object.items():
#     print(f"{key}: > '{val}'")
#     print()

# def best_effort_food_match2(ingredient: str) -> str:


#     ingredient = ingredient_object["standardized_ingredient"]
#     # regex_map.print_matches(ingredient)

#     paranethesis_to_remove = regex_map.SPLIT_BY_PARENTHESIS.findall(ingredient)

#     for parenthesis in paranethesis_to_remove:
#         ingredient = ingredient.replace(parenthesis, "")

#     # ingredient = '2.5 cups of sugar, lightly chopped (about 8 oz)'
#     stop_words_to_remove = regex_map.STOP_WORDS_PATTERN.findall(ingredient)

#     # remove any stop words
#     for stop_word in stop_words_to_remove:
#         ingredient = ingredient.replace(stop_word, "")


#     unit_matches        = regex_map.UNITS_PATTERN.findall(ingredient)
#     quantity_matches    = regex_map.ALL_NUMBERS.findall(ingredient)
#     parenthesis_matches = regex_map.SPLIT_BY_PARENTHESIS.findall(ingredient)
#     prep_words_matches  = regex_map.PREP_WORDS_PATTERN.findall(ingredient)
#     ly_words_matches    = regex_map.WORDS_ENDING_IN_LY.findall(ingredient)

#     # # Function to remove matches from the ingredient string
#     # def remove_matches(ingredient, matches):
#     #     for match in matches:
#     #         ingredient = re.sub(re.escape(match), '', ingredient)
#     #     return ingredient

#     # # Remove matches from the standard_ingredient string
#     # standard_ingredient = remove_matches(standard_ingredient, parenthesis_matches)
#     # standard_ingredient = remove_matches(standard_ingredient, unit_matches)
#     # standard_ingredient = remove_matches(standard_ingredient, quantity_matches)

#     # make a single list of the strings to remove (IMPORATNT that parenthesis content is removed first)
#     strings_to_remove = parenthesis_matches + unit_matches + quantity_matches + prep_words_matches + ly_words_matches

#     # Remove matches using regular expression substitution
#     for match in strings_to_remove:
#         print(f"match: {match}")
#         print(f"ingredient: {ingredient}")
#         ingredient = re.sub(re.escape(match), '', ingredient)
#         # ingredient = re.sub(match, '', ingredient)
#         print()
    
#     # remove any special characters
#     standard_ingredient = re.sub(r'[^\w\s]', '', standard_ingredient)

#     # remove any extra whitespace
#     standard_ingredient = re.sub(r'\s+', ' ', standard_ingredient).strip()
#     print(f"unit_matches: {unit_matches}")
#     print(f"quantity_matches: {quantity_matches}")
#     print(f"parenthesis_matches: {parenthesis_matches}")

#     standard_ingredient = '2.5 cups of sugar, lightly chopped (about 8 oz) (optional) (8 ounces), or 2 cans sugar'

#     unit_matches = regex_map.UNITS_PATTERN.findall(standard_ingredient)
#     quantity_matches = regex_map.ALL_NUMBERS.findall(standard_ingredient)
#     parenthesis_matches = regex_map.SPLIT_BY_PARENTHESIS.findall(standard_ingredient)
#     prep_words_matches = regex_map.PREP_WORDS_PATTERN.findall(standard_ingredient)
#     ly_words_matches = regex_map.WORDS_ENDING_IN_LY.findall(standard_ingredient)

#     # make a single list of the strings to remove (IMPORATNT that parenthesis content is removed first)
#     strings_to_remove = parenthesis_matches + unit_matches + quantity_matches + prep_words_matches + ly_words_matches

#     # Remove matches using regular expression substitution
#     for match in strings_to_remove:
#         print(f"match: {match}")
#         print(f"standard_ingredient: {standard_ingredient}")
#         standard_ingredient = re.sub(re.escape(match), '', standard_ingredient)
#         print()
    
#     # remove any special characters
#     standard_ingredient = re.sub(r'[^\w\s]', '', standard_ingredient)

#     # remove any extra whitespace
#     standard_ingredient = re.sub(r'\s+', ' ', standard_ingredient).strip()

    
#     # strings_to_remove = [parenthesis_matches, prep_words_matches, ly_words_matches, unit_matches, quantity_matches]
#     # strings_to_remove = [i for sublist in strings_to_remove for i in (sublist if isinstance(sublist, (list, tuple)) else [sublist])]

#     for match in strings_to_remove:
#         standard_ingredient = standard_ingredient.replace(match, "")
    
#     # remove any special characters
#     standard_ingredient = re.sub(r'[^\w\s]', '', standard_ingredient)

#     # remove any extra whitespace
#     standard_ingredient = re.sub(r'\s+', ' ', standard_ingredient).strip()
    
#     # for matches in 

#         reduce_ingredient(standard_ingredient, strings_to_remove)
#     print(f"strings_to_remove: {strings_to_remove}")



# strings_to_remove = [unit, quantity, secondary_unit, secondary_quantity, stashed_quantity, stashed_unit, parenthesis_content]
# strings_to_remove = [i for sublist in strings_to_remove for i in (sublist if isinstance(sublist, (list, tuple)) else [sublist])]

# reduced_ingredient = reduce_ingredient(standard_ingredient, strings_to_remove)

# def normalize_whitespace(string: str) -> str:
#     """Strip leading/trailing whitespace and normalize internal whitespace to a single space.
#     Args:
#         string: The string to normalize.
#     Example:
#         normalize_whitespace("  a  b   c  ")  # "a b c"
#         normalize_whitespace("a   bc")  # "a bc"
#     """
#     return " ".join([i.strip() for i in string.split()])

# def best_effort_food_match(ingredient_object):

#     unit = ingredient_object["unit"]
#     quantity = ingredient_object["quantity"]
#     secondary_unit = ingredient_object["secondary_unit"]
#     secondary_quantity = ingredient_object["secondary_quantity"]
#     stashed_quantity = ingredient_object["stashed_quantity"]
#     stashed_unit = ingredient_object["stashed_unit"]
#     parenthesis_content = ingredient_object["parenthesis_content"]

#     standard_ingredient = ingredient_object["standardized_ingredient"]

#     strings_to_remove = [unit, quantity, secondary_unit, secondary_quantity, stashed_quantity, stashed_unit, parenthesis_content]
#     strings_to_remove = [i for sublist in strings_to_remove for i in (sublist if isinstance(sublist, (list, tuple)) else [sublist])]

#     # try and reduce the ingredient down to  a single food word if possible
#     reduced_ingredient = reduce_ingredient(standard_ingredient, strings_to_remove)

#     split_reduced_ingredient = reduced_ingredient.split() # split the reduced ingredient into words

#     is_single_food_word = len(split_reduced_ingredient) == 1

#     if is_single_food_word:
#         return normalize_whitespace(reduce_ingredient)
    






# def reduce_ingredient(ingredient, strings_to_remove):

#     ingredient = " ".join([i.strip() for i in ingredient.split()])
#     # strip_ingredient = " ".join([i.strip() for i in ingredient.split()])
#     split_ingredient = ingredient.split()

#     # print(f"ingredient: '{ingredient}'")
#     # print(f"strip_ingredient: '{strip_ingredient}'")
#     # print(f"split_ingredient: '{split_ingredient}'")
#     # print(f"Any strings to remove in split_ingredient: '{[i for i in strings_to_remove if i in split_ingredient]}'")

#     # Base case: no more matches to remove from string, return the ingredient
#     if not strings_to_remove or not [i for i in strings_to_remove if i in split_ingredient]:
#         print(f" > Reached maximum ingredient reduction: '{ingredient}'\n===================\n")
#         return ingredient.strip()

#     reduced_ingredients = []

#     # print(f"Iterating through strings to remove....")

#     for word_to_drop in strings_to_remove:
#         # Remove the current word from the ingredient and add the result to the list
#         reduced_ingredients.append(ingredient.replace(word_to_drop, "").strip())

#     # Find the ingredient with the fewest characters remaining
#     shortest_ingredient = min(reduced_ingredients, key=len)

#     print(f"Reducing shortened ingredient: '{shortest_ingredient}'\n")

#     # Recur with the shortest ingredient and the remaining strings to remove
#     return reduce_ingredient(shortest_ingredient, strings_to_remove)


# nested_list = [["a", "b"], ["c", "d"], ["e", "f", "g"]]
# [i for sublist in nested_list for i in sublist]


# [item for sublist in strings_to_remove for item in (sublist if isinstance(sublist, list) else [sublist])]


# for key, val in parsed_obj.items():
#     print(f"{key}: {val}")
#     print()

# def _prioritize_weight_units(parsed_obj) -> dict:
#     """
#     Prioritize weight units over volume units if both are present in the parsed ingredient.
#     Sets the unit and secondary_unit member variables.
#     """

#     # # set default units
#     # unit = self.unit
#     # secondary_unit = self.secondary_unit

#     unit = parsed_obj["unit"]
#     secondary_unit = parsed_obj["secondary_unit"]

#     # # if the first unit is already a weight, just return early
#     # if unit in regex_map.constants["WEIGHT_UNITS_SET"]:
#     #     return 
    
#     # if the first unit is NOT a weight and the second unit IS a weight, then swap them
#     if unit not in regex_map.constants["WEIGHT_UNITS_SET"] and secondary_unit in regex_map.constants["WEIGHT_UNITS_SET"]:
#         # unit, secondary_unit = secondary_unit, unit
#         print(f"Swapping first quantity/units with second quantity/units")
#         # switch the units and quantities with the secondary units and quantities
#         parsed_obj["quantity"], parsed_obj["secondary_quantity"] = parsed_obj["secondary_quantity"], parsed_obj["quantity"]
#         parsed_obj["unit"], parsed_obj["secondary_unit"] = parsed_obj["secondary_unit"], parsed_obj["unit"]
#         parsed_obj["standard_unit"], parsed_obj["standard_secondary_unit"] = parsed_obj["standard_secondary_unit"], parsed_obj["standard_unit"]

#     for key, val in parsed_obj.items():
#         print(f"{key}: {val}")
#         print()
#     return

# def _add_standard_units(self) -> None:
#     """
#     Add standard units to the parsed ingredient if they are present in the
#     constants units to standard units map.
#     Sets the standard_unit and standard_secondary_unit member variables.
#     """

#     unit = self.unit
#     secondary_unit = self.secondary_unit

#     # set default standard units
#     standard_unit = None
#     standard_secondary_unit = None

#     if unit and unit in self.regex.constants["UNIT_TO_STANDARD_UNIT"]:
#         self.standard_unit = self.regex.constants["UNIT_TO_STANDARD_UNIT"][unit]
    
#     if secondary_unit and secondary_unit in self.regex.constants["UNIT_TO_STANDARD_UNIT"]:
#         self.standard_secondary_unit = self.regex.constants["UNIT_TO_STANDARD_UNIT"][secondary_unit]

#     return 
# ################################################################################################
# #### FIxed merge mixed nums ##########
# ################################################################################################
# ################################################################################################

# def _make_int_or_float_str(number_str: str) -> str:

#     number = float(number_str.strip())  # Convert string to float
#     if number == int(number):  # Check if float is equal to its integer value
#         return str(int(number))  # Return integer value if it's a whole number
#     else:
#         return str(number)  # Return float if it's a decimal
    
# def _merge_spaced_numbers(spaced_numbers: str) -> str:
#     """ Add or multiply the numbers in a string separated by a space.
#     If the second number is less than 1, then add the two numbers together, otherwise multiply them together.
#     This was the most generic form of dealing with numbers seperated by spaces that i could come up with
#     (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means to multiply the numbers 2 8 oz means 16 oz)
#     Args:
#         spaced_numbers (str): A string of numbers separated by a space.
#     Returns:
#         str: string containing the sum OR the product of the numbers in the string. 
#     Examples:
#         >>> _merge_spaced_numbers('2 0.5')
#         '2.5'
#         >>> _merge_spaced_numbers('2 8')
#         '16'
#     """

#     # spaced_numbers = '0.5'

#     # Get the numbers from the spaced seperated string
#     split_numbers = re.findall(regex_map.SPLIT_SPACED_NUMS, spaced_numbers)

#     # If the second number is less than 1, then add the two numbers together, otherwise multiply them together
#     # This was the most generic form of dealing with numbers seperated by spaces 
#     # (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means to multiply the numbers 2 8 oz means 16 oz)
#     try:
#         merged_totals = [_make_int_or_float_str(str(float(first) + float(second)) if float(second) < 1 else str(float(first) * float(second))) for first, second in split_numbers]
#     except:
#         warnings.warn(f"error while merging {split_numbers}...")
#         merged_totals = [""]
#     # # READABLE VERSION of above list comprehension: 
#     # This is the above list comprehensions split out into 2 list comprehensions for readability
#     # merged_totals = [float(first) + float(second) if float(second) < 1 else float(first) * float(second) for first, second in split_numbers]

#     # return merged_totals
#     return merged_totals[0] if merged_totals else ""

# def _which_merge_on_spaced_numbers(spaced_numbers: str) -> str:
#     """ Inform whether to add or multiply the numbers in a string separated by a space.
#     Args:
#         spaced_numbers (str): A string of numbers separated by a space.
#     Returns:
#         str: string indicating whether to add or multiply the numbers in the string.
#     """

#     split_numbers = re.findall(regex_map.SPLIT_SPACED_NUMS, spaced_numbers)
#     # split_numbers = [("2", "1")]

#     # If the second number is less than 1, then note the numbers should be "added", otherwise they should be "multiplied"
#     # This was the most generic form of dealing with numbers seperated by spaces 
#     # (i.e. 2 1/2 cups means 2.5 cups but in other contexts a number followed by a non fraction means
#     #  to multiply the numbers 2 8 oz means 16 oz)
#     try:
#         add_or_multiply = ["add" if float(second) < 1 else "multiply" for first, second in split_numbers]
#     except:
#         warnings.warn(f"error while deciding whether to note '{split_numbers}' as numbers to 'add' or 'multiply'...")
#         add_or_multiply = [""]

#     return add_or_multiply[0] if add_or_multiply else ""

# def _merge_multi_nums2(self) -> None:
#     """
#     Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient (v2).
#     Assumes that numeric values in string have been padded with a space between numbers and non numeric characters and
#     that any fractions have been converted to their decimal equivalents.
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         str: The parsed ingredient string with the numbers separated by a space merged into a single number (either added or multiplied).
    
#     >>> _merge_multi_nums('2 0.5 cups of sugar')
#     '2.5 cups of sugar'
#     >>> _merge_multi_nums('1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces')
#     '1.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'
#     """

#     # ingredient = '2 0.5 cups of sugar'
#     # ingredient = 'a lemon'
#     # ingredient = "1.5 lb of sugar"
#     # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

#     # # original ingred: "1½-2½cup of sugar"
#     # ingredient = '1 0.5 - 2 0.5 cup of sugar'
#     # ingredient = '1 0.5 - 2 0.5 of sugar'
#     # ingredient = '1 1/2 - 2 1/2 cup of sugar'

#     # go the spaced numbers matches and get each spaced seperated numbers match AND 
#     # try and get the units that follow them so we can correctly match each spaced number with its corresponding unit
#     spaced_nums = []
#     units = []

#     # Create iterable of the matched spaced numbers to insert updated values into the original string
#     spaced_matches = re.finditer(self.regex.SPACE_SEP_NUMBERS, self.standard_ingredient)
#     # spaced_matches = re.finditer(regex_map.SPACE_SEP_NUMBERS, ingredient)

#     # initialize offset and replacement index values for updating the ingredient string, 
#     # these will be used to keep track of the position of the match in the string
#     offset = 0
#     replacement_index = 0

#     # Update the ingredient string with the merged values
#     for match in spaced_matches:
#         # print(f"Ingredient string: {ingredient}")

#         # Get the start and end positions of the match
#         start, end = match.start(), match.end()

#         # search for the first unit that comes after the spaced numbers
#         unit_after_match = re.search(self.regex.UNITS_PATTERN,  self.standard_ingredient[end:])
#         # unit_after_match = re.search(regex_map.UNITS_PATTERN, ingredient[end:])
        
#         if unit_after_match:
#             print(f"unit after match: > '{unit_after_match.group()}'")
#             units.append(unit_after_match.group())

#         # add the spaced number to the list
#         spaced_nums.append(match.group())

#         # print(f"Match: {match.group()} at positions {start}-{end}")
#         merged_quantity = _merge_spaced_numbers(match.group())
#         merge_operation = _which_merge_on_spaced_numbers(match.group())

#         print(f"merged_quantity: {merged_quantity}")
#         print(f"merge_operation: {merge_operation}") 

#         # Calculate the start and end positions in the modified string
#         modified_start = start + offset
#         modified_end = end + offset

#         # print(f" -> Modified match positions: {modified_start}-{modified_end}")
#         # print(f"Replacing {match.group()} with '{merged_quantity}'...")
        
#         # Construct the modified string with the replacement applied
#         self.standard_ingredient = self.standard_ingredient[:modified_start] + str(merged_quantity) + self.standard_ingredient[modified_end:]
#         # ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]


#         # Update the offset for subsequent replacements
#         offset += len(merged_quantity) - (end - start)
#         replacement_index += 1

# def _merge_multi_nums() -> None:
#     """
#     Replace unicode and standard fractions with their decimal equivalents in the parsed ingredient.
#     Assumes that numeric values in string have been padded with a space between numbers and non numeric characters and
#     that any fractions have been converted to their decimal equivalents.
#     Args:
#         ingredient (str): The ingredient string to parse.
#     Returns:
#         str: The parsed ingredient string with the numbers separated by a space merged into a single number (either added or multiplied).
    
#     >>> _merge_multi_nums('2 0.5 cups of sugar')
#     '2.5 cups of sugar'
#     >>> _merge_multi_nums('1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces')
#     '1.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'
#     """

#     ingredient = '2 0.5 cups of sugar'
#     # ingredient = 'a lemon'
#     # ingredient = "1.5 lb of sugar"
#     # ingredient = '1 0.5 pounds skinless, boneless chicken breasts, cut into 0.5 inch pieces'

#     # # original ingred: "1½-2½cup of sugar"
#     ingredient = '1 0.5 - 2 0.5 cup of sugar'
#     # ingredient = '1 0.5 - 2 0.5 of sugar'
#     # ingredient = '1 1/2 - 2 1/2 cup of sugar'

#     ################################
#     # #### OLD METHOD using findall() to get the units and spaced numbers lists ####
#     ################################

#     # # # get the units from the ingredient string
#     # units = re.findall(regex_map.UNITS_PATTERN, ingredient)
#     # # units = re.findall(regex_map.UNITS_PATTERN, ingredient)

#     # # spaced_nums = re.findall(regex.SPACE_SEP_NUMBERS, '2 0.5 cups of sugar 3 0.5 lbs of carrots')
#     # spaced_nums = re.findall(regex_map.SPACE_SEP_NUMBERS, ingredient)
    
#     #################################
#     #### NEW METHOD using finditer() to get the units and spaced numbers lists  ####
#     # Helps when there is a range of numbers in the ingredient string and the units are not always directly after the numbers
#     # (i.e. 1 1/2 - 2 1/2 cups of sugar), "cups" is not directly after the first number
#     #################################

#     # iterator for matches of spaced numbers
#     spaced_iter = re.finditer(regex_map.SPACE_SEP_NUMBERS, ingredient)

#     # go the spaced numbers matches and get each spaced seperated numbers match AND 
#     # try and get the units that follow them so we can correctly match each spaced number with its corresponding unit
#     spaced_nums = []
#     units = []
#     for spaced in spaced_iter:
#         print(f"spaced: '{spaced.group()}'") 
#         print(f"spaced: '{spaced.start()}-{spaced.end()}'") 
#         print(f"rest of string: '{ingredient[spaced.end():]}'")
#         # print(f"spaced: '{spaced.group()}'") if self.debug else None
#         # print(f"spaced: '{spaced.start()}-{spaced.end()}'") if self.debug else None
#         # print(f"rest of string: '{ingredient[spaced.end():]}'") if self.debug else None

#         # search for the first unit that comes after the spaced numbers
#         unit_after_match = re.search(regex_map.UNITS_PATTERN, ingredient[spaced.end():])
        
#         if unit_after_match:
#             print(f"unit after match: > '{unit_after_match.group()}'")
#             units.append(unit_after_match.group())

#         spaced_nums.append(spaced.group())
#         print()

#     # Merge the numbers from the space seperated string of numbers
#     merged_values = [_merge_spaced_numbers(num_pair) for num_pair in spaced_nums]

#     # Was the operation to merge the numbers an addition or a multiplication?
#     merge_type = [_which_merge_on_spaced_numbers(num_pair) for num_pair in spaced_nums]


#     # TODO: if the there are multiple spaced numbers that need merging AND if there are less units the merged_values, 
#     # TODO: then assume all the spaced values have the same unit. Expand the units list to match the length of the merged_values list in this case

#     # expand the units list to match the length of the merged_values list
#     if len(units) < len(merged_values):
#         units = [units[0]] * len(merged_values)

#     regex_map.print_matches(ingredient)

#     # ---- METHOD 1 ----

#     # METHOD 1: Create a list of dictionaries with the units and their converted quantities
#     merged_unit_quantities = [{"units":u, "quantities": q, "merge_operation": m} for u, q, m in zip(units, merged_values, merge_type)]
#     # merged_unit_quantities = [{"units":u, "quantities": q} for u, q in zip(units, merged_values)] # not including merge_type

#     # map the spaced numbers to the units and their converted quantities
#     # Key is the spaced numbers, value is a dictionary with the units, merged quantities, and the merge operation
#     conversions_map = dict(zip(spaced_nums, merged_unit_quantities))

#     # ---- METHOD 2 ----
#     # METHOD 2: Create a LIST of dictionaries with the original string, the units, their converted quantities, and the merge method (keep track of iteration index and index the matches by position)
#     conversions_list = [{"input_numbers": n, "units":u, "quantities": q, "merge_operation": m} for n, u, q, m in zip(spaced_nums, units, merged_values, merge_type)]

#     # print(f"Number of matched spaced numbers: {len(spaced_nums)}")
#     # print(f"Number of converted matches (map): {len(conversions_map)}")
#     # print(f"Number of converted matches (list): {len(conversions_list)}")

#     if len(spaced_nums) != len(conversions_map):
#         warnings.warn(f"Number of spaced numbers and number of converted matches (MAP) are not equal...")

#     if len(spaced_nums) != len(conversions_list):    
#         warnings.warn(f"Number of spaced numbers and number of converted matches (LIST) are not equal...")
    
#     # Create iterable of the matched spaced numbers to insert updated values into the original string
#     spaced_matches = re.finditer(regex_map.SPACE_SEP_NUMBERS, ingredient)

#     # initialize offset and replacement index values for updating the ingredient string, 
#     # these will be used to keep track of the position of the match in the string
#     offset = 0
#     replacement_index = 0

#     # Update the ingredient string with the merged values
#     for match in spaced_matches:
#         # print(f"Ingredient string: {ingredient}")

#         # Get the start and end positions of the match
#         start, end = match.start(), match.end()

#         # print(f"Match: {match.group()} at positions {start}-{end}")

#         # Get key value pair in the conversions_map that corresponds to the current match and the new quantity values to sub in
#         conversions = conversions_map[match.group()]
#         # conversions = conversions_list[replacement_index]

#         # print(f"Conversions: {conversions}")

#         # starting_quantity = conversions["input_numbers"]
#         merged_quantity = conversions["quantities"]
#         merge_operation = conversions["merge_operation"] # add or multiply

#         # print(f"Starting quantity {starting_quantity}")
#         # print(f"Merged Quantity: {merged_quantity}") if self.debug else None

#         # Calculate the start and end positions in the modified string
#         modified_start = start + offset
#         modified_end = end + offset

#         # print(f" -> Modified match positions: {modified_start}-{modified_end}")
#         # print(f"Replacing {match.group()} with '{merged_quantity}'...")
        
#         # Construct the modified string with the replacement applied
#         ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]
#         # ingredient = ingredient[:modified_start] + str(merged_quantity) + ingredient[modified_end:]

#         # Update the offset for subsequent replacements
#         offset += len(merged_quantity) - (end - start)
#         replacement_index += 1
#         # print(f" --> Output ingredient: \n > '{ingredient}'")