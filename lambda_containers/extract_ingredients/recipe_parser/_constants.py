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
    'bag': ['bag', 'bags'], 
    'bagful': ['bagful', 'bagfuls'], 
    'bottle': ['bottle', 'bottles'], 
    'bottleful': ['bottleful', 'bottlefuls'], 
    'bowl': ['bowl', 'bowls'], 
    'bowlful': ['bowlful', 'bowlfuls'],
    'box': ['box', 'boxes'], 
    'boxful': ['boxful', 'boxfuls'], 
    'breast': ['breast', 'breasts'], 
    'bulb': ['bulb', 'bulbs'], 
    'bun': ['bun', 'buns'], 
    'bunch': ['bunch', 'bunches'], 
    'can': ['can', 'cans'], 
    'canful': ['canful', 'canfuls'], 
    # 'centimeter': ['centimeter', 'centimeters', 'cm', 'cms'],  # TODO: address dimensions
    'container': ['container', 'containers'], 
    'cube': ['cube', 'cubes'], 
    'cup': ['cup', 'cups', "C", "c"],
    'cupful': ['cupful', 'cupfuls'], 
    'dallop': ['dallop', 'dallops'], 
    'dash': ['dash', 'dashes'], 
    'drop': ['drop', 'drops'], 
    'drumstick': ['drumstick', 'drumsticks'], 
    'ear': ['ear', 'ears'], 
    'envelope': ['envelope', 'envelopes'], 
    'filet': ['filet', 'filets'], 
    'fillet': ['fillet', 'fillets'], 
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs', 'fluid oz', 'fluid ozs', 'fluid oz', 'fluid ozs'], 
    # 'foot': ['foot', 'feet', 'ft', 'fts'], # TODO: address dimensions
    'gallon': ['gallon', 'gallons', 'gals', 'gal'], 
    'glass': ['glass', 'glasses'], 
    'gram': ['gram', 'grams', 'g'], 
    'handful': ['handful', 'handfuls'], 
    'head': ['head', 'heads'], 
    # 'inch': ['inch', 'inches', 'ins'], # TODO: Removing unit "in" for now, unit "in" needs to be dealt with separately somehow, 
    #                                    # TODO: "in" is used for both the unit "inch" and the standard usage of the word "in" (i.e. "I am in a house")
    # 'inch': ['inch', 'inches', 'in', 'ins'], # Inches unit including the abbreviation "in"
    'jar': ['jar', 'jars'], 
    'jarful': ['jarful', 'jarfuls'], 
    'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'], 
    'leg': ['leg', 'legs'], 
    'link': ['link', 'links'], 
    'liter': ['liter', 'liters', 'l'], 
    'loaf': ['loaf', 'loaves'], 
    # 'meter': ['meter', 'meters', 'm', 'ms'], # TODO: address dimensions
    'milligram': ['milligram', 'milligrams', 'mg', 'mgs'], 
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'], 
    # 'millimeter': ['millimeter', 'millimeters', 'mm', 'mms'], # TODO: address dimensions
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', 'oz.', 'ozs.'], 
    'package': ['package', 'packages', 'pkg', 'pkgs'], 
    'packageful': ['packageful', 'packagefuls'], 
    'packet': ['packet', 'packets'], 
    'patty': ['patty', 'patties'], 
    'piece': ['piece', 'pieces'], 
    'pinch': ['pinch', 'pinches'], 
    'pint': ['pint', 'pints', 'pt', 'pts'], 
    'plate': ['plate', 'plates'], 
    'portion': ['portion', 'portions'], 
    'pound': ['pound', 'pounds', 'lbs', 'lb', 'lb.', 'lbs.'],
    'quart': ['quart', 'quarts', 'qt', 'qts'], 
    'rim': ['rim', 'rims'], 
    'roll': ['roll', 'rolls'], 
    'scoop': ['scoop', 'scoops'], 
    'sheet': ['sheet', 'sheets'], 
    'slice': ['slice', 'slices'], 
    'sprig': ['sprig', 'sprigs'], 
    'stalk': ['stalk', 'stalks'], 
    'stick': ['stick', 'sticks'], 
    'strip': ['strip', 'strips'], 
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps", "tbsp.", "tbsps.", "tbl", "tbls", "tbl.", "tbls.", "T", "tbs", "tbs."], # 'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', 'tbsp', 'tbsps'], 
    'tablespoonful': ['tablespoonful', 'tablespoonfuls'], 
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp", "tspn", "tspns", "tspn.", "tspns.", "ts", "t", "t."], # 'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp", "t"],
    'teaspoonful': ['teaspoonful', 'teaspoonfuls'], 
    'thigh': ['thigh', 'thighs'], 
    'tube': ['tube', 'tubes'], 
    'wheel': ['wheel', 'wheels'], 
    'wing': ['wing', 'wings']
}

UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the volume units words
for key, pattern in UNITS.items():
    UNITS_SET.add(key)
    for val in pattern:
        UNITS_SET.add(val)

# create a hash map that maps every variation of a unit to the standard unit name
UNIT_TO_STANDARD_UNIT = {}

for key, pattern in UNITS.items():
    # print(f"key: {key}, pattern: {pattern}")
    for val in pattern:
        UNIT_TO_STANDARD_UNIT[val] = key

# Only the core basic imperial and metric units (Excludes the more specific units like "stalk", "fillet", "slices", etc.)
BASIC_UNITS = {
    # Imperial volume units
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp", "tspn", "tspns", "tspn." "tspns." , "ts", "t", "t."], # 'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp", "t"],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps", "tbsp.", "tbsps.", "tbl", "tbls", "tbl.", "tbls.", "T", "tbs", "tbs."],
    'tablespoonful': ['tablespoonful', 'tablespoonfuls'],
    'teaspoonful': ['teaspoonful', 'teaspoonfuls'],
    'cup': ['cup', 'cups', "C", "c"],
    'pint': ['pint', 'pints', "pt", "pts"],
    'quart': ['quart', 'quarts', "qt", "qts"],
    'gallon': ['gallon', 'gallons', "gals", "gal"],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
                    "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],

    # Metric volume units
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'liter': ['liter', 'liters', 'l'],

    # Imperial weight units
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', 'oz.', 'ozs.'], 
    'pound': ['pound', 'pounds', 'lbs', 'lb', 'lb.', 'lbs.'],

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

# create a non basic units set by subtracting the basic units set from the units set
NON_BASIC_UNITS_SET = UNITS_SET - BASIC_UNITS_SET

# volume units dictionary, things like "cup", "fluid ounce", "gallon", etc.
VOLUME_UNITS = {
    'cup': ['cup', 'cups', "C", "c"],
    'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs', "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],
    'gallon': ['gallon', 'gallons', "gals", "gal"],
    'liter': ['liter', 'liters', 'l'],
    'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz", "ozs"],
    'pint': ['pint', 'pints', "pt", "pts"],
    'quart': ['quart', 'quarts', "qt", "qts"],
    'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps", "tbsp.", "tbsps.", "tbl", "tbls", "tbl.", "tbls.", "T", "tbs", "tbs."],
    'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp."]
}

VOLUME_UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the volume units words
for key, pattern in VOLUME_UNITS.items():
    VOLUME_UNITS_SET.add(key)
    for val in pattern:
        VOLUME_UNITS_SET.add(val)

# dry weight units dictionary, things like "ounce", "pound", "gram", etc.
WEIGHT_UNITS = {
    'ounce': ['ounce', 'ounces', 'oz', 'ozs', 'oz.', 'ozs.'], 
    'pound': ['pound', 'pounds', 'lbs', 'lb', 'lb.', 'lbs.'],
    'gram': ['gram', 'grams', 'g'],
    'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'],
    'milligram': ['milligram', 'milligrams', 'mg', 'mgs']
}

WEIGHT_UNITS_SET = set()

# add all of the keys and values to a Hash set to contain all of the weight units words
for key, pattern in WEIGHT_UNITS.items():
    WEIGHT_UNITS_SET.add(key)
    for val in pattern:
        WEIGHT_UNITS_SET.add(val)

# dimensions dictioanry, things like "feet", "inches", "centimeters", etc.
DIMENSION_UNITS = {
    'centimeter': ['centimeter', 'centimeters', 'cm', 'cms'],
    'foot': ['foot', 'feet', 'ft', 'fts'],
    # 'inch': ['inch', 'inches', 'in', 'ins'],
    'inch': ['inch', 'inches', 'ins'], # TODO: Removing unit "in" for now, unit "in" needs to be dealt with separately somehow, "in" is used for both the unit "inch" and the standard usage of the word "in" (i.e. "I am in a house")
    'meter': ['meter', 'meters', 'm', 'ms'],
    'millimeter': ['millimeter', 'millimeters', 'mm', 'mms']
}

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

# Units that if they appear in a string and there are no "real" units, then these strings might be units
# (i.e. "2 small carrots" -> "quantity: 2, unit: small, ingredient: carrots")
# (i.e. "medium carrot" -> "quantity: 1, unit: medium, ingredient: carrot")
SOMETIMES_UNITS_SET = set([
    "extra small",
    "extra-small",
    "small",
    "medium",
    "large",
    # "sm",
    # "med",
    # "lrg",
    "extra large",
    "extra-large",
    "big", 
    "tiny",
    "modest"
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
    "pitted",
])

# specific words that are used to describe something about a unit (i.e. "packed cup", "level tablespoon")
APPROXIMATE_STRINGS = set([
    "about",
    "bout",
    "around",
    "approximately",
    "approx",
    "approx.",
    "appx",
    "appx.",
    "nearly",
    "almost",
    "roughly",
    "estimated",
    "estimate",
    "est.",
    "est",
    "estim", 
    "estim."
])

# phrases that are used to specify the amount of quantity per unit (i.e. "4 lbs each", "about 2 ounces each")
QUANTITY_PER_UNIT_STRINGS = set([
    "each",
    "per",
    "apiece",
    "a piece",
    "per each"
])

# generic list of stop words that are not useful for parsing and should be removed from the string
STOP_WORDS = set([
    "i",
    "me",
    "my",
    "myself",
    "we",
    "our",
    "ours",
    "ourselves",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
    "he",
    "him",
    "his",
    "himself",
    "she",
    "her",
    "hers",
    "herself",
    "it",
    "its",
    "itself",
    "they",
    "them",
    "their",
    "theirs",
    "themselves",
    "what",
    "which",
    "who",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "am",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "having",
    "do",
    "does",
    "did",
    "doing",
    "a",
    "an",
    "the",
    "and",
    "but",
    "if",
    "or",
    "because",
    "as",
    "until",
    "while",
    "of",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "to",
    "from",
    "up",
    "down",
    "in",
    "out",
    "on",
    "off",
    "over",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "any",
    "both",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    # "s",
    # "t",
    "can",
    "will",
    "just",
    # "don",
    "should",
    "now",
    "couldn't",
    "didn't",
    "doesn't",
    "don't",
    "hadn't",
    "hasn't",
    "haven't",
    "isn't",
    "shouldn't",
    "wasn't",
    "weren't",
    "won't",
    "wouldn't",
    "can't",
    "aren't",
    "hasn't",
    "hadn't",
    "haven't",
    "wasn't",
    "weren't",
    
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

# UNITS = {
#     'teaspoon': ['teaspoon', 'teaspoons', 'tsp', 'tsps', "tsp"],
#     'tablespoon': ['tablespoon', 'tablespoons', 'tbsp', 'tbsps', "tbsp", "tbsps"],
#     'cup': ['cup', 'cups'],
#     'ounce': ['ounce', 'ounces', 'oz', 'ozs', "oz", "ozs"],
#     'pound': ['pound', 'pounds', 'lbs', 'lb', 'lbs'],
#     'gram': ['gram', 'grams', 'g'],
#     'kilogram': ['kilogram', 'kilograms', 'kg', 'kgs'],
#     'milliliter': ['milliliter', 'milliliters', 'ml', 'mls'],
#     'liter': ['liter', 'liters', 'l'],
#     'milligram': ['milligram', 'milligrams', 'mg', 'mgs'],
#     'pinch': ['pinch', 'pinches'],
#     'dash': ['dash', 'dashes'],
#     'dallop': ['dallop', 'dallops'],
#     'drop': ['drop', 'drops'],
#     'sprig': ['sprig', 'sprigs'],
#     'slice': ['slice', 'slices'],
#     'piece': ['piece', 'pieces'],
#     'package': ['package', 'packages'],
#     'tablespoonful': ['tablespoonful', 'tablespoonfuls'],
#     'teaspoonful': ['teaspoonful', 'teaspoonfuls'],
#     'handful': ['handful', 'handfuls'],
#     'bunch': ['bunch', 'bunches'],
#     'bottle': ['bottle', 'bottles'],
#     'can': ['can', 'cans'],
#     'jar': ['jar', 'jars'],
#     'package': ['package', 'packages'],
#     'bag': ['bag', 'bags'],
#     'box': ['box', 'boxes'],
#     'slice': ['slice', 'slices'],
#     'sprig': ['sprig', 'sprigs'],
#     'stalk': ['stalk', 'stalks'],
#     'gallon': ['gallon', 'gallons', "gals", "gal"],
#     'pint': ['pint', 'pints', "pt", "pts"],
#     'quart': ['quart', 'quarts', "qt", "qts"],
#     'fluid ounce': ['fluid ounce', 'fluid ounces', 'fl oz', 'fl ozs',
#                      "fluid oz", "fluid ozs", "fluid oz", "fluid ozs"],
#     'millimeter': ['millimeter', 'millimeters', 'mm', 'mms'],
#     'centimeter': ['centimeter', 'centimeters', 'cm', 'cms'],
#     'inch': ['inch', 'inches', 'in', 'ins'],
#     'foot': ['foot', 'feet', 'ft', 'fts'],
#     'meter': ['meter', 'meters', 'm', 'ms'],
#     'scoop': ['scoop', 'scoops'],
#     'packet': ['packet', 'packets'],
#     'tube': ['tube', 'tubes'],
#     'stick': ['stick', 'sticks'],
#     'fillet': ['fillet', 'fillets'],
#     'filet': ['filet', 'filets'],
#     'head': ['head', 'heads'],
#     'bulb': ['bulb', 'bulbs'],
#     'ear': ['ear', 'ears'],
#     'rim': ['rim', 'rims'],
#     'sheet': ['sheet', 'sheets'],
#     'portion': ['portion', 'portions'],
#     'envelope': ['envelope', 'envelopes'],
#     'cube': ['cube', 'cubes'],
#     'breast': ['breast', 'breasts'],
#     'thigh': ['thigh', 'thighs'],
#     'leg': ['leg', 'legs'],
#     'drumstick': ['drumstick', 'drumsticks'],
#     'wing': ['wing', 'wings'],
#     'patty': ['patty', 'patties'],
#     'link': ['link', 'links'],
#     'strip': ['strip', 'strips'],
#     'bun': ['bun', 'buns'],
#     'loaf': ['loaf', 'loaves'],
#     'roll': ['roll', 'rolls'],
#     'glass': ['glass', 'glasses'],
#     'bowl': ['bowl', 'bowls'],
#     'plate': ['plate', 'plates'],
#     'container': ['container', 'containers'],
#     'cupful': ['cupful', 'cupfuls'],
#     'bottleful': ['bottleful', 'bottlefuls'],
#     'canful': ['canful', 'canfuls'],
#     'can': ['can', 'cans'],
#     'jarful': ['jarful', 'jarfuls'],
#     'packageful': ['packageful', 'packagefuls'],
#     'bagful': ['bagful', 'bagfuls'],
#     'boxful': ['boxful', 'boxfuls'],
#     'head': ['head', 'heads'],
#     'stalk': ['stalk', 'stalks'],
#     'wheel': ['wheel', 'wheels']
# }