# Numbers represented as words
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

# Fractions represented as words
FRACTION_WORDS = {
    # singular versions
    "half": "1/2",
    "quarter": "1/4",
    "third": "1/3",
    "fourth": "1/4",
    "fifth": "1/5",
    "sixth": "1/6",
    "seventh": "1/7",
    "eighth": "1/8",
    "ninth": "1/9",
    "tenth": "1/10",
    "eleventh": "1/11",
    "twelfth": "1/12",

    # plural versions
    "halves": "1/2",
    "quarters": "1/4",
    "thirds": "1/3",
    "fourths": "1/4",
    "fifths": "1/5",
    "sixths": "1/6",
    "sevenths": "1/7",
    "eighths": "1/8",
    "ninths": "1/9",
    "tenths": "1/10",
    "elevenths": "1/11",
    "twelfths": "1/12",

    # amount with fraction words
    "one half": "1/2",
    "1 half": "1/2",
    "two halves": "1",
    "one quarter": "1/4",
    "1 quarter": "1/4",
    "two quarters": "1/2",
    "three quarters": "3/4",
    "3 quarters": "3/4",
    "one third": "1/3",
    "1 third": "1/3",
    "two thirds": "2/3",
    "2 thirds": "2/3",
    "one fourth": "1/4",
    "1 fourth": "1/4",
    "two fourths": "1/2",
    "three fourths": "3/4",
    "3 fourths": "3/4",
    "one fifth": "1/5",
    "1 fifth": "1/5",
    "two fifths": "2/5",
    "2 fifths": "2/5",
    "three fifths": "3/5",
    "3 fifths": "3/5",
    "four fifths": "4/5",
    "4 fifths": "4/5",
    "one sixth": "1/6",
    "1 sixth": "1/6",
    "two sixths": "1/3",
    "three sixths": "1/2",
    "four sixths": "2/3",
    "five sixths": "5/6",
    "5 sixths": "5/6",
    "one seventh": "1/7",
    "two sevenths": "2/7",
    "one eighth": "1/8",
    "1 eighth": "1/8",
    "two eighths": "1/4",
    "2 eighths": "1/4",
    "three eighths": "3/8",
    "3 eighths": "3/8",
    "four eighths": "1/2",
    "five eighths": "5/8",
    "six eighths": "3/4",
    "seven eighths": "7/8",
    "one ninth": "1/9",
    "two ninths": "2/9",
    "one tenth": "1/10",
    "two tenths": "1/5",
    "one eleventh": "1/11",
    "two elevenths": "2/11",
    "one twelfth": "1/12",
    "two twelfths": "1/6",
    "eleven twelfths": "11/12"
}

UNICODE_FRACTIONS = {
    '¼': "1/4",
    '½': "1/2",
    '¾': "3/4",
    '⅐': "1/7",
    '⅑': "1/9",
    '⅒': "1/10",
    '⅓': "1/3",
    '⅔': "2/3",
    '⅕': "1/5",
    '⅖': "2/5",
    '⅗': "3/5",
    '⅘': "4/5",
    '⅙': "1/6",
    '⅚': "5/6",
    '⅛': "1/8",
    '⅜': "3/8",
    '⅝': "5/8",
    '⅞': "7/8",
    '⅟': "1",
    # "⁄": "/"
    '-¼': "-1/4",
    '-½': "-1/2",
    '-¾': "-3/4",
    '-⅐': "-1/7",
    '-⅑': "-1/9",
    '-⅒': "-1/10",
    '-⅓': "-1/3",
    '-⅔': "-2/3",
    '-⅕': "-1/5",
    '-⅖': "-2/5",
    '-⅗': "-3/5",
    '-⅘': "-4/5",
    '-⅙': "-1/6",
    '-⅚': "-5/6",
    '-⅛': "-1/8",
    '-⅜': "-3/8",
    '-⅝': "-5/8",
    '-⅞': "-7/8",
    '-⅟': "-1"
}

TEMPERATURE_UNITS = {
    "degree celsius": ["degree celsius", "degrees celsius", "°C"],
    "degree fahrenheit": ["degree fahrenheit", "degrees fahrenheit", "°F"]
}

UNITS = {
    # 'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp."],
    # 'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp.", "tbsps."],
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp"],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps"],
    'cup': ['cup', 'cups'],
    # 'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz.", "ozs."],
    # 'pound': ['pound', 'pounds', 'lbs', 'lb', 'lbs.'],
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz", "ozs"],
    'pound': ['pound', 'pounds', 'lbs', 'lb', 'lbs'],
    'gram': ['gram', 'grams', 'g'],
    'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'],
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'liter': ['liter', 'liters', 'l'],
    'milligram': ['milligram', 'milligrams', 'mg', 'mgs'],
    'pinch': ['pinch', 'pinches'],
    'dash': ['dash', 'dashes'],
    'dallop': ['dallop', 'dallops'],
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
    'gallon': ['gallon', 'gallons', "gals", "gal"],
    'pint': ['pint', 'pints', "pt", "pts"],
    'quart': ['quart', 'quarts', "qt", "qts"],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
                     "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],
    # 'pint': ['pint', 'pints', "pt", "pts", "pt.", "pts."],
    # 'quart': ['quart', 'quarts', "qt", "qts", "qt.", "qts."],
    # 'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
    #                  "fl oz.", "fl ozs.", "fluid oz", "fluid ozs", "fluid oz.", "fluid ozs."],
    'millimeter': ['millimeter', 'millimeters', 'mm', 'mms'],
    'centimeter': ['centimeter', 'centimeters', 'cm', 'cms'],
    'inch': ['inch', 'inches', 'in', 'ins'],
    'foot': ['foot', 'feet', 'ft', 'fts'],
    'meter': ['meter', 'meters', 'm', 'ms'],
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
    'can': ['can', 'cans'],
    'jarful': ['jarful', 'jarfuls'],
    'packageful': ['packageful', 'packagefuls'],
    'bagful': ['bagful', 'bagfuls'],
    'boxful': ['boxful', 'boxfuls'],
    'head': ['head', 'heads'],
    'stalk': ['stalk', 'stalks'],
    'wheel': ['wheel', 'wheels']
}

UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the volume units words
for key, pattern in UNITS.items():
    UNITS_SET.add(key)
    for val in pattern:
        UNITS_SET.add(val)

# Only the core basic imperial and metric units (Excludes the more specific units like "stalk", "fillet", "slices", etc.)
BASIC_UNITS = {
    # Imperial volume units
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp", "t"],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps"],
    'tablespoonful': ['tablespoonful', 'tablespoonfuls'],
    'teaspoonful': ['teaspoonful', 'teaspoonfuls'],
    'cup': ['cup', 'cups', "c"],
    'pint': ['pint', 'pints', "pt", "pts"],
    'quart': ['quart', 'quarts', "qt", "qts"],
    'gallon': ['gallon', 'gallons', "gals", "gal"],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
                    "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],

    # Metric volume units
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'liter': ['liter', 'liters', 'l'],

    # Imperial weight units
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz", "ozs"],
    'pound': ['pound', 'pounds', 'lbs', 'lb'],

    # Metric weight units
    'milligram': ['milligram', 'milligrams', 'mg', 'mgs'],
    'gram': ['gram', 'grams', 'g'],
    'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'],
}

BASIC_UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the basic units words
for key, pattern in BASIC_UNITS.items():
    BASIC_UNITS_SET.add(key)
    for val in pattern:
        BASIC_UNITS_SET.add(val)

VOLUME_UNITS = {
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp"],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps"],
    # 'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp.", "t", "T"],
    # 'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp.", "tbsps."],
    'cup': ['cup', 'cups', "C", "c"],
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz", "ozs"],
    # 'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz.", "ozs."],
    # 'pint': ['pint', 'pints', "pt", "pts", "pt.", "pts."],
    # 'quart': ['quart', 'quarts', "qt", "qts", "qt.", "qts."],
    # 'gallon': ['gallon', 'gallons', "gal", "gals", "gal.", "gals."],
    #  'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
    #                 "fl. oz.", "fl. ozs.", "fl oz.", "fl ozs.",
    #                   "fluid oz", "fluid ozs", "fluid oz.", "fluid ozs."],
    'pint': ['pint', 'pints', "pt", "pts"],
    'quart': ['quart', 'quarts', "qt", "qts"],
    'gallon': ['gallon', 'gallons', "gals", "gal"],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
                    "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'liter': ['liter', 'liters', 'l']
}

VOLUME_UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the volume units words
for key, pattern in VOLUME_UNITS.items():
    VOLUME_UNITS_SET.add(key)
    for val in pattern:
        VOLUME_UNITS_SET.add(val)

# terms used to describe vague quantities
CASUAL_QUANTITIES = {
    'a' : 1,
    'an': 1,
    'a couple': 2,
    'a few': 3,
    'a bit': 1,
    'a tiny bit': 1,
    'a handful': 5,
    'a pinch': 1,
    'a dash': 1,
    'a dallop': 1,
    'a drop': 1, 
    "tad": 1,
    "smidgen": 1,
    "touch": 1,
}

# specific words that are used to describe something about a unit (i.e. "packed cup", "level tablespoon")
UNIT_MODIFIERS = set([
    "round",
    "rounded",
    "level",
    "leveled",
    "heaping",
    "heaped",
    "scant",
    "even",
    "generous",
    "packed",
    "sifted",
    "unsifted",
    "light",
    "lightly",
    "lightly packed",
    "heavy",
    "heavily",
    "firmly",
    "tightly",
    "smooth",
    "small",
    "medium",
    "large",
    "extra large",
    "big", 
    "tiny",
    "modest",
    "hefty",
    "roughly"
])

PREP_WORDS = set([
    "chopped",
    "diced",
    "minced",
    "sliced",
    "slivered",
    "julienned",
    "emulsified",
    "grated",
    "crushed",
    "mashed",
    "peeled",
    "seeded",
    "cored",
    "trimmed",
    "halved",
    "quartered",
    "squeezed",
    "zested",
    "juiced",
    "cubed",
    "shredded",
    "pitted"
])

# # Fractions represented as words
# FRACTION_WORDS = {
#     # singular versions
#     'half': round(1/2, 3),
#     'quarter': round(1/4, 3),
#     'third': round(1/3, 3),
#     'fourth': round(1/4, 3),
#     'fifth': round(1/5, 3),
#     'sixth': round(1/6, 3),
#     'seventh': round(1/7, 3),
#     'eighth': round(1/8, 3),
#     'ninth': round(1/9, 3),
#     'tenth': round(1/10, 3),
#     'eleventh': round(1/11, 3),
#     'twelfth': round(1/12, 3),
#     # plural versions
#     'halves': round(1/2, 3),
#     'quarters': round(1/4, 3),
#     'thirds': round(1/3, 3),
#     'fourths': round(1/4, 3),
#     'fifths': round(1/5, 3),
#     'sixths': round(1/6, 3),
#     'sevenths': round(1/7, 3),
#     'eighths': round(1/8, 3),
#     'ninths': round(1/9, 3),
#     'tenths': round(1/10, 3),
#     'elevenths': round(1/11, 3),
#     'twelfths': round(1/12, 3)
# }

# FRACTION_WORDS = {
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