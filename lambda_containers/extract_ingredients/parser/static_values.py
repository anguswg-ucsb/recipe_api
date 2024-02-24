import re

# Constants
NUMBER_WORDS = {
    'one': 1, 
    'two': 2,
    'three': 3, 
    'four': 4, 
    'five': 5,
    'six': 6, 
    'seven': 7, 
    'eight': 8, 
    'nine': 9, 
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
    'hundred': 100
}

NUMBER_WORDS_REGEX_MAP = {}
for word, value in NUMBER_WORDS.items():
    # print(f"Word: {word} \nValue: {value}")
    NUMBER_WORDS_REGEX_MAP[word] = [str(value), re.compile(r'\b' + word + r'\b', re.IGNORECASE)]
    # print(f"\n")

NUMBER_FRACTIONS = {
    # singular versions
    'half': round(1/2, 3),
    'quarter': round(1/4, 3),
    'third': round(1/3, 3),
    'fourth': round(1/4, 3),
    'fifth': round(1/5, 3),
    'sixth': round(1/6, 3),
    'seventh': round(1/7, 3),
    'eighth': round(1/8, 3),
    'ninth': round(1/9, 3),
    'tenth': round(1/10, 3),
    'eleventh': round(1/11, 3),
    'twelfth': round(1/12, 3),
    # plural versions
    'halves': round(1/2, 3),
    'quarters': round(1/4, 3),
    'thirds': round(1/3, 3),
    'fourths': round(1/4, 3),
    'fifths': round(1/5, 3),
    'sixths': round(1/6, 3),
    'sevenths': round(1/7, 3),
    'eighths': round(1/8, 3),
    'ninths': round(1/9, 3),
    'tenths': round(1/10, 3),
    'elevenths': round(1/11, 3),
    'twelfths': round(1/12, 3)
}

# NUMBER_FRACTIONS = {
#     # singular versions
#     'half': [round(1/2, 3), '1/2'],
#     'quarter': [round(1/4, 3), '1/4'],
#     'third': [round(1/3, 3), '1/3'],
#     'fourth': [round(1/4, 3), '1/4'],
#     'fifth': [round(1/5, 3), '1/5'],
#     'sixth': [round(1/6, 3), '1/6'],
#     'seventh': [round(1/7, 3), '1/7'],
#     'eighth': [round(1/8, 3), '1/8'],
#     'ninth': [round(1/9, 3), '1/9'],
#     'tenth': [round(1/10, 3), '1/10'],
#     'eleventh': [round(1/11, 3), '1/11'],
#     'twelfth': [round(1/12, 3), '1/12'],
#     # plural versions
#     'halves': [round(1/2, 3), '1/2'],
#     'quarters': [round(1/4, 3), '1/4'],
#     'thirds': [round(1/3, 3), '1/3'],
#     'fourths': [round(1/4, 3), '1/4'],
#     'fifths': [round(1/5, 3), '1/5'],
#     'sixths': [round(1/6, 3), '1/6'],
#     'sevenths': [round(1/7, 3), '1/7'],
#     'eighths': [round(1/8, 3), '1/8'],
#     'ninths': [round(1/9, 3), '1/9'],
#     'tenths': [round(1/10, 3), '1/10'],
#     'elevenths': [round(1/11, 3), '1/11'],
#     'twelfths': [round(1/12, 3), '1/12']
# }

# UNICODE_FRACTIONS = {
#     '¼': 1/4,
#     '½': 1/2,
#     '¾': 3/4,
#     '⅐': 1/7,
#     '⅑': 1/9,
#     '⅒': 1/10,
#     '⅓': 1/3,
#     '⅔': 2/3,
#     '⅕': 1/5,
#     '⅖': 2/5,
#     '⅗': 3/5,
#     '⅘': 4/5,
#     '⅙': 1/6,
#     '⅚': 5/6,
#     '⅛': 1/8,
#     '⅜': 3/8,
#     '⅝': 5/8,
#     '⅞': 7/8,
#     '⅟': 1
#     # "⁄": "/"
# }

# Credit to: @strangetom 
# https://github.com/strangetom/ingredient-parser/blob/master/ingredient_parser/_constants.py
UNICODE_FRACTIONS = {
    "\u215b": " 1/8",
    "\u215c": " 3/8",
    "\u215d": " 5/8",
    "\u215e": " 7/8",
    "\u2159": " 1/6",
    "\u215a": " 5/6",
    "\u2155": " 1/5",
    "\u2156": " 2/5",
    "\u2157": " 3/5",
    "\u2158": " 4/5",
    "\xbc": " 1/4",
    "\xbe": " 3/4",
    "\u2153": " 1/3",
    "\u2154": " 2/3",
    "\xbd": " 1/2",
    "\u2159": "1/8",
    "\u215a": "1/9",
    "\u215b": "1/10",
    "\u215c": "3/8",
    "\u215d": "3/9",
    "\u215e": "3/10",
    "\u215f": "5/8",
    "\u2160": "5/9",
    "\u2161": "5/10",
    "\u2162": "7/8",
    "\u2163": "7/9",
    "\u2164": "7/10",
    # Negative fractions
    "-\u2159": "-1/8",
    "-\u215a": "-1/9",
    "-\u215b": "-1/10",
    "-\u215c": "-3/8",
    "-\u215d": "-3/9",
    "-\u215e": "-3/10",
    "-\u215f": "-5/8",
    "-\u2160": "-5/9",
    "-\u2161": "-5/10",
    "-\u2162": "-7/8",
    "-\u2163": "-7/9",
    "-\u2164": "-7/10",
    "-\u215b": "-1/8",
    "-\u215c": "-3/8",
    "-\u215d": "-5/8",
    "-\u215e": "-7/8",
    "-\u2159": "-1/6",
    "-\u215a": "-5/6",
    "-\u2155": "-1/5",
    "-\u2156": "-2/5",
    "-\u2157": "-3/5",
    "-\u2158": "-4/5",
    "-\xbc": "-1/4",
    "-\xbe": "-3/4",
    "-\u2153": "-1/3",
    "-\u2154": "-2/3",
    "-\xbd": "-1/2"
}

UNITS = {
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps'],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps'],
    'cup': ['cup', 'cups'],
    'ounce': ['ounce', 'ounces', 'oz', 'ozs'],
    'pound': ['pound', 'pounds', 'lbs'],
    'gram': ['gram', 'grams', 'g'],
    'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'],
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'liter': ['liter', 'liters', 'l'],
    'milligram': ['milligram', 'milligrams', 'mg', 'mgs'],
    'pinch': ['pinch', 'pinches'],
    'dash': ['dash', 'dashes'],
    'drop': ['drop', 'drops'],
    'sprig': ['sprig', 'sprigs'],
    'slice': ['slice', 'slices'],
    'piece': ['piece', 'pieces'],
    'package': ['package', 'packages'],
    'tablespoonful': ['tablespoonful', 'tablespoonfuls'],
    'teaspoonful': ['teaspoonful', 'teaspoonfuls'],
    'handful': ['handful', 'handfuls'],
    'bunch': ['bunch', 'bunches'],
    'bottle': ['bottle', 'bottles'],
    'can': ['can', 'cans'],
    'jar': ['jar', 'jars'],
    'package': ['package', 'packages'],
    'bag': ['bag', 'bags'],
    'box': ['box', 'boxes'],
    'slice': ['slice', 'slices'],
    'sprig': ['sprig', 'sprigs'],
    'stalk': ['stalk', 'stalks'],
    'gallon': ['gallon', 'gallons'],
    'quart': ['quart', 'quarts'],
    'pint': ['pint', 'pints'],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs'],
    'millimeter': ['millimeter', 'millimeters', 'mm', 'mms'],
    'centimeter': ['centimeter', 'centimeters', 'cm', 'cms'],
    'inch': ['inch', 'inches'],
    'foot': ['foot', 'feet'],
    'meter': ['meter', 'meters'],
    'scoop': ['scoop', 'scoops'],
    'packet': ['packet', 'packets'],
    'tube': ['tube', 'tubes'],
    'stick': ['stick', 'sticks'],
    'fillet': ['fillet', 'fillets'],
    'head': ['head', 'heads'],
    'bulb': ['bulb', 'bulbs'],
    'ear': ['ear', 'ears'],
    'rim': ['rim', 'rims'],
    'sheet': ['sheet', 'sheets'],
    'portion': ['portion', 'portions'],
    'envelope': ['envelope', 'envelopes'],
    'cube': ['cube', 'cubes'],
    'breast': ['breast', 'breasts'],
    'thigh': ['thigh', 'thighs'],
    'leg': ['leg', 'legs'],
    'drumstick': ['drumstick', 'drumsticks'],
    'wing': ['wing', 'wings'],
    'patty': ['patty', 'patties'],
    'link': ['link', 'links'],
    'strip': ['strip', 'strips'],
    'bun': ['bun', 'buns'],
    'loaf': ['loaf', 'loaves'],
    'roll': ['roll', 'rolls'],
    'glass': ['glass', 'glasses'],
    'bowl': ['bowl', 'bowls'],
    'plate': ['plate', 'plates'],
    'cupful': ['cupful', 'cupfuls'],
    'bottleful': ['bottleful', 'bottlefuls'],
    'canful': ['canful', 'canfuls'],
    'jarful': ['jarful', 'jarfuls'],
    'packageful': ['packageful', 'packagefuls'],
    'bagful': ['bagful', 'bagfuls'],
    'boxful': ['boxful', 'boxfuls'],
    'head': ['head', 'heads'],
    'stalk': ['stalk', 'stalks'],
    'wheel': ['wheel', 'wheels']
}
# NUMBER_FRACTIONS_PATTERN = re.compile( r'\b(?:' + '|'.join(re.escape(word) for word in NUMBER_FRACTIONS.keys()) + r')\b', re.IGNORECASE)

# # create a regular expression pattern to match the units in the string
# UNITS_PATTERN = re.compile(r'\b(?:' + '|'.join('|'.join(variants) for variants in UNITS.values()) + r')\b', re.IGNORECASE)

# Generate the regular expression pattern for units in the string
any_unit_pattern = '|'.join('|'.join(variants) for variants in UNITS.values())

# create a regular expression pattern to match the units in the string
UNITS_PATTERN = re.compile(r'\b(?:' + any_unit_pattern + r')\b', re.IGNORECASE)
# UNITS_PATTERN = re.compile(r'\b(?:' + '|'.join('|'.join(variants) for variants in UNITS.values()) + r')\b', re.IGNORECASE)

# # Construct the regular expression pattern that matches the digit followed by 0+ spaces and
# #  then a unit in UNITS dictionary
# SINGLE_NUMBER_THEN_UNIT_PATTERN = re.compile(r'\b\d+\s*(?:' + any_unit_pattern + r')\b')
# # SINGLE_NUMBER_THEN_UNIT_PATTERN = r'\b\d+\s*(?:' + any_unit_pattern + r')\b'

# Construct the regular expression pattern that matches the number (including fractions and decimals)
# followed by 0+ spaces and then a unit in UNITS dictionary
ANY_NUMBER_THEN_UNIT_PATTERN = re.compile(r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*(?:' + any_unit_pattern + r')\b')
# ANY_NUMBER_THEN_UNIT_PATTERN = r'\b(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\s*(?:' + any_unit_pattern + r')\b'

# Construct the regular expression pattern that matches the unit followed by 0+ spaces
# and then a number (including fractions and decimals)
UNIT_THEN_ANY_NUMBER_PATTERN = re.compile(r'\b(?:' + any_unit_pattern + r')\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b')
# UNIT_THEN_ANY_NUMBER_PATTERN = r'\b(?:' + any_unit_pattern + r')\s*(?:\d*\.\d+|\d+\s*/\s*\d+|\d+)\b'

# #### Test ANY_NUMBER_THEN_UNIT_PATTERN #### 
# # Test strings
# test_string3 = "3.5 tsp of salt, 1/4 cup of sugar"
# test_string4 = "2 tablespoons of olive oil, 3/4 teaspoon of black pepper"
# test_string5 = "500 grams of flour, 1.25 liters of water"
# test_string6 = "1.75 lbs of beef, 2 1/2 cups of milk"
# test_string7 = "3 / 8 ounce of yeast, 0.75 teaspoon of salt"

# # Find all matches in the test strings
# matches3 = re.findall(ANY_NUMBER_THEN_UNIT_PATTERN, test_string3)
# print(matches3)  # Output: ['3.5 tsp', '1/4 cup']

# matches4 = re.findall(ANY_NUMBER_THEN_UNIT_PATTERN, test_string4)
# print(matches4)  # Output: ['2 tablespoons', '3/4 teaspoon']

# matches5 = re.findall(ANY_NUMBER_THEN_UNIT_PATTERN, test_string5)
# print(matches5)  # Output: ['500 grams', '1.25 liters']

# matches6 = re.findall(ANY_NUMBER_THEN_UNIT_PATTERN, test_string6)
# print(matches6)  # Output: ['1.75 lbs', '2 1/2 cups']

# matches7 = re.findall(ANY_NUMBER_THEN_UNIT_PATTERN, test_string7)
# print(matches7)  # Output: ['3/8 ounce', '0.75 teaspoon']

# ### Test UNIT_THEN_ANY_NUMBER_PATTERN ###
# # Test strings
# test_string8 = "tsp3 of salt, cup 1/4 of sugar"
# test_string9 = "tablespoons 2 of olive oil, teaspoon 3/4 of black pepper"
# test_string10 = "grams 500 of flour, liters 1.25 of water"
# test_string11 = "lbs 1.75 of beef, cups 2 1/2 of milk"
# test_string12 = "ounce 3 / 8 of yeast, teaspoon 0.75 of salt"

# # Find all matches in the test strings
# matches8 = re.findall(UNIT_THEN_ANY_NUMBER_PATTERN, test_string8)
# print(matches8)  # Output: ['tsp3', 'cup 1/4']

# matches9 = re.findall(UNIT_THEN_ANY_NUMBER_PATTERN, test_string9)
# print(matches9)  # Output: ['tablespoons 2', 'teaspoon 3/4']

# matches10 = re.findall(UNIT_THEN_ANY_NUMBER_PATTERN, test_string10)
# print(matches10)  # Output: ['grams 500', 'liters 1.25']

# matches11 = re.findall(UNIT_THEN_ANY_NUMBER_PATTERN, test_string11)
# print(matches11)  # Output: ['lbs 1.75', 'cups 2 1/2']

# matches12 = re.findall(UNIT_THEN_ANY_NUMBER_PATTERN, test_string12)
# print(matches12)  # Output: ['ounce 3 / 8', 'teaspoon 0.75']
